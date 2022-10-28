import instance as ic
import formulation as fm
import heuristic as hr
import export as ex
import sys

def is_equal(a, b, error = 0.0001):
    return abs(a - b) < error

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

keyword = sys.argv[1]

mark_section('Generating instance information based on the parameters...')

instance = ic.instance(keyword)

mark_section('Applying the greedy heuristic to the instance...')

heuristic, fitness = hr.greedy_heuristic(instance)

print('Heuristic solution: {}'.format(heuristic))

print('Total revenue over time: {}'.format(fitness))

mark_section('Building the DSFLP-SRA for the instance...')

mip, variable = fm.build_linear(instance)

mip.write('debug.lp')

# fm.warm_start(instance, mip, variable, heuristic)

mark_section('Solving the LPR of the DSFLP-SRA model...')

lpr = mip.relax()

lpr.optimize()

print('Total revenue over time: {}'.format(lpr.objVal))

mark_section('Solving the MIP of the DSFLP-SRA model...')

mip.optimize()

# ex.detail_solution(instance, mip, variable)

optimal = ex.format_solution(instance, mip, variable)

print('Optimal solution: {}'.format(optimal))

print('Total revenue over time: {}'.format(mip.objVal))

mark_section('Validating the MIP solution analytically...')

validated = hr.evaluate_solution(instance, optimal)

check = is_equal(mip.objVal, validated)

print('>>> Sanity check: {} = {} ? {}!'.format(mip.objVal, validated, check))

# mark_section('Writing execution records to an output file...')

ex.write_statistics(instance, mip, lpr, optimal, fitness, heuristic, check)