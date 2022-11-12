import instance as ic
import formulation as fm
import heuristic as hr
import validation as vd
import argparse as ap
import wandb as wb

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def main():

    parser = ap.ArgumentParser(description = 'Run 1-DFLP-RA for some instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', type = str, help = 'Project name on Weights & Biases for storing results')
    args = parser.parse_args()

    mark_section('Generating instance information based on the parameters...')
    instance = ic.instance(args.keyword)

    mark_section('Initiating a job for storing results at Weights & Biases ...')
    wb.init(project = args.project, config = instance.parameters)
    wb.save('instances/{}.json'.format(instance.keyword))
    wb.save('scripts/{}.sh'.format(instance.keyword))

    mark_section('Applying the greedy heuristic to the instance...')
    hrs_solution, hrs_objective = hr.greedy_heuristic(instance)
    print('Heuristic solution: [{}] {}'.format(hrs_objective, hrs_solution))
    wb.log({
        'hrs_objective': hrs_objective,
        'hrs_solution': '-'.join(hrs_solution.values())
    })

    mark_section('Building the 1-DFLP-RA for the instance...')
    mip, variable = fm.build_fancy(instance)
    mip.write('archives/{}.lp'.format(instance.keyword))
    wb.save('archives/{}.lp'.format(instance.keyword))

    mark_section('Solving the LPR of the 1-DFLP-RA model...')
    lpr = mip.relax()
    lpr.optimize()
    lpr.write('archives/lpr-{}.sol'.format(instance.keyword))
    wb.save('archives/lpr-{}.sol'.format(instance.keyword))
    lpr_objective = round(lpr.objVal, 2)
    lpr_runtime = round(lpr.runtime, 2)
    print('Optimal LPR solution: [{}] no interpretable solution'.format(round(lpr.objVal, 2)))
    wb.log({
        'lpr_objective': lpr_objective,
        'lpr_runtime': lpr_runtime,
        'lpr_status': lpr.status
    })

    mark_section('Solving the MIP of the 1-DFLP-RA model...')
    fm.warm_start(instance, variable, hrs_solution)
    mip.optimize()
    mip.write('archives/mip-{}.sol'.format(instance.keyword))
    wb.save('archives/mip-{}.sol'.format(instance.keyword))
    mip_solution = fm.format_solution(instance, mip, variable)
    mip_objective = round(mip.objVal, 2)
    mip_runtime = round(mip.runtime, 2)
    print('Optimal MIP solution: [{}] {}'.format(mip_objective, mip_solution))
    wb.log({
        'mip_objective': mip_objective,
        'mip_solution': '-'.join(mip_solution.values()),
        'mip_runtime': mip_runtime,
        'mip_status': mip.status,
        'mip_optgap': mip.MIPGap
    })

    mark_section('Validating the solution of the 1-DFLP-RA analytically...')
    analytical = vd.evaluate_solution(instance, mip_solution)
    validation = vd.is_equal(mip_objective, analytical)
    wb.log({
        'sanity_check': validation
    })

    for method in ['1', '2', '3']:

        mark_section('Approximating the 1-DFLP-RA by the #{} method...'.format(method))
        apr, variable = fm.build_simple(instance, method)
        apr.write('archives/ap{}-{}.lp'.format(method, instance.keyword))
        wb.save('archives/ap{}-{}.lp'.format(method, instance.keyword))
        apr.optimize()
        apr.write('archives/ap{}-{}.sol'.format(method, instance.keyword))
        wb.save('archives/ap{}-{}.sol'.format(method, instance.keyword))
        apr_solution = fm.format_solution(instance, apr, variable)
        apr_objective = vd.evaluate_solution(instance, apr_solution)
        apr_runtime = round(apr.runtime, 2)
        print('Approximate solution #{}: [{}] {}'.format(method, apr_objective, apr_solution))
        wb.log({
            'ap{}_objective'.format(method): apr_objective,
            'ap{}_solution'.format(method): '-'.join(apr_solution.values()),
            'ap{}_runtime'.format(method): apr_runtime,
            'ap{}_status'.format(method): apr.status
        })

    mark_section('Wrapping up the execution with sanity check {}!'.format(validation))

main()