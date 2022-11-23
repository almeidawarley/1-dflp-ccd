import json as js
import sys

experiment = sys.argv[1]

counter = 0

S = [0,1,2,3,4,5,6,7,8,9]

I = [10, 20]
J = [50, 100]
T = [7, 14]

zeta = [50, 100]
eta = [50, 100]
theta = [25, 50, 75]

replenishment = ['linear', 'exponential']
absorption = ['linear', 'exponential']

with open('commandsB.sh','w') as commands:
    for i in I:
        for s in S:
            for j in J:
                for t in T:
                    for r in replenishment:
                        for a in absorption:
                            for z in zeta:
                                for e in eta:
                                    for h in theta:

                                        if counter >= 0:

                                            keyword = '{}-{}-{}-{}-{}-{}-{}-{}-{}-{}'.format('B', s, i, j, t, r, z, a, e, h)
                                            instance = {}
                                            instance['S'] = s
                                            instance['I'] = i
                                            instance['J'] = j
                                            instance['T'] = t
                                            instance['replenishment'] = r
                                            instance['zeta'] = z
                                            instance['absorption'] = a
                                            instance['eta'] = e
                                            instance['theta'] = h

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
                                                # output.write('wandb offline\n')
                                                output.write('python main.py -p {} {}\n'.format(experiment, keyword))

                                            commands.write('dos2unix ../scripts/{}.sh\n'.format(keyword))
                                            commands.write('sbatch ../scripts/{}.sh\n'.format(keyword))

                                        counter += 1

print('Done generating {} instances and scripts'.format(counter))