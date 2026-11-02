from itertools import product

# Доходы стартапов при вложении от 1 до 7 млн.
income = {
    1: {1: 5, 2: 9, 3: 12, 4: 14, 5: 15, 6: 16, 7: 17},
    2: {1: 8, 2: 14, 3: 18, 4: 21, 5: 30, 6: 34, 7: 36},
    3: {1: 4, 2: 7, 3: 11, 4: 16, 5: 18, 6: 19, 7: 20},
}

TOTAL = 9
MIN_INVESTMENT = 1
MAX_SECOND = 4

# Этап 1 динамического программирования: третий стартап.
F3 = {s: income[3][s] for s in range(1, 8)}

# Этап 2: второй и третий стартапы.
F2 = {}
choice2 = {}

for s in range(2, 9):
    best = float("-inf")
    best_choices = []

    for x2 in range(1, min(MAX_SECOND, s - 1) + 1):
        x3 = s - x2
        if x3 not in income[3]:
            continue

        candidate = income[2][x2] + F3[x3]

        if candidate > best:
            best = candidate
            best_choices = [(x2, x3)]
        elif candidate == best:
            best_choices.append((x2, x3))

    F2[s] = best
    choice2[s] = best_choices

# Этап 3: выбираем вложение в первый стартап.
best_total = float("-inf")
best_plans = []

for x1 in range(1, 8):
    remaining = TOTAL - x1
    if remaining not in F2:
        continue

    candidate = income[1][x1] + F2[remaining]

    if candidate > best_total:
        best_total = candidate
        best_plans = []

    if candidate == best_total:
        for x2, x3 in choice2[remaining]:
            best_plans.append((x1, x2, x3))

print("Таблица F3:")
print(F3)

print("\nТаблица F2:")
for s in sorted(F2):
    print(f"s={s}: F2={F2[s]}, варианты={choice2[s]}")

print("\nИтоговые варианты:")
for x1 in range(1, 8):
    remaining = TOTAL - x1
    if remaining in F2:
        value = income[1][x1] + F2[remaining]
        print(f"x1={x1}, доход={value}")

print("\nМаксимальный доход:", best_total)
print("Оптимальные планы:", best_plans)

# Проверка ограничений и дохода каждого оптимального плана.
for x1, x2, x3 in best_plans:
    assert x1 + x2 + x3 == TOTAL
    assert x1 >= MIN_INVESTMENT
    assert MIN_INVESTMENT <= x2 <= MAX_SECOND
    assert x3 >= MIN_INVESTMENT

    actual = income[1][x1] + income[2][x2] + income[3][x3]
    assert actual == best_total

# Независимая проверка полным перебором.
all_plans = []

for x1, x2, x3 in product(range(1, 8), repeat=3):
    if x1 + x2 + x3 != TOTAL:
        continue
    if not (MIN_INVESTMENT <= x2 <= MAX_SECOND):
        continue

    value = income[1][x1] + income[2][x2] + income[3][x3]
    all_plans.append((value, x1, x2, x3))

brute_best = max(value for value, _, _, _ in all_plans)
assert brute_best == best_total

all_optimal_plans = [
    (x1, x2, x3)
    for value, x1, x2, x3 in all_plans
    if value == brute_best
]

assert set(best_plans) == set(all_optimal_plans)

print("\nПроверка полным перебором:", brute_best)
print("Все оптимальные планы:", all_optimal_plans)
print("Все проверки пройдены.")
