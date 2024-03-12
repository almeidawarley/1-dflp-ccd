import pandas as pd
import common as cm

content = pd.read_csv('results/paper1/summary.csv')

exact_approaches = ['cold_lrz', 'warm_lrz', 'cold_net', 'warm_net', 'cold_nlr', 'warm_nlr', 'bbd', 'bba', 'bsd', 'bsa']

content['best_objective'] = content.apply(lambda row: max(row['{}_objective'.format(approach)] for approach in exact_approaches), axis = 1)
content['best_optgap'] = content.apply(lambda row: min(row['{}_optgap'.format(approach)] for approach in exact_approaches), axis = 1)
content['best_optimal'] = content.apply(lambda row: (row['best_optgap'] <= cm.TOLERANCE), axis = 1)

for approach in ['rnd', 'eml', 'frw', 'bcw', 'prg']:
    content['{}_optgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['best_objective'], row['{}_objective'.format(approach)]), axis = 1)

for approach in exact_approaches:
    content['{}_optimal'.format(approach)] = content.apply(lambda row: (row['{}_optgap'.format(approach)] <= cm.TOLERANCE), axis = 1)

for approach in ['lrz', 'net']:
    content['{}_intgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['rlx_{}_objective'.format(approach)], row['best_objective']), axis = 1)

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
        50: '50 locations',
        100: '100 locations',
    },
    'preferences': {
        'small': 'Small consideration',
        'large': 'Large consideration'
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
                columns = ['lrz_intgap', 'net_intgap', 'cold_lrz_runtime', 'cold_net_runtime']
                filter = (content[characteristic] == value) & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)
            elif descriptor == 'warmcold':
                columns = ['lrz_intgap', 'net_intgap', 'cold_lrz_runtime', 'warm_lrz_runtime', 'cold_net_runtime', 'warm_net_runtime']
                filter = (content[characteristic] == value) & (content['cold_lrz_optimal'] == True) & (content['warm_lrz_optimal'] == True) & (content['cold_net_optimal'] == True) & (content['warm_net_optimal'] == True)
            elif descriptor == 'withnlr':
                columns = ['lrz_intgap', 'net_intgap', 'cold_lrz_runtime', 'warm_lrz_runtime', 'cold_net_runtime', 'warm_net_runtime', 'cold_nlr_runtime', 'warm_nlr_runtime']
                filter = (content[characteristic] == value) & (content['cold_lrz_optimal'] == True) & (content['warm_lrz_optimal'] == True) & (content['cold_net_optimal'] == True) & (content['warm_net_optimal'] == True) & (content['cold_nlr_optimal'] == True) & (content['warm_nlr_optimal'] == True)
            else:
                exit('Wrong descriptor for table 1')

            averages = {}
            deviations = {}
            maximums = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)

            count = len(content[filter].index)

            print('{}&{}&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

            # print('Ratio {}: {}'.format(value, averages['lrz_intgap'] / averages['net_intgap']))

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

            '''
            for column in columns:
                averages[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                feasibles[column] = content[filter & (content[column] > cm.TOLERANCE)][column].count()
            '''

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                optimals[column] = content[filter & (content[column] <= cm.TOLERANCE)][column].count()

            count = len(content[filter].index)

            print('{}&{}&{}{}{}'.
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

            count = len(content[filter].index)

            print('{}&{}&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table3 {}'.format(descriptor))

    print('**************************************************************************************************')

def table4(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_runtime', 'bbd_runtime', 'bba_runtime']
                filter = (content[characteristic] == value) & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True) & (content['bba_optimal'] == True)
            elif descriptor == 'duality':
                columns = ['cold_net_runtime', 'bbd_runtime', 'bsd_runtime']
                filter = (content[characteristic] == value) & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True) & (content['bsd_optimal'] == True)
            elif descriptor == 'analytical':
                columns = ['cold_net_runtime', 'bba_runtime', 'bsa_runtime']
                filter = (content[characteristic] == value) & (content['cold_net_optimal'] == True) & (content['bba_optimal'] == True) & (content['bsa_optimal'] == True)
            else:
                exit('Wrong descriptor for table 4')

            averages = {}
            deviations = {}
            maximums = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)

            # print('Ratio {}: {}'.format(value, averages['bbd_runtime'] / averages['bba_runtime']))

            count = len(content[filter].index)

            print('{}&{}&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table4 {}'.format(descriptor))

    print('**************************************************************************************************')

def table5(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_optgap', 'bbd_optgap', 'bba_optgap']
                filter = (content[characteristic] == value) & ((content['cold_net_optimal'] == False) | (content['bbd_optimal'] == False) | (content['bba_optimal'] == False))
            else:
                exit('Wrong descriptor for table 5')

            averages = {}
            deviations = {}
            maximums = {}
            feasibles = {}
            optimals = {}

            '''
            for column in columns:
                averages[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter & (content[column] > cm.TOLERANCE)][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                feasibles[column] = content[filter & (content[column] > cm.TOLERANCE)][column].count()
            '''

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                optimals[column] = content[filter & (content[column] <= cm.TOLERANCE)][column].count()

            count = len(content[filter].index)

            print('{}&{}&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table5 {}'.format(descriptor))

    print('**************************************************************************************************')

def table6(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['bbd_iterations', 'bba_iterations']
                filter = (content[characteristic] == value) #& (content['bbd_optimal'] == True) & (content['bba_optimal'] == True)
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

            count = len(content[filter].index)

            print('{}&{}&{}{}{}'.
            format(labels[characteristic][value], count, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

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

    for characteristic, values in characteristics.items():

        for value in values:

            # filter = (content['project'] == 'paper1')
            filter = (content[characteristic] == value)

            with open ('graphs/graph1_{}_{}.tex'.format(characteristic, value), 'w') as output:

                # output.write('\\begin{figure}[!ht]\n\centering\n')
                output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
                output.write('\draw[thick,->] (0,0) -- (10.5,0);\n')
                output.write('\draw[thick,->] (0,0) -- (0,10.5);\n')

                output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
                output.write('\draw (9,0.5) node[anchor=mid] {opportunity gap (\%)};\n')
                output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

                for x in range(1,11):
                    output.write('\draw ({},-0.5) node[anchor=mid] {}{}{};\n'.format(x, '{$', x * 10,'$}'))
                for y in range(1,11):
                    output.write('\draw (-0.5,{}) node[anchor=mid] {}{}{};\n'.format(y, '{$', y * 10,'$}'))


                for method in methods:

                    prev_x = 0
                    prev_y = 0

                    for x in range(1,101,5):

                        y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= x/100)])/len(content[filter]))
                        output.write('\draw[{},{}] ({},{})--({},{});'.format(colors[method], styles[method], prev_x/10, prev_y/10, x/10, y/10))

                        prev_x = x
                        prev_y = y

                output.write('\n')

                output.write('\draw[red, dashed] (8.5, 3.5)--(9.0, 3.5);\n')
                output.write('\draw[red] (9.0, 3.5) node[anchor=west] {DSFLP};\n')
                output.write('\draw[gray, dotted] (8.5, 3.0)--(9.0, 3.0);\n')
                output.write('\draw[gray] (9.0, 3.0) node[anchor=west] {RND};\n')
                output.write('\draw[blue, dashdotted] (8.5, 2.5)--(9.0, 2.5);\n')
                output.write('\draw[blue] (9.0, 2.5) node[anchor=west] {FRW};\n')
                output.write('\draw[orange, solid] (8.5, 2.0)--(9.0, 2.0);\n')
                output.write('\draw[orange] (9.0, 2.0) node[anchor=west] {BCW};\n')
                # output.write('\draw (8,4.0)--(11,4.0)--(11,1.5)--(8,1.5)--(8,4.0);\n')

                output.write('\end{tikzpicture}\n')
                # output.write('\caption{}Performance overview in terms of optimality gap of proposed heuristics for {}.{}\n'.format('{', labels[characteristic][value].lower(), '}'))
                # output.write('\end{figure}')

                print('Exported graph to graphs/graph_{}_{}.tex'.format(characteristic, value))

table1('paper')
table2('paper')
table3('paper')
table4('paper')
table5('paper')
graph1('paper')
table6('paper')