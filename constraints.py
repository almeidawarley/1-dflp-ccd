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

def create_c3_NL(instance, mip, variable):
    # Create constraint 3, nonlinear

    mip.addConstrs((variable['d1'][period, customer] == gp.min_(variable['o'][period, customer], instance.uppers[customer]) for period in instance.periods for customer in instance.customers), name = 'c3_p1')
    mip.addConstrs((variable['o'][period, customer] == (1 + instance.alphas[customer]) * variable['d3'][previous(period), customer] + instance.betas[customer] for period in instance.periods for customer in instance.customers), name = 'c3_p2')

def create_c3A(instance, mip, variable):
    # Create constraint 3, part A, linearized

    mip.addConstrs((variable['d1'][period, customer] <= instance.uppers[customer] for period in instance.periods for customer in instance.customers), name = 'c3A')

# ---------------------------------------------------------------------------

def create_c3B(instance, mip, variable):
    # Create constraint 3, part B, linearized

    mip.addConstrs((variable['d1'][period, customer] <= (1 + instance.alphas[customer]) * variable['d3'][previous(period), customer] + instance.betas[customer] for period in instance.periods for customer in instance.customers), name = 'c3B')

# ---------------------------------------------------------------------------

def create_c3C(instance, mip, variable):
    # Create constraint 3, part C, linearized

    mip.addConstrs((variable['d1'][period, customer] >= instance.uppers[customer] - instance.bigM[customer] * (1 - variable['s'][period, customer]) for period in instance.periods for customer in instance.customers), name = 'c3C')

# ---------------------------------------------------------------------------

def create_c3D(instance, mip, variable):
    # Create constraint 3, part D, linearized

    mip.addConstrs((variable['d1'][period, customer] >= (1 + instance.alphas[customer]) * variable['d3'][previous(period), customer] + instance.betas[customer] - instance.bigM[customer] * variable['s'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c3D')

# ---------------------------------------------------------------------------

def create_c4(instance, mip, variable):
    # Create constraint 4, linearized

    mip.addConstrs((variable['d2'][period, customer] == variable['d1'][period, customer] - variable['w'].sum(period, '*', customer) for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c4_NL(instance, mip, variable):
    # Create constraint 4, nonlinear

    mip.addConstrs((variable['d2'][period, customer] == variable['d1'][period, customer] - variable['w'].sum(period, customer) for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c5_NL(instance, mip, variable):
    # Create constraint 5, nonlinear

    mip.addConstrs((variable['d3'][period, customer] == gp.max_(variable['d2'][period, customer], instance.lowers[customer]) for period in instance.periods for customer in instance.customers), name = 'c5')

# ---------------------------------------------------------------------------

def create_c5A(instance, mip, variable):
    # Create constraint 5, part A, linearized

    mip.addConstrs((variable['d3'][period, customer] >= instance.lowers[customer] for period in instance.periods for customer in instance.customers), name = 'c5A')

# ---------------------------------------------------------------------------

def create_c5B(instance, mip, variable):
    # Create constraint 5, part B, linearized

    mip.addConstrs((variable['d3'][period, customer] >= variable['d2'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c5B')

# ---------------------------------------------------------------------------

def create_c5C(instance, mip, variable):
    # Create constraint 5, part C, linearized

    mip.addConstrs((variable['d3'][period, customer] <= instance.lowers[customer] + instance.bigM[customer] * (1 - variable['t'][period, customer]) for period in instance.periods for customer in instance.customers), name = 'c5C')

# ---------------------------------------------------------------------------

def create_c5D(instance, mip, variable):
    # Create constraint 5, part D, linearized

    mip.addConstrs((variable['d3'][period, customer] <= variable['d2'][period, customer] + instance.bigM[customer] * variable['t'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c5D')

# ---------------------------------------------------------------------------

def create_c6_NL(instance, mip, variable):
    # Create constraint 6, nonlinear

    mip.addConstrs(((variable['r'][period, customer] == 1) >> (variable['w'][period, customer] == variable['q'][period, customer]) for period in instance.periods for customer in instance.customers), name = 'c6_p1')
    mip.addConstrs(((variable['r'][period, customer] == 0) >> (variable['w'][period, customer] == 0) for period in instance.periods for customer in instance.customers), name = 'c6_p2')

    mip.addConstrs((variable['p'][period, customer] == instance.gammas[customer] * variable['d1'][period, customer] + instance.deltas[customer] for period in instance.periods for customer in instance.customers), name = 'c6_p3')
    mip.addConstrs((variable['q'][period, customer] == gp.min_(variable['p'][period, customer], variable['d1'][period, customer]) for period in instance.periods for customer in instance.customers), name = 'c6_p4')
    mip.addConstrs((variable['r'][period, customer] == sum([variable['y'][period, location] * instance.catalogs[location][customer] for location in instance.locations]) for period in instance.periods for customer in instance.customers), name = 'c6_p5')

# ---------------------------------------------------------------------------

def create_c6A(instance, mip, variable):
    # Create constraint 6, part A, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= instance.bigM[customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6A')

# ---------------------------------------------------------------------------

def create_c6B(instance, mip, variable):
    # Create constraint 6, part B, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= variable['v'][period, customer] + instance.bigM[customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6B')

# ---------------------------------------------------------------------------

def create_c6C(instance, mip, variable):
    # Create constraint 6, part C, linearized

    mip.addConstrs((variable['w'][period, location, customer] >=  -1 * instance.bigM[customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6C')

# ---------------------------------------------------------------------------

def create_c6D(instance, mip, variable):
    # Create constraint 6, part D, linearized

    mip.addConstrs((variable['w'][period, location, customer] >= variable['v'][period, customer] - 1 * instance.bigM[customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6D')

# ---------------------------------------------------------------------------

def create_c6E(instance, mip, variable):
    # Create constraint 6, part E, linearized

    mip.addConstrs((variable['v'][period, customer] <= variable['d1'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c6E')

# ---------------------------------------------------------------------------

def create_c6F(instance, mip, variable):
    # Create constraint 6, part F, linearized

    mip.addConstrs((variable['v'][period, customer] <= instance.gammas[customer] * variable['d1'][period, customer] + instance.deltas[customer] for period in instance.periods for customer in instance.customers), name = 'c6F')

# ---------------------------------------------------------------------------

def create_c6G(instance, mip, variable):
    # Create constraint 6, part G, linearized

    mip.addConstrs((variable['v'][period, customer] >= variable['d1'][period, customer] - instance.bigM[customer] * (1 - variable['u'][period, customer]) for period in instance.periods for customer in instance.customers), name = 'c6G')

# ---------------------------------------------------------------------------

def create_c6H(instance, mip, variable):
    # Create constraint 6, part H, linearized

    mip.addConstrs((variable['v'][period, customer] >= instance.gammas[customer] * variable['d1'][period, customer] + instance.deltas[customer] - instance.bigM[customer] * variable['u'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c6H')