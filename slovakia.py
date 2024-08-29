import instance as ic
import pandas as pd
import numpy as np
# import networkx as nx
import json as js

class slovakia(ic.instance):

    def __init__(self, keyword, project):

        super().__init__(keyword, project)

    def create_instance(self, folder = 'instances/slovakia'):
        # Create slovakia instances

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            print('No file found for keyword {}'.format(self.keyword))

        # Update folder based on map
        folder = '{}/{}'.format(folder, self.parameters['map'])

        np.random.seed(self.parameters['seed'])

        number_periods = self.parameters['periods']
        distance_threshold = self.parameters['distance']

        # Create input sets
        self.locations = []
        self.customers = []
        self.periods = [int(i + 1) for i in range(number_periods)]

        try:
            # Read specifications from file
            content = pd.read_csv('{}/csv/nodes.csv'.format(folder))

        except:
            print('No file found for slovakia dataset')

        # Create amplitude
        self.amplitudes = {}

        number_locations = int(np.ceil(0.01 * len(content)))
        population_threshold = content['residential_population'].nlargest(number_locations).iloc[-1]

        for _, row in content.iterrows():

            customer = str(row['id'])
            if row['type'] == 'dp' and row['residential_population'] > 0:
                self.customers.append(customer)
                if row['residential_population'] >= population_threshold:
                    self.locations.append(customer)
                self.amplitudes[customer] = row['residential_population']

        self.distances = {}
        if self.parameters['map'] in ['pa', 'ke']:
            for location in self.locations:
                self.distances[location] = {}
                for customer in self.customers:
                    self.distances[location][customer] = 0.
            with open ('{}/csv/Dmatrix.txt'.format(folder), 'r') as content:
                content.readline()
                content.readline()
                customer1 = 1
                customer2 = 1
                for line in content:
                    try:
                        self.distances[str(customer1)][str(customer2)] = float(line.strip())
                    except:
                        pass
                    customer2 += 1
                    if customer2 == len(self.customers) + 1:
                        customer2 = 1
                        customer1 += 1

        elif self.parameters['map'] in ['sr', 'za']:
            graph = nx.DiGraph()
            with open ('{}/csv/nodes.csv'.format(folder), 'r') as content:
                content.readline()
                for line in content:
                    node, _, _, _, _ = line.strip().split(',')
                    graph.add_node(customer)
            with open ('{}/csv/edges.csv'.format(folder), 'r') as content:
                content.readline()
                for line in content:
                    origin, destination, distance, _, direction, _ = line.strip().split(',')
                    graph.add_edge(origin, destination, weight = distance)
                    if direction != 'yes':
                        graph.add_edge(destination, origin, weight = distance)
            for location in self.locations:
                self.distances[location] = {}
                print('location: {} / {}'.format(location, self.locations))
                for customer in self.customers:
                    try:
                        self.distances[location][customer] = nx.shortest_path_length(graph, source = customer, target = location, method='dijkstra')
                    except Exception as e:
                        print(e, end = '_')
                        self.distances[location][customer] = 10**10
        else:
            exit('Wrong value for map parameter')

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                # print( self.distances[location][customer])
                self.catalogs[location][customer] = np.random.choice([0, 1], p = [0.05, 0.95]) * (1 if self.distances[location][customer] <= distance_threshold else 0)
                # self.catalogs[location][customer] = (1 if self.distances[location][customer] <= distance_threshold else 0)

        for customer in self.customers:
            if sum([self.catalogs[location][customer] for location in self.locations]) == 0:
                print('Warning: Targeted customer {} not covered by candidate locations'.format(customer))

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

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                if self.parameters['demands'] == 'constant':
                    self.spawning[period][customer] = self.amplitudes[customer]
                elif self.parameters['demands'] == 'seasonal':
                    self.spawning[period][customer] = (self.amplitudes[customer] / 2) * np.cos(period) + (self.amplitudes[customer] / 2)
                else:
                    exit('Wrong value for demand behaviour')
                self.spawning[period][customer] = np.ceil(self.spawning[period][customer])