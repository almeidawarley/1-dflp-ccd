import instance as ic
import formulation as fm
import heuristic as hr
import export as ex
import sys

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

ex.write_statistics(instance, mip, lpr, optimal, fitness, heuristic)

print('>>> Sanity check: {} = {} ? {}!'.format(mip.objVal, hr.evaluate_solution(instance, optimal), mip.objVal == hr.evaluate_solution(instance, optimal)))