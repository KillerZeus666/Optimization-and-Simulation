# ============================================================
# LIBRERÍAS
# ============================================================

import pandas as pd
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import time   # ⏱️ para medir tiempo


# ============================================================
# 1️⃣ LEER Y LIMPIAR ARCHIVO
# ============================================================

def leer_datos(nombre_archivo):

    df = pd.read_csv(nombre_archivo)

    df.columns = df.columns.str.replace('\u200b', '', regex=True)
    df.columns = df.columns.str.strip()
    df = df.replace('\u200b', '', regex=True)

    for col in ["Origen", "Destino", "Costo", "Capacidad"]:
        df[col] = pd.to_numeric(df[col])

    df = df[df["Capacidad"] > 0]

    return df


# ============================================================
# 2️⃣ MODELO MAX FLOW (PuLP)
# ============================================================

def max_flow_lp(df, source, sink):

    model = pulp.LpProblem("MaxFlow", pulp.LpMaximize)

    x = {}

    for _, row in df.iterrows():
        i = int(row["Origen"])
        j = int(row["Destino"])
        cap = row["Capacidad"]

        x[(i, j)] = pulp.LpVariable(
            f"x_{i}_{j}",
            lowBound=0,
            upBound=cap
        )

    # Función objetivo
    model += pulp.lpSum(
        x[(i, j)]
        for (i, j) in x if i == source
    )

    # Conservación de flujo
    nodos = set(df["Origen"]).union(set(df["Destino"]))

    for nodo in nodos:

        if nodo != source and nodo != sink:

            flujo_entrante = pulp.lpSum(
                x[(i, j)] for (i, j) in x if j == nodo
            )

            flujo_saliente = pulp.lpSum(
                x[(i, j)] for (i, j) in x if i == nodo
            )

            model += flujo_entrante == flujo_saliente

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    return model, x


# ============================================================
# 3️⃣ DIBUJAR GRAFO
# ============================================================

def dibujar_grafo(df, variables):

    G = nx.DiGraph()

    for _, row in df.iterrows():
        i = int(row["Origen"])
        j = int(row["Destino"])
        cap = row["Capacidad"]
        flujo = variables[(i, j)].value()

        G.add_edge(i, j, capacity=cap, flow=flujo)

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

    plt.title("Flujo Máximo")
    plt.show()


# ============================================================
# MAIN
# ============================================================

df = leer_datos("Datos grafo.txt")

source = 1
sink = 6

# ⏱️ INICIO DEL RELOJ
inicio = time.time()

modelo, variables = max_flow_lp(df, source, sink)

# ⏱️ FIN DEL RELOJ
fin = time.time()

tiempo_total = fin - inicio

print("Estado:", pulp.LpStatus[modelo.status])
print("Flujo máximo total:", pulp.value(modelo.objective))
print(f"Tiempo de ejecución: {tiempo_total:.6f} segundos")

print("\nFlujos en cada arco:")
for (i, j), var in variables.items():
    if var.value() > 0:
        print(f"{i} -> {j} : {var.value()}")

dibujar_grafo(df, variables)