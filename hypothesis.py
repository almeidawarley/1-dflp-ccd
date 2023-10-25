import instance as ic
import formulation as fm
import heuristic as hr
import validation as vd
import argparse as ap
import recording as rc
import time as tm

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def compute_gap(major, minor):
    return round((major - minor) / major, 4)

def main(keyword, periods, project = 'prober'):

    parser = ap.ArgumentParser(description = 'Run 1-DFLP-RA for some instance')
    args = parser.parse_args()

    args.keyword = keyword
    args.project = project

    mark_section('Generating instance information based on the parameters...')
    instance = ic.instance(args.keyword, args.project)
    instance.print_instance()
    instance.parameters['T'] = periods
    instance.create_rnd2()

    mark_section('Logging instance parameters read from file ...')
    record = rc.create_record(args.project, instance)

    mark_section('Applying the progressive algorithm to the instance...')
    start = tm.time()
    prg_solution, prg_objective = hr.progressive_algorithm(instance)
    end = tm.time()
    print('Progressive solution: [{}] {}'.format(prg_objective, prg_solution))
    record = rc.update_record(record, {
        'prg_objective': prg_objective,
        'prg_solution': '-'.join(prg_solution.values()),
        'prg_runtime': round(end - start, 2)
    })

    mark_section('Building the 1-DFLP-RA for the instance...')
    mip, mip_variable = fm.build_linearized(instance)
    mip.write('archives/{}-mip.lp'.format(instance.keyword))

    mark_section('Solving the MIP of the 1-DFLP-RA model...')
    fm.warm_start(instance, mip_variable, prg_solution)
    mip.optimize()
    mip.write('archives/{}-mip.sol'.format(instance.keyword))
    mip_solution = fm.format_solution(instance, mip, mip_variable)
    mip_objective = round(mip.objVal, 2)
    mip_runtime = round(mip.runtime, 2)
    print('Optimal MIP solution: [{}] {}'.format(mip_objective, mip_solution))
    record = rc.update_record(record,{
        'mip_objective': mip_objective,
        'mip_solution': '-'.join(mip_solution.values()),
        'mip_runtime': mip_runtime,
        'mip_status': mip.status,
        'mip_optgap': mip.MIPGap,
        'prg_optgap': compute_gap(mip_objective, prg_objective)
    })

    mark_section('Validating the solution of the DSFLP-DAR analytically...')
    analytical = vd.evaluate_solution(instance, mip_solution)
    record = rc.update_record(record, {
        'mip_check': vd.is_equal(mip_objective, analytical, 0.1)
    })

    print('>>> PRG objective: {}'.format(record['prg_objective']))
    print('>>> PRG optimality: {}'.format(record['prg_optgap']))
    print('>>> MIP solution: {}'.format('-'.join(mip_solution.values())))
    print('>>> PRG solution: {}'.format('-'.join(prg_solution.values())))

    return record

seed = 24

max_optgap = .0
max_seed = -1

while seed <= 100:
    periods = 1
    while periods <= 5:
        record = main('rnd2{}'.format(seed), periods)
        print('for period {}: {} <= {}'.format(periods, record['prg_objective'], record['mip_objective']))
        _ = input('aa')
        periods += 1