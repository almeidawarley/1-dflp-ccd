import json as js
import sys

features = {
    'seed': [i for i in range(1, 2)],
    'locations': [50, 100, 150],
    'customers': [1, 3, 5],
    'periods': [5, 7, 9],
    'facilities': [1, 3, 5],
    'rewards': ['identical', 'inversely'],
    'preferences': ['small', 'large'],
    'demands': ['fixed', 'sparse'],
    'penalties': [0]
}

'''
# Penalty graphs
features = {
    'seed': [1],
    'locations': [50],
    'customers': [1],
    'periods': [5],
    'facilities': [1,3,5],
    'rewards': ['identical', 'inversely'],
    'preferences': ['small', 'large'],
    'demands': ['fixed', 'sparse'],
    'penalties': [int(i) for i in range(0, 100, 10)]
}
'''

script = sys.argv[1]
hours = sys.argv[2]

parameters = {}

commands = open('benchmark_{}.sh'.format(script), 'w')

counter = 0

for seed in features['seed']:
    for locations in features['locations']:
        for customers in features['customers']:
            for periods in features['periods']:
                for facilities in features['facilities']:
                    for rewards in features['rewards']:
                        for preferences in features['preferences']:
                            for demands in features['demands']:
                                for penalties in features['penalties']:

                                    parameters['seed'] = seed
                                    parameters['locations'] = locations
                                    parameters['customers'] = customers
                                    parameters['periods'] = periods
                                    parameters['facilities'] = facilities
                                    parameters['rewards'] = rewards
                                    parameters['preferences'] = preferences
                                    parameters['demands'] = demands
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

                                        output.write('cd ~/shortcut/\n')
                                        output.write('python run-{}.py {}\n'.format(script, keyword))

                                    # commands.write('dos2unix ../scripts/{}_{}.sh\n'.format(script, keyword))
                                    commands.write('sbatch ../scripts/{}_{}.sh\n'.format(script, keyword))

                                    print(keyword)
                                    counter += 1

print('This script run wrote {} scripts in total!'.format(counter))
