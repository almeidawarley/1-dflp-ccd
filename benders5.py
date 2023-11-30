import gurobipy as gp
import variables as vb
import constraints as ct
import formulation as fm


def benders_decomposition(instance):

    B_TIME_LIMIT = 5 * 60 * 60
    M_TIME_LIMIT = B_TIME_LIMIT
    S_TIME_LIMIT = 1 * 10 * 60

    metadata = {}
    metadata['bdn_runtime'] = 0.

    # Creater master program
    master_mip = gp.Model('DSFLP-DAR-M')

    # Create decision variables
    master_var = {
        # Main decision variables
        'y': vb.create_vry_3(instance, master_mip),
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
    ct.create_c1T(instance, master_mip, master_var)

    master_mip._var = master_var

    # Create slave programs
    slaves = {}
    for customer in instance.customers:
        slaves[customer] = {}

        slave_mip = gp.Model('DSFLP-DAR-S{}'.format(customer))
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

        ct.create_c11(instance, slave_mip, slave_var, customer)

        # Update slave programs
        slave_mip.setObjective(
            - slave_var['q'][instance.start]
            + slave_var['q'][instance.end]
        )

        # Build cut for some customer
        slave_mip.optimize()
        inequality = {}
        inequality['p'] = {}
        inequality['q'] = {}
        for period in instance.periods_extended:
            if period != instance.start and period != instance.end:
                inequality['p'][period] = {}
                for location in instance.locations:
                    inequality['p'][period][location] = slave_var['p'][period, location].x
            inequality['q'][period] = slave_var['q'][period].x

        # Add built inequality
        master_mip.addConstr(master_var['v'][customer] <=
                             sum(inequality['p'][period][location] *
                                        instance.catalogs[location][customer] *
                                        master_var['y'].sum(period, location, '*')
                                    for period in instance.periods for location in instance.locations)
                            - inequality['q'][instance.start] +
                            inequality['q'][instance.end])

        slaves[customer]['mip'] = slave_mip
        slaves[customer]['var'] = slave_var

    def add_cut(model, where):

        if where == gp.GRB.Callback.MIPSOL:

            solution = model.cbGetSolution(model._var['y'])

            for customer in instance.customers:

                # Update slave programs
                slaves[customer]['mip'].setObjective(
                    sum([slaves[customer]['var']['p'][period, location] *
                        instance.catalogs[location][customer] *
                        sum(solution[period, location, destination] for destination in instance.locations_extended)
                        for period in instance.periods
                        for location in instance.locations]) -
                        slaves[customer]['var']['q'][instance.start] +
                        slaves[customer]['var']['q'][instance.end])
                # added = slaves[customer]['mip'].addConstrs(slaves[customer]['var']['p'][period, location] == 0 for period in instance.periods for location in instance.locations if solution[period, location] == 1)
                slaves[customer]['mip'].optimize()

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
                model.cbLazy(model._var['v'][customer] <=
                                    sum(inequality['p'][period][location] *
                                    instance.catalogs[location][customer] *
                                    model._var['y'].sum(period, location, '*')
                                for period in instance.periods for location in instance.locations)
                                - inequality['q'][instance.start] + inequality['q'][instance.end])

                # slaves[customer]['mip'].remove(added)
        '''
        elif where == gp.GRB.Callback.MIPNODE:

            solution = model.cbGetNodeRel(model._var['y'])
            print(solution)

            solution = model.cbGetNodeRel(model._var['v'])
            print(solution)

            print('wait...')
            _ = input('waht???')
        '''

    master_mip.optimize(add_cut)

    objective = round(master_mip.objVal, 2)
    solution = fm.format_solution(instance, master_mip, master_var, 3)

    metadata['bdn_runtime'] = master_mip.runtime
    metadata['bdn_iterations'] = -1
    metadata['bdn_objective'] = objective
    metadata['bdn_solution'] = '-'.join(solution.values())
    metadata['bdn_optgap'] = master_mip.MIPGap

    return solution, objective, metadata