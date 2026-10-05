import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from math import sin, cos, pi, exp, sqrt

# ============================================================
#  Метод ломаных (Пиявского)
# ============================================================
def pyavsky_method(f, a, b, L, eps, max_iter=100000):
    X = [float(a), float(b)]
    F = [float(f(a)), float(f(b))]
    history = []

    for it in range(max_iter):
        best_lower = np.inf
        x_next = None

        for i in range(len(X) - 1):
            x1, x2 = X[i], X[i + 1]
            f1, f2 = F[i], F[i + 1]

            # Точка пересечения прямых миноранты
            x_cross = (f1 + L * x1 - f2 + L * x2) / (2.0 * L)

            def phi_interval(x, x1=x1, x2=x2, f1=f1, f2=f2):
                return max(f1 - L * (x - x1), f2 - L * (x2 - x))

            if x1 < x_cross < x2:
                phi_min = phi_interval(x_cross)
            else:
                phi1 = phi_interval(x1)
                phi2 = phi_interval(x2)
                if phi1 <= phi2:
                    x_cross, phi_min = x1, phi1
                else:
                    x_cross, phi_min = x2, phi2

            if phi_min < best_lower:
                best_lower = phi_min
                x_next = x_cross

        f_next = float(f(x_next))
        upper = min(min(F), f_next)

        history.append({
            'iter': it + 1,
            'x_new': x_next,
            'f_new': f_next,
            'lower': best_lower,
            'upper': upper
        })

        if upper - best_lower <= eps:
            break

        pos = 0
        while pos < len(X) and X[pos] < x_next:
            pos += 1
        if pos > 0 and abs(X[pos - 1] - x_next) < 1e-15:
            continue
        X.insert(pos, x_next)
        F.insert(pos, f_next)

    best_idx = int(np.argmin(F))
    return X[best_idx], F[best_idx], len(history), history, X, F


# ============================================================
#  Визуализация — БЕЗ plt.show(), только сохранение в файл
# ============================================================
def visualize(f, a, b, X, F, x_best, f_best, history, eps, title,
              save_path):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # ---- График 1: функция и ломаная ----
    ax = axes[0]
    xs = np.linspace(a, b, 3000)
    ys = np.array([f(x) for x in xs])
    ax.plot(xs, ys, 'b-', linewidth=1.8, label='f(x)', alpha=0.85)

    Xs = np.array(X)
    Fs = np.array(F)
    ax.plot(Xs, Fs, 'ro-', markersize=4, linewidth=1.2,
            label='Вершины ломаной', alpha=0.8)

    ax.plot(x_best, f_best, 'g*', markersize=22,
            label=f'min: x={x_best:.6f}\nf={f_best:.6f}')
    ax.axvline(x_best, color='g', linestyle='--', alpha=0.5)

    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title(f'{title}\nТочек: {len(X)}, итераций: {len(history)}, ε={eps}')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)

    # ---- График 2: сходимость ----
    ax2 = axes[1]
    iters = [h['iter'] for h in history]
    lowers = [h['lower'] for h in history]
    uppers = [h['upper'] for h in history]

    ax2.plot(iters, uppers, 'r-', linewidth=1.5, label='Верхняя оценка (min f)')
    ax2.plot(iters, lowers, 'b-', linewidth=1.5, label='Нижняя оценка (миноранта)')
    ax2.fill_between(iters, lowers, uppers, alpha=0.2, color='gray')
    ax2.axhline(f_best, color='g', linestyle='--',
                label=f'Найденный min = {f_best:.6f}')

    ax2.set_xlabel('Итерация')
    ax2.set_ylabel('Значение')
    ax2.set_title('Сходимость метода ломаных')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)

    ax2.set_xlim(1, min(len(history), 150))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)          # ← ОБЯЗАТЕЛЬНО: закрываем фигуру, освобождаем память
    print(f"  → Сохранено: {save_path}")


# ============================================================
#  Тестовые функции
# ============================================================
def rastrigin_1d(x):
    return 10.0 + x**2 - 10.0 * cos(2.0 * pi * x)

def ackley_1d(x):
    return -20.0 * exp(-0.2 * sqrt(x**2)) - exp(cos(2.0 * pi * x)) + 20.0 + np.e

def multi_min(x):
    return x + sin(pi * x)

def double_well(x):
    return (x**2 - 1.0)**2 + 0.3 * x


# ============================================================
#  ЗАПУСК ТЕСТОВ — 4 функции, 4 файла
# ============================================================
if __name__ == "__main__":
    tests = [
        {
            'name': 'Функция Растригина (1D)',
            'f': rastrigin_1d,
            'a': -3.0, 'b': 3.0,
            'L': 70.0,
            'eps': 0.01,
            'file': 'result_1_rastrigin.png'
        },
        {
            'name': 'Функция Экли (1D)',
            'f': ackley_1d,
            'a': -3.0, 'b': 3.0,
            'L': 15.0,
            'eps': 0.01,
            'file': 'result_2_ackley.png'
        },
        {
            'name': 'f(x) = x + sin(pi * x)',
            'f': multi_min,
            'a': -2.0, 'b': 2.0,
            'L': 4.5,
            'eps': 0.0001,
            'file': 'result_3_x_plus_sin.png'
        },
        {
            'name': 'Двухъямная функция (x²-1)² + 0.3x',
            'f': double_well,
            'a': -2.0, 'b': 2.0,
            'L': 25.0,
            'eps': 0.001,
            'file': 'result_4_double_well.png'
        }
    ]

    results_summary = []

    for t in tests:
        print("=" * 65)
        print(f"ТЕСТ: {t['name']}")
        print("=" * 65)

        start = time.time()
        x_best, f_best, n_iter, history, X, F = pyavsky_method(
            t['f'], t['a'], t['b'], t['L'], t['eps']
        )
        elapsed = time.time() - start

        print(f"  Отрезок:            [{t['a']}, {t['b']}]")
        print(f"  Точность eps:       {t['eps']}")
        print(f"  Константа L:        {t['L']}")
        print(f"  Найденный x*:       {x_best:.8f}")
        print(f"  Найденный f(x*):    {f_best:.8f}")
        print(f"  Число итераций:     {n_iter}")
        print(f"  Число точек:        {len(X)}")
        print(f"  Затраченное время:  {elapsed:.4f} сек")

        visualize(t['f'], t['a'], t['b'], X, F,
                  x_best, f_best, history, t['eps'], t['name'],
                  save_path=t['file'])

        results_summary.append({
            'name': t['name'],
            'x*': x_best,
            'f(x*)': f_best,
            'iters': n_iter,
            'points': len(X),
            'time': elapsed,
            'file': t['file']
        })
        print()

    # ---- Итоговая таблица ----
    print("=" * 90)
    print("ИТОГОВАЯ ТАБЛИЦА")
    print("=" * 90)
    print(f"{'Функция':<40} {'x*':>10} {'f(x*)':>10} {'Итер.':>7} {'Время, с':>10}")
    print("-" * 90)
    for r in results_summary:
        print(f"{r['name']:<40} {r['x*']:>10.6f} {r['f(x*)']:>10.6f} "
              f"{r['iters']:>7} {r['time']:>10.4f}")
    print("=" * 90)
    print("\nСохранённые файлы:")
    for r in results_summary:
        print(f"  • {r['file']}  —  {r['name']}")