import gurobipy as gp
import variables as vb
import constraints as ct
import validation as vd

TIME_LIMIT = 5 * 60 * 60

def build_simplified_main(instance, method):
    # Build the MIP of the simplified DSFLP-DAR (i.e., DSFLP)

    mip = gp.Model('DSFLP')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', TIME_LIMIT)

    # Create main constraints
    ct.create_c1(instance, mip, variable)

    # Create cumulative demands
    cumulative = {}
    for customer in instance.customers:
        cumulative[customer] = instance.starts[customer]

    # Set objective function
    for period in instance.periods:
        if method in ['2']:
            cumulative = vd.apply_replenishment(instance, cumulative)
        for location in instance.locations:
            coefficient = vd.evaluate_location(instance, cumulative, period, location)
            variable['y'][period, location].obj = coefficient
        # if method in ['3']:
        #     cumulative = vd.apply_absorption(instance, cumulative, location, -1)
        #     cumulative = vd.apply_consolidation(instance, cumulative)

    return mip, variable

def build_linearized_main(instance):
    # Build the MIP of the linearized DSFLP-DAR

    mip = gp.Model('DSFLP-DAR')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'w': vb.create_vrw(instance, mip),
        'd1': vb.create_vrd1(instance, mip),
        'd2': vb.create_vrd2(instance, mip),
        'd3': vb.create_vrd3(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', TIME_LIMIT)

    # Set objective function
    mip.setObjective(
        sum([instance.revenues[period][location] *
             variable['w'][period, location, customer]
             for period in instance.periods
             for location in instance.locations
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c2(instance, mip, variable)
    ct.create_c3(instance, mip, variable)
    ct.create_c4(instance, mip, variable)
    ct.create_c5(instance, mip, variable)
    ct.create_c6A(instance, mip, variable)
    ct.create_c6B(instance, mip, variable)
    ct.create_c6C(instance, mip, variable)
    ct.create_c6D(instance, mip, variable)

    return mip, variable

def build_linearized_lprx(instance):
    # Build the LPRX of the linearized DSFLP-DAR

    mip, variable = build_linearized_main(instance)

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].vtype = 'C'

    mip.setParam('OutputFlag', 0)

    return mip, variable

def build_reformulated1_main(instance):
    # Build the MIP of the reformulated DSFLP-DAR #1

    mip = gp.Model('DSFLP-DAR-R1')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'z': vb.create_vrz_1(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', TIME_LIMIT)

    # WARNING: identical reward taken from first location at first period!
    # No problem if they are equal anyways, but only a heuristic if different
    common_reward = instance.revenues[instance.periods[0]][instance.locations[0]]

    # Set objective function
    mip.setObjective(
        sum([(common_reward *
              instance.partial_demand('0', period, customer)) *
              variable['z'][period, customer]
              for period in instance.periods
              for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c7(instance, mip, variable)
    ct.create_c8(instance, mip, variable)

    return mip, variable

def build_reformulated1_lprx(instance):
    # Build the LPRX of the reformulated DSFLP-DAR #1

    mip, variable = build_reformulated1_main(instance)

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].vtype = 'C'

    for period in instance.periods:
        for customer in instance.customers:
            variable['z'][period, customer].vtype = 'C'

    mip.setParam('OutputFlag', 0)

    return mip, variable

def build_reformulated2_main(instance):
    # Build the MIP of the reformulated DSFLP-DAR #2

    mip = gp.Model('DSFLP-DAR-R2')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'z': vb.create_vrz_2(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', TIME_LIMIT)

    # Set objective function
    mip.setObjective(
        sum([instance.revenues[period2][location] *
         instance.partial_demand(period1, period2, customer) *
         variable['z'][period1, period2, location, customer]
         for period1 in instance.periods_with_start
         for period2 in instance.periods
         for location in instance.locations
         for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c9(instance, mip, variable)
    ct.create_c10(instance, mip, variable)
    ct.create_c11(instance, mip, variable)
    ct.create_c12(instance, mip, variable)

    return mip, variable

def build_reformulated2_lprx(instance):
    # Build the LPRX of the reformulated DSFLP-DAR #2

    mip, variable = build_reformulated2_main(instance)

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].vtype = 'C'

    for period1 in instance.periods_with_start:
        for period2 in instance.periods_with_end:
            for location in instance.locations:
                for customer in instance.customers:
                    variable['z'][period1, period2, location, customer].vtype = 'C'

    mip.setParam('OutputFlag', 0)

    return mip, variable

def build_reformulated3_main(instance):
    # Build the MIP of the reformulated DSFLP-DAR #3

    mip = gp.Model('DSFLP-DAR-R2')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'z': vb.create_vrz_3(instance, mip),
        'w': vb.create_vrw(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', TIME_LIMIT)

    # Set objective function
    # Warning: update accordingly
    mip.setObjective(
        sum([instance.revenues[period][location] *
         variable['w'][period, location, customer]
         for period in instance.periods
         for location in instance.locations
         for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c13(instance, mip, variable)
    ct.create_c14(instance, mip, variable)
    ct.create_c15(instance, mip, variable)
    ct.create_c16(instance, mip, variable)

    return mip, variable

def build_reformulated3_lprx(instance):
    # Build the LPRX of the reformulated DSFLP-DAR #3

    mip, variable = build_reformulated3_main(instance)

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].vtype = 'C'

    for period1 in instance.periods_with_start:
        for period2 in instance.periods_with_end:
            for customer in instance.customers:
                variable['z'][period1, period2, customer].vtype = 'C'

    # mip.setParam('OutputFlag', 0)

    return mip, variable

def build_nonlinear_main(instance):
    # Build the MIP of the nonlinear DSFLP-DAR

    mip = gp.Model('DSFLP-DAR')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'w': vb.create_vrw_NL(instance, mip),
        'd1': vb.create_vrd1(instance, mip),
        'd2': vb.create_vrd2(instance, mip),
        'd3': vb.create_vrd3(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', TIME_LIMIT)

    # Set objective function
    mip.setObjective(
        sum([instance.revenues[period][location] *
             instance.catalogs[location][customer] *
             variable['w'][period, customer] *
             variable['y'][period, location]
             for period in instance.periods
             for location in instance.locations
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c2(instance, mip, variable)
    ct.create_c3(instance, mip, variable)
    ct.create_c4_NL(instance, mip, variable)
    ct.create_c5(instance, mip, variable)
    ct.create_c6_NL(instance, mip, variable)

    return mip, variable

def block_solution(mip, variable, solution):

    ignored = 0
    for location in solution.values():
        if location == '0':
            ignored += 1

    mip.addConstr(gp.quicksum(variable['y'][period, location] for period, location in solution.items() if location != '0') <= len(solution) - ignored - 1)

def fix_solution(mip, variable, solution):

    mip.addConstrs((variable['y'][period, solution[period]] == 1 if solution[period] != '0' else variable['y'].sum(period, '*') == 0 for period in solution.keys()), name = 'fix')

def warm_start(instance, variable, solution):
    # Warm start with a feasible solution

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].start  = 1. if location == solution[period] else 0.

def format_solution(instance, mip, variable, verbose = 0):
    # Format model solution as dictionary

    solution = {}

    for period in instance.periods:
        solution[period] = '0'

    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if vd.is_equal(value, 1.):
                solution[period] = location

    return solution

def detail_solution(instance, variable, filename = 'detailed_mip.csv'):
    # Detail cumulative demand over time

    solution = {}

    with open(filename, 'w') as output:

        for period in instance.periods:
            solution[period] = '0'

        d1 = {}
        d2 = {}
        d3 = {}
        for customer in instance.customers:
            d3[customer] = variable['d3']['0', customer].x
        output.write('{},{},{}\n'.format('0','0',','.join([str(d3[customer]) for customer in instance.customers])))

        for period in instance.periods:
            for location in instance.locations:
                value = variable['y'][period, location].x
                if vd.is_equal(value, 1.):
                    solution[period] = location
            for customer in instance.customers:
                d1[customer] = variable['d1'][period, customer].x
                d2[customer] = variable['d2'][period, customer].x
                d3[customer] = variable['d3'][period, customer].x
            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(d1[customer]) for customer in instance.customers])))
            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(d2[customer]) for customer in instance.customers])))
            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(d3[customer]) for customer in instance.customers])))

def write_bar(instance, variable, customer = 'A'):
    # Export latex code to plot the bar graph

    solution = {}

    for period in instance.periods:
        solution[period] = '0'

    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if vd.is_equal(value, 1.):
                solution[period] = location
        d1 = variable['d1'][period, customer].x
        a = d1

        xl = int(period) - 0.1
        xr = int(period) + 0.1

        if solution[period] != '0':
            print('\draw[fill=gray!25, dashed] ({},0) -- ({},0) -- ({},{}) -- ({},{}) -- ({},0);'.format(xl, xr, xr, d1, xl, d1, xl))
        else:
            print('\draw[fill=gray!25] ({},0) -- ({},0) -- ({},{}) -- ({},{}) -- ({},0);'.format(xl, xr, xr, d1, xl, d1, xl))
        print('\draw[fill=gray!50] ({},0) -- ({},0) -- ({},{}) -- ({},{}) -- ({},0);'.format(xl, xr, xr, d1 - a, xl, d1 - a, xl))
        print('\draw ({},0) node[anchor=north] {}${}${};'.format(int(period), '{', int(period), '}'))


    print('----------------------------------------------------------------')

    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if vd.is_equal(value, 1.):
                solution[period] = location
        d1 = variable['d1'][period, customer].x
        a = d1

        xl = int(period) - 0.1
        xr = int(period) + 0.1

        print('\draw[fill=gray!25] ({},0) -- ({},0) -- ({},{}) -- ({},{}) -- ({},0);'.format(xl, xr, xr, a, xl, a, xl))
        print('\draw ({},0) node[anchor=north] {}${}${};'.format(int(period), '{', int(period), '}'))

def write_scatter(instance, variable, color, customer = 'A'):
    # Export latex code to plot the bar graph

    solution = {}

    for period in instance.periods:
        solution[period] = '0'

    yprev = -1

    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if vd.is_equal(value, 1.):
                solution[period] = location

        ycurr = variable['d1'][period, customer].x

        xcurr = int(period)
        xprev = xcurr - 1

        print('\draw ({},{}) node[anchor=mid, color={}] {}x{};'.format(xcurr, ycurr, color, '{', '}'))
        # print('\draw ({},0) node[anchor=north] {}${}${};'.format(int(period), '{', int(period), '}'))

        if xcurr > 1:
            print('\draw[color={}] ({},{}) -- ({}, {});'.format(color, xprev, yprev, xcurr, ycurr))

        yprev = ycurr