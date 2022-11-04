import random as rd
import pandas as pd

class instance:

    def __init__(self, keyword):
        # Initiate instance class

        instance.keyword = keyword

        if keyword == 'example':
            # Create random instance
            self.create_example()
        else:
            self.create_random()

        # Validate stored instance
        self.validate_instance()

        # Print stored instance
        self.print_instance()

        # Set proper big M values
        self.bigM = {}
        for customer in self.customers:
            self.bigM[customer] = self.uppers[customer] + self.alphas[customer] * self.uppers[customer] + self.betas[customer] + self.gammas[customer] * self.uppers[customer] + self.deltas[customer]

    def create_random(self, folder = 'instances'):
        # Create random instance

        try:
            # Read specifications from file
            specs = pd.read_csv('{}/{}.csv'.format(folder, instance.keyword), index_col = 0)
        except:
            try:
                specs = pd.read_csv('servers/{}/{}.csv'.format(folder, instance.keyword), index_col = 0)
            except:
                specs = pd.read_csv('experiments/{}/{}.csv'.format(folder, instance.keyword), index_col = 0)

        rd.seed(int(specs.loc['seed']['value']))

        # Set instance size
        number_locations = int(specs.loc['number of locations']['value'])
        number_customers = int(specs.loc['number of customers']['value'])
        number_periods = int(specs.loc['number of periods']['value'])

        self.locations = [str(i+1) for i in range(number_locations)]
        self.customers = [str(i+1) for i in range(number_customers)]
        self.periods = [str(i+1) for i in range(number_periods)]

        # Decide patronization
        subsets = {}
        for location in self.locations:
            if specs.loc['location relevances']['value'] == 'local':
                subsets[location] = [location]
            elif specs.loc['location relevances']['value'] == 'medium':
                subsets[location] = rd.sample(self.customers, rd.randint(2, 4))
            elif specs.loc['location relevances']['value'] == 'large':
                subsets[location] = rd.sample(self.customers, rd.randint(5, 7))
            else:
                exit('Invalid value for parameter location relevances')

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if customer in subsets[location] else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                if specs.loc['location revenues']['value'] == 'same':
                    self.revenues[period][location] =  10
                elif specs.loc['location revenues']['value'] == 'different':
                    self.revenues[period][location] = rd.randint(5,15) if period == '1' else self.revenues[str(int(period) - 1)][location]
                else:
                    exit('Invalid value for parameter location revenues')

        # Create alphas and betas
        self.alphas = {}
        self.betas = {}
        for customer in self.customers:
            if specs.loc['replenishment type']['value'] == 'doubling':
                self.alphas[customer] = 1
                self.betas[customer] = 0
            elif specs.loc['replenishment type']['value'] == 'linear':
                self.alphas[customer] = 0
                self.betas[customer] = rd.randint(1, 5)
            else:
                exit('Invalid value for parameter replenishment type')

        # Create gammmas and deltas
        self.gammas = {}
        self.deltas = {}
        for customer in self.customers:
            if specs.loc['absorption type']['value'] == 'everything':
                self.gammas[customer] = 1
                self.deltas[customer] = 0
            elif specs.loc['absorption type']['value'] == 'linear':
                    self.gammas[customer] = 0
                    self.deltas[customer] = rd.randint(1, 5)
            else:
                exit('Invalid value for parameter absorption type')

        # Create start values
        self.starts = {}
        for customer in self.customers:
            if specs.loc['starting demand']['value'] == 'lower':
                self.starts[customer] = 1
            elif specs.loc['starting demand']['value'] == 'upper':
                self.starts[customer] = 10
            else:
                exit('Invalid value for parameter starting demand')

        # Create lower bounds
        self.lowers = {}
        for customer in self.customers:
            self.lowers[customer] = 1

        # Create upper bounds
        self.uppers = {}
        for customer in self.customers:
            if specs.loc['upper demand']['value'] == '10':
                self.uppers[customer] = 10
            elif specs.loc['upper demand']['value'] == 'inf':
                self.uppers[customer] = 10 * 2 ** number_periods
            else:
                exit('Invalid value for parameter upper demand')

        '''
        for customer in self.customers:
            self.alphas[customer] = 100
            self.gammas[customer] = 100
            self.deltas[customer] = 100 # self.deltas[customer] / 2
            self.betas[customer] = 1 # 2 * self.deltas[customer]
        '''

        '''
        for customer in self.customers:
            self.gammas[customer] = self.alphas[customer]
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

    def validate_instance(self):
        # Validate stored instance

        # Check if customers have at least one location in the catalog
        for customer in self.customers:
            if sum([self.catalogs[location][customer] for location in self.locations]) == 0:
                raise Exception('Customer {} has no location in the catalog'.format(customer))
        pass


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
            print('\t| {}: {}'.format(location, self.capturable_from(location)))

        pass

    def capturable_from(self, location):
        # Retrieve capturable customers from some location

        return [customer for customer in self.customers if self.catalogs[location][customer] == 1]