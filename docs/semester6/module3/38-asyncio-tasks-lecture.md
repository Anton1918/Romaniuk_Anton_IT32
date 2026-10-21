# 38. (Л) Керування асинхронними задачами та вимірювання продуктивності в asyncio

## Зміст лекції

1. Від кількох задач до сотень
2. `asyncio.gather`: дочекатися всіх
3. Помилки в `gather`: `return_exceptions`
4. `asyncio.as_completed`: у міру готовності
5. Таймаути: `wait_for` і `asyncio.timeout`
6. Скасування задач: `cancel` і `CancelledError`
7. `TaskGroup`: структурована конкурентність
8. `Semaphore`: обмеження одночасних операцій
9. Асинхронні HTTP-запити: aiohttp
10. Курси НБУ за місяць
11. Вимірювання продуктивності
12. Потоки чи asyncio: порівняння
13. Типові помилки

## Від кількох задач до сотень

У лекції 36 ми створювали задачі `create_task` і чекали кожну окремим `await`. Для реальних програм потрібно більше:

| Потреба | Інструмент |
|---|---|
| дочекатися всіх задач і отримати список результатів | `asyncio.gather` |
| обробляти результати, щойно вони готові | `asyncio.as_completed` |
| не чекати довше певного часу | `asyncio.wait_for`, `asyncio.timeout` |
| зупинити непотрібні задачі | `task.cancel()` |
| гарантувати, що жодна задача не «загубиться» | `asyncio.TaskGroup` |
| не перевантажити сервер тисячею запитів | `asyncio.Semaphore` |

## `asyncio.gather`: дочекатися всіх

`gather(*awaitables)` запускає корутини конкурентно (загортає їх у задачі) і повертає **список результатів у порядку аргументів** — незалежно від того, яка задача завершилася першою:

```python
# Program: gather returns results in the order of arguments
import asyncio
import time


async def get_rate(day: int) -> tuple[int, float]:
    await asyncio.sleep(0.1 * (4 - day))  # пізніші дні «відповідають» швидше
    return day, 41.0 + day / 100


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(*(get_rate(day) for day in range(1, 4)))
    print(results)
    print(f"{time.perf_counter() - start:.1f}s")


asyncio.run(main())
```

```text
[(1, 41.01), (2, 41.02), (3, 41.03)]
0.3s
```

Зірочка `*` розпаковує генератор корутин в окремі аргументи (лекція 10, 5 семестр).

## Помилки в `gather`: `return_exceptions`

Якщо одна з корутин згенерувала виняток:

| | `gather(...)` | `gather(..., return_exceptions=True)` |
|---|---|---|
| що отримує код | перший виняток генерується на `await gather` | список, де на місці помилки — обʼєкт винятку |
| інші задачі | **продовжують** виконуватися у фоні | завершуються, результати в списку |

```python
# Program: gather with and without return_exceptions
import asyncio


async def get_rate(day: int) -> float:
    await asyncio.sleep(0.1)
    if day == 31:
        raise ValueError(f"no such day: September {day}")
    return 41.0 + day / 100


async def main() -> None:
    try:
        await asyncio.gather(get_rate(1), get_rate(31), get_rate(2))
    except ValueError as error:
        print("without return_exceptions:", error)

    results = await asyncio.gather(get_rate(1), get_rate(31), get_rate(2), return_exceptions=True)
    for day, result in zip((1, 31, 2), results):
        if isinstance(result, Exception):
            print(f"day {day}: error {result}")
        else:
            print(f"day {day}: {result}")


asyncio.run(main())
```

```text
without return_exceptions: no such day: September 31
day 1: 41.01
day 31: error no such day: September 31
day 2: 41.02
```

Для пакетного завантаження зазвичай обирають `return_exceptions=True`: одна неправильна дата не повинна зупиняти обробку решти.

## `asyncio.as_completed`: у міру готовності

`as_completed` віддає задачі в порядку **завершення**. Так можна показувати прогрес або зберігати результати, не чекаючи найповільнішої задачі:

```python
# Program: process results as soon as they are ready
import asyncio
import time


async def download(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)
    return name


async def main() -> None:
    start = time.perf_counter()
    jobs = [download("big.csv", 0.3), download("small.csv", 0.1), download("medium.csv", 0.2)]
    for number, next_done in enumerate(asyncio.as_completed(jobs), 1):
        name = await next_done
        print(f"{time.perf_counter() - start:.1f}s [{number}/3] {name}")


asyncio.run(main())
```

```text
0.1s [1/3] small.csv
0.2s [2/3] medium.csv
0.3s [3/3] big.csv
```

## Таймаути: `wait_for` і `asyncio.timeout`

Мережевий запит може «зависнути». Без обмеження часу програма чекатиме вічно. `asyncio.wait_for(aw, timeout)` скасовує операцію, що не встигла, і генерує `TimeoutError`:

```python
# Program: timeouts for single operations and for a block
import asyncio


async def request(seconds: float) -> str:
    await asyncio.sleep(seconds)
    return f"answer after {seconds}s"


async def main() -> None:
    print(await asyncio.wait_for(request(0.1), timeout=0.5))
    try:
        await asyncio.wait_for(request(2), timeout=0.2)
    except TimeoutError:
        print("wait_for: too slow, cancelled")

    try:
        async with asyncio.timeout(0.25):  # Python 3.11+: одне обмеження на весь блок
            await request(0.1)
            await request(0.1)
            await request(0.1)
    except TimeoutError:
        print("timeout block: three requests did not fit in 0.25s")


asyncio.run(main())
```

```text
answer after 0.1s
wait_for: too slow, cancelled
timeout block: three requests did not fit in 0.25s
```

`async with` — асинхронний менеджер контексту: на вході й виході він теж може чекати (`await`).

## Скасування задач: `cancel` і `CancelledError`

`task.cancel()` просить задачу зупинитися: у точці, де вона чекає (`await`), генерується виняток `asyncio.CancelledError`. Задача може перехопити його, щоб прибрати за собою (закрити файл, зʼєднання), але має **згенерувати знову**:

```python
# Program: cancel the remaining tasks after the first results
import asyncio


async def get_rate(day: int) -> int:
    try:
        await asyncio.sleep(0.05 * day)
        return day
    except asyncio.CancelledError:
        print(f"day {day} cancelled")
        raise


async def main() -> None:
    tasks = [asyncio.create_task(get_rate(day)) for day in range(1, 6)]
    first = []
    for next_done in asyncio.as_completed(tasks):
        first.append(await next_done)
        if len(first) == 2:
            break
    for task in tasks:
        task.cancel()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print("got:", first)
    print("states:", ["cancelled" if t.cancelled() else "done" for t in tasks])
    print("gather:", [type(r).__name__ if isinstance(r, BaseException) else r for r in results])


asyncio.run(main())
```

```text
day 3 cancelled
day 4 cancelled
day 5 cancelled
got: [1, 2]
states: ['done', 'done', 'cancelled', 'cancelled', 'cancelled']
gather: [1, 2, 'CancelledError', 'CancelledError', 'CancelledError']
```

`cancel()` для вже завершеної задачі нічого не робить. Після `cancel()` задачу треба **дочекатися** (тут — через `gather`), щоб скасування справді відбулося до виходу з програми.

!!! warning "Не «ковтайте» `CancelledError`"
    `except asyncio.CancelledError: pass` без `raise` робить задачу «нескасовною»: `asyncio.run`, `TaskGroup` і таймаути перестають працювати правильно. Так само небезпечний `except BaseException:` без повторного `raise`.

## `TaskGroup`: структурована конкурентність

Задачі з `create_task` легко «загубити»: забули `await` — і задача тихо скасується при виході. `asyncio.TaskGroup` (Python 3.11+) гарантує, що **усі** задачі групи завершаться до виходу з блоку `async with`. Якщо одна задача впала, група **скасовує решту** і генерує `ExceptionGroup` з усіма помилками:

```python
# Program: TaskGroup waits for all tasks and cancels the rest on error
import asyncio

cancelled = []


async def get_rate(day: int) -> float:
    try:
        await asyncio.sleep(0.1 if day != 31 else 0.05)
        if day == 31:
            raise ValueError("no such day: 31")
        return 41.0 + day / 100
    except asyncio.CancelledError:
        cancelled.append(day)
        raise


async def main() -> None:
    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(get_rate(day)) for day in (1, 2)]
    print("all ok:", [t.result() for t in tasks])

    try:
        async with asyncio.TaskGroup() as group:
            for day in (1, 31, 2):
                group.create_task(get_rate(day))
    except* ValueError as errors:
        print("errors:", [str(e) for e in errors.exceptions])
        print("cancelled by the group:", sorted(cancelled))


asyncio.run(main())
```

```text
all ok: [41.01, 41.02]
errors: ['no such day: 31']
cancelled by the group: [1, 2]
```

`except*` (Python 3.11+) обробляє винятки з групи за типом.

| | `gather` | `TaskGroup` |
|---|---|---|
| помилка однієї задачі | решта продовжують у фоні | решта скасовуються |
| «забуті» задачі | можливі | неможливі: блок чекає всіх |
| усі помилки | лише перша (або в списку) | усі в `ExceptionGroup` |
| коли обирати | незалежні задачі, потрібні всі результати навіть з помилками | задачі однієї операції: або все, або нічого |

## `Semaphore`: обмеження одночасних операцій

1000 одночасних запитів до одного сервера — погана ідея: сервер може відповісти помилкою `429 Too Many Requests` або заблокувати вашу адресу. **Семафор** — лічильник дозволів: `async with semaphore:` забирає дозвіл (або чекає, якщо дозволів немає) і повертає його на виході:

```python
# Program: at most 3 requests at the same time
import asyncio
import time

active = 0
peak = 0


async def request(semaphore: asyncio.Semaphore, number: int) -> int:
    global active, peak
    async with semaphore:
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.1)
        active -= 1
        return number


async def main() -> None:
    semaphore = asyncio.Semaphore(3)
    start = time.perf_counter()
    results = await asyncio.gather(*(request(semaphore, n) for n in range(10)))
    print(f"{len(results)} requests, peak concurrency {peak}, {time.perf_counter() - start:.1f}s")


asyncio.run(main())
```

```text
10 requests, peak concurrency 3, 0.4s
```

10 запитів по 0,1 с з обмеженням 3 — чотири «хвилі»: 3 + 3 + 3 + 1. Глобальні змінні `active` і `peak` тут безпечні: між `await` код виконується без перемикань (лекція 36).

## Асинхронні HTTP-запити: aiohttp

`requests` (лекція 37, 5 семестр) — блокуюча бібліотека: у корутині вона зупинила б увесь цикл. Для asyncio потрібна асинхронна бібліотека — **aiohttp**:

```bash
python3 -m pip install aiohttp
```

| requests | aiohttp |
|---|---|
| `requests.get(url, params=p, timeout=10)` | `async with session.get(url, params=p) as response:` |
| `response.status_code` | `response.status` |
| `response.json()` | `await response.json()` |
| `requests.Session()` | `aiohttp.ClientSession()` — одна на всю програму |

`ClientSession` тримає пул зʼєднань: повторні запити до того самого сервера використовують уже відкрите зʼєднання. Створюють її **одну** і передають у корутини.

## Курси НБУ за місяць

```python
# File: nbu_rates.py
import asyncio
import time
from datetime import date, timedelta

import aiohttp

URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"


async def get_rate(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, day: date) -> tuple[date, float]:
    params = {"valcode": "USD", "date": day.strftime("%Y%m%d"), "json": ""}
    async with semaphore:
        async with session.get(URL, params=params) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)
    return day, data[0]["rate"]


async def main() -> None:
    days = [date(2026, 9, 1) + timedelta(days=i) for i in range(30)]
    semaphore = asyncio.Semaphore(5)
    timeout = aiohttp.ClientTimeout(total=15)
    start = time.perf_counter()
    async with aiohttp.ClientSession(timeout=timeout) as session:
        results = await asyncio.gather(*(get_rate(session, semaphore, day) for day in days),
                                       return_exceptions=True)
    elapsed = time.perf_counter() - start

    rates = [r for r in results if not isinstance(r, BaseException)]
    errors = [r for r in results if isinstance(r, BaseException)]
    for day, rate in rates[:3]:
        print(day, rate)
    values = [rate for _, rate in rates]
    print(f"days: {len(rates)}, errors: {len(errors)}")
    print(f"min {min(values):.4f}, max {max(values):.4f}, avg {sum(values) / len(values):.4f}")
    print(f"time: {elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
```

```text
2026-09-01 44.5249
2026-09-02 44.4553
2026-09-03 44.6093
days: 30, errors: 0
min 44.4553, max 44.9729, avg 44.6812
time: 0.4s
```

- `content_type=None` дозволяє розібрати JSON, навіть якщо сервер надіслав інший `Content-Type`;
- `raise_for_status()` перетворює відповідь `4xx`/`5xx` на виняток `aiohttp.ClientResponseError`;
- `ClientTimeout(total=15)` обмежує час кожного запиту;
- семафор обмежує навантаження на сервер НБУ: не більше 5 запитів одночасно.

Час залежить від мережі; порівняння з послідовним варіантом — у наступному розділі.

## Вимірювання продуктивності

Щоб чесно порівняти варіанти, вимірюють той самий набір операцій кілька разів. Для асинхронного коду зручний декоратор, що вимірює час корутини:

```python
# Program: an async timing decorator and a comparison of strategies
import asyncio
import functools
import time


def timed(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            print(f"{func.__name__:<12} {time.perf_counter() - start:.1f}s")
    return wrapper


async def request(n: int) -> int:
    await asyncio.sleep(0.1)
    return n


@timed
async def sequential(count: int) -> list[int]:
    return [await request(n) for n in range(count)]


@timed
async def unlimited(count: int) -> list[int]:
    return await asyncio.gather(*(request(n) for n in range(count)))


@timed
async def limited(count: int, limit: int = 5) -> list[int]:
    semaphore = asyncio.Semaphore(limit)

    async def one(n: int) -> int:
        async with semaphore:
            return await request(n)
    return await asyncio.gather(*(one(n) for n in range(count)))


async def main() -> None:
    for strategy in (sequential, unlimited, limited):
        assert await strategy(10) == list(range(10))


asyncio.run(main())
```

```text
sequential   1.0s
unlimited    0.1s
limited      0.2s
```

| Стратегія | Час для N запитів тривалістю t | Навантаження на сервер |
|---|---|---|
| послідовно | N · t | 1 запит |
| `gather` без обмеження | ≈ t | N запитів одночасно |
| `gather` + `Semaphore(k)` | ≈ ⌈N / k⌉ · t | k запитів |

## Потоки чи asyncio: порівняння

| Критерій | `ThreadPoolExecutor` + `requests` (лекція 32) | asyncio + aiohttp |
|---|---|---|
| зміни в коді | мінімальні: звичайні функції | `async`/`await` усюди |
| бібліотеки | будь-які | лише асинхронні |
| 10–50 одночасних запитів | чудово | чудово |
| 1000+ одночасних зʼєднань | памʼять на потоки, перемикання ОС | один потік, мало памʼяті |
| стани гонитви | потрібні замки | рідкісні |
| скасування й таймаути | складно | вбудовані (`cancel`, `timeout`) |

Для невеликого скрипта зі звичайними бібліотеками простіше взяти потоки. Для сервера з тисячами клієнтів (модуль 4) або програми з багатьма мережевими операціями — asyncio.

## Типові помилки

| Помилка | Чому погано | Як правильно |
|---|---|---|
| `requests.get` у корутині | блокує подієвий цикл | `aiohttp` |
| Нова `ClientSession` для кожного запиту | повільно, зайві зʼєднання | одна сесія на програму |
| `gather` без `return_exceptions` для пакетних задач | одна помилка — немає жодного результату | `return_exceptions=True` або `TaskGroup` |
| Тисячі запитів без обмеження | `429`, блокування, вичерпання сокетів | `Semaphore` |
| Немає таймаутів | програма «зависає» на одному запиті | `ClientTimeout`, `wait_for`, `asyncio.timeout` |
| `except CancelledError: pass` | задачу неможливо скасувати | прибрати ресурси і `raise` |
| Задачі скасовано, але не дочекано | скасування не завершилося | `await gather(*tasks, return_exceptions=True)` |
| Один вимір часу | випадкові коливання мережі | кілька запусків |

## Підсумок

- `gather` запускає корутини конкурентно й повертає результати в порядку аргументів; `return_exceptions=True` збирає помилки в список.
- `as_completed` віддає результати в міру готовності.
- `wait_for` і `asyncio.timeout` обмежують час; `task.cancel()` скасовує задачу через `CancelledError`.
- `TaskGroup` гарантує завершення всіх задач і скасовує решту при помилці.
- `Semaphore` обмежує кількість одночасних операцій.
- Для HTTP в asyncio використовують **aiohttp** з однією `ClientSession`.
- Продуктивність порівнюють вимірюваннями: послідовно N·t, конкурентно ≈ t, з обмеженням k — ≈ N/k·t.

## Корисні посилання

- [asyncio — Coroutines and Tasks (gather, wait_for, TaskGroup)](https://docs.python.org/3/library/asyncio-task.html)
- [asyncio — Synchronization Primitives (Semaphore)](https://docs.python.org/3/library/asyncio-sync.html)
- [aiohttp — Client Quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html)
- [API НБУ — курси валют](https://bank.gov.ua/ua/open-data/api-dev)
- Fowler M. Python Concurrency with asyncio. — Manning, 2022. — Розділи 2, 4.
