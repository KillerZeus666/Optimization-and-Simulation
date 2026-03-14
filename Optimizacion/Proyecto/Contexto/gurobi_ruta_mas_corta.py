"""
Ruta Mas Corta — Gurobi (ILP Binario)
=======================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Origenes : nodo 1, nodo 2
Destinos : nodo 78, nodo 79, nodo 80
Metrica  : Distancia

Formulacion ILP:
  Variables: x_ij in {0,1}  (1 si el arco i->j pertenece a la ruta)

  Minimizar   sum( distancia_ij * x_ij )

  Sujeto a:
    [1] Fuente      : sum(x_sj) - sum(x_is) =  1
    [2] Sumidero    : sum(x_it) - sum(x_tj) =  1
    [3] Intermedios : sum(x_uj) - sum(x_iu) =  0
    [4] x_ij in {0,1}
"""

import csv, os
from collections import defaultdict
import gurobipy as gp
from gurobipy import GRB

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
# 2. MODELO GUROBI — un par (source, sink)
# ═══════════════════════════════════════════════════════════
def resolver_ruta(edges, nodos, source, sink):
    m = gp.Model(f"Ruta_{source}_a_{sink}")
    m.setParam("OutputFlag", 0)

    # Variables binarias
    x = {(u, v): m.addVar(vtype=GRB.BINARY, name=f"x_{u}_{v}")
         for (u, v, _) in edges}

    # Objetivo: minimizar distancia total
    m.setObjective(
        gp.quicksum(dist * x[(u, v)] for (u, v, dist) in edges),
        GRB.MINIMIZE
    )

    salida  = defaultdict(list)
    entrada = defaultdict(list)
    for (u, v, _) in edges:
        salida[u].append((u, v))
        entrada[v].append((u, v))

    for n in nodos:
        sale  = gp.quicksum(x[arc] for arc in salida[n])
        entra = gp.quicksum(x[arc] for arc in entrada[n])
        if n == source:
            m.addConstr(sale - entra == 1,  "fuente")
        elif n == sink:
            m.addConstr(entra - sale == 1,  "sumidero")
        else:
            m.addConstr(sale - entra == 0,  f"balance_{n}")

    m.optimize()

    if m.Status != GRB.OPTIMAL:
        return None, None

    dist_total = int(round(m.ObjVal))

    # Reconstruir camino
    siguiente = {u: v for (u, v, _) in edges if x[(u,v)].X > 0.5}
    camino = [source]
    nodo   = source
    for _ in range(len(nodos)):
        nodo = siguiente.get(nodo)
        if nodo is None or nodo == sink:
            if nodo == sink:
                camino.append(sink)
            break
        camino.append(nodo)

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
    print("   RUTA MAS CORTA — GUROBI (ILP Binario)")
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
