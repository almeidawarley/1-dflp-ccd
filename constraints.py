def previous(period):

    return str(int(period) - 1)

def map_catalog(instance, reference, customer):

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
    # Create constraint 3

    mip.addConstrs((variable['d1'][period, customer] <= (1 + instance.alphas[customer]) * variable['d3'][previous(period), customer] + instance.betas[customer] for period in instance.periods for customer in instance.customers), name = 'c3')

# ---------------------------------------------------------------------------

def create_c4(instance, mip, variable):
    # Create constraint 4

    mip.addConstrs((variable['d1'][period, customer] <= instance.uppers[customer] for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c5(instance, mip, variable):
    # Create constraint 5

    mip.addConstrs((variable['d2'][period, customer] == variable['d1'][period, customer] - variable['w'].sum(period, '*', customer) for period in instance.periods for customer in instance.customers), name = 'c5')

# ---------------------------------------------------------------------------

def create_c6(instance, mip, variable):
    # Create constraint 6

    mip.addConstrs((variable['d3'][period, customer] <= instance.lowers[customer] + instance.uppers[customer] * (1 - variable['z'][period, customer]) for period in instance.periods for customer in instance.customers), name = 'c6')

# ---------------------------------------------------------------------------

def create_c7(instance, mip, variable):
    # Create constraint 7

    mip.addConstrs((variable['d3'][period, customer] <= variable['d2'][period, customer] + instance.uppers[customer] * variable['z'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c7')

# ---------------------------------------------------------------------------

def create_c8(instance, mip, variable):
    # Create constraint 8

    mip.addConstrs((variable['w'][period, location, customer] <= instance.uppers[customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c8')

# ---------------------------------------------------------------------------

def create_c9(instance, mip, variable):
    # Create constraint 9

    mip.addConstrs((variable['w'][period, location, customer] <= instance.gammas[customer] * variable['d1'][period, customer] + instance.deltas[customer] + instance.uppers[customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c9')


# ---------------------------------------------------------------------------

def create_c10(instance, mip, variable):
    # Create constraint 10

    mip.addConstrs((variable['w'][period, location, customer] >=  -1 * instance.uppers[customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c10')

# ---------------------------------------------------------------------------

def create_c11(instance, mip, variable):
    # Create constraint 11

    mip.addConstrs((variable['w'][period, location, customer] >= instance.gammas[customer] * variable['d1'][period, customer] + instance.deltas[customer] - 1 * instance.uppers[customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c11')