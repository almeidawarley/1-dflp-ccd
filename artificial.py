import instance as ic
import numpy as np
import json as js

class artificial(ic.instance):

    def __init__(self, keyword, project):

        super().__init__(keyword, project)

    def create_instance(self, folder = 'instances/artificial'):
        # Create artificial instances

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            print('No file found for keyword {}'.format(self.keyword))

        np.random.seed(self.parameters['seed'])

        # Create instance sets
        number_locations = int(self.parameters['locations'])
        self.locations = [str(i + 1) for i in range(number_locations)]
        number_customers = int(self.parameters['customers'])
        self.customers = [str(i + 1) for i in range(number_customers)]
        number_periods = int(self.parameters['periods'])
        self.periods = [int(i + 1) for i in range(number_periods)]

        # Create random preferences
        if self.parameters['patronizing'] == 'small':
            patronizing = 0.5 # 1 / 2.01
        elif self.parameters['patronizing'] == 'medium':
            patronizing = 1
        elif self.parameters['patronizing'] == 'large':
            patronizing = 2 # 2.01
        else:
            exit('Wrong value for patronizing parameter')
        consideration_size = int(np.ceil((patronizing * number_locations) / number_periods))
        consideration_sets = {}
        for customer in self.customers:
            consideration_sets[customer] = np.random.choice(self.locations, consideration_size)

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in consideration_sets[customer] or location == customer else 0

        # Create rewards
        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                popularity = sum([self.catalogs[location][customer] for customer in self.customers])
                if self.parameters['rewards'] == 'identical':
                    coefficient = 1.
                elif self.parameters['rewards'] == 'inversely':
                    coefficient = 1. / popularity
                else:
                    exit('Wrong value for rewards parameter')
                self.rewards[period][location] = np.ceil(coefficient * len(self.customers))

        stored_f = {}
        def bass(t, p = 0.04, q = 0.4, m = 10):
            return (p * m + (q - p) * sum(v for x, v in stored_f.items() if x <= t) - (q/m) * (sum(v for x, v in stored_f.items() if x <= t)) ** 2)

        for period in self.periods:
            stored_f[period] = bass(period)

        # Create amplitude
        self.amplitude = {}
        for customer in self.customers:
            if self.parameters['behaviour'] == 'heterogeneous':
                self.amplitude[customer] = np.random.choice([0, 5, 10, 15, 20])
            elif self.parameters['behaviour'] == 'homogeneous':
                self.amplitude[customer] = 10
            else:
                exit('Wrong value for behaviour parameter')

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                if self.parameters['demand'] == 'constant':
                    self.spawning[period][customer] = self.amplitude[customer]
                elif self.parameters['demand'] == 'seasonal':
                    self.spawning[period][customer] = (self.amplitude[customer] / 2) * np.cos(period) + (self.amplitude[customer] / 2)
                elif self.parameters['demand'] == 'increasing':
                    self.spawning[period][customer] = (period / number_periods) * self.amplitude[customer]
                elif self.parameters['demand'] == 'decreasing':
                    self.spawning[period][customer] = self.amplitude[customer] - ((period - 1)/ number_periods) * self.amplitude[customer]
                elif self.parameters['demand'] == 'bass':
                    self.spawning[period][customer] = stored_f[period] * self.amplitude[customer]
                else:
                    exit('Wrong value for demand behaviour')
                self.spawning[period][customer] = np.ceil(self.spawning[period][customer])