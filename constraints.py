def previous(period):

    return str(int(period) - 1)

def map_catalog(instance, reference, customer):

    return {
        (period, location) : instance.catalogs[location][customer] if period == reference else 0.
        for period in instance.periods
        for location in instance.locations
    }

def create_c1(instance, model, variable):
    # Create constraint 1

    model.addConstrs((variable['ys'].sum(period, '*') <= 1 for period in instance.periods), name = 'c1')

# ---------------------------------------------------------------------------

def create_c2(instance, model, variable):
    # Create constraint 2

    model.addConstrs((variable['d2s']['0', customer] == instance.starts[customer] for customer in instance.customers), name = 'c2')

# ---------------------------------------------------------------------------

def create_c3(instance, model, variable):
    # Create constraint 3

    model.addConstrs((variable['d1s'][period, customer] <= (1 + instance.alphas[customer]) * variable['d2s'][previous(period), customer] + instance.betas[customer] for period in instance.periods for customer in instance.customers), name = 'c3')

# ---------------------------------------------------------------------------

def create_c4(instance, model, variable):
    # Create constraint 4

    model.addConstrs((variable['d1s'][period, customer] <= instance.uppers[customer] for period in instance.periods for customer in instance.customers), name = 'c4')

# ---------------------------------------------------------------------------

def create_c5(instance, model, variable):
    # Create constraint 5

    model.addConstrs((variable['d1s'][period, customer] >= variable['d2s'][previous(period), customer] for period in instance.periods for customer in instance.customers), name = 'c5')

# ---------------------------------------------------------------------------

def create_c6(instance, model, variable):
    # Create constraint 6

    model.addConstrs((variable['d2s'][period, customer] <= variable['d1s'][period, customer] - variable['ws'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c6')

# ---------------------------------------------------------------------------

def create_c7(instance, model, variable):
    # Create constraint 7

    model.addConstrs((variable['d2s'][period, customer] >= instance.lowers[customer] for period in instance.periods for customer in instance.customers), name = 'c7')

# ---------------------------------------------------------------------------

def create_c8(instance, model, variable):
    # Create constraint 8

    model.addConstrs((variable['d2s'][period, customer] <= variable['d1s'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c8')

# ---------------------------------------------------------------------------

def create_c9(instance, model, variable):
    # Create constraint 9

    model.addConstrs((variable['ws'][period, customer] <= variable['d1s'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c9')

# ---------------------------------------------------------------------------

def create_c10(instance, model, variable):
    # Create constraint 10

    model.addConstrs((variable['ws'][period, customer] <= 100000 * (variable['ys'].prod(map_catalog(instance, period, customer))) for period in instance.periods for customer in instance.customers), name = 'c10')

# ---------------------------------------------------------------------------

def create_c11(instance, model, variable):
    # Create constraint 11

    model.addConstrs((variable['ws'][period, customer] <= instance.gammas[customer] * variable['d1s'][period, customer] + instance.deltas[customer] + 100000 * (1 - variable['ys'].prod(map_catalog(instance, period, customer))) for period in instance.periods for customer in instance.customers), name = 'c11')