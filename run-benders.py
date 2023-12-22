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

    cm.mark_section('Solving with standard Benders')

    cm.mark_section('Analytical subproblems')
    benders1 = bd.benders(instance, 'analytical')
    metadata = benders1.solve_std('bsa')
    record = rc.update_record(record, metadata)

    cm.mark_section('Duality subproblems')
    benders3 = bd.benders(instance, 'duality')
    metadata = benders3.solve_std('bsd')
    record = rc.update_record(record, metadata)

    cm.mark_section('Solving with branch-and-Benders')

    cm.mark_section('Analytical subproblems')
    benders2 = bd.benders(instance, 'analytical')
    metadata = benders2.solve_bbc('bba')
    record = rc.update_record(record, metadata)

    cm.mark_section('Duality subproblems')
    benders2 = bd.benders(instance, 'duality')
    metadata = benders2.solve_bbc('bdd')
    record = rc.update_record(record, metadata)

if __name__ == '__main__':

    main()