import argparse as ap
import recording as rc
import common as cm
import benders as bd

def main():

    parser = ap.ArgumentParser(description = 'Run hybrid Benders for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')

    instance = cm.load_instance(args.keyword)
    instance.print_instance()

    cm.mark_section('Solving with branch-and-Benders')

    cm.mark_section('External subproblems, separating fractional and integer solutions')
    benders1 = bd.benders(instance, 'external', True)
    metadata = benders1.solve('bbh')
    rc.update_record(args.keyword, metadata)

if __name__ == '__main__':

    main()