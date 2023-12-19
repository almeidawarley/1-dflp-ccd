import gurobipy as gp
import variables as vb
import constraints as ct
import formulation as fm
import heuristic as hr
import validation as vd
import time as tm

'''
    Implementation #2 of Benders decomposition
    Lazy constraints, original formulation
'''

def analytical_solution(instance, solution, customer):

    # Retrieve primal solution from master solution
    primal_solution = {}
    for period1 in instance.periods_with_start:
        primal_solution[period1] = instance.end
        for period2 in instance.periods:
            if instance.is_before(period1, period2) and solution[period2] != instance.depot and instance.catalogs[solution[period2]][customer] == 1.:
                primal_solution[period1] = period2
                break

    dual_solution = {}

    # print('Reference: {}'.format('-'.join(solution.values())))

    # print('Analytical solution for j = {} ...'.format(customer))

    dual_solution['q'] = {period : 0. for period in instance.periods_with_start}

    # period1 l, period2 t period3 k
    # First pass, capture periods
    for period3 in reversed(instance.periods_with_start):
        for period1, period2 in primal_solution.items():
            # compute Q for capture periods first  & check if it is not last period & check if it is not the same period & check precedence
            if primal_solution[period3] != period2 and period2 != instance.end and period1 != period3 and instance.is_before(period3, period2):
                location = solution[period2]
                # print('q{} through z[{} -> {}][{}]'.format(period3, period1, period2, location))
                current = instance.revenues[period2][location] * instance.accumulated_demand(period3, period2, customer)
                current -= instance.revenues[period2][location] * instance.accumulated_demand(period1, period2, customer)
                current += dual_solution['q'][period1]
                if current > dual_solution['q'][period3]:
                    dual_solution['q'][period3] = current

    # Second pass, free periods
    for period3 in reversed(instance.periods_with_start):
        for period1, period2 in primal_solution.items():
            # compute Q for free periods second  & check if it is not last period & check if it is not the same period & check precedence
            if primal_solution[period3] == period2 and period2 != instance.end and period1 != period3 and instance.is_before(period3, period2):
                location = solution[period2]
                # print('q{} through z[{} -> {}][{}]'.format(period3, period1, period2, location))
                current = instance.revenues[period2][location] * instance.accumulated_demand(period3, period2, customer)
                current -= instance.revenues[period2][location] * instance.accumulated_demand(period1, period2, customer)
                current += dual_solution['q'][period1]
                if current > dual_solution['q'][period3]:
                    dual_solution['q'][period3] = current

        # print('q[{}] = {}'.format(period3, dual_solution['q'][period3]))

    dual_solution['p'] = {}
    for period2 in instance.periods:
        dual_solution['p'][period2] = {}
        for location in instance.locations:
            current = instance.revenues[period2][location] * instance.accumulated_demand(instance.start, period2, customer)
            current += dual_solution['q'][period2]  - dual_solution['q'][instance.start]
            current *= instance.catalogs[location][customer]
            dual_solution['p'][period2][location] = current
            for period1 in instance.periods_with_start:
                if instance.is_before(period1, period2):
                    current = instance.revenues[period2][location] * instance.accumulated_demand(period1, period2, customer)
                    current += dual_solution['q'][period2] - dual_solution['q'][period1]
                    current *= instance.catalogs[location][customer]
                    if current > dual_solution['p'][period2][location]:
                        dual_solution['p'][period2][location] = current

            # print('p[{},{}] = {}'.format(period2, location, dual_solution['p'][period2][location]))

    # Build cut for some customer
    bds_inequality = {}
    bds_inequality['y'] = {}
    for period in instance.periods_extended:
        if period != instance.start and period != instance.end:
            bds_inequality['y'][period] = {}
            for location in instance.locations:
                bds_inequality['y'][period][location] = dual_solution['p'][period][location]
    bds_inequality['b'] = dual_solution['q'][instance.start]

    dual_objective = dual_solution['q'][instance.start] + sum([dual_solution['p'][period][location] for period, location in solution.items() if location != instance.depot])

    # print('... with an objective of {}'.format(dual_objective))
    # print('Reference: {}'.format('-'.join(solution.values())))

    return dual_objective, bds_inequality

def benders_decomposition(instance, algo = 'analytic'):

    B_TIME_LIMIT = 5 * 60 * 60
    M_TIME_LIMIT = B_TIME_LIMIT
    S_TIME_LIMIT = 1 * 10 * 60

    metadata = {}
    metadata['bl{}_subtime'.format(algo[0])] = 0.
    metadata['bl{}_cuttime'.format(algo[0])] = 0.
    metadata['bl{}_iterations'.format(algo[0])] = 0.

    # Creater master program
    master_mip = gp.Model('DSFLP-C-M')

    # Create decision variables
    master_var = {
        # Main decision variables
        'y': vb.create_vry(instance, master_mip),
        'v': vb.create_vrv(instance, master_mip)
    }

    # Maximize the total revenue
    master_mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # master_mip.setParam('OutputFlag', 0)
    master_mip.setParam('Threads', 1)
    master_mip.setParam('TimeLimit', M_TIME_LIMIT)

    # Activate lazy constraints
    master_mip.setParam('LazyConstraints', 1)

    # Set objective function
    master_mip.setObjective(
        sum([master_var['v'][customer]
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, master_mip, master_var)

    master_mip._var = master_var

    if algo == 'program':
        slaves = {}

    for customer in instance.customers:

        start = tm.time()

        if algo == 'program':

            # Create slave programs
            slaves[customer] = {}

            slave_mip = gp.Model('DSFLP-C-S{}'.format(customer))
            slave_var = {
                'p': vb.create_vrp(instance, slave_mip),
                'q': vb.create_vrq(instance, slave_mip)
            }

            # Minimize dual objective
            slave_mip.setAttr('ModelSense', 1)

            # Turn off GUROBI logs
            slave_mip.setParam('OutputFlag', 0)
            slave_mip.setParam('Threads', 1)
            slave_mip.setParam('TimeLimit', S_TIME_LIMIT)

            ct.create_c9(instance, slave_mip, slave_var, customer)

            # Update slave programs
            slave_mip.setObjective(
                slave_var['q'][instance.start]
            )

            slaves[customer]['mip'] = slave_mip
            slaves[customer]['var'] = slave_var

            # Build cut for some customer
            slave_mip.optimize()
            bds_inequality = {}
            bds_inequality['y'] = {}
            for period in instance.periods_with_start:
                if period != instance.start:
                    bds_inequality['y'][period] = {}
                    for location in instance.locations:
                        bds_inequality['y'][period][location] = slave_var['p'][period, location].x
            bds_inequality['b'] = slave_var['q'][instance.start].x

        elif algo == 'analytic':

            _, bds_inequality = analytical_solution(instance, hr.empty_solution(instance), customer)
        else:
                exit('Invalid algo for solving the dual problem')

        end = tm.time()

        metadata['bl{}_subtime'.format(algo[0])] += round(end - start, 2)

        start = tm.time()

        # Add built inequality
        master_mip.addConstr(master_var['v'][customer] <=
                            sum(bds_inequality['y'][period][location] *
                                        instance.catalogs[location][customer] *
                                        master_var['y'][period, location]
                                    for period in instance.periods for location in instance.locations)
                            + bds_inequality['b'])

        end = tm.time()

        metadata['bl{}_cuttime'.format(algo[0])] += round(end - start, 2)


    def benders_logic(model, where):

        if where == gp.GRB.Callback.MIPSOL:

            solution = model.cbGetSolution(model._var['y'])

            # Format raw solution
            reference = {}
            for period in instance.periods:
                reference[period] = '0'
            for period in instance.periods:
                for location in instance.locations:
                    value = solution[period, location]
                    if vd.is_equal(value, 1.):
                        reference[period] = location

            metadata['bl{}_iterations'.format(algo[0])] += 1

            for customer in instance.customers:

                if algo == 'program':

                    # Update slave programs
                    slaves[customer]['mip'].setObjective(
                        sum([slaves[customer]['var']['p'][period, location] *
                            instance.catalogs[location][customer] *
                            (1 if reference[period] == location else 0)
                            for period in instance.periods
                            for location in instance.locations])
                            + slaves[customer]['var']['q'][instance.start])
                    slaves[customer]['mip'].optimize()

                    # Build cut for some customer
                    bds_inequality = {}
                    bds_inequality['y'] = {}
                    for period in instance.periods_with_start:
                        if period != instance.start:
                            bds_inequality['y'][period] = {}
                            for location in instance.locations:
                                bds_inequality['y'][period][location] = slaves[customer]['var']['p'][period, location].x
                    bds_inequality['b'] = slaves[customer]['var']['q'][instance.start].x

                elif algo == 'analytic':

                    _, bds_inequality = analytical_solution(instance, reference, customer)

                else:

                    exit('Invalid algo for solving the dual problem')

                # Add inequality for some customer
                model.cbLazy(model._var['v'][customer] <=
                                        sum(bds_inequality['y'][period][location] *
                                        instance.catalogs[location][customer] *
                                        model._var['y'][period, location]
                                    for period in instance.periods for location in instance.locations)
                                    + bds_inequality['b'])

    master_mip.optimize(benders_logic)

    objective = round(master_mip.objVal, 2)
    solution = fm.format_solution(instance, master_mip, master_var)

    metadata['bl{}_runtime'.format(algo[0])] = master_mip.runtime
    metadata['bl{}_objective'.format(algo[0])] = objective
    metadata['bl{}_solution'.format(algo[0])] = '-'.join(solution.values())
    metadata['bl{}_optgap'.format(algo[0])] = master_mip.MIPGap

    return solution, objective, metadata