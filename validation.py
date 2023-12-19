def is_equal(a, b, error = 0.0001):

    return abs(a - b) < error

def compute_gap(major, minor):

    return round((major - minor) / major, 4)

def compare_obj(objective1, objective2, tolerance = 1/10**4):

    if objective1 < objective2:
      objective1, objective2 = objective2, objective1
    gap = compute_gap(objective1, objective2)

    return gap <= tolerance