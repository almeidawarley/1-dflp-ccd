import pandas as pd

content = pd.read_csv('experiments/e2/report-e2sE.csv')

# content = content[(content['C'] == 'het')]

characteristics = {
    'L' : [3,5,7],
    'H': [50,75,99],
    'T': [5,10,15,20]
}

for characteristic, values in characteristics.items():

    for value in values:

        filter = (content[characteristic] == value)

        avg_intgap = round(content[filter]['mip_intgap'].mean() * 100, 2)
        avg_hrsgap = round(content[filter]['hrs_optgap'].mean() * 100, 2)
        avg_ap1gap = round(content[filter]['ap1_optgap'].mean() * 100, 2)
        avg_ap2gap = round(content[filter]['ap2_optgap'].mean() * 100, 2)
        avg_ap3gap = round(content[filter]['ap3_optgap'].mean() * 100, 2)

        std_intgap = round(content[filter]['mip_intgap'].std() * 100, 2)
        std_hrsgap = round(content[filter]['hrs_optgap'].std() * 100, 2)
        std_ap1gap = round(content[filter]['ap1_optgap'].std() * 100, 2)
        std_ap2gap = round(content[filter]['ap2_optgap'].std() * 100, 2)
        std_ap3gap = round(content[filter]['ap3_optgap'].std() * 100, 2)

        max_intgap = round(content[filter]['mip_intgap'].max() * 100, 2)
        max_hrsgap = round(content[filter]['hrs_optgap'].max() * 100, 2)
        max_ap1gap = round(content[filter]['ap1_optgap'].max() * 100, 2)
        max_ap2gap = round(content[filter]['ap2_optgap'].max() * 100, 2)
        max_ap3gap = round(content[filter]['ap3_optgap'].max() * 100, 2)

        count = len(content[filter].index)

        print('{}&{}&{}&${}\pm{}\%$&${}\pm{}\%$[${}$]&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%${}{}'.format(characteristic, value, count, avg_intgap, std_intgap, avg_hrsgap, std_hrsgap, max_hrsgap, avg_ap1gap, std_ap1gap, avg_ap2gap, std_ap2gap, avg_ap3gap, std_ap3gap, '\\', '\\'))

    print('\\midrule')

avg_intgap = round(content['mip_intgap'].mean() * 100, 2)
avg_hrsgap = round(content['hrs_optgap'].mean() * 100, 2)
avg_ap1gap = round(content['ap1_optgap'].mean() * 100, 2)
avg_ap2gap = round(content['ap2_optgap'].mean() * 100, 2)
avg_ap3gap = round(content['ap3_optgap'].mean() * 100, 2)

std_intgap = round(content['mip_intgap'].std() * 100, 2)
std_hrsgap = round(content['hrs_optgap'].std() * 100, 2)
std_ap1gap = round(content['ap1_optgap'].std() * 100, 2)
std_ap2gap = round(content['ap2_optgap'].std() * 100, 2)
std_ap3gap = round(content['ap3_optgap'].std() * 100, 2)

count = len(content.index)

print('All&&{}&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%${}{}'.format(count, avg_intgap, std_intgap, avg_hrsgap, std_hrsgap, avg_ap1gap, std_ap1gap, avg_ap2gap, std_ap2gap, avg_ap3gap, std_ap3gap, '\\', '\\'))