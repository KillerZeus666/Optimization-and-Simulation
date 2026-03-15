"""
Flujo Maximo — OR-Tools (SimpleMaxFlow)
========================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Fuente   : nodo 1
Sumidero : nodo 80

OR-Tools tiene un modulo nativo para flujo maximo:
  - SimpleMaxFlow resuelve internamente con el algoritmo de
    push-relabel, uno de los mas eficientes conocidos.
  - Solo se definen arcos y capacidades, sin formular LP.
"""

import csv, os
from ortools.graph.python import max_flow

# ═══════════════════════════════════════════════════════════
# 1. LECTURA DEL CSV
# ═══════════════════════════════════════════════════════════
def leer_grafo(ruta_csv):
    edges = []          # (u, v, capacidad)
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
# 2. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    SOURCE, SINK = 1, 80

    print("=" * 65)
    print("   FLUJO MAXIMO — OR-Tools (SimpleMaxFlow)")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontro: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n Archivo leido correctamente.")
    print(f"  Nodos : {len(nodos)}  |  Arcos : {len(edges)}")
    print(f"  Fuente   : nodo {SOURCE}")
    print(f"  Sumidero : nodo {SINK}")

    # ── Construir el modelo OR-Tools ──
    smf = max_flow.SimpleMaxFlow()

    arc_ids = []
    for (u, v, cap) in edges:
        arc_id = smf.add_arc_with_capacity(u, v, cap)
        arc_ids.append((arc_id, u, v, cap))

    # ── Resolver ──
    status = smf.solve(SOURCE, SINK)

    estados = {
        smf.OPTIMAL        : "Optimo",
        smf.POSSIBLE_OVERFLOW: "Posible desbordamiento",
        smf.BAD_INPUT : "Entrada invalida",
        smf.BAD_RESULT     : "Resultado invalido",
    }
    estado = estados.get(status, f"Codigo {status}")
    print(f"\n  Estado del solver : {estado}")

    if status != smf.OPTIMAL:
        print("  No se encontro solucion optima."); return

    flujo_max = smf.optimal_flow()

    print(f"\n{'='*65}")
    print(f"  FLUJO MAXIMO = {flujo_max}")
    print(f"{'='*65}")

    # Arcos con flujo positivo
    arcos_activos = []
    for (arc_id, u, v, cap) in arc_ids:
        f = smf.flow(arc_id)
        if f > 0:
            arcos_activos.append((u, v, f, cap))
    arcos_activos.sort(key=lambda x: -x[2])

    print(f"\n  Arcos con flujo positivo: {len(arcos_activos)}")
    print(f"\n  {'Arco':<12} {'Flujo':>7} {'Capacidad':>10} {'Uso %':>7}")
    print(f"  {'─'*12} {'─'*7} {'─'*10} {'─'*7}")
    for (u, v, f, cap) in arcos_activos:
        uso = f / cap * 100
        print(f"  {u:>4} -> {v:<4}  {f:>7}    {cap:>7}     {uso:>5.1f}%")

    print(f"\n{'='*65}")
    print(f"  RESULTADO FINAL: Flujo maximo del nodo {SOURCE} al {SINK}")
    print(f"  = {flujo_max} unidades")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
