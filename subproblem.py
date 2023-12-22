
import gurobipy as gp
import common as cm

class subproblem:

    def __init__(self, instance, customer):

        self.ins = instance
        self.customer = customer
        self.solution = self.ins.empty_solution()

    def update(self, solution):

        self.solution = solution

class analytical(subproblem):

    def __init__(self, instance, customer):

        super().__init__(instance, customer)

    def cut(self):

        # Retrieve primal solution from master solution
        primal_solution = {}
        for period1 in self.ins.periods_with_start:
            primal_solution[period1] = self.ins.finish
            for period2 in self.ins.periods:
                if period1 < period2 and self.solution[period2] != self.ins.depot and self.ins.catalogs[self.solution[period2]][self.customer] == 1:
                    primal_solution[period1] = period2
                    break

        dual_solution = {}

        dual_solution['q'] = {period : 0. for period in self.ins.periods_with_start}

        # period1 l, period2 t period3 k
        # First pass, captured periods
        for period3 in reversed(self.ins.periods_with_start):
            for period1, period2 in primal_solution.items():
                # compute Q for captured periods first  & check if it is not last period & check if it is not the same period & check precedence
                if primal_solution[period3] != period2 and period2 != self.ins.finish and period1 != period3 and period3 < period2:
                    location = self.solution[period2]
                    # print('q{} through z[{} -> {}][{}]'.format(period3, period1, period2, location))
                    current = self.ins.rewards[period2][location] * self.ins.acc_demand[self.customer][period3][period2]  # self.ins.accumulated_demand(period3, period2, self.customer)
                    current -= self.ins.rewards[period2][location] * self.ins.acc_demand[self.customer][period1][period2] # self.ins.accumulated_demand(period1, period2, self.customer)
                    current += dual_solution['q'][period1]
                    if current > dual_solution['q'][period3]:
                        dual_solution['q'][period3] = current

        # Second pass, free periods
        for period3 in reversed(self.ins.periods_with_start):
            for period1, period2 in primal_solution.items():
                # compute Q for free periods second  & check if it is not last period & check if it is not the same period & check precedence
                if primal_solution[period3] == period2 and period2 != self.ins.finish and period1 != period3 and period3 < period2:
                    location = self.solution[period2]
                    # print('q{} through z[{} -> {}][{}]'.format(period3, period1, period2, location))
                    current = self.ins.rewards[period2][location] * self.ins.acc_demand[self.customer][period3][period2]  # self.ins.accumulated_demand(period3, period2, self.customer)
                    current -= self.ins.rewards[period2][location] * self.ins.acc_demand[self.customer][period1][period2] # self.ins.accumulated_demand(period1, period2, self.customer)
                    current += dual_solution['q'][period1]
                    if current > dual_solution['q'][period3]:
                        dual_solution['q'][period3] = current

            # print('q[{}] = {}'.format(period3, dual_solution['q'][period3]))

        dual_solution['p'] = {}
        for period2 in self.ins.periods:
            dual_solution['p'][period2] = {}
            for location in self.ins.locations:
                current = self.ins.rewards[period2][location] * self.ins.acc_demand[self.customer][self.ins.start][period2] # self.ins.accumulated_demand(self.ins.start, period2, self.customer)
                current += dual_solution['q'][period2]  - dual_solution['q'][self.ins.start]
                current *= self.ins.catalogs[location][self.customer]
                dual_solution['p'][period2][location] = current
                for period1 in self.ins.periods_with_start:
                    if period1 < period2:
                        current = self.ins.rewards[period2][location] * self.ins.acc_demand[self.customer][period1][period2] # self.ins.accumulated_demand(period1, period2, self.customer)
                        current += dual_solution['q'][period2] - dual_solution['q'][period1]
                        current *= self.ins.catalogs[location][self.customer]
                        if current > dual_solution['p'][period2][location]:
                            dual_solution['p'][period2][location] = current

                # print('p[{},{}] = {}'.format(period2, location, dual_solution['p'][period2][location]))

        # Build cut for some customer
        inequality = {}
        inequality['y'] = {}
        for period in self.ins.periods_extended:
            if period != self.ins.start and period != self.ins.finish:
                inequality['y'][period] = {}
                for location in self.ins.locations:
                    inequality['y'][period][location] = dual_solution['p'][period][location]
        inequality['b'] = dual_solution['q'][self.ins.start]

        dual_objective = dual_solution['q'][self.ins.start] + sum([dual_solution['p'][period][location] for period, location in self.solution.items() if location != self.ins.depot])

        # print('... with an objective of {}'.format(dual_objective))
        # print('Reference: {}'.format('-'.join(solution.values())))

        return dual_objective, inequality

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

        self.set_objective()

        self.mip.optimize()

        # Build cut for some customer
        inequality = {}
        inequality['y'] = {}
        for period in self.ins.periods_extended:
            if period != self.ins.start and period != self.ins.finish:
                inequality['y'][period] = {}
                for location in self.ins.locations:
                    inequality['y'][period][location] = self.var['p'][period, location].x
        inequality['b'] = self.var['q'][self.ins.start].x

        dual_objective = round(self.mip.objVal, 2)

        return dual_objective, inequality

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

    def set_objective(self):

        self.mip.setObjective(
            sum([self.var['p'][period, location] *
                self.ins.catalogs[location][self.customer] *
                (1 if self.solution[period] == location else 0)
                for period in self.ins.periods
                for location in self.ins.locations])
                + self.var['q'][self.ins.start])

    def set_constraints(self):

        self.create_c1()

    def create_vrp(self):
        # Create p^{t}_{i} variables

        lowers = [-gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.locations]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.locations]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.locations]
        types = ['C' for _ in self.ins.periods for _ in self.ins.locations]
        names = [
            'p~{}_{}'.format(period, location)
            for period in self.ins.periods
            for location in self.ins.locations
        ]

        self.var['p'] = self.mip.addVars(self.ins.periods, self.ins.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vrq(self):
        # Create q^{t} variables

        lowers = [0 for _ in self.ins.periods_with_start]
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

        self.mip.addConstrs((self.var['p'][period2, location] + self.var['q'][period1] - self.var['q'][period2]
                        >= self.ins.rewards[period2][location] * self.ins.accumulated_demand(period1, period2, self.customer)
                        for period1 in self.ins.periods_with_start for period2 in self.ins.periods for location in self.ins.locations
                        if period1 < period2 and self.ins.catalogs[location][self.customer] == 1), name = 'c1')

class maxQ(duality):

    # In short, maxQ seems to be a good idea!
    # It finds a stronger cut in some cases
    # Example: proof instance, solution 0-3

    def __init__(self, instance, customer):

        super().__init__(instance, customer)

        self.analytical = analytical(instance, customer)

    def update(self, solution):

        super().update(solution)

        self.analytical.update(self.solution)
        dual_objective, _ = self.analytical.cut()

        try:
            self.normalization
            self.mip.remove(self.normalization)
        except:
            pass

        self.normalization = self.mip.addConstr(
            sum([self.var['p'][period, location] *
                self.ins.catalogs[location][self.customer] *
                (1 if self.solution[period] == location else 0)
                for period in self.ins.periods
                for location in self.ins.locations])
                + self.var['q'][self.ins.start] == dual_objective, name = 'c2')