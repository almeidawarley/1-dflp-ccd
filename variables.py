import gurobipy as gp

def create_vry(instance, mip):
    # Create y^{t}_{i} variables

    lowers = [0. for _ in instance.periods for _ in instance.locations]
    uppers = [1. for _ in instance.periods for _ in instance.locations]
    coefs = [0. for _ in instance.periods for _ in instance.locations]
    types = ['B' for _ in instance.periods for _ in instance.locations]
    names = [
        'y~{}_{}'.format(period, location)
        for period in instance.periods
        for location in instance.locations
    ]

    return mip.addVars(instance.periods, instance.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrw(instance, mip):
    # Create w^{t}_{ij} variables

    lowers = [0 for _ in instance.periods for _ in instance.locations for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.locations for _ in instance.customers]
    coefs = [0 for _ in instance.periods for _ in instance.locations for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.locations for _ in instance.customers]
    names = [
        'w~{}_{}_{}'.format(period, location, customer)
        for period in instance.periods
        for location in instance.locations
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.locations, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrw_NL(instance, mip):
    # Create w^{t}_{j} variables

    lowers = [0 for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0 for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'w~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrd3(instance, mip):
    # Create d3^{t}_{j} variables

    lowers = [0. for _ in ['0'] + instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in ['0'] + instance.periods for _ in instance.customers]
    coefs = [0. for _ in ['0'] + instance.periods for _ in instance.customers]
    types = ['C' for _ in ['0'] + instance.periods for _ in instance.customers]
    names = [
        'd3~{}_{}'.format(period, customer)
        for period in ['0'] + instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(['0'] + instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrd1(instance, mip):
    # Create d1^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'd1~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrd2(instance, mip):
    # Create d2^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'd2~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrz_1(instance, mip):
    # Create z^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [1. for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'z~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrz_2(instance, mip):
    # Create z^{kt}_{ij} variables

    lowers = [0. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    uppers = [1. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    coefs = [0. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    types = ['B' for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    names = [
        'z~{}_{}_{}_{}'.format(period1, period2, location, customer)
        for period1 in instance.periods_with_start
        for period2 in instance.periods_with_end
        for location in instance.locations
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods_with_start, instance.periods_with_end, instance.locations, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrz_3(instance, mip):
    # Create z^{kt}_{j} variables

    lowers = [0. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.customers]
    uppers = [1. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.customers]
    coefs = [0. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.customers]
    types = ['B' for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.customers]
    names = [
        'z~{}_{}_{}'.format(period1, period2, customer)
        for period1 in instance.periods_with_start
        for period2 in instance.periods_with_end
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods_with_start, instance.periods_with_end, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)