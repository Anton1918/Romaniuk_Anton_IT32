# 22. (Л) Обробка помилок. Налаштування застосунку

## Зміст лекції

1. Два види проблем: очікувані помилки і баги
2. Очікувані помилки: повідомити й продовжити
3. Що відбувається з винятком в обробнику Qt
4. Глобальний перехоплювач `sys.excepthook`
5. Журнал застосунку
6. Де зберігати файли застосунку: `QStandardPaths`
7. Налаштування: `QSettings`
8. Типи значень і значення за замовчуванням
9. Групи налаштувань
10. Що зберігати в налаштуваннях
11. Відновлення стану вікна при запуску
12. Експорт та імпорт налаштувань у JSON
13. Повний приклад
14. Типові помилки

## Два види проблем: очікувані помилки і баги

| | Очікувані помилки | Баги (помилки програміста) |
|---|---|---|
| приклади | файл не знайдено, немає мережі, неправильний формат CSV, диск заповнений | `KeyError`, `AttributeError`, `ZeroDivisionError` у коді |
| хто винен | обставини або дані користувача | код |
| що робити | зрозуміле повідомлення, застосунок працює далі | записати подробиці в журнал, повідомити користувача, виправити в наступній версії |
| як ловити | конкретні винятки в місці виникнення | глобальний перехоплювач |

Обидва види потребують обробки, але по-різному. Очікувані помилки ловлять **точково** (лекція 23, 5 семестр), а баги — **на верхньому рівні**, щоб застосунок не зник без пояснень.

## Очікувані помилки: повідомити й продовжити

Повідомлення для користувача відповідає на три питання: **що сталося**, **чому** і **що робити**:

| Погано | Добре |
|---|---|
| `[Errno 2] No such file or directory: '/home/student/september.csv'` | *Can not open september.csv. The file was moved or deleted. Choose another file.* |
| `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` | *settings.json is damaged. Default settings are used.* |

```python
# Program: translate technical exceptions into user messages
import json
from pathlib import Path


def user_message(exc: Exception, path: Path) -> str:
    if isinstance(exc, FileNotFoundError):
        return f"Can not open {path.name}: the file was moved or deleted."
    if isinstance(exc, PermissionError):
        return f"No permission to read {path.name}."
    if isinstance(exc, (UnicodeDecodeError, json.JSONDecodeError, ValueError)):
        return f"{path.name} is damaged or has a wrong format."
    return f"Unexpected problem with {path.name}."


for path, action in [(Path("missing.json"), lambda p: p.read_text()),
                     (Path("bad.json"), lambda p: json.loads("{not json"))]:
    try:
        action(path)
    except Exception as exc:
        print(user_message(exc, path))
```

```text
Can not open missing.json: the file was moved or deleted.
bad.json is damaged or has a wrong format.
```

У застосунку текст показують у `QMessageBox` (лекція 11) або в рядку стану, а технічні подробиці — у журнал.

## Що відбувається з винятком в обробнику Qt

Якщо в слоті (обробнику сигналу) виник виняток, PySide6 **друкує трасування в stderr і продовжує роботу**. Застосунок не падає, але користувач нічого не бачить: кнопка «не працює», і незрозуміло чому. Якщо застосунок запущено без терміналу (з меню ОС), трасування зникає зовсім.

```python
# Program: an exception in a slot does not stop the application
import sys

from PySide6.QtWidgets import QApplication, QPushButton

app = QApplication(sys.argv)
button = QPushButton("Report")
clicks = []


def broken_report() -> None:
    clicks.append(1)
    totals = {"food": 270.5}
    # баг: такого ключа немає
    print(totals["fun"])


button.clicked.connect(broken_report)
button.click()
button.click()
print("handler was called", len(clicks), "times, the application is still alive")
```

```text
handler was called 2 times, the application is still alive
```

У терміналі при цьому двічі зʼявиться трасування `KeyError: 'fun'` — але лише в терміналі.

## Глобальний перехоплювач `sys.excepthook`

`sys.excepthook` — функція, яку Python викликає для **кожного необробленого винятку**. PySide6 теж викликає її для винятків у слотах. Замінивши її власною, можна записати трасування в журнал і показати користувачу повідомлення:

```python
# Program: a global exception hook logs the traceback and informs the user
import logging
import sys
import traceback

from PySide6.QtWidgets import QApplication, QPushButton

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout)
log = logging.getLogger("expenses")
shown_to_user = []


def excepthook(exc_type, exc_value, exc_tb) -> None:
    details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.error("unhandled exception\n%s", details.splitlines()[-1])
    # у застосунку: QMessageBox.critical(None, "Error", "...")
    shown_to_user.append("Something went wrong. The details are saved in the log file.")


sys.excepthook = excepthook
app = QApplication(sys.argv)
button = QPushButton("Report")
button.clicked.connect(lambda: {"food": 270.5}["fun"])
button.click()
print("user saw:", shown_to_user)
```

```text
ERROR unhandled exception
KeyError: 'fun'
user saw: ['Something went wrong. The details are saved in the log file.']
```

У прикладі до журналу потрапляє лише останній рядок трасування, щоб вивід був коротким; у застосунку записують `details` повністю. Перехоплювач — **страховка**, а не заміна точкової обробки: очікувані помилки ловлять там, де їх можна правильно обробити.

## Журнал застосунку

Журнал (модуль `logging`, лекція 26 5 семестру) записують **у файл**: користувач може надіслати його розробнику. Налаштовують його один раз у `main.py`:

```python
# Program: log to a rotating file and to the console
import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_dir = Path(tempfile.mkdtemp())
file_handler = RotatingFileHandler(log_dir / "expenses.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console])

log = logging.getLogger("expenses.storage")
log.info("opened september.csv, 12 rows")
log.warning("row 7 skipped: amount is not a number")

for handler in logging.getLogger().handlers:
    handler.flush()
lines = (log_dir / "expenses.log").read_text(encoding="utf-8").splitlines()
print([line.split(" ", 2)[2] for line in lines])
```

```text
WARNING:expenses.storage:row 7 skipped: amount is not a number
['INFO expenses.storage: opened september.csv, 12 rows', 'WARNING expenses.storage: row 7 skipped: amount is not a number']
```

Перший рядок виводу надрукував консольний обробник: він показує лише `WARNING` і серйозніші. У файл потрапили обидва записи. `RotatingFileHandler` не дає журналу рости без меж: після 1 МБ файл перейменовується в `expenses.log.1`, зберігаються 3 старі файли.

## Де зберігати файли застосунку: `QStandardPaths`

Журнали, кеш, бази даних застосунку не кладуть поруч з програмою (там може не бути прав на запис) і не «засмічують» домашній каталог. Кожна ОС має стандартні місця, і `QStandardPaths` їх знає:

```python
# Program: standard locations for application data
import sys

from PySide6.QtCore import QDir, QStandardPaths
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
app.setOrganizationName("demo-college")
app.setApplicationName("Expenses")
for kind in ("AppDataLocation", "CacheLocation", "DocumentsLocation"):
    location = getattr(QStandardPaths.StandardLocation, kind)
    path = QStandardPaths.writableLocation(location)
    print(f"{kind:<18} {path.replace(QDir.homePath(), '~')}")
```

```text
AppDataLocation    ~/.local/share/demo-college/Expenses
CacheLocation      ~/.cache/demo-college/Expenses
DocumentsLocation  ~/Documents
```

Шляхи на Linux. На macOS `AppDataLocation` — `~/Library/Application Support/Expenses`. Каталог створюють перед записом: `Path(path).mkdir(parents=True, exist_ok=True)`.

## Налаштування: `QSettings`

`QSettings` зберігає пари «ключ — значення» між запусками застосунку у стандартному для ОС місці:

| ОС | Де зберігається |
|---|---|
| Linux | `~/.config/<Organization>/<Application>.conf` (текстовий INI) |
| macOS | `~/Library/Preferences/com.<organization>.<Application>.plist` |

```python
# Program: write, read and remove settings
import sys

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
settings = QSettings("demo-college", "expenses-lecture")
settings.setValue("last_file", "/home/student/september.csv")
settings.setValue("monthly_budget", 8000)

print("last file:", settings.value("last_file"))
print("keys:", sorted(settings.allKeys()))
print("file ends with:", settings.fileName().split("/")[-2:])
settings.remove("last_file")
print("after remove:", settings.value("last_file"))
settings.clear()
```

```text
last file: /home/student/september.csv
keys: ['last_file', 'monthly_budget']
file ends with: ['demo-college', 'expenses-lecture.conf']
after remove: None
```

Якщо в `main.py` задано `app.setOrganizationName(...)` і `app.setApplicationName(...)`, далі достатньо писати `QSettings()` без аргументів.

## Типи значень і значення за замовчуванням

На Linux налаштування зберігаються в текстовому файлі, і при читанні число може повернутися **рядком**. Тому тип вказують явно параметром `type`, а відсутній ключ замінюють значенням `defaultValue`:

```python
# Program: read settings with types and defaults
import shutil
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
settings = QSettings("demo-college", "expenses-lecture")
settings.setValue("budget", 8000)
settings.setValue("dark_mode", True)
settings.sync()  # записати на диск зараз
print(Path(settings.fileName()).read_text().split())

# копія файлу імітує читання «після перезапуску», коли значення беруться з диска
copy = Path(tempfile.mkdtemp()) / "copy.conf"
shutil.copy(settings.fileName(), copy)
fresh = QSettings(str(copy), QSettings.Format.IniFormat)
print("without type:", repr(fresh.value("budget")), repr(fresh.value("dark_mode")))
print("with type:   ", fresh.value("budget", 5000, type=int), fresh.value("dark_mode", False, type=bool))
print("missing key: ", fresh.value("currency", "UAH", type=str))
settings.clear()
```

```text
['[General]', 'budget=8000', 'dark_mode=true']
without type: '8000' 'true'
with type:    8000 True
missing key:  UAH
```

`'true'` без вказаного типу — непорожній рядок, тож `if settings.value("dark_mode"):` спрацює навіть для `'false'`. Завжди вказуйте `type`.

## Групи налаштувань

Повʼязані ключі обʼєднують у **групи** (секції INI-файлу):

```python
# Program: grouped settings for category limits
import sys

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
settings = QSettings("demo-college", "expenses-lecture")
settings.beginGroup("limits")
for category, limit in {"food": 3000.0, "fun": 1000.0}.items():
    settings.setValue(category, limit)
settings.endGroup()

settings.beginGroup("limits")
limits = {key: settings.value(key, type=float) for key in settings.childKeys()}
settings.endGroup()
print(limits)
print("full key:", [k for k in settings.allKeys() if k.endswith("food")])
settings.clear()
```

```text
{'food': 3000.0, 'fun': 1000.0}
full key: ['limits/food']
```

## Що зберігати в налаштуваннях

| Так | Ні |
|---|---|
| розмір і положення вікна, розташування панелей | самі дані (витрати) — для них файл чи база |
| останній відкритий файл і каталог | паролі й токени у відкритому вигляді |
| вибрані користувачем параметри: ліміти, тема, мова | великі обʼєкти |
| ширина стовпців таблиці | тимчасовий стан, що не потрібен після перезапуску |

## Відновлення стану вікна при запуску

```python
# Program: the window restores its size and last folder after a restart
import sys

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QMainWindow


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("demo-college", "expenses-lecture")
        geometry = self.settings.value("window/geometry")
        if geometry is None or not self.restoreGeometry(geometry):
            self.resize(700, 450)  # перший запуск — розмір за замовчуванням
        self.last_folder = self.settings.value("window/last_folder", "", type=str)

    def closeEvent(self, event) -> None:
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/last_folder", self.last_folder)
        super().closeEvent(event)


app = QApplication(sys.argv)
first = Window()
print("first run folder:", repr(first.last_folder))
first.last_folder = "/home/student/expenses"
first.show()
first.close()

second = Window()
print("second run folder:", second.last_folder)
second.settings.clear()
```

```text
first run folder: ''
second run folder: /home/student/expenses
```

`restoreGeometry` повертає `False` для пошкоджених даних — тоді застосунок відкриється з розміром за замовчуванням. Якщо монітор, на якому було вікно, відʼєднали, Qt сам перенесе вікно на доступний екран.

## Експорт та імпорт налаштувань у JSON

Налаштування можна перенести на інший компʼютер, експортувавши у JSON (лекція 35, 5 семестр). Під час імпорту файл **перевіряють**: пошкоджений чи чужий файл не повинен зламати поточні налаштування:

```python
# File: settings_io.py
import json
from pathlib import Path

from PySide6.QtCore import QSettings

ALLOWED = {"budget": int, "currency": str, "dark_mode": bool}


def export_settings(settings: QSettings, path: Path) -> None:
    data = {key: settings.value(key, type=kind) for key, kind in ALLOWED.items() if settings.contains(key)}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def import_settings(settings: QSettings, path: Path) -> list[str]:
    """Validate first, change settings only if everything is correct. Return a list of problems."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"can not read file: {type(exc).__name__}"]
    if not isinstance(data, dict):
        return ["JSON object expected"]
    problems = [f"{key}: unknown setting" for key in data if key not in ALLOWED]
    problems += [f"{key}: {ALLOWED[key].__name__} expected" for key, value in data.items()
                 if key in ALLOWED and type(value) is not ALLOWED[key]]
    if problems:
        return problems
    for key, value in data.items():
        settings.setValue(key, value)
    return []
```

```python
# Program: export settings and reject a damaged import
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from settings_io import export_settings, import_settings

app = QApplication(sys.argv)
folder = Path(tempfile.mkdtemp())
settings = QSettings("demo-college", "expenses-lecture")
settings.setValue("budget", 8000)
settings.setValue("dark_mode", True)
export_settings(settings, folder / "settings.json")
print((folder / "settings.json").read_text(encoding="utf-8").replace("\n", " "))

(folder / "bad.json").write_text('{"budget": "a lot", "theme": "pink"}', encoding="utf-8")
print("problems:", import_settings(settings, folder / "bad.json"))
print("budget unchanged:", settings.value("budget", type=int))
(folder / "broken.json").write_text("{", encoding="utf-8")
print("problems:", import_settings(settings, folder / "broken.json"))
settings.clear()
```

```text
{   "budget": 8000,   "dark_mode": true }
problems: ['theme: unknown setting', 'budget: int expected']
budget unchanged: 8000
problems: ['can not read file: JSONDecodeError']
```

## Повний приклад

```python
# File: app_main.py
import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox

log = logging.getLogger("expenses")


def setup_logging() -> Path:
    folder = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    folder.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(folder / "expenses.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    return folder / "expenses.log"


def install_excepthook(log_path: Path) -> None:
    def excepthook(exc_type, exc_value, exc_tb) -> None:
        log.error("unhandled exception\n%s", "".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
        QMessageBox.critical(None, "Expenses", f"Something went wrong.\nDetails are saved in:\n{log_path}")
    sys.excepthook = excepthook


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings()
        if not self.restoreGeometry(self.settings.value("geometry", b"")):
            self.resize(640, 400)
        budget = self.settings.value("budget", 8000, type=int)
        self.setCentralWidget(QLabel(f"Monthly budget: {budget} UAH"))
        self.menuBar().addMenu("&Debug").addAction("&Crash", self.crash)

    def crash(self) -> None:
        raise RuntimeError("test error from the Debug menu")

    def closeEvent(self, event) -> None:
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("demo-college")
    app.setApplicationName("Expenses")
    log_path = setup_logging()
    install_excepthook(log_path)
    log.info("application started")
    window = MainWindow()
    window.show()
    code = app.exec()
    log.info("application finished with code %s", code)
    return code


if __name__ == "__main__":
    sys.exit(main())
```

Пункт меню *Debug → Crash* перевіряє, що перехоплювач працює: зʼявляється повідомлення з шляхом до журналу, а в журналі — повне трасування `RuntimeError`.

## Типові помилки

| Помилка | Чому погано | Як правильно |
|---|---|---|
| Користувачу показують трасування | незрозуміло й лякає | людське повідомлення, трасування — у журнал |
| `except Exception: pass` | помилки зникають без сліду | конкретні винятки; журнал |
| Немає глобального перехоплювача | у застосунку без терміналу помилки невидимі | `sys.excepthook` |
| Журнал поруч з програмою | немає прав на запис після встановлення | `QStandardPaths.AppDataLocation` |
| `settings.value(key)` без `type` | `'false'` як істина, `'8000'` як рядок | `type=bool`, `type=int` |
| Немає значення за замовчуванням | `None` при першому запуску | `defaultValue` |
| Дані застосунку в `QSettings` | налаштування не для великих даних | файл або база даних |
| Імпорт без перевірки | пошкоджений файл ламає налаштування | перевірити все, потім застосувати |
| Паролі в `QSettings` | читаються з текстового файлу | системне сховище секретів (keyring) |

## Підсумок

- Розрізняйте **очікувані помилки** (обробляти точково, зрозуміле повідомлення) і **баги** (журнал і глобальний перехоплювач).
- Виняток у слоті Qt не зупиняє застосунок, але без перехоплювача його видно лише в терміналі.
- `sys.excepthook` записує трасування в журнал і показує користувачу повідомлення.
- Журнал пишуть у файл (`RotatingFileHandler`) у стандартному каталозі даних (`QStandardPaths`).
- `QSettings` зберігає налаштування між запусками; читають з `type=` і значенням за замовчуванням; групи впорядковують ключі.
- Розмір вікна зберігають у `closeEvent` і відновлюють при запуску; імпорт налаштувань спершу перевіряють.

## Корисні посилання

- [QSettings — документація](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSettings.html)
- [QStandardPaths — документація](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QStandardPaths.html)
- [Модуль `logging.handlers` — RotatingFileHandler](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler)
- [`sys.excepthook` — довідник](https://docs.python.org/3/library/sys.html#sys.excepthook)
- [Python GUIs — Saving and restoring settings with QSettings](https://www.pythonguis.com/faq/pyside6-qsettings/)
