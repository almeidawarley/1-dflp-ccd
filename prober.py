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

def main(keyword, project = 'prober'):

    parser = ap.ArgumentParser(description = 'Run 1-DFLP-RA for some instance')
    args = parser.parse_args()

    args.keyword = keyword
    args.project = project

    mark_section('Generating instance information based on the parameters...')
    instance = ic.instance(args.keyword, args.project)
    instance.print_instance()

    mark_section('Logging instance parameters read from file ...')
    record = rc.create_record(args.project, instance)

    mark_section('Applying the random algorithm to the instance...')
    start = tm.time()
    rnd_solution, rnd_objective = hr.random_algorithm(instance)
    end = tm.time()
    print('Random solution: [{}] {}'.format(rnd_objective, rnd_solution))
    record = rc.update_record(record, {
        'rnd_objective': rnd_objective,
        'rnd_solution': '-'.join(rnd_solution.values()),
        'rnd_runtime': round(end - start, 2)
    })

    mark_section('Applying the forward (greedy) algorithm to the instance...')
    start = tm.time()
    frw_solution, frw_objective = hr.forward_algorithm(instance)
    end = tm.time()
    print('Forward solution: [{}] {}'.format(frw_objective, frw_solution))
    record = rc.update_record(record, {
        'frw_objective': frw_objective,
        'frw_solution': '-'.join(frw_solution.values()),
        'frw_runtime': round(end - start, 2)
    })

    mark_section('Applying the backward (greedy) algorithm to the instance...')
    start = tm.time()
    bcw_solution, bcw_objective = hr.backward_algorithm(instance)
    end = tm.time()
    print('Backward solution: [{}] {}'.format(bcw_objective, bcw_solution))
    record = rc.update_record(record, {
        'bcw_objective': bcw_objective,
        'bcw_solution': '-'.join(bcw_solution.values()),
        'bcw_runtime': round(end - start, 2)
    })

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
    mip, mip_variable = fm.build_fancy(instance)
    mip.write('archives/{}-mip.lp'.format(instance.keyword))
    nlr, nlr_variable = fm.build_nonlinear(instance)

    mark_section('Solving the LPR of the 1-DFLP-RA model...')
    lpr = mip.relax()
    lpr.optimize()
    lpr.write('archives/{}-lpr.sol'.format(instance.keyword))
    lpr_objective = round(lpr.objVal, 2)
    lpr_runtime = round(lpr.runtime, 2)
    print('Optimal LPR solution: [{}] no interpretable solution'.format(round(lpr.objVal, 2)))
    record = rc.update_record(record, {
        'lpr_objective': lpr_objective,
        'lpr_runtime': lpr_runtime,
        'lpr_status': lpr.status
    })

    mark_section('Solving the MIP of the 1-DFLP-RA model...')
    wms_objective = max(rnd_objective, frw_objective, bcw_objective, prg_objective)
    if wms_objective == rnd_objective:
        fm.warm_start(instance, mip_variable, rnd_solution)
    elif wms_objective == frw_objective:
        fm.warm_start(instance, mip_variable, frw_solution)
    elif wms_objective == bcw_objective:
        fm.warm_start(instance, mip_variable, bcw_solution)
    elif wms_objective == prg_objective:
        fm.warm_start(instance, mip_variable, prg_solution)
    else:
        raise Exception('No warm start solution found')
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
        'mip_intgap': compute_gap(lpr_objective, mip_objective),
        'rnd_optgap': compute_gap(mip_objective, rnd_objective),
        'frw_optgap': compute_gap(mip_objective, frw_objective),
        'bcw_optgap': compute_gap(mip_objective, bcw_objective),
        'prg_optgap': compute_gap(mip_objective, prg_objective)
    })

    wms_objective = max(rnd_objective, frw_objective, bcw_objective, prg_objective)
    if wms_objective == rnd_objective:
        fm.warm_start(instance, nlr_variable, rnd_solution)
    elif wms_objective == frw_objective:
        fm.warm_start(instance, nlr_variable, frw_solution)
    elif wms_objective == bcw_objective:
        fm.warm_start(instance, nlr_variable, bcw_solution)
    elif wms_objective == prg_objective:
        fm.warm_start(instance, nlr_variable, prg_solution)
    else:
        raise Exception('No warm start solution found')

    mark_section('Solving the nonlinear MIP of the 1-DFLP-RA model...')
    nlr.optimize()
    nlr.write('archives/{}-nlr.sol'.format(instance.keyword))
    nlr_solution = fm.format_solution(instance, nlr, nlr_variable)
    nlr_objective = round(nlr.objVal, 2)
    nlr_runtime = round(nlr.runtime, 2)
    print('Optimal MIP solution: [{}] {}'.format(nlr_objective, nlr_solution))
    record = rc.update_record(record,{
        'nlr_objective': nlr_objective,
        'nlr_solution': '-'.join(nlr_solution.values()),
        'nlr_runtime': nlr_runtime,
        'nlr_status': nlr.status,
        'nlr_optgap': nlr.MIPGap
    })

    mark_section('Validating the solution of the 1-DFLP-RA analytically...')
    analytical = vd.evaluate_solution(instance, mip_solution)
    validation = vd.is_equal(mip_objective, analytical, 0.1)
    record = rc.update_record(record, {
        'sanity_check': validation
    })
    print('>>> Sanity check: {} = {}? {} <<<'.format(mip_objective, analytical, validation))

    for method in ['1', '2', '3']:

        mark_section('Approximating the 1-DFLP-RA by the #{} method...'.format(method))
        apr, apr_variable = fm.build_simple(instance, method)
        apr.write('archives/{}-ap{}.lp'.format(instance.keyword, method))
        apr.optimize()
        apr.write('archives/{}-ap{}.sol'.format(instance.keyword, method))
        apr_solution = fm.format_solution(instance, apr, apr_variable)
        apr_objective = vd.evaluate_solution(instance, apr_solution)
        apr_runtime = round(apr.runtime, 2)
        print('Approximate solution #{}: [{}] {}'.format(method, apr_objective, apr_solution))
        record = rc.update_record(record, {
            'ap{}_objective'.format(method): apr_objective,
            'ap{}_solution'.format(method): '-'.join(apr_solution.values()),
            'ap{}_runtime'.format(method): apr_runtime,
            'ap{}_status'.format(method): apr.status,
            'ap{}_optgap'.format(method): compute_gap(mip_objective, apr_objective)
        })

    mark_section('Wrapping up the execution with sanity check {}!'.format(validation))

    print('>>> MIP objective: {}'.format(record['mip_objective']))
    print('>>> FRW objective: {}'.format(record['frw_objective']))
    print('>>> FRW optimality: {}'.format(record['frw_optgap']))
    print('>>> PRG objective: {}'.format(record['prg_objective']))
    print('>>> PRG optimality: {}'.format(record['prg_optgap']))
    print('>>> BCW objective: {}'.format(record['bcw_objective']))
    print('>>> BCW optimality: {}'.format(record['bcw_optgap']))
    print('>>> MIP solution: {}'.format('-'.join(mip_solution.values())))
    print('>>> FRW solution: {}'.format('-'.join(frw_solution.values())))
    print('>>> PRG solution: {}'.format('-'.join(prg_solution.values())))
    print('>>> BCW solution: {}'.format('-'.join(bcw_solution.values())))

    return record

seed = 1

max_optgap = .0
max_seed = -1

while seed <= 100:
    record = main('rnd2{}'.format(seed))
    if record['prg_optgap'] > max_optgap:
        max_optgap = record['prg_optgap']
        max_seed = seed
    seed += 1
    print('max_optgap: {} [seed: {}]'.format(max_optgap, max_seed))
    # _ = input('wait...')