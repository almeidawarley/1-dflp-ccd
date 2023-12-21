import instance as ic
import argparse as ap
import recording as rc

import benders as bd

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def main():

    parser = ap.ArgumentParser(description = 'Run relevant formulations for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-c', type = str, help = 'Instance project name')
    args = parser.parse_args()

    mark_section('Generating instance parameters')
    instance = ic.instance(args.keyword, args.project)
    instance.print_instance()
    record = rc.load_record(args.project, instance)

    mark_section('Solving with standard Benders')
    benders1 = bd.benders(instance, 'duality')
    metadata = benders1.solve_std('bsd')
    record = rc.update_record(record, metadata)

    mark_section('Solving with branch-and-Benders')
    benders2 = bd.benders(instance, 'duality')
    metadata = benders2.solve_bbc('bdd')
    record = rc.update_record(record, metadata)

    print(metadata)

if __name__ == '__main__':

    main()