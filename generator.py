import json as js

counter = 0

S = [0,1,2,3,4,5,6,7,8,9]

I = [10, 20]
T = [7, 14]

zeta = [1, 2, 3, 4]

replenishment = ['linear', 'exponential']
absorption = ['linear', 'exponential']

with open('commands.sh','w') as commands:
    for s in S:
        for i in I:
            # for j in J:
            for t in T:
                for r in replenishment:
                    for a in absorption:
                        for z in zeta:
                            if counter >= 0:

                                keyword = '{}-{}-{}-{}-{}-{}-{}-{}'.format('A', s, i, i, t, r, a, z)
                                instance = {}
                                instance['S'] = s
                                instance['I'] = i
                                instance['J'] = i
                                instance['T'] = t
                                instance['replenishment'] = r
                                instance['absorption'] = a
                                instance['zeta'] = z

                                with open('{}/{}.json'.format('instances', keyword), 'w') as output:
                                    js.dump(instance, output)

                                with open('{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                    output.write('#!/bin/bash\n')

                                    output.write('#SBATCH --time=12:00:00\n')
                                    output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                    output.write('#SBATCH --account=def-jenasanj\n')
                                    output.write('#SBATCH --mem=24576M\n')
                                    output.write('#SBATCH --cpus-per-task=1\n')
                                    output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                    output.write('#SBATCH --mail-type=FAIL\n')

                                    output.write('cd ~/shortcut/\n')
                                    output.write('python main.py {}\n'.format(keyword))

                                commands.write('dos2unix ../scripts/{}.sh\n'.format(keyword))
                                commands.write('sbatch ../scripts/{}.sh\n'.format(keyword))
                                counter += 1

print('Done generating {} instances and scripts'.format(counter))