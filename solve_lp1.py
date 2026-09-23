EPS = 1e-9


def pivot(tableau, basis, row, col):
    """Выполнить симплекс-пересчёт вокруг опорного элемента."""
    pivot_value = tableau[row][col]

    if abs(pivot_value) < EPS:
        raise ValueError("Нельзя выполнить pivot: опорный элемент равен 0.")

    width = len(tableau[0])

    # Нормируем ведущую строку.
    for j in range(width):
        tableau[row][j] /= pivot_value

    # Обнуляем ведущий столбец во всех остальных строках.
    for i in range(len(tableau)):
        if i == row:
            continue

        factor = tableau[i][col]

        if abs(factor) > EPS:
            for j in range(width):
                tableau[i][j] -= factor * tableau[row][j]

    basis[row - 1] = col


def set_objective(tableau, basis, costs):
    """
    Устанавливает строку целевой функции в формате:
    z-row = -reduced_costs.

    Для задачи max c*x:
    строка цели начинается с -c.
    Затем выполняется пересчёт относительно текущего базиса.
    """
    width = len(tableau[0])

    for j in range(width - 1):
        tableau[0][j] = -costs[j]

    tableau[0][-1] = 0.0

    # Делаем строку цели канонической относительно базисных переменных.
    for i, basic_col in enumerate(basis, start=1):
        cb = costs[basic_col]

        if abs(cb) > EPS:
            for j in range(width):
                tableau[0][j] += cb * tableau[i][j]


def simplex(tableau, basis, variable_names, max_iterations=100):
    """
    Симплекс-метод для задачи максимизации.

    В строке цели отрицательный коэффициент означает,
    что соответствующая переменная может войти в базис.
    """
    iterations = 0

    while iterations < max_iterations:
        entering = None

        # Выбираем входящую переменную.
        for j in range(len(variable_names)):
            if tableau[0][j] < -EPS:
                entering = j
                break

        # Нет отрицательных коэффициентов -> найден оптимум.
        if entering is None:
            return tableau[0][-1], iterations

        leaving = None
        best_ratio = None

        # Правило минимального отношения.
        for i in range(1, len(tableau)):
            a = tableau[i][entering]

            if a > EPS:
                ratio = tableau[i][-1] / a

                if ratio >= -EPS:
                    if best_ratio is None or ratio < best_ratio - EPS:
                        best_ratio = ratio
                        leaving = i

        if leaving is None:
            raise ValueError("Целевая функция не ограничена.")

        pivot(tableau, basis, leaving, entering)
        iterations += 1

    raise ValueError("Превышено максимальное число итераций.")


def solve_lp():
    # ============================================================
    # Исходная задача:
    #
    # min Z = x1 + 3*x2 + 2*x3 + x4
    #
    # x1 + x2 + 2*x4 <= 8
    # x2 + x3 + x4  = 6
    # 2*x1 + x3     >= 2
    # x1, x2, x3, x4 >= 0
    # ============================================================

    # Каноническая форма:
    #
    # x1 + x2 + 2*x4 + s1       = 8
    # x2 + x3 + x4      + a1    = 6
    # 2*x1 + x3 - s2         + a2 = 2
    #
    # s1 - дополнительная переменная для <=
    # s2 - избыточная переменная для >=
    # a1, a2 - искусственные переменные

    names = ["x1", "x2", "x3", "x4", "s1", "s2", "a1", "a2"]

    rows = [
        [1, 1, 0, 2, 1, 0, 0, 0, 8],
        [0, 1, 1, 1, 0, 0, 1, 0, 6],
        [2, 0, 1, 0, 0, -1, 0, 1, 2],
    ]

    # Начальный базис: s1, a1, a2.
    basis = [4, 6, 7]
    artificial = [6, 7]
    n = len(names)

    tableau = [[0.0] * (n + 1) for _ in range(len(rows) + 1)]

    for i, row in enumerate(rows, start=1):
        tableau[i] = [float(value) for value in row]

    # ============================================================
    # I
    # max F = -a1 - a2
    #
    # Если Fmax = 0, искусственные переменные можно исключить,
    # а исходная задача имеет допустимое решение.
    # ============================================================

    phase1_costs = [0.0] * n
    phase1_costs[6] = -1.0
    phase1_costs[7] = -1.0

    set_objective(tableau, basis, phase1_costs)
    phase1_value, phase1_iterations = simplex(
        tableau, basis, names
    )

    if phase1_value < -EPS:
        raise ValueError("Допустимого решения нет.")

    # Если искусственная переменная осталась в базисе,
    # пытаемся заменить её обычной переменной.
    for i in range(1, len(tableau)):
        basic_col = basis[i - 1]

        if basic_col in artificial:
            pivot_col = None

            for j in range(n):
                if j not in artificial and abs(tableau[i][j]) > EPS:
                    pivot_col = j
                    break

            if pivot_col is not None:
                pivot(tableau, basis, i, pivot_col)

    # Удаляем искусственные столбцы.
    keep = [j for j in range(n) if j not in artificial]
    old_to_new = {old: new for new, old in enumerate(keep)}

    tableau = [
        [row[j] for j in keep] + [row[-1]]
        for row in tableau
    ]

    names = [names[j] for j in keep]
    basis = [old_to_new[b] for b in basis]
    n = len(names)

    # ============================================================
    # II
    #
    # Исходная задача min Z превращается в
    # max(-Z).
    # ============================================================

    costs = [0.0] * n

    costs[names.index("x1")] = -1.0
    costs[names.index("x2")] = -3.0
    costs[names.index("x3")] = -2.0
    costs[names.index("x4")] = -1.0

    set_objective(tableau, basis, costs)

    phase2_max_value, phase2_iterations = simplex(
        tableau, basis, names
    )

    # Восстанавливаем значения переменных.
    solution = {name: 0.0 for name in names}

    for i, basic_col in enumerate(basis, start=1):
        solution[names[basic_col]] = tableau[i][-1]

    # Мы решали max(-Z), поэтому возвращаемся к min Z.
    z_min = -phase2_max_value

    # ============================================================
    # Вывод результата
    # ============================================================

    print("=== Решение задачи линейного программирования ===")
    print("Метод: двухфазный симплекс-метод")
    print("Внешние библиотеки не используются.")
    print()

    print("Оптимальная точка:")
    print("x1 =", round(solution["x1"], 10))
    print("x2 =", round(solution["x2"], 10))
    print("x3 =", round(solution["x3"], 10))
    print("x4 =", round(solution["x4"], 10))
    print()

    print("Минимальное значение Z =", round(z_min, 10))
    print()

    x1 = solution["x1"]
    x2 = solution["x2"]
    x3 = solution["x3"]
    x4 = solution["x4"]

    print("Проверка ограничений:")
    print("1)", x1 + x2 + 2 * x4, "<= 8")
    print("2)", x2 + x3 + x4, "= 6")
    print("3)", 2 * x1 + x3, ">= 2")

if __name__ == "__main__":
    solve_lp()
