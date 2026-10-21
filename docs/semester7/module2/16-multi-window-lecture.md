# 16. (Л) Багатовіконні застосунки. Модальні та немодальні вікна

## Зміст лекції

1. Навіщо застосунку кілька вікон
2. Окреме вікно: віджет без батька
3. Посилання на вікно: чому вікно «зникає»
4. Модальність: `exec()`, `setWindowModality`
5. Вікно з батьком: `Qt.WindowType.Window`
6. Передавання даних у вікно
7. Передавання даних з вікна: сигнали
8. Одне вікно — один екземпляр
9. Багато вікон одного типу
10. `WA_DeleteOnClose` і сигнал `destroyed`
11. Закриття головного вікна закриває всі
12. Повний приклад: головне вікно, налаштування, перегляд витрат
13. Типові помилки

## Навіщо застосунку кілька вікон

| Вікно | Модальність | Приклад |
|---|---|---|
| «Про програму» | модальне | версія, автор |
| налаштування | немодальне, один екземпляр | ліміти бюджету, тема |
| перегляд запису | немодальне, багато екземплярів | кілька витрат поруч для порівняння |
| діалог редагування | модальне | `ExpenseDialog` (лекція 11) |

Головні питання багатовіконного застосунку: **як передати дані** між вікнами і **хто відповідає за життя** кожного вікна.

## Окреме вікно: віджет без батька

Будь-який віджет без батька, для якого викликали `show()`, — окреме вікно верхнього рівня (лекція 1):

```python
# Program: two top-level windows in one application
import sys

from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
first = QLabel("Main window")
second = QLabel("Second window")
for window in (first, second):
    window.show()
print("top-level windows:", sorted(w.text() for w in app.topLevelWidgets() if w.isVisible()))
print("both are windows:", first.isWindow() and second.isWindow())
```

```text
top-level windows: ['Main window', 'Second window']
both are windows: True
```

## Посилання на вікно: чому вікно «зникає»

Типова помилка: вікно створено в локальній змінній обробника. Після виходу з методу на обʼєкт не лишається посилань, Python знищує його — і вікно зникає одразу після появи:

```python
# Program: a window without a reference is destroyed
import gc
import sys

from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)


def open_bad() -> None:
    window = QLabel("I will disappear")  # помилка: лише локальна змінна
    window.show()


class Holder:
    def open_good(self) -> None:
        self.window = QLabel("I stay")  # посилання в атрибуті
        self.window.show()


open_bad()
holder = Holder()
holder.open_good()
gc.collect()
print("visible windows:", [w.text() for w in app.topLevelWidgets() if w.isVisible()])
```

```text
visible windows: ['I stay']
```

Правило: вікно, що має жити після виходу з методу, зберігають в **атрибуті** (`self.settings_window`), у **списку** відкритих вікон або дають йому **батька**.

## Модальність: `exec()`, `setWindowModality`

| Спосіб | Що блокує |
|---|---|
| `dialog.exec()` | усі вікна застосунку; код чекає закриття (лекція 11) |
| `widget.setWindowModality(Qt.WindowModality.ApplicationModal)` + `show()` | усі вікна, але код **не** чекає |
| `Qt.WindowModality.WindowModal` + `show()` | лише батьківське вікно |
| `Qt.WindowModality.NonModal` (типово) | нічого |

```python
# Program: modality of different windows
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QWidget

app = QApplication(sys.argv)
main = QMainWindow()
about = QDialog(main)
about.setWindowModality(Qt.WindowModality.WindowModal)
settings = QWidget(main, Qt.WindowType.Window)
print("about:", about.windowModality().name, "| settings:", settings.windowModality().name)
print("about is modal:", about.isModal(), "| settings is modal:", settings.isModal())
```

```text
about: WindowModal | settings: NonModal
about is modal: True | settings is modal: False
```

## Вікно з батьком: `Qt.WindowType.Window`

Дочірній віджет звичайно малюється **всередині** батька. Прапорець `Qt.WindowType.Window` робить його окремим вікном, але зберігає звʼязок з батьком:

- вікно знищується разом з батьком;
- на більшості систем воно тримається над батьківським і не має окремої кнопки на панелі завдань;
- посилання на нього зберігає батько, тож воно не «зникне».

`QDialog` з батьком поводиться так автоматично.

## Передавання даних у вікно

Дані передають **конструктором** (як у `ExpenseDialog`, лекція 11) або методом. Найкраще — передати обʼєкт центрального стану (лекція 14), щоб вікно саме читало потрібне:

```python
# Program: pass data into a window through the constructor
import sys

from PySide6.QtWidgets import QApplication, QFormLayout, QLabel, QWidget


class ExpenseView(QWidget):
    def __init__(self, expense: dict) -> None:
        super().__init__()
        self.setWindowTitle(f"Expense {expense['date']}")
        self.values: dict[str, QLabel] = {}
        form = QFormLayout(self)
        for key in ("date", "category", "amount", "comment"):
            self.values[key] = QLabel(str(expense[key]))
            form.addRow(f"{key.title()}:", self.values[key])


app = QApplication(sys.argv)
view = ExpenseView({"date": "2026-09-21", "category": "food", "amount": 85.5, "comment": "lunch"})
print(view.windowTitle())
print({key: label.text() for key, label in view.values.items()})
```

```text
Expense 2026-09-21
{'date': '2026-09-21', 'category': 'food', 'amount': '85.5', 'comment': 'lunch'}
```

Посилання на написи зі значеннями зберігаються у словнику `values`: так їх легко оновити, якщо витрата зміниться.

## Передавання даних з вікна: сигнали

Немодальне вікно не «повертає» результат, як `exec()`. Воно **випромінює сигнал**, а головне вікно (або стан) підписується на нього. Вікно налаштувань не знає, хто використовує налаштування:

```python
# File: settings_window.py
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialogButtonBox, QDoubleSpinBox, QFormLayout, QWidget


class SettingsWindow(QWidget):
    settings_changed = Signal(dict)

    def __init__(self, limits: dict[str, float], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.spins: dict[str, QDoubleSpinBox] = {}
        form = QFormLayout(self)
        for category, limit in limits.items():
            spin = QDoubleSpinBox(maximum=100000, decimals=2, suffix=" UAH", value=limit)
            self.spins[category] = spin
            form.addRow(f"{category} limit:", spin)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Close)
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        self.buttons.rejected.connect(self.close)
        form.addRow(self.buttons)

    def apply(self) -> None:
        self.settings_changed.emit({category: spin.value() for category, spin in self.spins.items()})
```

```python
# Program: the settings window reports changes with a signal
import sys

from PySide6.QtWidgets import QApplication, QDialogButtonBox

from settings_window import SettingsWindow

app = QApplication(sys.argv)
received = []
window = SettingsWindow({"food": 3000.0, "fun": 1000.0})
window.settings_changed.connect(received.append)
window.show()
window.spins["food"].setValue(3500)
window.buttons.button(QDialogButtonBox.StandardButton.Apply).click()
print("received:", received)
print("window stays open after Apply:", window.isVisible())
```

```text
received: [{'food': 3500.0, 'fun': 1000.0}]
window stays open after Apply: True
```

## Одне вікно — один екземпляр

Пункт меню «Налаштування» не повинен відкривати нове вікно щоразу. Головне вікно зберігає посилання в атрибуті `self.settings_window` (спочатку `None`) і в методі `open_settings`:

1. створює вікно лише тоді, коли атрибут ще `None`, і одразу підʼєднує його сигнал до стану;
2. щоразу викликає `show()`, `raise_()` (підняти над іншими вікнами) і `activateWindow()` (передати фокус).

Метод `open_settings` — у повному прикладі наприкінці лекції.

## Багато вікон одного типу

Вікна перегляду витрат можна відкрити кілька. Їх зберігають у **списку** і прибирають зі списку, коли вікно закривають.

## `WA_DeleteOnClose` і сигнал `destroyed`

За замовчуванням закрите вікно лише **ховається**: обʼєкт живе далі. Атрибут `Qt.WidgetAttribute.WA_DeleteOnClose` змушує Qt знищити вікно після закриття, а сигнал `destroyed` повідомляє про це — у слоті вікно прибирають зі списку:

```python
# Program: closed viewer windows are deleted and removed from the list
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
viewers: list[QLabel] = []


def open_viewer(text: str) -> QLabel:
    viewer = QLabel(text)
    viewer.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    viewer.destroyed.connect(lambda _obj=None, v=viewer: viewers.remove(v))
    viewers.append(viewer)
    viewer.show()
    return viewer


first = open_viewer("food 85.50")
open_viewer("bus 30.00")
print("open viewers:", len(viewers))
first.close()
app.processEvents()  # знищення відбувається в циклі подій
app.sendPostedEvents(None, 0)
print("open viewers:", len(viewers))
```

```text
open viewers: 2
open viewers: 1
```

Знищення відкладене (`deleteLater`): воно відбувається в циклі обробки подій, тому в прикладі цикл «прокручено» вручну.

## Закриття головного вікна закриває всі

Типово застосунок завершується, коли закрито **останнє** вікно. Якщо відкрите вікно налаштувань без батька, після закриття головного вікна застосунок продовжить працювати. Варіанти:

| Спосіб | Як |
|---|---|
| дати допоміжним вікнам батька | `QWidget(main, Qt.WindowType.Window)` — знищуються разом з головним |
| закрити їх у `closeEvent` головного | пройти списком відкритих вікон і викликати `close()` |
| завершити застосунок при закритті головного | `app.quit()` у `closeEvent` |

## Повний приклад: головне вікно, налаштування, перегляд витрат

```python
# File: multi_window_app.py
import sys

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from settings_window import SettingsWindow


class State(QObject):
    limits_changed = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self.expenses = [
            {"date": "2026-09-05", "category": "food", "amount": 1250.0, "comment": "groceries"},
            {"date": "2026-09-20", "category": "food", "amount": 1940.0, "comment": "groceries"},
            {"date": "2026-09-25", "category": "fun", "amount": 315.0, "comment": "cinema"},
        ]
        self.limits = {"food": 3000.0, "fun": 1000.0}

    def set_limits(self, limits: dict) -> None:
        self.limits = dict(limits)
        self.limits_changed.emit(self.limits)

    def warnings(self) -> list[str]:
        totals: dict[str, float] = {}
        for e in self.expenses:
            totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
        return [f"{c}: {t - self.limits[c]:.2f} over" for c, t in totals.items() if t > self.limits.get(c, t)]


class ExpenseView(QWidget):
    def __init__(self, expense: dict, parent: QWidget) -> None:
        super().__init__(parent, Qt.WindowType.Window)  # окреме вікно, знищується разом з батьком
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(f"{expense['date']} {expense['category']}")
        QVBoxLayout(self).addWidget(QLabel(f"{expense['amount']:.2f} UAH, {expense['comment']}"))


class MainWindow(QMainWindow):
    def __init__(self, state: State) -> None:
        super().__init__()
        self.state = state
        self.settings_window: SettingsWindow | None = None
        self.viewers: list[ExpenseView] = []
        self.setWindowTitle("Expenses")

        self.list = QListWidget()
        self.list.addItems(f"{e['date']} {e['category']} {e['amount']:.2f}" for e in state.expenses)
        self.list.itemDoubleClicked.connect(lambda item: self.open_viewer(self.list.row(item)))
        self.warning_label = QLabel()
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.list)
        layout.addWidget(self.warning_label)
        self.setCentralWidget(central)

        menu = self.menuBar().addMenu("&Window")
        menu.addAction("&Settings...", self.open_settings)
        menu.addAction("&About", self.show_about)
        state.limits_changed.connect(self.update_warnings)
        self.update_warnings()

    def update_warnings(self, _limits=None) -> None:
        self.warning_label.setText("; ".join(self.state.warnings()) or "Budget is fine")

    def open_settings(self) -> None:
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.state.limits, self)
            self.settings_window.setWindowFlag(Qt.WindowType.Window)
            self.settings_window.settings_changed.connect(self.state.set_limits)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def open_viewer(self, row: int) -> ExpenseView:
        viewer = ExpenseView(self.state.expenses[row], self)
        viewer.destroyed.connect(lambda _obj=None, v=viewer: self.viewers.remove(v))
        self.viewers.append(viewer)
        viewer.show()
        return viewer

    def show_about(self) -> None:
        QMessageBox.about(self, "About", "Expenses 1.0\nCourse project, semester 7")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(State())
    window.resize(480, 320)
    window.show()
    sys.exit(app.exec())
```

```python
# Program: drive the multi-window application
import sys

from PySide6.QtWidgets import QApplication, QDialogButtonBox

from multi_window_app import MainWindow, State

app = QApplication(sys.argv)
window = MainWindow(State())
window.show()
print("warnings:", window.warning_label.text())

window.open_settings()
first_settings = window.settings_window
window.open_settings()
print("one settings window:", window.settings_window is first_settings)

window.settings_window.spins["food"].setValue(2500)
window.settings_window.buttons.button(QDialogButtonBox.StandardButton.Apply).click()
print("warnings:", window.warning_label.text())

window.open_viewer(0)
window.open_viewer(2)
print("viewers:", [v.windowTitle() for v in window.viewers])
print("viewers belong to the main window:", all(v.parent() is window for v in window.viewers))
```

```text
warnings: food: 190.00 over
one settings window: True
warnings: food: 690.00 over
viewers: ['2026-09-05 food', '2026-09-25 fun']
viewers belong to the main window: True
```

У цьому застосунку:

- вікно налаштувань створюється один раз і лише показується повторно;
- зміни налаштувань ідуть через сигнал у стан, а стан своїм сигналом оновлює попередження;
- вікна перегляду мають батька — головне вікно: закриття головного вікна закриває і знищує їх;
- «Про програму» — модальне повідомлення.

## Типові помилки

| Помилка | Чому погано | Як правильно |
|---|---|---|
| Вікно в локальній змінній | зникає одразу після появи | атрибут, список або батько |
| Нове вікно налаштувань при кожному кліку | кілька вікон з різними значеннями | одне вікно, `show()` + `raise_()` |
| Допоміжне вікно напряму змінює віджети головного | сильна звʼязаність | сигнал → стан → сигнал |
| Список відкритих вікон не очищається | витік памʼяті, звернення до знищених обʼєктів | `WA_DeleteOnClose` + `destroyed` |
| Дочірній віджет без `Qt.WindowType.Window` замість вікна | віджет зʼявляється всередині батька | прапорець `Window` |
| Після закриття головного вікна застосунок працює далі | залишилися вікна без батька | батько або закриття в `closeEvent` |
| `exec()` для вікна, з яким треба працювати паралельно | головне вікно заблоковане | немодальне `show()` |

## Підсумок

- Окреме вікно — віджет без батька або з прапорцем `Qt.WindowType.Window`; посилання на вікно треба зберігати.
- **Модальні** вікна блокують інші (`exec()`, `setWindowModality`), **немодальні** працюють поруч (`show()`).
- Дані передають у вікно конструктором (найкраще — стан застосунку), а з вікна — **сигналами**.
- Вікно, що має бути в одному екземплярі, створюють один раз і повторно показують (`show`, `raise_`, `activateWindow`).
- Багато вікон одного типу зберігають у списку; `WA_DeleteOnClose` і `destroyed` прибирають закриті.
- Допоміжні вікна з батьком закриваються разом з головним.

## Корисні посилання

- [QWidget — Window Flags і windowModality](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html)
- [Qt — Window and Dialog Widgets](https://doc.qt.io/qt-6/application-windows.html)
- [Qt — Object Trees & Ownership](https://doc.qt.io/qt-6/objecttrees.html)
- [Python GUIs — Creating additional windows](https://www.pythonguis.com/tutorials/pyside6-creating-multiple-windows/)
- Fitzpatrick M. Create GUI Applications with Python & Qt6 (PySide6 Edition). — 2023.
