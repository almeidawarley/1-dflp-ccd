import instance as ic
import argparse as ap
import benders as bd
import recording as rc

def mark_section(title):
    print('\n-----------------------------------------------------------------------------------\n')
    print(title)
    print('\n-----------------------------------------------------------------------------------\n')

def compute_gap(major, minor):
    return round((major - minor) / major, 4)

def compare_obj(objective1, objective2, tolerance = 1/10**4):
    if objective1 < objective2:
      objective1, objective2 = objective2, objective1
    gap = compute_gap(objective1, objective2)
    return gap <= tolerance

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

    bds_solution, bds_objective, bds_metadata = bd.benders_decomposition(instance)

    record = rc.update_record(record, bds_metadata)

if __name__ == '__main__':

    main()