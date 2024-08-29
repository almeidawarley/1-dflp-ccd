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

    cm.mark_section('Solving with branch-and-Benders')

    cm.mark_section('External subproblems')
    benders1 = bd.benders(instance, 'external')
    metadata = benders1.solve_bbc('bbe')
    record = rc.update_record(record, metadata)

if __name__ == '__main__':

    main()