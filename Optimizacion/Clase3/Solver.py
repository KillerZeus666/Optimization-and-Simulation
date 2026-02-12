import pulp as pl

# =========================
# Modelo
# =========================
modelo = pl.LpProblem("Flujo_Costo_Minimo_con_Capacidades", pl.LpMinimize)

# =========================
# Variables (con capacidad)
# =========================
x12 = pl.LpVariable("x12", lowBound=0, upBound=25)
x13 = pl.LpVariable("x13", lowBound=0, upBound=100)
x14 = pl.LpVariable("x14", lowBound=0, upBound=70)
x23 = pl.LpVariable("x23", lowBound=0, upBound=30)
x25 = pl.LpVariable("x25", lowBound=0, upBound=15)
x36 = pl.LpVariable("x36", lowBound=0, upBound=200)
x43 = pl.LpVariable("x43", lowBound=0, upBound=60)
x46 = pl.LpVariable("x46", lowBound=0, upBound=30)
x56 = pl.LpVariable("x56", lowBound=0, upBound=150)

# =========================
# Función objetivo
# =========================
modelo += (
    3*x12 + 5*x13 + 9*x14 +
    4*x23 + 4*x25 +
    10*x36 +
    6*x43 + 14*x46 +
    6*x56
)

# =========================
# Restricciones de flujo
# =========================
modelo += x12 + x13 + x14 == 180          # Origen
modelo += x12 - x23 - x25 == 0            # Nodo 2
modelo += x13 + x23 - x36 + x43 == 0      # Nodo 3
modelo += x14 - x43 - x46 == 0            # Nodo 4
modelo += x25 - x56 == 0                  # Nodo 5
modelo += x36 + x46 + x56 == 180          # Destino

# =========================
# Resolver
# =========================
modelo.solve()

# =========================
# Resultados
# =========================
print("Estado:", pl.LpStatus[modelo.status])
print("Costo mínimo:", pl.value(modelo.objective))

for v in modelo.variables():
    print(v.name, "=", v.varValue)
