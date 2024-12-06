import pandas as pd
import common as cm
import matplotlib.pyplot as plt

# Analysis instance set C
content = pd.read_csv('results/paper1/mrg_summary.csv')
# content = content[content['customers'] == 1]

content['index'] = content['keyword']
content = content.set_index('index')

# Single facility
formulation_approaches = ['cold_lrz', 'cold_net']
benders_approaches = ['bbd', 'bbe'] # , 'bbe', 'bbh']
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
    # content['{}_optgap'.format(method)] = content.apply(lambda row: cm.compute_gap(row['bst_bound'], row['{}_objective'.format(method)]), axis = 1)

for approach in heuristic_approaches:
    content['{}_optgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['bst_objective'], row['{}_objective'.format(approach)]), axis = 1)

for approach in exact_approaches:
    content['{}_optimal'.format(approach)] = content.apply(lambda row: (row['{}_optgap'.format(approach)] <= cm.TOLERANCE), axis = 1)

for approach in formulation_approaches:
    approach = approach.replace('cold_', '')
    content['{}_intgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['rlx_{}_bound'.format(approach)], row['bst_objective']), axis = 1)

for approach in exact_approaches:
    content['{}_optgap'.format(approach)] = content.apply(lambda row: 1 if row['{}_optgap'.format(approach)] > 1 else row['{}_optgap'.format(approach)], axis = 1)
    content['{}_ratio_objective'.format(approach)] = content.apply(lambda row: round(row['bst_objective'] / (row['{}_objective'.format(approach)] + cm.TOLERANCE), cm.PRECISION), axis = 1)
    content['{}_ratio_runtime'.format(approach)] = content.apply(lambda row: round(row['{}_runtime'.format(approach)] / (row['bst_runtime'] + cm.TOLERANCE), cm.PRECISION), axis = 1)
    content['{}_bstgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['bst_objective'], row['{}_objective'.format(approach)]), axis = 1)

content.to_csv('debugging.csv')

characteristics = {
    'branch': ['paper1'],
    'locations': [100, 200],
    'customers': [1, 5],
    'periods': [5, 10],
    'facilities': [1], # [1, 2, 3, 4],
    'penalties': [1, 2],
    'rewards': ['identical', 'inversely'],
    'preferences': ['small', 'large'],
    'demands': ['constant', 'seasonal'],
    'characters': ['homogeneous','heterogeneous']
}

labels = {
    'branch': {
        'paper1': 'Instance set C',
    },
    'locations': {
        100: '100 locations',
        200: '200 locations',
    },
    'customers': {
        1: 'x1 customers',
        5: 'x5 customers',
    },
    'periods': {
        5: '5 periods',
        10: '10 periods',
    },
    'facilities': {
        1: '1 facility',
        5: '5 facilities',
    },
    'penalties':{
        1: '25\% penalties',
        2: '50\% penalties'
    },
    'rewards':{
        'identical': 'Identical rewards',
        'inversely': 'Different rewards'
    },
    'preferences': {
        'small': 'Small choice sets',
        'large': 'Large choice sets'
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

layer1 = {
    'locations': [100, 200]
}

layer2 = {
    'customers': [1, 5]
}

def table1(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)

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

def stack1(descriptor = 'paper'):

    for label1, values1 in layer1.items():

        for value1 in values1:

                for label2, values2 in layer2.items():

                    for value2 in values2:

                        if descriptor == 'paper':
                            columns = ['lrz_intgap', 'cold_lrz_runtime', 'net_intgap', 'cold_net_runtime']
                            filter = (content[label1] == value1) & (content[label2] == value2) & (content['cold_lrz_optimal'] == True) & (content['cold_net_optimal'] == True)
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
                        total = len(content[(content[label1] == value1) | (content[label2] == value2)].index)

                        # print('{}&${:.2f}$&{}{}{}'.
                        print('{}&{}&${} \, ({})$&{}{}{}'.
                        format(labels[label1][value1], labels[label2][value2], count, total, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

                    print('\\midrule')

    _ = input('table1 {}'.format(descriptor))

    print('**************************************************************************************************')

def table2(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & ((content['cold_lrz_optimal'] == False) | (content['cold_net_optimal'] == False))

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

def stack2(descriptor = 'paper'):

    for label1, values1 in layer1.items():

        for value1 in values1:

                for label2, values2 in layer2.items():

                    for value2 in values2:

                        if descriptor == 'paper':
                            columns = ['cold_lrz_optgap', 'cold_net_optgap']
                            filter = (content[label1] == value1) & (content[label2] == value2) & ((content['cold_lrz_optimal'] == False) | (content['cold_net_optimal'] == False))
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
                        total = len(content[(content[label1] == value1) & (content[label2] == value2)].index)

                        # print('{}&${:.2f}$&{}{}{}'.
                        print('{}&{}&${} \, ({})$&{}{}{}'.
                        format(labels[label1][value1], labels[label2][value2], count, total, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

                    print('\\midrule')

    _ = input('table2 {}'.format(descriptor))

    print('**************************************************************************************************')

def table3(descriptor = 'paper'):

    for characteristic, values in characteristics.items():

        for value in values:

            filter = (content[characteristic] == value) & (content['bst_optimal'] == True)

            if descriptor == 'paper':
                columns = ['eml_optgap', 'rnd_optgap', 'frw_optgap', 'bcw_optgap']
            else:
                exit('Wrong descriptor for table 3')

            averages = {}
            deviations = {}
            maximums = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * 100, 2)
                deviations[column] = round(content[filter][column].std() * 100, 2)
                # maximums[column] = round(content[filter][column].max() * 100, 2)

            # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
            count = len(content[filter].index)
            total = len(content[(content[characteristic] == value)].index)

            print('{}&${} \, ({})$&{}{}{}'.
            format(labels[characteristic][value], count, total, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table3 {}'.format(descriptor))

    print('**************************************************************************************************')

def table4(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True) # & (content['bbf_optimal'] == True) & (content['bbh_optimal'] == True)

    content[filter].boxplot(['cold_net_runtime', 'bbd_runtime', 'bbe_runtime']) #, 'bbf_runtime', 'bbh_runtime'])
    plt.savefig('results/paper1/box_table4_runtime.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_runtime', 'bbd_runtime', 'bbe_runtime'] #, 'bbf_runtime', 'bbh_runtime']
                filter = (content[characteristic] == value) & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True) # & (content['bbf_optimal'] == True) & (content['bbh_optimal'] == True)
            else:
                exit('Wrong descriptor for table 4')

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

    _ = input('table4 {}'.format(descriptor))

    print('**************************************************************************************************')

def stack4(descriptor = 'paper'):

    for label1, values1 in layer1.items():

        for value1 in values1:

                for label2, values2 in layer2.items():

                    for value2 in values2:

                        if descriptor == 'paper':
                            columns = ['cold_net_runtime', 'bbd_runtime', 'bbf_runtime'] #, 'bbe_runtime', 'bbh_runtime']
                            filter = (content[label1] == value1) & (content[label2] == value2) & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True) & (content['bbf_optimal'] == True) # & (content['bbe_optimal'] == True) & (content['bbh_optimal'] == True)
                        else:
                            exit('Wrong descriptor for table 4')

                        averages = {}
                        deviations = {}
                        maximums = {}

                        for column in columns:
                            averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                            deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                            # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)

                        # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
                        count = len(content[filter].index)
                        total = len(content[(content[label1] == value1) & (content[label2] == value2)].index)

                        # print('{}&${:.2f}$&{}{}{}'.
                        print('{}&{}&${} \, ({})$&{}{}{}'.
                        format(labels[label1][value1], labels[label2][value2], count, total, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

                    print('\\midrule')

    _ = input('table4 {}'.format(descriptor))

    print('**************************************************************************************************')

def table5(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & ((content['cold_net_optimal'] == False) | (content['bbd_optimal'] == False) | (content['bbe_optimal'] == False)) # | (content['bbf_optimal'] == False) & (content['bbh_optimal'] == False))

    content[filter].boxplot(['cold_net_optgap', 'bbd_optgap', 'bbe_optgap']) #, 'bbf_optgap', 'bbh_optgap'])
    plt.savefig('results/paper1/box_table5_optgap.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_optgap', 'bbd_optgap', 'bbe_optgap'] #, 'bbf_optgap', 'bbh_optgap']
                filter = (content[characteristic] == value) & ((content['cold_net_optimal'] == False) | (content['bbd_optimal'] == False) | (content['bbe_optimal'] == False)) # | (content['bbf_optimal'] == False) | (content['bbh_optimal'] == False))
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

            # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
            count = len(content[filter].index)
            total = len(content[(content[characteristic] == value)].index)

            # print('{}&${:.2f}$&{}{}{}'.
            print('{}&${} \, ({})$&{}{}{}'.
            format(labels[characteristic][value], count, total, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table5 {}'.format(descriptor))

    print('**************************************************************************************************')

def stack5(descriptor = 'paper'):

    for label1, values1 in layer1.items():

        for value1 in values1:

                for label2, values2 in layer2.items():

                    for value2 in values2:

                        if descriptor == 'paper':
                            columns = ['cold_net_optgap', 'bbd_optgap', 'bbf_optgap'] #, 'bbe_optgap', 'bbh_optgap']
                            filter = (content[label1] == value1) & (content[label2] == value2) & ((content['cold_net_optimal'] == False) | (content['bbd_optimal'] == False) | (content['bbf_optimal'] == False)) # | (content['bbe_optimal'] == False) | (content['bbh_optimal'] == False))
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

                        # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
                        count = len(content[filter].index)
                        total = len(content[(content[label1] == value1) & (content[label2] == value2)].index)

                        # print('{}&${:.2f}$&{}{}{}'.
                        print('{}&{}&${} \, ({})$&{}{}{}'.
                        format(labels[label1][value1], labels[label2][value2], count, total, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

                    print('\\midrule')

    _ = input('table5 {}'.format(descriptor))

    print('**************************************************************************************************')

def table6(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True) # & (content['bbf_optimal'] == True) & (content['bbh_optimal'] == True)

    content[filter].boxplot(['bbd_nodes', 'bbe_nodes']) #, 'bbf_nodes', 'bbh_nodes'])
    plt.savefig('results/paper1/box_table6_nodes.png')
    plt.figure().clear()

    content[filter].boxplot(['bbd_proportion', 'bbe_proportion']) #, 'bbf_proportion', 'bbh_proportion'])
    plt.savefig('results/paper1/box_table6_proportion.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['bbd_nodes', 'bbd_proportion', 'bbe_nodes', 'bbe_proportion'] # , 'bbf_nodes', 'bbf_proportion', 'bbh_nodes', 'bbh_proportion']
                # columns = ['bbd_cuts_integer', 'bbd_proportion', 'bbe_cuts_integer', 'bbe_proportion']
                filter = (content[characteristic] == value) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True) # & (content['bbf_optimal'] == True) & (content['bbh_optimal'] == True)
                # filter = (content[characteristic] == value) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True)
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

            # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
            count = len(content[filter].index)
            total = len(content[(content[characteristic] == value)].index)

            # print('{}&${:.2f}$&{}{}{}'.
            print('{}&${} \, ({})$&{}{}{}'.
            format(labels[characteristic][value], count, total, '&'.join(['${:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

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

    filter = (content['branch'] == 'paper1') # & (content['bst_optgap'] > cm.TOLERANCE)

    with open ('graphs/heuristics.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 0, 1.0, 0.1
        length_y, lower_y, upper_y, step_y = 10, 0, 100, 10

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,10.5);\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (9.5,0.5) node[anchor=mid] {opportunity gap};\n')
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

            prev_x = 0
            prev_y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while x <= upper_x:

                y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= x)]) / len(content[filter]))

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

        print('Exported graph to graphs/heuristics.tex')

def graph2(descriptor = 'paper'):

    methods = ['cold_lrz', 'cold_net', 'bbd', 'bbe'] #, 'bbf', 'bbh']

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

    filter = (content['branch'] == 'paper1') # & (content['bst_optgap'] > cm.TOLERANCE)

    with open ('graphs/objectives.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 0, 0.5, 0.05
        length_y, lower_y, upper_y, step_y = 10, 60, 100, 6

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (9.5,0.5) node[anchor=mid] {gap to best objective};\n')
        output.write('\draw (0,11) node[anchor=mid] {instances (\%)};\n')

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.3f}{};\n'.format(formatted_x, '{$', x,'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 0
            prev_y = int(100 * len(content[filter & (content['{}_bstgap'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while x <= upper_x:

                y = int(100 * len(content[filter & (content['{}_bstgap'.format(method)] <= x)]) / len(content[filter]))

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

    methods = ['cold_lrz', 'cold_net', 'bbd', 'bbe'] #, 'bbf', 'bbh']

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

    filter = (content['branch'] == 'paper1') # & (content['bst_optgap'] > cm.TOLERANCE)

    with open ('graphs/runtimes.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 1, 5, 0.4
        length_y, lower_y, upper_y, step_y = 10, 10, 100, 9

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

# graph1('paper')
graph2('paper')
graph3('paper')
table1('paper')
table2('paper')
table4('paper')
table5('paper')
table6('paper')
# table3('paper')

# stack1('paper')
# stack2('paper')
# stack4('paper')
# stack5('paper')