import pandas as pd
import common as cm
import matplotlib.pyplot as plt


# content = pd.read_csv('results/paper1/fixed-notcaught.csv')
content = pd.read_csv('results/paper1/everyone-identical.csv')
# content = pd.read_csv('results/paper1/summary.csv')

# content = unfiltered.copy()
# content = content[content['customers'] != 2]
# content = content[content['penalties'] == 0]

content['index'] = content['keyword']
content = content.set_index('index')

formulation_approaches = ['cold_net']
benders_approaches = [] # 'bbd', 'bbe'] # , 'bbe', 'bbh']
heuristic_approaches = [] # ['eml', 'rnd', 'frw', 'bcw']
exact_approaches = formulation_approaches + benders_approaches

content['bst_objective'] = content.apply(lambda row: row['cold_net_objective'], axis = 1)
content['bst_runtime'] = content.apply(lambda row: row['cold_net_runtime'], axis = 1)
content['bst_optgap'] = content.apply(lambda row: row['cold_net_optgap'], axis = 1)
content['bst_bound'] = content.apply(lambda row: row['cold_net_bound'], axis = 1)
content['bst_optimal'] = content.apply(lambda row: (row['bst_optgap'] <= cm.TOLERANCE), axis = 1)
content['bst_solution'] = content.apply(lambda row: row['cold_net_solution'], axis = 1)

for method in benders_approaches:
    content['{}_proportion'.format(method)] = content.apply(lambda row: (row['{}_subtime_integer'.format(method)] + row['{}_subtime_fractional'.format(method)]) / row['{}_runtime'.format(method)], axis = 1)
    content['{}_nodes'.format(method)] = content.apply(lambda row: row['{}_nodes'.format(method)]  / 10**6, axis = 1)
    # content['{}_optgap'.format(method)] = content.apply(lambda row: cm.compute_gap(row['bst_bound'], row['{}_objective'.format(method)]), axis = 1)

for approach in heuristic_approaches:
    content['{}_optgap'.format(approach)] = content.apply(lambda row: cm.compute_gap1(row['bst_objective'], row['{}_objective'.format(approach)]), axis = 1)

for approach in exact_approaches:
    content['{}_optimal'.format(approach)] = content.apply(lambda row: (row['{}_optgap'.format(approach)] <= cm.TOLERANCE), axis = 1)

for approach in formulation_approaches:
    approach = approach.replace('cold_', '')
    content['{}_intgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['rlx_{}_bound'.format(approach)], row['bst_objective']), axis = 1)

for approach in exact_approaches:
    # content['{}_optgap'.format(approach)] = content.apply(lambda row: 1 if row['{}_optgap'.format(approach)] > 1 else row['{}_optgap'.format(approach)], axis = 1)
    content['{}_bstime'.format(approach)] = content.apply(lambda row: round(row['{}_runtime'.format(approach)] / (row['bst_runtime'] + cm.TOLERANCE), cm.PRECISION), axis = 1)
    content['{}_bstgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['bst_objective'], row['{}_objective'.format(approach)]), axis = 1)

content.to_csv('debugging.csv')

characteristics = {
    'branch': ['paper1'],
    'locations': [100, 200],
    'customers': [1, 5],
    'periods': [5, 10],
    'facilities': [1, 5],
    'rewards': ['identical', 'inversely'],
    'preferences': ['small', 'large'],
    'demands': ['constant', 'seasonal'],
    'characters': ['homogeneous','heterogeneous']
}

labels = {
    'branch': {
        'paper1': 'Benchmark',
    },
    'locations': {
        100: '100 locations',
        200: '200 locations',
    },
    'customers': {
        1: 'x1 customers',
        2: 'x2 customers',
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

colors = {
    'cold_lrz' : 'red',
    'cold_net' : 'teal',
    'bbd': 'blue',
    'bbe' : 'orange',
    'rnd' : 'teal',
    'frw' : 'blue',
    'bcw' : 'orange',
    'eml': 'red',
}

styles = {
    'cold_lrz' : 'dashed',
    'cold_net' : 'dotted',
    'bbd': 'dashdotted',
    'bbe' : 'solid',
    'rnd' : 'dotted',
    'frw' : 'dashdotted',
    'bcw' : 'solid',
    'eml': 'dashed'
}

legend = {
    'cold_lrz' : 'SIF',
    'cold_net' : 'DIF',
    'bbd': 'SBD',
    'bbe' : 'ABD',
    'rnd' : 'RND',
    'frw' : 'FGH',
    'bcw' : 'BGH',
    'eml': 'DBH'
}

def graph_effectpenalties():

    with open ('graphs/effectpenalties.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 5, 0, 50, 10
        length_y, lower_y, upper_y, step_y = 5, 0, 1.2 * 10 ** 4, 0.2

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}penalties $p_j${};\n'.format(length_x - 1, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}total penalty{};\n'.format(length_y + 1, '{', '}'))

        fac = {
            1: 'green',
            3: 'red',
            5: 'blue'
        }

        for facility in [1,3,5]:

            formatted_x = 0
            while formatted_x <= length_x:
                x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
                output.write('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_x, '{$', x, '$}'))
                formatted_x += 1

            formatted_y = 0
            while formatted_y <= length_y:
                y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
                output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
                formatted_y += 1

            prev_x = 0

            instance = cm.load_instance('bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, prev_x))
            solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, prev_x)].iloc[0]['cold_net_solution']
            reward, penalty = instance.evaluate_solution2(instance.unpack_solution(solution))

            # r_reward = reward
            # r_penalty = penalty

            prev_y1 = reward
            prev_y2 = penalty

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                instance = cm.load_instance('bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, x))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, x)].iloc[0]['cold_net_solution']
                reward, penalty = instance.evaluate_solution2(instance.unpack_solution(solution))

                y1 = reward #/ r_reward
                y2 = penalty # / r_penalty

                print('Reward: {}'.format(reward))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y1 = length_y * (prev_y1 - lower_y) / (upper_y - lower_y)
                formatted_prev_y2 = length_y * (prev_y2 - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y1 = length_y * (y1 - lower_y) / (upper_y - lower_y)
                formatted_y2 = length_y * (y2 - lower_y) / (upper_y - lower_y)

                # output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(fac[facility], 'solid', formatted_prev_x, formatted_prev_y1, formatted_x, formatted_y1))
                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(fac[facility], 'dotted', formatted_prev_x, formatted_prev_y2, formatted_x, formatted_y2))

                prev_x = x
                prev_y1 = y1
                prev_y2 = y2

            output.write('\n')

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/effectpenalties.tex')

def graph_effectrewards():

    with open ('graphs/effectrewards.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 9, 0, 90, 10
        length_y, lower_y, upper_y, step_y = 10, 0, 1.2 * 10 ** 4, 0.2

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}penalties $p_j${};\n'.format(length_x - 1, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}total reward{};\n'.format(length_y + 1, '{', '}'))

        fac = {
            1: 'green',
            3: 'red',
            5: 'blue'
        }

        for facility in [1,3,5]:

            formatted_x = 0
            while formatted_x <= length_x:
                x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
                output.write('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_x, '{$', x, '$}'))
                formatted_x += 1

            formatted_y = 0
            while formatted_y <= length_y:
                y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
                output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
                formatted_y += 1

            prev_x = 0

            instance = cm.load_instance('bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, prev_x))
            solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, prev_x)].iloc[0]['cold_net_solution']
            reward, penalty = instance.evaluate_solution2(instance.unpack_solution(solution))

            # r_reward = reward
            # r_penalty = penalty

            prev_y1 = reward
            prev_y2 = penalty

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                instance = cm.load_instance('bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, x))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-identical-large-fixed-{}'.format(facility, x)].iloc[0]['cold_net_solution']
                reward, penalty = instance.evaluate_solution2(instance.unpack_solution(solution))

                y1 = reward #/ r_reward
                y2 = penalty # / r_penalty

                print('Reward: {}'.format(reward))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y1 = length_y * (prev_y1 - lower_y) / (upper_y - lower_y)
                formatted_prev_y2 = length_y * (prev_y2 - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y1 = length_y * (y1 - lower_y) / (upper_y - lower_y)
                formatted_y2 = length_y * (y2 - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(fac[facility], 'solid', formatted_prev_x, formatted_prev_y1, formatted_x, formatted_y1))
                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(fac[facility], 'dotted', formatted_prev_x, formatted_prev_y2, formatted_x, formatted_y2))

                prev_x = x
                prev_y1 = y1
                prev_y2 = y2

            output.write('\n')

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/effectrewards.tex')

# graph_effectrewards()
# graph_effectpenalties()

def graph_numbercaptures():

    with open ('graphs/numbercaptures.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 0, 50, 3
        length_y, lower_y, upper_y, step_y = 5, 0, 5, 0.2

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}penalties (\%){};\n'.format(length_x - 1, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}reward/penalty{};\n'.format(length_y + 1, '{', '}'))

        fac = {
            1: 'green',
            3: 'red',
            5: 'blue'
        }

        for facility in [1,3,5]:

            formatted_x = 0
            while formatted_x <= length_x:
                x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
                output.write('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_x, '{$', x, '$}'))
                formatted_x += 1

            formatted_y = 0
            while formatted_y <= length_y:
                y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
                output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
                formatted_y += 1

            prev_x = facility

            # instance = cm.load_instance('bmk_1-50-1-5-{}-identical-large-fixed-0'.format(facility))
            # solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-identical-large-fixed-0'.format(facility)].iloc[0]['cold_net_solution']
            # captures = instance.evaluate_customer2(instance.unpack_solution(solution), str(prev_x))

            prev_y = 0

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                instance = cm.load_instance('bmk_1-50-1-5-{}-identical-large-fixed-0'.format(facility))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-identical-large-fixed-0'.format(facility)].iloc[0]['cold_net_solution']
                captures = instance.evaluate_customer2(instance.unpack_solution(solution), str(x))

                y = captures

                print('Customer {}, #{} captures [facility {}]'.format(x, y, facility))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(fac[facility], 'solid', formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))
                prev_x = x
                prev_y = y

            output.write('\n')

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/numbercaptures.tex')

def graph_histogram():

    with open ('graphs/histogram.tex', 'w') as output:

        fac = {
            1: 'green',
            3: 'red',
            5: 'blue'
        }

        captures  = {}

        for period in [0,1,2,3,4,5]:
            captures[period] = {}
            for facility in [1,3,5]:

                captures[period][facility] = 0

                instance = cm.load_instance('bmk_1-50-1-5-{}-identical-large-fixed-0'.format(facility))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-identical-large-fixed-0'.format(facility)].iloc[0]['cold_net_solution']

                for customer in instance.customers:
                    capture = instance.evaluate_customer2(instance.unpack_solution(solution), customer)
                    if capture == period:
                        captures[period][facility] += 1

        length_x, lower_x, upper_x, step_x = 25, 0, 25, 1
        length_y, lower_y, upper_y, step_y = 5, 0, 40, 4

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}penalties (\%){};\n'.format(length_x - 1, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}reward/penalty{};\n'.format(length_y + 1, '{', '}'))

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_x, '{$', x, '$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
            formatted_y += 1

        for period in [0,1,2,3,4,5]:

            for f, facility in enumerate([1,3,5]):

                x = period * 4 + f + 1
                y = captures[period][facility]

                print('Facility {}, captures{}, #{}'.format(facility, period, y))

                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f})--({:.2f},{:.2f})--({:.2f},{:.2f});'.format(fac[facility], 'solid', formatted_x - 0.5, 0, formatted_x - 0.5, formatted_y, formatted_x + 0.5, formatted_y, formatted_x + 0.5, 0))

            output.write('\n')

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/histogram.tex')

# graph_numbercaptures()

graph_histogram()