import gurobipy as gp
import variables as vb
import formulation as fm
import instance as ic
import validation as vd

def previous(period):

    return str(int(period) - 1)

def create_vrb(instance, mip):
    # Create beta_{j} variables

    lowers = [0 for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.customers]
    coefs = [0.  for _ in instance.customers]
    types = ['C' for _ in instance.customers]
    names = [
        'b~{}'.format(customer)
        for customer in instance.customers
    ]

    return mip.addVars(instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrw(instance, mip):
    # Create w^{t}_{j} variables

    lowers = [0 for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.periods for _ in instance.customers]
    coefs = [0.  for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in instance.periods for _ in instance.customers]
    names = [
        'w~{}_{}'.format(period, customer)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrd(instance, mip):
    # Create delta_{j} variables

    lowers = [0 for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.customers]
    coefs = [0.  for _ in instance.customers]
    types = ['C' for _ in instance.customers]
    names = [
        'd~{}'.format(customer)
        for customer in instance.customers
    ]

    return mip.addVars(instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_vrd0(instance, mip):
    # Create D^0_{j} variables

    lowers = [0 for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in instance.customers]
    coefs = [0.  for _ in instance.customers]
    types = ['C' for _ in instance.customers]
    names = [
        'd0~{}'.format(customer)
        for customer in instance.customers
    ]

    return mip.addVars(instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

# ---------------------------------------------------------------------------

def create_c1(instance, mip, variable):
    # Create constraint 1

    mip.addConstrs((variable['d3']['0', customer] - variable['d0'][customer] == 0 for customer in instance.customers), name = 'c1')
    # mip.addConstrs((variable['d3']['0', customer] == 0 for customer in instance.customers), name = 'c1A')
    # mip.addConstrs((variable['d0'][customer] == 0 for customer in instance.customers), name = 'c1B')

# ---------------------------------------------------------------------------

def create_c2(instance, mip, variable):
    # Create constraint 2

    mip.addConstrs((variable['d3'][period, customer] == variable['d3'][previous(period), customer] + variable['b'][customer] - variable['w'][period, customer] for period in instance.periods for customer in instance.customers), name = 'c2')

# ---------------------------------------------------------------------------

def create_c3A(instance, mip, variable, indicators):
    # Create constraint 3, part A

    mip.addConstrs((variable['w'][period, customer] <= indicators[period][customer] * (variable['d'][customer]) for period in instance.periods for customer in instance.customers), name = 'c3A')

def create_c3B(instance, mip, variable, indicators):
    # Create constraint 3, part B

    mip.addConstrs((variable['w'][period, customer] <= indicators[period][customer] * (variable['d3'][previous(period), customer] + variable['b'][customer]) for period in instance.periods for customer in instance.customers), name = 'c3B')

def create_c3C(instance, mip, variable, indicators):
    # Create constraint 3, part C

    mip.addConstrs((variable['w'][period, customer] >= indicators[period][customer] * (variable['d'][customer] - instance.bigM[customer] * (1 - variable['u'][period, customer])) for period in instance.periods for customer in instance.customers), name = 'c3C')

def create_c3D(instance, mip, variable, indicators):
    # Create constraint 3, part D

    mip.addConstrs((variable['w'][period, customer] >= indicators[period][customer] * (variable['d3'][previous(period), customer] + variable['b'][customer] - instance.bigM[customer] * variable['u'][period, customer]) for period in instance.periods for customer in instance.customers), name = 'c3D')

# ---------------------------------------------------------------------------

def build_estimation(instance, training):
    # Build the estimation model

    mip = gp.Model('EST-1-DFLP-DRA')

    # Create decision variables
    variable = {
        'd3': vb.create_vrd3(instance, mip),
        'u': vb.create_vru(instance, mip),
        'w': create_vrw(instance, mip),
        'b': create_vrb(instance, mip),
        'd': create_vrd(instance, mip),
        'd0': create_vrd0(instance, mip)
    }

    # Minimize error
    mip.setAttr('ModelSense', +1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', 10 * 60 * 60)

    # Set squared error as objective
    mip.setObjective(sum([(variable['w'][period, customer] - training['w'][period][customer]) ** 2 for period in instance.periods for customer in instance.customers]))

    # Build indicators for constraints
    indicators = {}
    for period in instance.periods:
        indicators[period] = {}
        for customer in instance.customers:
            # In short, 1 if customer is captured during a period
            indicators[period][customer] = sum([training['y'][period][location] * instance.catalogs[location][customer] for location in instance.locations])

    # Create main constraints
    create_c1(instance, mip, variable)
    create_c2(instance, mip, variable)
    create_c3A(instance, mip, variable, indicators)
    create_c3B(instance, mip, variable, indicators)
    create_c3C(instance, mip, variable, indicators)
    create_c3D(instance, mip, variable, indicators)

    return mip, variable

# ---------------------------------------------------------------------------

# Read instance from file
instance = ic.instance('D-toy')
modified = ic.instance('D-toy')

# Reset lower and upper bounds
# Modify betas to make it harder to estimate
for customer in instance.customers:

    # instance.starts[customer] = 0
    instance.lowers[customer] = 0
    instance.uppers[customer] = 99

    # instance.betas[customer] = instance.deltas[customer] / 2
    # modified.betas[customer] = modified.deltas[customer] / 2

    # modified.starts[customer] = 0
    modified.lowers[customer] = 0
    modified.uppers[customer] = 99

# If D^0_j == 0 for the original instance, it takes less periods to estimate beta! (how many? characterize it!)
# If D^0_j != 0 for the original instance, jt takes more periods to estimate beta! (how many? characterize it!)

instance.print_instance()

# Build 1-DFLP-RA model
mip, variable = fm.build_linearized(instance)
'''
try:
    for period in instance.periods:
        mip.addConstr(variable['y'][period, period] == 1)
except Exception as e:
    print('Not able to add one of the constraints')
    print('Error message: {}'.format(e))
'''
# Find optimal solution
mip.optimize()
org_solution = fm.format_solution(instance, mip, variable)

# Prepare training data
training = {}
training['w'] = {}
training['y'] = {}

for period in instance.periods:
    training['w'][period] = {}
    training['y'][period] = {}
    for customer in instance.customers:
        training['w'][period][customer] = sum([variable['w'][period, location, customer].x for location in instance.locations])
        if training['w'][period][customer] > 0.:
            print('| captured {} units from customer {} in period {}'.format(training['w'][period][customer], customer, period))
    for location in instance.locations:
        training['y'][period][location] = variable['y'][period, location].x
        if training['y'][period][location] > 0.:
            print('| visited location {} in period {}'.format(location, period))

# Build EST-1-DFL-RA model
est, variable = build_estimation(instance, training)
for customer in instance.customers:
    est.addConstr(variable['d0'][customer] == instance.starts[customer])
# Find optimal parameters
est.optimize()

# est.write('est.lp')

for customer in instance.customers:
    print('For customer {}...'.format(customer))

    print('| D^0: {}'.format(variable['d0'][customer].x))
    print('| Beta: {}'.format(variable['b'][customer].x))
    print('| Delta: {}'.format(variable['d'][customer].x))

# Set estimated parameters
for customer in instance.customers:
    modified.starts[customer] = variable['d0'][customer].x
    modified.alphas[customer] = 0.
    modified.betas[customer] = variable['b'][customer].x
    modified.gammas[customer] = 0.
    modified.deltas[customer] = variable['d'][customer].x

# Build 1-DFLP-RA model
mip, variable = fm.build_linearized(modified)
# Find optimal solution
mip.optimize()
est_solution = fm.format_solution(modified, mip, variable)

print('Optimal to original instance [{}]: {}'.format(vd.evaluate_solution(instance, org_solution), org_solution))
print('Original to estimated instance [{}]: {}'.format(vd.evaluate_solution(instance, est_solution), est_solution))