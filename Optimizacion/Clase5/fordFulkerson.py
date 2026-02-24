# ============================================================
# LIBRERÍAS
# ============================================================

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time


# ============================================================
# 1️⃣ LEER Y LIMPIAR ARCHIVO
# ============================================================

def leer_grafo(nombre_archivo):

    df = pd.read_csv(nombre_archivo)

    df.columns = df.columns.str.replace('\u200b', '', regex=True)
    df.columns = df.columns.str.strip()
    df = df.replace('\u200b', '', regex=True)

    for col in ["Origen", "Destino", "Costo", "Capacidad"]:
        df[col] = pd.to_numeric(df[col])

    df = df[df["Capacidad"] > 0]

    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_edge(
            int(row["Origen"]),
            int(row["Destino"]),
            capacity=row["Capacidad"],
            flow=0
        )

    return G


# ============================================================
# 2️⃣ CREAR RED RESIDUAL
# ============================================================

def crear_residual(G):

    R = nx.DiGraph()

    for u, v in G.edges():
        cap = G[u][v]["capacity"]
        flow = G[u][v]["flow"]

        # Arista forward
        if flow < cap:
            R.add_edge(u, v, capacity=cap - flow)

        # Arista backward
        if flow > 0:
            R.add_edge(v, u, capacity=flow)

    return R


# ============================================================
# 3️⃣ BUSCAR CAMINO AUMENTANTE (DFS)
# ============================================================

def buscar_camino(R, source, sink, path=None, visited=None):

    if path is None:
        path = []
    if visited is None:
        visited = set()

    if source == sink:
        return path

    visited.add(source)

    for vecino in R.successors(source):
        if vecino not in visited and R[source][vecino]["capacity"] > 0:
            resultado = buscar_camino(
                R,
                vecino,
                sink,
                path + [(source, vecino)],
                visited
            )
            if resultado is not None:
                return resultado

    return None


# ============================================================
# 4️⃣ FORD-FULKERSON
# ============================================================

def ford_fulkerson(G, source, sink):

    flujo_maximo = 0
    iteracion = 1

    while True:

        R = crear_residual(G)
        camino = buscar_camino(R, source, sink)

        if camino is None:
            print("\nNo existen más caminos aumentantes.")
            break

        print(f"\nIteración {iteracion}")
        print("Camino aumentante:", camino)

        # Encontrar cuello de botella
        delta = min(R[u][v]["capacity"] for u, v in camino)
        print("Capacidad mínima (delta):", delta)

        # Aumentar flujo
        for u, v in camino:
            if G.has_edge(u, v):
                G[u][v]["flow"] += delta
            else:
                G[v][u]["flow"] -= delta

        flujo_maximo += delta
        iteracion += 1

    return flujo_maximo


# ============================================================
# 5️⃣ DIBUJAR GRAFO FINAL
# ============================================================

def dibujar_grafo(G):

    pos = nx.spring_layout(G, seed=42)

    labels = {}
    for u, v in G.edges():
        labels[(u, v)] = f"{G[u][v]['flow']}/{G[u][v]['capacity']}"

    plt.figure(figsize=(8,6))
    nx.draw(G, pos,
            with_labels=True,
            node_color="lightblue",
            node_size=2000)

    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Resultado Ford-Fulkerson")
    plt.show()


# ============================================================
# MAIN
# ============================================================

G = leer_grafo("Datos grafo.txt")

source = 1
sink = 6

inicio = time.time()

flujo_max = ford_fulkerson(G, source, sink)

fin = time.time()

print("\nFlujo máximo total:", flujo_max)
print(f"Tiempo de ejecución: {fin - inicio:.6f} segundos")

dibujar_grafo(G)