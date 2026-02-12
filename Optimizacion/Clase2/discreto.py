Discreto 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Configuración de la figura
fig, ax = plt.subplots(figsize=(9, 7))
plt.subplots_adjust(bottom=0.25)

# 1. Definición de restricciones para el fondo (Visual)
x_vals = np.linspace(0, 5, 400)
r1 = (15 - 5*x_vals) / 3   # 5x + 3y <= 15
r2 = x_vals - 2            # x - y <= 2 -> y >= x - 2
r3 = 3                     # y <= 3

# Dibujar las líneas de las restricciones
ax.plot(x_vals, r1, 'b--', alpha=0.5, label='$5x + 3y \leq 15$')
ax.plot(x_vals, r2, 'g--', alpha=0.5, label='$x - y \leq 2$')
ax.axhline(r3, color='r', linestyle='--', alpha=0.5, label='$y \leq 3$')

# 2. Generar todos los puntos enteros factibles para referencia
puntos_x, puntos_y = [], []
for i in range(5):
    for j in range(5):
        if (5*i + 3*j <= 15) and (i - j <= 2) and (j <= 3):
            puntos_x.append(i)
            puntos_y.append(j)

ax.scatter(puntos_x, puntos_y, color='gray', s=50, alpha=0.3, label='Puntos Factibles')

# 3. Punto móvil controlado por sliders
x_init, y_init = 0, 0
punto_movil, = ax.plot([x_init], [y_init], 'ro', markersize=12, label='Punto Seleccionado')

# Texto informativo
texto_z = ax.text(0.5, 4.2, f'Punto: ({x_init}, {y_init}) | Z = {x_init + y_init} | Estado: Factible', 
                  fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

ax.set_xlim(-0.5, 4.5)
ax.set_ylim(-0.5, 4.5)
ax.set_title('Exploración Discreta: Selecciona coordenadas (x, y)')
ax.legend(loc='upper right', fontsize='small')
ax.grid(True, linestyle=':', alpha=0.6)

# --- Configuración de Sliders Discretos ---
ax_x = plt.axes([0.2, 0.1, 0.6, 0.03])
ax_y = plt.axes([0.2, 0.05, 0.6, 0.03])

# valstep=1 obliga a que el slider solo tome valores enteros
s_x = Slider(ax_x, 'Coordenada X ', 0, 4, valinit=x_init, valstep=1)
s_y = Slider(ax_y, 'Coordenada Y ', 0, 4, valinit=y_init, valstep=1)

def update(val):
    x = int(s_x.val)
    y = int(s_y.val)
    
    # Actualizar posición del punto
    punto_movil.set_data([x], [y])
    
    # Validar si el punto es factible
    es_factible = (5*x + 3*y <= 15) and (x - y <= 2) and (y <= 3)
    estado = "Factible" if es_factible else "No Factible"
    color_punto = 'green' if es_factible else 'red'
    
    punto_movil.set_color(color_punto)
    
    # Actualizar texto
    z = x + y
    texto_z.set_text(f'Punto: ({x}, {y}) | Z = {z} | Estado: {estado}')
    texto_z.set_bbox(dict(facecolor=color_punto, alpha=0.3))
    
    fig.canvas.draw_idle()

s_x.on_changed(update)
s_y.on_changed(update)

plt.show()