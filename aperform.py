import pandas as pd
import common as cm
import matplotlib.pyplot as plt

content = pd.read_csv('results/paper1/summary.csv')

content['index'] = content['keyword']
content = content.set_index('index')
content = content[content['seed'] == 1]

formulation_approaches = ['cold_lrz', 'cold_net']
benders_approaches = ['bbd', 'bbe']
heuristic_approaches = ['eml', 'rnd', 'frw', 'bcw']
exact_approaches = formulation_approaches + benders_approaches

content['bst_objective'] = content.apply(lambda row: max(row['{}_objective'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_runtime'] = content.apply(lambda row: min(row['{}_runtime'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_optgap'] = content.apply(lambda row: min(row['{}_optgap'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_bound'] = content.apply(lambda row: min(row['{}_bound'.format(approach)] for approach in exact_approaches), axis = 1)
content['bst_optimal'] = content.apply(lambda row: (row['bst_optgap'] <= cm.TOLERANCE), axis = 1)

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
    content['{}_objective'.format(approach)].fillna(0)

content.to_csv('debugging.csv')

for approach in exact_approaches: # + heuristic_approaches:
    # content['{}_optgap'.format(approach)] = content.apply(lambda row: 1 if row['{}_optgap'.format(approach)] > 1 else row['{}_optgap'.format(approach)], axis = 1)
    content['{}_bstime'.format(approach)] = content.apply(lambda row: round(row['{}_runtime'.format(approach)] / (row['bst_runtime'] + cm.TOLERANCE), cm.PRECISION), axis = 1)
    # content['{}_bstgap'.format(approach)] = content.apply(lambda row: cm.compute_gap(row['bst_objective'], row['{}_objective'.format(approach)]), axis = 1)
    content['{}_bstgap'.format(approach)] = content.apply(lambda row: round(row['bst_objective'] / (row['{}_objective'.format(approach)] + cm.TOLERANCE), cm.PRECISION), axis = 1)

content.to_csv('debugging.csv')

characteristics = {
    'branch': ['paper1'],
    'locations': [50, 100, 150],
    'customers': [1, 3, 5],
    'periods': [5, 7, 9],
    #'periods': [5, 7, 10],
    'facilities': [1, 3, 5],
    'rewards': ['identical', 'inversely'],
    'preferences': ['small', 'large'],
    'demands': ['fixed', 'sparse'], # 'constant', 'seasonal'],
    #'characters': ['homogeneous','heterogeneous']
}

labels = {
    'branch': {
        'paper1': 'Benchmark',
    },
    'locations': {
        50: '50 locations',
        100: '100 locations',
        150: '150 locations',
    },
    'customers': {
        1: 'x1 customers',
        3: 'x3 customers',
        5: 'x5 customers',
    },
    'periods': {
        5: '5 periods',
        7: '7 periods',
        9: '9 periods',
        10: '10 periods',
    },
    'facilities': {
        1: '1 facility',
        3: '3 facilities',
        5: '5 facilities',
    },
    'rewards':{
        'identical': 'Identical rewards',
        'inversely': 'Different rewards'
    },
    'preferences': {
        'small': 'Small rankings',
        'large': 'Large rankings'
    },
    'demands': {
        'constant': 'Constant demand',
        'seasonal': 'Seasonal demand',
        'fixed': 'Constant demand',
        'sparse': 'Sparse demand'
    },
    #'characters': {
    #    'homogeneous': 'Identical amplitudes',
    #    'heterogeneous': 'Sampled amplitudes'
    #}
}

colors = {
    'cold_lrz' : 'magenta',
    'cold_net' : 'teal',
    'bbd': 'blue',
    'bbe' : 'orange',
    'rnd' : 'gray',
    'frw' : 'olive',
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

def graph_heuristics():

    methods = ['eml', 'rnd', 'frw', 'bcw']

    filter = (content['branch'] == 'paper1') & (content['bst_optimal'] == True)

    with open ('graphs/heuristics.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 0, 1.0, 0.01
        length_y, lower_y, upper_y, step_y = 10, 0, 100, 10

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,10.5);\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw (9.5,0.5) node[anchor=mid] {opportunity gap (\%)};\n')
        output.write('\draw (0,11) node[anchor=mid] {\# instances};\n')

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.1f}{};\n'.format(formatted_x, '{$', x * 10**2,'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y * len(content[filter]) / 100,'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 0
            prev_y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= x)]) / len(content[filter]))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(colors[method], styles[method], formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))

                prev_x = x
                prev_y = y

        output.write('\n')

        current_y = 3.0
        next_y = 0.5

        for method in methods:
            output.write('\draw[line width=0.5mm, {}, {}] (8.5, {:.2f})--(9.0, {:.2f});\n'.format(colors[method], styles[method], current_y, current_y))
            output.write('\draw[line width=0.5mm, {}] (9.0, {:.2f}) node[anchor=west] {}{}{};\n'.format(colors[method], current_y, '{', legend[method], '}'))
            current_y += next_y

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/heuristics.tex')

def graph_objectives():

    methods = ['eml', 'frw', 'bcw', 'bbd', 'cold_lrz', 'cold_net']
    methods = ['bbd', 'cold_lrz', 'cold_net']

    filter = (content['branch'] == 'paper1') # & (content['bst_optimal'] == True)

    with open ('graphs/objectives.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 1, 1.5, 0.05
        length_y, lower_y, upper_y, step_y = 5, 40, 100, 6

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.7, every node/.style={scale=.7}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}objective ratio{};\n'.format(length_x - 0.5, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}\# instances{};\n'.format(length_y + 1, '{', '}'))

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.2f}{};\n'.format(formatted_x, '{$', x,'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y * len(content[filter]) / 100,'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 1
            prev_y = int(100 * len(content[filter & (content['{}_bstgap'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                y = int(100 * len(content[filter & (content['{}_bstgap'.format(method)] <= x)]) / len(content[filter]))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(colors[method], styles[method], formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))

                prev_x = x
                prev_y = y

        output.write('\n')

        current_y = 1.0
        next_y = 0.5

        for method in methods:
            output.write('\draw[line width=0.5mm, {}, {}] (8.5, {:.2f})--(9.0, {:.2f});\n'.format(colors[method], styles[method], current_y, current_y))
            output.write('\draw[line width=0.5mm, {}] (9.0, {:.2f}) node[anchor=west] {}{}{};\n'.format(colors[method], current_y, '{', legend[method], '}'))
            current_y += next_y

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/objectives.tex')

def graph_runtimes():

    methods = ['eml', 'frw', 'bcw', 'bbd', 'cold_lrz', 'cold_net']
    methods = ['bbd', 'cold_lrz', 'cold_net']

    filter = (content['branch'] == 'paper1') # & (content['bst_optimal'] == True)

    with open ('graphs/runtimes.tex', 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 1, 10, 0.09
        length_y, lower_y, upper_y, step_y = 5, 40, 100, 6

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.7, every node/.style={scale=.7}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}runtime ratio{};\n'.format(length_x - 0.5, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}\# instances{};\n'.format(length_y + 1, '{', '}'))

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.1f}{};\n'.format(formatted_x, '{$', x,'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y * len(content[filter]) / 100,'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 1
            prev_y = int(100 * len(content[filter & (content['{}_bstime'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                y = int(100 * len(content[filter & (content['{}_bstime'.format(method)] <= x)]) / len(content[filter]))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(colors[method], styles[method], formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))

                prev_x = x
                prev_y = y

        output.write('\n')

        current_y = 1.0
        next_y = 0.5

        for method in methods:
            output.write('\draw[line width=0.5mm, {}, {}] (8.5, {:.2f})--(9.0, {:.2f});\n'.format(colors[method], styles[method], current_y, current_y))
            output.write('\draw[line width=0.5mm, {}] (9.0, {:.2f}) node[anchor=west] {}{}{};\n'.format(colors[method], current_y, '{', legend[method], '}'))
            current_y += next_y

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/runtimes.tex')

def graph_runtime(method1, method2, descriptor = 1):

    timelimit = 60

    methods = [method1, method2]
    if descriptor == 1:
        filter = (content['{}_optimal'.format(method1)] == 1) & (content['{}_optimal'.format(method2)] == 1)
    #elif descriptor == 2:
    #    filter = (
    #        (content['{}_optimal'.format(method1)] == 0) & (content['{}_optimal'.format(method2)] == 1)
    #    ) | (
    #        (content['{}_optimal'.format(method1)] == 1) & (content['{}_optimal'.format(method2)] == 0)
    #    )
    elif descriptor == 3:
        filter = (content['{}_optimal'.format(method1)] == 0) | (content['{}_optimal'.format(method2)] == 0)
    else:
        exit('Wrong descriptor for runtime graph, {} versus {}, type {}'.format(method1, method2, descriptor))

    if method1 == 'bbe' or method2 == 'bbe':
        filter = filter & (content['facilities'] == 1)

    print('Number of instances considered for this graph: {}'.format(len(content[filter])))

    with open ('graphs/runtime_{}_{}_{}.tex'.format(method1.replace('cold_', ''), method2.replace('cold_', ''), descriptor), 'w') as output:

        length_x, lower_x, upper_x, step_x = 10, 0, 1.0, 0.01
        # length_x, lower_x, upper_x, step_x = 10, 0, 0.4, 0.04
        length_y, lower_y, upper_y, step_y = 5, 0, 100, 10

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.7, every node/.style={scale=.7}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}runtime (min){};\n'.format(length_x - 0.5, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}\# instances{};\n'.format(length_y + 1, '{', '}'))

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_x, '{$', round(x * timelimit),'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', round(y * len(content[filter]) / 100),'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 0
            prev_y = int(100 * len(content[filter & (content['{}_runtime'.format(method)] / 3601 <= prev_x)]) / len(content[filter]))

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x
                y = int(100 * len(content[filter & (content['{}_runtime'.format(method)] / 3601 <= x)]) / len(content[filter]))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(colors[method], styles[method], formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))

                prev_x = x
                prev_y = y

        output.write('\n')

        current_y = 3.0
        next_y = 0.5

        for method in methods:
            output.write('\draw[line width=0.5mm, {}, {}] ({}, {:.2f})--({}, {:.2f});\n'.format(colors[method], styles[method], length_x - 1.5, current_y, length_x - 1.0, current_y))
            output.write('\draw[line width=0.5mm, {}] ({}, {:.2f}) node[anchor=west] {}{}{};\n'.format(colors[method], length_x - 1.0, current_y, '{', legend[method], '}'))
            current_y += next_y

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/runtime_{}_{}_{}.tex'.format(method1, method2, descriptor))

def graph_optgap(method1, method2, descriptor = 1):

    methods = [method1, method2]
    if descriptor == 1:
        filter = (content['{}_optimal'.format(method1)] == 1) & (content['{}_optimal'.format(method2)] == 1)
    #elif descriptor == 2:
    #    filter = (
    #        (content['{}_optimal'.format(method1)] == 0) & (content['{}_optimal'.format(method2)] == 1)
    #    ) | (
    #        (content['{}_optimal'.format(method1)] == 1) & (content['{}_optimal'.format(method2)] == 0)
    #    )
    elif descriptor == 3:
        filter = (content['{}_optimal'.format(method1)] == 0) | (content['{}_optimal'.format(method2)] == 0)
    else:
        exit('Wrong descriptor for optgap graph, {} versus {}, type {}'.format(method1, method2, descriptor))

    if method1 == 'bbe' or method2 == 'bbe':
        filter = filter & (content['facilities'] == 1)

    print('Number of instances considered for this graph: {}'.format(len(content[filter])))

    with open ('graphs/optgap_{}_{}_{}.tex'.format(method1.replace('cold_', ''), method2.replace('cold_', ''), descriptor), 'w') as output:

        # length_x, lower_x, upper_x, step_x = 10, 0, 0.2, 0.002
        length_x, lower_x, upper_x, step_x = 10, 0, 1.0, 0.001
        length_y, lower_y, upper_y, step_y = 5, 0, 100, 10

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.7, every node/.style={scale=.7}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},0.5) node[anchor=mid] {}optimality gap (\%){};\n'.format(length_x - 0.5, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}\# instances{};\n'.format(length_y + 1, '{', '}'))

        formatted_x = 0
        while formatted_x <= length_x:
            x = (formatted_x / length_x) * (upper_x - lower_x) + lower_x
            output.write('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_x, '{$', x * 10**2,'$}'))
            formatted_x += 1

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', round(y * len(content[filter]) / 100),'$}'))
            formatted_y += 1

        for method in methods:

            prev_x = 0
            prev_y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= prev_x)]) / len(content[filter]))

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x
                x = round(x, 3)
                y = int(100 * len(content[filter & (content['{}_optgap'.format(method)] <= x)]) / len(content[filter]))

                formatted_prev_x = length_x * (prev_x - lower_x) / (upper_x - lower_x)
                formatted_prev_y = length_y * (prev_y - lower_y) / (upper_y - lower_y)
                formatted_x = length_x * (x - lower_x) / (upper_x - lower_x)
                formatted_y = length_y * (y - lower_y) / (upper_y - lower_y)

                output.write('\draw[line width=0.5mm,line width=0.5mm,{},{}] ({:.2f},{:.2f})--({:.2f},{:.2f});'.format(colors[method], styles[method], formatted_prev_x, formatted_prev_y, formatted_x, formatted_y))

                prev_x = x
                prev_y = y

        output.write('\n')

        current_y = 3.0
        next_y = 0.5

        for method in methods:
            output.write('\draw[line width=0.5mm, {}, {}] ({}, {:.2f})--({}, {:.2f});\n'.format(colors[method], styles[method], length_x - 1.5, current_y, length_x - 1.0, current_y))
            output.write('\draw[line width=0.5mm, {}] ({}, {:.2f}) node[anchor=west] {}{}{};\n'.format(colors[method], length_x - 1.0, current_y, '{', legend[method], '}'))
            current_y += next_y

        output.write('\end{tikzpicture}\n')

        print('Exported graph to graphs/optgap_{}_{}_{}.tex'.format(method1, method2, descriptor))

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

    filter = (content['branch'] == 'paper1') & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True)

    content[filter].boxplot(['cold_net_runtime', 'bbd_runtime'])
    plt.savefig('results/paper1/box_table4_runtime.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_runtime', 'bbd_runtime']
                filter = (content[characteristic] == value) & (content['cold_net_optimal'] == True) & (content['bbd_optimal'] == True)
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


def table5(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & ((content['cold_net_optimal'] == False) | (content['bbd_optimal'] == False))

    content[filter].boxplot(['cold_net_optgap', 'bbd_optgap'])
    plt.savefig('results/paper1/box_table5_optgap.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['cold_net_optgap', 'bbd_optgap']
                filter = (content[characteristic] == value) & ((content['cold_net_optimal'] == False) | (content['bbd_optimal'] == False))
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
            format(labels[characteristic][value], count, total, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table6 {}'.format(descriptor))

    print('**************************************************************************************************')

def table7(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & (content['facilities'] == 1) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True)

    content[filter].boxplot(['bbd_runtime', 'bbe_runtime'])
    plt.savefig('results/paper1/box_table7_runtime.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['bbd_runtime', 'bbe_runtime']
                filter = (content[characteristic] == value) & (content['facilities'] == 1) & (content['bbd_optimal'] == True) & (content['bbe_optimal'] == True)
            else:
                exit('Wrong descriptor for table 7')

            averages = {}
            deviations = {}
            maximums = {}

            for column in columns:
                averages[column] = round(content[filter][column].mean() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                deviations[column] = round(content[filter][column].std() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)
                # maximums[column] = round(content[filter][column].max() * (100 if 'runtime' not in column else 1) * (1/60 if 'runtime' in column else 1), 2)

            # count = 100 * len(content[filter].index) / len(content[(content[characteristic] == value)].index)
            count = len(content[filter].index)
            total = len(content[(content[characteristic] == value) & (content['facilities'] == 1)].index)

            # print('{}&${:.2f}$&{}{}{}'.
            print('{}&${} \, ({})$&{}{}{}'.
            format(labels[characteristic][value], count, total, '&'.join(['${:.2f}\pm{:.2f}$'.format(averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table7 {}'.format(descriptor))

    print('**************************************************************************************************')


def table8(descriptor = 'paper'):

    filter = (content['branch'] == 'paper1') & (content['facilities'] == 1) & ((content['bbd_optimal'] == False) | (content['bbe_optimal'] == False))

    content[filter].boxplot(['bbd_optgap', 'bbe_optgap'])
    plt.savefig('results/paper1/box_table8_optgap.png')
    plt.figure().clear()

    for characteristic, values in characteristics.items():

        for value in values:

            if descriptor == 'paper':
                columns = ['bbd_optgap', 'bbe_optgap']
                filter = (content[characteristic] == value) & (content['facilities'] == 1) & ((content['bbd_optimal'] == False) | (content['bbe_optimal'] == False))
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
            total = len(content[(content[characteristic] == value) & (content['facilities'] == 1)].index)

            # print('{}&${:.2f}$&{}{}{}'.
            print('{}&${} \, ({})$&{}{}{}'.
            format(labels[characteristic][value], count, total, '&'.join(['${}$&${:.2f}\pm{:.2f}$'.format(optimals[column], averages[column], deviations[column]) for column in columns]), '\\', '\\'))

        print('\\midrule')

    _ = input('table8 {}'.format(descriptor))

    print('**************************************************************************************************')

'''
table1()
table2()
table4()
table5()
table3()
table7()
table8()
'''

def table_overview():

    locations = [50, 100, 150]
    customers = [1, 3, 5]
    periods = [5, 7, 9]
    facilities = [1, 3, 5]

    methods = ['cold_lrz', 'cold_net', 'bbd']

    for location in locations:
        for customer in customers:
            for period in periods:
                #    for facility in facilities:

                line = 'I={},J={},T={},'.format(location, customer, period) #, T = {}, H = {}, '.format(location, customer, period, facility)
                filter1 = (content['branch'] == 'paper1') & (content['locations'] == location) & (content['customers'] == customer) & (content['periods'] == period)

                for method in methods:

                    filter2 = filter1 & (content['{}_optimal'.format(method)] == True)

                    line += '{},'.format(round(100 * len(content[filter2]) / len(content[filter1])))

                print(line)

    _ = input('overview')

    print('**************************************************************************************************')

table_overview()

graph_heuristics()
graph_objectives()
graph_runtimes()

graph_runtime('cold_lrz', 'cold_net', 1)
# graph_runtime('cold_lrz', 'cold_net', 3)
# graph_optgap('cold_lrz', 'cold_net', 1)
graph_optgap('cold_lrz', 'cold_net', 3)

graph_runtime('cold_net', 'bbd', 1)
# graph_runtime('cold_net', 'bbd', 3)
# graph_optgap('cold_net', 'bbd', 1)
graph_optgap('cold_net', 'bbd', 3)

graph_runtime('bbd', 'bbe', 1)
# graph_runtime('bbd', 'bbe', 3)
# graph_optgap('bbd', 'bbe', 1)
graph_optgap('bbd', 'bbe', 3)

print('Filtered total: {}'.format(len(content)))