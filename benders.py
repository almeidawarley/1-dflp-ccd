import gurobipy as gp
import common as cm
import variables as vb
import constraints as ct
import formulation as fm
import time as tm

'''
    Implementation #1 of Benders decomposition
    Vanilla version, original formulation
'''

# Create subproblems
subproblems = {}

def duality_method(instance, incumbent, customer):

    # Update subproblems
    subproblems[customer]['mip'].setObjective(
        sum([subproblems[customer]['var']['p'][period, location] *
            instance.catalogs[location][customer] *
            (1 if incumbent[period] == location else 0)
            for period in instance.periods
            for location in instance.locations])
            + subproblems[customer]['var']['q'][instance.start])
    subproblems[customer]['mip'].optimize()

    # Build cut for some customer
    inequality = {}
    inequality['y'] = {}
    for period in instance.periods_extended:
        if period != instance.start and period != instance.end:
            inequality['y'][period] = {}
            for location in instance.locations:
                inequality['y'][period][location] = subproblems[customer]['var']['p'][period, location].x
    inequality['b'] = subproblems[customer]['var']['q'][instance.start].x

    return subproblems[customer]['mip'].objVal, inequality

def analytical_method(instance, solution, customer):

    # Retrieve primal solution from master solution
    primal_solution = {}
    for period1 in instance.periods_with_start:
        primal_solution[period1] = instance.end
        for period2 in instance.periods:
            if instance.is_before(period1, period2) and solution[period2] != instance.depot and instance.catalogs[solution[period2]][customer] == 1.:
                primal_solution[period1] = period2
                break

    dual_solution = {}

    # print('Incumbent: {}'.format('-'.join(solution.values())))

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
    inequality = {}
    inequality['y'] = {}
    for period in instance.periods_extended:
        if period != instance.start and period != instance.end:
            inequality['y'][period] = {}
            for location in instance.locations:
                inequality['y'][period][location] = dual_solution['p'][period][location]
    inequality['b'] = dual_solution['q'][instance.start]

    dual_objective = dual_solution['q'][instance.start] + sum([dual_solution['p'][period][location] for period, location in solution.items() if location != instance.depot])

    # print('... with an objective of {}'.format(dual_objective))
    # print('Incumbent: {}'.format('-'.join(solution.values())))

    return dual_objective, inequality

def benders_standard(instance, algo = 'analytic'):

    subproblems = {}

    remaining = cm.TIMELIMIT

    metadata = {}
    metadata['bs{}_runtime'.format(algo[0])] = 0.
    metadata['bs{}_subtime'.format(algo[0])] = 0.
    metadata['bs{}_cuttime'.format(algo[0])] = 0.

    master_mip, master_var = fm.build_master(instance)

    if algo == 'duality':

        for customer in instance.customers:
            subproblems[customer] = {}
            subproblem_mip, subproblem_var = fm.build_subproblem(instance, customer)
            subproblems[customer]['mip'] = subproblem_mip
            subproblems[customer]['var'] = subproblem_var

    upper_bound = gp.GRB.INFINITY
    lower_bound = 0.
    it_counter = 0
    best_solution = instance.empty_solution()

    while not cm.compare_obj(upper_bound, lower_bound) and remaining > 1:

        if it_counter == 0:
            # Create empty solution
            incumbent = instance.empty_solution()
        else:
            fm.warm_start(instance, master_var, best_solution)
            remaining = max(cm.TIMELIMIT - metadata['bs{}_runtime'.format(algo[0])], 10) # Give 1s extra
            master_mip.setParam('TimeLimit', remaining)
            master_mip.optimize()
            upper_bound = min(upper_bound, round(master_mip.objBound, 2))
            metadata['bs{}_runtime'.format(algo[0])] += round(master_mip.runtime, 2)
            incumbent = instance.format_solution(master_var['y'])

        current_bound = 0.

        for customer in instance.customers:

            start = tm.time()
            if algo == 'analytic':
                dual_objective, inequality = analytical_method(instance, incumbent, customer)
            elif algo == 'duality':
                dual_objective, inequality = duality_method(instance, incumbent, customer)
            else:
                exit('Invalid algo for solving the dual problem')
            end = tm.time()
            current_bound += dual_objective
            metadata['bs{}_runtime'.format(algo[0])] += round(end - start, 2)
            metadata['bs{}_subtime'.format(algo[0])] += round(end - start, 2)

            start = tm.time()
            # Add inequality for some customer
            master_mip.addConstr(master_var['v'][customer] <=
                                    sum(inequality['y'][period][location] *
                                    instance.catalogs[location][customer] *
                                    master_var['y'][period, location]
                                    for period in instance.periods 
                                    for location in instance.locations)
                                + inequality['b']).lazy = 3
            end = tm.time()
            metadata['bs{}_runtime'.format(algo[0])] += round(end - start, 2)
            metadata['bs{}_cuttime'.format(algo[0])] += round(end - start, 2)

        current_bound = round(current_bound, 2)
        if current_bound > lower_bound:
            lower_bound = current_bound
            best_solution = instance.copy_solution(incumbent)
        it_counter += 1

        print('--------------------------------------------\n\n')
        print('Iteration: {}'.format(it_counter))
        print('Lower bound: {}'.format(lower_bound))
        print('Current bound: {}'.format(current_bound))
        print('Upper bound: {}'.format(upper_bound))
        print('Current solution: {}'.format('-'.join(incumbent.values())))
        print('Best solution: {}'.format('-'.join(best_solution.values())))
        print('\n\n--------------------------------------------')

        # _ = input('next iteration...')

    metadata['bs{}_optgap'.format(algo[0])] = cm.compute_gap(upper_bound, lower_bound)
    metadata['bs{}_iterations'.format(algo[0])] = it_counter
    metadata['bs{}_objective'.format(algo[0])] = lower_bound
    metadata['bs{}_solution'.format(algo[0])] = '-'.join(best_solution.values())

    return best_solution, lower_bound, metadata

def branch_and_benders_cut(instance, algo = 'analytic'):

    subproblems = {}

    metadata = {}
    metadata['bl{}_subtime'.format(algo[0])] = 0.
    metadata['bl{}_cuttime'.format(algo[0])] = 0.
    metadata['bl{}_iterations'.format(algo[0])] = 0.

    master_mip, master_var = fm.build_master(instance)

    master_mip._var = master_var

    empty = instance.empty_solution()

    for customer in instance.customers:

        start = tm.time()

        if algo == 'duality':

            # Create subproblems
            subproblems[customer] = {}

            subproblem_mip, subproblem_var = fm.build_subproblem(instance, customer)

            subproblems[customer]['mip'] = subproblem_mip
            subproblems[customer]['var'] = subproblem_var

            _, inequality = duality_method(instance, empty, customer)

        elif algo == 'analytic':

            _, inequality = analytical_method(instance, empty, customer)
        else:
                exit('Invalid algo for solving the dual problem')

        end = tm.time()

        metadata['bl{}_subtime'.format(algo[0])] += round(end - start, 2)

        start = tm.time()

        # Add built inequality
        master_mip.addConstr(master_var['v'][customer] <=
                                sum(inequality['y'][period][location] *
                                    instance.catalogs[location][customer] *
                                    master_var['y'][period, location]
                                    for period in instance.periods
                                    for location in instance.locations)
                            + inequality['b'])

        end = tm.time()

        metadata['bl{}_cuttime'.format(algo[0])] += round(end - start, 2)


    def benders_logic(model, where):

        if where == gp.GRB.Callback.MIPSOL:

            solution = model.cbGetSolution(model._var['y'])

            # Format raw solution
            incumbent = {}
            for period in instance.periods:
                incumbent[period] = '0'
            for period in instance.periods:
                for location in instance.locations:
                    value = solution[period, location]
                    if cm.is_equal_to(value, 1.):
                        incumbent[period] = location

            metadata['bl{}_iterations'.format(algo[0])] += 1

            for customer in instance.customers:

                if algo == 'duality':

                    _, inequality = duality_method(instance, incumbent, customer)

                elif algo == 'analytic':

                    _, inequality = analytical_method(instance, incumbent, customer)

                else:

                    exit('Invalid algo for solving the dual problem')

                # Add inequality for some customer
                model.cbLazy(model._var['v'][customer] <=
                                    sum(inequality['y'][period][location] *
                                    instance.catalogs[location][customer] *
                                    model._var['y'][period, location]
                                    for period in instance.periods 
                                    for location in instance.locations)
                                    + inequality['b'])

    master_mip.optimize(benders_logic)

    objective = round(master_mip.objVal, 2)
    solution = instance.format_solution(master_var['y'])

    metadata['bl{}_runtime'.format(algo[0])] = master_mip.runtime
    metadata['bl{}_objective'.format(algo[0])] = objective
    metadata['bl{}_solution'.format(algo[0])] = '-'.join(solution.values())
    metadata['bl{}_optgap'.format(algo[0])] = master_mip.MIPGap

    return solution, objective, metadata