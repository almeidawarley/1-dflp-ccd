import matplotlib.pyplot as pt
import random as rd
import math as mt
import json as js

class instance:

    def __init__(self, keyword):
        # Initiate instance class

        # Store instance keyword
        instance.keyword = keyword

        # Decide instance type
        if keyword == 'example':
            # Create example instance
            self.create_example()
        elif keyword == 'spp':
            # Create SPP instance
            self.create_spp()
        else:
            # Create random instance
            if 'A-' in keyword:
                self.create_setA()
            elif 'B-' in keyword:
                self.create_setB()
            elif 'C-' in keyword:
                self.create_setC()
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

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(int(self.parameters['S']))

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
                self.revenues[period][location] =  10

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}
        for customer in self.customers:
            lower = 100 - self.parameters['zeta']
            upper = 100 + self.parameters['zeta']
            random_s = rd.randint(lower, upper) / 100.
            lower = 100 - self.parameters['eta']
            upper = 100 + self.parameters['eta']
            random_t = rd.randint(lower, upper) / 100.
            if self.parameters['replenishment'] == 'linear':
                self.alphas[customer] = 0
                self.betas[customer] = round(random_s * 10, 2)
                self.lowers[customer] = 0
            elif self.parameters['replenishment'] == 'exponential':
                self.alphas[customer] = round(random_s * 0.5, 2)
                self.betas[customer] = 0
                self.lowers[customer] = round(1 / (1 + self.alphas[customer]), 2)
            else:
                exit('Invalid value for parameter replenishment type')
            if self.parameters['absorption'] == 'linear':
                self.gammas[customer] = 0
                self.deltas[customer] = round(random_s * random_t * 10, 2)
            elif self.parameters['absorption'] == 'exponential':
                self.gammas[customer] = round(random_s * random_t * 0.5, 2)
                self.deltas[customer] = 0
            else:
                exit('Invalid value for parameter absorption type')
            self.starts[customer] = rd.sample([0,10,20], 1)[0]
            self.uppers[customer] = 100

    def create_setB(self, folder = 'instances'):
        # Create instance set B

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(int(self.parameters['S']))

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

        self.threshold = {}
        radius_index = mt.floor((self.parameters['theta'] / 100) * number_locations) - 1
        for customer in self.customers:
            distances = []
            for location in self.locations:
                distances.append(mt.dist(self.points['i{}'.format(location)], self.points['j{}'.format(customer)]))
            distances.sort()
            self.threshold[customer] = distances[radius_index]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if mt.dist(self.points['i{}'.format(location)], self.points['j{}'.format(customer)]) <= self.threshold[customer] else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  10

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}
        for customer in self.customers:
            if self.parameters['replenishment'] == 'linear':
                self.alphas[customer] = 0
                self.betas[customer] = round((self.parameters['zeta'] / 100) * 10, 2)
                self.lowers[customer] = 0
            elif self.parameters['replenishment'] == 'exponential':
                self.alphas[customer] = round((self.parameters['zeta'] / 100) * 0.5, 2)
                self.betas[customer] = 0
                self.lowers[customer] = round(1 / (1 + self.alphas[customer]), 2)
            else:
                exit('Invalid value for parameter replenishment type')
            if self.parameters['absorption'] == 'linear':
                self.gammas[customer] = 0
                self.deltas[customer] = round((self.parameters['zeta'] / 100) * (1 + self.parameters['eta'] / 100) * 10, 2)
            elif self.parameters['absorption'] == 'exponential':
                self.gammas[customer] = round((self.parameters['zeta'] / 100) * (1 + self.parameters['eta'] / 100) * 0.5, 2)
                self.deltas[customer] = 0
            else:
                exit('Invalid value for parameter absorption type')
            self.starts[customer] = rd.sample([0,10,20], 1)[0]
            self.uppers[customer] = 100

    def create_setC(self, folder = 'instances'):
        # Create instance set C

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            with open ('experiments/{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)

        rd.seed(int(self.parameters['S']))

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
            self.points['i{}'.format(location)] = [rd.randint(-50, 50), rd.randint(-50, 50)]
        for customer in self.customers:
            self.points['j{}'.format(customer)] = [rd.randint(-50, 50), rd.randint(-50, 50)]
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

        self.threshold = {}
        for customer in self.customers:
            theta = rd.sample([25,50,75], 1)[0]
            radius_index = mt.floor((theta / 100) * number_locations) - 1
            distances = []
            for location in self.locations:
                distances.append(mt.dist(self.points['i{}'.format(location)], self.points['j{}'.format(customer)]))
            distances.sort()
            self.threshold[customer] = distances[radius_index]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if mt.dist(self.points['i{}'.format(location)], self.points['j{}'.format(customer)]) <= self.threshold[customer] else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  10

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.lowers = {}
        self.uppers = {}
        for customer in self.customers:
            lower = 100 - self.parameters['zeta']
            upper = 100 + self.parameters['zeta']
            random_s = rd.randint(lower, upper) / 100.
            lower = 100 - self.parameters['eta']
            upper = 100 + self.parameters['eta']
            random_t = rd.randint(lower, upper) / 100.
            if self.parameters['replenishment'] == 'linear':
                self.alphas[customer] = 0
                self.betas[customer] = round(random_s * 10, 2)
                self.lowers[customer] = 0
            elif self.parameters['replenishment'] == 'exponential':
                self.alphas[customer] = round(random_s * 0.5, 2)
                self.betas[customer] = 0
                self.lowers[customer] = round(1 / (1 + self.alphas[customer]), 2)
            else:
                exit('Invalid value for parameter replenishment type')
            if self.parameters['absorption'] == 'linear':
                self.gammas[customer] = 0
                self.deltas[customer] = round(random_s * random_t * 10, 2)
            elif self.parameters['absorption'] == 'exponential':
                self.gammas[customer] = round(random_s * random_t * 0.5, 2)
                self.deltas[customer] = 0
            else:
                exit('Invalid value for parameter absorption type')
            self.starts[customer] = rd.sample([0,10,20], 1)[0]
            self.uppers[customer] = 100

    def create_spp(self, K = 2):
        # Create SPP instances

        elements = ['1', '2', '3', '4', '5']
        collections = [['1', '2', '3'], ['1', '4', '5'], ['1', '5']]

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

        self.alphas = {}
        self.betas = {}
        self.gammas = {}
        self.deltas = {}
        self.starts = {}
        self.uppers = {}
        self.lowers = {}
        for customer in self.customers:
            self.alphas[customer] = 0
            self.betas[customer] = 0
            self.gammas[customer] = 0
            self.deltas[customer] = 1
            self.starts[customer] = 1
            self.lowers[customer] = 0
            self.uppers[customer] = 1000000

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

    def fix_instance(self):
        # Fix created instance

        # Check if customers have at least one location in the catalog
        for customer in self.customers:
            if sum([self.catalogs[location][customer] for location in self.locations]) == 0:
                location = rd.sample(self.locations, 1)[0]
                self.catalogs[location][customer]  = 1.
                print('Fix: customer {} had no location in the catalog, assigned it to location {}'.format(customer, location))


    def print_instance(self):
        # Print stored instance

        print('Keyword: <{}>'.format(self.keyword))

        print('Customers: {}'.format(self.customers))
        for customer in self.customers:
            print('\t| {}: {}, {}, {}, {}, {}, {}, {}'.format(
                customer,
                self.alphas[customer],
                self.betas[customer],
                self.gammas[customer],
                self.deltas[customer],
                self.lowers[customer],
                self.uppers[customer],
                self.starts[customer]))

        print('Locations: {}'.format(self.locations))
        for location in self.locations:
            print('\t| {} ({}) : {}'.format(location, self.revenues['1'][location], self.capturable_from(location)))

    def capturable_from(self, location):
        # Retrieve capturable customers from some location

        return [customer for customer in self.customers if self.catalogs[location][customer] == 1]