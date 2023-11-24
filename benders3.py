import gurobipy as gp
import validation as vd
import variables as vb
import constraints as ct
import formulation as fm
import heuristic as hr
import numpy as np

def benders_decomposition(instance, time):

    B_TIME_LIMIT = 5 * 60 * 60

    if time == 's':
        M_TIME_LIMIT = B_TIME_LIMIT
        S_TIME_LIMIT = B_TIME_LIMIT
    else:
        M_TIME_LIMIT = 1 * time * 60
        S_TIME_LIMIT = 1 * time * 60

    TIME_LEFT = B_TIME_LIMIT

    metadata = {}
    metadata['bd{}_runtime'.format(time)] = 0.

    # Creater master program
    master_mip = gp.Model('DSFLP-DAR-M')

    # Create decision variables
    master_var = {
        # Main decision variables
        'y': vb.create_vry(instance, master_mip),
        'v': vb.create_vrv(instance, master_mip)
    }
    master_mip._var = master_var

    # Maximize the total revenue
    master_mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # master_mip.setParam('OutputFlag', 0)
    master_mip.setParam('Threads', 1)
    master_mip.setParam('TimeLimit', M_TIME_LIMIT)

    # Set objective function
    master_mip.setObjective(
        sum([master_var['v'][customer]
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, master_mip, master_var)

    # Create slave programs
    slaves = {}
    for customer in instance.customers:
        slaves[customer] = {}

        # print('Creating slave customer {}'.format(customer))

        slave_mip = gp.Model('DSFLP-DAR-S{}'.format(customer))
        slave_var = {
            # Main decision variables
            'p': vb.create_vrp(instance, slave_mip),
            'q': vb.create_vrq(instance, slave_mip)
        }

        # Minimize dual objective
        slave_mip.setAttr('ModelSense', 1)

        # Turn off GUROBI logs
        slave_mip.setParam('OutputFlag', 0)
        slave_mip.setParam('Threads', 1)
        slave_mip.setParam('TimeLimit', S_TIME_LIMIT)

        ct.create_c11(instance, slave_mip, slave_var, customer)

        slaves[customer]['mip'] = slave_mip
        slaves[customer]['var'] = slave_var

    upper_bound = gp.GRB.INFINITY
    lower_bound = 0.
    it_counter = 0
    best_solution = hr.empty_solution(instance)

    bds_inequalities = {}

    def add_customer_cut(model, where):

        if where == gp.GRB.Callback.MIPNODE:

            shapes = {}
            for customer in instance.customers:
                shapes[customer] = {i : 0 for i, _ in enumerate(model.getVars())}
                summing = 0.
                for period in instance.periods:
                    for location in instance.locations:
                        summing += model.cbGetNodeRel(model._var['y'][period, location]) * instance.catalogs[location][customer]
                        if instance.catalogs[location][customer] == 1.:
                            shapes[customer][model._var['y'][period, location].index] = 1.
                if summing.is_integer():
                    # print('No cut for customer {}'.format(customer))
                    shapes[customer] = {i : 0 for i, _ in enumerate(model.getVars())}
                    shapes[customer][len(model.getVars())] = 0
                else:
                    shapes[customer][len(model.getVars())] = np.floor(summing)

                # print('Shape for customer {}: {}'.format(customer, shapes[customer]))

                ################################################################################

                # Create program for customer-based cut
                cut_generation = gp.Model('cut-generation-{}'.format(customer))
                cut_generation.setAttr('ModelSense', -1)
                # cut_generation.setParam('OutputFlag', 0)

                # Create decision variables
                vars_y = len(instance.periods) * len(instance.locations)
                vars_v = len(instance.customers)
                vars = vars_y + vars_v
                cons = len(master_mip.getConstrs())
                rows, cols = cons + 2 * vars_y, vars

                u = cut_generation.addVars([i for i in range(0, rows + 1)], lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['u~{}'.format(i) for i in range(0, rows + 1)])
                v = cut_generation.addVars([i for i in range(0, rows + 1)], lb = 0, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['v~{}'.format(i) for i in range(0, rows + 1)])
                d = cut_generation.addVars([i for i in range(0, cols + 1)], lb = -gp.GRB.INFINITY, ub = gp.GRB.INFINITY, obj = 0, vtype = 'C', name = ['g~{}'.format(i) for i in range(0, cols + 1)])

                A = model.getA()
                b = model.getAttr('RHS', model.getConstrs())
                for j in range(0, vars_y):
                    cut_generation.addConstr(sum(u[i] * A[i, j] for i in range(0, cons)) + u[cons + j] - u[cons + vars_y + j] + u[rows] * shapes[customer][j] - d[j] == 0)
                    cut_generation.addConstr(sum(v[i] * A[i, j] for i in range(0, cons)) + v[cons + j] - v[cons + vars_y + j] - v[rows] * shapes[customer][j] - d[j] == 0)
                for j in range(vars_y, vars):
                    cut_generation.addConstr(sum(u[i] * A[i, j] for i in range(0, cons)) + u[rows] * shapes[customer][j] - d[j] == 0)
                    cut_generation.addConstr(sum(v[i] * A[i, j] for i in range(0, cons)) - v[rows] * shapes[customer][j] - d[j] == 0)

                cut_generation.addConstr(sum(u[i] * b[i] for i in range(0, cons)) + sum(u[i] for i in range(cons, cons + vars_y)) + u[rows] * shapes[customer][cols] - d[cols] <= 0)
                cut_generation.addConstr(sum(v[i] * b[i] for i in range(0, cons)) + sum(v[i] for i in range(cons, cons + vars_y)) - v[rows] * (shapes[customer][cols] + 1) - d[cols] <= 0)
                cut_generation.addConstr(d[cols] >= -1)
                cut_generation.addConstr(d[cols] <= 1)

                solution = model.cbGetNodeRel(model.getVars())

                cut_generation.setObjective(sum(solution[j] * d[j] for j in range(0, cols)) - d[cols])

                cut_generation.optimize()

                model.cbCut(sum(d[j].x * v for j, v in enumerate(model.getVars())) <= d[cols].x)

                ################################################################################

            # print(model.getAttr("Sense",model.getConstrs()))

            # print(dir(model.getA()))
            # _ = input('check matrix...')

            pass

    while not vd.compare_obj(upper_bound, lower_bound) and TIME_LEFT > 1:

        if it_counter == 0:
            # Create empty solution
            reference = hr.empty_solution(instance)
        else:
            fm.warm_start(instance, master_var, best_solution)
            TIME_LEFT = min(M_TIME_LIMIT, B_TIME_LIMIT - metadata['bd{}_runtime'.format(time)])
            TIME_LEFT = max(TIME_LEFT, 1) # Give one extra second to solver
            master_mip.setParam('TimeLimit', TIME_LEFT)
            master_mip.optimize(add_customer_cut)
            metadata['bd{}_optgap'.format(time)] = master_mip.MIPGap
            metadata['bd{}_runtime'.format(time)] += round(master_mip.runtime, 2)
            upper_bound = min(upper_bound, round(master_mip.objBound, 2))
            reference = fm.format_solution(instance, master_mip, master_var)

        current_bound = 0.

        bds_inequalities[it_counter] = {}

        for customer in instance.customers:

            # Update slave programs
            slaves[customer]['mip'].setObjective(
                sum([slaves[customer]['var']['p'][period, location] *
                    instance.catalogs[location][customer] *
                    (1 if reference[period] == location else 0)
                    for period in instance.periods
                    for location in instance.locations]) -
                    slaves[customer]['var']['q'][instance.start] +
                    slaves[customer]['var']['q'][instance.end])
            # slaves[customer]['mip'].write('slave_{}.lp'.format(customer))
            # print('Solving slave customer {}'.format(customer))
            slaves[customer]['mip'].optimize()
            metadata['bd{}_runtime'.format(time)] += round(slaves[customer]['mip'].runtime, 2)
            current_bound += slaves[customer]['mip'].objVal

            # Build cut for some customer
            bds_inequality = {}
            bds_inequality['y'] = {}
            for period in instance.periods_extended:
                if period != instance.start and period != instance.end:
                    bds_inequality['y'][period] = {}
                    for location in instance.locations:
                        bds_inequality['y'][period][location] = slaves[customer]['var']['p'][period, location].x
            bds_inequality['b'] = - slaves[customer]['var']['q'][instance.start].x + slaves[customer]['var']['q'][instance.end].x

            # Add inequality for some customer
            master_mip.addConstr(master_var['v'][customer] <=
                                    sum(bds_inequality['y'][period][location] *
                                    instance.catalogs[location][customer] *
                                    master_var['y'][period, location]
                                for period in instance.periods for location in instance.locations)
                                + bds_inequality['b'])

            bds_inequalities[it_counter][customer] = bds_inequality

        current_bound = round(current_bound, 2)
        if current_bound > lower_bound:
            lower_bound = current_bound
            best_solution = hr.copy_solution(reference)
        it_counter += 1

        print('--------------------------------------------\n\n')
        print('Iteration: {}'.format(it_counter))
        print('Lower bound: {}'.format(lower_bound))
        print('Current bound: {}'.format(current_bound))
        print('Upper bound: {}'.format(upper_bound))
        print('\n\n--------------------------------------------')

    metadata['bd{}_iterations'.format(time)] = it_counter
    metadata['bd{}_objective'.format(time)] = lower_bound
    metadata['bd{}_solution'.format(time)] = '-'.join(best_solution.values())

    return best_solution, lower_bound, metadata