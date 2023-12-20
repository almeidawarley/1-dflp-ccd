TIMELIMIT = 5 * 60 * 60
TOLERANCE = 10 ** (-4)
PRECISION = 4

def is_equal_to(value1, value2, tolerance = TOLERANCE):
    # Compare two values according to tolerance
    return abs(value1 - value2) <= tolerance

def compute_gap(major, minor):
    # Compute relative gap between two values
    return round((major - minor) / major, PRECISION)

def compare_obj(objective1, objective2, tolerance = TOLERANCE):
    # Compare two objective values according to tolerance

    if objective1 < objective2:
      objective1, objective2 = objective2, objective1

    return compute_gap(objective1, objective2) <= tolerance