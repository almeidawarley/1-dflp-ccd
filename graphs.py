import math as mt

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

def f(t):

    # return bass(t)
    # return constant(t)
    # return decreasing(t)
    # return increasing(t)
    return sine(t)

color = 'orange'
style = 'dotted'
step = 1.0
step = 0.1

print('> Spawning demand graph:')

stored_f[0] = f(0)
scale = 2
x = 1.0
x = 0.1

while round(x) <= 10:

    x1 = round(max(x - step, 0), 2)
    x2 = round(x, 2)

    f1 = stored_f[x1]
    stored_f[x2] = f(x2)
    f2 = stored_f[x2]

    if x2 in [6.0]: # [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]:
        print('\draw[{}, {}] ({},{})--({},{}) node[anchor=mid] {}x{};'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2), '{', '}'))
    else:
        print('\draw[{}, {}] ({},{})--({},{});'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2)))

    x += step


print('> Accumulated demand graph:')
accumulated_f[0] = 0
scale = 10
x = 1.0
step = 1.0

while round(x) <= 10:

    x1 = round(max(x - step, 0), 2)
    x2 = round(x, 2)

    f1 = accumulated_f[x1]
    accumulated_f[x2] = f1 + f(x2)
    f2 = accumulated_f[x2]

    if x2 in [6.0]: # [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]:
        print('\draw[{}, {}] ({},{})--({},{}) node[anchor=mid] {}x{};'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2), '{', '}'))
    else:
        print('\draw[{}, {}] ({},{})--({},{});'.format(style, color, x1, round(f1 / scale, 2), x2, round(f2 / scale, 2)))

    x += step
