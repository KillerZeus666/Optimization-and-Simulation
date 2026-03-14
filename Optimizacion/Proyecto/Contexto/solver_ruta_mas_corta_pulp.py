"""
Ruta Más Corta — PuLP / CBC Solver (ILP binario)
=================================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Orígenes : nodo 1, nodo 2
Destinos : nodo 78, nodo 79, nodo 80
Métrica  : Distancia

Formulación ILP (entero binario):
  Variables: x_ij ∈ {0,1}  (1 si el arco i→j está en la ruta)

  Minimizar   sum( distancia_ij * x_ij )

  Sujeto a:
    [1] Flujo en fuente:   sum(x_sj) - sum(x_is) = 1
    [2] Flujo en sumidero: sum(x_it) - sum(x_tj) = 1
    [3] Conservación en intermedios:
            sum(x_uj) - sum(x_iu) = 0   para todo u ≠ s, t
    [4] x_ij ∈ {0, 1}
"""

import csv, os
from collections import defaultdict
import pulp

# ═══════════════════════════════════════════════════════════
# 1. LECTURA DEL CSV
# ═══════════════════════════════════════════════════════════
def leer_grafo(ruta_csv):
    edges = []          # (u, v, distancia)
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
# 2. MODELO PuLP — un par (source, sink)
# ═══════════════════════════════════════════════════════════
def resolver_ruta(edges, nodos, source, sink):

    prob = pulp.LpProblem(f"Ruta_{source}_a_{sink}", pulp.LpMinimize)

    # Variables binarias: ¿está el arco en la ruta?
    x = {(u, v): pulp.LpVariable(f"x_{u}_{v}", cat="Binary")
         for (u, v, _) in edges}

    # Función objetivo: minimizar distancia total
    prob += pulp.lpSum(dist * x[(u, v)]
                       for (u, v, dist) in edges), "Distancia_total"

    # Índices
    salida  = defaultdict(list)
    entrada = defaultdict(list)
    for (u, v, _) in edges:
        salida[u].append((u, v))
        entrada[v].append((u, v))

    # Restricciones de flujo
    for n in nodos:
        sale  = pulp.lpSum(x[arc] for arc in salida[n])
        entra = pulp.lpSum(x[arc] for arc in entrada[n])
        if n == source:
            prob += sale - entra == 1,  f"fuente_{n}"
        elif n == sink:
            prob += entra - sale == 1,  f"sumidero_{n}"
        else:
            prob += sale - entra == 0,  f"balance_{n}"

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if prob.status != 1:
        return None, None, None

    dist_total = pulp.value(prob.objective)

    # Reconstruir camino siguiendo los arcos activos
    siguiente = {}
    for (u, v, _) in edges:
        if pulp.value(x[(u, v)]) > 0.5:
            siguiente[u] = v

    camino = [source]
    nodo   = source
    for _ in range(len(nodos)):
        if nodo == sink:
            break
        nodo = siguiente.get(nodo)
        if nodo is None:
            break
        camino.append(nodo)

    return int(dist_total), camino, prob

# ═══════════════════════════════════════════════════════════
# 3. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    ORIGENES   = [1, 2]
    DESTINOS   = [78, 79, 80]

    print("=" * 65)
    print("   RUTA MÁS CORTA — PuLP / CBC Solver (ILP Binario)")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontró: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n✔ Archivo leído correctamente.")
    print(f"  • Nodos : {len(nodos)}  |  Arcos : {len(edges)}")
    print(f"  • Orígenes : {ORIGENES}")
    print(f"  • Destinos : {DESTINOS}")
    print(f"  • Métrica  : Distancia")

    resultados = {}

    for src in ORIGENES:
        print(f"\n{'─'*65}")
        print(f"  ORIGEN: nodo {src}")
        print(f"{'─'*65}")

        for dst in DESTINOS:
            dist_total, camino, _ = resolver_ruta(edges, nodos, src, dst)

            if camino is None:
                print(f"\n  → Destino nodo {dst}: NO EXISTE CAMINO")
                resultados[(src, dst)] = (float("inf"), None)
            else:
                ruta_str = " → ".join(str(n) for n in camino)
                saltos   = len(camino) - 1
                print(f"\n  → Destino nodo {dst}:")
                print(f"     Distancia total : {dist_total}")
                print(f"     Número de saltos: {saltos}")
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
                print(f"  {src:>6}  {dst:>7}  {'∞':>10}  {'─':>6}  Sin camino")
            else:
                ruta_str = " → ".join(str(n) for n in camino)
                print(f"  {src:>6}  {dst:>7}  {d:>10}  {len(camino)-1:>6}  {ruta_str}")

    # ── Mejor ruta global ──
    mejor = min(
        ((d, s, t, c) for (s, t), (d, c) in resultados.items() if c),
        key=lambda x: x[0]
    )
    d_min, s_min, t_min, c_min = mejor
    print(f"\n{'='*65}")
    print(f"  RUTA MÁS CORTA GLOBAL")
    print(f"{'='*65}")
    print(f"  Origen    : nodo {s_min}")
    print(f"  Destino   : nodo {t_min}")
    print(f"  Distancia : {d_min}")
    print(f"  Saltos    : {len(c_min)-1}")
    print(f"  Ruta      : {' → '.join(str(n) for n in c_min)}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
