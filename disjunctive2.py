import gurobipy as gp
import instance as ic

shape_ti = {
    '1': {
        '1': 1,
        '2': 0,
        '3': 1
    },
    '2': {
        '1': 1,
        '2': 0,
        '3': 1
    }
}
shape_j = {
    '1': 0,
    '2': 0
}
shape_0 = 1

solution_y = {
    '1': {
        '1': 0.51,
        '2': 0.49,
        '3': 0.00,
    },
    '2': {
        '1': 0.00,
        '2': 0.00,
        '3': 1.00,
    }
}

solution_v = {
    '1': 2.51,
    '2': 2.51
}

inequalities = {0: {'1': {'p': {'1': {'1': 2.0, '2': 0.0, '3': 1.02}, '2': {'1': 3.0, '2': 0.0, '3': 1.53}}, 'q': {'0': 0.0, '1': 0.0, '2': 0.0, '3': 0.0}}, '2': {'p': {'1': {'1': 0.0, '2': 2.0, '3': 1.02}, '2': {'1': 0.0, '2': 3.0, '3': 1.53}}, 'q': {'0': 0.0, '1': 0.0, '2': 0.0, '3': 0.0}}}, 1: {'1': {'p': {'1': {'1': 0.0, '2': 0.0, '3': -0.98}, '2': {'1': 1.0, '2': 0.0, '3': 0.51}}, 'q': {'0': -2.0, '1': 0.0, '2': 0.0, '3': 0.0}}, '2': {'p': {'1': {'1': 0.0, '2': 0.0, '3': -0.98}, '2': {'1': 0.0, '2': 1.0, '3': 0.51}}, 'q': {'0': -2.0, '1': 0.0, '2': 0.0, '3': 0.0}}}, 2: {'1': {'p': {'1': {'1': 0.0, '2': 0.0, '3': -0.98}, '2': {'1': 1.0, '2': 0.0, '3': 0.51}}, 'q': {'0': -2.0, '1': 0.0, '2': 0.0, '3': 0.0}}, '2': {'p': {'1': {'1': 0.0, '2': 0.0, '3': -0.98}, '2': {'1': 0.0, '2': 1.0, '3': 0.51}}, 'q': {'0': -2.0, '1': 0.0, '2': 0.0, '3': 0.0}}}}
it_counter = 2

instance = ic.instance('proof', 'trial')

program = gp.Model('program')
program.setAttr('ModelSense', -1)

cut_set = [i for i in range(0, it_counter)]

u_t = program.addVars(instance.periods, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['ut~{}'.format(period) for period in instance.periods])
u_ub = program.addVars(instance.periods, instance.locations, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['uub~{}_{}'.format(period, location) for period in instance.periods for location in instance.locations])
u_lb = program.addVars(instance.periods, instance.locations, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['ulb~{}_{}'.format(period, location) for period in instance.periods for location in instance.locations])
u_cj = program.addVars(cut_set, instance.customers, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['ucj~{}_{}'.format(cut, customer) for cut in cut_set for customer in instance.customers])
u_0 = program.addVar(lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = 'u~0')

v_t = program.addVars(instance.periods, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['vt~{}'.format(period) for period in instance.periods])
v_ub = program.addVars(instance.periods, instance.locations, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['vub~{}_{}'.format(period, location) for period in instance.periods for location in instance.locations])
v_lb = program.addVars(instance.periods, instance.locations, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['vlb~{}_{}'.format(period, location) for period in instance.periods for location in instance.locations])
v_cj = program.addVars(cut_set, instance.customers, lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['vcj~{}_{}'.format(cut, customer) for cut in cut_set for customer in instance.customers])
v_0 = program.addVar(lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = 'v~0')

g_ti = program.addVars(instance.periods, instance.locations, lb = -gp.GRB.INFINITY, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['gti~{}_{}'.format(period, location) for period in instance.periods for location in instance.locations])
g_j = program.addVars(instance.customers, lb = -gp.GRB.INFINITY, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['gv~{}'.format(customer) for customer in instance.customers])
g_0 = program.addVar(lb = -gp.GRB.INFINITY, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = 'g~0')


program.addConstrs(u_t[period] - sum(inequalities[cut][customer]['p'][period][location] * u_cj[cut, customer] for cut in cut_set for customer in instance.customers) + u_ub[period, location] - u_lb[period, location] + shape_ti[period][location] * u_0 - g_ti[period, location] == 0 for period in instance.periods for location in instance.locations)
program.addConstrs(sum(u_cj[cut, customer] for cut in cut_set) + shape_j[customer] * u_0 - g_j[customer] == 0 for customer in instance.customers)


program.addConstrs(v_t[period] - sum(inequalities[cut][customer]['p'][period][location] * v_cj[cut, customer] for cut in cut_set for customer in instance.customers) + v_ub[period, location] - v_lb[period, location] - shape_ti[period][location] * v_0 - g_ti[period, location]  == 0 for period in instance.periods for location in instance.locations)
program.addConstrs(sum(v_cj[cut, customer] for cut in cut_set) - shape_j[customer] * v_0 - g_j[customer] == 0 for customer in instance.customers)


program.addConstr(sum(u_t[period] for period in instance.periods) + sum((-inequalities[cut][customer]['q'][instance.start] + inequalities[cut][customer]['q'][instance.end]) * u_cj[cut, customer] for cut in cut_set for customer in instance.customers) + sum(u_ub[period, location] for period in instance.periods for location in instance.locations) + shape_0 * u_0 - g_0 <= 0)
program.addConstr(sum(v_t[period] for period in instance.periods) + sum((-inequalities[cut][customer]['q'][instance.start] + inequalities[cut][customer]['q'][instance.end]) * v_cj[cut, customer] for cut in cut_set for customer in instance.customers) + sum(v_ub[period, location] for period in instance.periods for location in instance.locations) - (shape_0 + 1) * v_0 - g_0 <= 0)


program.addConstr(g_0 >= -1)
program.addConstr(g_0 <= 1)

program.setObjective(sum(g_ti[period, location] * solution_y[period][location]
                        for period in instance.periods for location in instance.locations)
                    + sum(g_j[customer] * solution_v[customer]
                        for customer in instance.customers) - g_0)

program.optimize()

for period in instance.periods:
    for location in instance.locations:
        print('Period {}, location {} = {}'.format(period, location, g_ti[period, location].x))

for customer in instance.customers:
    print('Customer {} = {}'.format(customer, g_j[customer].x))

print('RHS: {}'.format(g_0.x))