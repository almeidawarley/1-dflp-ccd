import gurobipy as gp
import validation as vd
import variables as vb
import constraints as ct
import formulation as fm
import heuristic as hr

TIME_LIMIT = 5 * 60 * 60

'''
def build_master(instance):

    pass

def build_slave(instance, customer):

    pass

def add_cuts(instance, master, variable, slaves, reference):

    pass
'''

def benders_decomposition(instance):

    metadata = {}
    metadata['bds_runtime'] = 0.

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
    master_mip.setParam('TimeLimit', TIME_LIMIT)

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
        slave_mip.setParam('TimeLimit', TIME_LIMIT)

        ct.create_c11(instance, slave_mip, slave_var, customer)

        slaves[customer]['mip'] = slave_mip
        slaves[customer]['var'] = slave_var

    upper_bound = gp.GRB.INFINITY
    lower_bound = 0.
    it_counter = 0
    best_solution = hr.empty_solution(instance)

    while not vd.compare_obj(upper_bound, lower_bound):

        if it_counter == 0:
            # Create empty solution
            reference = hr.empty_solution(instance)
        else:
            fm.warm_start(instance, master_var, best_solution)
            master_mip.setParam('TimeLimit', max(TIME_LIMIT - metadata['bds_runtime'], 0.1))
            master_mip.optimize()
            metadata['bds_optgap'] = master_mip.MIPGap
            # Code for branching on customers
            # relaxed = master_mip.relax()
            # relaxed.optimize()
            # relaxed.write('relaxed.sol')
            # relaxed.write('relaxed.lp')
            metadata['bds_runtime'] += round(master_mip.runtime, 2)
            upper_bound = round(master_mip.objVal, 2)
            reference = fm.format_solution(instance, master_mip, master_var)

        current_bound = 0.

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
            metadata['bds_runtime'] += round(slaves[customer]['mip'].runtime, 2)
            current_bound += slaves[customer]['mip'].objVal

            # Build cut for some customer
            inequality = {}
            inequality['p'] = {}
            inequality['q'] = {}
            for period in instance.periods_extended:
                if period != instance.start and period != instance.end:
                    inequality['p'][period] = {}
                    for location in instance.locations:
                        inequality['p'][period][location] = slaves[customer]['var']['p'][period, location].x
                inequality['q'][period] = slaves[customer]['var']['q'][period].x

            # Add inequality for some customer
            master_mip.addConstr(master_var['v'][customer] <= 
                                    sum(inequality['p'][period][location] *
                                    instance.catalogs[location][customer] * 
                                    master_var['y'][period, location] 
                                for period in instance.periods for location in instance.locations)
                                - inequality['q'][instance.start] +
                                inequality['q'][instance.end])

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

    metadata['bds_iterations'] = it_counter
    metadata['bds_objective'] = lower_bound
    metadata['bds_solution'] = '-'.join(best_solution.values())

    return best_solution, lower_bound, metadata