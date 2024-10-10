
import gurobipy as gp
import common as cm
from ctypes import *
#c_int, c_float, cdll, pointer

class subproblem:

    def __init__(self, instance, customer):

        self.ins = instance
        self.customer = customer
        self.solution = self.ins.empty_solution()
        self.variable = {}
        self.counter = 0
        self.uncaptured = '-'

        # Create empty inequality
        self.inequality = {}
        self.inequality['b'] = 0.
        self.inequality['y'] = {}
        for period in self.ins.periods:
            self.inequality['y'][period] = {}
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = 0.

    def update(self, solution, variable = {}):

        self.solution = solution
        self.variable = variable

class analytical(subproblem):

    def __init__(self, instance, customer):

        super().__init__(instance, customer)

        # Create primal solution
        self.primal_solution = {}
        for period in self.ins.periods_with_start:
            self.primal_solution[period] = self.ins.finish

        # Create dual solution
        self.dual_solution = {}
        self.dual_solution['q'] = {}
        self.dual_solution['p'] = {}
        self.dual_solution['o'] = {}
        for period in self.ins.periods_with_start:
            self.dual_solution['q'][period] = 0.
        for period in self.ins.periods:
            self.dual_solution['p'][period] = {}
            self.dual_solution['o'][period] = {}
            for location in self.ins.captured_locations[self.customer]:
                self.dual_solution['p'][period][location] = 0.
                self.dual_solution['o'][period][location] = 0.

    def cut(self):

        # Compute patronization pattern for customer
        patronization = {period: self.uncaptured for period in self.ins.periods}
        for period2 in self.ins.periods:
            if len(self.solution[period2]) > 0:
                location = self.uncaptured
                for other in self.solution[period2]:
                    if other in self.ins.captured_locations[self.customer] and (location == self.uncaptured or self.ins.rewards[period2][other] > self.ins.rewards[period2][location]):
                        location = other
                patronization[period2] = location

        # print('Patronization pattern for customer {}: {}'.format(self.customer, patronization))

        # Compute previous capture at each time period
        previouscap = {period: self.ins.start for period in self.ins.periods}
        for period2 in self.ins.periods:
            for period1 in reversed(self.ins.periods):
                if period1 < period2:
                    if patronization[period1] != self.uncaptured:
                        previouscap[period2] = period1
                        break

        # print('Previous capture pattern for customer {}: {}'.format(self.customer, previouscap))

        # Compute future capture at each time period
        futurecap = {period: self.ins.finish for period in self.ins.periods_with_start}
        for period1 in self.ins.periods_with_start:
            for period2 in self.ins.periods:
                if period1 < period2:
                    if patronization[period2] != self.uncaptured:
                        futurecap[period1] = period2
                        break

        # print('Future capture pattern for customer {}: {}'.format(self.customer, futurecap))

        dual_objective = 0.

        # Assign zero values to variables p^t_i
        for period2 in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.dual_solution['p'][period2][location] = 0.

        # Compute variables o^t_i for CAPTURED periods t
        for period2 in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                if patronization[period2] != self.uncaptured:
                    # Notation: period1 s, other k^t
                    period1 = previouscap[period2]
                    other = patronization[period2]
                    if other == location:
                        self.dual_solution['o'][period2][location] = 0.
                    else:
                        self.dual_solution['o'][period2][location] = max(
                            self.ins.coefficients[period1][period2][location][self.customer] -
                            self.ins.coefficients[period1][period2][other][self.customer], 0
                        )
                if self.dual_solution['o'][period2][location] > 0.:
                    pass # print('o^{}_{} = {} properly computed?'.format(period2, location, self.dual_solution['o'][period2][location]))

        # Compute variables q^l for CAPTURED periods
        for period1 in reversed(self.ins.periods_with_start):
            # Set baseline value, which does not vary with variables p^t_i
            self.dual_solution['q'][period1] = max(self.ins.coefficients[period1][self.ins.finish][location][self.customer] for location in self.ins.captured_locations[self.customer])
            # Compute esimated value, assuming variables p^t_i are zero
            for period2 in self.ins.periods:
                if period1 < period2 and patronization[period2] != self.uncaptured:
                    for location in self.ins.captured_locations[self.customer]:
                        other = patronization[period2] # Notation: k^t
                        period3 = previouscap[period2] # Notation: s
                        if location in self.solution[period2]:
                            self.dual_solution['q'][period1] = max(self.dual_solution['q'][period1], 
                                                                    self.ins.coefficients[period1][period2][location][self.customer] + 
                                                                    self.dual_solution['p'][period2][other] +
                                                                    self.dual_solution['q'][period2])
                        else:
                            self.dual_solution['q'][period1] = max(self.dual_solution['q'][period1], 
                                                                    self.ins.coefficients[period1][period2][location][self.customer] -
                                                                    self.ins.coefficients[period3][period2][location][self.customer] +
                                                                    self.ins.coefficients[period3][period2][other][self.customer] +
                                                                    self.dual_solution['p'][period2][other] +
                                                                    self.dual_solution['q'][period2])

            if period1 == self.ins.start or patronization[period1] != self.uncaptured:
                # Optimality check based on completementary slackness-ish
                offset = sum(self.dual_solution['p'][period2][location] for period2 in self.ins.periods for location in self.ins.captured_locations[self.customer])
                if self.dual_solution['q'][period1] - offset == self.ins.evaluate_customer(self.solution, self.customer, period1):
                    pass # print('q^{} = properly computed, moving forward'.format(period1, self.dual_solution['q'][period1]))
                else:
                    period2, location = futurecap[period1], patronization[futurecap[period1]]
                    # print('q^{} = {} not properly computed, changing p^{}_{}'.format(period1, self.dual_solution['q'][period1], period2, location))
                    self.dual_solution['p'][period2][location] = self.dual_solution['q'][period1] - offset - self.ins.evaluate_customer(self.solution, self.customer, period1)
                    # print('p^{}_{} = {} should be proper now!'.format(period2, location, self.dual_solution['p'][period2][location]))

        # Compute variables o^t_i for UNCAPTURED periods t (q^t required! could it be tigther actually?)
        for period2 in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                if patronization[period2] == self.uncaptured:
                    '''
                    self.dual_solution['o'][period2][location] = max(
                            self.ins.coefficients[period1][period2][location][self.customer] -
                            self.ins.coefficients[period1][self.ins.finish][location][self.customer] +
                            self.dual_solution['q'][period2]
                            for period1 in self.ins.periods_with_start if period1 < period2)
                    '''
                    self.dual_solution['o'][period2][location] = max(
                            self.ins.coefficients[period1][period2][location][self.customer] -
                            self.dual_solution['q'][period1] + self.dual_solution['q'][period2]
                            for period1 in self.ins.periods_with_start if period1 < period2)
                    self.dual_solution['o'][period2][location] = max(self.dual_solution['o'][period2][location], 0)

        # Build optimality cut
        for period in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = self.dual_solution['o'][period][location] - self.dual_solution['p'][period][location]
        self.inequality['b'] = self.dual_solution['q'][self.ins.start]

        '''
        import os
        if not os.path.exists('subprbms/{}'.format(self.counter)):
            os.makedirs('subprbms/{}'.format(self.counter))
        with open('subprbms/{}/ASP_customer_{}.sol'.format(self.counter, self.customer), 'w') as content:
            for period2 in self.ins.periods:
                for location in self.ins.captured_locations[self.customer]:
                    content.write('p~{}_{} {}\n'.format(period2, location, self.dual_solution['p'][period2][location]))
            for period1 in self.ins.periods_with_start:
                content.write('q~{} {}\n'.format(period1, self.dual_solution['q'][period1]))
            for period2 in self.ins.periods:
                for location in self.ins.captured_locations[self.customer]:
                    content.write('o~{}_{} {}\n'.format(period2, location, self.dual_solution['o'][period2][location]))
        '''

        dual_objective = self.dual_solution['q'][self.ins.start] - sum(self.dual_solution['p'][period2][location] for period2 in self.ins.periods for location in self.ins.captured_locations[self.customer])

        # print('Dual objective for customer {}, solution {}: {}'.format(self.customer, self.ins.pack_solution(self.solution), dual_objective))

        self.counter += 1

        return dual_objective, self.inequality

class external(subproblem):

    def __init__(self, instance, customer):

        super().__init__(instance, customer)

        self.sequence = (c_int * len(self.ins.periods))()
        self.dual_q = (c_float * (len(self.ins.periods_with_start)))()
        self.dual_p = (c_float * (len(self.ins.periods) * len(self.ins.locations)))()
        self.library = cdll.LoadLibrary('./libanalytical.so')

    def cut(self):

        # gcc -Wall -g -shared -o libanalytical.so -fPIC analytical.c

        # Update sequence
        for period in self.ins.periods:
            self.sequence[period - 1] = int(self.solution[period])

        # Call external implementation in C
        dual_objective = self.library.procedure(
            self.ins.c_nb_locations,
            self.ins.c_nb_customers,
            self.ins.c_nb_periods,
            byref(self.ins.c_dt_catalogs),
            byref(self.ins.c_dt_rewards),
            byref(self.ins.c_dt_accumulated),
            int(self.customer),
            byref(self.sequence),
            byref(self.dual_q),
            byref(self.dual_p),
            0
        )

        # Build optimality cut
        for period in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = self.dual_p[(int(period) - 1) * len(self.ins.locations) + int(location) - 1]
        self.inequality['b'] = self.dual_q[self.ins.start]

        return dual_objective, self.inequality

class duality(subproblem):

    def __init__(self, instance, customer):

        super().__init__(instance, customer)
        self.mip = gp.Model('DSFLP-C-DUAL{}'.format(customer))
        self.var = {}

        self.set_parameters()
        self.set_variables()
        self.set_objective()
        self.set_constraints()

    def cut(self):

        # Update solution
        self.set_objective()

        '''
        patronization = {period: '-' for period in self.ins.periods}
        for period2 in self.ins.periods:
            if len(self.solution[period2]) > 0:
                location = '-'
                for i in self.solution[period2]:
                    if i in self.ins.captured_locations[self.customer] and (location == '-' or self.ins.rewards[period2][i] > self.ins.rewards[period2][location]):
                        location = i
                patronization[period2] = location

        # Identified behaviour, this should be easy to prove
        pattern1 = self.mip.addConstrs(self.var['p'][period2, location] == 0 for period2 in self.ins.periods for location in self.ins.captured_locations[self.customer] if location not in self.solution[period2])
        # Complementary slackness, not need to elaborate
        pattern2 = self.mip.addConstrs(self.var['o'][period2, location] == 0 for period2 in self.ins.periods for location in self.ins.captured_locations[self.customer] if location in self.solution[period2] and patronization[period2] != location)
        # Not true due to complementary slackness, but true
        pattern3 = self.mip.addConstrs(self.var['o'][period2, location] == 0 for period2 in self.ins.periods for location in self.ins.captured_locations[self.customer] if location in self.solution[period2] and patronization[period2] == location)
        # Identified behaviour, this should be easy to prove
        pattern4 = self.mip.addConstrs(self.var['p'][period2, location] == 0 for period2 in self.ins.periods for location in self.ins.captured_locations[self.customer] if location in self.solution[period2] and patronization[period2] != location)
        '''

        # Solve dual program
        self.mip.optimize()

        '''
        import os
        if not os.path.exists('subprbms/{}'.format(self.counter)):
            os.makedirs('subprbms/{}'.format(self.counter))
        self.mip.write('subprbms/{}/DSP_customer_{}.sol'.format(self.counter, self.customer))
        self.mip.write('subprbms/{}/DSP_customer_{}.lp'.format(self.counter, self.customer))
        '''

        # Build optimality cut
        for period in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = self.var['o'][period, location].x - self.var['p'][period, location].x
        self.inequality['b'] = self.var['q'][self.ins.start].x

        '''
        self.mip.remove(pattern1)
        self.mip.remove(pattern2)
        self.mip.remove(pattern3)
        self.mip.remove(pattern4)
        '''

        self.counter += 1

        return self.mip.objVal, self.inequality

    def set_parameters(self):

        # Minimize dual objective
        self.mip.setAttr('ModelSense', 1)
        # Turn off GUROBI logs
        self.mip.setParam('OutputFlag', 0)
        # Constrain Gurobi to 1 thread
        self.mip.setParam('Threads', 1)
        # Set experimental time limit
        self.mip.setParam('TimeLimit', cm.TIMELIMIT)

    def set_variables(self):

        self.create_vrp()
        self.create_vrq()
        self.create_vro()

    def set_objective(self):

        if len(self.variable) > 0.:

            self.mip.setObjective(
                sum(
                    (
                        self.var['o'][period, location] -
                        self.var['p'][period, location]
                    ) *
                    self.variable[period, location]
                    for period in self.ins.periods
                    for location in self.ins.captured_locations[self.customer]
                ) + self.var['q'][self.ins.start]
            )

        else:

            self.mip.setObjective(
                sum(
                    (
                        self.var['o'][period, location] -
                        self.var['p'][period, location]
                    ) *
                    (1 if location in self.solution[period] else 0)
                    for period in self.ins.periods
                    for location in self.ins.captured_locations[self.customer]
                ) + self.var['q'][self.ins.start]
            )

    def set_constraints(self):

        self.create_c1()
        self.create_c2()

    def create_vrp(self):
        # Create p^{t}_{i} variables

        lowers = [0. for _ in self.ins.periods for _ in self.ins.locations]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.locations]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.locations]
        types = ['C' for _ in self.ins.periods for _ in self.ins.locations]
        names = [
            'p~{}_{}'.format(period, location)
            for period in self.ins.periods
            for location in self.ins.locations
        ]

        self.var['p'] = self.mip.addVars(self.ins.periods, self.ins.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vro(self):
        # Create o^{t}_{i} variables

        lowers = [0. for _ in self.ins.periods for _ in self.ins.locations]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.locations]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.locations]
        types = ['C' for _ in self.ins.periods for _ in self.ins.locations]
        names = [
            'o~{}_{}'.format(period, location)
            for period in self.ins.periods
            for location in self.ins.locations
        ]

        self.var['o'] = self.mip.addVars(self.ins.periods, self.ins.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vrq(self):
        # Create q^{t} variables

        lowers = [-gp.GRB.INFINITY for _ in self.ins.periods_with_start]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods_with_start]
        coefs = [0. for _ in self.ins.periods_with_start]
        types = ['C' for _ in self.ins.periods_with_start]
        names = [
            'q~{}'.format(period)
            for period in self.ins.periods_with_start
        ]

        self.var['q'] = self.mip.addVars(self.ins.periods_with_start, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c1(self):
        # Create constraint 1

        self.mip.addConstrs(
            (
                self.var['o'][period2, location] -
                sum(
                    self.var['p'][period2, other]
                    for other in self.ins.captured_locations[self.customer]
                ) +
                self.var['q'][period1] - self.var['q'][period2] >=
                self.ins.coefficients[period1][period2][location][self.customer]
                for period1 in self.ins.periods_with_start
                for period2 in self.ins.periods
                for location in self.ins.captured_locations[self.customer]
                if period1 < period2
            ),
            name = 'c1'
        )

    def create_c2(self):
        # Create constraint 2

        self.mip.addConstrs(
            (
                self.var['q'][period1] >=
                self.ins.coefficients[period1][self.ins.finish][location][self.customer]
                for period1 in self.ins.periods_with_start
                for location in self.ins.captured_locations[self.customer]
            ),
            name = 'c2'
        )