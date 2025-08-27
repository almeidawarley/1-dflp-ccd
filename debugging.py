import instance as ic
import random as rd
import numpy as np

class debugging(ic.instance):

    def __init__(self, keyword):

        super().__init__(keyword)

    def create_instance(self):

        # Decide instance type
        if self.keyword == 'jopt':
            # Create JOPT instance
            self.create_jopt()
        elif self.keyword == 'approx':
            # Create approx instance
            self.create_approx()
        elif self.keyword == 'spp':
            # Create SPP instance
            self.create_spp()
        elif self.keyword == 'proof':
            # Create proof instance
            self.create_proof()
        else:
            exit('Invalid instance keyword')

        self.facilities = {period: 1 for period in self.periods}

        # Set proper time periods
        self.start, self.final = 0, len(self.periods) + 1
        self.periods_with_start = [self.start] + [period for period in self.periods]
        self.periods_with_final = [period for period in self.periods] + [self.final]
        self.periods_extended = [self.start] + [period for period in self.periods] + [self.final]

        # Compute accumulated demand
        self.accumulated = {}
        for period1 in self.periods_with_start:
            self.accumulated[period1] = {}
            for period2 in self.periods:
                if period1 < period2:
                    self.accumulated[period1][period2] = {}
                    for customer in self.customers:
                        # self.accumulated[period1][period2][customer] = sum(self.spawning[period][customer] for period in self.periods if period <= period2 - period1) 
                        self.accumulated[period1][period2][customer] = sum(self.spawning[period][customer] for period in self.periods if period1 < period and period <= period2)

        # Compute captured locations
        self.captured_locations = {}
        for customer in self.customers:
            self.captured_locations[customer] = [location for location in self.locations if self.catalogs[location][customer] == 1]

        # Compute captured customers
        self.captured_customers = {}
        for location in self.locations:
            self.captured_customers[location] = [customer for customer in self.customers if self.catalogs[location][customer] == 1]

        # Set proper limit values
        self.limits = {}
        for period in self.periods:
            self.limits[period] = {}
            for customer in self.customers:
                limit = self.accumulated[self.start][period][customer]
                self.limits[period][customer] = np.ceil(limit)

        # Compute coefficients
        self.coefficients = {}
        for period1 in self.periods_with_start:
            self.coefficients[period1] = {}
            for period2 in self.periods_with_final:
                if period1 < period2:
                    self.coefficients[period1][period2] = {}
                    for location in self.locations:
                        self.coefficients[period1][period2][location] = {}
                        for customer in self.captured_customers[location]:
                            if period2 != self.final:
                                self.coefficients[period1][period2][location][customer] = self.rewards[location] * self.accumulated[period1][period2][customer]
                            else:
                                self.coefficients[period1][period2][location][customer] = 0.

    def create_spp(self, random = False):
        # Create SPP instances

        # Set target K
        K = 5
        if random:
            np.random.seed(self.parameters['seed'])
            B = 10
            C = 5
            elements = [str(i) for i in range(1, B + 1)]
            collections = [np.random.choice(elements, rd.randint(1,int(B/1.1))) for _ in range(0, C)]
        else:
            B = 5
            C = 5
            elements = ['1', '2', '3', '4', '5']
            collections = [['1', '2', '3', '4', '5'], ['1'], ['2'], ['3'], ['1', '4', '5']] #, ['5']]

        self.locations = [str(i + 1) for i in range(0, len(collections))] + [str(i + 1 + len(collections)) for i in range(0, len(collections))]
        self.customers = [e for e in elements] + [str(i + 1 + len(elements)) for i in range(0, len(collections))]
        self.periods = [int(i + 1) for i in range(0, C)]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                if int(location) <= len(collections) and int(customer) <= len(elements):
                    self.catalogs[location][customer] = 1 if customer in collections[int(location)-1] else 0
                elif int(location) <= len(collections) and int(customer) > len(elements):
                    self.catalogs[location][customer] = 0
                elif int(location) > len(collections) and int(customer) <= len(elements):
                    self.catalogs[location][customer] = 0
                else:
                    self.catalogs[location][customer] = 1 if int(location) - 1 - len(collections) == int(customer) - 1 - len(elements) else 0

        self.rewards = {}
        for location in self.locations:
            if int(location) <= len(collections):
                self.rewards[location] =  1 / len(collections[int(location)-1])
            else:
                self.rewards[location] =  0.99
            '''
            if location == '1':
                # Avoid ambiguity for heuristic
                self.rewards[location] = 0.21
                '''

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1. if period == 1 else 0.

    def create_proof(self, K = 2):
        # Create proof instance

        elements = ['1', '2']
        collections = [['1'], ['2'], ['1', '2']]

        self.locations = [str(i + 1) for i in range(0, len(collections))]
        self.customers = [e for e in elements]
        self.periods = [int(i + 1) for i in range(0, K)]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if customer in collections[int(location)-1] else 0

        self.rewards = {}
        for location in self.locations:
            self.rewards[location] =  1/len(collections[int(location)-1])
            if location == '3':
                # Avoid ambiguity for heuristic
                self.rewards[location] = 0.51

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1.

    '''
        Create instance used for approximation proof
    '''
    def create_approx(self):
        # Create approx instance

        self.locations = ['1', '2', '3']
        self.customers = ['A','B', 'C', 'D', 'E']
        self.periods = [1, 2]

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

        # Create rewards
        self.rewards = {}
        for location in self.locations:
            self.rewards[location] =  1

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1. if period == 1 else 0.

    '''
        Create instance used for JOPT presentation
    '''
    def create_jopt(self):
        # Create JOPT instance

        self.locations = ['1', '2', '3', '4']
        self.customers = ['1', '2', '3']
        self.periods = [1, 2, 3] #, 4]

        # Create catalogs
        considerations = {}
        considerations ['1'] = ['1', '2', '4']
        considerations ['2'] = ['1', '3', '4']
        considerations ['3'] = ['2', '3', '4']
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in considerations[customer] else 0

        rewards = {'1': 4., '2': 4., '3': 4., '4': 3.}

        # Create rewards
        self.rewards = {}
        for location in self.locations:
            self.rewards[location] = rewards[location]

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1.