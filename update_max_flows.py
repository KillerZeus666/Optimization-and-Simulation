import re, os

def update_main(file_path, logic_snippet):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    new_main = '''def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    
    ORIGENES = [1, 2]
    DESTINOS = [78, 79, 80]

    print("=" * 65)
    print("   EVALUANDO TODAS LAS COMBINACIONES")
    print("=" * 65)

    if not os.path.exists(ruta_csv):
        print(f"[ERROR] No se encontro: {ruta_csv}"); return

    edges, nodos = leer_grafo(ruta_csv)
    
    resultados = {}
''' + logic_snippet + '''

if __name__ == "__main__":
    main()
'''
    text = re.sub(r'def main\(\):.*', new_main, text, flags=re.DOTALL)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

logic_gurobi = '''
    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            m, f, F = resolver(edges, nodos, SOURCE, SINK)
            # Para evitar imprimir logs de cada uno
            if m.Status == 2: # GRB.OPTIMAL
                flujo = int(round(F.X))
            else:
                flujo = 0
            resultados[(SOURCE, SINK)] = flujo

    print(f"\\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Flujo Max':>10}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*10}")
    
    for (src, dst), f_max in resultados.items():
        print(f"  {src:>6}  {dst:>7}  {f_max:>10}")

    mejor = max(resultados.items(), key=lambda x: x[1])
    (s_max, t_max), f_max_global = mejor

    print(f"\\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_max}")
    print(f"  Mejor Destino    : {t_max}")
    print(f"  FLUJO MAXIMO     : {f_max_global} unidades")
    print(f"{'='*65}\\n")
'''
update_main('Optimizacion/Proyecto/Contexto/gurobi_flujo_maximo.py', logic_gurobi)

logic_ortools = '''
    from ortools.graph.python import max_flow
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
            
    print(f"\\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Flujo Max':>10}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*10}")
    
    for (src, dst), f_max in resultados.items():
        print(f"  {src:>6}  {dst:>7}  {f_max:>10}")

    mejor = max(resultados.items(), key=lambda x: x[1])
    (s_max, t_max), f_max_global = mejor

    print(f"\\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_max}")
    print(f"  Mejor Destino    : {t_max}")
    print(f"  FLUJO MAXIMO     : {f_max_global} unidades")
    print(f"{'='*65}\\n")
'''
update_main('Optimizacion/Proyecto/Contexto/ortools_flujo_maximo.py', logic_ortools)

logic_pulp = '''
    import pulp
    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            prob, f, F = resolver_flujo_maximo(edges, nodos, SOURCE, SINK)
            if prob.status == 1:
                flujo = int(pulp.value(F))
            else:
                flujo = 0
            resultados[(SOURCE, SINK)] = flujo

    print(f"\\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Flujo Max':>10}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*10}")
    
    for (src, dst), f_max in resultados.items():
        print(f"  {src:>6}  {dst:>7}  {f_max:>10}")

    mejor = max(resultados.items(), key=lambda x: x[1])
    (s_max, t_max), f_max_global = mejor

    print(f"\\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_max}")
    print(f"  Mejor Destino    : {t_max}")
    print(f"  FLUJO MÁXIMO     : {f_max_global} unidades")
    print(f"{'='*65}\\n")
'''
update_main('Optimizacion/Proyecto/Contexto/solver_flujo_maximo_pulp.py', logic_pulp)

logic_ford = '''
    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            # Tenemos que recargar/clonar capacity en cada vuelta porque dfs/bfs la modula
            cap_copy = {u: dict(v) for u, v in capacity.items()}
            f_max, _ = ford_fulkerson(cap_copy, SOURCE, SINK)
            resultados[(SOURCE, SINK)] = f_max

    print(f"\\n{'='*65}")
    print("  TABLA COMPARATIVA — TODAS LAS COMBINACIONES")
    print(f"{'='*65}")
    print(f"  {'Origen':>6}  {'Destino':>7}  {'Flujo Max':>10}")
    print(f"  {'─'*6}  {'─'*7}  {'─'*10}")
    
    for (src, dst), f_max in resultados.items():
        print(f"  {src:>6}  {dst:>7}  {f_max:>10}")

    mejor = max(resultados.items(), key=lambda x: x[1])
    (s_max, t_max), f_max_global = mejor

    print(f"\\n{'='*65}")
    print(f"  RESULTADO OPTIMO GLOBAL")
    print(f"{'='*65}")
    print(f"  Mejor Origen     : {s_max}")
    print(f"  Mejor Destino    : {t_max}")
    print(f"  FLUJO MÁXIMO     : {f_max_global} unidades")
    print(f"{'='*65}\\n")
'''

with open('Optimizacion/Proyecto/Contexto/flujo_maximo_ford_fulkerson.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_main_ford = '''def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    
    ORIGENES = [1, 2]
    DESTINOS = [78, 79, 80]

    print("=" * 65)
    print("   FLUJO MAXIMO - FORD FULKERSON")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    capacity, nodos = leer_grafo(ruta_csv)
    resultados = {}
''' + logic_ford + '''

if __name__ == "__main__":
    main()
'''
text = re.sub(r'def main\(\):.*', new_main_ford, text, flags=re.DOTALL)
with open('Optimizacion/Proyecto/Contexto/flujo_maximo_ford_fulkerson.py', 'w', encoding='utf-8') as f:
    f.write(text)

