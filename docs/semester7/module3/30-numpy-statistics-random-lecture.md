# 30. (Л) Статистичні функції та генерація випадкових даних у NumPy

## Зміст лекції

1. Описова статистика: що розповідають числа
2. Середнє і медіана
3. Розкид: розмах, дисперсія, стандартне відхилення
4. Квантилі й перцентилі
5. Статистики по осях і з пропусками
6. Частоти: `unique`, `bincount`, `histogram`
7. Звʼязок двох величин: кореляція
8. Генератор випадкових чисел `default_rng`
9. Зерно (seed) і відтворюваність
10. Рівномірні й цілі випадкові числа
11. Нормальний розподіл
12. Вибір, перемішування, вибірки
13. Симуляції: кидки кубика
14. Метод Монте-Карло
15. Закон великих чисел і розмір вибірки
16. Типові помилки

## Описова статистика: що розповідають числа

Масив з 30 денних витрат важко «прочитати» очима. **Описова статистика** стискає його до кількох чисел:

| Питання | Статистика |
|---|---|
| скільки «зазвичай» | середнє, медіана, мода |
| наскільки значення відрізняються | розмах, дисперсія, стандартне відхилення |
| де межі «типових» значень | квартилі, перцентилі |
| як часто трапляються значення | частоти, гістограма |
| чи повʼязані дві величини | кореляція |

## Середнє і медіана

```python
# Program: mean and median react to an outlier differently
import numpy as np

daily = np.array([85.5, 30, 64.5, 120, 45, 30, 95, 70, 55, 12.5])
with_laptop = np.append(daily, 32000)  # один день — купівля ноутбука
for name, data in (("usual days", daily), ("with laptop", with_laptop)):
    print(f"{name:<12} mean {np.mean(data):9.2f} | median {np.median(data):6.2f}")
```

```text
usual days   mean     60.75 | median  59.75
with laptop  mean   2964.32 | median  64.50
```

**Медіана** — середнє за порядком значення: половина елементів менша, половина більша. Одна велика покупка «зсунула» середнє в 50 разів, а медіану майже не змінила. Тому для грошей, зарплат, цін медіана часто краще описує «типове» значення.

`np.average(values, weights=...)` рахує **зважене** середнє — наприклад, середній бал з урахуванням кредитів дисциплін:

```python
# Program: a weighted average grade
import numpy as np

grades = np.array([92, 78, 85, 60])
credits = np.array([6, 4, 3, 2])
print("simple mean:", grades.mean(), "| weighted by credits:", round(np.average(grades, weights=credits), 2))
```

```text
simple mean: 78.75 | weighted by credits: 82.6
```

## Розкид: розмах, дисперсія, стандартне відхилення

| Функція | Формула | Сенс |
|---|---|---|
| `np.ptp(a)` | max − min | розмах |
| `np.var(a)` | (1/n)·Σ(aᵢ − ā)² | дисперсія |
| `np.std(a)` | √var | стандартне відхилення, в одиницях даних |
| `np.std(a, ddof=1)` | ділення на *n − 1* | вибіркове стандартне відхилення |

```python
# Program: spread of two students' grades with the same mean
import numpy as np

steady = np.array([80, 82, 78, 81, 79])
unstable = np.array([100, 60, 95, 55, 90])
for name, g in (("steady", steady), ("unstable", unstable)):
    print(f"{name:<9} mean {g.mean():.1f}, range {np.ptp(g)}, std {g.std():.2f}, sample std {g.std(ddof=1):.2f}")
```

```text
steady    mean 80.0, range 4, std 1.41, sample std 1.58
unstable  mean 80.0, range 45, std 18.71, sample std 20.92
```

Однакове середнє — зовсім різна «стабільність». Якщо дані — **вибірка** з більшої сукупності (оцінки п'яти студентів, а не всіх), використовують `ddof=1`: так оцінка розкиду сукупності не занижена. Бібліотека pandas (лекція 32) рахує саме так за замовчуванням.

## Квантилі й перцентилі

**Перцентиль** *p* — значення, нижче якого лежить *p* % даних. Медіана — 50-й перцентиль. **Квартилі** — 25-й, 50-й, 75-й перцентилі; різниця між третім і першим — **міжквартильний розмах** (IQR), основа діаграми «ящик з вусами» (лекція 41).

```python
# Program: percentiles and outliers by the IQR rule
import numpy as np

daily = np.array([85.5, 30, 0, 185, 315, 12.5, 64.5, 0, 0, 120, 45, 30, 210, 0, 85,
                  30, 640, 0, 55, 12.5, 30, 185, 0, 95, 315, 0, 30, 70, 12.5, 150])
q1, median, q3 = np.percentile(daily, [25, 50, 75])
iqr = q3 - q1
print(f"Q1 {q1}, median {median}, Q3 {q3}, IQR {iqr}")
print("90th percentile:", round(np.percentile(daily, 90), 2))
upper_fence = q3 + 1.5 * iqr
print("outliers above", upper_fence, ":", daily[daily > upper_fence])
```

```text
Q1 12.5, median 37.5, Q3 113.75, IQR 101.25
90th percentile: 220.5
outliers above 265.625 : [315. 640. 315.]
```

Правило «1,5 IQR»: значення вище Q3 + 1,5 · IQR або нижче Q1 − 1,5 · IQR вважають **викидами** — їх варто перевірити окремо.

## Статистики по осях і з пропусками

Усі статистичні функції приймають `axis` (лекція 25). Для даних з пропусками `nan` є версії з префіксом `nan`:

```python
# Program: statistics per column and with missing values
import numpy as np

# рядки — студенти, стовпці — дисципліни; nan — ще немає оцінки
grades = np.array([[92, 78, np.nan],
                   [85, 64, 90],
                   [70, np.nan, 88],
                   [60, 72, 95]])
print("mean with nan:", np.mean(grades, axis=0))
print("nanmean per subject:", np.round(np.nanmean(grades, axis=0), 1))
print("nanmedian per student:", np.nanmedian(grades, axis=1))
print("missing grades per subject:", np.isnan(grades).sum(axis=0))
```

```text
mean with nan: [76.75   nan   nan]
nanmean per subject: [76.8 71.3 91. ]
nanmedian per student: [85. 85. 79. 72.]
missing grades per subject: [0 1 1]
```

## Частоти: `unique`, `bincount`, `histogram`

```python
# Program: frequencies of values and of intervals
import numpy as np

grades = np.array([5, 4, 4, 3, 5, 5, 2, 4, 3, 5, 4, 4])
values, counts = np.unique(grades, return_counts=True)
print("unique:", values, "counts:", counts)
print("most frequent (mode):", values[counts.argmax()])
print("bincount:", np.bincount(grades))

daily = np.array([85.5, 30, 0, 185, 315, 12.5, 64.5, 0, 120, 45, 640, 210])
counts, edges = np.histogram(daily, bins=[0, 50, 100, 200, 1000])
for left, right, n in zip(edges[:-1], edges[1:], counts):
    print(f"{left:>4.0f}-{right:<4.0f} {'#' * n} {n}")
```

```text
unique: [2 3 4 5] counts: [1 2 5 4]
most frequent (mode): 4
bincount: [0 0 1 2 5 4]
   0-50   ##### 5
  50-100  ## 2
 100-200  ## 2
 200-1000 ### 3
```

`np.histogram` ділить діапазон на інтервали (**кошики**, bins) і рахує, скільки значень потрапило в кожен. Гістограма як графік — лекція 39.

## Звʼязок двох величин: кореляція

**Коефіцієнт кореляції Пірсона** *r* від −1 до 1 показує, наскільки дві величини змінюються **лінійно разом**:

| *r* | Значення |
|---|---|
| близько 1 | одна росте — інша росте |
| близько 0 | лінійного звʼязку немає |
| близько −1 | одна росте — інша спадає |

```python
# Program: correlation between study hours, grades and sleep
import numpy as np

hours = np.array([2, 4, 5, 7, 8, 10, 12])
grade = np.array([60, 65, 70, 78, 80, 88, 95])
phone = np.array([6, 5, 5, 4, 3, 2, 1])  # години в телефоні
matrix = np.corrcoef([hours, grade, phone])
print(np.round(matrix, 3))
print("hours ~ grade:", round(matrix[0, 1], 3), "| hours ~ phone:", round(matrix[0, 2], 3))
```

```text
[[ 1.     0.998 -0.991]
 [ 0.998  1.    -0.985]
 [-0.991 -0.985  1.   ]]
hours ~ grade: 0.998 | hours ~ phone: -0.991
```

`np.corrcoef` повертає **матрицю кореляцій** усіх пар; на діагоналі — одиниці (кореляція величини з собою).

!!! warning "Кореляція — не причинність"
    Висока кореляція не означає, що одна величина **спричиняє** іншу. Продаж морозива й кількість утоплень корелюють — бо обидві зростають улітку. Висновки про причини потребують експериментів або додаткових знань.

## Генератор випадкових чисел `default_rng`

Випадкові числа потрібні для симуляцій, тестових даних, ігор, перемішування, вибірок. Сучасний спосіб у NumPy — **обʼєкт-генератор**:

```python
# Program: create a random generator and draw numbers
import numpy as np

rng = np.random.default_rng()
print("one float in [0, 1):", 0 <= rng.random() < 1)
print("five dice rolls are in 1..6:", np.all(np.isin(rng.integers(1, 7, size=5), np.arange(1, 7))))
```

```text
one float in [0, 1): True
five dice rolls are in 1..6: True
```

Старий інтерфейс `np.random.seed(...)`, `np.random.randint(...)` ще працює, але документація NumPy рекомендує `default_rng`: незалежні генератори не заважають один одному, а алгоритм PCG64 якісніший.

!!! danger "Не для паролів і токенів"
    Генератори NumPy (як і модуль `random`, лекція 29 5 семестру) **передбачувані**. Для паролів, токенів, ключів — лише модуль `secrets` (лекція 24, 6 семестр).

## Зерно (seed) і відтворюваність

Генератор псевдовипадкових чисел — детермінований алгоритм. **Зерно** (seed) задає його початковий стан: однакове зерно — однакова послідовність. Це потрібно для тестів, звітів і навчальних прикладів, які мають давати той самий результат:

```python
# Program: the same seed gives the same numbers
import numpy as np

first = np.random.default_rng(42).integers(1, 7, size=8)
second = np.random.default_rng(42).integers(1, 7, size=8)
other = np.random.default_rng(7).integers(1, 7, size=8)
print(first, second, other)
print("same seed, same numbers:", np.array_equal(first, second))
```

```text
[1 5 4 3 3 6 1 5] [1 5 4 3 3 6 1 5] [6 4 5 6 4 5 6 2]
same seed, same numbers: True
```

Далі в лекції всі генератори мають зерно, тому ваш вивід збігатиметься з наведеним.

## Рівномірні й цілі випадкові числа

| Метод | Що повертає |
|---|---|
| `rng.random(size)` | дробові рівномірно в `[0, 1)` |
| `rng.uniform(low, high, size)` | дробові рівномірно в `[low, high)` |
| `rng.integers(low, high, size)` | цілі в `[low, high)` — `high` не включається |
| `rng.integers(low, high, size, endpoint=True)` | цілі в `[low, high]` |

```python
# Program: uniform floats and integers
import numpy as np

rng = np.random.default_rng(2026)
print(np.round(rng.random(3), 3))
print(np.round(rng.uniform(20, 300, size=4), 2))
print(rng.integers(1, 7, size=10))
print(rng.integers(60, 100, size=(2, 3), endpoint=True))
```

```text
[0.179 0.64  0.467]
[123.74 119.38 241.35 273.44]
[5 2 6 4 1 2 1 6 5 6]
[[71 86 84]
 [90 64 81]]
```

## Нормальний розподіл

**Нормальний розподіл** (гаусівський, «дзвін») описує величини, що складаються з багатьох дрібних випадкових впливів: зріст, похибки вимірювань, результати тестів. Його задають середнім *μ* і стандартним відхиленням *σ*. Приблизно 68 % значень лежать у межах *μ ± σ*, 95 % — у межах *μ ± 2σ*:

```python
# Program: normal distribution and the 68-95 rule
import numpy as np

rng = np.random.default_rng(1)
scores = rng.normal(loc=75, scale=10, size=100_000)
print(f"mean {scores.mean():.2f}, std {scores.std():.2f}")
within_1 = np.mean(np.abs(scores - 75) <= 10)
within_2 = np.mean(np.abs(scores - 75) <= 20)
print(f"within 1 sigma: {within_1:.3f}, within 2 sigma: {within_2:.3f}")
grades = np.clip(np.round(scores), 0, 100).astype(int)
print("simulated grades of 8 students:", grades[:8])
```

```text
mean 74.95, std 9.97
within 1 sigma: 0.684, within 2 sigma: 0.955
simulated grades of 8 students: [78 83 78 62 84 79 70 81]
```

`np.mean` на масиві `True`/`False` дає **частку** істинних значень. `np.clip` обмежує значення діапазоном — оцінка не може бути більшою за 100.

Інші розподіли генератора: `exponential` (час між подіями), `poisson` (кількість подій за інтервал), `binomial` (кількість успіхів у n спробах).

## Вибір, перемішування, вибірки

```python
# Program: choice, permutation and shuffle
import numpy as np

rng = np.random.default_rng(11)
students = np.array(["Olena", "Taras", "Iryna", "Andrii", "Sofiia", "Maksym"])
print("who answers today:", rng.choice(students))
print("random order of presentations:", rng.permutation(students))
print("3 reviewers, no repeats:", rng.choice(students, size=3, replace=False))
weather = rng.choice(["sun", "rain", "snow"], size=10, p=[0.6, 0.3, 0.1])
print("weighted choice:", weather)

deck = np.arange(10)
rng.shuffle(deck)  # змінює масив на місці
print("shuffled in place:", deck)
```

```text
who answers today: Olena
random order of presentations: ['Andrii' 'Taras' 'Sofiia' 'Maksym' 'Iryna' 'Olena']
3 reviewers, no repeats: ['Olena' 'Maksym' 'Iryna']
weighted choice: ['sun' 'sun' 'snow' 'rain' 'sun' 'sun' 'rain' 'sun' 'sun' 'rain']
shuffled in place: [4 5 0 3 6 8 9 2 1 7]
```

| Метод | Особливість |
|---|---|
| `choice(a, size, replace=True)` | вибірка з поверненням (можливі повтори) |
| `choice(a, size, replace=False)` | без повторень |
| `choice(a, p=[...])` | з заданими ймовірностями |
| `permutation(a)` | **нова** перемішана копія |
| `shuffle(a)` | перемішує **на місці** |

## Симуляції: кидки кубика

**Симуляція** — моделювання випадкового процесу багато разів, щоб оцінити ймовірності, які важко порахувати формулою. Перевіримо, як часто сума двох кубиків дорівнює кожному значенню:

```python
# Program: simulate 100000 rolls of two dice
import numpy as np

rng = np.random.default_rng(2026)
rolls = rng.integers(1, 7, size=(100_000, 2))
sums = rolls.sum(axis=1)
counts = np.bincount(sums, minlength=13)[2:]
for total, n in zip(range(2, 13), counts):
    exact = (6 - abs(total - 7)) / 36
    print(f"{total:>2}: {n / sums.size:.3f} (exact {exact:.3f}) {'#' * int(n / sums.size * 100)}")
print("double six:", np.mean((rolls == 6).all(axis=1)).round(4), "exact", round(1 / 36, 4))
```

```text
 2: 0.029 (exact 0.028) ##
 3: 0.056 (exact 0.056) #####
 4: 0.083 (exact 0.083) ########
 5: 0.112 (exact 0.111) ###########
 6: 0.139 (exact 0.139) #############
 7: 0.166 (exact 0.167) ################
 8: 0.141 (exact 0.139) ##############
 9: 0.110 (exact 0.111) ###########
10: 0.081 (exact 0.083) ########
11: 0.055 (exact 0.056) #####
12: 0.028 (exact 0.028) ##
double six: 0.0283 exact 0.0278
```

Сто тисяч кидків — один рядок коду і частки секунди, без жодного циклу.

## Метод Монте-Карло

**Метод Монте-Карло** оцінює величину випадковими експериментами. Класичний приклад — число π: точки кидають у квадрат [0, 1] × [0, 1]; частка точок усередині чверті кола радіуса 1 наближається до π/4:

```python
# Program: estimate pi with random points
import numpy as np

rng = np.random.default_rng(3)
for n in (100, 10_000, 1_000_000):
    points = rng.random((n, 2))
    inside = (points ** 2).sum(axis=1) <= 1
    estimate = 4 * inside.mean()
    print(f"{n:>9} points: pi ~ {estimate:.4f}, error {abs(estimate - np.pi):.4f}")
```

```text
      100 points: pi ~ 3.2000, error 0.0584
    10000 points: pi ~ 3.1376, error 0.0040
  1000000 points: pi ~ 3.1405, error 0.0010
```

Той самий принцип оцінює ризики в фінансах, надійність систем, час виконання проєктів.

## Закон великих чисел і розмір вибірки

**Закон великих чисел**: зі зростанням кількості спроб середнє вибірки наближається до справжнього значення. Похибка зменшується приблизно як 1/√n: щоб зменшити її вдвічі, потрібно вчетверо більше даних.

```python
# Program: the sample mean gets closer as the sample grows
import numpy as np

rng = np.random.default_rng(5)
true_mean = 3.5  # середнє одного кубика
for n in (10, 100, 1_000, 10_000, 100_000):
    means = rng.integers(1, 7, size=(200, n)).mean(axis=1)  # 200 повторів експерименту
    print(f"n={n:>6}: typical error {np.abs(means - true_mean).mean():.4f}")
```

```text
n=    10: typical error 0.4205
n=   100: typical error 0.1418
n=  1000: typical error 0.0432
n= 10000: typical error 0.0116
n=100000: typical error 0.0045
```

Кожне збільшення вибірки в 10 разів зменшує похибку приблизно в √10 ≈ 3,2 раза. Тому висновки з опитування 10 одногрупників ненадійні, а з 1000 — значно точніші.

## Типові помилки

| Помилка | Чому погано | Як правильно |
|---|---|---|
| Лише середнє для грошей і зарплат | викиди спотворюють картину | також медіана й перцентилі |
| `std` вибірки без `ddof=1` | розкид сукупності занижено | `np.std(a, ddof=1)` |
| `mean` з `nan` | результат `nan` | `np.nanmean` |
| Висновок «корелює, отже спричиняє» | хибні висновки | кореляція — лише звʼязок |
| Випадкові дані без зерна в тестах і звітах | результат не відтворюється | `default_rng(seed)` |
| `integers(1, 6)` для кубика | шістка ніколи не випадає | `integers(1, 7)` або `endpoint=True` |
| Генератор NumPy для паролів | передбачувані значення | модуль `secrets` |
| Висновки з малої вибірки | велика похибка | збільшити вибірку, оцінити похибку |

## Підсумок

- **Описова статистика**: середнє, медіана, розмах, дисперсія, стандартне відхилення (`ddof=1` для вибірки), перцентилі й квартилі.
- Медіана стійка до викидів; викиди знаходять правилом 1,5 · IQR.
- Функції `nan...` пропускають відсутні значення; `axis` рахує статистики по рядках чи стовпцях.
- `unique`, `bincount`, `histogram` рахують частоти; `corrcoef` — матрицю кореляцій.
- Випадкові числа дає генератор `np.random.default_rng(seed)`: `random`, `uniform`, `integers`, `normal`, `choice`, `permutation`, `shuffle`; зерно робить результат відтворюваним.
- Симуляції й метод Монте-Карло оцінюють ймовірності; похибка зменшується як 1/√n.

## Корисні посилання

- [NumPy — Statistics](https://numpy.org/doc/stable/reference/routines.statistics.html)
- [NumPy — Random Generator](https://numpy.org/doc/stable/reference/random/generator.html)
- [NumPy — `numpy.percentile`](https://numpy.org/doc/stable/reference/generated/numpy.percentile.html)
- [Seeing Theory — візуальне введення в теорію ймовірностей](https://seeing-theory.brown.edu/)
- VanderPlas J. Python Data Science Handbook. — O'Reilly, 2023. — Розділ 2.
