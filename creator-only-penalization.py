import json as js
import sys

features = {
    'seed': [i for i in range(1, 5)],
    'locations': [50, 100],
    'customers': [1, 2],
    'periods': [10],
    'facilities': [1, 2], # [1, 2, 3], # [4]
    #'penalties': [0], # [0, 1, 2, 3],
    'preferences': ['small', 'large'], # ['small', 'large'],
    #'rewards': ['identical', 'inversely'], # ['identical', 'inversely'],
    'demands': ['constant', 'seasonal'], # ['constant', 'seasonal'], # + ['increasing', 'decreasing'],
    'characters': ['homogeneous', 'heterogeneous'] # ['homogeneous', 'heterogeneous']
}

script = sys.argv[1]
hours = sys.argv[2]

parameters = {}

commands = open('onlypenalization_{}.sh'.format(script), 'w')

counter = 0

for seed in features['seed']:
    for locations in features['locations']:
        for customers in features['customers']:
            for periods in features['periods']:
                for facilities in features['facilities']:
                    for preferences in features['preferences']:
                        for demands in features['demands']:
                            for character in features['characters']:

                                parameters['seed'] = seed
                                parameters['locations'] = locations
                                parameters['customers'] = customers
                                parameters['periods'] = periods
                                parameters['facilities'] = facilities
                                parameters['preferences'] = preferences
                                parameters['demands'] = demands
                                parameters['characters'] = character

                                keyword = '{}_{}'.format('cov', '-'.join([str(value) for value in parameters.values()]))

                                with open('{}/{}.json'.format('instances/coverage', keyword), 'w') as output:
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