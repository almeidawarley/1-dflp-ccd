import random as rd
import json as js
import matplotlib.pyplot as pt

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
            self.create_setA()

        # Fix created instance
        self.fix_instance()

        # Print stored instance
        self.print_instance()

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

        '''
        # Create map points
        self.points = {}
        X = []
        Y = []
        for location in self.locations:
            self.points['i{}'.format(location)] = (rd.randint(-5, 5), rd.randint(-5, 5))
            X.append(self.points['i{}'.format(location)][0])
            Y.append(self.points['i{}'.format(location)][1])
        pt.scatter(X, Y, marker = 'x')
        X = []
        Y = []
        for customer in self.customers:
            self.points['j{}'.format(customer)] = (rd.randint(-5, 5), rd.randint(-5, 5))
            X.append(self.points['j{}'.format(customer)][0])
            Y.append(self.points['j{}'.format(customer)][1])
        pt.scatter(X, Y, marker = 'o')
        pt.show()
        '''

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
            random = rd.randint(5 - self.parameters['zeta'], 5 + self.parameters['zeta'])
            if self.parameters['replenishment'] == 'linear':
                self.alphas[customer] = 0
                self.betas[customer] = random
                self.lowers[customer] = 0
            elif self.parameters['replenishment'] == 'exponential':
                self.alphas[customer] = random/10.
                self.betas[customer] = 0
                self.lowers[customer] = 10./random
            else:
                exit('Invalid value for parameter replenishment type')
            if self.parameters['absorption'] == 'linear':
                    self.gammas[customer] = 0
                    self.deltas[customer] = 2 * random
            elif self.parameters['absorption'] == 'exponential':
                self.gammas[customer] = 2 * random/10.
                self.deltas[customer] = 0
            else:
                exit('Invalid value for parameter absorption type')
            self.starts[customer] = self.lowers[customer]
            self.uppers[customer] = rd.sample([10,20,30,40,50], 1)[0]

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