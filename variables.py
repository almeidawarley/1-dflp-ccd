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

def create_vro(instance, mip):
    # Create o^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'o~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrp(instance, mip):
    # Create p^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'p~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrq(instance, mip):
    # Create q^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'q~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrr(instance, mip):
    # Create r^{t}_{ij} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [1 for _ in instance.periods  for _ in instance.customers]
    coefs = [0. for _ in instance.periods  for _ in instance.customers]
    types = ['B' for _ in instance.periods  for _ in instance.customers]
    names = [
        'r~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrs(instance, mip):
    # Create s^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [1 for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['B' for _ in instance.periods for _ in instance.customers]
    names = [
        's~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrt(instance, mip):
    # Create t^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [1 for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['B' for _ in instance.periods for _ in instance.customers]
    names = [
        't~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vru(instance, mip):
    # Create u^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [1 for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['B' for _ in instance.periods for _ in instance.customers]
    names = [
        'u~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrv(instance, mip):
    # Create v^{t}_{j} variables

    lowers = [0. for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'v~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)