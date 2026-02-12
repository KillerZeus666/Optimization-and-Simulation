import networkx as nx
import matplotlib.pyplot as plt

# =========================
# Crear el grafo dirigido
# =========================
G = nx.DiGraph()

datos = [
    (1, 2, 3, 25),
    (1, 3, 5, 100),
    (1, 4, 9, 70),
    (2, 3, 4, 30),
    (2, 5, 4, 15),
    (3, 6, 10, 200),
    (4, 3, 6, 60),
    (4, 6, 14, 30),
    (5, 6, 6, 150)
]

for origen, destino, costo, capacidad in datos:
    G.add_edge(origen, destino, costo=costo, capacidad=capacidad)

# =========================
# Posiciones jerárquicas
# =========================
pos = {
    1: (0, 0),
    2: (1, 1),
    3: (1, 0),
    4: (1, -1),
    5: (2, 0),
    6: (3, 0)
}

# =========================
# Dibujar el grafo
# =========================
plt.figure(figsize=(12, 7))

# Nodos
nx.draw_networkx_nodes(
    G, pos,
    node_size=1800,
    node_color="#CFE1F2",
    edgecolors="black",
    linewidths=1.5
)

# Etiquetas de nodos
nx.draw_networkx_labels(
    G, pos,
    font_size=12,
    font_weight="bold"
)

# =========================
# Aristas bonitas
# =========================
capacidades = [G[u][v]["capacidad"] for u, v in G.edges()]
anchos = [cap / 40 for cap in capacidades]

nx.draw_networkx_edges(
    G, pos,
    arrowstyle="-|>",
    arrowsize=25,
    edge_color="#444444",
    width=anchos,
    connectionstyle="arc3,rad=0.0"  # rectas
)

# =========================
# Etiquetas de aristas
# =========================
edge_labels = {
    (u, v): f"C:{d['costo']} | Cap:{d['capacidad']}"
    for u, v, d in G.edges(data=True)
}

nx.draw_networkx_edge_labels(
    G, pos,
    edge_labels=edge_labels,
    font_size=9,
    bbox=dict(
        boxstyle="round,pad=0.3",
        fc="white",
        ec="gray"
    )
)

# =========================
# Mostrar
# =========================
plt.title("Grafo jerárquico (flujo origen → destino)", fontsize=15)
plt.axis("off")
plt.tight_layout()
plt.show()
