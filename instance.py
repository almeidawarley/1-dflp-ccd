import matplotlib.pyplot as pt
import random as rd
import math as mt
import json as js
import pandas as pd

class instance:

    def __init__(self, keyword, argument = 0):
        # Initiate instance class

        # Store instance keyword
        instance.keyword = keyword

        # Decide instance type
        if keyword == 'example':
            # Create example instance
            self.create_example()
        elif keyword == 'graph':
            self.create_graph()
            # Create graph instance
        elif keyword == 'spp':
            # Create SPP instance
            self.create_spp()
        elif keyword == 'gap1':
            # Create GAP1 instance
            self.create_gap1()
        elif keyword == 'gap2':
            # Create GAP2 instance
            self.create_gap2()
        elif keyword == '3sat':
            # Create 3SAT instance
            self.create_3sat(argument)
        elif keyword == 'rnd1':
            # Create RND1 instance
            self.create_rnd1()
        elif keyword == 'rnd2':
            # Create RND2 instance
            self.create_rnd2(argument)
        elif keyword == 'slovakia':
            # Create slovakia instance
            self.create_slovakia()
        else:
            # Create random instance
            if 'A-' in keyword:
                self.create_setA()
            elif 'B-' in keyword:
                self.create_setB()
            elif 'C-' in keyword:
                self.create_setC()
            elif 'D-' in keyword:
                self.create_setD()
            elif 'E-' in keyword:
                self.create_setE()
            else:
                exit('Invalid instance keyword')

        # Fix created instance
        self.fix_instance()

        # Print stored instance
        # self.print_instance()

        # Set proper big M values
        self.bigM = {}
        for customer in self.customers:
            self.bigM[customer] = self.uppers[customer] + self.alphas[customer] * self.uppers[customer] + self.betas[customer] + self.gammas[customer] * self.uppers[customer] + self.deltas[customer]

    def create_setA(self, folder = 'instances'):
        # Create instance set A

        # Read specifications from file
        try:
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(self.parameters['O'] * 10 + self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location == customer else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 1 # 10

        # Absorption varieties
        # Gamma values
        G = {
            'rel': [0.1, 0.2, 0.3],
            'abs': [0.2, 0.4, 0.6]
        }
        # Delta values
        D = {
            'rel': [1.0, 1.5, 2.0],
            'abs': [2.0, 3.0, 4.0]
        }

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}

        for customer in self.customers:
            # Upper, lower and initial demand
            self.lowers[customer] = 0 # actually 1 in previous experiments
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.uppers[customer] = self.parameters['U']

        for customer in self.customers:

            # Demand replenishment assignments
            if self.parameters['R'] == 'rel':
                self.alphas[customer] = 0.1
                self.betas[customer] = 0.0
            elif self.parameters['R'] == 'abs':
                self.alphas[customer] = 0.0
                self.betas[customer] = 1.0
            else:
                exit('Wrong replenishment parameter')

            # Demand absorption assignments
            if self.parameters['A'] == 'rel':
                self.deltas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.gammas[customer] = G[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.gammas[customer] = G[self.parameters['R']][0] + scale * (G[self.parameters['R']][2] - G[self.parameters['R']][0])
                    self.gammas[customer] = round(self.gammas[customer], 2)
                else:
                    exit('Wrong (relative) customer parameter')
            elif self.parameters['A'] == 'abs':
                self.gammas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.deltas[customer] = D[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.deltas[customer] = D[self.parameters['R']][0] + scale * (D[self.parameters['R']][2] - D[self.parameters['R']][0])
                    self.deltas[customer] = round(self.deltas[customer], 2)
                else:
                    exit('Wrong (absorption) customer parameter')
            else:
                exit('Wrong absorption parameter')

    def create_setB(self, folder = 'instances'):
        # Create instance set B

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(self.parameters['O'] * 10 + self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create map points
        self.points = {}
        for location in self.locations:
            self.points['i{}'.format(location)] = [rd.randint(-10, 10), rd.randint(-10, 10)]
        for customer in self.customers:
            self.points['j{}'.format(customer)] = [rd.randint(-10, 10), rd.randint(-10, 10)]
        X = [self.points['i{}'.format(location)][0] for location in self.locations]
        Y = [self.points['i{}'.format(location)][1] for location in self.locations]
        pt.scatter(X, Y, marker = 'o')
        for location in self.locations:
            pt.annotate(location, (X[int(location) - 1], Y[int(location) - 1]))
        X = [self.points['j{}'.format(customer)][0] for customer in self.customers]
        Y = [self.points['j{}'.format(customer)][1] for customer in self.customers]
        pt.scatter(X, Y, marker = 'x')
        for customer in self.customers:
            pt.annotate(customer, (X[int(customer) - 1], Y[int(customer) - 1]))
        pt.savefig('archives/map-{}.png'.format(self.keyword))

        '''
        self.threshold = {}
        radius_index = mt.floor((self.parameters['theta'] / 100) * number_locations) - 1
        for customer in self.customers:
            distances = []
            for location in self.locations:
                distances.append(mt.dist(self.points['i{}'.format(location)], self.points['j{}'.format(customer)]))
            distances.sort()
            self.threshold[customer] = distances[radius_index]
        '''

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if mt.dist(self.points['i{}'.format(location)], self.points['j{}'.format(customer)]) <= self.parameters['B'] else 0.

        '''
        avg_patronizable = 0
        for customer in self.customers:
            patronizable = sum([self.catalogs[location][customer] for location in self.locations])
            print('Customer: {} -> {}'.format(customer, patronizable))
            avg_patronizable += patronizable
        print(avg_patronizable/len(self.customers))
        '''

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 10

        # Absorption varieties
        # Gamma values
        G = {
            'rel': [0.1, 0.2, 0.3],
            'abs': [0.2, 0.4, 0.6]
        }
        # Delta values
        D = {
            'rel': [1.0, 1.5, 2.0],
            'abs': [2.0, 3.0, 4.0]
        }

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}

        for customer in self.customers:
            # Upper, lower and initial demand
            self.lowers[customer] = 1
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.uppers[customer] = self.parameters['U']

        for customer in self.customers:

            # Demand replenishment assignments
            if self.parameters['R'] == 'rel':
                self.alphas[customer] = 0.1
                self.betas[customer] = 0.0
            elif self.parameters['R'] == 'abs':
                self.alphas[customer] = 0.0
                self.betas[customer] = 1.0
            else:
                exit('Wrong replenishment parameter')

            # Demand absorption assignments
            if self.parameters['A'] == 'rel':
                self.deltas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.gammas[customer] = G[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.gammas[customer] = G[self.parameters['R']][0] + scale * (G[self.parameters['R']][2] - G[self.parameters['R']][0])
                    self.gammas[customer] = round(self.gammas[customer], 2)
                else:
                    exit('Wrong (relative) customer parameter')
            elif self.parameters['A'] == 'abs':
                self.gammas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.deltas[customer] = D[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.deltas[customer] = D[self.parameters['R']][0] + scale * (D[self.parameters['R']][2] - D[self.parameters['R']][0])
                    self.deltas[customer] = round(self.deltas[customer], 2)
                else:
                    exit('Wrong (absorption) customer parameter')
            else:
                exit('Wrong absorption parameter')

    def create_setC(self, folder = 'instances'):
        # Create instance set C

        # Read specifications from file
        try:
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(self.parameters['O'] * 10 + self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location == customer else rd.sample([0.,1.], 1)[0]

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 1 # 10

        # Absorption varieties
        # Gamma values
        G = {
            'rel': [0.1, 0.2, 0.3],
            'abs': [0.2, 0.4, 0.6]
        }
        # Delta values
        D = {
            'rel': [1.0, 1.5, 2.0],
            'abs': [2.0, 3.0, 4.0]
        }

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}

        for customer in self.customers:
            # Upper, lower and initial demand
            self.lowers[customer] = 1
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.uppers[customer] = self.parameters['U']

        for customer in self.customers:

            # Demand replenishment assignments
            if self.parameters['R'] == 'rel':
                self.alphas[customer] = 0.1
                self.betas[customer] = 0.0
            elif self.parameters['R'] == 'abs':
                self.alphas[customer] = 0.0
                self.betas[customer] = 1.0
            else:
                exit('Wrong replenishment parameter')

            # Demand absorption assignments
            if self.parameters['A'] == 'rel':
                self.deltas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.gammas[customer] = G[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.gammas[customer] = G[self.parameters['R']][0] + scale * (G[self.parameters['R']][2] - G[self.parameters['R']][0])
                    self.gammas[customer] = round(self.gammas[customer], 2)
                else:
                    exit('Wrong (relative) customer parameter')
            elif self.parameters['A'] == 'abs':
                self.gammas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.deltas[customer] = D[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.deltas[customer] = D[self.parameters['R']][0] + scale * (D[self.parameters['R']][2] - D[self.parameters['R']][0])
                    self.deltas[customer] = round(self.deltas[customer], 2)
                else:
                    exit('Wrong (absorption) customer parameter')
            else:
                exit('Wrong absorption parameter')

    def create_setD(self, folder = 'instances'):
        # Create instance set D

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(self.parameters['O'] * 10 + self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = rd.sample([0.,1.], 1)[0]

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 10

        # Absorption varieties
        # Gamma values
        G = {
            'rel': [0.1, 0.2, 0.3],
            'abs': [0.2, 0.4, 0.6]
        }
        # Delta values
        D = {
            'rel': [1.0, 1.5, 2.0],
            'abs': [2.0, 3.0, 4.0]
        }

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}

        for customer in self.customers:
            # Upper, lower and initial demand
            self.lowers[customer] = 1
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.uppers[customer] = self.parameters['U']

        for customer in self.customers:

            # Demand replenishment assignments
            if self.parameters['R'] == 'rel':
                self.alphas[customer] = 0.1
                self.betas[customer] = 0.0
            elif self.parameters['R'] == 'abs':
                self.alphas[customer] = 0.0
                self.betas[customer] = 1.0
            else:
                exit('Wrong replenishment parameter')

            # Demand absorption assignments
            if self.parameters['A'] == 'rel':
                self.deltas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.gammas[customer] = G[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.gammas[customer] = G[self.parameters['R']][0] + scale * (G[self.parameters['R']][2] - G[self.parameters['R']][0])
                    self.gammas[customer] = round(self.gammas[customer], 2)
                else:
                    exit('Wrong (relative) customer parameter')
            elif self.parameters['A'] == 'abs':
                self.gammas[customer] = 0.0
                if self.parameters['C'] == 'hom':
                    self.deltas[customer] = D[self.parameters['R']][self.parameters['O']]
                elif self.parameters['C'] == 'het':
                    scale = rd.sample([i for i in range(0,100)], 1)[0] / 100.
                    self.deltas[customer] = D[self.parameters['R']][0] + scale * (D[self.parameters['R']][2] - D[self.parameters['R']][0])
                    self.deltas[customer] = round(self.deltas[customer], 2)
                else:
                    exit('Wrong (absorption) customer parameter')
            else:
                exit('Wrong absorption parameter')

    # Difficult E-toy: {"S": 9, "L": 3, "T": 10, "H": 75, "O": 0}
    def create_setE(self, folder = 'instances'):
        # Create instance set E

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(self.parameters['O'] * 10 + self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['L'] ** 2)
        number_customers = int(self.parameters['L'] ** 2)
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create map points
        mapping = pt.cm.get_cmap('hsv', self.parameters['L'] ** 2)
        self.points = {}
        self.threshold = {}
        for y in range(0, self.parameters['L']):
            for x in range(0, self.parameters['L']):
                identifier = y * self.parameters['L'] + x + 1
                self.points['{}'.format(identifier)] = [x, y]
                self.threshold['{}'.format(identifier)] = rd.randint(0, int(self.parameters['L'] * self.parameters['H'] / 100))

                circle = pt.Circle((x, y), radius = self.threshold['{}'.format(identifier)], color = mapping(identifier), linestyle = '--', fill = False)
                pt.gcf().gca().add_patch(circle)
                pt.scatter([x], [y], color = mapping(identifier), marker = '.')
                pt.annotate('#{}'.format(identifier), (x, y))
        pt.axis('off')
        pt.axis('equal')
        pt.savefig('archives/map-{}.png'.format(self.keyword), dpi = 1000)

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if mt.dist(self.points['{}'.format(location)], self.points['{}'.format(customer)]) <= self.threshold[customer] else 0.

        '''
        avg_patronizable = 0
        for customer in self.customers:
            patronizable = int(sum([self.catalogs[location][customer] for location in self.locations]))
            print('Customer: {} -> {}'.format(customer, patronizable))
            avg_patronizable += patronizable
        print(avg_patronizable/len(self.customers))
        '''

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}

        for customer in self.customers:

            if self.parameters['O'] == 0:
                # Upper, lower and initial demand
                self.lowers[customer] = 0
                self.starts[customer] = 0
                self.uppers[customer] = self.parameters['T'] + 1. # infinity
                # Alphas, betas, gammas and deltas
                self.alphas[customer] = 0.
                self.betas[customer] = 1.
                self.gammas[customer] = 0.
                self.deltas[customer] = 10.

            else:
                exit('Wrong parameter for customer parameters')

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                if period == '1':
                    self.revenues[period][location] = round(100 * 1 / sum([self.catalogs[location][customer] for customer in self.customers]))
                else:
                    self.revenues[period][location] = self.revenues['1'][location]

    def create_spp(self, K = 2):
        # Create SPP instances

        elements = ['1', '2', '3', '4', '5']
        collections = [['1', '2', '3', '4', '5'], ['1'], ['2'], ['3'], ['4', '5']]

        self.locations = [str(i + 1) for i in range(0, len(collections))]
        self.customers = [e for e in elements]
        self.periods = [str(i + 1) for i in range(0, K)]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if customer in collections[int(location)-1] else 0.

        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1/len(collections[int(location)-1])
                if location == '1':
                    # Avoid ambiguity for heuristic
                    self.revenues[period][location] = 0.21

        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.uppers = {}
        self.lowers = {}
        for customer in self.customers:
            self.alphas[customer] = 0.5
            self.betas[customer] = 0
            self.gammas[customer] = 0.5
            self.deltas[customer] = 0
            self.starts[customer] = 1
            self.lowers[customer] = 0
            self.uppers[customer] = 10

        self.parameters = {}

    def create_3sat(self, argument = 'toy.cnf'):
        # Create 3SAT instances

        self.keyword = self.keyword + argument

        # with open('3sat/uf20-01.cnf', 'r') as content:
        # with open('3sat/uuf50-01.cnf', 'r') as content:
        # with open('3sat/toy.cnf', 'r') as content:
        with open('3sat/{}'.format(argument), 'r') as content:
            clauses = []
            for line in content:
                if 'p' in line:
                    line = line.strip().split(' ')
                    variables = [str(i + 1) for i in range(0, int(line[2]))]
                elif 'c' not in line:
                    line = line.strip().split(' ')
                    if len(line) == 4:
                        clauses.append([line[0], line[1], line[2]])
                    else:
                        print('Skipped: {}'.format(line))
                else:
                    print('Skipped: {}'.format(line))

        self.locations = [variable for variable in variables] + ['-' + variable for variable in variables]
        self.customers = ['c{}'.format(index + 1) for index, _ in enumerate(clauses)] + ['v{}'.format(variable) for variable in variables]
        self.periods = [variable for variable in variables]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for index, customer in enumerate(self.customers):
                if 'c' in customer:
                    self.catalogs[location][customer] = 1. if location in clauses[int(customer.replace('c', '')) - 1] else 0.
                elif 'v' in customer:
                    self.catalogs[location][customer] = 1. if int(customer.replace('v', '')) == int(location.replace('-','')) else 0.
                else:
                    print('customer: {}'.format(customer))
                    exit('Error, unexpected type of customer')

        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1

        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.uppers = {}
        self.lowers = {}
        for customer in self.customers:
            self.starts[customer] = 1
            self.betas[customer] = 0
            self.deltas[customer] = 1
            self.lowers[customer] = 0
            self.uppers[customer] = 10**3
            self.alphas[customer] = 0
            self.gammas[customer] = 0

        self.parameters = {}

    def create_rnd1(self):
        # Create RND1 instance

        self.parameters = {}
        self.parameters['S'] = 1
        self.parameters['T'] = 4
        self.parameters['I'] = 10
        self.parameters['J'] = 10

        rd.seed(self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location == customer else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 1

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}

        for customer in self.customers:
            # Upper, lower and initial demand
            self.lowers[customer] = 0
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.uppers[customer] = 10 * (self.parameters['T'] + 1)
            self.alphas[customer] = 0
            self.gammas[customer] = 0
            self.betas[customer] = rd.sample([0,1,2,3,4,5,7,8,9], 1)[0]
            self.deltas[customer] = 4 * self.betas[customer]

    def create_rnd2(self, seed):
        # Create RND2 instance

        self.parameters = {}
        self.parameters['S'] = seed
        self.parameters['T'] = 10
        self.parameters['I'] = 30
        self.parameters['J'] = 30

        rd.seed(self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            maximum = rd.sample([0.1 * self.parameters['J'], 0.3 * self.parameters['J'], 0.5 * self.parameters['J']], 1)[0]
            assigned = 0
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location == customer else rd.sample([0.,1.], 1)[0]
                assigned += self.catalogs[location][customer]
                if location != customer and assigned > maximum:
                    self.catalogs[location][customer] = 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 1

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}

        for customer in self.customers:
            # Upper, lower and initial demand
            self.lowers[customer] = 0
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.uppers[customer] = 10 ** 3
            self.alphas[customer] = 0
            self.gammas[customer] = 0
            self.betas[customer] = rd.sample([0,1,2,3,4,5,7,8,9], 1)[0]
            self.deltas[customer] = rd.sample([1,2,3,4,5], 1)[0] * self.betas[customer]

    '''
        Create instance used as worst-case scenario
        (the greedy heuristic is as close to 50%)
    '''
    def create_gap1(self):
        # Create GAP1 instance

        crafted_t = 5
        crafted_b1 = 5
        crafted_b2 = 4.9

        self.locations = ['1', '2']
        self.customers = ['1', '2']
        self.periods = [str(i) for i in range(1, crafted_t + 1)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location == customer else 0

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 1

        # Create alphas
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.lowers = {}
        self.uppers = {}
        self.deltas = {}
        self.starts = {}

        self.alphas['1'] = 0.
        self.betas['1'] = crafted_b1
        self.gammas['1'] = 0.
        self.lowers['1'] = 0.
        self.uppers['1'] = 10 * crafted_t
        self.deltas['1'] = crafted_b1 * crafted_t
        self.starts['1'] = 0.

        self.alphas['2'] = 0.
        self.betas['2'] = crafted_b2
        self.gammas['2'] = 0.
        self.lowers['2'] = 0.
        self.uppers['2'] = 10 * crafted_t
        self.deltas['2'] = crafted_b2
        self.starts['2'] = 0.

        self.parameters = {}

    '''
        Create instance used as a counter example
        (here, forced postponing is not always optimal)
    '''
    def create_gap2(self):
        # Create GAP2 instance

        self.locations = ['1', '2']
        self.customers = ['1', '2']
        self.periods = ['1', '2']

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if customer == location else 0.

        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1

        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.uppers = {}
        self.lowers = {}
        for customer in self.customers:
            self.starts[customer] = 0
            self.lowers[customer] = 0
            self.uppers[customer] = 10**3

            self.alphas[customer] = 0
            self.gammas[customer] = 0

        self.betas['1'] = 1
        self.deltas['1'] = 1.001
        self.betas['2'] = 0.1
        self.deltas['2'] = 0.1

        self.parameters = {}

    '''
        Create instance used as a case study for the paper
        (this might not be in the paper after all though)
    '''
    def create_slovakia(self):
        # Create slovakia instance

        self.parameters = {}
        self.parameters['B'] = 10
        self.parameters['T'] = 12

        table = pd.read_csv('slovakia/csv/nodes.csv')

        self.locations = table['id'].tolist()
        self.locations = [str(location) for location in self.locations]
        self.customers = table['id'].tolist()
        self.customers = [str(customer) for customer in self.customers]
        self.periods = [str(i) for i in range(1, self.parameters['T'] + 1)]

        self.distances = {}
        for location in self.locations:
            self.distances[location] = {}
            for customer in self.customers:
                self.distances[location][customer] = 0.

        with open('slovakia/csv/Dmatrix.txt') as content:

            # Read number of rows and columns
            rows = int(content.readline())
            cols = int(content.readline())

            # Store distances between points
            for location in self.locations:
                for customer in self.customers:
                    self.distances[location][customer] = float(content.readline())

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if self.distances[location][customer] <= self.parameters['B'] else 0.

        avg_patronizable = 0
        for customer in self.customers:
            patronizable = sum([self.catalogs[location][customer] for location in self.locations])
            print('Customer: {} -> {}'.format(customer, patronizable))
            avg_patronizable += patronizable
        print(avg_patronizable/len(self.customers))

    '''
        Create instance used for introducing problem in the paper
    '''
    def create_example(self):
        # Create example instance

        self.locations = ['1', '2', '3']
        self.customers = ['A','B', 'C']
        self.periods = ['1', '2', '3']

        # Create catalogs
        considerations = {}
        considerations ['A'] = ['1', '2']
        considerations ['B'] = ['1', '3']
        considerations ['C'] = ['2', '3']
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in considerations[customer] else 0

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1

        # Create alphas
        self.alphas = {}
        for customer in self.customers:
            self.alphas[customer] = 0

        # Create betas
        self.betas = {}
        self.betas['A'] = 5
        self.betas['B'] = 4
        self.betas['C'] = 5

        # Create gammmas
        self.gammas = {}
        for customer in self.customers:
            self.gammas[customer] = 1

        # Create deltas
        self.deltas = {}
        for customer in self.customers:
            self.deltas[customer] = 0

        # Create start values
        self.starts = {}
        self.starts['A'] = 15.
        self.starts['B'] = 26.
        self.starts['C'] = 5.

        # Create lower bounds
        self.lowers = {}
        for customer in self.customers:
            self.lowers[customer] = 1

        # Create upper bounds
        self.uppers = {}
        for customer in self.customers:
            self.uppers[customer] = 50

    '''
        Create instance used for drawing graphs for the paper
    '''
    def create_graph(self):
        # Create graph instance

        self.locations = ['1']
        self.customers = ['A']
        self.periods = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18']

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}
        for customer in self.customers:
            self.alphas[customer] = 0.25
            self.betas[customer] = 0
            self.gammas[customer] = 0.25
            self.deltas[customer] = 0
            self.starts[customer] = 10
            self.lowers[customer] = 0
            self.uppers[customer] = 10

        self.parameters = {}

    def fix_instance(self):
        # Fix created instance

        # Check if customers have at least one location in the catalog
        for customer in self.customers:
            if sum([self.catalogs[location][customer] for location in self.locations]) == 0:
                location = rd.sample(self.locations, 1)[0]
                self.catalogs[location][customer]  = 1.
                print('Quick fix: customer {} had no location in the catalog, assigned it to location {}'.format(customer, location))


    def print_instance(self):
        # Print stored instance

        print('Keyword: <{}>'.format(self.keyword))

        print('Customers: {}'.format(self.customers))
        for customer in self.customers:
            print('\t| {}: {}, {}, {}, {}, {}, {}, {} [{}]'.format(
                customer,
                self.alphas[customer],
                self.betas[customer],
                self.gammas[customer],
                self.deltas[customer],
                self.lowers[customer],
                self.uppers[customer],
                self.starts[customer],
                self.bigM[customer]))

        print('Locations: {}'.format(self.locations))
        for location in self.locations:
            print('\t| {} ({}) : {}'.format(location, self.revenues['1'][location], self.capturable_from(location)))

    def capturable_from(self, location):
        # Retrieve capturable customers from some location

        return [customer for customer in self.customers if self.catalogs[location][customer] == 1]