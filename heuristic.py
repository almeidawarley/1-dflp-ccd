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

# largest profit first approach

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

# smaller regret now approach

def smart_heuristic(instance):

    cumulative = {}

    for customer in instance.customers:

        cumulative[customer] = instance.starts[customer]

    fitness = 0.

    solution = {}

    for period in instance.periods:

        cumulative = vd.apply_replenishment(instance, cumulative)

        scores = rank_locations(instance, cumulative, period)
        scales = {candidate : instance.revenues[period][candidate] * sum(instance.deltas[customer] for customer in instance.customers if instance.catalogs[candidate][customer] == 1) for candidate in instance.locations}

        location = -1
        postponed = 0

        print('Scores: {}'.format(scores))
        print('Scale: {}'.format(scales))

        for index, candidate in enumerate(scores.keys()):

            # Potentially suboptimal decision
            if index < len(instance.locations) and scales[candidate] > 0:
                print('> It is best to postpone choosing location {} at time period {}'.format(candidate, period))
                if int(period) + postponed < len(instance.periods):
                    postponed += 1
                    print('| which is feasible, so postponing it to the future')
                else:
                    print('| though not feasible, so choosing it for now instead')
                    location = candidate
                    break
            else:
                print('> It is best to take profits from location {} at time period {}'.format(candidate, period))
                location = candidate
                break

        score = scores[location]

        solution[period] = location

        fitness += score

        cumulative = vd.apply_absorption(instance, cumulative, location)

        cumulative = vd.apply_consolidation(instance, cumulative)

    return solution, round(fitness, 2)

# built upon best solution with n - 1, n -2, ..., 1 time periods

def progressive_heuristic(instance):

    # Create partial solution
    solution = {}
    for period in instance.periods:
        solution[period] = '0'
    best_global = 0.

    for frontier in instance.periods:

        print('| Going until time period {}'.format(frontier))

        best_local = best_global
        solution_local = {key : value for key, value in solution.items()}

        for reference in instance.periods:

            # print('| Inserting at time period {}'.format(reference))

            if int(reference) <= int(frontier) and int(reference):

                for location in instance.locations:

                    # print('| Trying out location  {}'.format(location))

                    # print('Partial solution: {}'.format('-'.join(solution.values())))

                    # Copy partial solution
                    candidate = {}
                    for period in solution.keys():
                        if int(period) <= int(reference):
                            # Mimic what happens until reference
                            candidate[period] = solution[period]
                        else:
                            # Delay decisions from reference onwards
                            previous = str(int(period) - 1)
                            candidate[period] = solution[previous]

                    # Insert location for reference
                    candidate[reference] = location

                    # print('Candidate solution: {}'.format('-'.join(candidate.values())))

                    fitness = vd.evaluate_solution(instance, candidate)

                    # print('Fitness of this solution: {}'.format(fitness))

                    if fitness > best_local:
                        best_local = fitness
                        solution_local = {key : value for key, value in candidate.items()}

                    elif fitness == best_local:

                        # _ = input('Tie between {} and {} '.format('-'.join(solution_local.values()), '-'.join(candidate.values())))
                        pass

                    else:

                        pass

            # _ = input(' enter...')

        # _ = input(' enter...')

        if best_local > best_global:
            best_global = best_local
            solution = {key : value for key, value in solution_local.items()}

        print('Best solution so far: {}'.format('-'.join(solution.values())))

    return solution, round(best_global, 2)

def passing_heuristic(instance):

    # Create partial solution
    best_solution, best_objective = greedy_heuristic(instance)

    for reference in instance.periods:

        for location in instance.locations:

            print('| Trying out location {} for period {}'.format(location, reference))

            local_solution = copy_solution(best_solution)
            local_solution[reference] = location
            local_objective = vd.evaluate_solution(instance, local_solution)

            if local_objective > best_objective:
                best_objective = local_objective
                best_solution = copy_solution(local_solution)
            elif local_objective == best_objective:
                print('Tie between {} and {} '.format('-'.join(best_solution.values()), '-'.join(local_solution.values())))
            else:
                pass

    return best_solution, round(best_objective, 2)

# built upon best solution with n - 1, n -2, ..., 1 time periods
# allow flips of locations before inserting

def optimal_algorithm(instance):

    # Create partial solution
    best_solution = {}
    for period in instance.periods:
        best_solution[period] = '0'
    best_objective = 0.

    for frontier in instance.periods:

        local_objective = best_objective
        local_solution = copy_solution(best_solution)

        for reference in reversed(instance.periods):

            if int(reference) <= int(frontier):

                for location in instance.locations:

                    # Copy partial solution
                    candidate = copy_solution(best_solution)
                    # Insert location
                    candidate = insert_location(candidate, reference, location)
                    objective = vd.evaluate_solution(instance, candidate)
                    # if objective >= local_objective: # to get alternative wrong solution
                    if objective >= local_objective:
                        local_objective =  objective
                        local_solution = copy_solution(candidate)

        if local_objective > best_objective:
            best_objective = local_objective
            best_solution = copy_solution(local_solution)

        print('Best solution so far: {}'.format('-'.join(best_solution.values())))

    return best_solution, round(best_objective, 2)