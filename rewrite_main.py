import glob
import re

main_snippet_gurobi = '''def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")
    
    ORIGENES = [1, 2]
    DESTINOS = [78, 79, 80]

    print("=" * 65)
    print("   FLUJO MAXIMO — GUROBI")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            m, f, F = resolver(edges, nodos, SOURCE, SINK)
            if m.Status == 2:
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

if __name__ == "__main__":
    main()
'''

main_snippet_ortools = main_snippet_gurobi.replace('FLUJO MAXIMO — GUROBI', 'FLUJO MAXIMO — OR-TOOLS').replace('m, f, F = resolver(edges, nodos, SOURCE, SINK)', '''smf = max_flow.SimpleMaxFlow()
            for (u, v, cap) in edges:
                smf.add_arc_with_capacity(u, v, cap)
            status = smf.solve(SOURCE, SINK)
            if status == smf.OPTIMAL:
                flujo = smf.optimal_flow()
            else:
                flujo = 0''').replace('''            if m.Status == 2:
                flujo = int(round(F.X))
            else:
                flujo = 0''', '').replace('def main():', 'def main():\\n    from ortools.graph.python import max_flow\\n')

main_snippet_pulp = main_snippet_gurobi.replace('FLUJO MAXIMO — GUROBI', 'FLUJO MAXIMO — PuLP').replace('m, f, F = resolver(edges, nodos, SOURCE, SINK)', '''prob, f, F = resolver_flujo_maximo(edges, nodos, SOURCE, SINK)''').replace('''            if m.Status == 2:
                flujo = int(round(F.X))
            else:
                flujo = 0''', '''            if prob.status == 1:
                import pulp
                flujo = int(pulp.value(F))
            else:
                flujo = 0''')

main_snippet_ford = main_snippet_gurobi.replace('FLUJO MAXIMO — GUROBI', 'FLUJO MAXIMO — FORD FULKERSON').replace('m, f, F = resolver(edges, nodos, SOURCE, SINK)', '''cap_copy = {u: dict(v) for u, v in capacity.items()}
            f_max, _ = ford_fulkerson(cap_copy, SOURCE, SINK)
            flujo = f_max''').replace('''            if m.Status == 2:
                flujo = int(round(F.X))
            else:
                flujo = 0''', '').replace('edges, nodos = leer_grafo(ruta_csv)', 'capacity, nodos = leer_grafo(ruta_csv)')

def replace_main(file_path, new_main):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'def main\(\):.*', new_main, text, flags=re.DOTALL)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

replace_main('Optimizacion/Proyecto/Contexto/gurobi_flujo_maximo.py', main_snippet_gurobi)
replace_main('Optimizacion/Proyecto/Contexto/ortools_flujo_maximo.py', main_snippet_ortools)
replace_main('Optimizacion/Proyecto/Contexto/solver_flujo_maximo_pulp.py', main_snippet_pulp)
replace_main('Optimizacion/Proyecto/Contexto/flujo_maximo_ford_fulkerson.py', main_snippet_ford)
