import uuid as ui

counter = 0
folder = 'instances'

locations = [10, 50, 100]
customers = [10, 50, 100]
periods = [7, 14, 30]

preferences = ['high'] # ['low', 'medium', 'high']
revenues = ['equal', 'different']
replenishment = ['linear', 'exponential']
alphabeta = ['high'] #  ['low', 'medium', 'high']
absorption = ['linear', 'exponential']
gammadelta = ['high'] # ['low', 'medium', 'high']
starting = ['high'] # ['low', 'medium', 'high']

with open('database.csv','w') as database:
    for a in locations:
        for b in customers:
            for c in periods:
                for d in preferences:
                    for e in revenues:
                        for f in replenishment:
                            for g in alphabeta:
                                for h in absorption:
                                    for i in gammadelta:
                                        for j in starting:
                                            keyword = ui.uuid4().hex[:10]
                                            with open('{}/{}.csv'.format(folder, keyword), 'w') as output:
                                                output.write('title,value\n')
                                                output.write('number of locations,{}\n'.format(a))
                                                output.write('number of customers,{}\n'.format(b))
                                                output.write('number of periods,{}\n'.format(c))
                                                output.write('willingness to patronize,{}\n'.format(d))
                                                output.write('location revenues,{}\n'.format(e))
                                                output.write('replenishment type,{}\n'.format(f))
                                                output.write('replenishment variability,{}\n'.format(g))
                                                output.write('absorption type,{}\n'.format(h))
                                                output.write('absorption variability,{}\n'.format(i))
                                                output.write('starting demand,{}\n'.format(j))

                                            database.write('{},{},{},{},{},{},{},{},{},{},{}\n'.format(keyword, a, b, c, d, e, f, g, h, i, j))
                                            counter += 1

print('Generated {} instances'.format(counter))