import gurobipy as gp
import common as cm

class simplification():

    def __init__(self, instance, period):

        self.ins = instance
        self.mip = gp.Model('DSFLP-SIMPLE-{}'.format(period))
        self.period = period
        self.var = {}

        self.set_parameters()
        self.set_variables()
        self.set_objective()
        self.set_constraints()

    def run(self):

        # Call Gurobi to optimize the model
        self.mip.optimize()

        # Retrieve locations based on y_{i} values
        locations = []
        for location in self.ins.locations:
            if self.var['y'][location].x > 0.:
                locations.append(location)

        self.mip.reset()

        return locations

    def set_parameters(self):

        # Maximize the total reward
        self.mip.setAttr('ModelSense', -1)
        # Turn off GUROBI logs
        self.mip.setParam('OutputFlag', 0)
        # Constrain Gurobi to 1 thread
        self.mip.setParam('Threads', 1)
        # Set experimental time limit
        self.mip.setParam('TimeLimit', cm.TIMELIMIT)

    def create_vry(self):
        # Create y_{i} variables

        lowers = [0. for _ in self.ins.locations]
        uppers = [1. for _ in self.ins.locations]
        coefs = [0. for _ in self.ins.locations]
        types = ['B' for _ in self.ins.locations]
        names = [
            'y~{}'.format(location)
            for location in self.ins.locations
        ]

        self.var['y'] = self.mip.addVars(self.ins.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vrx(self):
        # Create x^{kt}_{ij} variables

        lowers = [0. for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        uppers = [1. for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        coefs = [0. for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        types = ['C' for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        names = [
            'x~{}_{}'.format(location, customer)
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
        ]
        tuples = [
            (location, customer)
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
        ]

        self.var['x'] = self.mip.addVars(tuples, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c1(self):
        # Create constraint 1

        self.mip.addConstr(
            self.var['y'].sum('*') <= self.ins.facilities[self.period],
            name = 'c1'
        )

    def set_variables(self):

        self.create_vry()
        self.create_vrx()

    def set_objective(self):

        if 'cvr' in self.ins.keyword:

            self.mip.setObjective(
                sum(
                    - 1 * self.ins.spawning[self.period][customer] *
                    (
                        1 - sum(self.var['x'][location, customer] for location in self.ins.captured_locations[customer])
                    )
                    for customer in self.ins.customers
                )
            )

        elif 'bmk' in self.ins.keyword:

            self.mip.setObjective(
                sum(
                    self.ins.spawning[self.period][customer] *
                    self.ins.rewards[location] *
                    self.var['x'][location, customer]
                    for customer in self.ins.customers
                    for location in self.ins.captured_locations[customer]
                )
            )

        elif 'mrg' in self.ins.keyword:

            self.mip.setObjective(
                sum(
                    self.ins.spawning[self.period][customer] *
                    self.ins.rewards[location] *
                    self.var['x'][location, customer]
                    for customer in self.ins.customers
                    for location in self.ins.captured_locations[customer]
                ) -
                sum(
                    self.ins.penalties[customer] *
                    self.ins.spawning[self.period][customer] *
                    (
                        1 - sum(
                            self.var['x'][location, customer]
                            for location in self.ins.captured_locations[customer]
                        )
                    )
                    for customer in self.ins.customers
                )
            )

        else:

            exit('Wrong value for the intuitive objective')

    def set_constraints(self):

        self.create_c1()
        self.create_c2()
        self.create_c5()
        self.create_c6()

    def create_c2(self):
        # Create constraint 2

        self.mip.addConstrs(
            (
                sum(
                    self.var['x'][other, customer]
                    for other in self.ins.captured_locations[customer]
                ) >= self.var['y'][location]
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c2'
        )

    def create_c5(self):
        # Create constraint 5

        self.mip.addConstrs(
            (
                self.var['x'][location, customer]
                <= self.var['y'][location]
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c5'
        )

    def create_c6(self):
        # Create constraint 6

        self.mip.addConstrs(
            (
                self.var['y'][location] +
                sum(
                    self.var['x'][other, customer]
                    for other in self.ins.less_preferred[customer][location]
                ) <= 1
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c6'
        )