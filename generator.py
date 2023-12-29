import common as cm
import json as js
import sys

features = {
    'maps': ['ke', 'pa'],
    'periods': [6, 12],
    'distances': [50, 100, 200],
    'rewards': ['identical', 'inversely'],
    'demands': ['constant', 'seasonal']
}

project = 'paper1'

script = sys.argv[1]
hours = sys.argv[2]

parameters = {}

commands = open('commands-{}-{}.sh'.format(script, project), 'w')

counter = 0

for map in features['maps']:
    for periods in features['periods']:
        for distance in features['distances']:
            for rewards in features['rewards']:
                for demands in features['demands']:

                    parameters['seed'] = 0
                    parameters['map'] = map
                    parameters['periods'] = periods
                    parameters['distance'] = distance
                    parameters['rewards'] = rewards
                    parameters['demands'] = demands

                    keyword = '{}_{}'.format('slv', '-'.join([str(value) for value in parameters.values()]))

                    with open('{}/{}.json'.format('instances/slovakia', keyword), 'w') as output:
                        js.dump(parameters, output)

                    # _ = cm.load_instance(keyword, 'validation')

                    with open('{}/{}_{}.sh'.format('scripts', script, keyword), 'w') as output:

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

                    commands.write('dos2unix ../scripts/{}_{}.sh\n'.format(script, keyword))
                    commands.write('sbatch ../scripts/{}_{}.sh\n'.format(script, keyword))

                    print(keyword)
                    counter += 1

print('This script run wrote {} scripts in total!'.format(counter))