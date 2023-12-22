import common as cm
import json as js
import sys

features = {
    'seed': [i for i in range(0, 10)],
    'points': [50, 100],
    'periods': [10],
    'preferences': ['small', 'large'],
    'rewards': ['identical', 'inversely'],
    'demands': ['constant', 'increasing', 'decreasing', 'bass', 'seasonal'],
    'characters': ['homogeneous', 'heterogeneous']
}

project = 'paper1'

script = sys.argv[1]
hours = sys.argv[2]

parameters = {}

commands = open('commands-{}-{}.sh'.format(script, project), 'w')

counter = 0

for seed in features['seed']:
    for points in features['points']:
        for periods in features['periods']:
            for preferences in features['preferences']:
                for rewards in features['rewards']:
                    for demands in features['demands']:
                        for character in features['characters']:

                            parameters['seed'] = seed
                            parameters['locations'] = points
                            parameters['customers'] = points
                            parameters['periods'] = periods
                            parameters['preferences'] = preferences
                            parameters['rewards'] = rewards
                            parameters['demands'] = demands
                            parameters['characters'] = character

                            keyword = '{}_{}'.format('art', '-'.join([str(value) for value in parameters.values()]))

                            with open('{}/{}.json'.format('instances/artificial', keyword), 'w') as output:
                                js.dump(parameters, output)

                            _ = cm.load_instance(keyword, 'validation')

                            with open('{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                output.write('#!/bin/bash\n')

                                output.write('#SBATCH --time={}:00:00\n'.format(hours))
                                output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                output.write('#SBATCH --output={}.out\n'.format(keyword))
                                output.write('#SBATCH --account=def-mxm\n')
                                output.write('#SBATCH --mem=30GB\n')
                                output.write('#SBATCH --cpus-per-task=1\n')
                                output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                output.write('#SBATCH --mail-type=FAIL\n')

                                output.write('cd ~/shortcut/\n')
                                output.write('python {}.py -p {} {}\n'.format(script, project, keyword))

                            commands.write('dos2unix ../scripts/{}.sh\n'.format(keyword))
                            commands.write('sbatch ../scripts/{}.sh\n'.format(keyword))

                            print(keyword)
                            counter += 1

print('This script run wrote {} scripts in total!'.format(counter))