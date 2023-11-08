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

    warm_objective = max(rnd_objective, frw_objective, bcw_objective, fix_objective, prg_objective)
    if warm_objective == rnd_objective:
        warm_solution = rnd_solution
    elif warm_objective == frw_objective:
        warm_solution = frw_solution
    elif warm_objective == bcw_objective:
        warm_solution = bcw_solution
    elif warm_objective == fix_objective:
        warm_solution = fix_solution
    elif warm_objective == prg_objective:
        warm_solution = prg_solution
    else:
        raise Exception('No warm start solution found')

    mark_section('Building the DSFLP-DAR formulation...')
    warm_mip, warm_mip_variable = fm.build_linearized_main(instance)
    cold_mip, cold_mip_variable = fm.build_linearized_main(instance)
    warm_rf2, warm_rf2_variable = fm.build_reformulated2_main(instance)
    cold_rf2, cold_rf2_variable = fm.build_reformulated2_main(instance)

    mark_section('Solving the LPRX of the DSFLP-DAR model...')
    lprx_mip, lprx_mip_variable = fm.build_linearized_lprx(instance)
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

    mark_section('Solving warm MIP of the DSFLP-DAR model...')
    fm.warm_start(instance, warm_mip_variable, warm_solution)
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

    mark_section('Solving the LPRX of the DSFLP-DAR-R2 model...')
    lprx_rf2, lprx_rf2_variable = fm.build_reformulated2_lprx(instance)
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

    fm.warm_start(instance, warm_rf2_variable, warm_solution)

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

    record = rc.update_record(record, {
        'rf2_intgap': compute_gap(lprx_rf2_objective, cold_rf2_objective),
        'mip_intgap': compute_gap(lprx_mip_objective, warm_mip_objective),
        'rnd_optgap': compute_gap(warm_mip_objective, rnd_objective),
        'frw_optgap': compute_gap(warm_mip_objective, frw_objective),
        'bcw_optgap': compute_gap(warm_mip_objective, bcw_objective),
        'fix_optgap': compute_gap(warm_mip_objective, fix_objective),
        'prg_optgap': compute_gap(warm_mip_objective, prg_objective)
    })

    mark_section('Validating the solution of the DSFLP-DAR analytically...')
    reference = vd.evaluate_solution(instance, warm_mip_solution)
    record = rc.update_record(record, {
        'warm_mip_check': vd.is_equal(warm_mip_objective, reference, 0.1),
        'cold_mip_check': vd.is_equal(cold_mip_objective, reference, 0.1),
        'warm_rf2_check': vd.is_equal(warm_rf2_objective, reference, 0.1),
        'cold_rf2_check': vd.is_equal(cold_rf2_objective, reference, 0.1)
    })

    assert(record['warm_mip_check'] == True or record['warm_mip_status'] != 2)
    assert(record['cold_mip_check'] == True or record['cold_mip_status'] != 2)
    assert(record['warm_rf2_check'] == True or record['warm_rf2_status'] != 2)
    assert(record['cold_rf2_check'] == True or record['cold_rf2_status'] != 2)

    for method in ['1', '2']:

        mark_section('Emulating the DSFLP-DAR through DSFLP-{}...'.format(method))
        eml, eml_variable = fm.build_simplified_main(instance, method)
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

    mark_section('Wrapping up the execution with the following objectives...')
    print('>>> MIP objective: {}'.format(record['warm_mip_objective']))
    print('>>> FRW objective: {}'.format(record['frw_objective']))
    print('>>> BCW objective: {}'.format(record['bcw_objective']))
    print('>>> FIX objective: {}'.format(record['fix_objective']))
    print('>>> PRG objective: {}'.format(record['prg_objective']))

    mark_section('Wrapping up the execution with the following optimality gaps...')
    print('>>> FRW optimality: {}'.format(record['frw_optgap']))
    print('>>> BCW optimality: {}'.format(record['bcw_optgap']))
    print('>>> FIX optimality: {}'.format(record['fix_optgap']))
    print('>>> PRG optimality: {}'.format(record['prg_optgap']))

    mark_section('Wrapping up the execution with the following solutions...')
    print('>>> MIP solution: {}'.format('-'.join(warm_mip_solution.values())))
    print('>>> FRW solution: {}'.format('-'.join(frw_solution.values())))
    print('>>> BCW solution: {}'.format('-'.join(bcw_solution.values())))
    print('>>> FIX solution: {}'.format('-'.join(fix_solution.values())))
    print('>>> PRG solution: {}'.format('-'.join(prg_solution.values())))

    '''
    if record['rf2_intgap'] < record['mip_intgap']:
        print('Main formulation:')
        for period in instance.periods:
            for location in instance.locations:
                print('y^{}{}{}_{}{}{} = {}'.format('{', period, '}', '{', location, '}', lprx_mip_variable['y'][period, location].x))
        for period in instance.periods:
            for customer in instance.customers:
                print('w^{}{}{}_{}{}{}{} = {}'.format('{', period, '}', '{', customer, customer, '}', lprx_mip_variable['w'][period, customer, customer].x))
        print('Reformulation #2:')
        for period in instance.periods:
            for location in instance.locations:
                print('y^{}_{} = {}'.format(period, location, lprx_rf2_variable['y'][period, location].x))
        print('yes')
    else:
        print('no')

    print(record['mip_intgap'])
    '''

if __name__ == '__main__':

    main()