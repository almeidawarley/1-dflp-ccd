import pandas as pd
import common as cm
import matplotlib.pyplot as plt

# Analysis instance set A

content = pd.read_csv('results/paper1/double_check.csv')

content['index'] = content['keyword']
content = content.set_index('index')

formulation_approaches = ['cold_lrz', 'cold_net']
benders_approaches = [] # ['bbd', 'bbf', 'bbe', 'bbh']
heuristic_approaches = [] # ['eml', 'rnd', 'frw', 'bcw']
exact_approaches = formulation_approaches + benders_approaches

content['bst_objective'] = content.apply(lambda row: max(row['{}_objective'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_bound'] = content.apply(lambda row: min(row['{}_bound'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_runtime'] = content.apply(lambda row: min(row['{}_runtime'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_optgap'] = content.apply(lambda row: min(row['{}_optgap'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_optimal'] = content.apply(lambda row: (row['bst_optgap'] <= cm.TOLERANCE), axis = 1)

for method in benders_approaches:
    content['{}_proportion'.format(method)] = content.apply(lambda row: (row['{}_subtime_integer'.format(method)] + row['{}_subtime_fractional'.format(method)]) / row['{}_runtime'.format(method)], axis = 1)
    content['{}_nodes'.format(method)] = content.apply(lambda row: row['{}_nodes'.format(method)]  / 10**6, axis = 1)
    # content['{}_nodes'.format(method)] = content.apply(lambda row: row['{}_nodes'.format(method)]  / 10**6, axis = 1)
    # content['{}_optgap'.format(method)] = content.apply(lambda row: cm.compute_gap(row['bst_bound'], row['{}_objective'.format(method)]), axis = 1)

for approach in heuristic_approaches:
    content['{}_optgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['bst_objective'], row['{}_objective'.format(approach)]), axis = 1)

for approach in exact_approaches:
    content['{}_optimal'.format(approach)] = content.apply(lambda row: (row['{}_optgap'.format(approach)] <= cm.TOLERANCE), axis = 1)

for approach in formulation_approaches:
    approach = approach.replace('cold_', '')
    content['{}_intgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['rlx_{}_bound'.format(approach)], row['bst_objective']), axis = 1)

for approach in exact_approaches:
    content['{}_ratio_objective'.format(approach)] = content.apply(lambda row: round(row['bst_objective'] / (row['{}_objective'.format(approach)] + cm.TOLERANCE), cm.PRECISION), axis = 1)
    content['{}_ratio_runtime'.format(approach)] = content.apply(lambda row: round(row['{}_runtime'.format(approach)] / (row['bst_runtime'] + cm.TOLERANCE), cm.PRECISION), axis = 1)

content.to_csv('debugging.csv')

characteristics = {
    'periods': [10],
    'locations': [50, 100],
    'customers': [1, 2],
    'facilities': [1, 2], # [1, 2, 3, 4],
    'penalties': [0], # [0, 1, 2, 3],
    'preferences': ['small', 'large'],
    'rewards': ['identical', 'inversely'],
    'demands': ['constant', 'seasonal'], # 'demands': ['constant', 'seasonal', 'increasing', 'decreasing'],
    'characters': ['homogeneous', 'heterogeneous'] # ['homogeneous', 'heterogeneous']
}

labels = {
    'periods': {
        10: 'Complete benchmark',
    },
    'locations': {
        50: '50 locations',
        100: '100 locations',
    },
    'customers': {
        1: 'x1 customers',
        2: 'x2 customers',
    },
    'facilities': {
        1: '1 facility',
        2: '2 facilities',
        3: '3 facilities',
        4: '4 facilities',
    },
    'penalties': {
        0: 'No penalties',
        1: '25\\% penalties',
        2: '50\\% penalties',
        3: '75\\% penalties',
    },
    'preferences': {
        'small': 'Small choice sets',
        'large': 'Large choice sets'
    },
    'rewards':{
        'identical': 'Identical rewards',
        'inversely': 'Different rewards'
    },
    'demands': {
        'constant': 'Constant demand',
        'seasonal': 'Seasonal demand',
        'increasing': 'Increasing demand',
        'decreasing': 'Decreasing demand',
    },
    'characters': {
        'homogeneous': 'Identical amplitudes',
        'heterogeneous': 'Sampled amplitudes'
    }
}

def table1(descriptor = 'paper'):

    filter = (content['periods'] == 10) & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)

    content[filter].boxplot(['cold_lrz_runtime', 'cold_net_runtime'])
    plt.savefig('results/paper1/box_table1_runtime.png')
    plt.figure().clear()

    content[filter].boxplot(['lrz_intgap', 'net_intgap'])
    plt.savefig('results/paper1/box_table1_intgap.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['lrz_intgap', 'cold_lrz_runtime', 'net_intgap', 'cold_net_runtime']
                filter = (content[characteristic] == value) & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)
            else:
                exit('Wrong descriptor for table 1')

            averages = {}
            deviations = {}
            maximums = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)

            # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
            count = len(content[filter].index)
            total = len(content[(content[characteristic] == value)].index)

            # print('{}&${:.2f}$&{}{}{}'.
            print('{}&${} \, ({})$&{}{}{}'.
            format(labels[characteristic][value], count, total, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table1 {}'.format(descriptor))

    print('**************************************************************************************************')

def table2(descriptor = 'paper'):

    filter = (content['periods'] == 10) & ((content['cold_lrz_optimal'] == False) | (content['cold_net_optimal'] == False))

    content[filter].boxplot(['cold_lrz_optgap', 'cold_net_optgap'])
    plt.savefig('results/paper1/box_table2_optgap.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_lrz_optgap', 'cold_net_optgap']
                filter = (content[characteristic] == value) & ((content['cold_lrz_optimal'] == False) | (content['cold_net_optimal'] == False))
            else:
                exit('Wrong descriptor for table 2')

            averages = {}
            deviations = {}
            maximums = {}
            feasibles = {}
            optimals = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                optimals[column] = content[filter & (content[column] <= cm.TOLERANCE)][column].count()

            # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
            count = len(content[filter].index)
            total = len(content[(content[characteristic] == value)].index)

            # print('{}&${:.2f}$&{}{}{}'.
            print('{}&${} \, ({})$&{}{}{}'.
            format(labels[characteristic][value], count, total, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table2 {}'.format(descriptor))

    print('**************************************************************************************************')

def graph2(descriptor = 'paper'):

    methods = ['cold_lrz', 'cold_net']

    colors = {
        'cold_lrz' : 'red',
        'cold_net' : 'gray',
        'bbd': 'blue',
        'bbf': 'yellow',
        'bba' : 'orange',
        'bbe' : 'orange',
        'bbh': 'green'
    }

    styles = {
        'cold_lrz' : 'dashed',
        'cold_net' : 'dotted',
        'bbd': 'dashdotted',
        'bbf' : 'dashed',
        'bba' : 'dotted',
        'bbe' : 'dotted',
        'bbh': 'dashdotted',
    }

    filter = (content['periods'] == 10) # & (content['bst_optgap'] > cm.TOLERANCE)

    with open ('graphs/objectives.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 1, 1.1, 0.01
        length_y, lower_y, upper_y, step_y = 10, 50, 100, 5

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,10.5);\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (9.5,0.5) node[anchor=mid] {objective ratio};\n')
        output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.2f}{};\n'.format(formatted_x, '{$', x,'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 1
            prev_y = int(100 * len(content[filter & (content['{}_ratio_objective'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while x <= upper_x:

                y = int(100 * len(content[filter & (content['{}_ratio_objective'.format(method)] <= x)]) / len(content[filter]))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(colors[method], styles[method], formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))

                prev_x = x
                prev_y = y
                x += step_x

        output.write('\n')

        current_y = 3.0
        next_y = 0.5

        for method in methods:
            output.write('\draw[line width=0.5mm, {}, {}] (8.5, {:.2f})--(9.0, {:.2f});\n'.format(colors[method], styles[method], current_y, current_y))
            output.write('\draw[line width=0.5mm, {}] (9.0, {:.2f}) node[anchor=west] {}{}{};\n'.format(colors[method], current_y, '{', method.replace('cold_', ''), '}'))
            current_y += next_y

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/objectives.tex')

def graph3(descriptor = 'paper'):

    methods = ['cold_lrz', 'cold_net']

    colors = {
        'cold_lrz' : 'red',
        'cold_net' : 'gray',
        'bbd': 'blue',
        'bbf': 'yellow',
        'bba' : 'orange',
        'bbe' : 'orange',
        'bbh': 'green'
    }

    styles = {
        'cold_lrz' : 'dashed',
        'cold_net' : 'dotted',
        'bbd': 'dashdotted',
        'bbf' : 'dashed',
        'bba' : 'dotted',
        'bbe' : 'dotted',
        'bbh': 'dashdotted',
    }

    filter = (content['periods'] == 10) # & (content['bst_optgap'] > cm.TOLERANCE)

    with open ('graphs/runtimes.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 1, 21, 2
        length_y, lower_y, upper_y, step_y = 10, 30, 100, 7

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,10.5);\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (9.5,0.5) node[anchor=mid] {runtime ratio};\n')
        output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.2f}{};\n'.format(formatted_x, '{$', x,'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 1
            prev_y = int(100 * len(content[filter & (content['{}_ratio_runtime'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while x <= upper_x:

                y = int(100 * len(content[filter & (content['{}_ratio_runtime'.format(method)] <= x)]) / len(content[filter]))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(colors[method], styles[method], formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))

                prev_x = x
                prev_y = y
                x += step_x

        output.write('\n')

        current_y = 3.0
        next_y = 0.5

        for method in methods:
            output.write('\draw[line width=0.5mm, {}, {}] (8.5, {:.2f})--(9.0, {:.2f});\n'.format(colors[method], styles[method], current_y, current_y))
            output.write('\draw[line width=0.5mm, {}] (9.0, {:.2f}) node[anchor=west] {}{}{};\n'.format(colors[method], current_y, '{', method.replace('cold_', ''), '}'))
            current_y += next_y

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/runtimes.tex')

table1('paper')
table2('paper')
graph2('paper')
graph3('paper')