import instance as ic
import pandas as pd

class slovakia(ic.instance):

    def __init__(self, keyword, project):

        super().__init__(keyword, project)

    def create_instance(self, folder = 'instances/slovakia'):
        # Create slovakia instances

        # number_periods = 12
        number_periods = 6
        # population_threshold = 13
        population_threshold = 80
        distance_threshold = 50

        # Create input sets
        self.locations = []
        self.customers = []
        self.periods = [str(period + 1) for period in range(0, number_periods)]

        # Create parameters
        self.alphas = {}
        self.betas = {}
        self.starts = {}

        try:
            # Read specifications from file
            content = pd.read_csv('{}/csv/nodes.csv'.format(folder))

        except:
            print('No file found for slovakia dataset')

        for _, row in content.iterrows():

            customer = str(row['id'])
            self.customers.append(customer)
            if row['residential_population'] >= population_threshold:
                self.locations.append(customer)
            self.starts[customer] = 0
            self.alphas[customer] = 0
            self.betas[customer] = row['residential_population'] / number_periods

        self.distances = {}
        for customer1 in self.customers:
            self.distances[customer1] = {}
            for customer2 in self.customers:
                self.distances[customer1][customer2] = 0.

        with open ('{}/csv/Dmatrix.txt'.format(folder), 'r') as content:
            content.readline()
            content.readline()
            customer1 = 1
            customer2 = 1
            for line in content:
                self.distances[str(customer1)][str(customer2)] = float(line.strip())
                customer2 += 1
                if customer2 == len(self.customers) + 1:
                    customer2 = 1
                    customer1 += 1

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if self.distances[location][customer] <= distance_threshold else 0.

        # Create rewards
        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                self.rewards[period][location] = 1.