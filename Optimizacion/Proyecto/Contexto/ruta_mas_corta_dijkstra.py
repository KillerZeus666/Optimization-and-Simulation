"""
Ruta Más Corta — Algoritmo de Dijkstra
=======================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Orígenes : nodo 1, nodo 2
Destinos : nodo 78, nodo 79, nodo 80
Métrica  : Distancia (columna "Distancia" del CSV)
"""

import csv
import os
import heapq
from collections import defaultdict

# ═══════════════════════════════════════════════════════════
# 1. LECTURA DEL CSV
# ═══════════════════════════════════════════════════════════
def leer_grafo(ruta_csv: str):
    """
    Construye el grafo de distancias (dígrafo dirigido).
    Devuelve:
      graph[u] = [(distancia, v), ...]
      nodos    : conjunto de todos los nodos
    """
    graph = defaultdict(list)
    nodos = set()

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u    = int(row["Origen"])
            v    = int(row["Destino"])
            dist = int(row["Distancia"])
            graph[u].append((dist, v))
            nodos.add(u)
            nodos.add(v)

    return graph, nodos


# ═══════════════════════════════════════════════════════════
# 2. DIJKSTRA (desde un origen hacia todos los nodos)
# ═══════════════════════════════════════════════════════════
def dijkstra(graph, source, nodos):
    """
    Dijkstra con heap de mínimos.
    Devuelve:
      dist   : diccionario {nodo: distancia_mínima desde source}
      parent : diccionario {nodo: predecesor en el camino mínimo}
    """
    dist   = {n: float("inf") for n in nodos}
    parent = {n: None         for n in nodos}
    dist[source] = 0

    heap = [(0, source)]   # (distancia_acumulada, nodo)

    while heap:
        d_u, u = heapq.heappop(heap)

        if d_u > dist[u]:  # entrada obsoleta en el heap
            continue

        for (w, v) in graph[u]:
            nueva_dist = dist[u] + w
            if nueva_dist < dist[v]:
                dist[v]   = nueva_dist
                parent[v] = u
                heapq.heappush(heap, (nueva_dist, v))

    return dist, parent


# ═══════════════════════════════════════════════════════════
# 3. RECONSTRUIR CAMINO
# ═══════════════════════════════════════════════════════════
def reconstruir_camino(parent, source, target):
    """Recorre el diccionario parent hacia atrás para obtener la ruta."""
    if parent[target] is None and target != source:
        return None   # no hay camino
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


# ═══════════════════════════════════════════════════════════
# 4. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")

    ORIGENES = [1, 2]
    DESTINOS = [78, 79, 80]

    print("=" * 65)
    print("   RUTA MÁS CORTA — DIJKSTRA")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"\n[ERROR] No se encontró: {ruta_csv}")
        return

    graph, nodos = leer_grafo(ruta_csv)
    print(f"\n✔ Archivo leído correctamente.")
    print(f"  • Nodos totales : {len(nodos)}")
    print(f"  • Arcos totales : {sum(len(v) for v in graph.values())}")
    print(f"  • Orígenes      : {ORIGENES}")
    print(f"  • Destinos      : {DESTINOS}")
    print(f"  • Métrica       : Distancia")

    # ── Resultados por origen ──
    resultados = {}   # (origen, destino) -> (distancia, camino)

    for src in ORIGENES:
        dist, parent = dijkstra(graph, src, nodos)

        print(f"\n{'─'*65}")
        print(f"  ORIGEN: nodo {src}")
        print(f"{'─'*65}")

        for dst in DESTINOS:
            camino = reconstruir_camino(parent, src, dst)
            d      = dist[dst]

            if camino is None or d == float("inf"):
                print(f"\n  → Destino nodo {dst}: NO EXISTE CAMINO")
                resultados[(src, dst)] = (float("inf"), None)
            else:
                ruta_str = " → ".join(str(n) for n in camino)
                saltos   = len(camino) - 1
                print(f"\n  → Destino nodo {dst}:")
                print(f"     Distancia total : {d}")
                print(f"     Número de saltos: {saltos}")
                print(f"     Ruta            : {ruta_str}")
                resultados[(src, dst)] = (d, camino)

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
                print(f"  {src:>6}  {dst:>7}  {'∞':>10}  {'─':>6}  Sin camino")
            else:
                ruta_str = " → ".join(str(n) for n in camino)
                print(f"  {src:>6}  {dst:>7}  {d:>10}  {len(camino)-1:>6}  {ruta_str}")

    # ── Ruta global más corta ──
    mejor = min(
        ((d, src, dst, cam)
         for (src, dst), (d, cam) in resultados.items()
         if cam is not None),
        key=lambda x: x[0]
    )
    d_min, src_min, dst_min, cam_min = mejor
    ruta_min = " → ".join(str(n) for n in cam_min)

    print(f"\n{'='*65}")
    print(f"  RUTA MÁS CORTA GLOBAL")
    print(f"{'='*65}")
    print(f"  Origen   : nodo {src_min}")
    print(f"  Destino  : nodo {dst_min}")
    print(f"  Distancia: {d_min}")
    print(f"  Saltos   : {len(cam_min) - 1}")
    print(f"  Ruta     : {ruta_min}")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
