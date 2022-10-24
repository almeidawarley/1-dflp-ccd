import gurobipy as gp

def name_vry(period, location):
    # Name y^{t}_{i} variables

    return 'y~{}_{}'.format(period, location)

def create_vry(instance, model):
    # Create y^{t}_{i} variables

    lowers = [0. for _ in instance.periods for _ in instance.locations]
    uppers = [1. for _ in instance.periods for _ in instance.locations]
    coefs = [0. for _ in instance.periods for _ in instance.locations]
    types = ['B' for _ in instance.periods for _ in instance.locations]
    names = [
        name_vry(period, location)
        for period in instance.periods
        for location in instance.locations
    ]

    return model.addVars(instance.periods, instance.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

def split_vry(name):
    # Split y^{t}_{i} information

    # Order: period, location
    return name.split('_')[1:]

# ---------------------------------------------------------------------------

def name_vrw(period, customer):
    # Name w^{t}_{j} variables

    return 'w~{}_{}'.format(period, customer)

def create_vrw(instance, model):
    # Create w^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [
        sum(1. * instance.revenues[period][location] * instance.catalogs[location][customer] for location in instance.locations)
        for period in instance.periods
        for customer in instance.customers
    ]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        name_vrw(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return model.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

def split_vrw(name):
    # Split w^{t}_{j} information

    # Order: period, customer
    return name.split('_')[1:]

# ---------------------------------------------------------------------------

def name_vrd1(period, customer):
    # Name d1^{t}_{j} variables

    return 'd1~{}_{}'.format(period, customer)

def create_vrd1(instance, model):
    # Create d1^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        name_vrd1(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return model.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

def split_vrd1(name):
    # Split d1^{t}_{j} information

    # Order: period, customer
    return name.split('_')[1:]

# ---------------------------------------------------------------------------

def name_vrd2(period, customer):
    # Name d2^{t}_{j} variables

    return 'd2~{}_{}'.format(period, customer)

def create_vrd2(instance, model):
    # Create d2^{t}_{j} variables

    lowers = [0. for _ in ['0'] + instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in ['0'] + instance.periods for _ in instance.customers]
    coefs = [0. for _ in ['0'] + instance.periods for _ in instance.customers]
    types = ['C' for _ in ['0'] + instance.periods for _ in instance.customers]
    names = [
        name_vrd2(period, customer)
        for period in ['0'] + instance.periods
        for customer in instance.customers
    ]

    return model.addVars(['0'] + instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

def split_vrd2(name):
    # Split d2^{t}_{j} information

    # Order: period, customer
    return name.split('_')[1:]