import formulation as fm
import validation as vd
import numpy as np

def copy_solution(solution):

    return {period : location for period, location in solution.items()}

def empty_solution(instance):

    return {period: '0' for period in instance.periods}

def insert_location(solution, period, location):

    inserted = copy_solution(solution)

    for reference in inserted.keys():
        previous = str(int(reference) - 1)
        if int(reference) > int(period):
            inserted[reference] = solution[previous]

    inserted[period] = location

    return inserted

def progressive_algorithm(instance):

    # Create partial solution
    best_solution = empty_solution(instance)
    best_objective = 0.

    for frontier in instance.periods:

        local_objective = best_objective
        local_solution = copy_solution(best_solution)

        for reference in reversed(instance.periods):

            if int(reference) <= int(frontier):

                for location in instance.locations_extended:

                    # Copy partial solution
                    candidate = copy_solution(best_solution)
                    # Insert location
                    candidate = insert_location(candidate, reference, location)
                    objective = vd.evaluate_solution(instance, candidate)

                    # if objective >= local_objective:
                    if objective > local_objective:
                        local_solution = copy_solution(candidate)
                        local_objective =  objective

        if local_objective > best_objective:
            best_objective = local_objective
            best_solution = copy_solution(local_solution)

    return best_solution, round(best_objective, 2)

def forward_algorithm(instance):

    # Create partial solution
    best_solution = empty_solution(instance)
    best_objective = 0.

    for reference in instance.periods:

        for location in instance.locations_extended:

            # Copy partial solution
            candidate = copy_solution(best_solution)
            # Insert location
            candidate[reference] = location
            objective = vd.evaluate_solution(instance, candidate)

            if objective > best_objective:
                best_solution = copy_solution(candidate)
                best_objective =  objective

    return best_solution, round(best_objective, 2)

def backward_algorithm(instance):

    # Create partial solution
    best_solution = empty_solution(instance)
    best_objective = 0.

    for reference in reversed(instance.periods):

        for location in instance.locations_extended:

            # Copy partial solution
            candidate = copy_solution(best_solution)
            # Insert location
            candidate[reference] = location
            objective = vd.evaluate_solution(instance, candidate)

            if objective > best_objective:
                best_solution = copy_solution(candidate)
                best_objective =  objective

    return best_solution, round(best_objective, 2)

def random_algorithm(instance):

    np.random.seed(instance.parameters['seed'])

    # Create partial solution
    best_solution = {}
    for period in instance.periods:
        best_solution[period] = np.random.choice(instance.locations_extended)
    best_objective = vd.evaluate_solution(instance, best_solution)

    return best_solution, round(best_objective, 2)

'''
def fixing_algorithm(instance):

    # Create relaxation
    relax, variable = fm.build_linearized_lpr(instance)

    # Check integrality
    integral = False

    while not integral:

        minimum_value = 1.
        minimum_location = '0'
        minimum_period = '0'

        maximum_value = 0.
        maximum_location = '0'
        maximum_period = '0'

        # Solve relaxation
        relax.optimize()

        # Parse solution
        integral = True
        for location in instance.locations:
            for period in instance.periods:
                value = variable['y'][period, location].x
                # Check integrality
                if not vd.is_equal(value, 0) and not vd.is_equal(value, 1):
                    integral = False
                    # Store closest to 0
                    if value < minimum_value:
                        minimum_value = value
                        minimum_location = location
                        minimum_period = period
                    # Store closest to 1
                    if value > maximum_value:
                        maximum_value = value
                        maximum_location = location
                        maximum_period = period
                    # print('Variable y^{}_{} = {}'.format(period, location, value))

        # Fix variable
        if not integral:
            if abs(minimum_value - 0.) < abs(maximum_value - 1.):
                # _ = input('Fixing y^{}_{} = 0 [{}]'.format(minimum_period, minimum_location, minimum_value))
                relax.addConstr(variable['y'][minimum_period, minimum_location] == 0)
            else:
                #_ = input('Fixing y^{}_{} = 1 [{}]'.format(maximum_period, maximum_location, maximum_value))
                relax.addConstr(variable['y'][maximum_period, maximum_location] == 1)

    solution = fm.format_solution(instance, relax, variable)
    objective = vd.evaluate_solution(instance, solution)

    return solution, round(objective, 2)
'''

def fixing_algorithm(instance):

    # Create relaxation
    relax, variable = fm.build_linearized_lpr(instance)

    for period in instance.periods:

        # Check integrality
        integral = False

        while not integral:

            minimum_value = 1.
            minimum_location = '0'
            maximum_value = 0.
            maximum_location = '0'

            # Solve relaxation
            relax.optimize()

            integral = True
            for location in instance.locations:
                value = variable['y'][period, location].x
                # Check integrality
                if not vd.is_equal(value, 0) and not vd.is_equal(value, 1):
                    integral = False
                    # Store smallest
                    if value < minimum_value:
                        minimum_value = value
                        minimum_location = location
                    if value > maximum_value:
                        maximum_value = value
                        maximum_location = location
                    # print('Variable y^{}_{} = {}'.format(period, location, value))

            # Fix variable
            if not integral:
                if abs(minimum_value - 0.) < abs(maximum_value - 1.):
                    # _ = input('Fixing y^{}_{} = 0 [{}]'.format(minimum_period, location, minimum_value))
                    relax.addConstr(variable['y'][period, minimum_location] == 0)
                else:
                    # _ = input('Fixing y^{}_{} = 1 [{}]'.format(minimum_period, location, minimum_value))
                    relax.addConstr(variable['y'][period, maximum_location] == 1)

    solution = fm.format_solution(instance, relax, variable)
    objective = vd.evaluate_solution(instance, solution)

    return solution, round(objective, 2)