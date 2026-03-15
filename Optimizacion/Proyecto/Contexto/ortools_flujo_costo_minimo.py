"""
Flujo al Costo Minimo — OR-Tools (SimpleMinCostFlow)
=====================================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Fuente   : nodo 1
Sumidero : nodo 80
Supply   : 500 unidades
Restriccion: al menos el 20% (100 unidades) deben llegar al nodo 80

OR-Tools tiene un modulo nativo para flujo de costo minimo:
  - SimpleMinCostFlow resuelve con el algoritmo de successive
    shortest paths, optimo para redes de flujo.
  - Se definen arcos, capacidades, costos y balances de nodos.

Estrategia para el minimo 20%:
  Se resuelve primero enviando exactamente MIN_SINK unidades
  (100) al destino con costo minimo. Esto garantiza la
  restriccion del 20% al menor costo posible.
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
            u, v   = int(row["Origen"]), int(row["Destino"])
            costo  = int(row["Costo"])
            cap    = int(row["Capacidad"])
            edges.append((u, v, costo, cap))
            nodos.update([u, v])
    return edges, sorted(nodos)

# ═══════════════════════════════════════════════════════════
# 2. RESOLVER CON SimpleMinCostFlow
# ═══════════════════════════════════════════════════════════
def resolver(edges, nodos, source, sink, supply):
    smcf = min_cost_flow.SimpleMinCostFlow()

    arc_ids = []
    for (u, v, costo, cap) in edges:
        arc_id = smcf.add_arc_with_capacity_and_unit_cost(u, v, cap, costo)
        arc_ids.append((arc_id, u, v, costo, cap))

    # Balances: fuente produce `supply`, sumidero consume `supply`
    for n in nodos:
        if n == source:
            smcf.set_node_supply(n,  supply)
        elif n == sink:
            smcf.set_node_supply(n, -supply)
        else:
            smcf.set_node_supply(n,  0)

    status = smcf.solve()
    return smcf, arc_ids, status

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
    print("   FLUJO AL COSTO MINIMO — OR-Tools (SimpleMinCostFlow)")
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

    # ── Resolver enviando exactamente MIN_SINK al destino ──
    print(f"\n  Resolviendo con supply = {MIN_SINK} unidades (minimo requerido)...")
    smcf, arc_ids, status = resolver(edges, nodos, SOURCE, SINK, MIN_SINK)

    estados = {
        smcf.OPTIMAL          : "Optimo",
        smcf.INFEASIBLE       : "Infactible",
        smcf.UNBALANCED       : "No balanceado",
        smcf.BAD_COST_RANGE   : "Rango de costo invalido",
        smcf.BAD_RESULT       : "Resultado invalido",
        smcf.NOT_SOLVED       : "No resuelto",
    }
    estado = estados.get(status, f"Codigo {status}")
    print(f"  Estado del solver : {estado}")

    if status != smcf.OPTIMAL:
        print("  No se encontro solucion optima."); return

    costo_total   = smcf.optimal_cost()
    flujo_enviado = MIN_SINK

    # Arcos con flujo positivo
    arcos_activos = []
    for (arc_id, u, v, costo, cap) in arc_ids:
        f = smcf.flow(arc_id)
        if f > 0:
            arcos_activos.append((u, v, f, costo, f * costo))
    arcos_activos.sort(key=lambda x: -x[4])

    print(f"\n{'='*65}")
    print(f"  RESULTADOS FINALES")
    print(f"{'='*65}")
    print(f"\n  Flujo enviado desde nodo {SOURCE} : {flujo_enviado} unidades")
    print(f"  Flujo que llega al nodo  {SINK}  : {flujo_enviado} unidades")
    print(f"  Minimo requerido (20%)          : {MIN_SINK} unidades")
    print(f"  Restriccion cumplida            : SI ({flujo_enviado/SUPPLY*100:.1f}% >= 20%)")
    print(f"\n  ┌─────────────────────────────────────────────")
    print(f"  │  COSTO MINIMO TOTAL  =  {costo_total:>10,}")
    print(f"  └─────────────────────────────────────────────")

    print(f"\n  Arcos con flujo positivo : {len(arcos_activos)}")
    print(f"\n  {'Arco':<12} {'Flujo':>7} {'Costo Unit':>10} {'Costo Total':>12}")
    print(f"  {'─'*12} {'─'*7} {'─'*10} {'─'*12}")
    for (u, v, f, c, fc) in arcos_activos[:30]:
        print(f"  {u:>4} -> {v:<4}  {f:>7}    {c:>6}        {fc:>10,}")
    if len(arcos_activos) > 30:
        print(f"  ... y {len(arcos_activos)-30} arcos mas con flujo positivo.")

    print(f"\n{'='*65}")
    print(f"  RESUMEN EJECUTIVO")
    print(f"{'='*65}")
    print(f"  Supply solicitado : {SUPPLY} unidades")
    print(f"  Flujo enviado     : {flujo_enviado} unidades")
    print(f"  Flujo al nodo {SINK} : {flujo_enviado} ({flujo_enviado/SUPPLY*100:.1f}% del supply)")
    print(f"  Costo minimo      : {costo_total:,}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
