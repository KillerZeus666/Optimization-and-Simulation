import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ==========================
# 1. Leer CSV
# ==========================

df = pd.read_csv("matriz_de_datos.csv")

# ==========================
# 2. Crear grafo
# ==========================

G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_edge(int(row["Origen"]), int(row["Destino"]))

print("Nodos:", G.number_of_nodes())
print("Aristas:", G.number_of_edges())

# ==========================
# 3. Definir nodos
# ==========================

origenes = [1,2]
destinos = [78,79,80]

intermedios = [n for n in G.nodes() if n not in origenes and n not in destinos]

# ==========================
# 4. Crear posiciones
# ==========================

pos = {}

# ORIGENES (no tan lejos)
for i, node in enumerate(origenes):
    pos[node] = (2, -i*4)

# DESTINOS (un poco más alejados)
for i, node in enumerate(destinos):
    pos[node] = (18, -i*4)

# INTERMEDIOS (rejilla central)
cols = 10
spacing_x = 1.2
spacing_y = 1.4

for i, node in enumerate(intermedios):

    col = i % cols
    row = i // cols

    x = 6 + col * spacing_x
    y = -row * spacing_y

    pos[node] = (x, y)

# ==========================
# 5. Colores
# ==========================

node_colors = []

for node in G.nodes():

    if node in origenes:
        node_colors.append("green")

    elif node in destinos:
        node_colors.append("red")

    else:
        node_colors.append("skyblue")

# ==========================
# 6. Dibujar grafo
# ==========================

plt.figure(figsize=(22,14))

nx.draw_networkx_nodes(
    G,
    pos,
    node_color=node_colors,
    node_size=220
)

nx.draw_networkx_edges(
    G,
    pos,
    arrows=True,
    width=0.5,
    alpha=0.5
)

nx.draw_networkx_labels(
    G,
    pos,
    font_size=7
)

plt.title("Red del sistema (Orígenes → Intermedios → Destinos)", fontsize=16)

plt.axis("off")

plt.tight_layout()

plt.savefig("grafo_final_distribuido.png", dpi=300)

plt.show()