import argparse as ap
import recording as rc
import common as cm

import heuristic as hr

def main():

    parser = ap.ArgumentParser(description = 'Run relevant heuristics for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-c', type = str, help = 'Instance project name')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')
    instance = cm.load_instance(args.keyword, args.project)
    instance.print_instance()
    record = rc.load_record(args.project, instance)

    warmest_solution = '-'.join([instance.depot for _ in instance.periods])
    warmest_objective = 0.

    cm.mark_section('Solving with the PRG heuristic')
    heuristic1 = hr.progressive(instance)
    metadata = heuristic1.solve('prg')
    record = rc.update_record(record, metadata)
    if metadata['prg_objective'] > warmest_objective:
        warmest_solution = metadata['prg_solution']
        warmest_objective = metadata['prg_objective']

    cm.mark_section('Solving with the FRW heuristic')
    heuristic2 = hr.forward(instance)
    metadata = heuristic2.solve('frw')
    record = rc.update_record(record, metadata)
    if metadata['frw_objective'] > warmest_objective:
        warmest_solution = metadata['frw_solution']
        warmest_objective = metadata['frw_objective']

    cm.mark_section('Solving with the BCW heuristic')
    heuristic3 = hr.backward(instance)
    metadata = heuristic3.solve('bcw')
    record = rc.update_record(record, metadata)
    if metadata['bcw_objective'] > warmest_objective:
        warmest_solution = metadata['bcw_solution']
        warmest_objective = metadata['bcw_objective']

    cm.mark_section('Solving with the RND heuristic')
    heuristic4 = hr.random(instance)
    metadata = heuristic4.solve('rnd')
    record = rc.update_record(record, metadata)
    if metadata['rnd_objective'] > warmest_objective:
        warmest_solution = metadata['rnd_solution']
        warmest_objective = metadata['rnd_objective']

    cm.mark_section('Solving with the EML heuristic')
    heuristic5 = hr.emulation(instance)
    metadata = heuristic5.solve('eml')
    record = rc.update_record(record, metadata)
    try:
        record['warm_objective']
        if metadata['eml_objective'] > float(record['warm_objective']):
            exit('Run everything again, EML gives warmest objevtive')
    except Exception as e:
        print('Exception: {}'.format(e))
    if metadata['eml_objective'] > warmest_objective:
        warmest_solution = metadata['eml_solution']
        warmest_objective = metadata['eml_objective']

    record = rc.update_record(record, {
        'warm_solution': warmest_solution,
        'warm_objective': warmest_objective
    })

    for approach in ['rnd', 'eml', 'frw', 'bcw', 'prg']:
        print('> {} heuristic: {} [{}]'.format(approach.upper(), record['{}_objective'.format(approach)], record['{}_solution'.format(approach)]))

if __name__ == '__main__':

    main()