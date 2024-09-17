import debugging as db
# import synthetic as sy
import slovakia as sl
import satisfiability as st
import artificial as ar

TIMELIMIT = 5 * 60 * 60
TIMENOUGH = 5
TOLERANCE = 10 ** (-4)
PRECISION = 4
INFINITY = 10 ** 6

def is_equal_to(value1, value2, tolerance = TOLERANCE):
    # Compare two values according to tolerance
    return abs(value1 - value2) <= tolerance

def compute_gap(major, minor):
    # Compute relative gap between two values
    if major < minor:
        print('>>>>> Flipping objective values for gap computation <<<<<')
        major, minor = minor, major
    return round((major - minor) / abs(major + 1 / INFINITY), PRECISION)

def compare_obj(objective1, objective2, tolerance = TOLERANCE):
    # Compare two objective values according to tolerance

    if objective1 < objective2:
      objective1, objective2 = objective2, objective1

    return compute_gap(objective1, objective2) <= tolerance

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def load_instance(keyword, project):
    if keyword in ['proof', 'spp', 'approx', 'jopt']:
        instance = db.debugging(keyword, project)
    elif '.cnf' in keyword:
        instance = st.satisfiability(keyword, project)
    # elif 'rnd' in keyword:
    #     instance = sy.synthetic(keyword, project)
    elif 'art' in keyword:
        instance = ar.artificial(keyword, project)
    elif 'slv' in keyword:
        instance = sl.slovakia(keyword, project)
    else:
        exit('Invalid instance keyword')
    return instance