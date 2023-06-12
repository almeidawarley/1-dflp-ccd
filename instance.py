import matplotlib.pyplot as pt
import math as mt
import json as js
import pandas as pd
import random as rd
import numpy as np

class instance:

    def __init__(self, keyword, project):
        # Initiate instance class

        # Store instance keyword
        instance.keyword = keyword
        # Store project keyword
        instance.project = project

        # Store parameters
        self.parameters = {}

        # Decide instance type
        if keyword == 'jopt':
            # Create JOPT instance
            self.create_jopt()
        elif keyword == 'graph':
            # Create graph instance
            self.create_graph()
        elif keyword == 'approx':
            # Create approx instance
            self.create_approx()
        elif keyword == 'gap1':
            # Create GAP1 instance
            self.create_gap1()
        elif keyword == 'gap2':
            # Create GAP2 instance
            self.create_gap2()
        elif keyword == 'spp':
            # Create SPP instance
            self.create_spp()
        elif '.cnf' in keyword:
            # Create 3SAT instance
            self.create_3sat()
        elif 'rnd1' in keyword:
            # Create RND1 instance
            self.create_rnd1()
        elif 'rnd2' in keyword:
            # Create RND2 instance
            self.create_rnd2()
        elif keyword == '1toN':
            # Create 1:N instance
            self.create_1toN()
        elif keyword == 'slovakia':
            # Create slovakia instance
            self.create_slovakia()
        elif 'syn' in keyword:
            # Create synthetic instance
            self.create_synthetic()
        else:
            exit('Invalid instance keyword')

        # Set proper big M values
        self.bigM = {}
        for customer in self.customers:
            self.bigM[customer] = self.uppers[customer] + self.alphas[customer] * self.uppers[customer] + self.betas[customer] + self.gammas[customer] * self.uppers[customer] + self.deltas[customer]

    def create_synthetic(self, folder = 'instances/synthetic'):
        # Create synthetic instances

        # Read specifications from file
        with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
            self.parameters = js.load(content)

        np.random.seed(self.parameters['seed'])

        # Set instance information
        number_locations = int(self.parameters['locations'])
        number_customers = int(self.parameters['customers'])
        number_periods = int(self.parameters['periods'])

        assert number_customers == number_locations, 'Number of customers and locations must be equal'
        assert number_periods == number_locations/5, 'Number of periods must be 1/5 number of locations'

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create coordinates in map
        self.points = {}
        for location in self.locations:
            if self.parameters['coordinates'] == 'uniform':
                x = np.random.uniform(0,100)
                y = np.random.uniform(0,100)
            elif self.parameters['coordinates'] == 'normal1':
                x = max(0, min(np.random.normal(50,10), 100), 0)
                y = max(0, min(np.random.normal(50,10), 100), 0)
                self.points['{}'.format(location)] = [x, y]
            elif self.parameters['coordinates'] == 'normal5':
                sector = number_locations/5
                if int(location) <= 1 * sector:
                    x = max(0, min(np.random.normal(25,10), 100), 0)
                    y = max(0, min(np.random.normal(25,10), 100), 0)
                elif int(location) <= 2 * sector:
                    x = max(0, min(np.random.normal(25,10), 100), 0)
                    y = max(0, min(np.random.normal(75,10), 100), 0)
                elif int(location) <= 3 * sector:
                    x = max(0, min(np.random.normal(50,10), 100), 0)
                    y = max(0, min(np.random.normal(50,10), 100), 0)
                elif int(location) <= 4 * sector:
                    x = max(0, min(np.random.normal(75,10), 100), 0)
                    y = max(0, min(np.random.normal(25,10), 100), 0)
                elif int(location) <= 5 * sector:
                    x = max(0, min(np.random.normal(75,10), 100), 0)
                    y = max(0, min(np.random.normal(75,10), 100), 0)
            else:
                exit('Wrong value for coordinates parameter')
            self.points['{}'.format(location)] = [int(np.floor(x)), int(np.floor(y))]
        X = [self.points['{}'.format(location)][0] for location in self.locations]
        Y = [self.points['{}'.format(location)][1] for location in self.locations]
        pt.xticks(range(0, 101, 20))
        pt.yticks(range(0, 101, 20))
        pt.scatter(X, Y, marker = 'o')
        for location in self.locations:
            pt.annotate(location, (X[int(location) - 1], Y[int(location) - 1]))
        pt.savefig('archives/{}-coordinates.png'.format(self.keyword))

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                if self.parameters['patronizing'] == 'radius0':
                    radius = 0.
                elif self.parameters['patronizing'] == 'radius15':
                    radius = 15.
                elif self.parameters['patronizing'] == 'radius30':
                    radius = 30.
                else:
                    exit('Wrong value for patronizing parameter')
                if self.parameters['correlation'] == 'low':
                    chance = 0.25
                elif self.parameters['correlation'] == 'medium':
                    chance = 0.50
                elif self.parameters['correlation'] == 'high':
                    chance = 0.75
                else:
                    exit('Wrong value for correlation parameter')
                self.catalogs[location][customer] = 1. if mt.dist(self.points['{}'.format(location)], self.points['{}'.format(customer)]) <= radius and (np.random.choice([0., 1.], p = [1 - chance, chance]) or location == customer) else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                popularity = sum([self.catalogs[location][customer] for customer in self.customers])
                if self.parameters['rewards'] == 'identical':
                    coefficient = 1.
                elif self.parameters['rewards'] == 'inversely':
                    coefficient = 1. / popularity
                elif self.parameters['rewards'] == 'directly':
                    coefficient = 1. - 1. / popularity
                else:
                    exit('Wrong value for rewards parameter')
                self.revenues[period][location] = np.ceil(coefficient * 10)

        # Create parameters
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
            self.uppers[customer] = 10**6
            if self.parameters['initial'] == 'low':
                self.starts[customer] = 1
            elif self.parameters['initial'] == 'high':
                self.starts[customer] = 5
            else:
                exit('Wrong value for initial parameter')
            if self.parameters['type'] == 'relative':
                self.betas[customer] = 0
                if self.parameters['replenishment'] == 'none':
                    self.alphas[customer] = 0
                elif self.parameters['replenishment'] == 'low':
                    self.alphas[customer] = 0.1
                elif self.parameters['replenishment'] == 'high':
                    self.alphas[customer] = 0.5
                else:
                    exit('Wrong value for replenishment parameter')
            elif self.parameters['type'] == 'absolute':
                self.alphas[customer] = 0
                if self.parameters['replenishment'] == 'none':
                    self.betas[customer] = 0
                elif self.parameters['replenishment'] == 'low':
                    self.betas[customer] = 1
                elif self.parameters['replenishment'] == 'high':
                    self.betas[customer] = 5
                else:
                    exit('Wrong value for replenishment parameter')
            if self.parameters['absorption'] == 'full':
                self.gammas[customer] = 1
                self.deltas[customer] = 0
            else:
                if self.parameters['absorption'] == 'low':
                    factor = 0.25
                elif self.parameters['absorption'] == 'medium':
                    factor = 0.50
                elif self.parameters['absorption'] == 'high':
                    factor = 0.75
                else:
                    exit('Wrong value for absorption parameter')
                self.gammas[customer] = 0
                self.deltas[customer] = np.floor(factor * number_periods) * max(self.betas[customer], 10 * self.alphas[customer])

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

    def create_3sat(self, folder = 'instances/3sat'):
        # Create 3SAT instances

        with open('{}/{}'.format(folder, self.keyword), 'r') as content:
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

    def create_rnd1(self):
        # Create RND1 instance

        '''
            Previous key RND1 example could be fixed with a tie breaking rule.
            Here are the configurations: S = 1, T = 4, I = J = 10, delta = 4 * beta
        '''

        seed = int(self.keyword.replace('rnd1', ''))

        self.parameters['S'] = 5
        self.parameters['T'] = 5
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
            self.deltas[customer] = 4 * self.betas[customer] # 10 * (self.parameters['T'] + 1) # 4 * self.betas[customer]

    def create_rnd2(self):
        # Create RND2 instance

        seed = int(self.keyword.replace('rnd2', ''))

        self.parameters['S'] = 222 # seed
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

    def create_1toN(self):
        # Create 1toN instance

        self.parameters['S'] = 0
        self.parameters['T'] = 20
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
                self.catalogs[location][customer] = 1. if location == customer else rd.sample([0.,1.], 1)[0]

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
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9], 1)[0]
            self.uppers[customer] = 10 ** 6 # infinity
            self.alphas[customer] = 0.1
            self.gammas[customer] = 0.1
            self.betas[customer] = rd.sample([1,2,3,4,5,6,7,8,9], 1)[0]
            self.deltas[customer] = rd.sample([1,2,3,4,5,6,7,8,9], 1)[0]

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

    '''
        Create instance used as a case study for the paper
        (this might not be in the paper after all though)
    '''
    def create_slovakia(self):
        # Create slovakia instance

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
        Create instance used for approximation proof
    '''
    def create_approx(self):
        # Create approx instance

        self.locations = ['1', '2', '3']
        self.customers = ['A','B', 'C', 'D', 'E']
        self.periods = ['1', '2']

        # Create catalogs
        considerations = {}
        considerations ['A'] = ['1', '3']
        considerations ['B'] = ['1', '2']
        considerations ['C'] = ['1', '2', '3']
        considerations ['D'] = ['2']
        considerations ['E'] = ['3']
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
        for customer in self.customers:
            self.betas[customer] = 0

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
        for customer in self.customers:
            self.starts[customer] = 1

        # Create lower bounds
        self.lowers = {}
        for customer in self.customers:
            self.lowers[customer] = 0

        # Create upper bounds
        self.uppers = {}
        for customer in self.customers:
            self.uppers[customer] = 10 ** 3

    '''
        Create instance used for JOPT presentation
    '''
    def create_jopt(self):
        # Create JOPT instance

        self.locations = ['1', '2', '3', '4']
        self.customers = ['A', 'B', 'C']
        self.periods = ['1', '2', '3']

        # Create catalogs
        considerations = {}
        considerations ['A'] = ['1', '2', '4']
        considerations ['B'] = ['1', '3', '4']
        considerations ['C'] = ['2', '3', '4']
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in considerations[customer] else 0

        revenues = {'1': 4., '2': 4., '3': 4., '4': 3.}

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = revenues [location]

        # Create alphas
        self.alphas = {}
        for customer in self.customers:
            self.alphas[customer] = 0

        # Create betas
        self.betas = {}
        self.betas['A'] = 1
        self.betas['B'] = 1
        self.betas['C'] = 1

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
        self.starts['A'] = 0.
        self.starts['B'] = 0.
        self.starts['C'] = 0.

        # Create lower bounds
        self.lowers = {}
        for customer in self.customers:
            self.lowers[customer] = 0

        # Create upper bounds
        self.uppers = {}
        for customer in self.customers:
            self.uppers[customer] = 10**3

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

    def print_instance(self):
        # Print stored instance

        print('Keyword: <{}>'.format(self.keyword))

        print('Customers: {}'.format(self.customers))
        print('\t| j: a, b, g, d, l, u, s [M]')
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