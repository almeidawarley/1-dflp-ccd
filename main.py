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

    parser = ap.ArgumentParser(description = 'Run all approaches to solve the DSFLP-DAR for some instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-dar', type = str, help = 'Instance project name')
    args = parser.parse_args()

    mark_section('Generating instance based on the parameters...')
    instance = ic.instance(args.keyword, args.project)
    instance.print_instance()

    mark_section('Logging instance parameters read from file...')
    record = rc.create_record(args.project, instance)

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

    mark_section('Building the DSFLP-DAR formulation...')
    warm_mip, warm_mip_variable = fm.build_linearized(instance)
    cold_mip, cold_mip_variable = fm.build_linearized(instance)
    warm_nlr, warm_nlr_variable = fm.build_nonlinear(instance)
    cold_nlr, cold_nlr_variable = fm.build_nonlinear(instance)
    warm_rf1, warm_rf1_variable = fm.build_reformulation1(instance)
    cold_rf1, cold_rf1_variable = fm.build_reformulation1(instance)
    warm_rf2, warm_rf2_variable = fm.build_reformulation2(instance)
    cold_rf2, cold_rf2_variable = fm.build_reformulation2(instance)

    mark_section('Solving the LPRX of the DSFLP-DAR model...')
    lprx_mip, _ = fm.build_relaxation(instance, fm.build_linearized)
    # lprx_mip.write('archives/{}-lprx_mip.lp'.format(instance.keyword))
    lprx_mip.optimize()
    lprx_mip_objective = round(lprx_mip.objVal, 2)
    lprx_mip_runtime = round(lprx_mip.runtime, 2)
    print('Optimal LPRX MIP solution: [{}] no interpretable solution'.format(round(lprx_mip.objVal, 2)))
    record = rc.update_record(record, {
        'lprx_mip_objective': lprx_mip_objective,
        'lprx_mip_runtime': lprx_mip_runtime,
        'lprx_mip_status': lprx_mip.status
    })

    mark_section('Solving cold MIP of the DSFLP-DAR model...')
    # cold_mip.write('archives/{}-cold_mip.lp'.format(instance.keyword))
    cold_mip.optimize()
    cold_mip_solution = fm.format_solution(instance, cold_mip, cold_mip_variable)
    cold_mip_objective = round(cold_mip.objVal, 2)
    cold_mip_runtime = round(cold_mip.runtime, 2)
    print('Optimal cold MIP solution: [{}] {}'.format(cold_mip_objective, cold_mip_solution))
    record = rc.update_record(record,{
        'cold_mip_objective': cold_mip_objective,
        'cold_mip_solution': '-'.join(cold_mip_solution.values()),
        'cold_mip_runtime': cold_mip_runtime,
        'cold_mip_status': cold_mip.status,
        'cold_mip_optgap': cold_mip.MIPGap
    })

    mark_section('Solving cold NLR of the DSFLP-DAR model...')
    # cold_nlr.write('archives/{}-cold_nlr.lp'.format(instance.keyword))
    cold_nlr.optimize()
    cold_nlr_solution = fm.format_solution(instance, cold_nlr, cold_nlr_variable)
    cold_nlr_objective = round(cold_nlr.objVal, 2)
    cold_nlr_runtime = round(cold_nlr.runtime, 2)
    print('Optimal cold NLR solution: [{}] {}'.format(cold_nlr_objective, cold_nlr_solution))
    record = rc.update_record(record,{
        'cold_nlr_objective': cold_nlr_objective,
        'cold_nlr_solution': '-'.join(cold_nlr_solution.values()),
        'cold_nlr_runtime': cold_nlr_runtime,
        'cold_nlr_status': cold_nlr.status,
        'cold_nlr_optgap': cold_nlr.MIPGap
    })

    mark_section('Identifying the warmest objective value...')
    warm_objective = max(rnd_objective, frw_objective, bcw_objective, prg_objective)
    if warm_objective == rnd_objective:
        fm.warm_start(instance, warm_mip_variable, rnd_solution)
        fm.warm_start(instance, warm_nlr_variable, rnd_solution)
        fm.warm_start(instance, warm_rf1_variable, rnd_solution)
        fm.warm_start(instance, warm_rf2_variable, rnd_solution)
    elif warm_objective == frw_objective:
        fm.warm_start(instance, warm_mip_variable, frw_solution)
        fm.warm_start(instance, warm_nlr_variable, frw_solution)
        fm.warm_start(instance, warm_rf1_variable, frw_solution)
        fm.warm_start(instance, warm_rf2_variable, frw_solution)
    elif warm_objective == bcw_objective:
        fm.warm_start(instance, warm_mip_variable, bcw_solution)
        fm.warm_start(instance, warm_nlr_variable, bcw_solution)
        fm.warm_start(instance, warm_rf1_variable, bcw_solution)
        fm.warm_start(instance, warm_rf2_variable, bcw_solution)
    elif warm_objective == prg_objective:
        fm.warm_start(instance, warm_mip_variable, prg_solution)
        fm.warm_start(instance, warm_nlr_variable, prg_solution)
        fm.warm_start(instance, warm_rf1_variable, prg_solution)
        fm.warm_start(instance, warm_rf2_variable, prg_solution)
    else:
        raise Exception('No warm start solution found')

    mark_section('Solving warm MIP of the DSFLP-DAR model...')
    # warm_mip.write('archives/{}-warm_mip.lp'.format(instance.keyword))
    warm_mip.optimize()
    warm_mip_solution = fm.format_solution(instance, warm_mip, warm_mip_variable)
    warm_mip_objective = round(warm_mip.objVal, 2)
    warm_mip_runtime = round(warm_mip.runtime, 2)
    print('Optimal warm MIP solution: [{}] {}'.format(warm_mip_objective, warm_mip_solution))
    record = rc.update_record(record,{
        'warm_mip_objective': warm_mip_objective,
        'warm_mip_solution': '-'.join(warm_mip_solution.values()),
        'warm_mip_runtime': warm_mip_runtime,
        'warm_mip_status': warm_mip.status,
        'warm_mip_optgap': warm_mip.MIPGap
    })

    mark_section('Solving warm NLR of the DSFLP-DAR model...')
    # warm_nlr.write('archives/{}-warm_nlr.lp'.format(instance.keyword))
    warm_nlr.optimize()
    warm_nlr_solution = fm.format_solution(instance, warm_nlr, warm_nlr_variable)
    warm_nlr_objective = round(warm_nlr.objVal, 2)
    warm_nlr_runtime = round(warm_nlr.runtime, 2)
    print('Optimal warm NLR solution: [{}] {}'.format(warm_nlr_objective, warm_nlr_solution))
    record = rc.update_record(record,{
        'warm_nlr_objective': warm_nlr_objective,
        'warm_nlr_solution': '-'.join(warm_nlr_solution.values()),
        'warm_nlr_runtime': warm_nlr_runtime,
        'warm_nlr_status': warm_nlr.status,
        'warm_nlr_optgap': warm_nlr.MIPGap
    })

    mark_section('Solving the LPRX of the DSFLP-DAR-R1 model...')
    lprx_rf1, _ = fm.build_relaxation(instance, fm.build_reformulation1)
    # lprx_rf1.write('archives/{}-lprx_rf1.lp'.format(instance.keyword))
    lprx_rf1.optimize()
    lprx_rf1_objective = round(lprx_rf1.objVal, 2)
    lprx_rf1_runtime = round(lprx_rf1.runtime, 2)
    print('Optimal LPRX R1 solution: [{}] no interpretable solution'.format(round(lprx_rf1.objVal, 2)))
    record = rc.update_record(record, {
        'lprx_rf1_objective': lprx_rf1_objective,
        'lprx_rf1_runtime': lprx_rf1_runtime,
        'lprx_rf1_status': lprx_rf1.status
    })

    mark_section('Solving the LPRX of the DSFLP-DAR-R2 model...')
    lprx_rf2, _ = fm.build_relaxation(instance, fm.build_reformulation1)
    # lprx_rf2.write('archives/{}-lprx_rf2.lp'.format(instance.keyword))
    lprx_rf2.optimize()
    lprx_rf2_objective = round(lprx_rf2.objVal, 2)
    lprx_rf2_runtime = round(lprx_rf2.runtime, 2)
    print('Optimal LPRX R2 solution: [{}] no interpretable solution'.format(round(lprx_rf2.objVal, 2)))
    record = rc.update_record(record, {
        'lprx_rf2_objective': lprx_rf2_objective,
        'lprx_rf2_runtime': lprx_rf2_runtime,
        'lprx_rf2_status': lprx_rf2.status
    })

    mark_section('Solving cold MIP of the DSFLP-DAR-R1 model...')
    # cold_rf1.write('archives/{}-cold_rf1.lp'.format(instance.keyword))
    cold_rf1.optimize()
    cold_rf1_solution = fm.format_solution(instance, cold_rf1, cold_rf1_variable)
    cold_rf1_objective = round(cold_rf1.objVal, 2)
    cold_rf1_runtime = round(cold_rf1.runtime, 2)
    print('Optimal cold RF1 solution: [{}] {}'.format(cold_rf1_objective, cold_rf1_solution))
    record = rc.update_record(record,{
        'cold_rf1_objective': cold_rf1_objective,
        'cold_rf1_solution': '-'.join(cold_rf1_solution.values()),
        'cold_rf1_runtime': cold_rf1_runtime,
        'cold_rf1_status': cold_rf1.status,
        'cold_rf1_optgap': cold_rf1.MIPGap
    })

    mark_section('Solving cold MIP of the DSFLP-DAR-R2 model...')
    # cold_rf2.write('archives/{}-cold_rf2.lp'.format(instance.keyword))
    cold_rf2.optimize()
    cold_rf2_solution = fm.format_solution(instance, cold_rf2, cold_rf2_variable)
    cold_rf2_objective = round(cold_rf2.objVal, 2)
    cold_rf2_runtime = round(cold_rf2.runtime, 2)
    print('Optimal cold RF2 solution: [{}] {}'.format(cold_rf2_objective, cold_rf2_solution))
    record = rc.update_record(record,{
        'cold_rf2_objective': cold_rf2_objective,
        'cold_rf2_solution': '-'.join(cold_rf2_solution.values()),
        'cold_rf2_runtime': cold_rf2_runtime,
        'cold_rf2_status': cold_rf2.status,
        'cold_rf2_optgap': cold_rf2.MIPGap
    })

    mark_section('Solving warm MIP of the DSFLP-DAR-R1 model...')
    # warm_rf1.write('archives/{}-warm_rf1.lp'.format(instance.keyword))
    warm_rf1.optimize()
    warm_rf1_solution = fm.format_solution(instance, warm_rf1, warm_rf1_variable)
    warm_rf1_objective = round(warm_rf1.objVal, 2)
    warm_rf1_runtime = round(warm_rf1.runtime, 2)
    print('Optimal warm RF1 solution: [{}] {}'.format(warm_rf1_objective, warm_rf1_solution))
    record = rc.update_record(record,{
        'warm_rf1_objective': warm_rf1_objective,
        'warm_rf1_solution': '-'.join(warm_rf1_solution.values()),
        'warm_rf1_runtime': warm_rf1_runtime,
        'warm_rf1_status': warm_rf1.status,
        'warm_rf1_optgap': warm_rf1.MIPGap
    })

    mark_section('Solving warm MIP of the DSFLP-DAR-R2 model...')
    # warm_rf2.write('archives/{}-warm_rf2.lp'.format(instance.keyword))
    warm_rf2.optimize()
    warm_rf2_solution = fm.format_solution(instance, warm_rf2, warm_rf2_variable)
    warm_rf2_objective = round(warm_rf2.objVal, 2)
    warm_rf2_runtime = round(warm_rf2.runtime, 2)
    print('Optimal warm RF2 solution: [{}] {}'.format(warm_rf2_objective, warm_rf2_solution))
    record = rc.update_record(record,{
        'warm_rf2_objective': warm_rf2_objective,
        'warm_rf2_solution': '-'.join(warm_rf2_solution.values()),
        'warm_rf2_runtime': warm_rf2_runtime,
        'warm_rf2_status': warm_rf2.status,
        'warm_rf2_optgap': warm_rf2.MIPGap
    })

    mark_section('Computing relevant integrality/optimality gaps...')
    record = rc.update_record(record, {
        'rf1_intgap': compute_gap(lprx_rf1_objective, warm_rf1_objective),
        'rf2_intgap': compute_gap(lprx_rf2_objective, warm_rf2_objective),
        'mip_intgap': compute_gap(lprx_mip_objective, warm_mip_objective),
        'rnd_optgap': compute_gap(warm_mip_objective, rnd_objective),
        'frw_optgap': compute_gap(warm_mip_objective, frw_objective),
        'bcw_optgap': compute_gap(warm_mip_objective, bcw_objective),
        'prg_optgap': compute_gap(warm_mip_objective, prg_objective)
    })

    mark_section('Validating the solution of the DSFLP-DAR analytically...')
    reference = vd.evaluate_solution(instance, warm_mip_solution)
    record = rc.update_record(record, {
        'warm_rf1_check': vd.is_equal(warm_mip_objective, warm_rf1_objective, 0.1),
        'cold_rf1_check': vd.is_equal(warm_mip_objective, cold_rf1_objective, 0.1),
        'warm_rf2_check': vd.is_equal(warm_mip_objective, warm_rf2_objective, 0.1),
        'cold_rf2_check': vd.is_equal(warm_mip_objective, cold_rf2_objective, 0.1),
        'warm_mip_check': vd.is_equal(warm_mip_objective, reference, 0.1),
        'warm_nlr_check': vd.is_equal(warm_nlr_objective, reference, 0.1),
        'cold_mip_check': vd.is_equal(cold_mip_objective, reference, 0.1),
        'cold_nlr_check': vd.is_equal(cold_nlr_objective, reference, 0.1)
    })

    assert(record['warm_mip_check'] == True)
    assert(record['warm_nlr_check'] == True)
    assert(record['warm_rf2_check'] == True)
    # assert(record['cold_mip_check'] == True)
    # assert(record['cold_nlr_check'] == True)

    mark_section('Assessing meaning of DSFLP-DAR reformulations...')

    if not instance.has_identical_rewards():
        print('The DSFLP-DAR-R1 is only an heuristic, computing actual objective')
        cold_rf1_objective = vd.evaluate_solution(instance, cold_rf1_solution)
        warm_rf1_objective = vd.evaluate_solution(instance, warm_rf1_solution)
        record = rc.update_record(record, {
            'cold_rf1_objective': cold_rf1_objective,
            'cold_rf1_optgap': compute_gap(warm_mip_objective, cold_rf1_objective),
            'cold_rf1_optgap': compute_gap(warm_mip_objective, cold_rf1_objective),
            'warm_rf1_objective': warm_rf1_objective,
            'warm_rf1_optgap': compute_gap(warm_mip_objective, warm_rf1_objective),
            'warm_rf1_optgap': compute_gap(warm_mip_objective, warm_rf1_objective)
        })
    else:
        print('The DSFLP-DAR-R1 should be exact, no need to recompute objective')
        assert(record['warm_rf1_check'] == True)

    for method in ['1', '2']:

        mark_section('Emulating the DSFLP-DAR through DSFLP-{}...'.format(method))
        eml, eml_variable = fm.build_simple(instance, method)
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
            'em{}_optgap'.format(method): compute_gap(warm_mip_objective, eml_objective)
        })

    mark_section('Wrapping up the execution with the following information...')
    print('>>> MIP objective: {}'.format(record['warm_mip_objective']))
    print('>>> FRW objective: {}'.format(record['frw_objective']))
    print('>>> FRW optimality: {}'.format(record['frw_optgap']))
    print('>>> BCW optimality: {}'.format(record['bcw_optgap']))
    print('>>> PRG objective: {}'.format(record['prg_objective']))
    print('>>> PRG optimality: {}'.format(record['prg_optgap']))
    print('>>> MIP solution: {}'.format('-'.join(warm_mip_solution.values())))
    print('>>> FRW solution: {}'.format('-'.join(frw_solution.values())))
    print('>>> BCW solution: {}'.format('-'.join(bcw_solution.values())))
    print('>>> PRG solution: {}'.format('-'.join(prg_solution.values())))

if __name__ == '__main__':

    main()