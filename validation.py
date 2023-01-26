def is_equal(a, b, error = 0.0001):
    return abs(a - b) < error

def apply_replenishment(instance, cumulative):

    for customer in instance.customers:

        cumulative[customer] = min((1 + instance.alphas[customer]) * cumulative[customer] + instance.betas[customer], instance.uppers[customer])

    return cumulative

def apply_absorption(instance, cumulative, location, flag = 0):

    for customer in instance.customers:

        if instance.catalogs[location][customer] or flag == -1:

            cumulative[customer] -= min(instance.gammas[customer] * cumulative[customer] + instance.deltas[customer], cumulative[customer])

    return cumulative

def apply_consolidation(instance, cumulative):

    for customer in instance.customers:

            cumulative[customer] = max(cumulative[customer], instance.lowers[customer])

    return cumulative

def evaluate_location(instance, cumulative, period, location):

    score = 0.

    for customer in instance.customers:

        if instance.catalogs[location][customer]:

            score += instance.revenues[period][location] * min(instance.gammas[customer] * cumulative[customer] + instance.deltas[customer], cumulative[customer])

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