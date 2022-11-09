import validation as vd

def write_statistics(instance, mip, lpr, solutions, times, folder = 'records'):

    check = vd.is_equal(round(mip.objVal, 2), vd.evaluate_solution(instance, solutions['MIP']))
    mip_objective = vd.evaluate_solution(instance, solutions['MIP'])
    hrs_objective = vd.evaluate_solution(instance, solutions['HRS'])
    apr1_objective = vd.evaluate_solution(instance, solutions['APR1'])
    apr2_objective = vd.evaluate_solution(instance, solutions['APR2'])
    apr3_objective = vd.evaluate_solution(instance, solutions['APR3'])

    with open('{}/{}.csv'.format(folder, instance.keyword), 'w') as output:

        output.write('keyword,lpr_status,lpr_time,lpr_objective,mip_status,mip_time,mip_objective,mip_solution,hrs_objective,hrs_solution,apr1_time,apr1_objective,apr1_solution,apr2_time,apr2_objective,apr2_solution,apr3_time,apr3_objective,apr3_solution,sanity\n')

        output.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
            instance.keyword,
            lpr.status, lpr.runtime, lpr.objVal, mip.status, mip.runtime,
            mip_objective, '-'.join(solutions['MIP'].values()),
            hrs_objective, '-'.join(solutions['HRS'].values()),
            times['APR1'], apr1_objective, '-'.join(solutions['APR1'].values()),
            times['APR2'], apr2_objective, '-'.join(solutions['APR2'].values()),
            times['APR3'], apr3_objective, '-'.join(solutions['APR3'].values()),
            check))


def detail_solution(instance, variable, filename = 'detailed_export.csv'):

    solution = {}

    with open(filename, 'w') as output:

        for period in instance.periods:
            solution[period] = '0'

        d1 = {}
        d2 = {}
        d3 = {}
        for customer in instance.customers:
            d3[customer] = variable['d3']['0', customer].x
        output.write('{},{},{}\n'.format('0','0',','.join([str(d3[customer]) for customer in instance.customers])))

        for period in instance.periods:
            for location in instance.locations:
                value = variable['y'][period, location].x
                if vd.is_equal(value, 1.):
                    solution[period] = location
            for customer in instance.customers:
                d1[customer] = variable['d1'][period, customer].x
                d2[customer] = variable['d2'][period, customer].x
                d3[customer] = variable['d3'][period, customer].x
            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(d1[customer]) for customer in instance.customers])))
            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(d2[customer]) for customer in instance.customers])))
            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(d3[customer]) for customer in instance.customers])))

def format_solution(instance, mip, variable, verbose = 0):

    solution = {}

    for period in instance.periods:
        solution[period] = '0'

    for period in instance.periods:
        for location in instance.locations:
            value = variable['y'][period, location].x
            if vd.is_equal(value, 1.):
                solution[period] = location

    return solution