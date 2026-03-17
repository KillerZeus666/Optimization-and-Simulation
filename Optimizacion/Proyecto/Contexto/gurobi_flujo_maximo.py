# -*- coding: utf-8 -*-
"""
Flujo Máximo — Gurobi
======================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Fuente   : nodo 1
Sumidero : nodo 80

Formulación LP:
  Maximizar   F  (flujo neto que sale de la fuente)
  Sujeto a:
    [1] Conservación de flujo en nodos intermedios
    [2] Balance en fuente  : sum(f_1j) - sum(f_i1) = F
    [3] Balance en sumidero: sum(f_i80) - sum(f_80j) = F
    [4] Capacidad          : 0 <= f_ij <= cap_ij
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
            cap  = int(row["Capacidad"])
            edges.append((u, v, cap))
            nodos.update([u, v])
    return edges, sorted(nodos)

# ═══════════════════════════════════════════════════════════
# 2. MODELO GUROBI
# ═══════════════════════════════════════════════════════════
def resolver(edges, nodos, source, sink):
    m = gp.Model("Flujo_Maximo")
    m.setParam("OutputFlag", 0)

    f = {(u, v): m.addVar(lb=0, ub=cap, name=f"f_{u}_{v}")
         for (u, v, cap) in edges}
    F = m.addVar(lb=0, name="F")

    m.setObjective(F, GRB.MAXIMIZE)

    salida  = defaultdict(list)
    entrada = defaultdict(list)
    for (u, v, _) in edges:
        salida[u].append((u, v))
        entrada[v].append((u, v))

    for n in nodos:
        sale  = gp.quicksum(f[arc] for arc in salida[n])
        entra = gp.quicksum(f[arc] for arc in entrada[n])
        if n == source:
            m.addConstr(sale - entra == F,  "balance_fuente")
        elif n == sink:
            m.addConstr(entra - sale == F,  "balance_sumidero")
        else:
            m.addConstr(sale - entra == 0,  f"balance_{n}")

    m.optimize()
    return m, f, F

# ═══════════════════════════════════════════════════════════
# 3. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    
    ORIGENES = [1, 2]
    DESTINOS = [78, 79, 80]

    print("=" * 65)
    print("   FLUJO MAXIMO — GUROBI")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            m, f, F = resolver(edges, nodos, SOURCE, SINK)
            if m.Status == 2:
                flujo = int(round(F.X))
            else:
                flujo = 0
            resultados[(SOURCE, SINK)] = flujo

    print(f"\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Flujo Max':>10}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*10}")
    
    for (src, dst), f_max in resultados.items():
        print(f"  {src:>6}  {dst:>7}  {f_max:>10}")

    mejor = max(resultados.items(), key=lambda x: x[1])
    (s_max, t_max), f_max_global = mejor

    print(f"\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_max}")
    print(f"  Mejor Destino    : {t_max}")
    print(f"  FLUJO MAXIMO     : {f_max_global} unidades")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
