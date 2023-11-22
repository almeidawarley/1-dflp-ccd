import gurobipy as gp

A = [
    [1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [-2, 0, -1.02, -3, 0, -1.53, 1, 0],
    [0, -2, -1.02, 0, -3, -1.53, 0, 1],
    [0, 0, 0.98, -1, 0, -0.51, 1, 0],
    [0, 0, 0.98, 0, -1, -0.51, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [-1, 0, 0, 0, 0, 0, 0, 0],
    [0, -1, 0, 0, 0, 0, 0, 0],
    [0, 0, -1, 0, 0, 0, 0, 0],
    [0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, -1, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0]
]

'''
A = [
    [1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [-2.5, 0, -1.275, -4.75, 0, -2.4225, 1, 0],
    [0, -2.5, -1.275, 0, -4.75, -2.4225, 0, 1],
    [1.25, 0, 2.475, -1, 0, -0.51, 1, 0],
    [0, 1.25, 2.475, 0, -1, -0.51, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [-1, 0, 0, 0, 0, 0, 0, 0],
    [0, -1, 0, 0, 0, 0, 0, 0],
    [0, 0, -1, 0, 0, 0, 0, 0],
    [0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, -1, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0]
]
'''

b = [
    1,
    1,
    0,
    0,
    2,
    2,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    0
]

'''
b = [
    1,
    1,
    0,
    0,
    3.75,
    3.75,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    0
]
'''

p = [
    1,
    0,
    1,
    1,
    0,
    1,
    0,
    0,
    1
]

rows = 18
cols = 8

model1 = gp.Model('model1')
model1.setAttr('ModelSense', -1)
x = model1.addVars([0,1,2,3,4,5,6,7], lb = -gp.GRB.INFINITY, ub = gp.GRB.INFINITY, obj = [0,0,0,0,0,0,1,1], vtype = 'C') #['B','B','B','B','B','B','C','C'])
for i in range(0, rows):
    model1.addConstr(sum(A[i][j] * x[j] for j in range(0, cols)) <= b[i])
model1.optimize()

_ = input('Move onto cut generation...')

xs = [x[i].x for i in range(0, cols)]

model2 = gp.Model('model2')
model2.setAttr('ModelSense', -1)

u = model2.addVars([i for i in range(0, rows + 1)], lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C')
v = model2.addVars([i for i in range(0, rows + 1)], lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C')
g = model2.addVars([i for i in range(0, cols + 1)], lb = -gp.GRB.INFINITY, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C')

for j in range(0, cols):
    model2.addConstr(sum(u[i] * A[i][j] for i in range(0, rows)) + u[rows] * p[j]- g[j] == 0)
    model2.addConstr(sum(v[i] * A[i][j] for i in range(0, rows)) - v[rows] * p[j]- g[j] == 0)

model2.addConstr(sum(u[i] * b[i] + u[rows] * p[cols] - g[cols] for i in range(0, rows)) <= 0)
model2.addConstr(sum(v[i] * b[i] - u[rows] * (p[cols] + 1) - g[cols] for i in range(0, rows)) <= 0)
model2.addConstr(g[cols] >= -1)
model2.addConstr(g[cols] <= 1)

model2.setObjective(sum(xs[j] * g[j] for j in range(0, cols)) - g[cols])

model2.optimize()

for j in range(0, cols + 1):
    print('g[{}] = {}'.format(j, g[j].x))