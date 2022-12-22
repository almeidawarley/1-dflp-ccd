import argparse as ap
import json as js

parser = ap.ArgumentParser(description = 'Generate experimental 1-DFLP-RA instances')
parser.add_argument('project', type = str, help = 'Project name to identify experimental procedure')
parser.add_argument('--letter', type = str, default = 'A', help = 'Letter identifying the instance set')
parser.add_argument('--simulate', action = 'store_true', help = 'Simulate creation without writing files')
args = parser.parse_args()

counter = 0

# Seeds for random number generation
S = [0,1,2,3,4,5,6,7,8,9]
# Number of locations
I = [10, 20]
# Number of time periods
T = [10, 30, 50]
# Customer profiles
C = ['hom', 'het']
# Replenishment profiles
R = ['abs', 'rel']
# Absorption profiles
A = ['abs', 'rel']
# Number of options
O = [0, 1, 2]
# Upper bounds
U = [10, 99]

with open('commands{}.sh'.format(args.letter),'w') as commands:
    for s in S:
        for i in I:
            # for j in J:
            for t in T:
                for c in C:
                    for r in R:
                        for a in A:
                            for o in O:
                                for u in U:

                                    j = i

                                    if counter >= 0:

                                        instance = {}

                                        instance['S'] = s
                                        instance['I'] = i
                                        instance['J'] = j
                                        instance['T'] = t

                                        instance['C'] = c
                                        instance['R'] = r
                                        instance['A'] = a
                                        instance['O'] = o
                                        instance['U'] = u

                                        keyword = '{}-{}-{}-{}-{}-{}-{}-{}-{}-{}'.format(args.letter, s, i, j, t, c, r, a, o, u)

                                        if not args.simulate:

                                            with open('{}/{}.json'.format('instances', keyword), 'w') as output:
                                                js.dump(instance, output)

                                            with open('{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                                output.write('#!/bin/bash\n')

                                                output.write('#SBATCH --time=12:00:00\n')
                                                output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                                output.write('#SBATCH --output={}.out\n'.format(keyword))
                                                output.write('#SBATCH --account=def-jenasanj\n')
                                                output.write('#SBATCH --mem=24576M\n')
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