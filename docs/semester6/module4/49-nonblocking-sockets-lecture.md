# 49. (Л) Основи роботи з неблокуючими сокетами

## Зміст лекції

1. Від «чекати» до «спитати й піти далі»
2. `setblocking(False)`
3. Неблокуючий `accept`
4. Неблокуючий `recv`
5. Неблокуючий `send`: буфер ОС і часткове надсилання
6. Неблокуючий `connect`
7. Стан кожного клієнта
8. Сервер з опитуванням (polling)
9. Ціна опитування: 100 % процесора
10. Пауза в циклі — компроміс
11. Що потрібно насправді: повідомлення від ОС
12. Типові помилки

## Від «чекати» до «спитати й піти далі»

У лекції 47 ми побачили: блокуючий виклик зупиняє весь потік, тому один потік не може обслуговувати кількох клієнтів. **Неблокуючий** сокет змінює поведінку кожного виклику:

| Виклик | Блокуючий сокет | Неблокуючий сокет |
|---|---|---|
| `accept()` без клієнтів | чекає | одразу `BlockingIOError` |
| `recv()` без даних | чекає | одразу `BlockingIOError` |
| `send()` при повному буфері | чекає | надсилає скільки може або `BlockingIOError` |
| `connect()` | чекає завершення рукостискання | одразу повертається, рукостискання триває у фоні |

`BlockingIOError` тут — не помилка, а відповідь «зараз нічого немає, спробуй пізніше». Програма може піти обслуговувати інших клієнтів і повернутися до цього сокета пізніше.

## `setblocking(False)`

| Запис | Режим |
|---|---|
| `sock.setblocking(True)` / `settimeout(None)` | блокуючий (типово) |
| `sock.settimeout(2)` | блокуючий з тайм-аутом |
| `sock.setblocking(False)` / `settimeout(0)` | **неблокуючий** |

```python
# Program: switch a socket to non-blocking mode
import socket

sock = socket.socket()
print("blocking:", sock.getblocking(), "timeout:", sock.gettimeout())
sock.setblocking(False)
print("blocking:", sock.getblocking(), "timeout:", sock.gettimeout())
sock.close()
```

```text
blocking: True timeout: None
blocking: False timeout: 0.0
```

Режим задають окремо для **кожного** сокета: слухаючого і кожного сокета зʼєднання, повернутого `accept()`.

## Неблокуючий `accept`

```python
# Program: accept does not wait on a non-blocking socket
import socket

server = socket.create_server(("127.0.0.1", 0))
server.setblocking(False)
try:
    server.accept()
except BlockingIOError as error:
    print("no clients yet:", error.strerror)

client = socket.create_connection(server.getsockname())
conn, address = server.accept()  # тепер клієнт є в черзі — accept повертається одразу
print("accepted:", address == client.getsockname())
print("new socket is blocking:", conn.getblocking())
for s in (conn, client, server):
    s.close()
```

```text
no clients yet: Resource temporarily unavailable
accepted: True
new socket is blocking: True
```

Зверніть увагу: сокет, повернутий `accept()`, на Linux **блокуючий**, навіть якщо слухаючий — неблокуючий. Його треба перевести в неблокуючий режим окремо.

## Неблокуючий `recv`

```python
# Program: non-blocking recv returns data, raises BlockingIOError or returns b""
import socket
import time


def try_recv(sock: socket.socket) -> str:
    try:
        data = sock.recv(1024)
    except BlockingIOError:
        return "no data yet"
    return "peer closed" if data == b"" else f"data {data!r}"


server = socket.create_server(("127.0.0.1", 0))
client = socket.create_connection(server.getsockname())
conn, _ = server.accept()
conn.setblocking(False)

print(try_recv(conn))
client.sendall(b"hello")
client.sendall(b" world")
time.sleep(0.05)  # даємо даним дійти
print(try_recv(conn))
print(try_recv(conn))
client.close()
time.sleep(0.05)
print(try_recv(conn))
conn.close()
server.close()
```

```text
no data yet
data b'hello world'
no data yet
peer closed
```

Три можливі результати неблокуючого `recv` — і кожен треба обробити:

| Результат | Значення | Дія сервера |
|---|---|---|
| байти | прийшли дані | обробити |
| `BlockingIOError` | даних поки немає | перейти до інших сокетів |
| `b""` | клієнт закрив зʼєднання | закрити сокет, видалити стан клієнта |

## Неблокуючий `send`: буфер ОС і часткове надсилання

`send` не передає дані в мережу напряму: він копіює їх у **буфер надсилання** ОС, а ядро вже відправляє їх, коли дозволяє вікно TCP (лекція 45). Якщо отримувач не читає, буфер заповнюється:

- блокуючий `sendall` у такому разі **чекає** — і зупиняє весь сервер;
- неблокуючий `send` надсилає **скільки вміщується** і повертає кількість байтів, а при повному буфері генерує `BlockingIOError`.

```python
# Program: a non-blocking send accepts only what fits into the OS buffer
import socket

server = socket.create_server(("127.0.0.1", 0))
client = socket.create_connection(server.getsockname())
conn, _ = server.accept()
conn.setblocking(False)

big = b"x" * 50_000_000  # 50 МБ, а клієнт нічого не читає
sent_total = 0
while True:
    try:
        sent = conn.send(big[sent_total:])
    except BlockingIOError:
        break
    sent_total += sent
print("buffer is full after", sent_total < len(big))
print("bytes still waiting in the program:", len(big) - sent_total > 0)
for s in (conn, client, server):
    s.close()
```

```text
buffer is full after True
bytes still waiting in the program: True
```

Тому неблокуючий сервер зберігає для кожного клієнта **вихідний буфер** — байти, які ще не вдалося надіслати, — і дописує їх пізніше, коли сокет знову буде готовий до запису.

## Неблокуючий `connect`

Неблокуючий `connect` одразу повертається з помилкою «операція в процесі» (`BlockingIOError`, errno `EINPROGRESS`), а рукостискання триває у фоні. Результат зручно отримати через `connect_ex`, що повертає код помилки замість винятку:

```python
# Program: a non-blocking connect completes in the background
import errno
import socket
import time

server = socket.create_server(("127.0.0.1", 0))
client = socket.socket()
client.setblocking(False)
code = client.connect_ex(server.getsockname())
print("first call:", errno.errorcode.get(code, "OK"))
time.sleep(0.05)
print("later, SO_ERROR:", client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR), "(0 means connected)")
client.close()
server.close()
```

```text
first call: EINPROGRESS
later, SO_ERROR: 0 (0 means connected)
```

На `localhost` зʼєднання інколи встановлюється миттєво, і перший виклик поверне `OK`. У реальній мережі `connect` триває один RTT, і саме тоді неблокуючий режим корисний: можна відкривати сотні зʼєднань паралельно.

## Стан кожного клієнта

Блокуючий обробник з лекції 46 зберігав стан у **локальних змінних** функції: поки потік чекає в `recv`, змінні «живуть» у стеку. Неблокуючий сервер обробляє клієнтів шматочками, по черзі, тому стан кожного треба зберігати **явно** — наприклад, у словнику за сокетом:

```python
# Program: per-client state for a non-blocking server
from dataclasses import dataclass, field


@dataclass
class Client:
    address: tuple
    inbox: bytes = b""          # отримано, але ще не оброблено (неповний рядок)
    outbox: bytes = b""         # треба надіслати, але буфер ОС був повний
    messages: int = 0


def on_data(client: Client, data: bytes) -> None:
    client.inbox += data
    while b"\n" in client.inbox:
        line, client.inbox = client.inbox.split(b"\n", 1)
        client.messages += 1
        client.outbox += b"echo: " + line + b"\n"


state = Client(("127.0.0.1", 51000))
for chunk in (b"hel", b"lo\nwor", b"ld\nunfinished"):
    on_data(state, chunk)
print(state)
```

```text
Client(address=('127.0.0.1', 51000), inbox=b'unfinished', outbox=b'echo: hello\necho: world\n', messages=2)
```

Дані приходять шматками (`hel`, `lo\nwor`), але завдяки буферу `inbox` сервер правильно виділяє повні рядки, а неповний `unfinished` чекає продовження.

## Сервер з опитуванням (polling)

Поєднаємо все: один потік у нескінченному циклі по черзі «питає» слухаючий сокет і кожного клієнта:

```python
# File: polling_echo.py
import socket

HOST, PORT = "127.0.0.1", 8888


def serve(server: socket.socket, max_loops: int | None = None) -> None:
    server.setblocking(False)
    clients: dict[socket.socket, bytes] = {}  # сокет -> вихідний буфер
    loops = 0
    while max_loops is None or loops < max_loops:
        loops += 1
        try:
            conn, address = server.accept()
            conn.setblocking(False)
            clients[conn] = b""
            print(f"connected {address[1] > 0}")
        except BlockingIOError:
            pass

        for conn in list(clients):
            try:
                data = conn.recv(1024)
            except BlockingIOError:
                data = None
            except ConnectionResetError:
                data = b""
            if data == b"":
                print("disconnected")
                del clients[conn]
                conn.close()
                continue
            if data:
                clients[conn] += data
            if clients[conn]:
                try:
                    sent = conn.send(clients[conn])
                    clients[conn] = clients[conn][sent:]
                except BlockingIOError:
                    pass


if __name__ == "__main__":
    with socket.create_server((HOST, PORT)) as srv:
        print(f"polling echo on {HOST}:{PORT}")
        try:
            serve(srv)
        except KeyboardInterrupt:
            print("stopped")
```

```python
# Program: three clients served by one thread with polling
import socket
import threading
import time

import polling_echo

server = socket.create_server(("127.0.0.1", 0))
thread = threading.Thread(target=polling_echo.serve, args=(server,), daemon=True)
thread.start()

clients = [socket.create_connection(server.getsockname(), timeout=1) for _ in range(3)]
time.sleep(0.1)
for number, client in enumerate(clients):
    client.sendall(f"message {number}".encode())
print([client.recv(100) for client in clients])
for client in clients:
    client.close()
time.sleep(0.1)
server.close()
```

```text
connected True
connected True
connected True
[b'message 0', b'message 1', b'message 2']
disconnected
disconnected
disconnected
```

Один потік обслуговує трьох клієнтів, і жоден не чекає інших. Але є серйозна проблема.

## Ціна опитування: 100 % процесора

Цикл `while True` крутиться **безперервно**, навіть коли нічого не відбувається: мільйони викликів `accept` і `recv`, що лише генерують `BlockingIOError`. Таке очікування називають **активним** (busy waiting):

```python
# Program: how many useless loop iterations polling makes while idle
import socket
import time

server = socket.create_server(("127.0.0.1", 0))
server.setblocking(False)
loops = 0
cpu_start, wall_start = time.process_time(), time.perf_counter()
while time.perf_counter() - wall_start < 0.5:
    loops += 1
    try:
        server.accept()
    except BlockingIOError:
        pass
cpu = time.process_time() - cpu_start
print(f"idle loops in 0.5 s: more than 100000: {loops > 100_000}")
print(f"cpu time is close to wall time (busy waiting): {cpu > 0.4}")
server.close()
```

```text
idle loops in 0.5 s: more than 100000: True
cpu time is close to wall time (busy waiting): True
```

`time.process_time()` рахує процесорний час програми. Він майже дорівнює реальному: сервер без жодного клієнта займає ціле ядро процесора. На ноутбуці це розряджає батарею, на сервері — забирає ресурси в інших програм.

## Пауза в циклі — компроміс

Можна додати `time.sleep(0.01)` в кінці кожної ітерації. Навантаження на процесор впаде майже до нуля, але зʼявиться **затримка** відповіді до 10 мс, а за великої кількості клієнтів цикл однаково перебиратиме всі сокети, більшість з яких нічого не надіслали.

| Варіант | Процесор у простої | Затримка відповіді |
|---|---|---|
| опитування без паузи | ≈ 100 % ядра | мінімальна |
| опитування з `sleep(0.01)` | ≈ 0 % | до 10 мс |
| `selectors` (лекція 51) | ≈ 0 % | мінімальна |

## Що потрібно насправді: повідомлення від ОС

Ідеальний варіант: потік **спить**, поки нічого не відбувається, і прокидається **одразу**, коли якийсь сокет готовий. Операційна система це вміє — системні виклики `select`, `poll`, `epoll`, `kqueue`. Модуль `selectors` дає до них єдиний інтерфейс (лекція 34, детально — лекція 51):

```python
# Program: selectors wakes up only when a socket is ready
import selectors
import socket
import threading
import time

server = socket.create_server(("127.0.0.1", 0))
server.setblocking(False)
selector = selectors.DefaultSelector()
selector.register(server, selectors.EVENT_READ)

threading.Timer(0.5, socket.create_connection, (server.getsockname(),)).start()
cpu_start, wall_start = time.process_time(), time.perf_counter()
events = selector.select(timeout=2)  # спить, доки не підключиться клієнт
print(f"woke up after {time.perf_counter() - wall_start:.1f}s with {len(events)} ready socket")
print(f"cpu time while waiting is tiny: {time.process_time() - cpu_start < 0.05}")
conn, _ = server.accept()
conn.close()
selector.close()
server.close()
```

```text
woke up after 0.5s with 1 ready socket
cpu time while waiting is tiny: True
```

Пів секунди очікування — і майже нуль процесорного часу.

## Типові помилки

| Помилка | Чому погано | Як правильно |
|---|---|---|
| Не обробляють `BlockingIOError` | виняток зупиняє сервер | `except BlockingIOError` |
| Не переводять сокет з `accept()` у неблокуючий режим | `recv` блокує весь цикл | `conn.setblocking(False)` |
| `sendall` на неблокуючому сокеті | `BlockingIOError` посеред надсилання, частина даних втрачена | `send` + вихідний буфер |
| Не перевіряють `b""` | закриті клієнти лишаються в словнику | закрити й видалити |
| Стан клієнта в локальних змінних | губиться між ітераціями | словник / обʼєкт стану на клієнта |
| Опитування без паузи | 100 % процесора в простої | `selectors` |
| Перебирають словник і змінюють його | `RuntimeError: dictionary changed size` | `for conn in list(clients)` |

## Підсумок

- `setblocking(False)` робить `accept`, `recv`, `send`, `connect` миттєвими: якщо операцію виконати неможливо — `BlockingIOError` (або `EINPROGRESS` для `connect`).
- Неблокуючий `recv` має три результати: дані, `BlockingIOError`, `b""`.
- Неблокуючий `send` може надіслати лише частину; решту зберігають у вихідному буфері клієнта.
- Стан кожного клієнта (вхідний і вихідний буфери) зберігають явно.
- Сервер з **опитуванням** обслуговує багатьох клієнтів одним потоком, але займає 100 % процесора в простої.
- Розвʼязання — чекати повідомлення від ОС про готовність сокетів (`selectors`).

## Корисні посилання

- [Модуль `socket` — `setblocking` і тайм-аути](https://docs.python.org/3/library/socket.html#socket-timeouts)
- [Python Socket Programming HOWTO — Non-blocking Sockets](https://docs.python.org/3/howto/sockets.html#non-blocking-sockets)
- [Модуль `selectors` — довідник](https://docs.python.org/3/library/selectors.html)
- [Real Python — Socket Programming: Handling Multiple Connections](https://realpython.com/python-sockets/#handling-multiple-connections)
- Fowler M. Python Concurrency with asyncio. — Manning, 2022. — Розділ 3.
