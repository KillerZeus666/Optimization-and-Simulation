import networkx as nx
import matplotlib.pyplot as plt
import pulp
import pandas as pd


# ============================================================
# 1️⃣ LEER GRAFO
# ============================================================

def leer_grafo(nombre_archivo):

    df = pd.read_csv(nombre_archivo)

    df.columns = df.columns.str.replace('\u200b', '', regex=True)
    df.columns = df.columns.str.strip()
    df = df.replace('\u200b', '', regex=True)

    for col in ["Origen", "Destino", "Costo", "Capacidad"]:
        df[col] = pd.to_numeric(df[col])

    G = nx.DiGraph()

    for _, row in df.iterrows():
        if row["Capacidad"] > 0:
            G.add_edge(
                int(row["Origen"]),
                int(row["Destino"]),
                cost=float(row["Costo"]),
                capacity=float(row["Capacidad"]),
                flow=0
            )

    return G


# ============================================================
# 2️⃣ SOLUCIÓN FACTIBLE INICIAL
# ============================================================

def solucion_factible(G, source, sink, demanda):

    model = pulp.LpProblem("MinCostFlow", pulp.LpMinimize)

    x = {}
    for u, v in G.edges():
        x[(u, v)] = pulp.LpVariable(
            f"x_{u}_{v}",
            lowBound=0,
            upBound=G[u][v]["capacity"]
        )

    model += pulp.lpSum(
        G[u][v]["cost"] * x[(u, v)]
        for u, v in G.edges()
    )

    for nodo in G.nodes():

        if nodo == source:
            model += (
                pulp.lpSum(x[(source, j)] for j in G.successors(source))
                - pulp.lpSum(x[(i, source)] for i in G.predecessors(source))
                == demanda
            )

        elif nodo == sink:
            model += (
                pulp.lpSum(x[(i, sink)] for i in G.predecessors(sink))
                - pulp.lpSum(x[(sink, j)] for j in G.successors(sink))
                == demanda
            )

        else:
            model += (
                pulp.lpSum(x[(i, nodo)] for i in G.predecessors(nodo))
                - pulp.lpSum(x[(nodo, j)] for j in G.successors(nodo))
                == 0
            )

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    for u, v in G.edges():
        G[u][v]["flow"] = x[(u, v)].value()

    return G


# ============================================================
# 3️⃣ RED RESIDUAL
# ============================================================

def crear_residual(G):

    R = nx.DiGraph()

    for u, v in G.edges():

        cap = G[u][v]["capacity"]
        flow = G[u][v]["flow"]
        cost = G[u][v]["cost"]

        if flow < cap:
            R.add_edge(u, v,
                       capacity=cap - flow,
                       cost=cost)

        if flow > 0:
            R.add_edge(v, u,
                       capacity=flow,
                       cost=-cost)

    return R


# ============================================================
# 4️⃣ BUSCAR CICLO NEGATIVO CORRECTAMENTE
# ============================================================

def encontrar_ciclo_negativo(R):

    nodes = list(R.nodes())
    dist = {n: 0 for n in nodes}
    parent = {}

    # Bellman-Ford completo
    for _ in range(len(nodes)):
        updated = False
        for u, v in R.edges():
            if dist[v] > dist[u] + R[u][v]["cost"]:
                dist[v] = dist[u] + R[u][v]["cost"]
                parent[v] = u
                updated = True
        if not updated:
            break

    # Buscar ciclo negativo
    for u, v in R.edges():
        if dist[v] > dist[u] + R[u][v]["cost"]:

            # Encontramos nodo dentro del ciclo
            ciclo_nodo = v
            for _ in range(len(nodes)):
                ciclo_nodo = parent[ciclo_nodo]

            # Reconstruir ciclo
            ciclo = [ciclo_nodo]
            actual = parent[ciclo_nodo]

            while actual != ciclo_nodo:
                ciclo.append(actual)
                actual = parent[actual]

            ciclo.append(ciclo_nodo)
            ciclo.reverse()

            return ciclo

    return None


# ============================================================
# 5️⃣ CYCLE CANCELING COMPLETO
# ============================================================

def cycle_canceling(G, source, sink, demanda):

    G = solucion_factible(G, source, sink, demanda)

    iteracion = 1

    while True:

        R = crear_residual(G)
        ciclo = encontrar_ciclo_negativo(R)

        if ciclo is None:
            print("\nNo hay más ciclos negativos.")
            break

        print(f"\nIteración {iteracion}")
        print("Ciclo negativo:", ciclo)

        aristas = [(ciclo[i], ciclo[i+1]) for i in range(len(ciclo)-1)]

        delta = min(R[u][v]["capacity"] for u, v in aristas)
        print("Delta:", delta)

        for u, v in aristas:
            if G.has_edge(u, v):
                G[u][v]["flow"] += delta
            else:
                G[v][u]["flow"] -= delta

        iteracion += 1

    return G


# ============================================================
# 6️⃣ COSTO TOTAL
# ============================================================

def costo_total(G):
    return sum(G[u][v]["flow"] * G[u][v]["cost"] for u, v in G.edges())


# ============================================================
# MAIN
# ============================================================

G = leer_grafo("Datos grafo.txt")

source = 1
sink = 6
demanda = 50

G_final = cycle_canceling(G, source, sink, demanda)

print("\nFlujos finales:")
for u, v in G_final.edges():
    print(f"{u} -> {v} : {G_final[u][v]['flow']}")

print("\nCosto total final:", costo_total(G_final))