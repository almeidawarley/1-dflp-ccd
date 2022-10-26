import random as rd

class instance:

    def __init__(self):
        # Initiate instance class

        # Original = 100
        rd.seed(10)

        # Create random instance
        self.create_random()
        # self.create_example()

        # Validate stored instance
        self.validate_instance()

        # Print stored instance
        self.print_instance()

    def create_random(self):
        # Create random instance

        # Set instance size
        number_locations = 5
        number_customers = 10
        number_periods = 6

        self.locations = [str(i+1) for i in range(number_locations)]
        self.customers = [str(i+1) for i in range(number_customers)]
        self.periods = [str(i+1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = rd.choices([0,1])[0]

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1 # rd.randint(30,50)

        # Create alphas
        self.alphas = {}
        for customer in self.customers:
            self.alphas[customer] = 0 # rd.randint(30,50)

        # Create betas
        self.betas = {}
        for customer in self.customers:
            self.betas[customer] = 5 # rd.randint(30,50)

        # Create gammmas
        self.gammas = {}
        for customer in self.customers:
            self.gammas[customer] = 1 # rd.randint(30,50)

        # Create deltas
        self.deltas = {}
        for customer in self.customers:
            self.deltas[customer] = 0 # rd.randint(30,50)

        # Create lower bounds
        self.lowers = {}
        for customer in self.customers:
            self.lowers[customer] = 0 # rd.randint(30,50)

        # Create upper bounds
        self.uppers = {}
        for customer in self.customers:
            self.uppers[customer] = 10 # rd.randint(30,50)

        # Create start values
        self.starts = {}
        for customer in self.customers:
            self.starts[customer] = rd.randint(0,10)

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

        # Create lower bounds
        self.lowers = {}
        for customer in self.customers:
            self.lowers[customer] = -10

        # Create upper bounds
        self.uppers = {}
        for customer in self.customers:
            self.uppers[customer] = 50

        # Create start values
        self.starts = {}
        self.starts['A'] = 15.
        self.starts['B'] = 26.
        self.starts['C'] = 5.

    def validate_instance(self):
        # Validate stored instance

        # Check if customers have at least one location in the catalog
        for customer in self.customers:
            if sum([self.catalogs[location][customer] for location in self.locations]) == 0:
                raise Exception('Customer {} has no location in the catalog'.format(customer))
        pass


    def print_instance(self):
        # Print stored instance

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