import validation as vd

def copy_solution(solution):

    return {period : location for period, location in solution.items()}

def insert_location(solution, period, location):

    inserted = copy_solution(solution)

    for reference in inserted.keys():
        previous = str(int(reference) - 1)
        if int(reference) > int(period):
            inserted[reference] = solution[previous]

    inserted[period] = location

    return inserted

def rank_locations(instance, cumulative, period):

    scores = {}

    for location in instance.locations:

        scores[location] = vd.evaluate_location(instance, cumulative, period, location)

    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse = True)}

    return scores

# largest profit first
def greedy_heuristic(instance):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    solution = {}

    for period in instance.periods:

        cumulative = vd.apply_replenishment(instance, cumulative)

        scores = rank_locations(instance, cumulative, period)

        # Choose the absolute best location
        location = list(scores.keys())[0]
        score = scores[location]

        solution[period] = location

        fitness += score

        cumulative = vd.apply_absorption(instance, cumulative, location)

        cumulative = vd.apply_consolidation(instance, cumulative)

    return solution, round(fitness, 2)


# build n based on n - 1
def progressive_algorithm(instance):

    # Create partial solution
    best_solution = {}
    for period in instance.periods:
        best_solution[period] = '0'
    best_objective = 0.

    for frontier in instance.periods:

        # print('Starting with {}'.format('-'.join(best_solution.values())))

        local_objective = best_objective
        local_solution = copy_solution(best_solution)

        for reference in reversed(instance.periods):

            if int(reference) <= int(frontier):

                for location in instance.locations + ['0']:

                    # Copy partial solution
                    candidate = copy_solution(best_solution)
                    # Insert location
                    candidate = insert_location(candidate, reference, location)
                    objective = vd.evaluate_solution(instance, candidate)

                    # if objective >= local_objective:
                    if objective > local_objective:
                        local_solution = copy_solution(candidate)
                        local_objective =  objective
                        '''
                        # Tie breaking rule, which works for some delta cases
                        elif objective == local_objective:

                            if location not in local_solution.values():

                                # What to do if

                                org_deltas = {key: value for (key, value) in instance.deltas.items()}
                                for customer in instance.customers:
                                    instance.deltas[customer] = 10**6

                                ign_solutionA = vd.evaluate_solution(instance, candidate)
                                ign_solutionB = vd.evaluate_solution(instance, local_solution)

                                if ign_solutionA > ign_solutionB:
                                    local_solution = copy_solution(candidate)
                                    local_objective =  objective
                                else:
                                    print(candidate)
                                    print(local_solution)
                                    print('Solutions should be equivalent...')

                                for customer in instance.customers:
                                    instance.deltas[customer] = org_deltas[customer]
                        '''
                    else:
                        pass

        if local_objective > best_objective:
            best_objective = local_objective
            best_solution = copy_solution(local_solution)

        # print('Best solution: {}'.format('-'.join(best_solution.values())))

    return best_solution, round(best_objective, 2)