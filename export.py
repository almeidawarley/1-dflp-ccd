def write_statistics(instance, mip, lpr, optimal, heur_obj, heuristic, check, folder = 'records'):

    with open('{}/{}.csv'.format(folder, instance.keyword), 'w') as output:

        output.write('keyword,mip_obj,mip_status,mip_time,lpr_obj,lpr_status,lpr_time,mip_solution,heur_obj,heur_solution, sanity\n')

        output.write('{},{},{},{},{},{},{},{},{},{},{}\n'.format(
            instance.keyword,
            mip.objVal, mip.status, mip.runtime,
            lpr.objVal, lpr.status, lpr.runtime,
            '-'.join(optimal.values()), heur_obj,
            '-'.join(heuristic.values()),
            check))


def detail_solution(instance, mip, variable, verbose = 0):

    print('Facility installation scheme:')
    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if value > 0.:
                print('\t| At time period {} location {}'.format(period, location))
                for customer in instance.customers:
                    captured = variable['w'][period, location, customer].x
                    if captured > 0.:
                        print('\t\t| Got {} units from customer {}'.format(captured, customer, period))

    if verbose > 1:
        for customer in instance.customers:
            print('Demand behaviour for customer {}:'.format(customer))
            print('\t| Start with demand {}'.format(variable['d3']['0', customer].x))
            for period in instance.periods:
                d1 = variable['d1'][period, customer].x
                d2 = variable['d2'][period, customer].x
                d3 = variable['d3'][period, customer].x
                print('\t| At time period {}: [{}] -> [{}] -> [{}]'.format(period, d1, d2, d3))

def format_solution(instance, mip, variable, verbose = 0):

    solution = {}

    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if value > 0.:
                solution[period] = location

    return solution