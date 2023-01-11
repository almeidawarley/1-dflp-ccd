import pandas as pd

content = pd.read_csv('experiments/e1/report-e1sC.csv')

c = 'hom'

content = content[content['C'] == c]

for r in ['abs', 'rel']:
    for a in ['abs', 'rel']:
        for o in [0,1,2]:
        # for i in [10, 20]:
            # for t in [5, 10, 15, 20]:

            # j = i

            # filter = (content['I'] == i) & (content['T'] == t) & (content['R'] == r) & (content['A']  == a)
            # filter = (content['U'] == u)
            filter = (content['O'] == o) & (content['R'] == r) & (content['A']  == a)

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

            count = len(content[filter].index)

            print('({},{})&{}&{}&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%${}{}'.format(r,a,o, count, avg_intgap, std_intgap, avg_hrsgap, std_hrsgap, avg_ap1gap, std_ap1gap, avg_ap2gap, std_ap2gap, avg_ap3gap, std_ap3gap, '\\', '\\'))
        # print('({})\t{}\t${}+-{}\%$\t${}+-{}\%$\t${}+-{}\%$\t${}+-{}\%$\t${}+-{}\%${}{}'.format(u,count, avg_intgap, std_intgap, avg_hrsgap, std_hrsgap, avg_ap1gap, std_ap1gap, avg_ap2gap, std_ap2gap, avg_ap3gap, std_ap3gap, '\\', '\\'))

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