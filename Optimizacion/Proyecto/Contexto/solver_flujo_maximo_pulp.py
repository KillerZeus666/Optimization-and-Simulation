"""
Flujo Máximo — PuLP (CBC Solver)
=================================
Datos    : matriz_de_datos.csv  (misma carpeta que este script)
Fuente   : nodo 1
Sumidero : nodo 80

Formulación LP:
  Maximizar   F  (flujo total que sale de la fuente)
  Sujeto a:
    [1] Conservación de flujo en cada nodo intermedio:
            sum(f_ij : j vecino de u) - sum(f_ki : k predecesor de u) = 0
    [2] Conservación en fuente:
            sum(f_1j) - sum(f_k1) = F
    [3] Conservación en sumidero:
            sum(f_i80) - sum(f_80j) = F
    [4] Capacidad:
            0 <= f_ij <= cap_ij   para todo arco (i,j)
"""

import csv, os
from collections import defaultdict
import pulp

# ═══════════════════════════════════════════════════════════
# 1. LECTURA DEL CSV
# ═══════════════════════════════════════════════════════════
def leer_grafo(ruta_csv):
    edges = []          # (u, v, capacidad)
    nodos = set()
    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u, v   = int(row["Origen"]), int(row["Destino"])
            cap    = int(row["Capacidad"])
            edges.append((u, v, cap))
            nodos.update([u, v])
    return edges, sorted(nodos)

# ═══════════════════════════════════════════════════════════
# 2. MODELO PuLP
# ═══════════════════════════════════════════════════════════
def resolver_flujo_maximo(edges, nodos, source, sink):

    prob = pulp.LpProblem("Flujo_Maximo", pulp.LpMaximize)

    # Variables de flujo en cada arco
    f = {(u, v): pulp.LpVariable(f"f_{u}_{v}", lowBound=0, upBound=cap)
         for (u, v, cap) in edges}

    # Variable auxiliar: flujo total F
    F = pulp.LpVariable("F", lowBound=0)

    # Función objetivo: maximizar F
    prob += F, "Flujo_total"

    # Índices de salida/entrada por nodo
    salida  = defaultdict(list)
    entrada = defaultdict(list)
    for (u, v, _) in edges:
        salida[u].append((u, v))
        entrada[v].append((u, v))

    # Restricciones de conservación
    for n in nodos:
        flujo_sale  = pulp.lpSum(f[arc] for arc in salida[n])
        flujo_entra = pulp.lpSum(f[arc] for arc in entrada[n])
        if n == source:
            prob += flujo_sale - flujo_entra == F,  f"balance_fuente_{n}"
        elif n == sink:
            prob += flujo_entra - flujo_sale == F,  f"balance_sumidero_{n}"
        else:
            prob += flujo_sale - flujo_entra == 0,  f"balance_{n}"

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    return prob, f, F

# ═══════════════════════════════════════════════════════════
# 3. MAIN
# ═══════════════════════════════════════════════════════════
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    SOURCE, SINK = 1, 80

    print("=" * 65)
    print("   FLUJO MÁXIMO — PuLP / CBC Solver")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontró: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    print(f"\n✔ Archivo leído correctamente.")
    print(f"  • Nodos : {len(nodos)}  |  Arcos : {len(edges)}")
    print(f"  • Fuente : nodo {SOURCE}  |  Sumidero : nodo {SINK}")

    prob, f, F = resolver_flujo_maximo(edges, nodos, SOURCE, SINK)

    estado = pulp.LpStatus[prob.status]
    print(f"\n  Estado del solver : {estado}")

    if prob.status != 1:
        print("  El problema no tiene solución óptima."); return

    flujo_max = pulp.value(F)

    print(f"\n{'='*65}")
    print(f"  FLUJO MÁXIMO = {int(flujo_max)}")
    print(f"{'='*65}")

    # Arcos con flujo positivo
    arcos_activos = [(u, v, pulp.value(f[(u,v)]))
                     for (u, v, _) in edges
                     if pulp.value(f[(u,v)]) > 1e-6]
    arcos_activos.sort(key=lambda x: -x[2])

    print(f"\n  Arcos con flujo positivo: {len(arcos_activos)}")
    print(f"\n  {'Arco':<12} {'Flujo':>8}")
    print(f"  {'─'*12} {'─'*8}")
    for (u, v, fv) in arcos_activos:
        print(f"  {u:>4} → {v:<4}   {fv:>8.1f}")

    print(f"\n{'='*65}")
    print(f"  RESULTADO FINAL: Flujo máximo del nodo {SOURCE} al {SINK} = "
          f"{int(flujo_max)} unidades")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
