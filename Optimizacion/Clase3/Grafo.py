# Instrucciones de instalación (ejecutar antes si no está instalado):
# pip install graphviz
# Además, asegúrate de tener Graphviz instalado en el sistema:
# Windows: https://graphviz.org/download/
# Linux (Debian/Ubuntu): sudo apt-get install graphviz
# macOS (brew): brew install graphviz

from graphviz import Digraph

# Crear el grafo dirigido
dot = Digraph(
    name="RedDirigida",
    format="png",
    graph_attr={
        "rankdir": "LR",          # Izquierda a derecha
        "splines": "true",        # Curvas solo si es necesario
        "nodesep": "0.8",
        "ranksep": "1.2"
    }
)

# Estilo de nodos
dot.attr(
    "node",
    shape="circle",
    style="filled",
    fillcolor="#cce5ff",  # Azul claro
    color="black",
    fontname="Helvetica"
)

# Definición de nodos
nodos = ["1", "2", "3", "4", "5", "6"]
for n in nodos:
    dot.node(n, n)

# Definición de aristas (Origen, Destino, Costo, Capacidad)
aristas = [
    ("1", "2", 3, 25),
    ("1", "3", 5, 100),
    ("1", "4", 9, 70),
    ("2", "3", 4, 30),
    ("2", "5", 4, 15),
    ("3", "6", 10, 200),
    ("4", "3", 6, 60),
    ("4", "6", 14, 30),
    ("5", "6", 6, 150),
]

# Función para escalar el grosor según la capacidad
def grosor(capacidad):
    return str(max(1.0, capacidad / 40))

# Agregar aristas con etiquetas y estilo
for o, d, c, cap in aristas:
    dot.edge(
        o,
        d,
        label=f"C:{c} | Cap:{cap}",
        penwidth=grosor(cap),
        fontname="Helvetica",
        fontsize="10"
    )

# Subniveles (rank) para jerarquía clara
with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("1")

with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("2")
    s.node("4")

with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("3")
    s.node("5")

with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("6")

# Renderizar el grafo
dot
