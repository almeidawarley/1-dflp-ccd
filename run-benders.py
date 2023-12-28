import argparse as ap
import recording as rc
import common as cm

import benders as bd

def main():

    parser = ap.ArgumentParser(description = 'Run relevant formulations for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-c', type = str, help = 'Instance project name')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')

    instance = cm.load_instance(args.keyword, args.project)
    instance.print_instance()
    record = rc.load_record(args.project, instance)

    cm.mark_section('Identifying solution for warm start')
    if 'warm_objective' in record.keys():
        cutoff = float(record['warm_objective'])
    else:
        cutoff = 0.

    cm.mark_section('Solving with branch-and-Benders')

    cm.mark_section('Analytical subproblems')
    benders1 = bd.benders(instance, 'analytical')
    metadata = benders1.solve_bbc('bba', cutoff)
    record = rc.update_record(record, metadata)

    cm.mark_section('Duality subproblems')
    benders2 = bd.benders(instance, 'duality')
    metadata = benders2.solve_bbc('bbd', cutoff)
    record = rc.update_record(record, metadata)

    cm.mark_section('Solving with standard Benders')

    cm.mark_section('Analytical subproblems')
    benders3 = bd.benders(instance, 'analytical')
    metadata = benders3.solve_std('bsa', cutoff)
    record = rc.update_record(record, metadata)

    cm.mark_section('Duality subproblems')
    benders4 = bd.benders(instance, 'duality')
    metadata = benders4.solve_std('bsd', cutoff)
    record = rc.update_record(record, metadata)

    for approach in ['bba', 'bbd', 'bsa', 'bsd']:
        print('> {} approach: {} <{}> [{}]'.format(approach.upper(), record['{}_objective'.format(approach)], record['{}_runtime'.format(approach)], record['{}_solution'.format(approach)]))

if __name__ == '__main__':

    main()