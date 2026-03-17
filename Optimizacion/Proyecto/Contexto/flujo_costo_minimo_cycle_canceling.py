# -*- coding: utf-8 -*-
"""
Flujo al Costo Mínimo — Algoritmo de Cycle Canceling (Klein)
=============================================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Fuente   : nodo 1
Sumidero : nodo 80
Demanda total enviada : 500 unidades
Restricción           : al menos el 20 % debe llegar al nodo 80
                        => mínimo 100 unidades deben llegar al destino 80
"""

import csv
import os
from collections import defaultdict, deque
import math

# ═══════════════════════════════════════════════════════════
# 1. LECTURA DEL CSV
# ═══════════════════════════════════════════════════════════
def leer_grafo(ruta_csv: str):
    """
    Devuelve:
      edges   : lista de (u, v, costo, capacidad)
      nodos   : conjunto de todos los nodos
    """
    edges = []
    nodos = set()
    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u   = int(row["Origen"])
            v   = int(row["Destino"])
            c   = int(row["Costo"])
            cap = int(row["Capacidad"])
            edges.append((u, v, c, cap))
            nodos.add(u)
            nodos.add(v)
    return edges, nodos


# ═══════════════════════════════════════════════════════════
# PASO 1 Y 2 — FLUJO FACTIBLE CON BFS Y RED RESIDUAL
# ═══════════════════════════════════════════════════════════
def construir_red_residual(edges):
    """
    Devuelve:
      cap[u][v]  : capacidad residual
      cost[u][v] : costo unitario (negativo en arco inverso)
      adj[u]     : lista de vecinos (incluyendo inversos)
    """
    cap  = defaultdict(lambda: defaultdict(int))
    cost = defaultdict(lambda: defaultdict(int))
    adj  = defaultdict(set)

    for (u, v, c, capacity) in edges:
        cap[u][v]  += capacity
        cost[u][v]  = c
        cost[v][u]  = -c          # arco inverso tiene costo negativo
        adj[u].add(v)
        adj[v].add(u)

    return cap, cost, adj


def bfs_path(cap, adj, s, t):
    """BFS para encontrar camino s→t con cap > 0. Devuelve parent o None."""
    parent = {s: None}
    queue  = deque([s])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in parent and cap[u][v] > 0:
                parent[v] = u
                if v == t:
                    return parent
                queue.append(v)
    return None


def enviar_flujo(cap, cost, adj, s, t, max_units):
    """
    Envía hasta max_units unidades de s→t usando BFS repetido.
    Devuelve (flujo_enviado, costo_total, rutas).
    """
    total_flow = 0
    total_cost = 0
    rutas      = []

    while total_flow < max_units:
        parent = bfs_path(cap, adj, s, t)
        if parent is None:
            break  # No hay más caminos

        # Cuello de botella
        bottleneck = max_units - total_flow
        v = t
        while v != s:
            u = parent[v]
            bottleneck = min(bottleneck, cap[u][v])
            v = u

        # Reconstruir camino y acumular costo
        path = []
        v = t
        path_cost = 0
        while v != s:
            u = parent[v]
            path.append(v)
            path_cost   += cost[u][v] * bottleneck
            cap[u][v]   -= bottleneck
            cap[v][u]   += bottleneck
            v = u
        path.append(s)
        path.reverse()

        total_flow += bottleneck
        total_cost += path_cost
        rutas.append((list(path), bottleneck, path_cost))

    return total_flow, total_cost, rutas


# ═══════════════════════════════════════════════════════════
# PASO 3 Y 4 — CYCLE CANCELING (Detectar bucles, cancelar, actualizar)
# ═══════════════════════════════════════════════════════════
def bellman_ford_negative_cycle(cap, cost, adj, nodes):
    """
    Detecta un ciclo de costo negativo en la red residual (solo arcos con cap>0).
    Devuelve la lista de nodos del ciclo o None si no existe.
    Usa el algoritmo de Bellman-Ford con detección de ciclo por padre.
    """
    nodes = list(nodes)
    dist   = {n: 0 for n in nodes}
    parent = {n: None for n in nodes}

    for _ in range(len(nodes) - 1):
        for u in nodes:
            for v in adj[u]:
                if cap[u][v] > 0 and dist[u] + cost[u][v] < dist[v]:
                    dist[v]   = dist[u] + cost[u][v]
                    parent[v] = u

    # Una relajación más → si mejora, hay ciclo negativo
    for u in nodes:
        for v in adj[u]:
            if cap[u][v] > 0 and dist[u] + cost[u][v] < dist[v]:
                # Reconstruir el ciclo
                visited = {}
                x = v
                for _ in range(len(nodes)):
                    if x in visited:
                        break
                    visited[x] = True
                    x = parent[x]
                # x está dentro del ciclo; recolectarlo
                cycle = []
                start = x
                node  = x
                while True:
                    cycle.append(node)
                    node = parent[node]
                    if node == start:
                        break
                cycle.reverse()
                return cycle
    return None


def cycle_canceling(cap, cost, adj, nodes):
    """
    Pasos 3, 4 y 5 integrados:
    Paso 3: Comprueba si hay un bucle negativo en la red residual. Si no, pasa al Paso 5.
    Paso 4: Reduce el coste inyectando flujo (cancelación). Actualiza residual (Paso 2 rep).
    """
    savings    = 0
    iterations = 0

    while True:
        # PASO 3: Comprobar bucles negativos
        cycle = bellman_ford_negative_cycle(cap, cost, adj, nodes)
        if cycle is None:
            # Pasa al Paso 5 (finaliza el bucle y por tanto el coste es minimo)
            break
        iterations += 1

        # PASO 4: Cancelar ciclo inyectando flujo de trafico
        bottleneck = math.inf
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            bottleneck = min(bottleneck, cap[u][v])

        if bottleneck == 0 or bottleneck == math.inf:
            break

        # Calcular ahorro en costo
        cycle_cost = sum(
            cost[cycle[i]][cycle[(i + 1) % len(cycle)]]
            for i in range(len(cycle))
        )
        savings += -cycle_cost * bottleneck   # cycle_cost < 0 → ahorro > 0

        # Actualizar red residual
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            cap[u][v] -= bottleneck
            cap[v][u] += bottleneck

    return savings, iterations


# ═══════════════════════════════════════════════════════════
# 4. CÁLCULO DEL FLUJO TOTAL Y COSTO TRAS CYCLE CANCELING
# ═══════════════════════════════════════════════════════════
def calcular_flujo_y_costo(cap_original, cap_residual, cost, adj, edges):
    """
    Reconstruye el flujo real en cada arco y calcula el costo total.
    flujo[u][v] = cap_original[u][v] - cap_residual[u][v]
    """
    flow_on_arc  = {}
    total_cost   = 0
    arcos_usados = []

    for (u, v, c, capacity) in edges:
        f = capacity - cap_residual[u][v]
        if f < 0:
            f = 0
        flow_on_arc[(u, v)] = f
        if f > 0:
            arcos_usados.append((u, v, f, c, f * c))
            total_cost += f * c

    return total_cost, arcos_usados, flow_on_arc


# ═══════════════════════════════════════════════════════════
# 5. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")

    ORIGENES = [1, 2]
    DESTINOS = [80]
    SUPPLY      = 500   # Unidades a enviar desde la fuente
    MIN_SINK_PCT= 0.20  # Al menos 20 % debe llegar al nodo 80
    min_requerido = int(SUPPLY * MIN_SINK_PCT)

    print("=" * 65)
    print("   FLUJO AL COSTO MÍNIMO — CYCLE CANCELING (Klein)")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            cap_original = defaultdict(lambda: defaultdict(int))
            for (u, v, c, capacity) in edges:
                cap_original[u][v] += capacity

            cap, cost, adj = construir_red_residual(edges)

            flujo_enviado, costo_inicial, rutas_fase1 = enviar_flujo(
                cap, cost, adj, SOURCE, SINK, min_requerido
            )

            if flujo_enviado < min_requerido:
                resultados[(SOURCE, SINK)] = float('inf')
                continue

            ahorro, n_ciclos = cycle_canceling(cap, cost, adj, nodos)
            
            costo_final = costo_inicial - ahorro
            resultados[(SOURCE, SINK)] = costo_final

    print(f"\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Costo Minimo':>15}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*15}")

    for (src, dst), c_min in resultados.items():
        if c_min != float('inf'):
            print(f"  {src:>6}  {dst:>7}  {c_min:>15.1f}")
        else:
            print(f"  {src:>6}  {dst:>7}  {'Infactible':>15}")

    validos = {k: v for k,v in resultados.items() if v != float('inf')}
    if not validos:
        print("Ninguna ruta factible.")
        return
        
    mejor = min(validos.items(), key=lambda x: x[1])
    (s_min, t_min), c_min_global = mejor

    print(f"\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_min}")
    print(f"  Mejor Destino    : {t_min}")
    print(f"  COSTO MÍNIMO     : {c_min_global:.1f}")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
