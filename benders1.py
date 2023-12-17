import gurobipy as gp
import validation as vd
import variables as vb
import constraints as ct
import formulation as fm
import heuristic as hr
import time as tm

'''
    Implementation #1 of Benders decomposition
    Vanilla version, original formulation
'''

def analytical_solution(instance, solution, customer):

    # Retrieve primal solution from master solution
    primal_solution = {}
    for period1 in instance.periods_with_start:
        primal_solution[period1] = instance.end
        for period2 in instance.periods:
            if ct.is_before(period1, period2) and solution[period2] != instance.depot and instance.catalogs[solution[period2]][customer] == 1.:
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
            if primal_solution[period3] != period2 and period2 != instance.end and period1 != period3 and ct.is_before(period3, period2):
                location = solution[period2]
                # print('q{} through z[{} -> {}][{}]'.format(period3, period1, period2, location))
                current = instance.revenues[period2][location] * instance.partial_demand(period3, period2, customer)
                current -= instance.revenues[period2][location] * instance.partial_demand(period1, period2, customer)
                current += dual_solution['q'][period1]
                if current > dual_solution['q'][period3]:
                    dual_solution['q'][period3] = current

    # Second pass, free periods
    for period3 in reversed(instance.periods_with_start):
        for period1, period2 in primal_solution.items():
            # compute Q for free periods second  & check if it is not last period & check if it is not the same period & check precedence
            if primal_solution[period3] == period2 and period2 != instance.end and period1 != period3 and ct.is_before(period3, period2):
                location = solution[period2]
                # print('q{} through z[{} -> {}][{}]'.format(period3, period1, period2, location))
                current = instance.revenues[period2][location] * instance.partial_demand(period3, period2, customer)
                current -= instance.revenues[period2][location] * instance.partial_demand(period1, period2, customer)
                current += dual_solution['q'][period1]
                if current > dual_solution['q'][period3]:
                    dual_solution['q'][period3] = current

        # print('q[{}] = {}'.format(period3, dual_solution['q'][period3]))

    dual_solution['p'] = {}
    for period2 in instance.periods:
        dual_solution['p'][period2] = {}
        for location in instance.locations:
            current = instance.revenues[period2][location] * instance.partial_demand(instance.start, period2, customer)
            current += dual_solution['q'][period2]  - dual_solution['q'][instance.start]
            current *= instance.catalogs[location][customer]
            dual_solution['p'][period2][location] = current
            for period1 in instance.periods_with_start:
                if ct.is_before(period1, period2):
                    current = instance.revenues[period2][location] * instance.partial_demand(period1, period2, customer)
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
    S_TIME_LIMIT = B_TIME_LIMIT

    TIME_LEFT = B_TIME_LIMIT

    metadata = {}
    metadata['bds_runtime'] = 0.
    metadata['bds_subtime'] = 0.
    metadata['bds_cuttime'] = 0.

    # Creater master program
    master_mip = gp.Model('DSFLP-DAR-M')

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

    # Set objective function
    master_mip.setObjective(
        sum([master_var['v'][customer]
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, master_mip, master_var)

    if algo == 'program':

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

    while not vd.compare_obj(upper_bound, lower_bound) and TIME_LEFT > 1:

        if it_counter == 0:
            # Create empty solution
            reference = hr.empty_solution(instance)
        else:
            fm.warm_start(instance, master_var, best_solution)
            TIME_LEFT = min(M_TIME_LIMIT, B_TIME_LIMIT - metadata['bds_runtime'])
            TIME_LEFT = max(TIME_LEFT, 1) # Give one extra second to solver
            master_mip.setParam('TimeLimit', TIME_LEFT)
            master_mip.optimize()
            upper_bound = min(upper_bound, round(master_mip.objBound, 2))
            metadata['bds_runtime'] += round(master_mip.runtime, 2)
            reference = fm.format_solution(instance, master_mip, master_var)

        current_bound = 0.

        bds_inequalities[it_counter] = {}

        for customer in instance.customers:

            start = tm.time()
            if algo == 'analytic':
                dual_objective, bds_inequality = analytical_solution(instance, reference, customer)
                current_bound += dual_objective
            elif algo == 'program':
                # Update slave programs
                slaves[customer]['mip'].setObjective(
                    sum([slaves[customer]['var']['p'][period, location] *
                        instance.catalogs[location][customer] *
                        (1 if reference[period] == location else 0)
                        for period in instance.periods
                        for location in instance.locations])
                        + slaves[customer]['var']['q'][instance.start])
                # slaves[customer]['mip'].write('slave_{}.lp'.format(customer))
                # print('Solving slave customer {}'.format(customer))
                slaves[customer]['mip'].optimize()
                current_bound += slaves[customer]['mip'].objVal

                # Build cut for some customer
                bds_inequality = {}
                bds_inequality['y'] = {}
                for period in instance.periods_extended:
                    if period != instance.start and period != instance.end:
                        bds_inequality['y'][period] = {}
                        for location in instance.locations:
                            bds_inequality['y'][period][location] = slaves[customer]['var']['p'][period, location].x
                bds_inequality['b'] = slaves[customer]['var']['q'][instance.start].x
            else:
                exit('Invalid algo for solving the dual problem')
            end = tm.time()
            metadata['bds_runtime'] += round(end - start, 2)
            metadata['bds_subtime'] += round(end - start, 2)

            start = tm.time()
            # Add inequality for some customer
            master_mip.addConstr(master_var['v'][customer] <=
                                    sum(bds_inequality['y'][period][location] *
                                    instance.catalogs[location][customer] *
                                    master_var['y'][period, location]
                                for period in instance.periods for location in instance.locations)
                                + bds_inequality['b']).lazy = 1
            end = tm.time()
            metadata['bds_runtime'] += round(end - start, 2)
            metadata['bds_cuttime'] += round(end - start, 2)

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
        print('Current solution: {}'.format('-'.join(reference.values())))
        print('Best solution: {}'.format('-'.join(best_solution.values())))
        print('\n\n--------------------------------------------')

        # _ = input('next iteration...')

    metadata['bds_optgap'] = vd.compute_gap(upper_bound, lower_bound)
    metadata['bds_iterations'] = it_counter
    metadata['bds_objective'] = lower_bound
    metadata['bds_solution'] = '-'.join(best_solution.values())

    return best_solution, lower_bound, metadata