import math as mt

stored_f = {}
accumulated_f = {}
scale_up = 1
scale_down = 10

def bass(t, p = 0.04, q = 0.4, m = 40):

    return (p * m + (q - p) * sum(v for x, v in stored_f.items() if x <= t) - (q/m) * (sum(v for x, v in stored_f.items() if x <= t)) ** 2)

def cosine(t, a = 0.5):

    return a * mt.cos(t) + a

def increasing(t, a = 0.1, b = 0.0):

    return t * a + b

def decreasing(t, a = 0.1, b = 1.0):

    return b - t * a

def constant(t, a = 0.5):

    return a

def f(t):

    return bass(t)
    # return decreasing(t)
    # return increasing(t)
    # return cosine(t)
    # return constant(t)

color = 'cyan'

print('> Spawning demand graph:')
x = 1.0
step = 1.0
stored_f[0] = f(0)

while round(x) <= 10:

    x1 = round(max(x - step, 0), 2)
    x2 = round(x, 2)

    f1 = stored_f[x1]
    stored_f[x2] = f(x2)
    f2 = stored_f[x2]

    if x2 in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]:
        print('\draw[dashed, {}] ({},{})--({},{}) node[anchor=mid] {}x{};'.format(color, x1, round(f1 * scale_up, 2), x2, round(f2 * scale_up, 2), '{', '}'))
    else:
        print('\draw[dashed, {}] ({},{})--({},{});'.format(color, x1, round(f1 * scale_up, 2), x2, round(f2 * scale_up, 2)))

    x += step


print('> Accumulated demand graph:')
x = 1.0
step = 1.0
accumulated_f[0] = 0
while round(x) <= 10:

    x1 = round(max(x - step, 0), 2)
    x2 = round(x, 2)

    f1 = accumulated_f[x1]
    accumulated_f[x2] = f1 + stored_f[x2]
    f2 = accumulated_f[x2]

    if x2 in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]:
        print('\draw[dashed, {}] ({},{})--({},{}) node[anchor=mid] {}x{};'.format(color, x1, round(f1 * scale_up/scale_down, 2), x2, round(f2 * scale_up/scale_down, 2), '{', '}'))
    else:
        print('\draw[dashed, {}] ({},{})--({},{});'.format(color, x1, round(f1 * scale_up/scale_down, 2), x2, round(f2 * scale_up/scale_down, 2)))

    x += step
