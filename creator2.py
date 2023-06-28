import json as js
import instance as ic

features = {
    'seed': [i for i in range(0, 100)],
    'points': [20],
    'patronizing': ['weak', 'medium', 'strong'],
    'rewards': ['identical', 'inversely', 'directly'],
    'replenishment': ['absolute'],
    'absorption': ['full']
}

project = 'rnd1A'

instance = {}

commands = open('commands-{}.sh'.format(project), 'w')

for seed in features['seed']:
    for points in features['points']:
        for patronizing in features['patronizing']:
            for rewards in features['rewards']:
                for replenishment in features['replenishment']:
                    for absorption in features['absorption']:
                        for periods in [int(points/4), int(points/2), int(points/1)]:

                            instance['seed'] = seed
                            instance['locations'] = points
                            instance['customers'] = points
                            instance['periods'] = periods
                            instance['patronizing'] = patronizing
                            instance['rewards'] = rewards
                            instance['replenishment'] = replenishment
                            instance['absorption'] = absorption

                            keyword = '{}_{}'.format('rnd', '-'.join([str(value) for value in instance.values()]))

                            with open('{}/{}.json'.format('instances/synthetic', keyword), 'w') as output:
                                js.dump(instance, output)

                            _ = ic.instance(keyword, 'validation')

                            with open('{}/{}.sh'.format('scripts', keyword), 'w') as output:

                                output.write('#!/bin/bash\n')

                                output.write('#SBATCH --time=12:00:00\n')
                                output.write('#SBATCH --job-name={}.job\n'.format(keyword))
                                output.write('#SBATCH --output={}.out\n'.format(keyword))
                                output.write('#SBATCH --account=def-mxm\n')
                                output.write('#SBATCH --mem=30GB\n')
                                output.write('#SBATCH --cpus-per-task=1\n')
                                output.write('#SBATCH --mail-user=<almeida.warley@outlook.com>\n')
                                output.write('#SBATCH --mail-type=FAIL\n')

                                output.write('cd ~/shortcut/\n')
                                output.write('python main.py -p {} {}\n'.format(project, keyword))

                            commands.write('dos2unix ../scripts/{}.sh\n'.format(keyword))
                            commands.write('sbatch ../scripts/{}.sh\n'.format(keyword))

                            print(keyword)