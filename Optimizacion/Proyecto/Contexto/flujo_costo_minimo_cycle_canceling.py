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
# 2. FASE 1 — FLUJO FACTIBLE CON BFS (Ford-Fulkerson)
#    Enviamos exactamente `supply` unidades de 1 → 80.
#    Si la red no tiene capacidad suficiente se avisa.
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
# 3. FASE 2 — CYCLE CANCELING (Klein)
#    Detecta ciclos de costo negativo en la red residual
#    y envía flujo por ellos hasta que no queden más.
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
    Mejora el flujo actual cancelando todos los ciclos de costo negativo.
    Devuelve el ahorro total de costo logrado.
    """
    savings    = 0
    iterations = 0

    while True:
        cycle = bellman_ford_negative_cycle(cap, cost, adj, nodes)
        if cycle is None:
            break
        iterations += 1

        # Cuello de botella en el ciclo
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

    SUPPLY      = 500   # Unidades a enviar desde la fuente
    MIN_SINK_PCT= 0.20  # Al menos 20 % debe llegar al nodo 80
    SOURCE      = 1
    SINK        = 80

    print("=" * 65)
    print("   FLUJO AL COSTO MÍNIMO — CYCLE CANCELING (Klein)")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"\n[ERROR] No se encontró: {ruta_csv}")
        return

    # ── Leer datos ──
    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n✔ Archivo leído correctamente.")
    print(f"  • Nodos totales : {len(nodos)}")
    print(f"  • Arcos totales : {len(edges)}")
    print(f"  • Fuente        : nodo {SOURCE}")
    print(f"  • Sumidero      : nodo {SINK}")
    print(f"  • Supply total  : {SUPPLY} unidades")
    print(f"  • Mínimo a nodo {SINK}: {int(SUPPLY * MIN_SINK_PCT)} unidades "
          f"({MIN_SINK_PCT*100:.0f}%)")

    # ── Construir red residual ──
    cap_original = defaultdict(lambda: defaultdict(int))
    for (u, v, c, capacity) in edges:
        cap_original[u][v] += capacity

    cap, cost, adj = construir_red_residual(edges)

    # ── FASE 1: Flujo factible ──
    print("\n" + "─" * 65)
    print("  FASE 1 — Flujo factible (BFS / Ford-Fulkerson)")
    print("─" * 65)

    flujo_enviado, costo_inicial, rutas_fase1 = enviar_flujo(
        cap, cost, adj, SOURCE, SINK, SUPPLY
    )

    min_requerido = int(SUPPLY * MIN_SINK_PCT)

    print(f"\n  Flujo enviado al nodo {SINK}: {flujo_enviado} unidades")
    print(f"  Mínimo requerido           : {min_requerido} unidades")

    if flujo_enviado < min_requerido:
        print(f"\n  ⚠  ADVERTENCIA: Solo se pudieron enviar {flujo_enviado} "
              f"unidades al nodo {SINK}.")
        print(f"     Esto es {'SUFICIENTE' if flujo_enviado >= min_requerido else 'INSUFICIENTE'} "
              f"para el 20 % requerido.")
    else:
        print(f"\n  ✔ Se satisface la restricción del 20 % "
              f"({flujo_enviado} ≥ {min_requerido} unidades).")

    print(f"\n  Costo inicial (antes de optimizar): {costo_inicial:,}")
    print(f"\n  Caminos aumentantes encontrados: {len(rutas_fase1)}")
    for i, (path, f, pc) in enumerate(rutas_fase1, 1):
        ruta_str = " → ".join(str(n) for n in path)
        print(f"    [{i:>2}] Flujo={f:>3}  Costo={pc:>6,}  |  {ruta_str}")

    # ── FASE 2: Cycle Canceling ──
    print("\n" + "─" * 65)
    print("  FASE 2 — Cycle Canceling (eliminación de ciclos negativos)")
    print("─" * 65)

    ahorro, n_ciclos = cycle_canceling(cap, cost, adj, nodos)

    print(f"\n  Ciclos negativos cancelados: {n_ciclos}")
    print(f"  Ahorro total de costo      : {ahorro:,}")

    # ── Reconstruir flujo final ──
    costo_final, arcos_usados, flow_on_arc = calcular_flujo_y_costo(
        cap_original, cap, cost, adj, edges
    )

    # Verificar flujo que llega al sumidero
    flujo_al_sink = sum(f for (u, v, f, c, fc) in arcos_usados if v == SINK)

    # ── Resultados Finales ──
    print("\n" + "=" * 65)
    print("  RESULTADOS FINALES")
    print("=" * 65)
    print(f"\n  Flujo total enviado     : {flujo_enviado} unidades")
    print(f"  Flujo que llega al nodo {SINK}: {flujo_enviado} unidades")
    print(f"  Mínimo requerido (20 %) : {min_requerido} unidades")
    restriccion_ok = flujo_enviado >= min_requerido
    print(f"  Restricción cumplida    : {'✔ SÍ' if restriccion_ok else '✗ NO'}")
    print(f"\n  Costo antes de optimizar: {costo_inicial:>10,}")
    print(f"  Ahorro por Cycle Cancel.: {ahorro:>10,}")
    print(f"  ┌─────────────────────────────────────────────")
    print(f"  │  COSTO MÍNIMO TOTAL  =  {costo_inicial - ahorro:>10,}")
    print(f"  └─────────────────────────────────────────────")

    print(f"\n  Arcos con flujo positivo: {len(arcos_usados)}")
    print(f"\n  {'Arco':<12} {'Flujo':>6} {'Costo Unit':>10} {'Costo Total':>12}")
    print(f"  {'─'*12} {'─'*6} {'─'*10} {'─'*12}")
    for (u, v, f, c, fc) in sorted(arcos_usados, key=lambda x: -x[4])[:30]:
        print(f"  {u:>4} → {v:<4}   {f:>6}     {c:>6}        {fc:>8,}")
    if len(arcos_usados) > 30:
        print(f"  ... y {len(arcos_usados) - 30} arcos más con flujo positivo.")

    print("\n" + "=" * 65)
    print(f"  RESUMEN EJECUTIVO")
    print("=" * 65)
    print(f"  • Se enviaron {flujo_enviado} de {SUPPLY} unidades solicitadas.")
    print(f"  • El {flujo_enviado/SUPPLY*100:.1f}% del supply llega al destino "
          f"(requerido ≥ 20%).")
    print(f"  • Ciclos negativos eliminados: {n_ciclos}  →  ahorro: {ahorro:,}")
    print(f"  • Costo mínimo final: {costo_inicial - ahorro:,}")
    print("=" * 65)


if __name__ == "__main__":
    main()
