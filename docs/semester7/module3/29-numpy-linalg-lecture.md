# 29. (Л) Базова лінійна алгебра у NumPy. Матричні операції, системи лінійних рівнянь

## Зміст лекції

1. Навіщо програмісту лінійна алгебра
2. Вектори: сума, множення на число, скалярний добуток
3. Довжина вектора і відстань
4. Матриці й матричне множення: `@`
5. `*` чи `@`
6. Транспонування й одинична матриця
7. Визначник
8. Обернена матриця
9. Системи лінійних рівнянь: `np.linalg.solve`
10. Коли розвʼязку немає: ранг і вироджені матриці
11. Метод найменших квадратів: лінія тренду
12. Власні значення і власні вектори
13. Точність обчислень: `allclose`
14. Типові помилки

## Навіщо програмісту лінійна алгебра

Лінійну алгебру ви вивчаєте в курсі вищої математики. У програмуванні вона повсюди:

| Галузь | Що рахують матрицями |
|---|---|
| комп'ютерна графіка, ігри | повороти, масштабування, перспектива |
| машинне навчання | шари нейромереж — множення матриць |
| аналіз даних | регресія, кореляції, стиснення даних |
| економіка | вартість наборів товарів, баланси |
| інженерія | системи рівнянь для схем, конструкцій |

Модуль `np.linalg` містить готові, швидкі й чисельно надійні реалізації — писати цикли вручну не потрібно.

## Вектори: сума, множення на число, скалярний добуток

Вектор у NumPy — одновимірний масив. Сума й множення на число — поелементні (лекція 25). **Скалярний добуток** *a · b = Σ aᵢ·bᵢ* рахує `np.dot` або оператор `@`:

```python
# Program: vector operations on a shopping list
import numpy as np

prices = np.array([42.0, 85.5, 30.0])   # хліб, сир, молоко, грн
week1 = np.array([3, 1, 4])              # кількість у першому тижні
week2 = np.array([2, 2, 3])

print("total quantity:", week1 + week2)
print("prices +10%:", prices * 1.1)
print("cost of week 1:", prices @ week1, "=", np.dot(prices, week1))
print("cost of both weeks:", prices @ (week1 + week2))
```

```text
total quantity: [5 3 7]
prices +10%: [46.2  94.05 33.  ]
cost of week 1: 331.5 = 331.5
cost of both weeks: 676.5
```

Скалярний добуток «цін» на «кількості» — це вартість покупки: 42 · 3 + 85,5 · 1 + 30 · 4 = 331,5.

## Довжина вектора і відстань

Довжина (норма) вектора *‖v‖ = √(Σ vᵢ²)* — `np.linalg.norm`. Відстань між точками — довжина їхньої різниці:

```python
# Program: vector length, distance and angle
import numpy as np

home = np.array([0.0, 0.0])
shop = np.array([3.0, 4.0])
print("distance:", np.linalg.norm(shop - home))

a, b = np.array([1.0, 0.0]), np.array([1.0, 1.0])
cos_angle = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
print("angle, degrees:", round(np.degrees(np.arccos(cos_angle)), 1))
```

```text
distance: 5.0
angle, degrees: 45.0
```

Косинус кута між векторами (**косинусна подібність**) використовують у пошукових системах і рекомендаціях: чим ближче до 1, тим «схожіші» вектори-описи.

## Матриці й матричне множення: `@`

Добуток матриць *A* розміру *m × n* і *B* розміру *n × p* — матриця *C* розміру *m × p*, де *cᵢⱼ* — скалярний добуток *i*-го рядка *A* на *j*-й стовпець *B*. Кількість **стовпців** першої матриці має дорівнювати кількості **рядків** другої.

```python
# Program: cost of several purchases at several shops
import numpy as np

# рядки — покупки, стовпці — хліб, сир, молоко
purchases = np.array([[3, 1, 4],
                      [2, 2, 3],
                      [0, 1, 6]])
# рядки — товари, стовпці — магазини A і B
prices = np.array([[42.0, 39.5],
                   [85.5, 92.0],
                   [30.0, 28.0]])
costs = purchases @ prices
print(costs)
print("shape:", purchases.shape, "@", prices.shape, "->", costs.shape)
print("cheapest shop for each purchase:", np.array(["A", "B"])[costs.argmin(axis=1)])
```

```text
[[331.5 322.5]
 [345.  347. ]
 [265.5 260. ]]
shape: (3, 3) @ (3, 2) -> (3, 2)
cheapest shop for each purchase: ['B' 'A' 'B']
```

Одне множення матриць порахувало вартість кожної покупки в кожному магазині.

## `*` чи `@`

| Оператор | Операція | Вимога до форм |
|---|---|---|
| `A * B` | поелементне множення | однакові форми або broadcasting |
| `A @ B`, `np.matmul(A, B)`, `np.dot(A, B)` | матричне множення | стовпці `A` = рядки `B` |

```python
# Program: element-wise and matrix products differ
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print("A * B:\n", A * B)
print("A @ B:\n", A @ B)
print("A @ B == B @ A:", np.array_equal(A @ B, B @ A))
```

```text
A * B:
 [[ 5 12]
 [21 32]]
A @ B:
 [[19 22]
 [43 50]]
A @ B == B @ A: False
```

Матричне множення **не комутативне**: *AB ≠ BA* у загальному випадку.

## Транспонування й одинична матриця

```python
# Program: transpose and identity
import numpy as np

A = np.array([[1, 2, 3], [4, 5, 6]])
I = np.eye(2)
print("A.T:\n", A.T)
print("I @ A equals A:", np.array_equal(I @ A, A))
print("(A @ A.T) is symmetric:", np.array_equal(A @ A.T, (A @ A.T).T))
```

```text
A.T:
 [[1 4]
 [2 5]
 [3 6]]
I @ A equals A: True
(A @ A.T) is symmetric: True
```

## Визначник

**Визначник** *det A* квадратної матриці показує, чи вона **невироджена**: якщо *det A = 0*, у матриці немає оберненої, а система *Ax = b* не має єдиного розвʼязку.

```python
# Program: determinants
import numpy as np

A = np.array([[2.0, 1.0], [5.0, 3.0]])
singular = np.array([[1.0, 2.0], [2.0, 4.0]])  # другий рядок = 2 × перший
print("det A:", round(np.linalg.det(A), 6))
print("det singular:", round(np.linalg.det(singular), 6))
```

```text
det A: 1.0
det singular: 0.0
```

`det` рахується з похибкою чисел з рухомою комою, тому результат округлюють або порівнюють з нулем приблизно.

## Обернена матриця

**Обернена** матриця *A⁻¹* задовольняє *A·A⁻¹ = I*:

```python
# Program: the inverse matrix
import numpy as np

A = np.array([[2.0, 1.0], [5.0, 3.0]])
A_inv = np.linalg.inv(A)
print(A_inv)
print("A @ A_inv is identity:", np.allclose(A @ A_inv, np.eye(2)))

try:
    np.linalg.inv(np.array([[1.0, 2.0], [2.0, 4.0]]))
except np.linalg.LinAlgError as error:
    print("error:", error)
```

```text
[[ 3. -1.]
 [-5.  2.]]
A @ A_inv is identity: True
error: Singular matrix
```

## Системи лінійних рівнянь: `np.linalg.solve`

Задача. Студент купив 3 зошити і 2 ручки за 136 грн, а одногрупник — 2 зошити й 5 ручок за 175 грн. Скільки коштує зошит і ручка?

```text
3x + 2y = 136        | 3  2 |   | x |   | 136 |
2x + 5y = 175   <=>  | 2  5 | · | y | = | 175 |
```

```python
# Program: solve a system of linear equations
import numpy as np

A = np.array([[3.0, 2.0],
              [2.0, 5.0]])
b = np.array([136.0, 175.0])
x = np.linalg.solve(A, b)
print("notebook:", x[0], "| pen:", x[1])
print("check:", A @ x, np.allclose(A @ x, b))
```

```text
notebook: 30.0 | pen: 23.0
check: [136. 175.] True
```

Систему з трьома й більше невідомими розвʼязують так само. Наприклад, баланс трьох рахунків:

```python
# Program: three unknowns
import numpy as np

# card + cash + savings = 5000; card - cash = 1200; savings = 2 * cash
A = np.array([[1.0, 1.0, 1.0],
              [1.0, -1.0, 0.0],
              [0.0, -2.0, 1.0]])
b = np.array([5000.0, 1200.0, 0.0])
card, cash, savings = np.linalg.solve(A, b)
print(f"card {card:.2f}, cash {cash:.2f}, savings {savings:.2f}")
```

```text
card 2150.00, cash 950.00, savings 1900.00
```

!!! tip "`solve`, а не `inv(A) @ b`"
    Математично *x = A⁻¹b*, але обчислювати обернену матрицю, щоб розвʼязати систему, не варто: `np.linalg.solve` швидший і точніший, особливо для великих матриць.

## Коли розвʼязку немає: ранг і вироджені матриці

**Ранг** матриці — кількість лінійно незалежних рядків. Якщо ранг квадратної матриці менший за її розмір, рівняння системи «повторюють» одне одного, і єдиного розвʼязку немає:

```python
# Program: rank and a system without a unique solution
import numpy as np

A = np.array([[1.0, 2.0], [2.0, 4.0]])
b = np.array([3.0, 6.0])
print("rank:", np.linalg.matrix_rank(A), "of", A.shape[0])
try:
    np.linalg.solve(A, b)
except np.linalg.LinAlgError as error:
    print("solve failed:", error)
print("condition number is huge:", np.linalg.cond(A) > 1e15)
```

```text
rank: 1 of 2
solve failed: Singular matrix
condition number is huge: True
```

**Число обумовленості** (`cond`) показує, наскільки розвʼязок чутливий до малих змін даних. Дуже велике значення — сигнал, що результат ненадійний.

## Метод найменших квадратів: лінія тренду

Коли рівнянь **більше**, ніж невідомих (точок даних більше, ніж параметрів), точного розвʼязку зазвичай немає. **Метод найменших квадратів** знаходить параметри, за яких сума квадратів похибок мінімальна. Так будують лінію тренду *y = kx + c* — наприклад, як ростуть витрати з місяця в місяць:

```python
# Program: fit a trend line with least squares
import numpy as np

months = np.arange(1, 7)
spent = np.array([7200.0, 7450.0, 7300.0, 7900.0, 8100.0, 8350.0])
A = np.column_stack([months, np.ones_like(months)])  # стовпці: x і 1
(k, c), *_ = np.linalg.lstsq(A, spent)
print(f"trend: {k:.1f} UAH per month, start {c:.1f}")
print("forecast for month 7:", round(k * 7 + c, 1))
print("same with polyfit:", np.round(np.polyfit(months, spent, 1), 1))
```

```text
trend: 237.1 UAH per month, start 6886.7
forecast for month 7: 8546.7
same with polyfit: [ 237.1 6886.7]
```

`np.polyfit(x, y, degree)` — зручна обгортка для поліноміального тренду; у лекції 37 побудуємо цю лінію на графіку.

## Власні значення і власні вектори

**Власний вектор** *v* матриці *A* під час множення лише змінює довжину: *Av = λv*, де *λ* — **власне значення**. Власні вектори показують «головні напрямки» перетворення; на них побудовано метод головних компонент (стиснення даних), аналіз стійкості систем, алгоритм PageRank.

```python
# Program: eigenvalues and eigenvectors
import numpy as np

A = np.array([[2.0, 0.0],
              [0.0, 3.0]])
values, vectors = np.linalg.eigh(A)  # eigh — для симетричних матриць, результат дійсний
print("eigenvalues:", values)
print("eigenvectors (columns):\n", vectors)
v = vectors[:, 1]
print("A @ v equals 3 * v:", np.allclose(A @ v, 3 * v))

# ланцюг Маркова: студент сьогодні вдома (0) чи в кафе (1)
P = np.array([[0.8, 0.2],
              [0.4, 0.6]])
values, vectors = np.linalg.eig(P.T)
stationary = np.real(vectors[:, np.isclose(values, 1)]).ravel()
stationary /= stationary.sum()
print("long run share of days home / cafe:", np.round(stationary, 3))
```

```text
eigenvalues: [2. 3.]
eigenvectors (columns):
 [[1. 0.]
 [0. 1.]]
A @ v equals 3 * v: True
long run share of days home / cafe: [0.667 0.333]
```

`np.linalg.eig` працює для будь-яких квадратних матриць і в NumPy 2 повертає комплексні числа (власні значення несиметричної матриці можуть бути комплексними), тому дійсну частину беремо `np.real`. Для симетричних матриць є `np.linalg.eigh` — швидша і повертає дійсні значення.

Власний вектор зі значенням 1 для матриці переходів дає **стаціонарний розподіл**: у довгостроковій перспективі студент дві третини днів проводить удома.

## Точність обчислень: `allclose`

Числа з рухомою комою мають похибку (лекція 4, 5 семестр), тому результати лінійної алгебри порівнюють **приблизно**:

```python
# Program: compare floating point results approximately
import numpy as np

A = np.array([[0.1, 0.2], [0.3, 0.4]])
product = A @ np.linalg.inv(A)
print(product)
print("exact equality:", np.array_equal(product, np.eye(2)))
print("approximate equality:", np.allclose(product, np.eye(2)))
```

```text
[[ 1.00000000e+00  3.33066907e-17]
 [-2.22044605e-17  1.00000000e+00]]
exact equality: False
approximate equality: True
```

`np.allclose(a, b)` перевіряє, що `|a - b| <= atol + rtol * |b|` для всіх елементів (типово `rtol=1e-05`, `atol=1e-08`).

## Типові помилки

| Помилка | Чому погано | Як правильно |
|---|---|---|
| `A * B` для матричного добутку | поелементне множення | `A @ B` |
| Невідповідні розміри | `ValueError: matmul: Input operand 1 has a mismatch in its core dimension` | стовпці `A` = рядки `B` |
| `inv(A) @ b` для системи | повільніше й менш точно | `np.linalg.solve(A, b)` |
| Не обробляють `LinAlgError` | програма падає на виродженій матриці | `try/except np.linalg.LinAlgError` |
| `det(A) == 0` | через похибку майже ніколи не точний нуль | `matrix_rank`, `cond`, `np.isclose` |
| Точне порівняння результатів | `False` через `1e-17` | `np.allclose` |
| Одновимірний вектор як стовпець | плутанина з формами | `reshape(-1, 1)`, коли потрібна саме матриця |

## Підсумок

- Вектори — одновимірні масиви; **скалярний добуток** `a @ b`, довжина `np.linalg.norm`.
- **Матричне множення** — оператор `@`; `*` — поелементне множення; *AB ≠ BA*.
- `np.linalg.det` — визначник, `inv` — обернена матриця, `matrix_rank` і `cond` — перевірка виродженості.
- Системи *Ax = b* розвʼязує `np.linalg.solve`; для виродженої матриці — `LinAlgError`.
- Метод найменших квадратів (`lstsq`, `polyfit`) будує лінію тренду, коли точок більше, ніж параметрів.
- `np.linalg.eig` дає власні значення й вектори; результати порівнюють `np.allclose`.

## Корисні посилання

- [NumPy — Linear algebra (`numpy.linalg`)](https://numpy.org/doc/stable/reference/routines.linalg.html)
- [NumPy — `numpy.linalg.solve`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html)
- [NumPy — `numpy.linalg.lstsq`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html)
- [3Blue1Brown — Essence of linear algebra](https://www.3blue1brown.com/topics/linear-algebra)
- Strang G. Introduction to Linear Algebra. — Wellesley-Cambridge Press, 2023.
