import os, subprocess, sys

scripts = [
    'fruta_mas_corta_dijkstra.py',
    'gurobi_ruta_mas_corta.py',
    'ortools_ruta_mas_corta.py',
    'solver_ruta_mas_corta_pulp.py',
    
    'flujo_maximo_ford_fulkerson.py',
    'gurobi_flujo_maximo.py',
    'ortools_flujo_maximo.py',
    'solver_flujo_maximo_pulp.py',
    
    'flujo_costo_minimo_cycle_canceling.py',
    'gurobi_flujo_costo_minimo.py',
    'ortools_flujo_costo_minimo.py',
    'solver_flujo_costo_minimo_pulp.py'
]

folder = 'Optimizacion/Proyecto/Contexto'
output_file = os.path.join(folder, 'resultados_comparativos_algoritmos.txt')

env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

with open(output_file, 'w', encoding='utf-8') as outfile:
    for script in scripts:
        path = os.path.join(folder, script)
        print(f'Running {script}...')
        outfile.write(f'\\n======================================================\\n')
        outfile.write(f'   RESULTADOS DE: {script}\\n')
        outfile.write(f'======================================================\\n')
        
        try:
            result = subprocess.run([sys.executable, path], capture_output=True, text=False, env=env)
            stdout_str = result.stdout.decode('utf-8', errors='replace')
            stderr_str = result.stderr.decode('utf-8', errors='replace')
            
            outfile.write(stdout_str)
            if stderr_str:
                outfile.write('\nERRORES:\n' + stderr_str)
        except Exception as e:
            outfile.write(str(e))
        outfile.write('\\n\\n')
