def is_equal(a, b, error = 0.0001):
    return abs(a - b) < error

def apply_replenishment(instance, cumulative):

    for customer in instance.customers:

        cumulative[customer] = (1 + instance.alphas[customer]) * cumulative[customer] + instance.betas[customer]

    return cumulative

def apply_absorption(instance, cumulative, location, flag = 0):

    for customer in instance.customers:

        if instance.catalogs[location][customer] or flag == -1:

            cumulative[customer] -= cumulative[customer]

    return cumulative

def apply_consolidation(instance, cumulative):

    for customer in instance.customers:

            cumulative[customer] = cumulative[customer]

    return cumulative

def evaluate_location(instance, cumulative, period, location):

    score = 0.

    for customer in instance.customers:

        if instance.catalogs[location][customer]:

            partial_demand = cumulative[customer]
            partial_reward = instance.revenues[period][location] * partial_demand

            # print('| obtaning {} from customer {} at time period {}'.format(partial_reward, customer, period))

            score += partial_reward

    return score

def evaluate_solution(instance, solution):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    for period in instance.periods:

        cumulative = apply_replenishment(instance, cumulative)

        if solution[period] != '0':

            score = evaluate_location(instance, cumulative, period, solution[period])

            # print('| scoring {} through location {} at time period {}'.format(score, solution[period], period))

            fitness += score

            cumulative = apply_absorption(instance, cumulative, solution[period])

        cumulative = apply_consolidation(instance, cumulative)

    return round(fitness, 2)

def export_data(instance, solution, filename = 'analysis.csv'):

    with open(filename, 'w') as output:

        output.write('i,j,t,{},{},{},w,d\n'.format(','.join(['v{}'.format(period) for period in instance.periods]),','.join(['w{}'.format(period) for period in instance.periods]), ','.join(['d{}'.format(period) for period in instance.periods])))

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    memory = {}
    memory_d = {}

    for period in instance.periods:

        cumulative = apply_replenishment(instance, cumulative)

        memory[period] = {}
        memory_d[period] = {}

        if solution[period] != '0':

            score = 0.

            for customer in instance.customers:

                if instance.catalogs[solution[period]][customer]:

                    local = instance.revenues[period][solution[period]] * cumulative[customer]

                    score += local

                    memory[period][customer] = local

                    memory_d[period][customer] = max(cumulative[customer] - local, 0.)

                else:

                    memory[period][customer] = 0.

                    memory_d[period][customer] = cumulative[customer]

                with open(filename, 'a') as output:

                        print('Period: {}, Customer: {}'.format(period, customer))

                        output.write('{},{},{},{},{},{},{},{}\n'.format(solution[period], customer, period,
                            ','.join(['{}'.format(instance.catalogs[solution[reference]][customer]) if int(reference) < int(period) else '{}'.format(0.) for reference in instance.periods]),
                            ','.join(['{}'.format(memory[reference][customer]) if int(reference) < int(period) else '{}'.format(0.) for reference in instance.periods]),
                            ','.join(['{}'.format(memory_d[reference][customer]) if int(reference) < int(period) else '{}'.format(0.) for reference in instance.periods]),
                            memory[period][customer],
                            memory_d[period][customer]))

            fitness += score

            cumulative = apply_absorption(instance, cumulative, solution[period])

        cumulative = apply_consolidation(instance, cumulative)

    return round(fitness, 2)

def export_data2(instance, solution, filename = 'analysis.csv'):

    with open(filename, 'w') as output:

        output.write('i,t,{},W\n'.format(','.join(['W{}'.format(period) for period in instance.periods])))

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    memory_l = {}

    for period in instance.periods:

        cumulative = apply_replenishment(instance, cumulative)

        memory_l[period] = {}

        for location in instance.locations:

            memory_l[period][location] = 0.

        if solution[period] != '0':

            score = 0.

            for customer in instance.customers:

                if instance.catalogs[solution[period]][customer]:

                    local = instance.revenues[period][solution[period]] * cumulative[customer]

                    score += local

            memory_l[period][solution[period]] = score

        for location in instance.locations:

            with open(filename, 'a') as output:

                print('Period: {}, Location: {}'.format(period, location))

                output.write('{},{},{},{}\n'.format(location, period,
                    ','.join(['{}'.format(memory_l[reference][location]) if int(reference) < int(period) else '{}'.format(0.) for reference in instance.periods]),
                    memory_l[period][location]))

                fitness += score

            cumulative = apply_absorption(instance, cumulative, solution[period])

        cumulative = apply_consolidation(instance, cumulative)

    return round(fitness, 2)

def detail_solution(instance, solution, filename = 'detailed_hrs.csv'):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    with open(filename, 'w') as output:

        output.write('{},{},{}\n'.format('0', '0', ','.join([str(cumulative[customer]) for customer in instance.customers])))

        for period in instance.periods:

            cumulative = apply_replenishment(instance, cumulative)

            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(cumulative[customer]) for customer in instance.customers])))

            if solution[period] != '0':

                score = evaluate_location(instance, cumulative, period, solution[period])

                fitness += score

                cumulative = apply_absorption(instance, cumulative, solution[period])

            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(cumulative[customer]) for customer in instance.customers])))

            cumulative = apply_consolidation(instance, cumulative)

            output.write('{},{},{}\n'.format(period, solution[period], ','.join([str(cumulative[customer]) for customer in instance.customers])))