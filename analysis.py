import pandas as pd
import main as mn

content = pd.read_csv('experiments/paper1/summary.csv')

content['cold_lrz_optimal'] = content.apply(lambda row: mn.compare_obj(row['upper_bound'], row['cold_lrz_objective']) and (row['cold_lrz_status'] == 2 or row['warm_lrz_status'] == 2 or row['warm_net_status'] == 2 or row['cold_net_status'] == 2), axis = 1)
content['cold_net_optimal'] = content.apply(lambda row: mn.compare_obj(row['upper_bound'], row['cold_net_objective']) and (row['cold_lrz_status'] == 2 or row['warm_lrz_status'] == 2 or row['warm_net_status'] == 2 or row['cold_net_status'] == 2), axis = 1)

# content.to_csv('debugging.csv')

characteristics = {
    'project': ['paper1'],
    'locations': [10, 50, 100],
    'periods': [5, 10],
    'patronizing': ['small', 'medium', 'large'],
    'rewards': ['identical', 'inversely'],
    'character': ['homogeneous', 'heterogeneous'],
    'replenishment': ['absolute', 'relative', 'mixed']
}

labels = {
    'project': {
        'paper1': 'Complete benchmark'
    },
    'periods': {
        5: '5 time periods',
        10: '10 time periods',
    },
    'locations': {
        10: '10 locations/customers',
        50: '50 locations/customers',
        100: '100 locations/customers',
    },
    'patronizing': {
        'small': 'Small patronizing',
        'medium': 'Medium patronizing',
        'large': 'Large patronizing'
    },
    'rewards':{
        'identical': 'Identical rewards',
        'inversely': 'Inversely rewards'
    },
    'character': {
        'homogeneous': 'Homogeneous customer',
        'heterogeneous': 'Heterogeneous customer'
    },
    'replenishment': {
        'absolute': 'Absolute replenishment',
        'relative': 'Relative replenishment',
        'mixed': 'Mixed replenishment'
    }
}

def table1(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            filter = (content[characteristic] == value) & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)

            if descriptor == 'paper':
                columns = ['lrz_intgap', 'net_intgap', 'cold_lrz_runtime', 'cold_net_runtime'] # 'cold_nlr_runtime', 'warm_nlr_runtime'
            else:
                exit('Wrong descriptor for table 2')

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

        print('\\midrule')

    _ = input('table1 {}'.format(descriptor))

    print('**************************************************************************************************')

def table2(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            filter = (content[characteristic] == value) & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)

            if descriptor == 'paper':
                columns = ['em1_optgap', 'em2_optgap', 'rnd_optgap', 'frw_optgap']
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

    _ = input('table2 {}'.format(descriptor))

    print('**************************************************************************************************')

def table3(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            filter = (content[characteristic] == value) & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)

            if descriptor == 'paper':
                # columns = ['fix_optgap', 'frw_optgap', 'prg_optgap', 'bcw_optgap',]
                columns = ['frw_optgap', 'prg_optgap', 'bcw_optgap',]
            else:
                exit('Wrong descriptor for table 4')


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

def graph1(descriptor = 'paper'):

    methods = {
        'rnd' : 'orange',
        'frw' : 'red',
        'bcw' : 'blue',
        'prg' : 'olive',
        'em1': 'pink',
        #'fix' : 'gray',
        'em2' : 'magenta',
        'warm_lrz' : 'black'
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

                        if method == 'warm_lrz':
                            prev_y = 100
                            y = 100
                        else:
                            y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= x/100)])/len(content[filter]))
                        output.write('\draw[color={}] ({},{})--({},{});'.format(color, prev_x/10, prev_y/10, x/10, y/10))

                        prev_x = x
                        prev_y = y

                output.write('\n')

                output.write('\draw[color=black!100] (10, 5.0) node[anchor=mid] {MIP};\n')
                output.write('\draw[color=blue!100] (10, 4.5) node[anchor=mid] {BCW};\n')
                output.write('\draw[color=olive!100] (10, 4.0) node[anchor=mid] {PRG};\n')
                output.write('\draw[color=red!100] (10, 3.5) node[anchor=mid] {FRW};\n')
                output.write('\draw[color=orange!100] (10, 3.0) node[anchor=mid] {RND};\n')
                output.write('\draw[color=gray!100] (10, 2.5) node[anchor=mid] {FIX};\n')
                output.write('\draw[color=magenta!100] (10, 2.0) node[anchor=mid] {EML-$2$};\n')
                output.write('\draw[color=pink!100] (10, 1.5) node[anchor=mid] {EML-$1$};\n')
                output.write('\draw (9,5.5)--(11,5.5)--(11,1.0)--(9,1.0)--(9,5.5);\n')

                output.write('\end{tikzpicture}\n')
                # output.write('\caption{}Performance overview in terms of optimality gap of proposed heuristics for {}.{}\n'.format('{', labels[characteristic][value].lower(), '}'))
                # output.write('\end{figure}')

                print('Exported graph to graphs/graph_{}_{}.tex'.format(characteristic, value))

table1('paper')
table2('paper')
table3('paper')
graph1('paper')