import instance as ic
import formulation as fm
import heuristic as hr
import validation as vd
import export as ex
import sys

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

keyword = sys.argv[1]

mark_section('Generating instance information based on the parameters...')

instance = ic.instance(keyword)

solutions = {}
times = {}

mark_section('Applying the greedy heuristic to the instance...')

hrs_solution, hrs_objective = hr.greedy_heuristic(instance)

solutions['HRS'] = hrs_solution

print('Heuristic solution: [{}] {}'.format(hrs_objective, hrs_solution))

mark_section('Building the 1-DFLP-DRA for the instance...')

mip, variable = fm.build_fancy(instance)

mip.write('{}/{}.lp'.format('models', instance.keyword))

# fm.warm_start(instance, mip, variable, hrs_solution)

mark_section('Solving the LPR of the 1-DFLP-DRA model...')

lpr = mip.relax()

lpr.optimize()

print('Optimal LPR solution: [{}] no interpretable solution'.format(round(lpr.objVal, 2)))

mark_section('Solving the MIP of the 1-DFLP-DRA model...')

mip.optimize()

# ex.detail_solution(instance, mip, variable)

mip_solution = ex.format_solution(instance, mip, variable)

mip_objective = round(mip.objVal, 2)

solutions['MIP'] = mip_solution

print('Optimal MIP solution: [{}] {}'.format(mip_objective, mip_solution))

for method in ['1', '2', '3']:

    mark_section('Approximating the 1-DFLP-DRA by the #{} method...'.format(method))

    apr, variable = fm.build_simple(instance, method)

    apr.optimize()

    apr_solution = ex.format_solution(instance, apr, variable)

    apr_objective = vd.evaluate_solution(instance, apr_solution)

    solutions['APR{}'.format(method)] = apr_solution

    times['APR{}'.format(method)] = apr.runtime

    print('Approximate solution #{}: [{}] {}'.format(method, apr_objective, apr_solution))

mark_section('Writing execution records to an output file...')

ex.write_statistics(instance, mip, lpr, solutions, times)

mark_section('Validating the solution of the 1-DFLP-DRA analytically...')

validated = vd.evaluate_solution(instance, mip_solution)

check = vd.is_equal(mip_objective, validated)

print('>>> Sanity check: {} = {} ? {}!'.format(mip_objective, validated, check))