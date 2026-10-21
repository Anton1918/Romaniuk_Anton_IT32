# 29. (Л) Огляд стандартних бібліотек: math, random, datetime, os, sys

## Зміст лекції

1. Стандартна бібліотека: навіщо і як шукати
2. `math` — математичні функції
3. `random` — випадкові числа
4. `datetime` — дати і час
5. `os` — взаємодія з операційною системою
6. `sys` — інтерпретатор і запуск програми
7. Приклад: усе разом
8. Типові помилки

## Стандартна бібліотека: навіщо і як шукати

У лекції 27 ми побачили, що разом з Python встановлюються сотні готових модулів — **стандартна бібліотека** (standard library). Їх не треба встановлювати через `pip`: достатньо `import`.

Сьогодні розглянемо пʼять модулів, які трапляються майже в кожній програмі. Мета — не вивчити все напамʼять, а знати, **що існує**, і вміти швидко знайти потрібне.

Два способи подивитися, що є в модулі, прямо з інтерпретатора:

```python
import math

# Імена, визначені в модулі (без службових)
print([name for name in dir(math) if not name.startswith("_")])

# Документація до конкретної функції
help(math.sqrt)
```

```text
['acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'cbrt', 'ceil', 'comb', ...]
Help on built-in function sqrt in module math:

sqrt(x, /)
    Return the square root of x.
```

Повна документація кожного модуля — на [docs.python.org/3/library](https://docs.python.org/3/library/index.html).

## `math` — математичні функції

Модуль `math` містить математичні константи і функції для роботи з числами `int` і `float`.

### Константи

```python
import math

print(math.pi)   # число пі
print(math.e)    # основа натурального логарифма
print(math.inf)  # нескінченність
```

```text
3.141592653589793
2.718281828459045
inf
```

`math.inf` зручно використовувати як початкове значення при пошуку мінімуму: будь-яке число буде менше за нього.

### Корені, степені, логарифми

```python
import math

print(math.sqrt(16))       # квадратний корінь, завжди float
print(math.isqrt(17))      # цілий квадратний корінь (округлення вниз)
print(math.pow(2, 10))     # степінь, завжди float
print(2 ** 10)             # те саме оператором, для int дає int
print(math.log(math.e))    # натуральний логарифм
print(math.log10(1000))    # десятковий логарифм
print(math.log2(1024))     # двійковий логарифм
print(math.log(81, 3))     # логарифм за довільною основою
```

```text
4.0
4
1024.0
1024
1.0
3.0
10.0
4.0
```

!!! note "`math.sqrt` vs `** 0.5`"
    `x ** 0.5` теж обчислює корінь, але `math.sqrt(x)` читається однозначніше. Для відʼємного аргументу `math.sqrt(-1)` кидає `ValueError: math domain error`, тоді як `(-1) ** 0.5` мовчки повертає комплексне число.

### Округлення

Python має вбудовану функцію `round()`, а `math` додає ще три способи:

| Функція | Що робить | `2.7` | `-2.7` |
|---|---|---|---|
| `math.floor(x)` | вниз, до меншого цілого | `2` | `-3` |
| `math.ceil(x)` | вгору, до більшого цілого | `3` | `-2` |
| `math.trunc(x)` | відкидає дробову частину (до нуля) | `2` | `-2` |
| `round(x)` | до найближчого цілого | `3` | `-3` |

```python
import math

students = 47
group_size = 10

# Скільки груп потрібно, щоб помістилися всі студенти
groups = math.ceil(students / group_size)
print("groups needed:", groups)

# Скільки повних груп вийде
full_groups = math.floor(students / group_size)
print("full groups:", full_groups)
```

```text
groups needed: 5
full groups: 4
```

!!! warning "`round()` округлює «до парного»"
    `round(2.5)` дає `2`, а `round(3.5)` — `4`. Це «банківське округлення»: половинки округлюються до найближчого **парного** числа, щоб при багатьох округленнях похибка не накопичувалася в один бік. Якщо потрібно «шкільне» округлення вгору, використовуйте `math.floor(x + 0.5)` для додатних чисел.

### Тригонометрія

Тригонометричні функції приймають кут у **радіанах**. Для переходу між градусами і радіанами є `math.radians()` і `math.degrees()`.

```python
import math

angle = 30  # у градусах

print(f"sin(30) = {math.sin(math.radians(angle)):.2f}")
print(f"cos(60) = {math.cos(math.radians(60)):.2f}")
print(f"pi rad = {math.degrees(math.pi)} deg")

# Довжина гіпотенузи за катетами 3 і 4
print("hypot:", math.hypot(3, 4))
```

```text
sin(30) = 0.50
cos(60) = 0.50
pi rad = 180.0 deg
hypot: 5.0
```

### Цілочисельні функції

```python
import math

print(math.factorial(5))   # 5! = 1 * 2 * 3 * 4 * 5
print(math.gcd(48, 36))    # найбільший спільний дільник
print(math.lcm(4, 6))      # найменше спільне кратне
print(math.comb(5, 2))     # кількість способів вибрати 2 з 5
print(math.prod([2, 3, 4]))  # добуток елементів (як sum, але множення)
```

```text
120
12
12
10
24
```

### Порівняння дробових чисел

Через особливості зберігання `float` (лекція 04) звичайне `==` для дробових чисел ненадійне:

```python
import math

a = 0.1 + 0.2

print(a)
print(a == 0.3)
print(math.isclose(a, 0.3))
```

```text
0.30000000000000004
False
True
```

`math.isclose(a, b)` перевіряє, що числа «достатньо близькі». Завжди використовуйте його замість `==`, коли порівнюєте результати обчислень з `float`.

## `random` — випадкові числа

Модуль `random` генерує **псевдовипадкові** числа: їх обчислює детермінований алгоритм, але для людини вони виглядають випадковими. Цього достатньо для ігор, симуляцій, перемішування тестових даних.

Вивід прикладів у цьому розділі у вас буде **інший** — на те він і випадковий.

### Випадкові числа

```python
import random

print(random.random())          # float у діапазоні [0.0, 1.0)
print(random.uniform(1.5, 3.5)) # float у діапазоні [1.5, 3.5]
print(random.randint(1, 6))     # int від 1 до 6 ВКЛЮЧНО
print(random.randrange(0, 10, 2))  # int з range(0, 10, 2): 0, 2, 4, 6 або 8
```

```text
0.6394267984578837
2.0500114085310283
3
6
```

!!! warning "`randint` включає обидві межі"
    `random.randint(1, 6)` може повернути і `1`, і `6` — як гральний кубик. Це відрізняється від `range(1, 6)`, де `6` не входить. `random.randrange(1, 6)` поводиться як `range` — повертає від `1` до `5`.

### Вибір з послідовності

```python
import random

names = ["Olena", "Taras", "Iryna", "Andrii", "Marta"]

# Один випадковий елемент
print("on duty:", random.choice(names))

# k елементів БЕЗ повторів
print("team:", random.sample(names, 3))

# k елементів З повторами
print("with repeats:", random.choices(names, k=3))

# Перемішування списку на місці: змінює сам список і повертає None
random.shuffle(names)
print("shuffled:", names)
```

```text
on duty: Iryna
team: ['Marta', 'Olena', 'Andrii']
with repeats: ['Taras', 'Taras', 'Olena']
shuffled: ['Andrii', 'Marta', 'Taras', 'Olena', 'Iryna']
```

`random.choices` вміє враховувати **ваги** — наскільки часто має випадати кожен варіант:

```python
import random

prizes = ["sticker", "pen", "book"]

# sticker випадатиме в 7 разів частіше, ніж book
result = random.choices(prizes, weights=[7, 2, 1], k=10)
print(result)
```

```text
['sticker', 'sticker', 'pen', 'sticker', 'sticker', 'book', 'sticker', 'sticker', 'pen', 'sticker']
```

### Відтворюваність: `random.seed()`

Генератор починає з певного початкового значення — **зерна** (seed). Якщо задати зерно явно, послідовність «випадкових» чисел буде **однаковою** при кожному запуску. Це потрібно для тестів і для відтворення помилок.

```python
import random

random.seed(42)
print([random.randint(1, 100) for _ in range(5)])

random.seed(42)
print([random.randint(1, 100) for _ in range(5)])
```

```text
[82, 15, 4, 95, 36]
[82, 15, 4, 95, 36]
```

Обидва рядки однакові. Запустіть програму ще раз — і отримаєте ті самі числа.

Саме тому, щоб при кожному запуску числа були різними, зерном часто роблять **поточний час** (timestamp): він ніколи не повторюється. У Python це не обовʼязково робити вручну — при імпорті `random` генератор сам ініціалізується випадковими даними від операційної системи (або поточним часом, якщо ОС їх не надає). Але явний timestamp корисний, коли треба поєднати обидва підходи: числа щоразу різні, а зерно виводиться на екран, тож будь-який запуск можна точно повторити.

```python
import random
import time

# Поточний час у секундах від 1 січня 1970 року — щоразу інше значення
seed = int(time.time())
random.seed(seed)

print("seed:", seed)
print([random.randint(1, 100) for _ in range(5)])
```

```text
seed: 1791729012
[32, 24, 15, 23, 41]
```

Якщо в такому запуску знайшлася помилка, достатньо підставити виведене зерно — `random.seed(1791729012)` — і отримати ту саму послідовність.

!!! danger "`random` — не для паролів і токенів"
    Знаючи кілька згенерованих чисел, можна передбачити наступні. Для паролів, токенів, кодів підтвердження використовуйте модуль `secrets`:

    ```python
    import secrets

    print(secrets.token_hex(16))       # випадковий токен
    print(secrets.randbelow(1000000))  # випадкове число для коду підтвердження
    ```

### Приклад: гра «Вгадай число»

```python
import random

secret = random.randint(1, 20)
attempts = 0

print("I am thinking of a number from 1 to 20.")

while True:
    guess = int(input("Your guess: "))
    attempts += 1

    if guess < secret:
        print("Too small")
    elif guess > secret:
        print("Too big")
    else:
        print(f"Correct! Attempts: {attempts}")
        break
```

```text
I am thinking of a number from 1 to 20.
Your guess: 10
Too big
Your guess: 5
Too small
Your guess: 7
Correct! Attempts: 3
```

## `datetime` — дати і час

Модуль `datetime` містить кілька класів. Найуживаніші:

| Клас | Що зберігає | Приклад значення |
|---|---|---|
| `date` | дату: рік, місяць, день | `2026-10-11` |
| `datetime` | дату і час | `2026-10-11 14:30:00` |
| `timedelta` | проміжок часу | `3 days, 2:00:00` |

Зверніть увагу: модуль називається `datetime`, і клас у ньому — теж `datetime`. Тому зазвичай імпортують класи напряму:

```python
from datetime import date, datetime, timedelta
```

Після цього `datetime.now()` — це метод класу. Якщо ж написати `import datetime`, той самий виклик буде `datetime.datetime.now()`.

### Поточна дата і час

```python
from datetime import date, datetime

today = date.today()
now = datetime.now()

print("today:", today)
print("now:", now)
print("year:", today.year, "month:", today.month, "day:", today.day)
print("time:", now.hour, now.minute, now.second)

# Понеділок = 0, неділя = 6
print("weekday:", today.weekday())
```

```text
today: 2026-10-11
now: 2026-10-11 14:30:12.345678
year: 2026 month: 10 day: 11
time: 14 30 12
weekday: 6
```

### Створення конкретної дати

```python
from datetime import date, datetime

birthday = date(2008, 3, 15)
exam = datetime(2026, 12, 20, 9, 30)  # 20 грудня 2026, 09:30

print(birthday)
print(exam)
```

```text
2008-03-15
2026-12-20 09:30:00
```

Неіснуюча дата одразу дає помилку:

```python
from datetime import date

date(2026, 2, 30)
```

```text
ValueError: day is out of range for month
```

### Арифметика дат: `timedelta`

Різниця двох дат — це обʼєкт `timedelta`. І навпаки: додавши `timedelta` до дати, отримаємо нову дату.

```python
from datetime import date, timedelta

today = date(2026, 10, 11)
exam = date(2026, 12, 20)

left = exam - today
print("days until exam:", left.days)

deadline = today + timedelta(days=14)
print("deadline:", deadline)

week_ago = today - timedelta(weeks=1)
print("week ago:", week_ago)
```

```text
days until exam: 70
deadline: 2026-10-25
week ago: 2026-10-04
```

`timedelta` приймає `days`, `weeks`, `hours`, `minutes`, `seconds` і вміє переходити через межі місяців і років — не треба вручну рахувати, скільки днів у лютому.

```python
from datetime import datetime, timedelta

start = datetime(2026, 10, 11, 22, 45)
duration = timedelta(hours=1, minutes=30)

end = start + duration
print("end:", end)

# Загальна кількість секунд у проміжку
print("seconds:", duration.total_seconds())
```

```text
end: 2026-10-12 00:15:00
seconds: 5400.0
```

Дати можна порівнювати звичайними операторами:

```python
from datetime import date

deadline = date(2026, 10, 25)
submitted = date(2026, 10, 27)

if submitted > deadline:
    print("late by", (submitted - deadline).days, "days")
```

```text
late by 2 days
```

### Форматування: дата → рядок (`strftime`)

Метод `strftime` (string **f**ormat time) перетворює дату на рядок за шаблоном. У шаблоні коди з `%` замінюються частинами дати:

| Код | Значення | Приклад |
|---|---|---|
| `%Y` | рік, 4 цифри | `2026` |
| `%m` | місяць, 2 цифри | `03` |
| `%d` | день, 2 цифри | `05` |
| `%H` | години (00–23) | `09` |
| `%M` | хвилини | `07` |
| `%S` | секунди | `00` |
| `%A` | назва дня тижня | `Sunday` |
| `%B` | назва місяця | `October` |

```python
from datetime import datetime

moment = datetime(2026, 10, 11, 9, 7)

print(moment.strftime("%d.%m.%Y"))
print(moment.strftime("%Y-%m-%d %H:%M"))
print(moment.strftime("%A, %d %B %Y"))

# ISO 8601 — стандартний формат для файлів, логів, обміну даними
print(moment.isoformat())
```

```text
11.10.2026
2026-10-11 09:07
Sunday, 11 October 2026
2026-10-11T09:07:00
```

### Розбір: рядок → дата (`strptime`)

`strptime` (string **p**arse time) робить зворотне: розбирає рядок за тим самим шаблоном.

```python
from datetime import date, datetime

text = "15.03.2008"
birthday = datetime.strptime(text, "%d.%m.%Y").date()
print(birthday, type(birthday))

# Для ISO-формату є окремий метод
print(date.fromisoformat("2026-12-20"))
```

```text
2008-03-15 <class 'datetime.date'>
2026-12-20
```

Якщо рядок не відповідає шаблону, буде `ValueError`:

```python
from datetime import datetime

try:
    datetime.strptime("2008/03/15", "%d.%m.%Y")
except ValueError as error:
    print("error:", error)
```

```text
error: time data '2008/03/15' does not match format '%d.%m.%Y'
```

### Приклад: вік у днях і роках

```python
from datetime import date


def age_in_years(birthday: date, today: date) -> int:
    years = today.year - birthday.year
    # Якщо день народження цього року ще не настав — віднімаємо рік
    if (today.month, today.day) < (birthday.month, birthday.day):
        years -= 1
    return years


birthday = date(2008, 3, 15)
today = date.today()

print("age:", age_in_years(birthday, today), "years")
print("lived:", (today - birthday).days, "days")
```

```text
age: 18 years
lived: 6784 days
```

!!! note "Часові пояси"
    `datetime.now()` повертає **локальний** час без інформації про часовий пояс. Для програм, які працюють з користувачами з різних країн або зберігають час на сервері, використовують час з поясом: `datetime.now(timezone.utc)` (`from datetime import timezone`). У межах цього курсу достатньо локального часу.

## `os` — взаємодія з операційною системою

Модуль `os` дає доступ до можливостей операційної системи: змінних оточення, інформації про систему, процесів, а також до файлів і каталогів.

### `os` і `pathlib`: шляхи, файли, каталоги

Раніше для роботи зі шляхами, файлами і каталогами використовували тільки `os` і `os.path`: `os.path.join`, `os.path.exists`, `os.listdir`, `os.makedirs`, `os.remove`, `os.rename`, `os.walk`. Ви часто бачитимете їх у старому коді, прикладах з інтернету і відповідях на Stack Overflow.

Тепер для цього використовують `pathlib` (лекція 21). У `pathlib` є аналог кожної з цих функцій, тож у цій лекції ми їх не розглядаємо. Причини, чому від `os.path` відходять:

- **Шлях — обʼєкт, а не рядок.** У `os.path` шлях — звичайний `str`, і будь-який рядок можна випадково передати туди, де очікується шлях. `Path` знає, що він шлях, і має власні методи: `.name`, `.suffix`, `.parent`, `.exists()`, `.read_text()`.
- **Усе в одному місці.** Зі старим підходом функції розкидані між `os`, `os.path`, `glob` і `shutil`. У `pathlib` вони зібрані в одному класі.
- **Код читається легше.** Порівняйте:

```python
import os
from pathlib import Path

# Старий підхід: os.path
path = os.path.join("data", "2026", "grades.txt")
print(os.path.basename(path), os.path.splitext(path)[1], os.path.dirname(path))

# Сучасний підхід: pathlib
path = Path("data") / "2026" / "grades.txt"
print(path.name, path.suffix, path.parent)
```

```text
grades.txt .txt data/2026
grades.txt .txt data/2026
```

- **Менше кроків для типових задач.** Прочитати файл — `Path("a.txt").read_text()` замість `open` + `read`; знайти всі `.py` в дереві каталогів — `Path(".").rglob("*.py")` замість циклу з `os.walk` і перевіркою розширення.

Функції `os`, які приймають шлях, розуміють і `Path`, тож старий і новий код можна поєднувати. Але у **новому** коді для шляхів обирайте `pathlib`. А от для того, що описано нижче, у `pathlib` аналогів немає — тут потрібен `os`.

### Змінні оточення

**Змінні оточення** (environment variables) — це пари «імʼя = значення», які операційна система передає кожній програмі. Через них зазвичай передають налаштування: режим роботи, адреси серверів, ключі доступу. Так їх не треба записувати в код.

У терміналі змінні можна подивитися і задати:

```bash
echo $HOME
APP_MODE=debug python3 main.py
```

У Python вони доступні через `os.environ` (поводиться як словник) або `os.getenv()`:

```python
import os

print("home:", os.environ["HOME"])

# getenv повертає None (або значення за замовчуванням), якщо змінної немає
mode = os.getenv("APP_MODE", "production")
print("mode:", mode)

# environ["..."] для відсутньої змінної кидає KeyError
try:
    print(os.environ["NO_SUCH_VARIABLE"])
except KeyError:
    print("variable is not set")
```

```bash
APP_MODE=debug python3 main.py
```

```text
home: /home/student
mode: debug
variable is not set
```

!!! note "Значення змінних оточення — завжди рядки"
    `os.getenv("WORKERS", "4")` поверне `"4"`, а не `4`. Якщо потрібне число, перетворюйте явно: `int(os.getenv("WORKERS", "4"))`.

### Інформація про систему

```python
import os

print("os name:", os.name)        # 'posix' для Linux/macOS
print("cpu count:", os.cpu_count())
print("separator:", os.sep)
print("pid:", os.getpid())        # номер процесу цієї програми
```

```text
os name: posix
cpu count: 8
separator: /
pid: 48213
```

## `sys` — інтерпретатор і запуск програми

Модуль `sys` дає доступ до самого інтерпретатора Python: як запущено програму, з якими аргументами, куди писати вивід, як завершитися.

### Аргументи командного рядка: `sys.argv`

З лекції 21 ви вже знаєте: усе, що написано після імені скрипта, потрапляє у список `sys.argv`. Елемент `sys.argv[0]` — імʼя самого скрипта, далі — аргументи, **завжди рядки**.

```python
# File: greet.py
import sys

print("argv:", sys.argv)

if len(sys.argv) < 2:
    print("usage: python3 greet.py <name> [times]")
    sys.exit(1)

name = sys.argv[1]
times = int(sys.argv[2]) if len(sys.argv) > 2 else 1

for _ in range(times):
    print(f"Hello, {name}!")
```

```bash
python3 greet.py Olena 2
```

```text
argv: ['greet.py', 'Olena', '2']
Hello, Olena!
Hello, Olena!
```

Для програм з багатьма параметрами (`--debug`, `--output file.txt`) замість ручного розбору `sys.argv` використовують модуль `argparse`.

### Завершення програми: `sys.exit()`

`sys.exit(code)` негайно завершує програму. **Код виходу** (exit code) повідомляє системі, чи успішно відпрацювала програма:

- `0` — успіх (за замовчуванням, якщо програма дійшла до кінця);
- будь-яке інше число — помилка.

Якщо передати рядок, він виводиться в stderr, а код виходу буде `1`.

```python
import sys
from pathlib import Path

filename = Path("config.txt")

if not filename.exists():
    sys.exit(f"error: file {filename} not found")

print("config found")
```

```bash
python3 main.py
echo "exit code: $?"
```

```text
error: file config.txt not found
exit code: 1
```

У терміналі `$?` показує код виходу останньої команди. Інші програми і скрипти (наприклад, CI на GitHub) перевіряють саме його, щоб зрозуміти, чи все пройшло добре.

### Стандартні потоки: `stdout`, `stderr`, `stdin`

Кожна програма має три стандартні потоки:

| Потік | Для чого | У Python |
|---|---|---|
| stdin | ввід (клавіатура) | `sys.stdin`, `input()` |
| stdout | звичайний вивід | `sys.stdout`, `print()` |
| stderr | повідомлення про помилки | `sys.stderr` |

Помилки варто писати в stderr: тоді, якщо вивід програми перенаправлено у файл, повідомлення про помилки все одно зʼявляться в терміналі.

```python
import sys

print("result: 42")
print("warning: input file is empty", file=sys.stderr)
```

```bash
python3 main.py > out.txt
cat out.txt
```

```text
warning: input file is empty
result: 42
```

Перший рядок зʼявився в терміналі (це stderr), а `result: 42` потрапив у файл `out.txt`.

`sys.stdin` дозволяє читати весь ввід, наприклад з конвеєра (pipe):

```python
# File: count_lines.py
import sys

lines = sys.stdin.readlines()
print("lines:", len(lines))
```

```bash
ls /etc | python3 count_lines.py
```

```text
lines: 214
```

### Інформація про інтерпретатор

```python
import sys

print("version:", sys.version)
print("version info:", sys.version_info.major, sys.version_info.minor)
print("platform:", sys.platform)
print("executable:", sys.executable)

# Де Python шукає модулі (лекція 27)
for path in sys.path:
    print("  ", path)
```

```text
version: 3.13.5 (main, Jun 25 2025, 18:55:22) [GCC 14.2.0]
version info: 3 13
platform: linux
executable: /home/student/projects/env/bin/python3
   /home/student/projects
   /usr/lib/python313.zip
   /usr/lib/python3.13
   ...
```

`sys.executable` корисний, щоб перевірити, чи активоване віртуальне оточення (лекція 02): шлях має вести всередину `env/`.

Перевірка мінімальної версії Python:

```python
import sys

if sys.version_info < (3, 10):
    sys.exit("error: Python 3.10 or newer is required")

print("Python version is OK")
```

```text
Python version is OK
```

## Приклад: усе разом

Програма генерує журнал оцінок для групи студентів: випадкові оцінки за кожен навчальний день (пн–пт), зберігає звіт у файл і виводить статистику. Кількість днів передається аргументом, каталог для звітів — змінною оточення.

```python
# File: journal.py
import math
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

STUDENTS = ["Olena", "Taras", "Iryna", "Andrii", "Marta"]


def parse_days() -> int:
    """Read number of days from command line, default 5."""
    if len(sys.argv) < 2:
        return 5
    try:
        days = int(sys.argv[1])
    except ValueError:
        sys.exit(f"error: days must be a number, got {sys.argv[1]!r}")
    if days <= 0:
        sys.exit("error: days must be positive")
    return days


def school_days(start: date, count: int) -> list[date]:
    """Return count working days (Mon-Fri) starting from start."""
    result = []
    current = start
    while len(result) < count:
        if current.weekday() < 5:
            result.append(current)
        current += timedelta(days=1)
    return result


def main() -> None:
    days = parse_days()
    report_dir = Path(os.getenv("REPORT_DIR", "reports"))
    report_dir.mkdir(parents=True, exist_ok=True)

    # Фіксоване зерно: однаковий журнал при кожному запуску
    random.seed(2026)

    dates = school_days(date.today(), days)
    grades = {name: [random.randint(60, 100) for _ in dates] for name in STUDENTS}

    filename = report_dir / f"journal_{date.today():%Y%m%d}.txt"
    with open(filename, "w") as file:
        header = "name".ljust(8) + " ".join(d.strftime("%d.%m") for d in dates)
        file.write(header + "\n")
        for name, scores in grades.items():
            file.write(name.ljust(8) + " ".join(f"{s:5}" for s in scores) + "\n")

    all_scores = [s for scores in grades.values() for s in scores]
    mean = sum(all_scores) / len(all_scores)
    spread = math.sqrt(sum((s - mean) ** 2 for s in all_scores) / len(all_scores))

    print(f"period: {dates[0]:%d.%m.%Y} - {dates[-1]:%d.%m.%Y}")
    print(f"saved: {filename.resolve()}")
    print(f"mean: {mean:.1f}, std dev: {spread:.1f}")
    print(f"best student: {max(grades, key=lambda n: sum(grades[n]))}")


if __name__ == "__main__":
    main()
```

```bash
REPORT_DIR=out python3 journal.py 3
cat out/journal_*.txt
```

```text
period: 12.10.2026 - 14.10.2026
saved: /home/student/projects/out/journal_20261011.txt
mean: 87.7, std dev: 10.6
best student: Iryna
name    12.10 13.10 14.10
Olena      67    80    92
Taras      92    66    74
Iryna      98    99    95
Andrii     86    96    95
Marta      91    97    88
```

Кожен модуль робить свою частину: `sys` — аргументи і вихід з помилкою, `os` — змінна оточення, `pathlib` — каталог і шлях до файлу, `datetime` — дні тижня та форматування, `random` — дані, `math` — обчислення.

## Типові помилки

| Помилка | Що відбувається | Як правильно |
|---|---|---|
| `import datetime`, потім `datetime.now()` | `AttributeError: module 'datetime' has no attribute 'now'` | `from datetime import datetime` або `datetime.datetime.now()` |
| `names = random.shuffle(names)` | `names` стає `None` — `shuffle` змінює список на місці | `random.shuffle(names)` без присвоєння |
| `random.randint(0, len(names))` як індекс | інколи `IndexError`: верхня межа включна | `random.choice(names)` або `randrange(len(names))` |
| `random` для паролів | значення можна передбачити | модуль `secrets` |
| `0.1 + 0.2 == 0.3` | `False` | `math.isclose(0.1 + 0.2, 0.3)` |
| `math.sin(30)` для 30 градусів | результат для 30 **радіан** | `math.sin(math.radians(30))` |
| `"data" + "/" + name` | ручна склейка шляхів | `Path("data") / name` |
| `os.path` у новому коді | шлях — рядок, функції розкидані по модулях | `pathlib.Path` |
| `int(os.environ["PORT"])` без перевірки | `KeyError`, якщо змінну не задано | `int(os.getenv("PORT", "8000"))` |
| `sys.argv[1]` без перевірки довжини | `IndexError`, якщо аргументів немає | перевірити `len(sys.argv)` |
| `sys.argv[1] + 1` | `TypeError`: аргументи — рядки | `int(sys.argv[1]) + 1` |
| Файл `random.py` у каталозі проєкту | затінює стандартний модуль (лекція 27) | інше імʼя файлу |

## Підсумок

- **`math`**: `pi`, `e`, `inf`; `sqrt`, `log`; округлення `floor`/`ceil`/`trunc`; `factorial`, `gcd`, `comb`; кути в радіанах (`radians`); порівняння `float` через `isclose`.
- **`random`**: `random()`, `randint(a, b)` (обидві межі включно), `uniform`, `choice`, `sample` (без повторів), `choices` (з повторами і вагами), `shuffle` (на місці); `seed` для відтворюваності. Для паролів — `secrets`.
- **`datetime`**: `date`, `datetime`, `timedelta`; `today()`/`now()`; арифметика і порівняння дат; `strftime` — дата в рядок, `strptime` — рядок у дату; `isoformat`/`fromisoformat`.
- **`os`**: змінні оточення (`os.environ`, `os.getenv`), інформація про систему (`os.name`, `os.cpu_count`, `os.getpid`). Шляхи, файли і каталоги раніше обробляли через `os`/`os.path`, тепер — через `pathlib`: шлях є обʼєктом, усе зібрано в одному класі, код коротший.
- **`sys`**: `sys.argv` — аргументи (рядки); `sys.exit(code)` — завершення з кодом виходу; `sys.stdout`/`sys.stderr`/`sys.stdin`; `sys.version_info`, `sys.executable`, `sys.path`.

## Корисні посилання

- [`math` — Mathematical functions](https://docs.python.org/3/library/math.html)
- [`random` — Generate pseudo-random numbers](https://docs.python.org/3/library/random.html)
- [`secrets` — Generate secure random numbers](https://docs.python.org/3/library/secrets.html)
- [`datetime` — Basic date and time types](https://docs.python.org/3/library/datetime.html)
- [`strftime()` and `strptime()` format codes](https://docs.python.org/3/library/datetime.html#format-codes)
- [`os` — Miscellaneous operating system interfaces](https://docs.python.org/3/library/os.html)
- [`sys` — System-specific parameters and functions](https://docs.python.org/3/library/sys.html)

## Домашнє завдання

Усі дані — **ваші власні**, латиницею. Для кожного завдання покажіть код, команду запуску і вивід.

1. **`math`.** Напишіть функцію `circle_info(radius: float) -> dict`, яка повертає довжину кола, площу кола і площу вписаного квадрата. Радіус — номер вашого дня народження. Округліть результати трьома способами (`floor`, `ceil`, `round`) і поясніть різницю. Окремо покажіть, що `0.1 * 3 == 0.3` дає `False`, і виправте порівняння.

2. **`math`.** Скільки способів вибрати старосту і заступника з вашої групи (порядок важливий) і скільки способів вибрати команду з 3 людей (порядок не важливий)? Обчисліть через `math.perm` і `math.comb`, перевірте результат через `math.factorial`.

3. **`random`.** Напишіть програму «Розподіл тем доповідей»: список з 5–8 прізвищ одногрупників (включно з вашим) і список тем. Кожен студент отримує унікальну тему (`random.sample`), черговість виступів — `random.shuffle`. Задайте `seed` рівним вашому року народження і покажіть, що два запуски дають однаковий результат, а без `seed` — різний.

4. **`random`.** Змоделюйте 10 000 кидків двох кубиків і порахуйте, як часто випадає кожна сума від 2 до 12. Виведіть таблицю з відсотками. Яка сума найчастіша і чому?

5. **`datetime`.** Програма приймає вашу дату народження рядком у форматі `DD.MM.YYYY` і виводить: вік у роках, кількість прожитих днів, день тижня, у який ви народилися (`%A`), скільки днів до наступного дня народження і на який день тижня він припаде. Неправильний формат дати має оброблятися через `try`/`except`.

6. **`datetime`.** Згенеруйте розклад занять: перша пара — у найближчий понеділок о 08:30, тривалість пари — 1 год 20 хв, перерва — 10 хв. Виведіть час початку і кінця чотирьох пар у форматі `HH:MM - HH:MM`.

7. **`os`.** Напишіть програму `env_info.py`, яка виводить: імʼя користувача (`USER`), домашній каталог (`HOME`), кількість ядер процесора, `os.name` і PID процесу. Додайте власне налаштування через змінну оточення `GREETING_NAME` (за замовчуванням — ваше імʼя) та `GREETING_TIMES` (число, за замовчуванням `1`): програма вітається вказану кількість разів. Покажіть запуск без змінних, з обома змінними і з `GREETING_TIMES=abc` (оброблена помилка).

8. **`os` + `sys`.** Напишіть скрипт `backup.py <file>`, який створює копію файлу з датою в назві в каталозі, заданому змінною оточення `BACKUP_DIR` (за замовчуванням `backups`), наприклад `notes_20261011_1430.txt`. Якщо аргумент не передано або файлу не існує — повідомлення в stderr і `sys.exit` з кодом `1` або `2` відповідно. Покажіть `echo $?` після кожного з трьох випадків.

9. **`sys`.** Напишіть фільтр `stats.py`, який читає числа з `sys.stdin` (по одному в рядку) і виводить кількість, мінімум, максимум, середнє і медіану. Нечислові рядки пропускайте з попередженням у stderr. Покажіть запуск з конвеєром: `printf "5\n3\nabc\n10\n" | python3 stats.py` і з перенаправленням stderr у файл: `... 2> errors.txt`.
