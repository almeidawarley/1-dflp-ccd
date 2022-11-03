import validation as vd

def choose_location(instance, cumulative):

    best = -1

    scores = {}

    for location in instance.locations:

        scores[location] = vd.evaluate_location(instance, cumulative, location)

        if best == -1 or scores[location] > scores[best]:

            best = location

    return best, scores[best]

def greedy_heuristic(instance):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    solution = {}

    for period in instance.periods:

        cumulative = vd.apply_replenishment(instance, cumulative)

        location, score = choose_location(instance, cumulative)

        solution[period] = location

        fitness += score

        cumulative = vd.apply_absorption(instance, cumulative, location)

        cumulative = vd.apply_consolidation(instance, cumulative)

    return solution, fitness