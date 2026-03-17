# -*- coding: utf-8 -*-
import os, csv
from collections import defaultdict
import pulp

def leer_grafo(ruta_csv):
    edges = []
    nodos = set()
    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append((int(row["Origen"]), int(row["Destino"]), float(row["Costo"]), int(row["Capacidad"])))
            nodos.update([int(row["Origen"]), int(row["Destino"])])
    return edges, sorted(nodos)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    
    ORIGENES = [1, 2]
    DESTINOS = [80]
    SUPPLY = 500

    print("=" * 65)
    print("   FLUJO AL COSTO MÍNIMO — PuLP")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            prob = pulp.LpProblem(f"MCF_{SOURCE}_{SINK}", pulp.LpMinimize)
            f = {(u, v): pulp.LpVariable(f"f_{u}_{v}", lowBound=0, upBound=cap) for (u, v, costo, cap) in edges}
            
            prob += pulp.lpSum(costo * f[(u,v)] for (u,v,costo,cap) in edges)
            
            salida = {n: [] for n in nodos}
            entrada = {n: [] for n in nodos}
            for (u, v, _, __) in edges:
                salida[u].append((u, v))
                entrada[v].append((u, v))
                
            for n in nodos:
                sale = pulp.lpSum(f[arc] for arc in salida[n])
                entra = pulp.lpSum(f[arc] for arc in entrada[n])
                if n == SOURCE:
                    prob += sale - entra <= SUPPLY
                    prob += sale - entra >= 0
                elif n == SINK:
                    # El usuario indicó: "coloquemos que minimo se mande el 20% no que mandes 100 simplemnte"
                    prob += entra - sale >= 0.20 * SUPPLY  
                else:
                    prob += sale - entra == 0
                    
            prob.solve(pulp.PULP_CBC_CMD(msg=0))
            if prob.status == 1:
                costo_val = pulp.value(prob.objective)
            else:
                costo_val = float('inf')
                
            resultados[(SOURCE, SINK)] = costo_val

    print(f"\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Costo Minimo':>15}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*15}")
    
    for (src, dst), c_min in resultados.items():
        if c_min != float('inf'):
            print(f"  {src:>6}  {dst:>7}  {c_min:>15.1f}")
        else:
            print(f"  {src:>6}  {dst:>7}  {'Infactible':>15}")

    validos = {k: v for k,v in resultados.items() if v != float('inf')}
    if not validos:
        print("Ninguna ruta factible.")
        return
        
    mejor = min(validos.items(), key=lambda x: x[1])
    (s_min, t_min), c_min_global = mejor

    print(f"\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_min}")
    print(f"  Mejor Destino    : {t_min}")
    print(f"  COSTO MÍNIMO     : {c_min_global:.1f}")
    print(f"{'='*65}\n")

if __name__ == '__main__':
    main()
