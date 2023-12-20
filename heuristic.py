import formulation as fm
import validation as vd
import numpy as np

def progressive_algorithm(instance):

    # Create partial solution
    best_solution = instance.empty_solution()
    best_objective = 0.

    for frontier in instance.periods:

        local_objective = best_objective
        local_solution = instance.copy_solution(best_solution)

        for reference in reversed(instance.periods):

            if int(reference) <= int(frontier):

                for location in instance.locations_extended:

                    # Copy partial solution
                    candidate = instance.copy_solution(best_solution)
                    # Insert location
                    candidate = instance.insert_solution(candidate, reference, location)
                    objective = instance.evaluate_solution(candidate)

                    if objective > local_objective:
                        local_solution = instance.copy_solution(candidate)
                        local_objective =  objective

        if local_objective > best_objective:
            best_objective = local_objective
            best_solution = instance.copy_solution(local_solution)

    return best_solution, round(best_objective, 2)

def forward_algorithm(instance):

    # Create partial solution
    best_solution = instance.empty_solution()
    best_objective = 0.

    for reference in instance.periods:

        for location in instance.locations_extended:

            # Copy partial solution
            candidate = instance.copy_solution(best_solution)
            # Insert location
            candidate[reference] = location
            objective = instance.evaluate_solution(candidate)

            if objective > best_objective:
                best_solution = instance.copy_solution(candidate)
                best_objective =  objective

    return best_solution, round(best_objective, 2)

def backward_algorithm(instance):

    # Create partial solution
    best_solution = instance.empty_solution()
    best_objective = 0.

    for reference in reversed(instance.periods):

        for location in instance.locations_extended:

            # Copy partial solution
            candidate = instance.copy_solution(best_solution)
            # Insert location
            candidate[reference] = location
            objective = instance.evaluate_solution(candidate)

            if objective > best_objective:
                best_solution = instance.copy_solution(candidate)
                best_objective =  objective

    return best_solution, round(best_objective, 2)

def random_algorithm(instance):

    np.random.seed(instance.parameters['seed'])

    # Create partial solution
    best_solution = {}
    for period in instance.periods:
        best_solution[period] = np.random.choice(instance.locations_extended)
    best_objective = instance.evaluate_solution(best_solution)

    return best_solution, round(best_objective, 2)

def fixing_algorithm(instance):

    # Create relaxation
    relax, variable = fm.build_linearized_lpr(instance)

    for period in instance.periods:

        # Store integrality
        integral = False

        while not integral:

            minimum_value = 1.
            minimum_location = '0'
            maximum_value = 0.
            maximum_location = '0'

            # Solve relaxation
            relax.optimize()

            # Check integrality
            integral = True
            for location in instance.locations:
                value = variable['y'][period, location].x
                if not vd.is_equal(value, 0) and not vd.is_equal(value, 1):
                    integral = False
                    # Store smallest
                    if value < minimum_value:
                        minimum_value = value
                        minimum_location = location
                    # Store largest
                    if value > maximum_value:
                        maximum_value = value
                        maximum_location = location

            # Fix variable
            if not integral:
                if abs(minimum_value - 0.) < abs(maximum_value - 1.):
                    relax.addConstr(variable['y'][period, minimum_location] == 0)
                else:
                    relax.addConstr(variable['y'][period, maximum_location] == 1)

    solution = fm.format_solution(instance, relax, variable)
    objective = instance.evaluate_solution(solution)

    return solution, round(objective, 2)