"""
Flujo al Costo Mínimo — PuLP / CBC Solver
==========================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Fuente   : nodo 1
Sumidero : nodo 80
Supply   : 500 unidades (se envía lo que la red permita, máx 500)
Restricción: al menos el 20% del flujo enviado debe llegar al nodo 80
             => mínimo 100 unidades al destino

Formulación LP:
  Minimizar   sum( costo_ij * f_ij )   para todo arco (i,j)
  Sujeto a:
    [1] Conservación de flujo neto en cada nodo
    [2] El flujo que sale de la fuente <= SUPPLY
    [3] El flujo que llega al sumidero >= MIN_SINK  (20% de SUPPLY)
    [4] 0 <= f_ij <= capacidad_ij
"""

import csv, os
from collections import defaultdict
import pulp

# ═══════════════════════════════════════════════════════════
# 1. LECTURA DEL CSV
# ═══════════════════════════════════════════════════════════
def leer_grafo(ruta_csv):
    edges = []          # (u, v, costo, capacidad)
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
# 2. MODELO PuLP
# ═══════════════════════════════════════════════════════════
def resolver_costo_minimo(edges, nodos, source, sink, supply, min_sink):

    prob = pulp.LpProblem("Flujo_Costo_Minimo", pulp.LpMinimize)

    # Variables de flujo
    f = {(u, v): pulp.LpVariable(f"f_{u}_{v}", lowBound=0, upBound=cap)
         for (u, v, costo, cap) in edges}

    # Función objetivo: minimizar costo total
    prob += pulp.lpSum(costo * f[(u, v)]
                       for (u, v, costo, cap) in edges), "Costo_total"

    # Índices de salida/entrada por nodo
    salida  = defaultdict(list)
    entrada = defaultdict(list)
    for (u, v, _, __) in edges:
        salida[u].append((u, v))
        entrada[v].append((u, v))

    # Variable de flujo neto en cada nodo
    for n in nodos:
        flujo_sale  = pulp.lpSum(f[arc] for arc in salida[n])
        flujo_entra = pulp.lpSum(f[arc] for arc in entrada[n])
        if n == source:
            # Fuente: puede enviar hasta SUPPLY
            prob += flujo_sale - flujo_entra <= supply,  f"supply_{n}"
            prob += flujo_sale - flujo_entra >= 0,       f"supply_pos_{n}"
        elif n == sink:
            # Sumidero: debe recibir al menos MIN_SINK
            prob += flujo_entra - flujo_sale >= min_sink, f"demand_{n}"
        else:
            # Nodos intermedios: flujo entrante = flujo saliente
            prob += flujo_sale - flujo_entra == 0,        f"balance_{n}"

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    return prob, f

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
    print("   FLUJO AL COSTO MÍNIMO — PuLP / CBC Solver")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontró: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n✔ Archivo leído correctamente.")
    print(f"  • Nodos : {len(nodos)}  |  Arcos : {len(edges)}")
    print(f"  • Fuente        : nodo {SOURCE}")
    print(f"  • Sumidero      : nodo {SINK}")
    print(f"  • Supply máximo : {SUPPLY} unidades")
    print(f"  • Mínimo al nodo {SINK}: {MIN_SINK} unidades ({MIN_SINK_PCT*100:.0f}%)")

    prob, f = resolver_costo_minimo(edges, nodos, SOURCE, SINK, SUPPLY, MIN_SINK)

    estado = pulp.LpStatus[prob.status]
    print(f"\n  Estado del solver : {estado}")

    if prob.status != 1:
        print("  El problema no tiene solución óptima."); return

    costo_total = pulp.value(prob.objective)

    # Flujo que sale de la fuente y llega al sumidero
    salida_fuente  = defaultdict(list)
    entrada_nodo   = defaultdict(list)
    for (u, v, _, __) in edges:
        salida_fuente[u].append((u, v))
        entrada_nodo[v].append((u, v))

    flujo_enviado = sum(pulp.value(f[(u,v)]) or 0
                        for (u, v) in salida_fuente[SOURCE])
    flujo_sink    = sum(pulp.value(f[(u,v)]) or 0
                        for (u, v) in entrada_nodo[SINK])

    # Arcos activos
    arcos_activos = []
    for (u, v, costo, cap) in edges:
        fv = pulp.value(f[(u, v)]) or 0
        if fv > 1e-6:
            arcos_activos.append((u, v, fv, costo, fv * costo))
    arcos_activos.sort(key=lambda x: -x[4])

    print(f"\n{'='*65}")
    print(f"  RESULTADOS FINALES")
    print(f"{'='*65}")
    print(f"\n  Flujo enviado desde nodo {SOURCE} : {flujo_enviado:.1f} unidades")
    print(f"  Flujo que llega al nodo  {SINK}  : {flujo_sink:.1f} unidades")
    print(f"  Mínimo requerido (20%)          : {MIN_SINK} unidades")
    ok = flujo_sink >= MIN_SINK - 1e-6
    print(f"  Restricción cumplida            : {'✔ SÍ' if ok else '✗ NO'}")
    print(f"\n  ┌─────────────────────────────────────────────")
    print(f"  │  COSTO MÍNIMO TOTAL  =  {costo_total:>10,.1f}")
    print(f"  └─────────────────────────────────────────────")

    print(f"\n  Arcos con flujo positivo : {len(arcos_activos)}")
    print(f"\n  {'Arco':<12} {'Flujo':>7} {'Costo Unit':>10} {'Costo Total':>12}")
    print(f"  {'─'*12} {'─'*7} {'─'*10} {'─'*12}")
    for (u, v, fv, c, fc) in arcos_activos[:30]:
        print(f"  {u:>4} → {v:<4}  {fv:>7.1f}    {c:>6}        {fc:>10,.1f}")
    if len(arcos_activos) > 30:
        print(f"  ... y {len(arcos_activos)-30} arcos más con flujo positivo.")

    print(f"\n{'='*65}")
    print(f"  RESUMEN EJECUTIVO")
    print(f"{'='*65}")
    print(f"  • Flujo enviado : {flujo_enviado:.0f} unidades")
    print(f"  • Flujo al nodo {SINK} : {flujo_sink:.0f} "
          f"({flujo_sink/SUPPLY*100:.1f}% del supply, requerido ≥ 20%)")
    print(f"  • Costo mínimo  : {costo_total:,.1f}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
