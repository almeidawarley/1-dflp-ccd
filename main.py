import instance as ic
import formulation as fm
import heuristic as hr
import export as ex
import sys

def is_equal(a, b, error = 0.0001):
    return abs(a - b) < error

keyword = sys.argv[1]

instance = ic.instance(keyword)

mip, variable = fm.build_linear(instance)

mip.write('debug.lp')

heuristic, fitness = hr.greedy_heuristic(instance)

# fm.warm_start(instance, mip, variable, heuristic)

lpr = mip.relax()

lpr.optimize()

mip.optimize()

ex.print_solution(instance, mip, variable)

optimal = ex.format_solution(instance, mip, variable)

validated = hr.evaluate_solution(instance, optimal)

check = is_equal(mip.objVal, validated)

print('>>> Sanity check: {} = {} ? {}!'.format(mip.objVal, validated, check))

ex.write_statistics(instance, mip, lpr, optimal, fitness, heuristic, check)