import argparse as ap
import recording as rc
import common as cm
import network as nt

def main():

    parser = ap.ArgumentParser(description = 'Run network formulation for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')
    instance = cm.load_instance(args.keyword)
    instance.print_instance()

    cm.mark_section('Solving the DSFLP-C-NET formulation')
    formulation1 = nt.network(instance)

    cm.mark_section('Cold MIP (i.e., without warm start)')
    metadata = formulation1.solve('cold_net')
    rc.update_record(args.keyword, metadata)

    '''
    cm.mark_section('Warm MIP (i.e., with a warm start)')
    formulation1.heaten(warm_solution)
    metadata = formulation1.solve('warm_net')
    rc.update_record(args.keyword, metadata)
    '''

    cm.mark_section('Linear programming relaxation bound')
    metadata = formulation1.bound('rlx_net')
    rc.update_record(args.keyword, metadata)

if __name__ == '__main__':

    main()