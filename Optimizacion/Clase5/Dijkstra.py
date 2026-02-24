import pulp

# Definir aristas (origen, destino, costo)
aristas = [
    ("A","B",90),
    ("A","C",138),
    ("A","D",348),
    ("B","C",66),
    ("B","E",84),
    ("C","D",156),
    ("C","F",90),
    ("D","G",48),
    ("E","I",84),
    ("F","G",132),
    ("F","H",60),
    ("G","H",48),
    ("G","J",150),
    ("H","I",132),
    ("H","J",126),
    ("I","J",126)
]

nodos = sorted(set([i for i,j,c in aristas] + [j for i,j,c in aristas]))

origen = "A"
destino = "J"

# Crear problema
modelo = pulp.LpProblem("Camino_Minimo", pulp.LpMinimize)

# Variables binarias
x = pulp.LpVariable.dicts("x",
                          [(i,j) for i,j,c in aristas],
                          cat="Binary")

# Función objetivo
modelo += pulp.lpSum(c * x[(i,j)] for i,j,c in aristas)

# Restricciones de flujo
for nodo in nodos:
    flujo_salida = pulp.lpSum(x[(i,j)] for i,j,c in aristas if i == nodo)
    flujo_entrada = pulp.lpSum(x[(i,j)] for i,j,c in aristas if j == nodo)

    if nodo == origen:
        modelo += flujo_salida - flujo_entrada == 1
    elif nodo == destino:
        modelo += flujo_entrada - flujo_salida == 1
    else:
        modelo += flujo_salida - flujo_entrada == 0

# Resolver
modelo.solve()

# Resultados
print("Estado:", pulp.LpStatus[modelo.status])
print("Costo mínimo:", pulp.value(modelo.objective))

print("Aristas seleccionadas:")
for i,j,c in aristas:
    if pulp.value(x[(i,j)]) == 1:
        print(f"{i} → {j}  (costo {c})")