import sympy as sp

# Объявление переменных
x, y, z, lmbda = sp.symbols('x y z lmbda')

# Целевая функция и ограничение
f = 2 * x - y + 2 * z
g = x**2 + y**2 + z**2 - 9

# Функция Лагранжа
L = f + lmbda * g

# Частные производные
eq1 = sp.Eq(sp.diff(L, x), 0)
eq2 = sp.Eq(sp.diff(L, y), 0)
eq3 = sp.Eq(sp.diff(L, z), 0)
eq4 = sp.Eq(sp.diff(L, lmbda), 0)

# Решение системы уравнений
solutions = sp.solve((eq1, eq2, eq3, eq4), (x, y, z, lmbda))

print("Найденные точки и значения функции:")
for sol in solutions:
  val = f.subs({x: sol[0], y: sol[1], z: sol[2]})
  print(f"Точка (x, y, z, lambda): {sol}")
  print(f"Значение функции f: {val}\n")