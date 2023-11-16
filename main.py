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

def compare_obj(objective1, objective2, tolerance = 1/10**4):
    if objective1 < objective2:
      objective1, objective2 = objective2, objective1
    gap = compute_gap(objective1, objective2)
    return gap <= tolerance

def main():

    parser = ap.ArgumentParser(description = 'Run relevant solution methods for some DSFLP-DAR instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-dar', type = str, help = 'Instance project name')
    args = parser.parse_args()

    mark_section('Generating instance based on the parameters...')
    instance = ic.instance(args.keyword, args.project)
    instance.print_instance()

    mark_section('Logging instance parameters read from file...')
    record = rc.load_record(args.project, instance)

    mark_section('Applying the random algorithm...')
    start = tm.time()
    rnd_solution, rnd_objective = hr.random_algorithm(instance)
    end = tm.time()
    print('Random solution: [{}] {}'.format(rnd_objective, rnd_solution))
    record = rc.update_record(record, {
        'rnd_objective': rnd_objective,
        'rnd_solution': '-'.join(rnd_solution.values()),
        'rnd_runtime': round(end - start, 2)
    })

    '''
    mark_section('Applying the fixing algorithm...')
    start = tm.time()
    fix_solution, fix_objective = hr.fixing_algorithm(instance)
    end = tm.time()
    print('Fixing solution: [{}] {}'.format(fix_objective, fix_solution))
    record = rc.update_record(record, {
        'fix_objective': fix_objective,
        'fix_solution': '-'.join(fix_solution.values()),
        'fix_runtime': round(end - start, 2)
    })
    '''

    mark_section('Applying the forward (greedy) algorithm ...')
    start = tm.time()
    frw_solution, frw_objective = hr.forward_algorithm(instance)
    end = tm.time()
    print('Forward solution: [{}] {}'.format(frw_objective, frw_solution))
    record = rc.update_record(record, {
        'frw_objective': frw_objective,
        'frw_solution': '-'.join(frw_solution.values()),
        'frw_runtime': round(end - start, 2)
    })

    mark_section('Applying the backward (greedy) algorithm...')
    start = tm.time()
    bcw_solution, bcw_objective = hr.backward_algorithm(instance)
    end = tm.time()
    print('Backward solution: [{}] {}'.format(bcw_objective, bcw_solution))
    record = rc.update_record(record, {
        'bcw_objective': bcw_objective,
        'bcw_solution': '-'.join(bcw_solution.values()),
        'bcw_runtime': round(end - start, 2)
    })

    mark_section('Applying the progressive algorithm...')
    start = tm.time()
    prg_solution, prg_objective = hr.progressive_algorithm(instance)
    end = tm.time()
    print('Progressive solution: [{}] {}'.format(prg_objective, prg_solution))
    record = rc.update_record(record, {
        'prg_objective': prg_objective,
        'prg_solution': '-'.join(prg_solution.values()),
        'prg_runtime': round(end - start, 2)
    })

    warm_objective = max(rnd_objective, frw_objective, bcw_objective, prg_objective) #fix_objective
    if warm_objective == rnd_objective:
        warm_solution = rnd_solution
    elif warm_objective == frw_objective:
        warm_solution = frw_solution
    elif warm_objective == bcw_objective:
        warm_solution = bcw_solution
    #elif warm_objective == fix_objective:
    #    warm_solution = fix_solution
    elif warm_objective == prg_objective:
        warm_solution = prg_solution
    else:
        raise Exception('No warm start solution found')

    warm_lrz, warm_lrz_variable = fm.build_linearized_mip(instance)
    cold_lrz, cold_lrz_variable = fm.build_linearized_mip(instance)
    warm_net, warm_net_variable = fm.build_networked_mip(instance)
    cold_net, cold_net_variable = fm.build_networked_mip(instance)

    mark_section('Solving the relaxed DSFLP-DAR-LRZ model...')
    rlxt_lrz, rlxt_lrz_variable = fm.build_linearized_lpr(instance)
    # rlxt_lrz.write('archives/{}-rlxt_lrz.lp'.format(instance.keyword))
    rlxt_lrz.optimize()
    # rlxt_lrz.write('archives/{}-rlxt_lrz.sol'.format(instance.keyword))
    rlxt_lrz_objective = round(rlxt_lrz.objVal, 2)
    rlxt_lrz_runtime = round(rlxt_lrz.runtime, 2)
    print('Optimal relaxed LRZ solution: [{}] no interpretable solution'.format(round(rlxt_lrz.objVal, 2)))
    record = rc.update_record(record, {
        'rlxt_lrz_objective': rlxt_lrz_objective,
        'rlxt_lrz_runtime': rlxt_lrz_runtime,
        'rlxt_lrz_status': rlxt_lrz.status
    })

    mark_section('Solving warm MIP of the DSFLP-DAR-LRZ model...')
    fm.warm_start(instance, warm_lrz_variable, warm_solution)
    # warm_lrz.write('archives/{}-warm_lrz.lp'.format(instance.keyword))
    warm_lrz.optimize()
    warm_lrz_solution = fm.format_solution(instance, warm_lrz, warm_lrz_variable)
    warm_lrz_objective = round(warm_lrz.objVal, 2)
    warm_lrz_runtime = round(warm_lrz.runtime, 2)
    print('Optimal warm LRZ solution: [{}] {}'.format(warm_lrz_objective, warm_lrz_solution))
    record = rc.update_record(record,{
        'warm_lrz_objective': warm_lrz_objective,
        'warm_lrz_solution': '-'.join(warm_lrz_solution.values()),
        'warm_lrz_runtime': warm_lrz_runtime,
        'warm_lrz_status': warm_lrz.status,
        'warm_lrz_optgap': warm_lrz.MIPGap
    })
    assert(compare_obj(warm_lrz_objective, warm_objective) or warm_lrz_objective >= warm_objective)

    mark_section('Solving cold MIP of the DSFLP-DAR-LRZ model...')
    # cold_lrz.write('archives/{}-cold_lrz.lp'.format(instance.keyword))
    cold_lrz.optimize()
    cold_lrz_solution = fm.format_solution(instance, cold_lrz, cold_lrz_variable)
    cold_lrz_objective = round(cold_lrz.objVal, 2)
    cold_lrz_runtime = round(cold_lrz.runtime, 2)
    print('Optimal cold LRZ solution: [{}] {}'.format(cold_lrz_objective, cold_lrz_solution))
    record = rc.update_record(record,{
        'cold_lrz_objective': cold_lrz_objective,
        'cold_lrz_solution': '-'.join(cold_lrz_solution.values()),
        'cold_lrz_runtime': cold_lrz_runtime,
        'cold_lrz_status': cold_lrz.status,
        'cold_lrz_optgap': cold_lrz.MIPGap
    })

    mark_section('Solving the relaxed DSFLP-DAR-NET model...')
    rlxt_net, rlxt_net_variable = fm.build_networked_lpr(instance)
    # rlxt_net.write('archives/{}-rlxt_net.lp'.format(instance.keyword))
    rlxt_net.optimize()
    # rlxt_net.write('archives/{}-rlxt_net.sol'.format(instance.keyword))
    rlxt_net_objective = round(rlxt_net.objVal, 2)
    rlxt_net_runtime = round(rlxt_net.runtime, 2)
    print('Optimal relaxed NET solution: [{}] no interpretable solution'.format(round(rlxt_net.objVal, 2)))
    record = rc.update_record(record, {
        'rlxt_net_objective': rlxt_net_objective,
        'rlxt_net_runtime': rlxt_net_runtime,
        'rlxt_net_status': rlxt_net.status
    })

    mark_section('Solving warm MIP of the DSFLP-DAR-NET model...')
    fm.warm_start(instance, warm_net_variable, warm_solution)
    # warm_net.write('archives/{}-warm_net.lp'.format(instance.keyword))
    warm_net.optimize()
    warm_net_solution = fm.format_solution(instance, warm_net, warm_net_variable)
    warm_net_objective = round(warm_net.objVal, 2)
    warm_net_runtime = round(warm_net.runtime, 2)
    print('Optimal warm NET solution: [{}] {}'.format(warm_net_objective, warm_net_solution))
    record = rc.update_record(record,{
        'warm_net_objective': warm_net_objective,
        'warm_net_solution': '-'.join(warm_net_solution.values()),
        'warm_net_runtime': warm_net_runtime,
        'warm_net_status': warm_net.status,
        'warm_net_optgap': warm_net.MIPGap
    })
    assert(compare_obj(warm_net_objective, warm_objective) or warm_net_objective >= warm_objective)

    mark_section('Solving cold MIP of the DSFLP-DAR-NET model...')
    # cold_net.write('archives/{}-cold_net.lp'.format(instance.keyword))
    cold_net.optimize()
    cold_net_solution = fm.format_solution(instance, cold_net, cold_net_variable)
    cold_net_objective = round(cold_net.objVal, 2)
    cold_net_runtime = round(cold_net.runtime, 2)
    print('Optimal cold NET solution: [{}] {}'.format(cold_net_objective, cold_net_solution))
    record = rc.update_record(record,{
        'cold_net_objective': cold_net_objective,
        'cold_net_solution': '-'.join(cold_net_solution.values()),
        'cold_net_runtime': cold_net_runtime,
        'cold_net_status': cold_net.status,
        'cold_net_optgap': cold_net.MIPGap
    })

    mark_section('Validating DSFLP-DAR solution methods analytically...')
    record = rc.update_record(record, {
        'warm_lrz_check': compare_obj(warm_lrz_objective, vd.evaluate_solution(instance, warm_lrz_solution)),
        'cold_lrz_check': compare_obj(cold_lrz_objective, vd.evaluate_solution(instance, cold_lrz_solution)),
        'warm_net_check': compare_obj(warm_net_objective, vd.evaluate_solution(instance, warm_net_solution)),
        'cold_net_check': compare_obj(cold_net_objective, vd.evaluate_solution(instance, cold_net_solution))
    })

    assert(record['warm_lrz_check'] == True)
    assert(record['cold_lrz_check'] == True)
    assert(record['warm_net_check'] == True)
    assert(record['cold_net_check'] == True)

    upper_bound = max(warm_lrz_objective, cold_lrz_objective, warm_net_objective, cold_net_objective)
    record = rc.update_record(record, {
        'upper_bound': upper_bound
    })

    record = rc.update_record(record, {
        'lrz_intgap': compute_gap(rlxt_lrz_objective, warm_lrz_objective),
        'net_intgap': compute_gap(rlxt_net_objective, warm_net_objective),
        'rnd_optgap': compute_gap(upper_bound, rnd_objective),
        'frw_optgap': compute_gap(upper_bound, frw_objective),
        'bcw_optgap': compute_gap(upper_bound, bcw_objective),
        #'fix_optgap': compute_gap(upper_bound, fix_objective),
        'prg_optgap': compute_gap(upper_bound, prg_objective)
    })

    for method in ['1', '2']:

        mark_section('Emulating the DSFLP-DAR through DSFLP-{}...'.format(method))
        eml, eml_variable = fm.build_simplified_mip(instance, method)
        eml.optimize()
        eml_solution = fm.format_solution(instance, eml, eml_variable)
        eml_objective = vd.evaluate_solution(instance, eml_solution)
        eml_runtime = round(eml.runtime, 2)
        print('Emulated solution #{}: [{}] {}'.format(method, eml_objective, eml_solution))
        record = rc.update_record(record, {
            'em{}_objective'.format(method): eml_objective,
            'em{}_solution'.format(method): '-'.join(eml_solution.values()),
            'em{}_runtime'.format(method): eml_runtime,
            'em{}_status'.format(method): eml.status,
            'em{}_optgap'.format(method): compute_gap(upper_bound, eml_objective)
        })

    mark_section('Wrapping up the execution with the following objectives...')
    print('>>> LRZ objective: {}'.format(record['warm_lrz_objective']))
    print('>>> NET objective: {}'.format(record['warm_net_objective']))
    print('>>> FRW objective: {}'.format(record['frw_objective']))
    print('>>> BCW objective: {}'.format(record['bcw_objective']))
    # print('>>> FIX objective: {}'.format(record['fix_objective']))
    print('>>> PRG objective: {}'.format(record['prg_objective']))

    mark_section('Wrapping up the execution with the following optimality gaps...')
    print('>>> FRW optimality: {}'.format(record['frw_optgap']))
    print('>>> BCW optimality: {}'.format(record['bcw_optgap']))
    # print('>>> FIX optimality: {}'.format(record['fix_optgap']))
    print('>>> PRG optimality: {}'.format(record['prg_optgap']))

    mark_section('Wrapping up the execution with the following solutions...')
    print('>>> LRZ solution: {}'.format('-'.join(warm_lrz_solution.values())))
    print('>>> NET solution: {}'.format('-'.join(warm_net_solution.values())))
    print('>>> FRW solution: {}'.format('-'.join(frw_solution.values())))
    print('>>> BCW solution: {}'.format('-'.join(bcw_solution.values())))
    # print('>>> FIX solution: {}'.format('-'.join(fix_solution.values())))
    print('>>> PRG solution: {}'.format('-'.join(prg_solution.values())))

if __name__ == '__main__':

    main()