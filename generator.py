import uuid as ui

counter = 0

seeds = [1,2,3,4,5]

locations = [10]
customers = [10]
periods = [7, 14]

relevances = ['local',  'medium', 'large']
revenues = ['same', 'different']
uppers = ['10', 'inf']
startings = ['lower', 'upper']
replenishments = ['doubling', 'linear']
absorptions = ['everything', 'linear']

with open('commands.sh','w') as commands:
    for a in seeds:
        for b in locations:
            for c in customers:
                for d in periods:
                    for e in relevances:
                        for f in revenues:
                            for g in uppers:
                                for h in startings:
                                    for i in replenishments:
                                        for j in absorptions:
                                            if counter >= 0:

                                                keyword = '{}-{}-{}-{}-{}-{}-{}-{}-{}-{}'.format(a, b, c, d, e, f, g, h, i, j)
                                                with open('experiments/{}/{}.csv'.format('instances', keyword), 'w') as output:
                                                    output.write('title,value\n')

                                                    output.write('seed,{}\n'.format(a))
                                                    output.write('number of locations,{}\n'.format(b))
                                                    output.write('number of customers,{}\n'.format(c))
                                                    output.write('number of periods,{}\n'.format(d))
                                                    output.write('location relevances,{}\n'.format(e))
                                                    output.write('location revenues,{}\n'.format(f))
                                                    output.write('upper demand,{}\n'.format(g))
                                                    output.write('starting demand,{}\n'.format(h))
                                                    output.write('replenishment type,{}\n'.format(i))
                                                    output.write('absorption type,{}\n'.format(j))

                                                with open('experiments/{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                                    output.write('#!/bin/bash\n')

                                                    output.write('#SBATCH --time=12:00:00\n')
                                                    output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                                    output.write('#SBATCH --output={}.out\n'.format(keyword))
                                                    output.write('#SBATCH --account=def-jenasanj\n')
                                                    output.write('#SBATCH --mem=24576M\n')
                                                    output.write('#SBATCH --cpus-per-task=1\n')
                                                    output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                                    output.write('#SBATCH --mail-type=FAIL\n')

                                                    output.write('cd ~/projects/def-jenasanj/walm/code-dsflp-dra/\n')
                                                    output.write('python main.py {}\n'.format(keyword))

                                                commands.write('dos2unix ../scripts/{}.sh\n'.format(keyword))
                                                commands.write('sbatch ../scripts/{}.sh\n'.format(keyword))
                                                counter += 1

print('Done generating {} instances and scripts'.format(counter))