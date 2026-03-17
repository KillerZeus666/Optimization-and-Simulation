import os, subprocess, sys

grouped_scripts = {
    "1. RUTA MAS CORTA": ['fruta_mas_corta_dijkstra.py', 'gurobi_ruta_mas_corta.py', 'ortools_ruta_mas_corta.py', 'solver_ruta_mas_corta_pulp.py'],
    "2. FLUJO MAXIMO": ['flujo_maximo_ford_fulkerson.py', 'gurobi_flujo_maximo.py', 'ortools_flujo_maximo.py', 'solver_flujo_maximo_pulp.py'],
    "3. FLUJO DE COSTO MINIMO": ['flujo_costo_minimo_cycle_canceling.py', 'gurobi_flujo_costo_minimo.py', 'ortools_flujo_costo_minimo.py', 'solver_flujo_costo_minimo_pulp.py']
}

folder = 'Optimizacion/Proyecto/Contexto'
output_file = os.path.join(folder, 'resultados_comparativos_algoritmos.txt')

env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("=================================================================\n")
    outfile.write("        RESUMEN EJECUTIVO DE RESULTADOS POR ALGORITMO            \n")
    outfile.write("=================================================================\n\n")

    for category, scripts in grouped_scripts.items():
        outfile.write(f"#################################################################\n")
        outfile.write(f"   {category}\n")
        outfile.write(f"#################################################################\n\n")
        
        for script in scripts:
            path = os.path.join(folder, script)
            # Prevenir errores de lectura inyectando codificacion si falta
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if not content.startswith('# -*- coding: utf-8 -*-'):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('# -*- coding: utf-8 -*-\n' + content)

            print(f'Running {script}...')
            try:
                result = subprocess.run([sys.executable, path], capture_output=True, text=False, env=env)
                stdout_str = result.stdout.decode('utf-8', errors='replace')
                
                # Filtrar sólo desde la TABLA COMPARATIVA en adelante
                resumen = []
                capturar = False
                for line in stdout_str.split('\n'):
                    if "TABLA COMPARATIVA" in line:
                        capturar = True
                    if "Restricted license" in line:
                        continue
                    if capturar:
                        resumen.append(line)
                
                texto_final = '\n'.join(resumen).strip()
                errores = result.stderr.decode('utf-8', errors='replace').strip()
                
                outfile.write(f"--- ALGORITMO / SOLVER: {script} ---\n")
                if texto_final:
                    outfile.write(texto_final + "\n")
                else:
                    outfile.write("No se pudo generar la tabla para este script.\n")
                    
                if errores and ("SyntaxError" in errores or "Traceback" in errores):
                    outfile.write("\nERRORES INTERNOS:\n" + errores + "\n")
                    
                outfile.write("\n" + "-"*65 + "\n\n")
                
            except Exception as e:
                outfile.write(f"Error ejecutando {script}: {str(e)}\n\n")
