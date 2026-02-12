import numpy as np
import matplotlib.pyplot as plt

# Definición del rango para x1
x = np.linspace(0, 15, 400)

def plot_setup(title):
    plt.figure(figsize=(8, 6))
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    plt.xlabel('$x_1$')
    plt.ylabel('$x_2$')
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.7)

# --- 1. Restricción 1: 0.3x1 + 0.1x2 <= 2.7 ---
plot_setup('Restricción 1: $0.3x_1 + 0.1x_2 \leq 2.7$')
y1 = (2.7 - 0.3 * x) / 0.1
plt.plot(x, y1, label='0.3x1 + 0.1x2 = 2.7', color='blue')
plt.fill_between(x, 0, y1, where=(y1>=0), color='blue', alpha=0.2)
plt.xlim(0, 15); plt.ylim(0, 30); plt.legend(); plt.show()

# --- 2. Restricción 2: 0.5x1 + 0.5x2 = 6 ---
plot_setup('Restricción 2: $0.5x_1 + 0.5x_2 = 6$ (Igualdad)')
y2 = (6 - 0.5 * x) / 0.5
plt.plot(x, y2, label='0.5x1 + 0.5x2 = 6', color='red', linewidth=3)
plt.xlim(0, 15); plt.ylim(0, 15); plt.legend(); plt.show()

# --- 3. Restricción 3: 0.6x1 + 0.4x2 >= 6 ---
plot_setup('Restricción 3: $0.6x_1 + 0.4x_2 \geq 6$')
y3 = (6 - 0.6 * x) / 0.4
plt.plot(x, y3, label='0.6x1 + 0.4x2 = 6', color='green')
plt.fill_between(x, y3, 30, color='green', alpha=0.2)
plt.xlim(0, 15); plt.ylim(0, 15); plt.legend(); plt.show()

# --- 4. GRÁFICO FINAL: Región Factible ---
plot_setup('Región Factible (Segmento de Recta)')
y1 = (2.7 - 0.3 * x) / 0.1
y2 = (6 - 0.5 * x) / 0.5
y3 = (6 - 0.6 * x) / 0.4

plt.plot(x, y1, '--', color='blue', alpha=0.5, label='R1 (<=)')
plt.plot(x, y2, color='black', linewidth=2, label='R2 (=)')
plt.plot(x, y3, '--', color='green', alpha=0.5, label='R3 (>=)')

# Hallar los puntos de intersección calculados previamente
# Punto A: Intersección R2 y R3 (6, 6)
# Punto B: Intersección R1 y R2 (7.5, 4.5)
plt.plot([6, 7.5], [6, 4.5], color='red', linewidth=5, label='REGIÓN FACTIBLE')
plt.scatter([6, 7.5], [6, 4.5], color='black', zorder=5)

plt.annotate('A (6,6)', (6, 6.5))
plt.annotate('B (7.5, 4.5)', (7.5, 5))

plt.xlim(4, 10)
plt.ylim(2, 10)
plt.legend()
plt.show()