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

def main():

    parser = ap.ArgumentParser(description = 'Run 1-DFLP-RA for some instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = '1-dflp-ra', type = str, help = 'Instance project name')
    args = parser.parse_args()

    mark_section('Generating instance information based on the parameters...')
    instance = ic.instance(args.keyword, args.project)
    instance.print_instance()

    mark_section('Logging instance parameters read from file ...')
    record = rc.create_record(args.project, instance)

    mark_section('Applying the greedy heuristic to the instance...')
    start = tm.time()
    grd_solution, grd_objective = hr.greedy_heuristic(instance)
    end = tm.time()
    print('Greedy solution: [{}] {}'.format(grd_objective, grd_solution))
    record = rc.update_record(record, {
        'grd_objective': grd_objective,
        'grd_solution': '-'.join(grd_solution.values()),
        'grd_runtime': round(end - start, 2)
    })

    mark_section('Applying the progressive heuristic to the instance...')
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
    nws, nws_variable = fm.build_fancy(instance)

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
        'mip_intgap': compute_gap(lpr_objective, mip_objective),
        'grd_optgap': compute_gap(mip_objective, grd_objective),
        'prg_optgap': compute_gap(mip_objective, prg_objective)
    })

    mark_section('Solving the MIP (no warm start) of the 1-DFLP-RA model...')
    nws.optimize()
    nws.write('archives/{}-nws.sol'.format(instance.keyword))
    nws_solution = fm.format_solution(instance, nws, nws_variable)
    nws_objective = round(nws.objVal, 2)
    nws_runtime = round(nws.runtime, 2)
    print('Optimal MIP solution: [{}] {}'.format(nws_objective, nws_solution))
    record = rc.update_record(record,{
        'nws_objective': nws_objective,
        'nws_solution': '-'.join(nws_solution.values()),
        'nws_runtime': nws_runtime,
        'nws_status': nws.status,
        'nws_optgap': nws.MIPGap
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
    print('>>> GRD objective: {}'.format(record['grd_objective']))
    print('>>> GRD optimality: {}'.format(record['grd_optgap']))
    print('>>> PRG objective: {}'.format(record['prg_objective']))
    print('>>> PRG optimality: {}'.format(record['prg_optgap']))
    print('>>> MIP solution: {}'.format('-'.join(mip_solution.values())))
    print('>>> GRD solution: {}'.format('-'.join(grd_solution.values())))
    print('>>> PRG solution: {}'.format('-'.join(prg_solution.values())))

    '''
    mark_section('Listing all optimal MIP solution...')

    print('Optimal MIP solution: [{}] {} <{}>'.format(mip_objective, mip_solution, '-'.join(mip_solution.values())))
    fm.block_solution(mip, mip_variable, mip_solution)
    ref_objective = mip_objective
    while mip_objective == ref_objective:
        # print(vd.evaluate_solution(instance, mip_solution))
        mip.setParam('OutputFlag', 0)
        mip.optimize()
        mip_solution = fm.format_solution(instance, mip, mip_variable)
        mip_objective = round(mip.objVal, 2)
        mip_runtime = round(mip.runtime, 2)
        print('Optimal MIP solution: [{}] {} <{}>'.format(mip_objective, mip_solution, '-'.join(mip_solution.values())))
        fm.block_solution(mip, mip_variable, mip_solution)

    '''

main()