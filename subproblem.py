
import gurobipy as gp
import common as cm
from ctypes import *
#c_int, c_float, cdll, pointer

class subproblem:

    def __init__(self, instance, customer):

        self.ins = instance
        self.customer = customer
        self.solution = self.ins.empty_solution()

        # Create empty inequality
        self.inequality = {}
        self.inequality['b'] = 0.
        self.inequality['y'] = {}
        for period in self.ins.periods:
            self.inequality['y'][period] = {}
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = 0.

    def update(self, solution):

        self.solution = solution

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
        for period in self.ins.periods_with_start:
            self.dual_solution['q'][period] = 0.
        for period in self.ins.periods:
            self.dual_solution['p'][period] = {}
            for location in self.ins.captured_locations[self.customer]:
                self.dual_solution['p'][period][location] = 0.

    def cut(self):

        # Update primal solution
        for period1 in self.ins.periods_with_start:
            self.primal_solution[period1] = self.ins.finish
            for period2 in self.ins.periods:
                if period1 < period2 and self.solution[period2] != self.ins.depot and self.ins.catalogs[self.solution[period2]][self.customer] == 1:
                    self.primal_solution[period1] = period2
                    break

        dual_objective = 0.

        # Notation: period1 l, period2 t period3 k

        # First pass: compute q for captured periods
        for period3 in reversed(self.ins.periods_with_start):
            self.dual_solution['q'][period3] = 0.
            for period1, period2 in self.primal_solution.items():
                if self.primal_solution[period3] != period2 and period2 != self.ins.finish and period1 != period3 and period3 < period2:
                    location = self.solution[period2]
                    current = self.ins.rewards[period2][location] * self.ins.accumulated[period3][period2][self.customer] 
                    current -= self.ins.rewards[period2][location] * self.ins.accumulated[period1][period2][self.customer]
                    current += self.dual_solution['q'][period1]
                    if current > self.dual_solution['q'][period3]:
                        self.dual_solution['q'][period3] = current

        # Second pass: compute q for free periods
        for period3 in reversed(self.ins.periods_with_start):
            for period1, period2 in self.primal_solution.items():
                if self.primal_solution[period3] == period2 and period2 != self.ins.finish and period1 != period3 and period3 < period2:
                    location = self.solution[period2]
                    current = self.ins.rewards[period2][location] * self.ins.accumulated[period3][period2][self.customer] 
                    current -= self.ins.rewards[period2][location] * self.ins.accumulated[period1][period2][self.customer] 
                    current += self.dual_solution['q'][period1]
                    if current > self.dual_solution['q'][period3]:
                        self.dual_solution['q'][period3] = current

        dual_objective += self.dual_solution['q'][self.ins.start]

        # Compute p based on q values
        for period2 in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                # Start with max as start period
                current = self.ins.rewards[period2][location] * self.ins.accumulated[self.ins.start][period2][self.customer] 
                current += self.dual_solution['q'][period2]  - self.dual_solution['q'][self.ins.start]
                self.dual_solution['p'][period2][location] = current
                # Parse through other periods
                for period1 in self.ins.periods:
                    if period1 < period2:
                        current = self.ins.rewards[period2][location] * self.ins.accumulated[period1][period2][self.customer] 
                        current += self.dual_solution['q'][period2] - self.dual_solution['q'][period1]
                        if current > self.dual_solution['p'][period2][location]:
                            self.dual_solution['p'][period2][location] = current
                if self.solution[period2] == location:
                    dual_objective += self.dual_solution['p'][period2][location]

        # Build optimality cut
        for period in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = self.dual_solution['p'][period][location]
        self.inequality['b'] = self.dual_solution['q'][self.ins.start]

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

        # Solve dual program
        self.mip.optimize()

        # Build optimality cut
        for period in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = self.var['p'][period, location].x
        self.inequality['b'] = self.var['q'][self.ins.start].x

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

    def set_objective(self):

        self.mip.setObjective(
            sum(
                self.var['p'][period, location] *
                (1 if self.solution[period] == location else 0)
                for period in self.ins.periods
                for location in self.ins.captured_locations[self.customer]
            ) + self.var['q'][self.ins.start]
        )

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

        self.mip.addConstrs(
            (
                self.var['p'][period2, location] +
                self.var['q'][period1] - self.var['q'][period2] >=
                self.ins.rewards[period2][location] *
                self.ins.accumulated[period1][period2][self.customer]
                for period1 in self.ins.periods_with_start
                for period2 in self.ins.periods
                for location in self.ins.captured_locations[self.customer]
                if period1 < period2
            ),
            name = 'c1'
        )