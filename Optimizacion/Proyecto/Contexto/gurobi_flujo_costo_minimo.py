# -*- coding: utf-8 -*-
import os, csv
from collections import defaultdict
import gurobipy as gp
from gurobipy import GRB

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
    print("   FLUJO AL COSTO MÍNIMO — GUROBI")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            m = gp.Model("MinCost")
            m.setParam("OutputFlag", 0)
            
            f = {(u, v): m.addVar(lb=0, ub=cap, name=f"f_{u}_{v}") for (u, v, costo, cap) in edges}
            m.setObjective(gp.quicksum(costo * f[(u,v)] for (u,v,costo,cap) in edges), GRB.MINIMIZE)
            
            salida = {n: [] for n in nodos}
            entrada = {n: [] for n in nodos}
            for (u, v, _, __) in edges:
                salida[u].append((u, v))
                entrada[v].append((u, v))
                
            for n in nodos:
                sale = gp.quicksum(f[arc] for arc in salida[n])
                entra = gp.quicksum(f[arc] for arc in entrada[n])
                if n == SOURCE:
                    m.addConstr(sale - entra <= SUPPLY)
                    m.addConstr(sale - entra >= 0)
                elif n == SINK:
                    m.addConstr(entra - sale >= 0.20 * SUPPLY)
                else:
                    m.addConstr(sale - entra == 0)
                    
            m.optimize()
            if m.Status == GRB.OPTIMAL:
                costo_val = m.ObjVal
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
