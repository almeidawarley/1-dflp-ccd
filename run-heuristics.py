import argparse as ap
import recording as rc
import common as cm
import heuristic as hr

def main():

    parser = ap.ArgumentParser(description = 'Run relevant heuristics for some DSFLP-C instance')
    parser.add_argument('keyword', type = str, help = 'Instance keyword following established patterns')
    args = parser.parse_args()

    cm.mark_section('Generating instance parameters')
    instance = cm.load_instance(args.keyword)
    instance.print_instance()

    cm.mark_section('Solving with the EML heuristic')
    heuristic1 = hr.emulation(instance)
    metadata = heuristic1.solve('eml')
    rc.update_record(args.keyword, metadata)

    cm.mark_section('Solving with the BCW heuristic')
    heuristic2 = hr.backward(instance)
    metadata = heuristic2.solve('bcw')
    rc.update_record(args.keyword, metadata)

    cm.mark_section('Solving with the FRW heuristic')
    heuristic3 = hr.forward(instance)
    metadata = heuristic3.solve('frw')
    rc.update_record(args.keyword, metadata)

    cm.mark_section('Solving with the RND heuristic')
    heuristic4 = hr.random(instance)
    metadata = heuristic4.solve('rnd')
    rc.update_record(args.keyword, metadata)

if __name__ == '__main__':

    main()