import gurobipy as gp
import math as mt

mip = gp.Model('1-DFLP')

inf = 1e20

periods = [i for i in range(1, 2 + 1)]
customers = [1, 2]

betas = {
    1 : 5,
    2 : 4.9
}

deltas = {
    1 : 25,
    2 : 4.9
}

past = {customer : mt.floor(deltas[customer] / betas[customer]) + 1 for customer in customers}

def adjust_beta(previous, period, customer):
    if period - past[customer] + 1 == previous:
        return deltas[customer] % betas[customer]
    else:
        return betas[customer]

ys = mip.addVars(periods, customers, lb = 0., ub = 1., obj = 0., vtype = 'B', name = 'y')
hs = mip.addVars(periods, periods, customers, lb = 0., ub = 1., obj = 0., vtype = 'B', name = 'h')
ws = mip.addVars(periods, customers, lb = 0., ub = inf, obj = 1., vtype = 'C', name = 'w')

mip.addConstrs((ys.sum(period, '*') <= 1 for period in periods), name = 'c1')
mip.addConstrs((ws[period, customer] <= inf * ys[period, customer] for period in periods for customer in customers), name = 'c2')

mip.addConstrs((ws[period, customer] <= sum([hs[previous, period, customer] * adjust_beta(previous, period, customer) for previous in range(max(1, period - past[customer] + 1), period + 1)]) for period in periods for customer in customers), name = 'c3')

mip.addConstrs((2 * hs[period1, period2, customer] <= 1 - ys[period1, customer] + hs[period1 + 1, period2, customer] for period2 in periods for period1 in periods for customer in customers if period1 < period2), name = 'c4')

mip.setAttr('ModelSense', -1)

mip.optimize()

mip.write('bounder.lp')

for variable in mip.getVars():
    if variable.x > 0. and 'y' in variable.varName:
        print('{} = {}'.format(variable.varName, variable.x))