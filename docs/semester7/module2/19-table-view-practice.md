# 19. (П10) Відображення даних у таблицях: Model/View

## Мета роботи

- **Освітня (навчальна):** навчитися відображати дані в `QTableView` через власну модель на основі `QAbstractTableModel`, реалізувати сортування й фільтрацію через `QSortFilterProxyModel` та редагування комірок.
- **Дослідна (розвиваюча):** розвинути розуміння архітектури Model/View і вміння пояснювати, як представлення дізнається про зміни даних.
- **Виховна (патріотична):** сформувати інтерес до роботи з відкритими даними та прагнення подавати їх у зручному для людини вигляді.

!!! danger "Персоналізація обовʼязкова"
    Таблиця показує **ваші** витрати; додатково ви відкриваєте один набір даних з порталу data.gov.ua у форматі CSV.

## Підготовка

Скористайтеся `expense_tracker` з роботи П9. Завантажте з [data.gov.ua](https://data.gov.ua) невеликий CSV-набір (до 1000 рядків), що вас цікавить.

## Хід роботи

### Завдання 1. Власна модель

Файл `ui/expense_model.py`:

```python
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ExpenseModel(QAbstractTableModel):
    HEADERS = ["Date", "Category", "Amount", "Comment"]

    def __init__(self, expenses):
        super().__init__()
        self.expenses = expenses  # список обʼєктів Expense

    def rowCount(self, parent=QModelIndex()):
        return len(self.expenses)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        expense = self.expenses[index.row()]
        values = [expense.spent_on.isoformat(), expense.category, f"{expense.amount:.2f}", expense.comment]
        return values[index.column()]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return None
```

Замініть список у головному вікні на `QTableView` з цією моделлю.

**Очікуваний результат:** таблиця показує всі ваші витрати з заголовками стовпців.

### Завдання 2. Оформлення комірок

Використайте інші ролі в методі `data`: суми вирівняно праворуч (`TextAlignmentRole`), витрати понад ліміт виділено кольором (`ForegroundRole`), підказка з повним коментарем (`ToolTipRole`).

**Очікуваний результат:** великі витрати помітні одразу, а підказка зʼявляється під час наведення на комірку.

### Завдання 3. Сортування та фільтр

Підключіть `QSortFilterProxyModel` між моделлю і таблицею. Увімкніть сортування кліком на заголовок і поле пошуку, що фільтрує рядки за коментарем або категорією. Сортування суми має бути числовим (роль `UserRole` з числом).

**Очікуваний результат:** сума `100.00` стоїть після `85.50` під час сортування за зростанням, а фільтр працює під час введення.

### Завдання 4. Редагування

Реалізуйте методи `flags` і `setData`, щоб редагувати категорію, суму та коментар прямо в таблиці. Під час додавання витрати використовуйте `beginInsertRows`/`endInsertRows`.

**Очікуваний результат:** зміни в таблиці зберігаються в CSV, а некоректна сума (від’ємна або текст) не приймається.

### Завдання 5. Відкриті дані

Відкрийте завантажений набір з data.gov.ua в окремому вікні з універсальною моделлю, що будує стовпці за заголовком CSV.

**Очікуваний результат:** таблиця показує набір відкритих даних; у звіті назва набору, посилання на нього і кількість рядків.

## Що здати

Каталог `expense_tracker` (без `.venv`): код і звіт у PDF зі знімками таблиць та відповідями на контрольні запитання.

## Контрольні запитання

1. Що таке архітектура Model/View?
2. Які методи обовʼязково реалізувати в нащадку `QAbstractTableModel`?
3. Що таке роль даних (role)?
4. Навіщо потрібна проксі-модель?
5. Як повідомити представлення про додавання нового рядка?
