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
    return increasing(t)
    # return sine(t)

color = 'blue'
shape = '*'

print('> Spawning demand graph:')

scale = 2

print('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]')
print('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);'.format(10 + 0.5))
print('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});'.format(5 + 1))

print('\draw ({},0.5) node[anchor=mid] {}$t${};'.format(10, '{', '}'))
print('\draw (0,{}) node[anchor=mid] {}$d^t_j${};'.format(5 + 1.5, '{', '}'))

x = 0
while x <= 10:
    formatted_x = x
    print('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};'.format(x, '{$', formatted_x,'$}'))
    x += 1

y = 0
while y <= 5:
    formatted_y = y * scale
    print('\draw (-0.5, {}) node[anchor=mid] {}{:.0f}{};'.format(y, '{$', formatted_y,'$}'))
    y += 1

stored_f[0] = f(0)
x = 1.0
step = 1.0

while round(x) <= 10:

    x2 = round(x, 2)
    stored_f[x2] = f(x2)
    f2 = stored_f[x2]

    print('\draw[{}] ({},{}) node[anchor=mid] {}{}{};'.format(color, x2, round(f2 / scale, 2), '{', shape, '}'))

    x += step

print('\end{tikzpicture}')

_ = input('wait...')

print('> Accumulated demand graph:')

scale = 10

print('\\begin{tikzpicture}[scale=.8, every node/.style={scale=.8}]')
print('\draw[line width=0.5mm,thick,->] (0,0) -- ({},0);'.format(10 + 0.5))
print('\draw[line width=0.5mm,thick,->] (0,0) -- (0,{});'.format(5 + 1))

print('\draw ({},0.5) node[anchor=mid] {}$t${};'.format(10, '{', '}'))
print('\draw (0,{}) node[anchor=mid] {}$c^t_j(\\boldsymbol{}0{})${};'.format(5 + 1.5, '{', '{', '}', '}'))

x = 0
while x <= 10:
    formatted_x = x
    print('\draw ({},-0.5) node[anchor=mid] {}{:.0f}{};'.format(x, '{$', formatted_x,'$}'))
    x += 1

y = 0
while y <= 5:
    formatted_y = y * scale
    print('\draw (-0.5, {}) node[anchor=mid] {}{:.0f}{};'.format(y, '{$', formatted_y,'$}'))
    y += 1

accumulated_f[0] = 0
x = 1.0
step = 1.0

while round(x) <= 10:

    x1 = round(max(x - step, 0), 2)
    x2 = round(x, 2)

    f1 = accumulated_f[x1]
    accumulated_f[x2] = f1 + f(x2)
    f2 = accumulated_f[x2]

    print('\draw[{}] ({},{}) node[anchor=mid] {}{}{};'.format(color, x2, round(f2 / scale, 2), '{', shape, '}'))

    x += step

print('\end{tikzpicture}')