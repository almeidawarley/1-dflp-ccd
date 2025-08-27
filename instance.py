from ctypes import *
import common as cm
import gurobipy as gp

class instance:

    def __init__(self, keyword):

        '''
            Mandatory attributes:

            - self.locations: list of locations
            - self.customers: list of customers
            - self.periods: list of periods

            - self.facilities: number of facilities
            - self.catalogs: preference rules
            - self.rankings: preference rankings
            - self.coefficients: objective function
        '''

        # Initiate standard attributes
        self.keyword = keyword
        self.parameters = {}
        self.parameters['seed'] = 0

        # Apply some generator
        self.create_instance()

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

        # Write coefficients to file
        with open('coefficients/{}.csv'.format(self.keyword), 'w') as content:
            for period1 in self.periods_with_start:
                for period2 in self.periods_with_final:
                    if period1 < period2:
                        for location in self.locations:
                            for customer in self.captured_customers[location]:
                                content.write('{}, {}, {}, {}, {}\n'.format(period1, period2, location, customer, self.coefficients[period1][period2][location][customer]))

        # Print instance summary
        print('Keyword: {}'.format(self.keyword))
        print('Facilities: {}'.format([number for number in self.facilities.values()]))

        # Print customer information
        print('Customers: {}'.format(self.customers))
        print('\t| j: #\t[I]')
        for customer in self.customers:
            print('\t| {}: {}\t{}'.format(
                customer,
                len(self.captured_locations[customer]),
                self.captured_locations[customer][:50]))
            print('\t\t{}'.format([self.rankings[customer][location] for location in self.captured_locations[customer]]))
            print('\t\t{}'.format([self.spawning[period][customer] for period in self.periods]))

        # Print location information
        print('Locations: {}'.format(self.locations))
        print('\t| i: #\t[J]')
        for location in self.locations:
            print('\t| {} ({}) : {}\t{}'.format(
                location,
                self.rewards[location],
                len(self.captured_customers[location]),
                self.captured_customers[location][:50]))

        print('Coefficients at coefficients/{}.csv'.format(self.keyword))

    def evaluate_solution(self, solution):

        # Evaluate objective value of a solution
        objective = 0.

        latest = {customer: self.start for customer in self.customers}

        # Parse regular periods for rewards
        for period, locations in solution.items():
            for customer in self.customers:
                preference_ranking = 0
                for location in locations:
                    if location in self.captured_locations[customer]:
                        if self.rankings[customer][location] > preference_ranking:
                            preference_ranking = self.rankings[customer][location]
                            preference_location = location
                if preference_ranking != 0:
                    # print('Customer {} caught at period {}'.format(customer, period))
                    objective += self.coefficients[latest[customer]][period][preference_location][customer]
                    latest[customer] = period

        # Parse final period for penalties
        for customer in self.customers:
            reward = - 1 * gp.GRB.INFINITY
            for location in self.captured_locations[customer]:
                reward = max(reward, self.coefficients[latest[customer]][self.final][location][customer])
            objective += reward

        return objective

    def evaluate_solution2(self, solution):

        # Evaluate objective value of a solution
        objective = 0.
        reward = 0.
        penalty = 0.

        try:
            self.penalties
        except:
            self.penalties = {customer: 0. for customer in self.customers}

        latest = {customer: self.start for customer in self.customers}

        # Parse regular periods for rewards
        for period, locations in solution.items():
            for customer in self.customers:
                preference_ranking = 0
                for location in locations:
                    if location in self.captured_locations[customer]:
                        if self.rankings[customer][location] > preference_ranking:
                            preference_ranking = self.rankings[customer][location]
                            preference_location = location
                if preference_ranking != 0:
                    # print('Customer {} caught at period {}'.format(customer, period))
                    objective += self.coefficients[latest[customer]][period][preference_location][customer]
                    reward += self.coefficients_reward[latest[customer]][period][preference_location][customer]
                    penalty += self.coefficients_penalty[latest[customer]][period][preference_location][customer]
                    latest[customer] = period

        # Parse final period for penalties
        for customer in self.customers:
            preference_objective = - 1 * gp.GRB.INFINITY
            preference_location = 0
            for location in self.captured_locations[customer]:
                if self.coefficients[latest[customer]][self.final][location][customer] > preference_objective:
                    preference_objective = self.coefficients[latest[customer]][self.final][location][customer]
                    preference_location = location
            objective += preference_objective
            reward += self.coefficients_reward[latest[customer]][self.final][preference_location][customer]
            penalty += self.coefficients_penalty[latest[customer]][self.final][preference_location][customer]

        # print('Objective: {}'.format(objective))
        # print('Reward: {}'.format(reward))
        # print('Penalty: {}'.format(penalty))
        assert objective == reward - penalty

        return reward, penalty

    def evaluate_customer(self, solution, customer, from_period = 0):

        # Evaluate objective value of a solution
        objective = 0.

        # For some customer, and from a certain period
        latest = from_period

        # Parse regular periods for rewards
        for period, locations in solution.items():
            if period > from_period:
                captured = False
                reward = - 1 * gp.GRB.INFINITY
                for location in locations:
                    if location in self.captured_locations[customer]:
                        captured = True
                        reward = max(reward, self.coefficients[latest][period][location][customer])
                if captured:
                    latest = period
                    objective += reward

        # Parse final period for penalties
        reward = - 1 * gp.GRB.INFINITY
        for location in self.captured_locations[customer]:
            reward = max(reward, self.coefficients[latest][self.final][location][customer])
        objective += reward

        return objective

    def evaluate_customer2(self, solution, customer, from_period = 0):

        # Evaluate number of captures in a solution
        captures = 0

        # For some customer, and from a certain period
        latest = from_period

        # Parse regular periods for rewards
        for period, locations in solution.items():
            if period > from_period:
                captured = False
                reward = - 1 * gp.GRB.INFINITY
                for location in locations:
                    if location in self.captured_locations[customer]:
                        captured = True
                if captured:
                    captures += 1

        return captures

    def copy_solution(self, solution):

        # Create a hard copy of the solution
        return {period : location for period, location in solution.items()}

    def empty_solution(self):

        # Create an empty solution
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