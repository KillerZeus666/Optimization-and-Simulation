import os, csv

def fix_all_min_cost():
    orig = [1, 2]
    dest = [78, 79, 80]
    
    # 1) Pulp Min Cost
    pulp_code = """import os, csv
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
    DESTINOS = [78, 79, 80]
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

    print(f"\\n{'='*65}")
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

    print(f"\\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_min}")
    print(f"  Mejor Destino    : {t_min}")
    print(f"  COSTO MÍNIMO     : {c_min_global:.1f}")
    print(f"{'='*65}\\n")

if __name__ == '__main__':
    main()
"""
    with open('Optimizacion/Proyecto/Contexto/solver_flujo_costo_minimo_pulp.py', 'w', encoding='utf-8') as f:
        f.write(pulp_code)


    # 2) Gurobi Min Cost
    gurobi_code = """import os, csv
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
    DESTINOS = [78, 79, 80]
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

    print(f"\\n{'='*65}")
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

    print(f"\\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_min}")
    print(f"  Mejor Destino    : {t_min}")
    print(f"  COSTO MÍNIMO     : {c_min_global:.1f}")
    print(f"{'='*65}\\n")

if __name__ == '__main__':
    main()
"""
    with open('Optimizacion/Proyecto/Contexto/gurobi_flujo_costo_minimo.py', 'w', encoding='utf-8') as f:
        f.write(gurobi_code)


    # 3) OR-Tools Min Cost
    ortools_code = """import os, csv
from ortools.graph.python import min_cost_flow

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
    DESTINOS = [78, 79, 80]
    SUPPLY = 500

    print("=" * 65)
    print("   FLUJO AL COSTO MÍNIMO — OR-Tools")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            smcf = min_cost_flow.SimpleMinCostFlow()
            
            for (u, v, costo, cap) in edges:
                # OR-Tools SimpleMinCostFlow requires integer capacities and costs!
                c_int = int(round(costo))
                smcf.add_arc_with_capacity_and_unit_cost(u, v, cap, c_int)
                
            # For min cost flow with at least 20% supply, SimpleMinCostFlow is a true flow network.
            # We must set exactly supply= demand. If we want to find min cost for exactly 0.20*SUPPLY:
            # The prompt says minimum 20% of 500. So we will supply exactly 20% of 500 which is 100 since we just want minimum cost.
            # Wait, OR-Tools requires strict balance at all nodes. We will just supply exactly 100 to the sink and -100 to sink.
            # That is the equivalent to `entra >= 0.20*SUPPLY` with `MINIMIZE cost`.
            
            demanda_minima = int(0.20 * SUPPLY)
            for n in nodos:
                if n == SOURCE:
                    smcf.set_node_supply(n, demanda_minima)
                elif n == SINK:
                    smcf.set_node_supply(n, -demanda_minima)
                else:
                    smcf.set_node_supply(n, 0)
                    
            status = smcf.solve()
            if status == smcf.OPTIMAL:
                costo_val = smcf.optimal_cost()
            else:
                costo_val = float('inf')
                
            resultados[(SOURCE, SINK)] = costo_val

    print(f"\\n{'='*65}")
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

    print(f"\\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_min}")
    print(f"  Mejor Destino    : {t_min}")
    print(f"  COSTO MÍNIMO     : {c_min_global:.1f}")
    print(f"{'='*65}\\n")


if __name__ == '__main__':
    main()
"""
    with open('Optimizacion/Proyecto/Contexto/ortools_flujo_costo_minimo.py', 'w', encoding='utf-8') as f:
        f.write(ortools_code)

if __name__ == '__main__':
    fix_all_min_cost()
