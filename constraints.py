def create_c1(instance, mip, variable):
    # Create constraint 1

    mip.addConstrs((variable['y'].sum(period, '*') <= 1 for period in instance.periods), name = 'c1')

# ---------------------------------------------------------------------------

def create_c2(instance, mip, variable):
    # Create constraint 2

    mip.addConstrs((variable['b']['0', customer] == instance.starts[customer] for customer in instance.customers), name = 'c2')

# ---------------------------------------------------------------------------

def create_c3(instance, mip, variable):
    # Create constraint 3

    mip.addConstrs((variable['c'][period, customer] == (1 + instance.alphas[customer]) * variable['b'][instance.previous_period(period), customer] + instance.betas[customer] for period in instance.periods for customer in instance.customers), name = 'c3')

# ---------------------------------------------------------------------------

def create_c4(instance, mip, variable):
    # Create constraint 4, linearized

    mip.addConstrs((variable['b'][period, customer] == variable['c'][period, customer] - variable['w'].sum(period, '*', customer) for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c4_NL(instance, mip, variable):
    # Create constraint 4, nonlinear

    mip.addConstrs((variable['b'][period, customer] == variable['c'][period, customer] - variable['w'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c5_NL(instance, mip, variable):
    # Create constraint 6, nonlinear

    mip.addConstrs((variable['w'][period, customer] == sum(variable['y'][period, location] * instance.catalogs[location][customer] for location in instance.locations) * variable['c'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c5')

# ---------------------------------------------------------------------------

def create_c5A(instance, mip, variable):
    # Create constraint 5, part A, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= instance.limits[period][customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c5A')

# ---------------------------------------------------------------------------

def create_c5B(instance, mip, variable):
    # Create constraint 5, part B, linearized

    mip.addConstrs((variable['w'][period, location, customer] <= variable['c'][period, customer] + instance.limits[period][customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c5B')

# ---------------------------------------------------------------------------

def create_c5C(instance, mip, variable):
    # Create constraint 5, part C, linearized

    mip.addConstrs((variable['w'][period, location, customer] >=  -1 * instance.limits[period][customer] * instance.catalogs[location][customer] * variable['y'][period, location] for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c5C')

# ---------------------------------------------------------------------------

def create_c5D(instance, mip, variable):
    # Create constraint 5, part D, linearized

    mip.addConstrs((variable['w'][period, location, customer] >= variable['c'][period, customer] - 1 * instance.limits[period][customer] * (1 - instance.catalogs[location][customer] * variable['y'][period, location]) for period in instance.periods for location in instance.locations for customer in instance.customers), name = 'c5D')

# ---------------------------------------------------------------------------

def create_c6(instance, mip, variable):
    # Create constraint 6

    mip.addConstrs((sum(variable['z'][period1, period2, location, customer] for period1 in instance.periods_with_start if instance.is_before(period1, period2)) == instance.catalogs[location][customer] * variable['y'][period2, location] for period2 in instance.periods for location in instance.locations for customer in instance.customers), name = 'c6')

# ---------------------------------------------------------------------------

def create_c7(instance, mip, variable):
    # Create constraint 7

    mip.addConstrs((sum(variable['z'].sum(period1, period2, '*', customer) for period1 in instance.periods_with_start if instance.is_before(period1, period2)) == sum(variable['z'].sum(period2, period1, '*', customer) for period1 in instance.periods_with_end if instance.is_after(period1, period2)) for period2 in instance.periods for customer in instance.customers), name = 'c7')

# ---------------------------------------------------------------------------

def create_c8(instance, mip, variable):
    # Create constraint 8

    mip.addConstrs((variable['z'].sum('0', '*', '*', customer) == 1 for customer in instance.customers), name = 'c8')

# ---------------------------------------------------------------------------

def create_c9(instance, mip, variable, customer):
    # Create constraint 9, slave

    mip.addConstrs((variable['p'][period2, location] + variable['q'][period1] - variable['q'][period2]
                     >= instance.revenues[period2][location] * instance.accumulated_demand(period1, period2, customer)
                    for period1 in instance.periods_with_start for period2 in instance.periods for location in instance.locations
                    if instance.is_before(period1, period2) and instance.catalogs[location][customer] == 1.), name = 'c9')