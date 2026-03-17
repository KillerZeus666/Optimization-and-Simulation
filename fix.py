import glob

for f_path in glob.glob('Optimizacion/Proyecto/Contexto/*_flujo_maximo*.py'):
    with open(f_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(f_path, 'w', encoding='utf-8') as f:
        for line in lines:
            line = line.replace('f"\n', 'f"\\n').replace('f"\\n{', 'f"\\n{')
            f.write(line)
