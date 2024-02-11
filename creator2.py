import common as cm
import json as js
import sys

features = {
    'maps': ['ke', 'pa'],
    'periods': [6, 12],
    'distances': [50, 100],
    'rewards': ['identical', 'inversely'],
    'demands': ['constant', 'seasonal']
}

methods = [1,2,3,4]

project = 'p1slovakia'

script = sys.argv[1]
hours = sys.argv[2]

parameters = {}

commands = open('commands_{}_{}.sh'.format(script, project), 'w')

counter = 0

for method in methods:
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

                        with open('{}/{}_{}_{}.sh'.format('scripts', script, method, keyword), 'w') as output:

                            output.write('#!/bin/bash\n')

                            output.write('#SBATCH --time={}:00:00\n'.format(hours))
                            output.write('#SBATCH --job-name={}_{}_{}.job\n'.format(script, method, keyword))
                            output.write('#SBATCH --output={}_{}_{}.out\n'.format(script, method, keyword))
                            output.write('#SBATCH --account=def-mxm\n')
                            output.write('#SBATCH --mem=30GB\n')
                            output.write('#SBATCH --cpus-per-task=1\n')
                            output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                            output.write('#SBATCH --mail-type=FAIL\n')

                            output.write('cd ~/shortcut/\n')
                            output.write('python run-{}.py -p {} -m {} {}\n'.format(script, project, method, keyword))

                        commands.write('dos2unix ../scripts/{}_{}_{}.sh\n'.format(script, method, keyword))
                        commands.write('sbatch ../scripts/{}_{}_{}.sh\n'.format(script, method,keyword))

                        print(keyword)
                        counter += 1

print('This script run wrote {} scripts in total!'.format(counter))