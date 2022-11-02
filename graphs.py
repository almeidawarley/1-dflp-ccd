import matplotlib.pyplot as plt
import math as mt
import numpy as np

def apply_replenishment(demand, alpha, beta):

    return (1 + alpha) * demand + beta

def apply_absorption(demand, gamma, delta):

    return (1 - gamma) * demand - delta

time_periods = [i for i in range(0, 6)]

computed_demands = []
predicted_demands = []

# Replenishment
alpha = 0
beta  = 1

# Absorption
gamma = 0
delta = 2

demand_ref = 6

# ------------------------------------------------------------------------
# Compute actual demands based on how the problem works
# ------------------------------------------------------------------------

# Previous demand
demand_previous = demand_ref

for t in time_periods:

    computed_demands.append(demand_previous)

    # The replenishment step always happens
    # demand_next = apply_replenishment(demand_previous, alpha, beta)
    demand_next = apply_replenishment(demand_previous, alpha, beta)

    if t == 2:
        d = 0
    else:
        d = delta

    # The absorption step happens if captured
    demand_next = apply_absorption(demand_next, gamma, d)
    # dn = absorption(dp, gamma * 10* (len(ts) - t), delta)

    demand_previous = demand_next

# Previous demand
demand_previous = demand_ref

# ------------------------------------------------------------------------
# Compute analytical demands based on formulas
# ------------------------------------------------------------------------

for t in time_periods:

    if t == 0:
        predicted_demands.append(demand_previous)

    else:

        demand_lin = (beta - delta) * (t) + demand_previous
        demand_exp = ((1 + alpha) * (1 - gamma))**(t) * demand_previous

        demand_next = demand_lin
        predicted_demands.append(demand_next)


plt.plot(time_periods, computed_demands)
# plot(time_periods, computed_demands,'o')
# plt.plot(time_periods, predicted_demands, 'x')
# plt.show()

for t in time_periods:

    print('\draw ({},0) node[anchor=north east] {}$t_{}${};'.format(t + 1.25, '{', t, '}'))
    print('\draw (-0.25,{}) node[anchor=north east] {}$d^{}t_{}{}_{}${};'.format(computed_demands[t] + 0.25, '{', '{', t, '}', '{j}','}'))
    print('\draw (-0.15,{}) -- (0.15, {});'.format(computed_demands[t], computed_demands[t]))

    xl = t + 1 - 0.1
    xr = t + 1 + 0.1

    print('\draw[fill=gray!50] ({},0) -- ({},0) -- ({},{}) -- ({},{}) -- ({},0);'.format(xl, xr, xr, computed_demands[t], xl, computed_demands[t], xl))