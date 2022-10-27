def apply_replenishment(instance, cumulative):

    for customer in instance.customers:

        cumulative[customer] = min((1 + instance.alphas[customer]) * cumulative[customer] + instance.betas[customer], instance.uppers[customer])

    return cumulative

def apply_absorption(instance, cumulative, location):

    for customer in instance.customers:

        if instance.catalogs[location][customer]:

            cumulative[customer] -= min(instance.gammas[customer] * cumulative[customer] + instance.deltas[customer], cumulative[customer])

    return cumulative

def apply_consolidation(instance, cumulative):

    for customer in instance.customers:

            cumulative[customer] = max(cumulative[customer], instance.lowers[customer])

    return cumulative

def choose_location(instance, cumulative):

    best = -1

    scores = {}

    for location in instance.locations:

        scores[location] = evaluate_location(instance, cumulative, location)

        if best == -1 or scores[location] > scores[best]:

            best = location

    return best, scores[best]

def evaluate_location(instance, cumulative, location):

    score = 0.

    for customer in instance.customers:

        if instance.catalogs[location][customer]:

            score += instance.revenues['1'][location] * min(instance.gammas[customer] * cumulative[customer] + instance.deltas[customer], cumulative[customer])

    return score

def greedy_heuristic(instance):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    solution = {}

    for period in instance.periods:

        cumulative = apply_replenishment(instance, cumulative)

        location, score = choose_location(instance, cumulative)

        solution[period] = location

        fitness += score

        cumulative = apply_absorption(instance, cumulative, location)

        cumulative = apply_consolidation(instance, cumulative)

    return solution, fitness

def evaluate_solution(instance, solution):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    for period in instance.periods:

        cumulative = apply_replenishment(instance, cumulative)

        score = evaluate_location(instance, cumulative, solution[period])

        fitness += score

        cumulative = apply_absorption(instance, cumulative, solution[period])

        cumulative = apply_consolidation(instance, cumulative)

    return fitness