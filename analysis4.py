import pandas as pd

content = pd.read_csv('experiments/predoc3/summary.csv')

content = content.replace('predoc3-het', 'predoc3')

characteristics = {
    'project': ['predoc3'],
    'periods': [5, 10, 20],
    'patronizing': ['weak', 'medium', 'strong'],
    'rewards': ['identical', 'inversely'],
    'replenishment': ['absolute', 'relative'],
    'absorption': ['complete', 'constrained']
}

labels = {
    'predoc3':'All instances',
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

content = content[content['character'] == 'homogeneous']
# content = content[content['character'] == 'heterogeneous']
content = content[content['rewards'] != 'directly']


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
            maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1), 2)

        count = len(content[filter].index)

        print('{}&{}&{}{}{}'.
        format(labels[value], count, '&'.join(['${}\pm{}\%({}\%)$'.format(averages[column], deviations[column], maximums[column]) for column in columns]), '\\', '\\'))

    print('\\midrule')

_ = input('table1')


print('**************************************************************************************************')

for characteristic, values in characteristics.items():

    for value in values:

        filter = (content[characteristic] == value)

        columns = ['ap2_optgap', 'rnd_optgap', 'frw_optgap']
        columns = ['ap1_optgap', 'ap3_optgap', 'ap2_optgap', 'rnd_optgap', 'frw_optgap']

        averages = {}
        deviations = {}
        maximums = {}

        for column in columns:
            averages[column] = round(content[filter][column].mean() * 100, 2)
            deviations[column] = round(content[filter][column].std() * 100, 2)
            maximums[column] = round(content[filter][column].max() * 100, 2)

        count = len(content[filter].index)

        print('{}&{}&{}&{}{}{}'.
        format(characteristic, value, count, '&'.join(['${}\pm{}\%({}\%)$'.format(averages[column], deviations[column], maximums[column]) for column in columns]), '\\', '\\'))

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
            maximums[column] = round(content[filter][column].max() * 100, 2)

        count = len(content[filter].index)

        print('{}&{}&{}&{}{}{}'.
        format(characteristic, value, count, '&'.join(['${}\pm{}\%({}\%)$'.format(averages[column], deviations[column], maximums[column]) for column in columns]), '\\', '\\'))

    print('\\midrule')

_ = input('table3')