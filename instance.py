import json as js
import numpy as np
import pandas as pd
import common as cm
from ctypes import *
# c_int, c_float, cdll, pointer
import gurobipy as gp

class instance:

    def __init__(self, keyword):

        # Initiate instance class

        '''
            Mandatory attributes:

            - self.locations: list of locations
            - self.customers: list of customers
            - self.periods: list of periods
            - self.facilities: list of facilities

            - self.catalogs: preference rules
            - self.rewards: location rewards
            - self.spawning: spawning demand
            - self.accumulated: accumulated demand
            - self.penalties: customer penalties
        '''

        # Store instance keyword
        self.keyword = keyword

        # Store parameters
        self.parameters = {}

        # Set random seed
        self.parameters['seed'] = 0

        # Set start period
        self.start = 0

        # Apply generator
        self.create_instance()

        # Set final period
        self.final = len(self.periods) + 1
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

        self.captured_locations = {}
        for customer in self.customers:
            self.captured_locations[customer] = [location for location in self.locations if self.catalogs[location][customer] == 1]

        self.captured_customers = {}
        for location in self.locations:
            self.captured_customers[location] = [customer for customer in self.customers if self.catalogs[location][customer] == 1]

        # Set proper big M values
        self.limits = {}
        for period in self.periods:
            self.limits[period] = {}
            for customer in self.customers:
                limit = self.accumulated[self.start][period][customer]
                self.limits[period][customer] = np.ceil(limit)

        # Compute coefficients
        with open('coefficients/{}.csv'.format(keyword), 'w') as content:
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
                                    self.coefficients[period1][period2][location][customer] = self.rewards[period2][location] * self.accumulated[period1][period2][customer]
                                else:
                                    self.coefficients[period1][period2][location][customer] = 0.
                                self.coefficients[period1][period2][location][customer] -= self.penalties[customer] * sum(self.spawning[period3][customer] for period3 in self.periods if period3 > period1 and period3 < period2)
                                content.write('{}, {}, {}, {}, {}\n'.format(period1, period2, location, customer, self.coefficients[period1][period2][location][customer]))

        # Prepare proper ctypes

        self.c_nb_locations = c_int(len(self.locations))
        self.c_nb_customers = c_int(len(self.customers))
        self.c_nb_periods = c_int(len(self.periods))

        self.c_dt_catalogs = (c_int * (len(self.locations) * len(self.customers)))()
        for location in self.locations:
            for customer in self.customers:
                self.c_dt_catalogs[(int(location) - 1) * len(self.customers) + int(customer) - 1] = c_int(self.catalogs[location][customer])

        self.c_dt_coefficients = (c_float * (len(self.periods_with_start) * len(self.periods_with_final) * len(self.locations) * len(self.customers)))()
        for period1 in self.periods_with_start:
            for period2 in self.periods_with_final:
                for location in self.locations:
                    for customer in self.customers:
                        self.c_dt_coefficients[(
                            (int(period1) - 0) * len(self.periods_with_final) * len(self.locations) * len(self.customers) + 
                            (int(period2) - 1) * len(self.locations) * len(self.customers) + 
                            (int(location) - 1) * len(self.customers) + 
                            (int(customer) - 1)
                        )] = c_float(self.coefficients[period1][period2][location][customer] if period1 < period2 and customer in self.captured_customers[location] else -10 ** 8)

    def print_instance(self):
        # Print stored instance

        print('Keyword: <{}>'.format(self.keyword))

        print('Penalties: {}'.format(self.penalties.values()))

        print('Facilities: {}'.format(self.facilities.values()))

        print('Customers: {}'.format(self.customers))
        print('\t| j: #\t[I]')
        for customer in self.customers:
            print('\t| {}: {}\t{}'.format(
                customer,
                len(self.captured_locations[customer]),
                self.captured_locations[customer] if len(self.locations) <= 100 else '[...]'))
            print('\t\t{}'.format([self.spawning[period][customer] for period in self.periods]))

        print('Locations: {}'.format(self.locations))
        print('\t| i: #\t[J]')
        for location in self.locations:
            print('\t| {} ({}) : {}'.format(
                location,
                self.rewards[self.start + 1][location],
                self.captured_customers[location] if len(self.customers) <= 100 else len(self.captured_customers[location])))

    def evaluate_solution(self, solution):

        objective = 0.

        latest = {customer: self.start for customer in self.customers}

        for period, locations in solution.items():
            if len(locations) > 0.:
                for customer in self.customers:
                    reward = - 1 * gp.GRB.INFINITY
                    captured = False
                    for location in locations:
                        if location in self.captured_locations[customer]:
                            captured = True
                            reward = max(reward, self.rewards[period][location] * self.accumulated[latest[customer]][period][customer])
                    if captured:
                        latest[customer] = period
                        objective += reward
                    else:
                        objective -= self.penalties[customer] * self.spawning[period][customer]
                        # penalty = self.penalties[customer] * self.spawning[period][customer]
            else:
                for customer in self.customers:
                    objective -= self.penalties[customer] * self.spawning[period][customer]

        return objective

    def evaluate_customer(self, solution, customer, from_period = 0):

        objective = 0.

        latest = from_period

        for period, locations in solution.items():
            if period > from_period:
                if len(locations) > 0.:
                    reward = - 1 * gp.GRB.INFINITY
                    captured = False
                    for location in locations:
                        if location in self.captured_locations[customer]:
                            captured = True
                            reward = max(reward, self.rewards[period][location] * self.accumulated[latest][period][customer])
                    if captured:
                        latest = period
                        objective += reward
                    else:
                        objective -= self.penalties[customer] * self.spawning[period][customer]
                        # penalty = self.penalties[customer] * self.spawning[period][customer]
                else:
                    objective -= self.penalties[customer] * self.spawning[period][customer]

        return objective

    def copy_solution(self, solution):

        return {period : location for period, location in solution.items()}

    def empty_solution(self):

        return {period: [] for period in self.periods}

    def insert_solution(self, solution, period, location):

        inserted = self.copy_solution(solution)

        for reference in inserted.keys():
            previous = reference - 1
            if reference > period:
                inserted[reference] = solution[previous]

        inserted[period] = location

        return inserted

    def format_solution(self, variables):
        # Format model solution as dictionary

        solution = self.empty_solution()

        for period in self.periods:
            solution[period] = []
            for location in self.locations:
                value = variables[period, location].x
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
            solution[period] = text[index].split('~')
            index += 1

        return solution