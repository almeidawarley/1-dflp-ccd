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
            self.bigM[customer] = self.uppers[customer]

    def create_random(self, folder = 'instances'):
        # Create random instance

        try:
            # Read specifications from file
            specs = pd.read_csv('{}/{}.csv'.format(folder, instance.keyword), index_col = 0)
        except:
            specs = pd.read_csv('server/{}/{}.csv'.format(folder, instance.keyword), index_col = 0)

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
        for customer in self.customers:

            if specs.loc['willingness to patronize']['value'] == 'low':
                subsets[customer] = rd.sample(self.locations, rd.randint(1, 3))
            elif specs.loc['willingness to patronize']['value'] == 'medium':
                subsets[customer] = rd.sample(self.locations, rd.randint(4, 6))
            elif specs.loc['willingness to patronize']['value'] == 'high':
                subsets[customer] = rd.sample(self.locations, rd.randint(7, 9))
            else:
                exit('Invalid value for parameter willingness to patronize')

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location in subsets[customer] else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                if specs.loc['location revenues']['value'] == 'equal':
                    self.revenues[period][location] =  1 # rd.randint(30,50)
                elif specs.loc['location revenues']['value'] == 'different':
                    self.revenues[period][location] = rd.randint(5,15) / 10. if period == '1' else self.revenues[str(int(period) - 1)][location]
                else:
                    exit('Invalid value for parameter location revenues')

        # Create alphas
        self.alphas = {}
        for customer in self.customers:
            if specs.loc['replenishment type']['value'] == 'linear':
                self.alphas[customer] = 0
            elif specs.loc['replenishment type']['value'] == 'exponential':
                if specs.loc['replenishment variability']['value'] == 'low':
                    self.alphas[customer] = rd.randint(4,6) / 10.
                elif specs.loc['replenishment variability']['value'] == 'medium':
                    self.alphas[customer] = rd.randint(3,7) / 10.
                elif specs.loc['replenishment variability']['value'] == 'high':
                    self.alphas[customer] = rd.randint(2,8) / 10.
                else:
                    exit('Invalid value for parameter replenishment variability')
            else:
                exit('Invalid value for parameter replenishment type')

        # Create betas
        self.betas = {}
        for customer in self.customers:
            if specs.loc['replenishment type']['value'] == 'exponential':
                self.betas[customer] = 0
            elif specs.loc['replenishment type']['value'] == 'linear':
                if specs.loc['replenishment variability']['value'] == 'low':
                    self.betas[customer] = rd.randint(4,6)
                elif specs.loc['replenishment variability']['value'] == 'medium':
                    self.betas[customer] = rd.randint(3,7)
                elif specs.loc['replenishment variability']['value'] == 'high':
                    self.betas[customer] = rd.randint(2,8)
                else:
                    exit('Invalid value for parameter replenishment variability')
            else:
                exit('Invalid value for parameter replenishment type')

        # Create gammmas
        self.gammas = {}
        for customer in self.customers:
            if specs.loc['absorption type']['value'] == 'linear':
                self.gammas[customer] = 0
            elif specs.loc['absorption type']['value'] == 'exponential':
                if specs.loc['absorption variability']['value'] == 'low':
                    self.gammas[customer] = rd.randint(4,6) / 10.
                elif specs.loc['absorption variability']['value'] == 'medium':
                    self.gammas[customer] = rd.randint(3,7) / 10.
                elif specs.loc['absorption variability']['value'] == 'high':
                    self.gammas[customer] = rd.randint(2,8) / 10.
                else:
                    exit('Invalid value for parameter absorption variability')
            else:
                exit('Invalid value for parameter absorption type')

        # Create deltas
        self.deltas = {}
        for customer in self.customers:
            if specs.loc['absorption type']['value'] == 'exponential':
                self.deltas[customer] = 0
            elif specs.loc['absorption type']['value'] == 'linear':
                if specs.loc['absorption variability']['value'] == 'low':
                    self.deltas[customer] = rd.randint(4,6)
                elif specs.loc['absorption variability']['value'] == 'medium':
                    self.deltas[customer] = rd.randint(3,7)
                elif specs.loc['absorption variability']['value'] == 'high':
                    self.deltas[customer] = rd.randint(2,8)
                else:
                    exit('Invalid value for parameter absorption variability')
            else:
                exit('Invalid value for parameter absorption type')

        # Create start values
        self.starts = {}
        for customer in self.customers:
            if specs.loc['starting demand']['value'] == 'low':
                self.starts[customer] = rd.randint(4,6)
            elif specs.loc['starting demand']['value'] == 'medium':
                self.starts[customer] = rd.randint(3,7)
            elif specs.loc['starting demand']['value'] == 'high':
                self.starts[customer] = rd.randint(2,8)
            else:
                exit('Invalid value for parameter starting demand')

        # Create lower bounds
        self.lowers = {}
        for customer in self.customers:
            self.lowers[customer] = 0

        # Create upper bounds
        self.uppers = {}
        for customer in self.customers:
            self.uppers[customer] = 10

        '''
        for customer in self.customers:
            self.alphas[customer] = 0
            self.gammas[customer] = 0
            self.betas[customer] = 0
            self.deltas[customer] = 10
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
            self.lowers[customer] = 0

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