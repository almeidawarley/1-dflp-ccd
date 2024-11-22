import json as js
import sys

features = {
    'seed': [i for i in range(1, 6)],
    'locations': [100, 200],
    'customers': [1, 5],
    'periods': [5, 10],
    'facilities': [1, 5],
    'penalties': [1, 2],
    'rewards': ['identical', 'inversely']
}

script = sys.argv[1]
hours = sys.argv[2]

parameters = {}

commands = open('marginal_{}.sh'.format(script), 'w')

counter = 0

for seed in features['seed']:
    for locations in features['locations']:
        for customers in features['customers']:
            for periods in features['periods']:
                for facilities in features['facilities']:
                    for rewards in features['rewards']:
                        for penalties in features['penalties']:

                            parameters['seed'] = seed
                            parameters['locations'] = locations
                            parameters['customers'] = customers
                            parameters['periods'] = periods
                            parameters['facilities'] = facilities
                            parameters['rewards'] = rewards
                            parameters['penalties'] = penalties

                            keyword = '{}_{}'.format('bmk', '-'.join([str(value) for value in parameters.values()]))

                            with open('{}/{}.json'.format('instances/benchmark', keyword), 'w') as output:
                                js.dump(parameters, output)

                            # _ = cm.load_instance(keyword, 'validation')

                            with open('{}/{}_{}.sh'.format('scripts', script, keyword), 'w') as output:

                                output.write('#!/bin/bash\n')

                                output.write('#SBATCH --time={}:00:00\n'.format(hours))
                                output.write('#SBATCH --job-name={}_{}.job\n'.format(script, keyword))
                                output.write('#SBATCH --output={}_{}.out\n'.format(script, keyword))
                                output.write('#SBATCH --account=def-mxm\n')
                                output.write('#SBATCH --mem=30GB\n')
                                output.write('#SBATCH --cpus-per-task=1\n')
                                output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                output.write('#SBATCH --mail-type=FAIL\n')

                                output.write('cd /home/walm/projects/def-mxm/walm/1-dflp-ra/\n')
                                output.write('python run-{}.py {}\n'.format(script, keyword))

                            commands.write('dos2unix ../scripts/{}_{}.sh\n'.format(script, keyword))
                            commands.write('sbatch ../scripts/{}_{}.sh\n'.format(script, keyword))

                            print(keyword)
                            counter += 1

print('This script run wrote {} scripts in total!'.format(counter))