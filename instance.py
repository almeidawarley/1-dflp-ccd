import json as js
import numpy as np
import pandas as pd
import common as cm
from ctypes import *
# c_int, c_float, cdll, pointer

class instance:

    def __init__(self, keyword, project):
        # Initiate instance class

        '''
            Mandatory attributes:

            - self.locations: list of locations
            - self.customers: list of customers
            - self.periods: list of periods
            - self.facilities: list of facilities
            - self.penalization: penalization factor

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
            self.captured_locations[customer] = [location for location in self.locations if self.catalogs[location][customer] == 1]

        self.captured_customers = {}
        self.captured_customers[self.depot] = []
        for location in self.locations:
            self.captured_customers[location] = [customer for customer in self.customers if self.catalogs[location][customer] == 1]

        # Set proper big M values
        self.limits = {}
        for period in self.periods:
            self.limits[period] = {}
            for customer in self.customers:
                limit = self.accumulated[self.start][period][customer]
                self.limits[period][customer] = np.ceil(limit)

        # Prepare proper ctypes

        '''
        self.c_nb_locations = c_int(len(self.locations))
        self.c_nb_customers = c_int(len(self.customers))
        self.c_nb_periods = c_int(len(self.periods))

        self.c_dt_catalogs = (c_int * (len(self.locations) * len(self.customers)))()

        for location in self.locations:
            for customer in self.customers:
                self.c_dt_catalogs[(int(location) - 1) * len(self.customers) + int(customer) - 1] = c_int(self.catalogs[location][customer])

        self.c_dt_rewards = (c_float * (len(self.periods) * len(self.locations)))()

        for period in self.periods:
            for location in self.locations:
                self.c_dt_rewards[(int(period) - 1) * len(self.locations) + int(location) - 1] = self.rewards[period][location]

        self.c_dt_accumulated = (c_int * (len(self.periods_with_start) * len(self.periods) * len(self.customers)))()

        for period1 in self.periods_with_start:
            for period2 in self.periods:
                for customer in self.customers:
                    self.c_dt_accumulated[int(period1) * len(self.periods) * len(self.customers) + (int(period2) - 1)* len(self.customers) + int(customer) - 1] = int(self.accumulated[period1][period2][customer]) if period1 < period2 else 0
        '''

    def print_instance(self):
        # Print stored instance

        print('Keyword: <{}>'.format(self.keyword))

        print('Penalization: {}'.format(self.penalization))

        print('Facilities: {}'.format(self.facilities[self.start + 1]))

        print('Customers: {}'.format(self.customers))
        print('\t| j: #\t[I]')
        for customer in self.customers:
            print('\t| {}: {}\t{}'.format(
                customer,
                len(self.captured_locations[customer]),
                self.captured_locations[customer] if len(self.locations) <= 100 else '[...]'))

        print('Locations: {}'.format(self.locations))
        print('\t| j: #\t[J]')
        for location in self.locations:
            print('\t| {} ({}) : {}'.format(
                location,
                self.rewards[self.start + 1][location],
                self.captured_customers[location] if len(self.customers) <= 100 else len(self.captured_customers[location])))

    def evaluate_solution(self, solution):

        objective = 0.

        latest = {customer: self.start for customer in self.customers}

        for period, locations in solution.items():
            if locations != [self.depot]:
                for customer in self.customers:
                    marginal = - 1 * cm.INFINITY
                    captured = False
                    for location in locations:
                        if location in self.captured_locations[customer]:
                            captured = True
                            marginal = max(marginal, self.rewards[period][location] * self.accumulated[latest[customer]][period][customer])
                    if captured:
                        latest[customer] = period
                        objective += marginal

        return objective

    def copy_solution(self, solution):

        return {period : location for period, location in solution.items()}

    def empty_solution(self):

        return {period: [self.depot] for period in self.periods}

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
            solution[period] = []
            for location in self.locations:
                value = variable[period, location].x
                if cm.is_equal_to(value, 1.):
                    solution[period].append(location)

        return solution

    def pack_solution(self, solution):
        # Format dictionary solution as text

        formatted = list(solution.values())

        for index, _ in enumerate(formatted):
            formatted[index] = '~'.join(formatted[index])

        return '-'.join(formatted)

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