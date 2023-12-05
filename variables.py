import gurobipy as gp

# ---------------------------------------------------------------------------

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

def create_vry_3(instance, mip):
    # Create y^{t}_{ki} variables

    lowers = [0. for _ in instance.periods_with_start for _ in instance.locations_extended for _ in instance.locations_extended]
    uppers = [1. for _ in instance.periods_with_start for _ in instance.locations_extended for _ in instance.locations_extended]
    coefs = [0. for _ in instance.periods_with_start for _ in instance.locations_extended for _ in instance.locations_extended]
    types = ['B' for _ in instance.periods_with_start for _ in instance.locations_extended for _ in instance.locations_extended]
    names = [
        'y~{}_{}_{}'.format(period, location, destination)
        for period in instance.periods_with_start
        for location in instance.locations_extended
        for destination in instance.locations_extended
    ]

    return mip.addVars(instance.periods_with_start, instance.locations_extended, instance.locations_extended, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

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

def create_vrw_2(instance, mip):
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

    lowers = [0. for _ in instance.periods_with_start for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods_with_start for _ in instance.customers]
    coefs = [0. for _ in instance.periods_with_start for _ in instance.customers]
    types = ['C' for _ in instance.periods_with_start for _ in instance.customers]
    names = [
        'd3~{}_{}'.format(period, customer)
        for period in instance.periods_with_start
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods_with_start, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

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

def create_vrz_4(instance, mip):
    # Create z^{kt}_{ij} variables

    lowers = [0. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    uppers = [1. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    coefs = [0. for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    types = ['C' for _ in instance.periods_with_start for _ in instance.periods_with_end for _ in instance.locations for _ in instance.customers]
    names = [
        'z~{}_{}_{}_{}'.format(period1, period2, location, customer)
        for period1 in instance.periods_with_start
        for period2 in instance.periods_with_end
        for location in instance.locations
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods_with_start, instance.periods_with_end, instance.locations, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrv(instance, mip):
    # Create v_{j} variables

    lowers = [0. for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.customers]
    coefs = [0. for _ in instance.customers]
    types = ['C' for _ in instance.customers]
    names = [
        'v~{}'.format(customer)
        for customer in instance.customers
    ]

    return mip.addVars(instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrp(instance, mip):
    # Create p^{t}_{i} variables

    lowers = [-gp.GRB.INFINITY for _ in instance.periods for _ in instance.locations]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.locations]
    coefs = [0. for _ in instance.periods for _ in instance.locations]
    types = ['C' for _ in instance.periods for _ in instance.locations]
    names = [
        'p~{}_{}'.format(period, location)
        for period in instance.periods
        for location in instance.locations
    ]

    return mip.addVars(instance.periods, instance.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrq(instance, mip):
    # Create q^{t} variables

    lowers = [0 for _ in instance.periods_with_start]
    uppers = [gp.GRB.INFINITY for _ in instance.periods_with_start]
    coefs = [0. for _ in instance.periods_with_start]
    types = ['C' for _ in instance.periods_with_start]
    names = [
        'q~{}'.format(period)
        for period in instance.periods_with_start
    ]

    return mip.addVars(instance.periods_with_start, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)