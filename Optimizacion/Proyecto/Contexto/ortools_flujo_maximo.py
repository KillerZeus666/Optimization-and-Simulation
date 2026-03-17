# -*- coding: utf-8 -*-
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
    from ortools.graph.python import max_flow

    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    
    ORIGENES = [1, 2]
    DESTINOS = [78, 79, 80]

    print("=" * 65)
    print("   FLUJO MAXIMO — OR-TOOLS")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            smf = max_flow.SimpleMaxFlow()
            for (u, v, cap) in edges:
                smf.add_arc_with_capacity(u, v, cap)
            status = smf.solve(SOURCE, SINK)
            if status == smf.OPTIMAL:
                flujo = smf.optimal_flow()
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
