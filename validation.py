def apply_replenishment(instance, cumulative):

    for customer in instance.customers:

        cumulative[customer] = min((1 + instance.alphas[customer]) * cumulative[customer] + instance.betas[customer], instance.uppers[customer])

    return cumulative

def apply_absorption(instance, cumulative, location, flag):

    for customer in instance.customers:

        if instance.catalogs[location][customer] or flag == -1:

            cumulative[customer] -= min(instance.gammas[customer] * cumulative[customer] + instance.deltas[customer], cumulative[customer])

    return cumulative

def apply_consolidation(instance, cumulative):

    for customer in instance.customers:

            cumulative[customer] = max(cumulative[customer], instance.lowers[customer])

    return cumulative

def evaluate_location(instance, cumulative, location):

    score = 0.

    for customer in instance.customers:

        if instance.catalogs[location][customer]:

            score += instance.revenues['1'][location] * min(instance.gammas[customer] * cumulative[customer] + instance.deltas[customer], cumulative[customer])

    return score

def evaluate_solution(instance, solution):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    for period in instance.periods:

            cumulative = apply_replenishment(instance, cumulative)

            if solution[period] != '0':

                score = evaluate_location(instance, cumulative, solution[period])

                fitness += score

                cumulative = apply_absorption(instance, cumulative, solution[period])

            cumulative = apply_consolidation(instance, cumulative)

    return fitness