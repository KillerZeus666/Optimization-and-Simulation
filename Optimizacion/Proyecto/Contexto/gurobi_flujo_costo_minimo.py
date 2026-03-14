"""
Flujo al Costo Minimo — Gurobi
================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Fuente   : nodo 1
Sumidero : nodo 80
Supply   : 500 unidades (se envia lo que la red permita)
Restriccion: al menos el 20% del supply debe llegar al nodo 80
             => minimo 100 unidades al destino

Formulacion LP:
  Minimizar   sum( costo_ij * f_ij )
  Sujeto a:
    [1] Conservacion de flujo en nodos intermedios
    [2] Fuente   : flujo neto saliente <= SUPPLY
    [3] Sumidero : flujo neto entrante >= MIN_SINK (20% de SUPPLY)
    [4] 0 <= f_ij <= capacidad_ij
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
            u, v   = int(row["Origen"]), int(row["Destino"])
            costo  = int(row["Costo"])
            cap    = int(row["Capacidad"])
            edges.append((u, v, costo, cap))
            nodos.update([u, v])
    return edges, sorted(nodos)

# ═══════════════════════════════════════════════════════════
# 2. MODELO GUROBI
# ═══════════════════════════════════════════════════════════
def resolver(edges, nodos, source, sink, supply, min_sink):
    m = gp.Model("Flujo_Costo_Minimo")
    m.setParam("OutputFlag", 0)

    f = {(u, v): m.addVar(lb=0, ub=cap, name=f"f_{u}_{v}")
         for (u, v, costo, cap) in edges}

    # Objetivo: minimizar costo total
    m.setObjective(
        gp.quicksum(costo * f[(u, v)] for (u, v, costo, cap) in edges),
        GRB.MINIMIZE
    )

    salida  = defaultdict(list)
    entrada = defaultdict(list)
    for (u, v, _, __) in edges:
        salida[u].append((u, v))
        entrada[v].append((u, v))

    for n in nodos:
        sale  = gp.quicksum(f[arc] for arc in salida[n])
        entra = gp.quicksum(f[arc] for arc in entrada[n])
        if n == source:
            m.addConstr(sale - entra <= supply,  "supply_max")
            m.addConstr(sale - entra >= 0,       "supply_pos")
        elif n == sink:
            m.addConstr(entra - sale >= min_sink, "demanda_min")
        else:
            m.addConstr(sale - entra == 0,        f"balance_{n}")

    m.optimize()
    return m, f

# ═══════════════════════════════════════════════════════════
# 3. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    SOURCE, SINK  = 1, 80
    SUPPLY        = 500
    MIN_SINK_PCT  = 0.20
    MIN_SINK      = int(SUPPLY * MIN_SINK_PCT)   # 100

    print("=" * 65)
    print("   FLUJO AL COSTO MINIMO — GUROBI")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontro: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n Archivo leido correctamente.")
    print(f"  Nodos : {len(nodos)}  |  Arcos : {len(edges)}")
    print(f"  Fuente        : nodo {SOURCE}")
    print(f"  Sumidero      : nodo {SINK}")
    print(f"  Supply maximo : {SUPPLY} unidades")
    print(f"  Minimo al nodo {SINK}: {MIN_SINK} unidades ({MIN_SINK_PCT*100:.0f}%)")

    m, f = resolver(edges, nodos, SOURCE, SINK, SUPPLY, MIN_SINK)

    estados = {2: "Optimo", 3: "Infactible", 5: "No acotado"}
    estado  = estados.get(m.Status, f"Codigo {m.Status}")
    print(f"\n  Estado del solver : {estado}")

    if m.Status != GRB.OPTIMAL:
        print("  El problema no tiene solucion optima."); return

    costo_total = m.ObjVal

    salida_f  = defaultdict(list)
    entrada_f = defaultdict(list)
    for (u, v, _, __) in edges:
        salida_f[u].append((u, v))
        entrada_f[v].append((u, v))

    flujo_enviado = sum(f[(u,v)].X for (u,v) in salida_f[SOURCE])
    flujo_sink    = sum(f[(u,v)].X for (u,v) in entrada_f[SINK])

    arcos_activos = []
    for (u, v, costo, cap) in edges:
        fv = f[(u,v)].X
        if fv > 1e-6:
            arcos_activos.append((u, v, fv, costo, fv * costo))
    arcos_activos.sort(key=lambda x: -x[4])

    print(f"\n{'='*65}")
    print(f"  RESULTADOS FINALES")
    print(f"{'='*65}")
    print(f"\n  Flujo enviado desde nodo {SOURCE} : {flujo_enviado:.1f} unidades")
    print(f"  Flujo que llega al nodo  {SINK}  : {flujo_sink:.1f} unidades")
    print(f"  Minimo requerido (20%)          : {MIN_SINK} unidades")
    ok = flujo_sink >= MIN_SINK - 1e-6
    print(f"  Restriccion cumplida            : {'SI' if ok else 'NO'}")
    print(f"\n  ┌─────────────────────────────────────────────")
    print(f"  │  COSTO MINIMO TOTAL  =  {costo_total:>10,.1f}")
    print(f"  └─────────────────────────────────────────────")

    print(f"\n  Arcos con flujo positivo : {len(arcos_activos)}")
    print(f"\n  {'Arco':<12} {'Flujo':>7} {'Costo Unit':>10} {'Costo Total':>12}")
    print(f"  {'─'*12} {'─'*7} {'─'*10} {'─'*12}")
    for (u, v, fv, c, fc) in arcos_activos[:30]:
        print(f"  {u:>4} -> {v:<4}  {fv:>7.1f}    {c:>6}        {fc:>10,.1f}")
    if len(arcos_activos) > 30:
        print(f"  ... y {len(arcos_activos)-30} arcos mas con flujo positivo.")

    print(f"\n{'='*65}")
    print(f"  RESUMEN EJECUTIVO")
    print(f"{'='*65}")
    print(f"  Flujo enviado : {flujo_enviado:.0f} unidades")
    print(f"  Flujo al nodo {SINK} : {flujo_sink:.0f} "
          f"({flujo_sink/SUPPLY*100:.1f}% del supply, requerido >= 20%)")
    print(f"  Costo minimo  : {costo_total:,.1f}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
