import pulp

# 1. RESOLUCIÓN DEL PROBLEMA PRIMAL
primal = pulp.LpProblem("Problema_Primal", pulp.LpMinimize)

# Variables de decisión
x1 = pulp.LpVariable('X1', lowBound=0)
x2 = pulp.LpVariable('X2', lowBound=0)

# Función Objetivo
primal += 3*x1 - 2*x2

# Restricciones
primal += 2*x1 + x2 <= 18
primal += 2*x1 + 3*x2 <= 42
primal += 3*x1 - 2*x2 <= 24

# Resolver
primal.solve(pulp.PULP_CBC_CMD(msg=0))

# 2. RESOLUCIÓN DEL PROBLEMA DUAL
dual = pulp.LpProblem("Problema_Dual", pulp.LpMaximize)

# Variables duales (u, v, w <= 0)
u = pulp.LpVariable('u', upBound=0)
v = pulp.LpVariable('v', upBound=0)
w = pulp.LpVariable('w', upBound=0)

# Función Objetivo Dual
dual += 18*u + 42*v + 24*w

# Restricciones Duales
dual += 2*u + 2*v + 3*w <= 3
dual += 1*u + 3*v - 2*w <= -2

# Resolver
dual.solve(pulp.PULP_CBC_CMD(msg=0))

# RESULTADOS
print(f"PRIMAL: Z = {pulp.value(primal.objective)}, X1 = {pulp.value(x1)}, X2 = {pulp.value(x2)}")
print(f"DUAL:   W = {pulp.value(dual.objective)}, u = {pulp.value(u)}, v = {pulp.value(v)}, w = {pulp.value(w)}")
