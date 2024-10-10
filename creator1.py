import common as cm
import json as js
import sys

features = {
    'seed': [i for i in range(0, 5)],
    'points': [50, 100],
    'periods': [10],
    'facilities': [1, 2, 3, 4],
    'penalization': [0, 1],
    'preferences': ['small', 'large'],
    'rewards': ['identical', 'inversely'],
    'demands': ['constant'], # ['constant', 'seasonal', 'increasing', 'decreasing'],
    'characters': ['heterogeneous'] # ['homogeneous', 'heterogeneous']
}

project = 'p1artificial'

script = sys.argv[1]
hours = sys.argv[2]

parameters = {}

commands = open('commands_{}_{}.sh'.format(script, project), 'w')

counter = 0

for seed in features['seed']:
    for points in features['points']:
        for periods in features['periods']:
            for facilities in features['facilities']:
                for penalization in features['penalization']:
                    for preferences in features['preferences']:
                        for rewards in features['rewards']:
                            for demands in features['demands']:
                                for character in features['characters']:

                                    parameters['seed'] = seed
                                    parameters['locations'] = points
                                    parameters['customers'] = points
                                    parameters['periods'] = periods
                                    parameters['facilities'] = facilities
                                    parameters['penalization'] = penalization
                                    parameters['preferences'] = preferences
                                    parameters['rewards'] = rewards
                                    parameters['demands'] = demands
                                    parameters['characters'] = character

                                    keyword = '{}_{}'.format('art', '-'.join([str(value) for value in parameters.values()]))

                                    with open('{}/{}.json'.format('instances/artificial', keyword), 'w') as output:
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
                                        output.write('python run-{}.py -p {} -m 2 {}\n'.format(script, project, keyword))

                                    commands.write('dos2unix ../scripts/{}_{}.sh\n'.format(script, keyword))
                                    commands.write('sbatch ../scripts/{}_{}.sh\n'.format(script, keyword))

                                    print(keyword)
                                    counter += 1

print('This script run wrote {} scripts in total!'.format(counter))