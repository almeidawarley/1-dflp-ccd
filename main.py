import instance as ic
import formulation as fm
import gurobipy as gp

instance = ic.instance()

model, variable = fm.build(instance)

model.write('debug.lp')

model.optimize()

for period in instance.periods:
    for location in instance.locations:
        value = variable['ys'][period, location].x
        if value > 0.:
            print('y {} {} : {}'.format(period, location, value))

_ = input('wait..')

for customer in instance.customers:
    print('start for customer {}: {}'.format(customer, instance.starts[customer]))
    for period in instance.periods:

        d1 = variable['d1s'][period, customer].x
        d2 = variable['d2s'][period, customer].x

        w = variable['ws'][period, customer].x

        print('[{}] -> [{}], got {}'.format(d1, d2, w))