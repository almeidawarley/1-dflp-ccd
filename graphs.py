import math as mt

shape = 'circle (2pt)'

stored_f = {}
accumulated_f = {}

def sine(t, a = 5):

    return a * mt.sin(t) + a

def increasing(t, a = 1, b = 0.0):

    return t * a + b

def decreasing(t, a = 1, b = 10):

    return b - t * a

def constant(t, a = 5):

    return a

'''
def f(t):

    # return bass(t)
    # return constant(t)
    # return decreasing(t)
    # return increasing(t)
    return sine(t)
'''

colors = ['teal', 'blue', 'red',  'orange']
styles = ['dotted', 'dashdotted', 'dashed', 'solid', ]
functions = [constant, increasing, decreasing, sine]

for (color, style, f) in zip(colors, styles, functions):

    # color = 'orange'
    # style = 'dotted'
    step = 1.0
    step = 0.1

    # print('> Spawning demand graph:')

    stored_f[0] = f(0)
    scale = 2
    x = 1.0
    x = 0.1

    while round(x) < 10:

        x1 = round(max(x - step, 0), 2)
        x2 = round(x, 2)

        f1 = stored_f[x1]
        stored_f[x2] = f(x2)
        f2 = stored_f[x2]

        with open('graphs/spawning.txt', 'a') as output:
            # print('\draw[{}, {}] ({},{})--({},{});'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2)))
            output.write('\draw[{}, {}] ({},{})--({},{});\n'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2)))

            if x2 in [0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.]:
                # print('\draw[{}] ({},{}) node[anchor=mid] {}{}{};'.format(color, x2, round(f2 / scale, 2), '{', shape, '}'))
                output.write('\draw[{},fill={}] ({},{}) {};\n'.format(color, color, x2, round(f2 / scale, 2), shape))

        x += step

    print('spawning: {}, {}, {}'.format(color, style, f))

    # print('> Accumulated demand graph:')
    accumulated_f[0] = 0
    scale = 10
    x = 1.0
    step = 1.0

    while round(x) < 10:

        x1 = round(max(x - step, 0), 2)
        x2 = round(x, 2)

        f1 = accumulated_f[x1]
        accumulated_f[x2] = f1 + f(x2)
        f2 = accumulated_f[x2]

        with open('graphs/accumulated.txt', 'a') as output:

            # print('\draw[{}, {}] ({},{})--({},{});'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2)))
            output.write('\draw[{}, {}] ({},{})--({},{});\n'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2)))

            if x2 in [0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.]:

                # print('\draw[{}] ({},{}) node[anchor=mid] {}{}{};'.format(color, x2, round(f2 / scale, 2), '{', shape, '}'))
                output.write('\draw[{},fill={}] ({},{}) {};\n'.format(color, color, x2, round(f2 / scale, 2), shape))

        x += step

    print('accumulated: {}, {}, {}'.format(color, style, f))