import os
import re

fpath = 'Optimizacion/Proyecto/Contexto/flujo_costo_minimo_cycle_canceling.py'
with open(fpath, 'r', encoding='utf-8') as f:
    text = f.read()

new_main = '''def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_csv   = os.path.join(script_dir, "matriz_de_datos.csv")

    ORIGENES = [1, 2]
    DESTINOS = [78, 79, 80]
    SUPPLY      = 500   # Unidades a enviar desde la fuente
    MIN_SINK_PCT= 0.20  # Al menos 20 % debe llegar al nodo 80
    min_requerido = int(SUPPLY * MIN_SINK_PCT)

    print("=" * 65)
    print("   FLUJO AL COSTO MÍNIMO — CYCLE CANCELING (Klein)")
    print("=" * 65)

    if not os.path.exists(ruta_csv): return

    edges, nodos = leer_grafo(ruta_csv)
    resultados = {}

    for SOURCE in ORIGENES:
        for SINK in DESTINOS:
            cap_original = defaultdict(lambda: defaultdict(int))
            for (u, v, c, capacity) in edges:
                cap_original[u][v] += capacity

            cap, cost, adj = construir_red_residual(edges)

            flujo_enviado, costo_inicial, rutas_fase1 = enviar_flujo(
                cap, cost, adj, SOURCE, SINK, min_requerido
            )

            if flujo_enviado < min_requerido:
                resultados[(SOURCE, SINK)] = float('inf')
                continue

            ahorro, n_ciclos = cycle_canceling(cap, cost, adj, nodos)
            
            costo_final = costo_inicial - ahorro
            resultados[(SOURCE, SINK)] = costo_final

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
'''

text = re.sub(r'def main\(\):.*', new_main + '\nif __name__ == "__main__":\n    main()\n', text, flags=re.DOTALL)

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(text)
