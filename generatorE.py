import argparse as ap
import json as js

parser = ap.ArgumentParser(description = 'Generate experimental 1-DFLP-RA instances')
parser.add_argument('project', type = str, help = 'Project name to identify experimental procedure')
parser.add_argument('--letter', type = str, default = 'E', help = 'Letter identifying the instance set')
parser.add_argument('--simulate', action = 'store_true', help = 'Simulate creation without writing files')
args = parser.parse_args()

counter = 0

# Seeds for random number generation
S = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# Grid size
L = [3, 5, 7]
# Number of periods
T = [5, 10, 15, 20]
# Maximum radius
H = [50, 75, 99]
# Number of options
O = [0]

with open('details-{}.txt'.format(args.project),'w') as details:
    details.write('S : {}\n'.format(S))
    details.write('L : {}\n'.format(L))
    details.write('T : {}\n'.format(T))
    details.write('O : {}\n'.format(O))
    details.write('H : {}\n'.format(H))

with open('commands-{}.sh'.format(args.project),'w') as commands:
    for s in S:
        for l in L:
            for t in T:
                for h in H:
                     for o in O:
                          if counter >= 0:

                            instance = {}

                            instance['S'] = s
                            instance['L'] = l
                            instance['T'] = t

                            instance['H'] = h
                            instance['O'] = o

                            keyword = '{}-{}-{}-{}-{}-{}'.format(args.letter, s, l, str(t).zfill(2), h, o)

                            if not args.simulate:

                                with open('{}/{}.json'.format('instances', keyword), 'w') as output:
                                    js.dump(instance, output)

                                with open('{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                    output.write('#!/bin/bash\n')

                                    output.write('#SBATCH --time=12:00:00\n')
                                    output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                    output.write('#SBATCH --output={}.out\n'.format(keyword))
                                    output.write('#SBATCH --account=def-jenasanj\n')
                                    output.write('#SBATCH --mem=30GB\n')
                                    output.write('#SBATCH --cpus-per-task=1\n')
                                    output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                    output.write('#SBATCH --mail-type=FAIL\n')

                                    output.write('cd ~/shortcut/\n')
                                    output.write('python main.py -p {} {}\n'.format(args.project, keyword))

                                commands.write('dos2unix ../scripts/{}.sh\n'.format(keyword))
                                commands.write('sbatch ../scripts/{}.sh\n'.format(keyword))

                            else:

                                print(keyword)

                            counter += 1

print('Done generating {} instances and scripts'.format(counter))