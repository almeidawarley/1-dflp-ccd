import pandas as pd
import common as cm

subset = 'identical-large-sparse'

content = pd.read_csv('results/paper1/{}.csv'.format(subset), encoding = 'utf-16')
content['index'] = content['keyword']
content = content.set_index('index')

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

            instance = cm.load_instance('bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, prev_x))
            solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, prev_x)].iloc[0]['cold_net_solution']
            reward, penalty = instance.evaluate_solution2(instance.unpack_solution(solution))

            # r_reward = reward
            # r_penalty = penalty

            prev_y1 = reward
            prev_y2 = penalty

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                instance = cm.load_instance('bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, x))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, x)].iloc[0]['cold_net_solution']
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

            instance = cm.load_instance('bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, prev_x))
            solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, prev_x)].iloc[0]['cold_net_solution']
            reward, penalty = instance.evaluate_solution2(instance.unpack_solution(solution))

            # r_reward = reward
            # r_penalty = penalty

            prev_y1 = reward
            prev_y2 = penalty

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                instance = cm.load_instance('bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, x))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, x)].iloc[0]['cold_net_solution']
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

            prev_y = 0

            x = lower_x

            while abs(x - upper_x) > 10**(-3):

                x += step_x

                instance = cm.load_instance('bmk_1-50-1-5-{}-{}-0'.format(facility, subset))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-{}-0'.format(facility, subset)].iloc[0]['cold_net_solution']
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

def graph_histogram(penalty):

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

                instance = cm.load_instance('bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, penalty))
                solution = content[content['keyword'] == 'bmk_1-50-1-5-{}-{}-{}'.format(facility, subset, penalty)].iloc[0]['cold_net_solution']

                for customer in instance.customers:
                    capture = instance.evaluate_customer2(instance.unpack_solution(solution), customer)
                    if capture == period:
                        captures[period][facility] += 1

        length_x, lower_x, upper_x, step_x = 25, 0, 25, 1
        length_y, lower_y, upper_y, step_y = 5, 0, 40, 4

        # output.write('\\begin{figure}[!ht]\n\centering\n')
        output.write('\\begin{tikzpicture}[scale=.5, every node/.style={scale=.5}]\n')
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);\n'.format(length_x + 0.5))
        output.write('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});\n'.format(length_y + 0.5))

        # output.write('\draw (-0.5,-0.5) node[anchor=mid] {$0$};\n')
        output.write('\draw ({},1) node[anchor=mid] {}number of captures{};\n'.format(length_x - 1, '{', '}'))
        output.write('\draw (0,{}) node[anchor=mid] {}number of customers{};\n'.format(length_y + 1, '{', '}'))

        output.write('\draw[line width=0.5mm, green, solid] (19.5, 5)--(20.0, 5);')
        output.write('\draw[line width=0.5mm, green] (20.0, 5) node[anchor=west] {1 facility};')
        output.write('\draw[line width=0.5mm, red, solid] (19.5, 4.5)--(20.0, 4.5);')
        output.write('\draw[line width=0.5mm, red] (20.0, 4.5) node[anchor=west] {3 facilities};')
        output.write('\draw[line width=0.5mm, blue, solid] (19.5, 4)--(20.0, 4);')
        output.write('\draw[line width=0.5mm, blue] (20.0, 4) node[anchor=west] {5 facilities};')

        formatted_y = 0
        while formatted_y <= length_y:
            y = (formatted_y / length_y) * (upper_y - lower_y) + lower_y
            output.write('\draw (-0.5,{}) node[anchor=mid] {}{:.0f}{};\n'.format(formatted_y, '{$', y,'$}'))
            formatted_y += 1

        output.write('\draw (2,-0.5) node[anchor=mid] {$0$};')
        output.write('\draw (6,-0.5) node[anchor=mid] {$1$};')
        output.write('\draw (10,-0.5) node[anchor=mid] {$2$};')
        output.write('\draw (14,-0.5) node[anchor=mid] {$3$};')
        output.write('\draw (18,-0.5) node[anchor=mid] {$4$};')
        output.write('\draw (22,-0.5) node[anchor=mid] {$5$};')

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

graph_histogram(0)
_ = input('wait..')
graph_histogram(50)