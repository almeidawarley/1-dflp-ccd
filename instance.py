import json as js
import numpy as np
import pandas as pd
import common as cm

class instance:

    def __init__(self, keyword, project):
        # Initiate instance class

        '''
            Mandatory attributes:

            - self.locations: list of locations
            - self.customers: list of customers
            - self.periods: list of periods

            - self.catalogs: preference rules
            - self.rewards: location rewards
            - self.spawning: spawning demand
            - self.accumulated: accumulated demand
        '''

        # Store instance keyword
        self.keyword = keyword

        # Store project keyword
        self.project = project

        # Store parameters
        self.parameters = {}

        # Set random seed
        self.parameters['seed'] = 0

        # Apply generator
        self.create_instance()

        # Set start/finish
        self.start = 0
        self.finish = len(self.periods) + 1
        self.periods_with_start = [self.start] + [period for period in self.periods]
        self.periods_with_end = [period for period in self.periods] + [self.finish]
        self.periods_extended = [self.start] + [period for period in self.periods] + [self.finish]

        # Set depot info
        self.depot = '0'
        self.locations_extended = [self.depot] + self.locations

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

        self.captured_locations = {}
        for customer in self.customers:
            self.captured_locations[customer] = self.attended_locations(customer)

        self.captured_customers = {}
        self.captured_customers[self.depot] = []
        for location in self.locations:
            self.captured_customers[location] = self.served_customers(location)

        # Set proper big M values
        self.limits = {}
        for period in self.periods:
            self.limits[period] = {}
            for customer in self.customers:
                limit = self.accumulated[self.start][period][customer]
                self.limits[period][customer] = np.ceil(limit)

    def print_instance(self):
        # Print stored instance

        print('Keyword: <{}>'.format(self.keyword))

        print('Customers: {}'.format(self.customers))
        print('\t| j: #\t[L]')
        for customer in self.customers:
            print('\t| {}: {}\t{}'.format(
                customer,
                len(self.attended_locations(customer)),
                self.attended_locations(customer) if self.keyword != 'slovakia' else '[..]'))

        print('Locations: {}'.format(self.locations))
        for location in self.locations:
            print('\t| {} ({}) : {}'.format(location, self.rewards[self.start + 1][location], self.served_customers(location) if self.keyword != 'slovakia' else len(self.served_customers(location))))

    def served_customers(self, location):
        # Retrieve customers captured by some location

        return [customer for customer in self.customers if self.catalogs[location][customer] == 1]

    def attended_locations(self, customer):
        # Retrieve locations capturing some customer

        return [location for location in self.locations if self.catalogs[location][customer] == 1]

    def evaluate_solution(self, solution):

        objective = 0.

        lastly = {customer: self.start for customer in self.customers}

        for period, location in solution.items():
            for customer in self.customers:
                if location != self.depot and self.catalogs[location][customer] == 1:
                    objective += self.rewards[period][location] * self.accumulated[lastly[customer]][period][customer]
                    lastly[customer] = period

        return round(objective, 2)

    def copy_solution(self, solution):

        return {period : location for period, location in solution.items()}

    def empty_solution(self):

        return {period: self.depot for period in self.periods}

    def insert_solution(self, solution, period, location):

        inserted = self.copy_solution(solution)

        for reference in inserted.keys():
            previous = reference - 1
            if reference > period:
                inserted[reference] = solution[previous]

        inserted[period] = location

        return inserted

    def format_solution(self, variable):
        # Format model solution as dictionary

        solution = self.empty_solution()

        for period in self.periods:
            for location in self.locations:
                value = variable[period, location].x
                if cm.is_equal_to(value, 1.):
                    solution[period] = location

        return solution

    def pack_solution(self, solution):
        # Format dictionary solution as text

        return '-'.join(solution.values())

    def unpack_solution(self, text):
        # Format text solution as dictionary

        solution = self.empty_solution()
        text = text.strip().split('-')

        assert len(text) == len(self.periods)

        index = 0

        for period in self.periods:
            solution[period] = text[index]
            index += 1

        return solution

    def stable_solution(self, location):

        return {period: location for period in self.periods}