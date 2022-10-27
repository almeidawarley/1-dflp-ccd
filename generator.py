import uuid as ui

counter = 0

locations = [10, 50, 100]
customers = [10, 50, 100]
periods = [7, 14, 30]

preferences = ['high'] # ['low', 'medium', 'high']
revenues = ['equal', 'different']
replenishment = ['linear', 'exponential']
alphabeta = ['low','high'] #  ['low', 'medium', 'high']
absorption = ['linear', 'exponential']
gammadelta = ['low','high'] # ['low', 'medium', 'high']
starting = ['medium'] # ['low', 'medium', 'high']

with open('database.csv','w') as database:
    for a in locations:
        for b in customers:
            for c in periods:
                for d in preferences:
                    for e in revenues:
                        for f in replenishment:
                            for g in alphabeta:
                                for h in absorption:
                                    for i in gammadelta:
                                        for j in starting:
                                            if counter >= 0:

                                                keyword = '{}-{}-{}-{}-{}-{}-{}-{}-{}-{}'.format(a, b, c, d, e, f, g, h, i, j)
                                                with open('{}/{}.csv'.format('instances', keyword), 'w') as output:
                                                    output.write('title,value\n')

                                                    output.write('seed,{}\n'.format(100))
                                                    output.write('number of locations,{}\n'.format(a))
                                                    output.write('number of customers,{}\n'.format(b))
                                                    output.write('number of periods,{}\n'.format(c))
                                                    output.write('willingness to patronize,{}\n'.format(d))
                                                    output.write('location revenues,{}\n'.format(e))
                                                    output.write('replenishment type,{}\n'.format(f))
                                                    output.write('replenishment variability,{}\n'.format(g))
                                                    output.write('absorption type,{}\n'.format(h))
                                                    output.write('absorption variability,{}\n'.format(i))
                                                    output.write('starting demand,{}\n'.format(j))

                                                with open('{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                                    output.write('#!/bin/bash\n')

                                                    output.write('#SBATCH --time=6:00:00\n')
                                                    output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                                    output.write('#SBATCH --output={}.out\n'.format(keyword))
                                                    output.write('#SBATCH --account=def-jenasanj\n')
                                                    output.write('#SBATCH --mem=24576M\n')
                                                    output.write('#SBATCH --cpus-per-task=1\n')
                                                    output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                                    output.write('#SBATCH --mail-type=FAIL\n')

                                                    output.write('cd ~/projects/def-jenasanj/walm/code-dsflp-dra/\n')
                                                    output.write('python main.py {}\n'.format(keyword))

                                                database.write('{},{},{},{},{},{},{},{},{},{},{}\n'.format(keyword, a, b, c, d, e, f, g, h, i, j))

                                                print('dos2unix ../scripts/{}.sh'.format(keyword))
                                                print('sbatch ../scripts/{}.sh'.format(keyword))
                                                counter += 1

print('Generated {} instances'.format(counter))