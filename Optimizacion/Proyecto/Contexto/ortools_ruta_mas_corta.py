# -*- coding: utf-8 -*-
"""
Ruta Mas Corta — OR-Tools (SimpleShortestPathsAll / MinCostFlow)
================================================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Origenes : nodo 1, nodo 2
Destinos : nodo 78, nodo 79, nodo 80
Metrica  : Distancia

OR-Tools resuelve ruta mas corta como un problema de
flujo de costo minimo con supply=1 en el origen y
demand=1 en el destino, capacidad=1 en cada arco y
costo = distancia del arco. Esto es equivalente a
Dijkstra pero usando el motor de redes de OR-Tools.
"""

import csv, os
from ortools.graph.python import min_cost_flow

# ═══════════════════════════════════════════════════════════
# 1. LECTURA DEL CSV
# ═══════════════════════════════════════════════════════════
def leer_grafo(ruta_csv):
    edges = []
    nodos = set()
    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u, v = int(row["Origen"]), int(row["Destino"])
            dist = int(row["Distancia"])
            edges.append((u, v, dist))
            nodos.update([u, v])
    return edges, sorted(nodos)

# ═══════════════════════════════════════════════════════════
# 2. RESOLVER RUTA MAS CORTA ENTRE UN PAR (src, dst)
# ═══════════════════════════════════════════════════════════
def resolver_ruta(edges, nodos, source, sink):
    smcf = min_cost_flow.SimpleMinCostFlow()

    arc_ids = []
    for (u, v, dist) in edges:
        # capacidad = 1 (solo necesitamos una unidad de flujo)
        # costo = distancia
        arc_id = smcf.add_arc_with_capacity_and_unit_cost(u, v, 1, dist)
        arc_ids.append((arc_id, u, v, dist))

    # Supply: 1 unidad sale de source, 1 llega a sink
    for n in nodos:
        if n == source:
            smcf.set_node_supply(n,  1)
        elif n == sink:
            smcf.set_node_supply(n, -1)
        else:
            smcf.set_node_supply(n,  0)

    status = smcf.solve()

    if status != smcf.OPTIMAL:
        return None, None

    dist_total = smcf.optimal_cost()

    # Reconstruir camino siguiendo arcos con flujo = 1
    siguiente = {}
    for (arc_id, u, v, dist) in arc_ids:
        if smcf.flow(arc_id) == 1:
            siguiente[u] = v

    camino = [source]
    nodo   = source
    for _ in range(len(nodos)):
        nodo = siguiente.get(nodo)
        if nodo is None:
            break
        camino.append(nodo)
        if nodo == sink:
            break

    return dist_total, camino

# ═══════════════════════════════════════════════════════════
# 3. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    ORIGENES   = [1, 2]
    DESTINOS   = [78, 79, 80]

    print("=" * 65)
    print("   RUTA MAS CORTA — OR-Tools (SimpleMinCostFlow)")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontro: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n Archivo leido correctamente.")
    print(f"  Nodos : {len(nodos)}  |  Arcos : {len(edges)}")
    print(f"  Origenes : {ORIGENES}")
    print(f"  Destinos : {DESTINOS}")
    print(f"  Metrica  : Distancia")

    resultados = {}

    for src in ORIGENES:
        print(f"\n{'─'*65}")
        print(f"  ORIGEN: nodo {src}")
        print(f"{'─'*65}")

        for dst in DESTINOS:
            dist_total, camino = resolver_ruta(edges, nodos, src, dst)

            if camino is None:
                print(f"\n  -> Destino nodo {dst}: NO EXISTE CAMINO")
                resultados[(src, dst)] = (float("inf"), None)
            else:
                ruta_str = " -> ".join(str(n) for n in camino)
                saltos   = len(camino) - 1
                print(f"\n  -> Destino nodo {dst}:")
                print(f"     Distancia total : {dist_total}")
                print(f"     Numero de saltos: {saltos}")
                print(f"     Ruta            : {ruta_str}")
                resultados[(src, dst)] = (dist_total, camino)

    # ── Tabla comparativa ──
    print(f"\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Distancia':>10}  {'Saltos':>6}  Ruta")
    print(f"  {'─'*6}  {'─'*7}  {'─'*10}  {'─'*6}  {'─'*35}")
    for src in ORIGENES:
        for dst in DESTINOS:
            d, camino = resultados[(src, dst)]
            if camino is None:
                print(f"  {src:>6}  {dst:>7}  {'inf':>10}  {'─':>6}  Sin camino")
            else:
                ruta_str = " -> ".join(str(n) for n in camino)
                print(f"  {src:>6}  {dst:>7}  {d:>10}  {len(camino)-1:>6}  {ruta_str}")

    # ── Mejor ruta global ──
    mejor = min(
        ((d, s, t, c) for (s, t), (d, c) in resultados.items() if c),
        key=lambda x: x[0]
    )
    d_min, s_min, t_min, c_min = mejor
    print(f"\n{'='*65}")
    print(f"  RUTA MAS CORTA GLOBAL")
    print(f"{'='*65}")
    print(f"  Origen    : nodo {s_min}")
    print(f"  Destino   : nodo {t_min}")
    print(f"  Distancia : {d_min}")
    print(f"  Saltos    : {len(c_min)-1}")
    print(f"  Ruta      : {' -> '.join(str(n) for n in c_min)}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
