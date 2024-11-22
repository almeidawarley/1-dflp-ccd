import subproblem as sb
import gurobipy as gp
import common as cm

class duality(sb.subproblem):

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
                    if i in self.ins.captured_locations[self.customer] and (location == '-' or self.ins.rewards[i] > self.ins.rewards[location]):
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
                self.inequality['y'][period][location] = self.var['o'][period, location].x - self.var['p'][period, location].x - self.var['u'][period, location].x
        self.inequality['b'] = self.var['q'][self.ins.start].x + sum(self.var['u'][period, location].x for period in self.ins.periods for location in self.ins.captured_locations[self.customer])

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
        self.create_vru()

    def set_objective(self):

        if len(self.raw_solution) > 0.:

            print('>>> Writing objective function based on raw solution <<<')

            self.mip.setObjective(
                sum(
                    (
                        self.var['o'][period, location] -
                        self.var['p'][period, location] -
                        self.var['u'][period, location]
                    ) *
                    self.raw_solution[period, location]
                    for period in self.ins.periods
                    for location in self.ins.captured_locations[self.customer]
                ) + self.var['q'][self.ins.start] +
                sum(
                    self.var['u'][period, location]
                    for period in self.ins.periods
                    for location in self.ins.captured_locations[self.customer]
                )
            )

        else:

            self.mip.setObjective(
                sum(
                    (
                        self.var['o'][period, location] -
                        self.var['p'][period, location] -
                        self.var['u'][period, location]
                    ) *
                    (1 if location in self.solution[period] else 0)
                    for period in self.ins.periods
                    for location in self.ins.captured_locations[self.customer]
                ) + self.var['q'][self.ins.start] +
                sum(
                    self.var['u'][period, location]
                    for period in self.ins.periods
                    for location in self.ins.captured_locations[self.customer]
                )
            )

    def set_constraints(self):

        self.create_c1()
        self.create_c2()

    def create_vrp(self):
        # Create p^{t}_{i} variables

        lowers = [0. for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        types = ['C' for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        names = [
            'p~{}_{}'.format(period, location)
            for period in self.ins.periods
            for location in self.ins.captured_locations[self.customer]
        ]
        tuples = [
            (period, location)
            for period in self.ins.periods
            for location in self.ins.captured_locations[self.customer]
        ]

        self.var['p'] = self.mip.addVars(tuples, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vro(self):
        # Create o^{t}_{i} variables

        lowers = [0. for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        types = ['C' for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        names = [
            'o~{}_{}'.format(period, location)
            for period in self.ins.periods
            for location in self.ins.captured_locations[self.customer]
        ]
        tuples = [
            (period, location)
            for period in self.ins.periods
            for location in self.ins.captured_locations[self.customer]
        ]

        self.var['o'] = self.mip.addVars(tuples, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vru(self):
        # Create u^{t}_{i} variables

        lowers = [0. for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        types = ['C' for _ in self.ins.periods for _ in self.ins.captured_locations[self.customer]]
        names = [
            'u~{}_{}'.format(period, location)
            for period in self.ins.periods
            for location in self.ins.captured_locations[self.customer]
        ]
        tuples = [
            (period, location)
            for period in self.ins.periods
            for location in self.ins.captured_locations[self.customer]
        ]

        self.var['u'] = self.mip.addVars(tuples, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

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
                sum(
                    self.var['u'][period2, other]
                    for other in self.ins.more_preferred[self.customer][location]
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
                self.ins.coefficients[period1][self.ins.final][location][self.customer]
                for period1 in self.ins.periods_with_start
                for location in self.ins.captured_locations[self.customer]
            ),
            name = 'c2'
        )