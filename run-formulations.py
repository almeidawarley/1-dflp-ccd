import argparse as ap
import recording as rc
import common as cm

import network as nt
import original as og

def main():

    parser = ap.ArgumentParser(description = 'Run relevant formulations for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    parser.add_argument('-p', '--project', default = 'dsflp-c', type = str, help = 'Instance project name')
    parser.add_argument('-m', '--methods', default =  0, type = str, help = 'Method identification number')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')
    instance = cm.load_instance(args.keyword, args.project)
    instance.print_instance()
    record = rc.load_record(args.project, instance)

    cm.mark_section('Identifying solution for warm start')
    if 'warm_solution' in record.keys():
        warm_solution = instance.unpack_solution(record['warm_solution'])
    else:
        warm_solution = instance.empty_solution()

    cm.mark_section('Solving the DSFLP-C-LRZ formulation')
    formulation1 = og.linearized(instance)

    if args.methods == '1' or args.methods == '0':
        cm.mark_section('Cold MIP (i.e., without warm start)')
        metadata = formulation1.solve('cold_lrz')
        record = rc.update_record(record, metadata)

    if args.methods == '0':
        cm.mark_section('Warm MIP (i.e., with a warm start)')
        formulation1.heaten(warm_solution)
        metadata = formulation1.solve('warm_lrz')
        record = rc.update_record(record, metadata)

    if args.methods == '2' or args.methods == '0':
        cm.mark_section('Linear programming relaxation bound')
        metadata = formulation1.bound('rlx_lrz')
        record = rc.update_record(record, metadata)

    cm.mark_section('Solving the DSFLP-C-NET formulation')
    formulation2 = nt.network(instance)

    if args.methods == '3' or args.methods == '0':
        cm.mark_section('Cold MIP (i.e., without warm start)')
        metadata = formulation2.solve('cold_net')
        record = rc.update_record(record, metadata)

    if args.methods == '0':
        cm.mark_section('Warm MIP (i.e., with a warm start)')
        formulation2.heaten(warm_solution)
        metadata = formulation2.solve('warm_net')
        record = rc.update_record(record, metadata)

    if args.methods == '4' or args.methods == '0':
        cm.mark_section('Linear programming relaxation bound')
        metadata = formulation2.bound('rlx_net')
        record = rc.update_record(record, metadata)

    cm.mark_section('Solving the DSFLP-C-NLR formulation')
    formulation3 = og.nonlinear(instance)

    if args.methods == '0':

        cm.mark_section('Cold MIP (i.e., without warm start)')
        metadata = formulation3.solve('cold_nlr')
        record = rc.update_record(record, metadata)

        cm.mark_section('Warm MIP (i.e., with a warm start)')
        formulation3.heaten(warm_solution)
        metadata = formulation3.solve('warm_nlr')
        record = rc.update_record(record, metadata)

        # cm.mark_section('Linear programming relaxation bound')
        # metadata = formulation3.bound('rlx_nlr')
        # record = rc.update_record(record, metadata)

    if args.methods == '0':
        for approach in ['lrz', 'nlr', 'net']:
            print('> {} formulation: {} [{}]'.format(approach.upper(), record['cold_{}_objective'.format(approach)], record['cold_{}_solution'.format(approach)]))

if __name__ == '__main__':

    main()