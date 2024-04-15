import pandas as pd
import common as cm
import matplotlib.pyplot as plt

content = pd.read_csv('results/paper1/summary.csv')
supervl = pd.read_csv('results/paper1/supervalid.csv')

content['index'] = content['keyword']
content = content.set_index('index')
supervl['index'] = supervl['keyword']
supervl = supervl.set_index('index')

exact_approaches = ['cold_lrz', 'cold_net', 'bbd', 'bbe']

for approach in exact_approaches:
    for column in supervl.columns:
        if approach in column:
            supervl = supervl.rename({column: column.replace(approach, 'sv_' + approach)}, axis = 1)
        if 'rlx' in column:
            supervl = supervl.drop(column, axis = 1)
supervl = supervl.drop(['project','keyword','created','seed','locations','customers','periods','preferences','rewards','demands','characters','updated','commit','branch'], axis = 1)

content = pd.concat([content, supervl], axis = 1, join = 'inner')

content['best_objective'] = content.apply(lambda row: max(row['{}_objective'.format(approach)] for approach in exact_approaches), axis = 1)
content['best_optgap'] = content.apply(lambda row: min(row['{}_optgap'.format(approach)] for approach in exact_approaches), axis = 1)
content['best_optimal'] = content.apply(lambda row: (row['best_optgap'] <= cm.TOLERANCE), axis = 1)

for approach in ['rnd', 'eml', 'frw', 'bcw', 'prg']:
    content['{}_optgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['best_objective'], row['{}_objective'.format(approach)]), axis = 1)

for approach in exact_approaches:
    content['{}_optimal'.format(approach)] = content.apply(lambda row: (row['{}_optgap'.format(approach)] <= cm.TOLERANCE), axis = 1)

for approach in ['lrz', 'net']:
    content['{}_intgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['rlx_{}_objective'.format(approach)], row['best_objective']), axis = 1)

content['refr_objective'] = content.apply(lambda row: max(row['{}_objective'.format(approach)] for approach in exact_approaches), axis = 1)
content['refr_runtime'] = content.apply(lambda row: min(row['{}_runtime'.format(approach)] for approach in exact_approaches), axis = 1)

for approach in exact_approaches:
    content['{}_ratio_objective'.format(approach)] = content.apply(lambda row: round(row['refr_objective'] / row['{}_objective'.format(approach)], 3), axis = 1)
    content['{}_ratio_runtime'.format(approach)] = content.apply(lambda row: round(row['{}_runtime'.format(approach)] / row['refr_runtime'], 3), axis = 1)

content.to_csv('debugging.csv')

characteristics = {
    'periods': [10],
    'locations': [50, 100],
    'preferences': ['small', 'large'],
    'rewards': ['identical', 'inversely'],
    'demands': ['constant', 'seasonal'],
    'characters': ['homogeneous', 'heterogeneous']
}

labels = {
    'periods': {
        10: 'Complete benchmark',
    },
    'locations': {
        50: '50 locations, customers',
        100: '100 locations, customers',
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
        'seasonal': 'Seasonal demand'
    },
    'characters': {
        'homogeneous': 'Identical amplitudes',
        'heterogeneous': 'Sampled amplitudes'
    }
}

def table1(descriptor = 'paper'):

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

            count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)

            print('{}&${:.2f}$&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table1 {}'.format(descriptor))

    print('**************************************************************************************************')

def table2(descriptor = 'paper'):

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

            count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)

            print('{}&${:.2f}$&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table2 {}'.format(descriptor))

    print('**************************************************************************************************')

def table3(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            filter = (content[characteristic] == value) & (content['best_optimal'] == True)

            if descriptor == 'paper':
                columns = ['eml_optgap', 'rnd_optgap', 'frw_optgap', 'bcw_optgap'] #, 'prg_optgap']
            else:
                exit('Wrong descriptor for table 3')

            averages = {}
            deviations = {}
            maximums = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * 100, 2)
                deviations[column] = round(content[filter][column].std() * 100, 2)
                # maximums[column] = round(content[filter][column].max() * 100, 2)

            count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)

            print('{}&${:.2f}$&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table3 {}'.format(descriptor))

    print('**************************************************************************************************')

def table4(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_runtime', 'bbd_runtime', 'bbe_runtime']
                filter = (content[characteristic] == value) & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True)
            else:
                exit('Wrong descriptor for table 4')

            averages = {}
            deviations = {}
            maximums = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)

            count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)

            print('{}&${:.2f}$&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table4 {}'.format(descriptor))

    print('**************************************************************************************************')

def table5(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_optgap', 'bbd_optgap', 'bbe_optgap']
                filter = (content[characteristic] == value) & ((content['cold_net_optimal'] == False) | (content['bbd_optimal'] == False) | (content['bbe_optimal'] == False))
            else:
                exit('Wrong descriptor for table 5')

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

            count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)

            print('{}&${:.2f}$&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table5 {}'.format(descriptor))

    print('**************************************************************************************************')

def table6(descriptor = 'paper'):

    content['bbd_proportion'] = content.apply(lambda row: row['bbd_subtime'] / row['bbd_runtime'], axis = 1)
    content['bbe_proportion'] = content.apply(lambda row: row['bbe_subtime'] / row['bbe_runtime'], axis = 1)

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['bbd_iterations', 'bbd_proportion', 'bbe_iterations', 'bbe_proportion']
                filter = (content[characteristic] == value) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True)
            else:
                exit('Wrong descriptor for table 6')

            averages = {}
            deviations = {}
            maximums = {}
            feasibles = {}

            for column in columns:
                averages[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)

            count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)

            print('{}&${:.2f}$&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table6 {}'.format(descriptor))

    print('**************************************************************************************************')


def graph1(descriptor = 'paper'):

    methods = ['rnd', 'frw', 'bcw', 'eml']

    colors = {
        'rnd' : 'gray',
        'frw' : 'blue',
        'bcw' : 'orange',
        'eml': 'red'
    }

    styles = {
        'rnd' : 'dotted',
        'frw' : 'dashdotted',
        'bcw' : 'solid',
        'eml': 'dashed'
    }

    filter = (content['periods'] == 10)

    with open ('graphs/heuristic.tex', 'w') as output:

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (10.5,0);\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,10.5);\n')

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (9,0.5) node[anchor=mid] {opportunity gap (\%)};\n')
        output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

        for x in range(0,11):
            output.write('\draw ({},-0.5) node[anchor=mid] {}{}{};\n'.format(x, '{$', x * 10,'$}'))
        for y in range(0,11):
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{}{};\n'.format(y, '{$', y * 10,'$}'))


        for method in methods:

            prev_x = 0
            prev_y = 0

            for x in range(1,102,5):

                y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= x/100)])/len(content[filter]))
                output.write('\draw[line width=0.5mm,{},{}] ({},{})--({},{});'.format(colors[method], styles[method], prev_x/10, prev_y/10, x/10, y/10))

                prev_x = x
                prev_y = y

        output.write('\n')

        output.write('\draw[line width=0.5mm,red, dashed] (8.5, 3.5)--(9.0, 3.5);\n')
        output.write('\draw[line width=0.5mm,red] (9.0, 3.5) node[anchor=west] {DBH};\n')
        output.write('\draw[line width=0.5mm,gray, dotted] (8.5, 3.0)--(9.0, 3.0);\n')
        output.write('\draw[line width=0.5mm,gray] (9.0, 3.0) node[anchor=west] {RND};\n')
        output.write('\draw[line width=0.5mm,blue, dashdotted] (8.5, 2.5)--(9.0, 2.5);\n')
        output.write('\draw[line width=0.5mm,blue] (9.0, 2.5) node[anchor=west] {FGH};\n')
        output.write('\draw[line width=0.5mm,orange, solid] (8.5, 2.0)--(9.0, 2.0);\n')
        output.write('\draw[line width=0.5mm,orange] (9.0, 2.0) node[anchor=west] {BGH};\n')
        # output.write('\draw (8,4.0)--(11,4.0)--(11,1.5)--(8,1.5)--(8,4.0);\n')

        output.write('\end{tikzpicture}\n')
        # output.write('\caption{}Performance overview in terms of optimality gap of proposed heuristics for {}.{}\n'.format('{', labels[characteristic][value].lower(), '}'))
        # output.write('\end{figure}')

        print('Exported graph to graphs/heuristic.tex')

def graph2(descriptor = 'paper'):

    methods = ['cold_lrz', 'cold_net', 'bbd', 'bbe']

    colors = {
        'cold_lrz' : 'red',
        'cold_net' : 'gray',
        'bbd': 'blue',
        'bbe' : 'orange'
    }

    styles = {
        'cold_lrz' : 'dashed',
        'cold_net' : 'dotted',
        'bbd': 'dashdotted',
        'bbe' : 'solid'
    }

    filter = (content['periods'] == 10) # & (content['best_optgap'] > cm.TOLERANCE)

    with open ('graphs/objectives.tex', 'w') as output:

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (10.5,0);\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,10.5);\n')

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (-1,-0.5) node[anchor=mid] {$(+1)$};\n')
        output.write('\draw (9,0.5) node[anchor=mid] {objective ratio ($10^{-3}$)};\n')
        output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

        for x in range(0,11):
            output.write('\draw ({},-0.5) node[anchor=mid] {}{}{};\n'.format(x, '{$', x,'$}'))
        for y in range(0,11):
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{}{};\n'.format(y, '{$', 90 + y,'$}'))


        for method in methods:

            prev_x = 0
            prev_y = int(100 * len(content[filter & (content['{}_ratio_objective'.format(method)] <= (prev_x + 10**3)/ 10**3)])/len(content[filter]))

            for x in range(1,11,1):

                y = int(100 * len(content[filter & (content['{}_ratio_objective'.format(method)] <= (x + 10**3)/ 10**3)])/len(content[filter]))
                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({},{})--({},{});'.format(colors[method], styles[method], prev_x, (prev_y - 90), x, (y - 90)))

                prev_x = x
                prev_y = y

        output.write('\n')

        output.write('\draw[line width=0.5mm,red, dashed] (8.5, 3.5)--(9.0, 3.5);\n')
        output.write('\draw[line width=0.5mm,red] (9.0, 3.5) node[anchor=west] {STI};\n')
        output.write('\draw[line width=0.5mm,gray, dotted] (8.5, 3.0)--(9.0, 3.0);\n')
        output.write('\draw[line width=0.5mm,gray] (9.0, 3.0) node[anchor=west] {DTI};\n')
        output.write('\draw[line width=0.5mm,blue, dashdotted] (8.5, 2.5)--(9.0, 2.5);\n')
        output.write('\draw[line width=0.5mm,blue] (9.0, 2.5) node[anchor=west] {BSD};\n')
        output.write('\draw[line width=0.5mm,orange, solid] (8.5, 2.0)--(9.0, 2.0);\n')
        output.write('\draw[line width=0.5mm,orange] (9.0, 2.0) node[anchor=west] {BSE};\n')
        # output.write('\draw (8,4.0)--(11,4.0)--(11,1.5)--(8,1.5)--(8,4.0);\n')

        output.write('\end{tikzpicture}\n')
        # output.write('\caption{}Performance overview in terms of optimality gap of proposed heuristics for {}.{}\n'.format('{', labels[characteristic][value].lower(), '}'))
        # output.write('\end{figure}')

        print('Exported graph to graphs/objectives.tex')

def graph3(descriptor = 'paper'):

    methods = ['cold_lrz', 'cold_net', 'bbd', 'bbe']

    colors = {
        'cold_lrz' : 'red',
        'cold_net' : 'gray',
        'bbd': 'blue',
        'bbe' : 'orange'
    }

    styles = {
        'cold_lrz' : 'dashed',
        'cold_net' : 'dotted',
        'bbd': 'dashdotted',
        'bbe' : 'solid'
    }

    filter = (content['periods'] == 10)

    with open ('graphs/runtime.tex', 'w') as output:

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (10.5,0);\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,10.5);\n')

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (9,0.5) node[anchor=mid] {time ratio ($10^{0}$)};\n')
        output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

        for x in range(0,11):
            output.write('\draw ({},-0.5) node[anchor=mid] {}{}{};\n'.format(x - 1, '{$', x,'$}'))
        for y in range(0,11):
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{}{};\n'.format(y, '{$', y * 10,'$}'))


        for method in methods:

            prev_x = 1
            prev_y = int(100 * len(content[filter & (content['{}_ratio_runtime'.format(method)] <= prev_x)])/len(content[filter]))

            for x in range(1,11,1):

                y = int(100 * len(content[filter & (content['{}_ratio_runtime'.format(method)] <= x)])/len(content[filter]))
                output.write('\draw[line width=0.5mm,{},{}] ({},{})--({},{});'.format(colors[method], styles[method], prev_x - 1, prev_y/10, x - 1, y/10))

                prev_x = x
                prev_y = y

        output.write('\n')

        output.write('\draw[line width=0.5mm,red, dashed] (8.5, 3.5)--(9.0, 3.5);\n')
        output.write('\draw[line width=0.5mm,red] (9.0, 3.5) node[anchor=west] {STI};\n')
        output.write('\draw[line width=0.5mm,gray, dotted] (8.5, 3.0)--(9.0, 3.0);\n')
        output.write('\draw[line width=0.5mm,gray] (9.0, 3.0) node[anchor=west] {DTI};\n')
        output.write('\draw[line width=0.5mm,blue, dashdotted] (8.5, 2.5)--(9.0, 2.5);\n')
        output.write('\draw[line width=0.5mm,blue] (9.0, 2.5) node[anchor=west] {BSD};\n')
        output.write('\draw[line width=0.5mm,orange, solid] (8.5, 2.0)--(9.0, 2.0);\n')
        output.write('\draw[line width=0.5mm,orange] (9.0, 2.0) node[anchor=west] {BSE};\n')
        # output.write('\draw (8,4.0)--(11,4.0)--(11,1.5)--(8,1.5)--(8,4.0);\n')

        output.write('\end{tikzpicture}\n')
        # output.write('\caption{}Performance overview in terms of optimality gap of proposed heuristics for {}.{}\n'.format('{', labels[characteristic][value].lower(), '}'))
        # output.write('\end{figure}')

        print('Exported graph to graphs/runtime.tex')

table1('paper')
table2('paper')
table3('paper')
table4('paper')
table5('paper')
table6('paper')
graph1('paper')
graph2('paper')
graph3('paper')