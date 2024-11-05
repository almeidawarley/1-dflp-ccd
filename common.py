import debugging as db
import benchmark as bm

TIMELIMIT = 2 * 60 * 60
TOLERANCE = 10 ** (-4)
PRECISION = 4 # 10 ** (-4)
INFINITY = 10 ** 8

def is_equal_to(value1, value2, tolerance = TOLERANCE):
    # Compare two values according to tolerance
    return abs(value1 - value2) <= tolerance

def compute_gap(major, minor):
    # Compute relative gap between two values
    if major < minor:
        major, minor = minor, major
        print('>>> Flipping objective values for gap computation (major = {}, minor = {}) <<<'.format(major, minor))
    return compute_gap1(major, minor)

def compute_gap1(major, minor):
    # Compute relative gap between two values (major as reference)
    return round((major - minor) / abs(major + TOLERANCE), PRECISION)

def compute_gap2(major, minor):
    # Compute relative gap between two values (minor as reference)
    return round((major - minor) / abs(minor + TOLERANCE), PRECISION)

def compute_gap3(major, minor):
    # Compute relative gap between two values (Gurobi version?)
    return round(abs(major - minor) / abs(minor + TOLERANCE), PRECISION)

def compare_obj(objective1, objective2, tolerance = TOLERANCE):
    # Compare two objective values according to tolerance
    if objective1 < objective2:
        objective1, objective2 = objective2, objective1
    return compute_gap(objective1, objective2) <= tolerance

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def load_instance(keyword):
    if keyword in ['proof', 'spp', 'approx', 'jopt']:
        instance = db.debugging(keyword)
    elif 'bmk' in keyword:
        instance = bm.benchmark(keyword)
    else:
        exit('Invalid instance keyword')
    return instance