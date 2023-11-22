import instance as ic
import argparse as ap
import benders1 as b1
import benders2 as b2
import recording as rc

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def main():

    parser = ap.ArgumentParser(description = 'Run relevant solution methods for some DSFLP-DAR instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-dar', type = str, help = 'Instance project name')
    args = parser.parse_args()

    mark_section('Generating instance based on the parameters...')
    instance = ic.instance(args.keyword, args.project)
    instance.print_instance()

    mark_section('Logging instance parameters read from file...')
    record = rc.load_record(args.project, instance)

    _, _, bds_metadata = b2.benders_decomposition(instance)
    record = rc.update_record(record, bds_metadata)
    _, _, bds_metadata = b1.benders_decomposition(instance, 5)
    record = rc.update_record(record, bds_metadata)
    _, _, bds_metadata = b1.benders_decomposition(instance, 's')
    record = rc.update_record(record, bds_metadata)

if __name__ == '__main__':

    main()