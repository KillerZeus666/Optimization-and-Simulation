"""
Flujo Máximo - Algoritmo de Ford-Fulkerson (BFS / Edmonds-Karp)
Datos leídos desde: matriz_de_datos.csv
Fuente (source): nodo 1
Sumidero (sink):  nodo 80
"""

import csv
import os
from collections import defaultdict, deque

# ─────────────────────────────────────────────
# 1. LECTURA DEL ARCHIVO CSV
# ─────────────────────────────────────────────
def leer_grafo(ruta_csv: str):
    """Lee el CSV y construye el grafo de capacidades."""
    # Grafo de capacidades: capacity[u][v] = capacidad del arco u -> v
    capacity = defaultdict(lambda: defaultdict(int))
    nodos = set()

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row["Origen"])
            v = int(row["Destino"])
            cap = int(row["Capacidad"])
            # Si ya existe el arco sumamos (puede haber arcos paralelos)
            capacity[u][v] += cap
            nodos.add(u)
            nodos.add(v)

    return capacity, nodos


# ─────────────────────────────────────────────
# 2. BFS - ENCONTRAR CAMINO AUMENTANTE
# ─────────────────────────────────────────────
def bfs(capacity, source, sink, parent):
    """
    BFS sobre la red residual.
    Devuelve True si existe un camino s->t con capacidad residual > 0.
    'parent' guarda el nodo predecesor de cada nodo en el camino.
    """
    visited = set([source])
    queue = deque([source])

    while queue:
        u = queue.popleft()
        for v in capacity[u]:
            if v not in visited and capacity[u][v] > 0:
                visited.add(v)
                parent[v] = u
                if v == sink:
                    return True
                queue.append(v)
    return False


# ─────────────────────────────────────────────
# 3. FORD-FULKERSON (variante Edmonds-Karp)
# ─────────────────────────────────────────────
def ford_fulkerson(capacity, source, sink):
    """
    Implementa Ford-Fulkerson con BFS (= Edmonds-Karp).
    Devuelve:
        max_flow  : valor del flujo máximo
        flow_paths: lista de (camino, flujo_enviado)
    """
    # Construimos la red residual como copia del grafo original
    # (los arcos inversos parten en 0)
    residual = defaultdict(lambda: defaultdict(int))
    for u in capacity:
        for v in capacity[u]:
            residual[u][v] += capacity[u][v]
            # arco inverso (si no existe, queda en 0 por defecto)
            residual[v][u] += 0

    max_flow = 0
    flow_paths = []

    while True:
        parent = {}
        if not bfs(residual, source, sink, parent):
            break  # No hay más caminos aumentantes

        # Encontrar el cuello de botella a lo largo del camino encontrado
        path_flow = float("inf")
        v = sink
        path = []
        while v != source:
            u = parent[v]
            path.append(v)
            path_flow = min(path_flow, residual[u][v])
            v = u
        path.append(source)
        path.reverse()

        # Actualizar capacidades residuales
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            v = u

        max_flow += path_flow
        flow_paths.append((path, path_flow))

    return max_flow, flow_paths


# ─────────────────────────────────────────────
# 4. MAIN
# ─────────────────────────────────────────────
def main():
    # El CSV debe estar en la misma carpeta que este script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(script_dir, "matriz_de_datos.csv")

    print("=" * 60)
    print("   FLUJO MÁXIMO — FORD-FULKERSON (Edmonds-Karp)")
    print("=" * 60)

    # Verificar que el archivo existe
    if not os.path.exists(ruta_csv):
        print(f"\n[ERROR] No se encontró el archivo: {ruta_csv}")
        print("        Coloca 'matriz_de_datos.csv' en la misma carpeta.")
        return

    # Leer datos
    capacity, nodos = leer_grafo(ruta_csv)
    print(f"\n✔ Archivo leído correctamente.")
    print(f"  • Total de nodos: {len(nodos)}")
    print(f"  • Total de arcos: {sum(len(v) for v in capacity.values())}")

    # Definir fuente y sumidero
    SOURCE = 1   # Nodo fuente
    SINK   = 80  # Nodo sumidero

    print(f"\n  • Fuente  (source): nodo {SOURCE}")
    print(f"  • Sumidero (sink) : nodo {SINK}")

    # Ejecutar Ford-Fulkerson
    print("\n─ Ejecutando Ford-Fulkerson... ─")
    max_flow, flow_paths = ford_fulkerson(capacity, SOURCE, SINK)

    # ── Resultados ──
    print(f"\n{'='*60}")
    print(f"  FLUJO MÁXIMO = {max_flow}")
    print(f"{'='*60}")

    print(f"\n  Caminos aumentantes encontrados: {len(flow_paths)}\n")
    for i, (path, f) in enumerate(flow_paths, 1):
        ruta_str = " → ".join(str(n) for n in path)
        print(f"  [{i:>3}] Flujo={f:>4}  |  {ruta_str}")

    print("\n" + "=" * 60)
    print(f"  RESULTADO FINAL: El flujo máximo del nodo {SOURCE}")
    print(f"  al nodo {SINK} es:  {max_flow} unidades")
    print("=" * 60)


if __name__ == "__main__":
    main()
