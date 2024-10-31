import instance as ic
import numpy as np
import json as js

class artificial(ic.instance):

    def __init__(self, keyword):

        super().__init__(keyword)

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

        # Store number of facilities
        self.facilities = {period : int(self.parameters['facilities']) for period in self.periods}

        # Create random preferences
        if self.parameters['preferences'] == 'only':
            preferences = 0
        elif self.parameters['preferences'] == 'small':
            preferences = 0.5
        elif self.parameters['preferences'] == 'medium':
            preferences = 1
        elif self.parameters['preferences'] == 'large':
            preferences = 2
        else:
            exit('Wrong value for preferences parameter')
        consideration_size = int(np.ceil((preferences * number_locations) / number_periods))
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
                popularity = sum(self.catalogs[location][customer] for customer in self.customers)
                if self.parameters['rewards'] == 'identical':
                    coefficient = 1.
                elif self.parameters['rewards'] == 'inversely':
                    coefficient = 1. / popularity
                else:
                    exit('Wrong value for rewards parameter')
                self.rewards[period][location] = np.ceil(coefficient * len(self.locations))

        # Create amplitude
        self.amplitudes = {}
        for customer in self.customers:
            if self.parameters['characters'] == 'heterogeneous':
                self.amplitudes[customer] = np.random.choice([10, 15, 20, 25, 30])
            elif self.parameters['characters'] == 'homogeneous':
                self.amplitudes[customer] = 20
            else:
                exit('Wrong value for behaviour parameter')

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                if self.parameters['demands'] == 'constant':
                    self.spawning[period][customer] = self.amplitudes[customer]
                elif self.parameters['demands'] == 'seasonal':
                    self.spawning[period][customer] = (self.amplitudes[customer] / 2) * np.cos(period) + (self.amplitudes[customer] / 2)
                elif self.parameters['demands'] == 'increasing':
                    self.spawning[period][customer] = (period / number_periods) * self.amplitudes[customer]
                elif self.parameters['demands'] == 'decreasing':
                    self.spawning[period][customer] = ((number_periods - period + 1)/ number_periods) * self.amplitudes[customer]
                else:
                    exit('Wrong value for demand behaviour')
                self.spawning[period][customer] = np.ceil(self.spawning[period][customer])

        # Store customer penalties
        '''
        # Left here for the sake of future reference
        self.penalties = {
            customer : (
                int(self.parameters['penalties'])  * 0.25 *
                len(self.locations)
            )
            for customer in self.customers
        }
        '''
        self.penalties = {
            customer : np.ceil(
                int(self.parameters['penalties'])  * 0.25 *
                sum(
                    self.catalogs[location][customer] *
                    self.rewards[self.start + 1][location]
                    for location in self.locations
                ) /
                sum(
                    self.catalogs[location][customer]
                    for location in self.locations
                )
            )
            for customer in self.customers
        }