import argparse as ap
import recording as rc
import common as cm
import intuitive as iv

def main():

    parser = ap.ArgumentParser(description = 'Run  nonlinear intuitive formulation for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')
    instance = cm.load_instance(args.keyword)
    instance.print_instance()

    cm.mark_section('Solving the DSFLP-C-NLR formulation')
    formulation1 = iv.nonlinear(instance)

    cm.mark_section('Cold MIP (i.e., without warm start)')
    metadata = formulation1.solve('cold_nlr')
    rc.update_record(args.keyword, metadata)

    '''
    cm.mark_section('Warm MIP (i.e., with a warm start)')
    formulation1.heaten(warm_solution)
    metadata = formulation1.solve('warm_nlr')
    rc.update_record(args.keyword, metadata)
    '''

    # cm.mark_section('Linear programming relaxation bound')
    # metadata = formulation1.bound('rlx_nlr')
    # rc.update_record(args.keyword, metadata)

if __name__ == '__main__':

    main()