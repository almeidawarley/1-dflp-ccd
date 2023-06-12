import json as js
import instance as ic

'''
features = {
    'seed': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    'points': [50, 100],
    'coordinates': ['normal1', 'normal5', 'uniform'],
    'patronizing': ['radius0', 'radius15', 'radius30'],
    'correlation': ['low', 'medium', 'high'],
    'rewards': ['identical', 'inversely', 'directly'],
    'initial': ['low', 'high'],
    'type': ['absolute', 'relative'],
    'replenishment': ['none', 'low', 'high'],
    'absorption': ['low', 'medium', 'high', 'full']
}
'''

features = {
    'seed': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    'points': [50, 100],
    'coordinates': ['normal1', 'normal5', 'uniform'],
    'patronizing': ['radius15', 'radius30'],
    'correlation': ['low', 'medium', 'high'],
    'rewards': ['identical', 'inversely', 'directly'],
    'initial': ['low', 'high'],
    'type': ['absolute'],
    'replenishment': ['low', 'high'],
    'absorption': ['full']
}

project = 'set1D'

instance = {}

commands = open('commands-{}.sh'.format(project), 'w')

for seed in features['seed']:
    for points in features['points']:
        for coordinates in features['coordinates']:
            for patronizing in features['patronizing']:
                for correlation in features['correlation']:
                    for rewards in features['rewards']:
                        for initial in features['initial']:
                            for type in features['type']:
                                for replenishment in features['replenishment']:
                                    for absorption in features['absorption']:

                                        instance['seed'] = seed
                                        instance['locations'] = points
                                        instance['customers'] = points
                                        instance['periods'] = points/5
                                        instance['coordinates'] = coordinates
                                        instance['patronizing'] = patronizing
                                        instance['correlation'] = correlation
                                        instance['rewards'] = rewards
                                        instance['initial'] = initial
                                        instance['type'] = type
                                        instance['replenishment'] = replenishment
                                        instance['absorption'] = absorption

                                        keyword = '{}_{}'.format('syn', '-'.join([str(value) for value in instance.values()]))

                                        with open('{}/{}.json'.format('instances/synthetic', keyword), 'w') as output:
                                            js.dump(instance, output)

                                        _ = ic.instance(keyword, 'validation')

                                        with open('{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                            output.write('#!/bin/bash\n')

                                            output.write('#SBATCH --time=12:00:00\n')
                                            output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                            output.write('#SBATCH --output={}.out\n'.format(keyword))
                                            output.write('#SBATCH --account=def-jenasanj\n')
                                            output.write('#SBATCH --mem=30GB\n')
                                            output.write('#SBATCH --cpus-per-task=1\n')
                                            output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                            output.write('#SBATCH --mail-type=FAIL\n')

                                            output.write('cd ~/shortcut/\n')
                                            output.write('python main.py -p {} {}\n'.format(project, keyword))

                                        commands.write('dos2unix ../scripts/{}.sh\n'.format(keyword))
                                        commands.write('sbatch ../scripts/{}.sh\n'.format(keyword))
