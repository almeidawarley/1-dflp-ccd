import instance as ic
import numpy as np
import json as js

class benchmark(ic.instance):

    def __init__(self, keyword):

        super().__init__(keyword)

    def create_instance(self, folder = 'instances/benchmark'):

        # Create benchmark instances
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
        times_customers = int(self.parameters['customers'])
        number_customers = times_customers * number_locations
        self.customers = [str(i + 1) for i in range(number_customers)]
        number_periods = int(self.parameters['periods'])
        self.periods = [int(i + 1) for i in range(number_periods)]

        # Store number of facilities
        self.facilities = {period : int(self.parameters['facilities']) for period in self.periods}

        # Create random preferences
        if self.parameters['preferences'] == 'small':
            percentage = 0.10
        elif self.parameters['preferences'] == 'large':
            percentage = 0.20
        else:
            exit('Wrong value for preferences parameter')
        consideration_size = int(np.ceil(percentage * number_locations))
        consideration_sets = {}
        for customer in self.customers:
            consideration_sets[customer] = np.random.choice(self.locations, consideration_size)

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in consideration_sets[customer] else 0

        # Create rewards
        self.rewards = {}
        for location in self.locations:
            popularity = sum(self.catalogs[location][customer] for customer in self.customers)
            if self.parameters['rewards'] == 'identical':
                coefficient = 1.
            elif self.parameters['rewards'] == 'inversely':
                coefficient = 1. / popularity if popularity > 0. else 1.
            else:
                exit('Wrong value for rewards parameter')
            self.rewards[location] = np.ceil(coefficient * len(self.locations))

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

        # Create penalties
        self.penalties = {
            customer : np.ceil(
                int(self.parameters['penalties'])  * 0.25 *
                sum(
                    self.catalogs[location][customer] *
                    self.rewards[location]
                    for location in self.locations
                ) /
                sum(
                    self.catalogs[location][customer]
                    for location in self.locations
                )
            )
            for customer in self.customers
        }

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
                            self.coefficients[period1][period2][location][customer] -= self.penalties[customer] * sum(self.spawning[period3][customer] for period3 in self.periods if period3 > period1 and period3 < period2)