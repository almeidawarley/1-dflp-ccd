import gurobipy as gp
import validation as vd
import variables as vb
import constraints as ct
import formulation as fm
import heuristic as hr

def benders_decomposition(instance, time):

    B_TIME_LIMIT = 5 * 60 * 60

    if time == 's':
        M_TIME_LIMIT = B_TIME_LIMIT
        S_TIME_LIMIT = B_TIME_LIMIT
    else:
        M_TIME_LIMIT = 1 * time * 60
        S_TIME_LIMIT = 1 * time * 60

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

    while not vd.compare_obj(upper_bound, lower_bound):

        if it_counter == 0:
            # Create empty solution
            reference = hr.empty_solution(instance)
        else:
            fm.warm_start(instance, master_var, best_solution)
            master_mip.setParam('TimeLimit', min(M_TIME_LIMIT, max(B_TIME_LIMIT - metadata['bd{}_runtime'.format(time)], 0.1)))
            master_mip.optimize()
            metadata['bd{}_optgap'.format(time)] = master_mip.MIPGap
            metadata['bd{}_runtime'.format(time)] += round(master_mip.runtime, 2)
            upper_bound = round(master_mip.objBound, 2)
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