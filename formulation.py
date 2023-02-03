import gurobipy as gp
import variables as vb
import constraints as ct
import validation as vd

def build_simple(instance, method):
    # Build the 1-DFLP

    mip = gp.Model('1-DFLP')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    # mip.setParam('NumericFocus', 3)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', 60 * 60 * 6)

    # Create main constraints
    ct.create_c1(instance, mip, variable)

    # Create cumulative demands
    cumulative = {}
    for customer in instance.customers:
        cumulative[customer] = instance.starts[customer]

    # Compute capturable demands
    for period in instance.periods:
        if method in ['2', '3']:
            cumulative = vd.apply_replenishment(instance, cumulative)
        for location in instance.locations:
            coefficient = vd.evaluate_location(instance, cumulative, period, location)
            variable['y'][period, location].obj = coefficient
        if method in ['3']:
            cumulative = vd.apply_absorption(instance, cumulative, location, -1)
            cumulative = vd.apply_consolidation(instance, cumulative)

    return mip, variable

def build_fancy(instance):
    # Build the 1-DFLP-DRA

    mip = gp.Model('1-DFLP-DRA')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, mip),
        'w': vb.create_vrw(instance, mip),
        'd1': vb.create_vrd1(instance, mip),
        'd2': vb.create_vrd2(instance, mip),
        'd3': vb.create_vrd3(instance, mip),
        's': vb.create_vrs(instance, mip),
        't': vb.create_vrt(instance, mip),
        'u': vb.create_vru(instance, mip),
        'v': vb.create_vrv(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    # mip.setParam('NumericFocus', 3)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', 10 * 60 * 60)

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c2(instance, mip, variable)
    ct.create_c3A(instance, mip, variable)
    ct.create_c3B(instance, mip, variable)
    ct.create_c3C(instance, mip, variable)
    ct.create_c3D(instance, mip, variable)
    ct.create_c4(instance, mip, variable)
    ct.create_c5A(instance, mip, variable)
    ct.create_c5B(instance, mip, variable)
    ct.create_c5C(instance, mip, variable)
    ct.create_c5D(instance, mip, variable)
    ct.create_c6A(instance, mip, variable)
    ct.create_c6B(instance, mip, variable)
    ct.create_c6C(instance, mip, variable)
    ct.create_c6D(instance, mip, variable)
    ct.create_c6E(instance, mip, variable)
    ct.create_c6F(instance, mip, variable)
    ct.create_c6G(instance, mip, variable)
    ct.create_c6H(instance, mip, variable)

    return mip, variable

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
        a = min(instance.gammas[customer] * d1 + instance.deltas[customer], d1)

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
        a = min(instance.gammas[customer] * d1 + instance.deltas[customer], d1)

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