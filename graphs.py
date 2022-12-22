import instance as ic
import formulation as fm

instance = ic.instance('graph')
instance.print_instance()

capture_all = {
        '1': '1',
        '2': '1',
        '3': '1',
        '4': '1',
        '5': '1',
        '6': '1',
        '7': '1',
        '8': '1',
        '9': '1',
        '10': '0',
        '11': '0',
        '12': '0',
        '13': '0',
        '14': '0',
        '15': '0',
        '16': '0',
        '17': '0',
        '18': '0'
    }

capture_none = {
    '1': '0',
    '2': '0',
    '3': '0',
    '4': '0',
    '5': '0',
    '6': '0',
    '7': '0',
    '8': '0',
    '9': '0',
    '10': '0',
    '11': '0',
    '12': '0',
    '13': '0',
    '14': '0',
    '15': '0',
    '16': '0',
    '17': '0',
    '18': '0'
}

counter = 0

# red, green, blue, cyan, magenta, yellow, black, gray, darkgray, lightgray, brown, lime, olive, orange, pink, purple, teal, violet and white. 

color = {
    1: 'red!100',
    2: 'green!100',
    3: 'blue!100',
    4: 'cyan!100',
    5: 'magenta!100',
    6: 'yellow!100',
    7: 'gray!100',
    8: 'brown!100',
    9: 'orange!100',
    10: 'purple!100',
    11: 'teal!100',
    12: 'violet!100',
    13: 'lime!100',
    14: 'olive!100',
    15: 'pink!100',
    16: 'red!50',
    17: 'green!50',
    18: 'blue!50',
    19: 'cyan!50',
    20: 'magenta!50',
    21: 'yellow!50',
    22: 'gray!50',
    23: 'brown!50',
    24: 'orange!50',
    25: 'purple!50',
    26: 'teal!50',
    27: 'violet!50',
    28: 'lime!50',
    29: 'olive!50',
    30: 'pink!50'
}

colorg = {
    0.1: 'red!100',
    0.15: 'pink!100',
    0.2: 'green!100',
    0.3: 'blue!100',
    0.4: 'cyan!100',
    0.5: 'magenta!100',
    0.6: 'yellow!100',
    0.7: 'gray!100',
    0.8: 'brown!100',
    0.9: 'orange!100'
}

colord = {
    1: 'red!100',
    1.1: 'pink!100',
    1.2: 'brown!100',
    2: 'green!100',
    3: 'blue!100',
    4: 'cyan!100',
    5: 'magenta!100',
    6: 'yellow!100',
    7: 'gray!100',
    8: 'brown!100',
    9: 'orange!100'
}

valids = []

# for alpha in [0.2]:
for beta in [1]:
    # for delta in [1,2,3,4,5]:
    for gamma in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:

        # if alpha  - gamma - alpha * gamma < 0:
        # if beta < delta:
        # if (1 + alpha) * delta / alpha > 10:
        if beta / gamma < 10:

            counter += 1

            for customer in instance.customers:
                instance.alphas[customer] = 0
                instance.betas[customer] = beta
                instance.gammas[customer] = gamma
                instance.deltas[customer] = 0
                instance.starts[customer] = 10
                instance.lowers[customer] = 1
                instance.uppers[customer] = 10

            mip, variable = fm.build_fancy(instance)
            fm.fix_solution(mip, variable, capture_all)
            mip.optimize()
            fm.write_scatter(instance, variable, colorg[gamma])
            # fm.write_scatter(instance, variable, colord[delta])

            # valids.append((alpha, gamma))
            # valids.append((beta, delta))
            # valids.append((alpha, delta))
            valids.append((beta, gamma))

        else:
            pass
            # print('alpha: {}, gamma: {} is not valid'.format(alpha, gamma))
            # _ = input('wait...')


for i in range(0, counter):

    # print('\draw[color={}] (12.5,{}) -- (13,{}) node[anchor=west] {}$\\alpha_j = {}, \\gamma_j = {}${};'.format(colorg[valids[i][1]], 9.0 - 0.5 * i, 9.0 - 0.5 * i, '{', valids[i][0], valids[i][1], '}'))
    # print('\draw[color={}] (12.5,{}) -- (13,{}) node[anchor=west] {}$\\beta_j = {}, \\delta_j = {}${};'.format(colord[valids[i][1]], 9.0 - 0.5 * i, 9.0 - 0.5 * i, '{', valids[i][0], valids[i][1], '}'))
    # print('\draw[color={}] (12.5,{}) -- (13,{}) node[anchor=west] {}$\\alpha_j = {}, \\delta_j = {}${};'.format(colord[valids[i][1]], 9.0 - 0.5 * i, 9.0 - 0.5 * i, '{', valids[i][0], valids[i][1], '}'))
    print('\draw[color={}] (12.5,{}) -- (13,{}) node[anchor=west] {}$\\beta_j = {}, \\gamma_j = {}${};'.format(colorg[valids[i][1]], 9.0 - 0.5 * i, 9.0 - 0.5 * i, '{', valids[i][0], valids[i][1], '}'))