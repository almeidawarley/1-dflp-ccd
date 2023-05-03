import instance as ic
import formulation as fm
import heuristic as hr
import validation as vd
import argparse as ap
import recording as rc

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def compute_gap(major, minor):
    return round((major - minor) / major, 4)

def main(seed):

    mark_section('Generating instance information based on the parameters...')
    instance = ic.instance('rnd2', seed)
    instance.print_instance()

    mark_section('Logging instance parameters read from file ...')
    record = rc.create_record('prober', instance)

    mark_section('Applying the greedy heuristic to the instance...')
    hrs_solution, hrs_objective = hr.greedy_heuristic(instance)
    print('Heuristic solution: [{}] {}'.format(hrs_objective, hrs_solution))
    record = rc.update_record(record, {
        'hrs_objective': hrs_objective,
        'hrs_solution': '-'.join(hrs_solution.values())
    })

    mark_section('Building the 1-DFLP-RA for the instance...')
    mip, mip_variable = fm.build_fancy(instance)
    mip.write('archives/mip-{}.lp'.format(instance.keyword))

    mark_section('Solving the LPR of the 1-DFLP-RA model...')
    lpr = mip.relax()
    lpr.optimize()
    lpr.write('archives/lpr-{}.sol'.format(instance.keyword))
    lpr_objective = round(lpr.objVal, 2)
    lpr_runtime = round(lpr.runtime, 2)
    print('Optimal LPR solution: [{}] no interpretable solution'.format(round(lpr.objVal, 2)))
    '''
    with open('lpr.csv', 'w') as content:
        for v in lpr.getVars():
            content.write('{},{}\n'.format(v.varName, v.x))
    '''
    record = rc.update_record(record, {
        'lpr_objective': lpr_objective,
        'lpr_runtime': lpr_runtime,
        'lpr_status': lpr.status
    })

    mark_section('Solving the MIP of the 1-DFLP-RA model...')
    fm.warm_start(instance, mip_variable, hrs_solution)
    mip.optimize()
    mip.write('archives/mip-{}.sol'.format(instance.keyword))
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
        'hrs_optgap': compute_gap(mip_objective, hrs_objective)
    })
    '''
    with open('mip.csv', 'w') as content:
        for v in mip.getVars():
            content.write('{},{}\n'.format(v.varName, v.x))
    '''

    mark_section('Validating the solution of the 1-DFLP-RA analytically...')
    analytical = vd.evaluate_solution(instance, mip_solution)
    validation = vd.is_equal(mip_objective, analytical, 0.1)
    record = rc.update_record(record, {
        'sanity_check': validation
    })
    print('>>> Sanity check: {} = {}? {} <<<'.format(mip_objective, analytical, validation))

    mark_section('Wrapping up the execution with sanity check {}!'.format(validation))

    with open('prober.csv', 'a') as content:
        content.write(rc.format_record(record))

    print('>>>>>>>>> Heuristic gap: {}'.format(record['hrs_optgap']))
    print('>>>>>>>>> MIP objective: {}'.format(record['mip_objective']))
    print('>>>>>>>>> HRS objective: {}'.format(record['hrs_objective']))
    print('>>>>>>>>> MIP solution: {}'.format('-'.join(mip_solution.values())))
    print('>>>>>>>>> HRS solution: {}'.format('-'.join(hrs_solution.values())))

    if record['hrs_optgap'] >= 0.5:
        _ = input('Found hard counter example!!!')

for i in range(0, 1000):
    main(i)