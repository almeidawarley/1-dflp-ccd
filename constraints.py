import gurobipy as gp

def previous(period):

    return str(int(period) - 1)

def is_before(period1, period2):

    return int(period1) < int(period2)

def is_after(period1, period2):

    return int(period1) > int(period2)

def map_catalog(instance, reference, customer):
    # Kind of deprecated, but may be useful

    return {
        (period, location) : instance.catalogs[location][customer] if period == reference else 0.
        for period in instance.periods
        for location in instance.locations
    }

# ---------------------------------------------------------------------------

def create_c1(instance, mip, variable):
    # Create constraint 1

    mip.addConstrs((variable['y'].sum(period, '*') <= 1 for period in instance.periods), name = 'c1')

# ---------------------------------------------------------------------------

def create_c1T(instance, mip, variable):
    # Create constraint 1, network version

    mip.addConstrs((variable['y'].sum(previous(period), '*', location) == variable['y'].sum(period, location, '*') for period in instance.periods for location in instance.locations_extended), name = 'c1A')
    mip.addConstr((variable['y'].sum(instance.start, instance.depot, '*') == 1), name = 'cB1')
    mip.addConstr(sum(variable['y'].sum(instance.start, location, '*') for location in instance.locations) == 0, name = 'cC1')
    mip.addConstr((variable['y'].sum(previous(instance.end), '*', instance.depot) == 1), name = 'c1D')
    mip.addConstr(sum(variable['y'].sum(previous(instance.end), '*', location) for location in instance.locations) == 0, name = 'cE1')

# ---------------------------------------------------------------------------

def create_c2(instance, mip, variable):
    # Create constraint 2

    mip.addConstrs((variable['d3']['0', customer] == instance.starts[customer] for customer in instance.customers), name = 'c2')

# ---------------------------------------------------------------------------

def create_c3(instance, mip, variable):
    # Create constraint 3

    mip.addConstrs((variable['d1'][period, customer] == (1 + instance.alphas[customer]) * variable['d3'][previous(period), customer] + instance.betas[customer] for period in instance.periods for customer in instance.customers), name = 'c3')

# ---------------------------------------------------------------------------

def create_c4(instance, mip, variable):
    # Create constraint 4, linearized

    mip.addConstrs((variable['d2'][period, customer] == variable['d1'][period, customer] - variable['w'].sum(period, '*', customer) for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c4_NL(instance, mip, variable):
    # Create constraint 4, nonlinear

    mip.addConstrs((variable['d2'][period, customer] == variable['d1'][period, customer] - variable['w'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c5(instance, mip, variable):
    # Create constraint 5

    mip.addConstrs((variable['d3'][period, customer] == variable['d2'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c5')

# ---------------------------------------------------------------------------

def create_c6_NL(instance, mip, variable):
    # Create constraint 6, nonlinear

    mip.addConstrs((variable['w'][period, customer] == sum(variable['y'][period, location] * instance.catalogs[location][customer] for location in instance.locations) * variable['d1'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c6')

# ---------------------------------------------------------------------------

def create_c6A(instance, mip, variable):
    # Create constraint 6, part A, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= instance.limits[period][customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6A')

# ---------------------------------------------------------------------------

def create_c6B(instance, mip, variable):
    # Create constraint 6, part B, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= variable['d1'][period, customer] + instance.limits[period][customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6B')

# ---------------------------------------------------------------------------

def create_c6C(instance, mip, variable):
    # Create constraint 6, part C, linearized

    mip.addConstrs((variable['w'][period, location, customer] >=  -1 * instance.limits[period][customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6C')

# ---------------------------------------------------------------------------

def create_c6D(instance, mip, variable):
    # Create constraint 6, part D, linearized

    mip.addConstrs((variable['w'][period, location, customer] >= variable['d1'][period, customer] - 1 * instance.limits[period][customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6D')

# ---------------------------------------------------------------------------

def create_c7(instance, mip, variable):
    # Create constraint 7

    mip.addConstrs((sum(variable['z'][period1, period2, location, customer] for period1 in instance.periods_with_start if is_before(period1, period2)) == instance.catalogs[location][customer] * variable['y'][period2, location] for period2 in instance.periods for location in instance.locations for customer in instance.customers), name = 'c7')

# ---------------------------------------------------------------------------

def create_c8(instance, mip, variable):
    # Create constraint 8

    mip.addConstrs((sum(variable['z'].sum(period1, period2, '*', customer) for period1 in instance.periods_with_start if is_before(period1, period2)) == sum(variable['z'].sum(period2, period1, '*', customer) for period1 in instance.periods_with_end if is_after(period1, period2)) for period2 in instance.periods for customer in instance.customers), name = 'c8')

# ---------------------------------------------------------------------------

def create_c9(instance, mip, variable):
    # Create constraint 9

    mip.addConstrs((variable['z'].sum('0', '*', '*', customer) == 1 for customer in instance.customers), name = 'c9')

# ---------------------------------------------------------------------------

def create_c10(instance, mip, variable):
    # Create constraint 10

    mip.addConstrs((variable['z'].sum('*', str(len(instance.periods) + 1), '*', customer) == 1 for customer in instance.customers), name = 'c10')

# ---------------------------------------------------------------------------

def create_c11(instance, mip, variable, customer):
    # Create constraint 11, slave

    mip.addConstrs((variable['p'][period2, location] - variable['q'][period1] + variable['q'][period2]
                     >= instance.revenues[period2][location] * instance.partial_demand(period1, period2, customer)
                    for period1 in instance.periods_with_start for period2 in instance.periods for location in instance.locations 
                    if is_before(period1, period2) and instance.catalogs[location][customer] == 1.), name = 'c11a')

    mip.addConstrs((- variable['q'][period1] + variable['q'][instance.end] >= 0
                    for period1 in instance.periods_with_start), name = 'c11b')