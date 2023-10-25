import gurobipy as gp
import variables as vb
import formulation as fm
import instance as ic
import validation as vd
import pandas as pd
import os

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

def create_vrw(instance, mip, episodes):
    # Create w^{et}_{j} variables

    lowers = [0 for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    coefs = [0.  for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    types = ['C' for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    names = [
        'w~{}_{}_{}'.format(episode, period, customer)
        for episode in range(episodes)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(list(range(episodes)), instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

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

def create_c1(instance, mip, variable, episodes):
    # Create constraint 1

    mip.addConstrs((variable['d3'][episode, '0', customer] - variable['d0'][customer] == 0 for episode in range(episodes) for customer in instance.customers), name = 'c1')
    # mip.addConstrs((variable['d0'][customer] == instance.starts[customer] for customer in instance.customers), name = 'c1A')

# ---------------------------------------------------------------------------

def create_c2(instance, mip, variable, episodes):
    # Create constraint 2

    mip.addConstrs((variable['d3'][episode, period, customer] == variable['d3'][episode, previous(period), customer] + variable['b'][customer] - variable['w'][episode, period, customer] for episode in range(episodes) for period in instance.periods for customer in instance.customers), name = 'c2')

# ---------------------------------------------------------------------------

def create_c3A(instance, mip, variable, indicators, episodes):
    # Create constraint 3, part A

    mip.addConstrs((variable['w'][episode, period, customer] <= indicators[episode][period][customer] * (variable['d'][customer]) for episode in range(episodes) for period in instance.periods for customer in instance.customers), name = 'c3A')

def create_c3B(instance, mip, variable, indicators, episodes):
    # Create constraint 3, part B

    mip.addConstrs((variable['w'][episode, period, customer] <= indicators[episode][period][customer] * (variable['d3'][episode, previous(period), customer] + variable['b'][customer]) for episode in range(episodes) for period in instance.periods for customer in instance.customers), name = 'c3B')

def create_c3C(instance, mip, variable, indicators, episodes):
    # Create constraint 3, part C

    mip.addConstrs((variable['w'][episode, period, customer] >= indicators[episode][period][customer] * (variable['d'][customer] - instance.limits[customer] * (1 - variable['u'][episode, period, customer])) for episode in range(episodes) for period in instance.periods for customer in instance.customers), name = 'c3C')

def create_c3D(instance, mip, variable, indicators, episodes):
    # Create constraint 3, part D

    mip.addConstrs((variable['w'][episode, period, customer] >= indicators[episode][period][customer] * (variable['d3'][episode, previous(period), customer] + variable['b'][customer] - instance.limits[customer] * variable['u'][episode, period, customer]) for episode in range(episodes) for period in instance.periods for customer in instance.customers), name = 'c3D')

# ---------------------------------------------------------------------------

def create_vrd3(instance, mip, episodes):
    # Create d3^{et}_{j} variables

    lowers = [0. for _ in range(episodes) for _ in ['0'] + instance.periods for _ in instance.customers]
    uppers = [gp.GRB.INFINITY for _ in range(episodes) for _ in ['0'] + instance.periods for _ in instance.customers]
    coefs = [0. for _ in range(episodes) for _ in ['0'] + instance.periods for _ in instance.customers]
    types = ['C' for _ in range(episodes) for _ in ['0'] + instance.periods for _ in instance.customers]
    names = [
        'd3~{}_{}_{}'.format(episode, period, customer)
        for episode in range(episodes)
        for period in ['0'] + instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(list(range(episodes)), ['0'] + instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

def create_vru(instance, mip, episodes):
    # Create u^{et}_{j} variables

    lowers = [0. for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    uppers = [1 for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    coefs = [0. for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    types = ['B' for _ in range(episodes) for _ in instance.periods for _ in instance.customers]
    names = [
        'u~{}_{}_{}'.format(episode, period, customer)
        for episode in range(episodes)
        for period in instance.periods
        for customer in instance.customers
    ]

    return mip.addVars(list(range(episodes)), instance.periods, instance.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)


# ---------------------------------------------------------------------------

def build_estimation(instance, training):
    # Build the estimation model

    mip = gp.Model('EST-1-DFLP-DRA')

    # Create decision variables
    variable = {
        'd3': create_vrd3(instance, mip, len(training)),
        'u': create_vru(instance, mip, len(training)),
        'w': create_vrw(instance, mip, len(training)),
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
    mip.setObjective(sum([(variable['w'][episode, period, customer] - training[episode]['w'][period][customer]) ** 2 for episode in range(len(training)) for period in instance.periods for customer in instance.customers]))

    # Build indicators for constraints
    indicators = {}
    for episode in range(len(training)):
        indicators[episode] = {}
        for period in instance.periods:
            indicators[episode][period] = {}
            for customer in instance.customers:
                # In short, 1 if customer is captured during a period in some episode
                indicators[episode][period][customer] = sum([training[episode]['y'][period][location] * instance.catalogs[location][customer] for location in instance.locations])

    # Create main constraints
    create_c1(instance, mip, variable, len(training))
    create_c2(instance, mip, variable, len(training))
    create_c3A(instance, mip, variable, indicators, len(training))
    create_c3B(instance, mip, variable, indicators, len(training))
    create_c3C(instance, mip, variable, indicators, len(training))
    create_c3D(instance, mip, variable, indicators, len(training))

    return mip, variable

# ---------------------------------------------------------------------------

# Read instance from file
instance = ic.instance('1toN', 'est')
modified = ic.instance('1toN', 'est')
instance.print_instance()

# Prepare training data
training = {}
episodes = 0

for file in os.listdir('episodes/training'):

    content = pd.read_csv('episodes/training/{}'.format(file))
    training[episodes] = {}

    training[episodes]['w'] = {}
    training[episodes]['y'] = {}

    for period in instance.periods:
        training[episodes]['w'][period] = {}
        training[episodes]['y'][period] = {}
        for customer in instance.customers:
            training[episodes]['w'][period][customer] = content[(content['j'] == int(customer)) & (content['t'] == int(period))].iloc[0]['w']
        for location in instance.locations:
            training[episodes]['y'][period][location] = 1. if int(location) == content[(content['j'] == int(customer)) & (content['t'] == int(period))].iloc[0]['i'] else 0.

    episodes += 1

# Build EST-1-DFL-RA model
est, variable = build_estimation(instance, training)
# Find optimal parameters
est.optimize()

est.write('est.lp')

for customer in instance.customers:
    print('For customer {}...'.format(customer))

    print('| D^0: {} vs {}'.format(variable['d0'][customer].x, instance.starts[customer]))
    print('| Beta: {} vs {}'.format(variable['b'][customer].x, instance.betas[customer]))
    print('| Delta: {} vs {}'.format(variable['d'][customer].x, instance.deltas[customer]))

for customer in instance.customers:
    print('For customer {}...'.format(customer))

    modified.starts[customer] = variable['d0'][customer].x
    modified.betas[customer] = variable['b'][customer].x
    modified.deltas[customer] = variable['d'][customer].x
    modified.alphas[customer] = 0.
    modified.gammas[customer] = 0.

'''
mip2, variable2 = fm.build_linearized(modified)
mip2.optimize()
mip2_solution = fm.format_solution(modified, mip2, variable2)

fm.warm_start(instance, variable2, mip2_solution)

mip, variable = fm.build_fancy(instance)
mip.optimize()
mip_solution = fm.format_solution(instance, mip, variable)
'''


ml1_solution = {'1': '8', '2': '7', '3': '8', '4': '7' , '5': '8',  '6': '7', '7': '9', '8': '1', '9': '1', '10': '1', '11': '1', '12': '1', '13': '1', '14': '1', '15': '1', '16': '1', '17': '3', '18': '1', '19': '4', '20': '1'}
ml2_solution = {'1': '1', '2': '1', '3': '1', '4': '1' , '5': '1',  '6': '1', '7': '1', '8': '1', '9': '1', '10': '1', '11': '1', '12': '1', '13': '1', '14': '1', '15': '1', '16': '1', '17': '1', '18': '1', '19': '1', '20': '1'}
ml3_solution = {'1': '5', '2': '8', '3': '5', '4': '5', '5': '5', '6': '5', '7': '5', '8': '2', '9': '2', '10': '5', '11': '4', '12': '7', '13': '10', '14': '10', '15': '10', '16': '3', '17': '3', '18': '1', '19': '1', '20': '1'}

# print('MIP1: {}'.format('-'.join(mip_solution.values())))
# print('MIP2: {}'.format('-'.join(mip2_solution.values())))
# print('MIP3: {}'.format('-'.join(ml1_solution.values())))
# print('MIP4: {}'.format('-'.join(ml2_solution.values())))
# print('MIP5: {}'.format('-'.join(ml3_solution.values())))

# print(vd.evaluate_solution(instance, mip_solution))
# print(vd.evaluate_solution(instance, mip2_solution))
# print(vd.evaluate_solution(instance, ml1_solution))
# print(vd.evaluate_solution(instance, ml2_solution))
# print(vd.evaluate_solution(instance, ml3_solution))

ml4_solution = {'1': '0', '2': '0', '3': '0', '4': '0', '5': '0', '6': '0', '7': '0', '8': '2', '9': '2', '10': '8', '11': '3', '12': '7', '13': '10', '14': '2', '15': '2', '16': '3', '17': '1', '18': '1', '19': '1', '20': '1'}
ml5_solution = {'1': '9', '2': '6', '3': '5', '4': '5', '5': '0', '6': '0', '7': '8', '8': '5', '9': '8', '10': '8', '11': '8', '12': '4', '13': '4', '14': '1', '15': '1', '16': '1', '17': '1', '18': '1', '19': '1', '20': '1'}
ml6_solution = {'1': '1', '2': '1', '3': '10', '4': '1', '5': '3', '6': '1', '7': '1', '8': '1', '9': '1', '10': '1', '11': '4', '12': '1', '13': '1', '14': '1', '15': '1', '16': '3', '17': '1', '18': '1', '19': '1', '20': '1'}
ml7_solution = {'1': '5', '2': '0', '3': '5', '4': '0', '5': '5', '6': '5', '7': '2', '8': '2', '9': '2', '10': '4', '11': '4', '12': '3', '13': '3', '14': '3', '15': '3', '16': '1', '17': '1', '18': '1', '19': '1', '20': '1'}


ml8_solution = {'1': '1', '2': '1', '3': '1', '4': '1', '5': '1', '6': '1', '7': '1', '8': '1', '9': '1', '10': '1', '11': '1', '12': '3', '13': '1', '14': '3', '15': '4', '16': '1', '17': '3', '18': '1', '19': '4', '20': '3'}
ml9_solution = {'1': '9', '2': '1', '3': '1', '4': '9', '5': '1', '6': '1', '7': '1', '8': '1', '9': '9', '10': '1', '11': '1', '12': '1', '13': '1', '14': '1', '15': '1', '16': '1', '17': '1', '18': '9', '19': '1', '20': '4'}

# print(vd.evaluate_solution(instance, ml4_solution))
# print(vd.evaluate_solution(instance, ml5_solution))
# print(vd.evaluate_solution(instance, ml6_solution))
print(vd.evaluate_solution(instance, ml9_solution))



'''

# Prepare testing data
testing = {}
episodes = 0

for file in os.listdir('episodes/testing'):

    content = pd.read_csv('episodes/testing/{}'.format(file))
    testing[episodes] = {}

    testing[episodes]['w'] = {}
    testing[episodes]['y'] = {}

    for period in instance.periods:
        testing[episodes]['w'][period] = {}
        testing[episodes]['y'][period] = {}
        for customer in instance.customers:
            testing[episodes]['w'][period][customer] = content[(content['j'] == int(customer)) & (content['t'] == int(period))].iloc[0]['w']
        for location in instance.locations:
            testing[episodes]['y'][period][location] = 1. if int(location) == content[(content['j'] == int(customer)) & (content['t'] == int(period))].iloc[0]['i'] else 0.

    episodes += 1

for episode in range(episodes):

    print('Episode {}'.format(episode))

    slc_solution = {}

    for period in instance.periods:

        for location in instance.locations:

            if testing[episode]['y'][period][location] > 0.:
                slc_solution[period] = location

    vd.export_data(instance, slc_solution, 'groundtruth_{}.csv'.format(episode))
    vd.export_data(modified, slc_solution, 'prediction_{}.csv'.format(episode))
'''