import argparse as ap
import recording as rc
import common as cm

import benders as bd

def main():

    parser = ap.ArgumentParser(description = 'Run relevant formulations for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-c', type = str, help = 'Instance project name')
    parser.add_argument('-m', '--methods', default = '0', type = str, help = 'Method identification number')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')

    instance = cm.load_instance(args.keyword, args.project)
    instance.print_instance()
    record = rc.load_record(args.project, instance)

    '''
    cm.mark_section('Identifying solution for warm start')
    if 'warm_objective' in record.keys():
        cutoff = float(record['warm_objective'])
        incumbent = instance.unpack_solution(record['warm_solution'])
    else:
        cutoff = 0.
        incumbent = instance.empty_solution()
    '''

    cm.mark_section('Solving with branch-and-Benders')

    if args.methods == '1' or args.methods == '0':
        cm.mark_section('Analytical subproblems')
        benders1 = bd.benders(instance, 'analytical')
        metadata = benders1.solve_bbc('bba')
        record = rc.update_record(record, metadata)

    if args.methods == '2' or args.methods == '0':
        cm.mark_section('Duality subproblems')
        benders2 = bd.benders(instance, 'duality')
        metadata = benders2.solve_bbc('bbd')
        record = rc.update_record(record, metadata)

    cm.mark_section('Solving with standard Benders')

    if args.methods == '0':
        cm.mark_section('Analytical subproblems')
        benders3 = bd.benders(instance, 'analytical')
        metadata = benders3.solve_std('bsa')
        record = rc.update_record(record, metadata)

    if args.methods == '0':
        cm.mark_section('Duality subproblems')
        benders4 = bd.benders(instance, 'duality')
        metadata = benders4.solve_std('bsd')
        record = rc.update_record(record, metadata)

    if args.methods == '0':
        for approach in ['bba', 'bbd', 'bsa', 'bsd']:
            print('> {} approach: {} <{}> [{}]'.format(approach.upper(), record['{}_objective'.format(approach)], record['{}_runtime'.format(approach)], record['{}_solution'.format(approach)]))

if __name__ == '__main__':

    main()