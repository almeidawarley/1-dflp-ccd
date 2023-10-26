import gurobipy as gp

def previous(period):

    return str(int(period) - 1)

def map_catalog(instance, reference, customer):
    # Kind of deprecated, but may be useful

    return {
        (period, location) : instance.catalogs[location][customer] if period == reference else 0.
        for period in instance.periods
        for location in instance.locations
    }

def create_c1(instance, mip, variable):
    # Create constraint 1

    mip.addConstrs((variable['y'].sum(period, '*') <= 1 for period in instance.periods), name = 'c1')

# ---------------------------------------------------------------------------

def create_c2(instance, mip, variable):
    # Create constraint 2

    mip.addConstrs((variable['d3']['0', customer] == instance.starts[customer] for customer in instance.customers), name = 'c2')

# ---------------------------------------------------------------------------

def create_c3(instance, mip, variable):
    # Create constraint 3, linear

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
    # Create constraint 5, linearized

    mip.addConstrs((variable['d3'][period, customer] == variable['d2'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c5')

# ---------------------------------------------------------------------------

def create_c6_NL(instance, mip, variable):
    # Create constraint 6, nonlinear

    mip.addConstrs((variable['w'][period, customer] == sum([variable['y'][period, location] * instance.catalogs[location][customer] for location in instance.locations]) * variable['d1'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c6')

# ---------------------------------------------------------------------------

def create_c6A(instance, mip, variable):
    # Create constraint 6, part A, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= instance.limits[customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6A')

# ---------------------------------------------------------------------------

def create_c6B(instance, mip, variable):
    # Create constraint 6, part B, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= variable['d1'][period, customer] + instance.limits[customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6B')

# ---------------------------------------------------------------------------

def create_c6C(instance, mip, variable):
    # Create constraint 6, part C, linearized

    mip.addConstrs((variable['w'][period, location, customer] >=  -1 * instance.limits[customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6C')

# ---------------------------------------------------------------------------

def create_c6D(instance, mip, variable):
    # Create constraint 6, part D, linearized

    mip.addConstrs((variable['w'][period, location, customer] >= variable['d1'][period, customer] - 1 * instance.limits[customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6D')