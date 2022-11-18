import pandas as pd

content = pd.read_csv('s1e1-1-dflp-ra.csv')

for i in [10,20]:
    for t in [7,14]:
        for r in ['linear', 'exponential']:
            for a in ['linear', 'exponential']:

                filter = (content['I'] == i) & (content['T'] == t) & (content['replenishment'] == r) & (content['absorption']  == a)

                avg_intgap = round(content[filter]['mip_intgap'].mean() * 100, 2)
                avg_hrsgap = round(content[filter]['hrs_objgap'].mean() * 100, 2)
                avg_ap1gap = round(content[filter]['ap1_optgap'].mean() * 100, 2)
                avg_ap2gap = round(content[filter]['ap2_optgap'].mean() * 100, 2)
                avg_ap3gap = round(content[filter]['ap3_optgap'].mean() * 100, 2)

                std_intgap = round(content[filter]['mip_intgap'].std() * 100, 2)
                std_hrsgap = round(content[filter]['hrs_objgap'].std() * 100, 2)
                std_ap1gap = round(content[filter]['ap1_optgap'].std() * 100, 2)
                std_ap2gap = round(content[filter]['ap2_optgap'].std() * 100, 2)
                std_ap3gap = round(content[filter]['ap3_optgap'].std() * 100, 2)

                rp = 'lin' if r == 'linear' else 'exp'
                ab = 'lin' if a == 'linear' else 'exp'

                count = len(content[filter].index)

                print('({},{},{})&({},{})&{}&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%$&${}\pm{}\%${}{}'.format(i,i,t,rp,ab, count, avg_intgap, std_intgap, avg_hrsgap, std_hrsgap, avg_ap1gap, std_ap1gap, avg_ap2gap, std_ap2gap, avg_ap3gap, std_ap3gap, '\\', '\\'))
        print('\\midrule')