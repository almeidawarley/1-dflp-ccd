import instance as ic
import formulation as fm


def print_solution(model, variable, verbose = False):

    print('Facility installation scheme:')
    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if value > 0.:
                print('\t| Location {} in time period {}'.format(location, period))

    if verbose:
        _ = input('Wait...')

    for period in instance.periods:
        print('Captured demand in time period {}'.format(period))
        for customer in instance.customers:
            captured = 0.
            for location in instance.locations:
                captured += variable['w'][period, location, customer].x
            if captured > 0.1:
                print('\t| Got {} units from customer {}'.format(captured, customer, period))

    if verbose:
        _ = input('Wait...')

    for customer in instance.customers:
        print('Demand behaviour for customer {}:'.format(customer))
        print('\t| Start with demand {}'.format(variable['d3']['0', customer].x))
        for period in instance.periods:
            d1 = variable['d1'][period, customer].x
            d2 = variable['d2'][period, customer].x
            d3 = variable['d3'][period, customer].x
            print('\t| At time period {}: [{}] -> [{}] -> [{}]'.format(period, d1, d2, d3))

    if verbose:
        _ = input('Wait...')

instance = ic.instance()

model, variable = fm.build(instance)

model.write('debug.lp')

relaxed = model.relax()

relaxed.optimize()

model.optimize()

print_solution(model, variable)