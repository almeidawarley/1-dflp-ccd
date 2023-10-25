import pandas as pd

content = pd.read_csv('experiments/predoc3/summary.csv')

content = content.replace('paper1-hom', 'predoc3')
content = content.replace('paper1-het', 'predoc3')

dataset = 'Homogeneous'
# dataset = 'Heterogeneous'

characteristics = {
    'project': ['predoc3'],
    'periods': [5, 10, 20],
    'patronizing': ['weak', 'medium', 'strong'],
    'rewards': ['identical', 'inversely'],
    'replenishment': ['absolute', 'relative'],
    'absorption': ['complete', 'constrained']
}

labels = {
    'predoc3': '{} dataset'.format(dataset),
    5: '5 time periods',
    10: '10 time periods',
    20: '20 time periods',
    'weak': 'Weak patronizing',
    'medium': 'Medium patronizing',
    'strong': 'Strong patronizing',
    'identical': 'Identical rewards',
    'inversely': 'Inversely rewards',
    'absolute': 'Absolute replenishment',
    'relative': 'Relative replenishment',
    'complete': 'Complete absorption',
    'constrained': 'Constrained absorption'
}

content = content[content['character'] == '{}'.format(dataset.lower())]
content = content[content['rewards'] != 'directly']
content = content[content['absorption'] != 'constrained']
content = content[content['periods'] != 20]


print('**************************************************************************************************')

for characteristic, values in characteristics.items():

    for value in values:

        filter = (content[characteristic] == value)

        columns = ['mip_intgap', 'nws_runtime', 'mip_runtime']

        averages = {}
        deviations = {}
        maximums = {}

        for column in columns:
            averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1), 2)
            deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1), 2)
            # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1), 2)

        count = len(content[filter].index)

        print('{}&{}&{}{}{}'.
        format(labels[value], count, '&'.join(['${}\pm{}\%$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

    print('\\midrule')

_ = input('table1')


print('**************************************************************************************************')

for characteristic, values in characteristics.items():

    for value in values:

        filter = (content[characteristic] == value)

        columns = ['ap2_optgap', 'rnd_optgap', 'frw_optgap']
        # columns = ['ap1_optgap', 'ap3_optgap', 'ap2_optgap', 'rnd_optgap', 'frw_optgap']
        # columns = ['rnd_optgap', 'frw_optgap']

        averages = {}
        deviations = {}
        maximums = {}

        for column in columns:
            averages[column] = round(content[filter][column].mean() * 100, 2)
            deviations[column] = round(content[filter][column].std() * 100, 2)
            # maximums[column] = round(content[filter][column].max() * 100, 2)

        count = len(content[filter].index)

        print('{}&{}&{}{}{}'.
        format(labels[value], count, '&'.join(['${}\pm{}\%$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

    print('\\midrule')

_ = input('table2')

print('**************************************************************************************************')

for characteristic, values in characteristics.items():

    for value in values:

        filter = (content[characteristic] == value)

        columns = ['frw_optgap', 'bcw_optgap', 'prg_optgap']

        averages = {}
        deviations = {}
        maximums = {}

        for column in columns:
            averages[column] = round(content[filter][column].mean() * 100, 2)
            deviations[column] = round(content[filter][column].std() * 100, 2)
            # maximums[column] = round(content[filter][column].max() * 100, 2)

        count = len(content[filter].index)

        print('{}&{}&{}{}{}'.
        format(labels[value], count, '&'.join(['${}\pm{}\%$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

    print('\\midrule')

_ = input('table3')

print('**************************************************************************************************')

for characteristic, values in characteristics.items():

    for value in values:

        filter = (content[characteristic] == value)

        methods = {
            'rnd' : 'orange',
            'frw' : 'red',
            'bcw' : 'blue',
            'prg' : 'olive',
            'ap2' : 'magenta',
            'mip' : 'gray'
        }

        with open ('coordinates.txt', 'w') as output:

            output.write('\\begin{figure}[!ht]\n\centering\n')
            output.write('\\begin{tikzpicture}[scale=.8 every node/.style={scale=.8}]\n')
            output.write('\draw[thick,->] (0,0) -- (10.5,0);\n')
            output.write('\draw[thick,->] (0,0) -- (0,10.5);\n')

            output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
            output.write('\draw (10,0.5) node[anchor=mid] {optimality gap (\%)};\n')
            output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

            for x in range(1,11):
                output.write('\draw ({},-0.5) node[anchor=mid] {}{}{};\n'.format(x, '{$', x * 10,'$}'))
            for y in range(1,11):
                output.write('\draw (-0.5,{}) node[anchor=mid] {}{}{};\n'.format(y, '{$', y * 10,'$}'))


            for method, color in methods.items():

                prev_x = 0
                prev_y = 0

                for x in range(1,101):

                    if method == 'mip':
                        prev_y = 100
                        y = 100
                    else:
                        y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= x/100)])/len(content[filter]))
                    output.write('\draw[color={}] ({},{})--({},{});\n'.format(color, prev_x/10, prev_y/10, x/10, y/10))

                    prev_x = x
                    prev_y = y

            output.write('\draw[color=gray!100] (10, 4) node[anchor=mid] {MIP reference};\n')
            output.write('\draw[color=magenta!100] (10, 3.5) node[anchor=mid] {EML-$2$ heuristic};\n')
            output.write('\draw[color=orange!100] (10, 3) node[anchor=mid] {RND heuristic};\n')
            output.write('\draw[color=red!100] (10, 2.5) node[anchor=mid] {FRW heuristic};\n')
            output.write('\draw[color=blue!100] (10, 2) node[anchor=mid] {BCW heuristic};\n')
            output.write('\draw[color=olive!100] (10, 1.5) node[anchor=mid] {PRG heuristic};\n')
            output.write('\draw (8.5,4.5)--(11.5,4.5)--(11.5,1)--(8.5,1)--(8.5,4.5);\n')

            output.write('\end{tikzpicture}\n')
            output.write('\caption{Performance comparison between proposed heuristics.}\n')
            output.write('\label{fg:demand_growth}\n')
            output.write('\end{figure}')

        _ = input('{} = {}'.format(characteristic, value))