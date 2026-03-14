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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    SOURCE, SINK = 1, 80

    print("=" * 65)
    print("   FLUJO MAXIMO — GUROBI")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontro: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n Archivo leido correctamente.")
    print(f"  Nodos : {len(nodos)}  |  Arcos : {len(edges)}")
    print(f"  Fuente : nodo {SOURCE}  |  Sumidero : nodo {SINK}")

    m, f, F = resolver(edges, nodos, SOURCE, SINK)

    estados = {2: "Optimo", 3: "Infactible", 5: "No acotado"}
    estado  = estados.get(m.Status, f"Codigo {m.Status}")
    print(f"\n  Estado del solver : {estado}")

    if m.Status != GRB.OPTIMAL:
        print("  El problema no tiene solucion optima."); return

    flujo_max = int(round(F.X))

    print(f"\n{'='*65}")
    print(f"  FLUJO MAXIMO = {flujo_max}")
    print(f"{'='*65}")

    arcos_activos = [(u, v, f[(u,v)].X)
                     for (u, v, _) in edges if f[(u,v)].X > 1e-6]
    arcos_activos.sort(key=lambda x: -x[2])

    print(f"\n  Arcos con flujo positivo: {len(arcos_activos)}")
    print(f"\n  {'Arco':<12} {'Flujo':>8}")
    print(f"  {'─'*12} {'─'*8}")
    for (u, v, fv) in arcos_activos:
        print(f"  {u:>4} -> {v:<4}   {fv:>8.1f}")

    print(f"\n{'='*65}")
    print(f"  RESULTADO FINAL: Flujo maximo del nodo {SOURCE} al {SINK} = {flujo_max} unidades")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
