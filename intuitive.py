import gurobipy as gp
import formulation as fm

class intuitive(fm.formulation):

    def __init__(self, instance, name):

        super().__init__(instance, name)

    def relax(self):

        for period in self.ins.periods:
            for location in self.ins.locations:
                self.var['y'][period, location].vtype = 'C'

        for period in self.ins.periods:
            for customer in self.ins.customers:
                for location in self.ins.captured_locations[customer]:
                    self.var['x'][period, location, customer].vtype = 'C'

    def tense(self):

        for period in self.ins.periods:
            for location in self.ins.locations:
                self.var['y'][period, location].vtype = 'B'

        for period in self.ins.periods:
            for customer in self.ins.customers:
                for location in self.ins.captured_locations[customer]:
                    self.var['x'][period, location, customer].vtype = 'B'

    def set_variables(self):

        self.create_vry()
        self.create_vrx()
        self.create_vrw()
        self.create_vrc()
        self.create_vrb()

    def set_objective(self):

        if 'cvr' in self.ins.keyword:

            self.mip.setObjective(
                -1 * sum(
                    self.var['b'][self.ins.final - 1, customer]
                    for customer in self.ins.customers
                )
            )

        elif 'mrg' in self.ins.keyword:

            self.mip.setObjective(
                sum(
                    self.ins.rewards[location] *
                    self.var['w'][period, location, customer]
                    for period in self.ins.periods
                    for customer in self.ins.customers
                    for location in self.ins.captured_locations[customer]
                ) -
                sum(
                    self.ins.penalties[customer] *
                    self.ins.spawning[period][customer] *
                    (
                        1 - sum(
                            self.var['x'][period, location, customer]
                            for location in self.ins.captured_locations[customer]
                        )
                    )
                    for period in self.ins.periods
                    for customer in self.ins.customers
                )
            )

        elif 'bmk' in self.ins.keyword:

            self.mip.setObjective(
                sum(
                    self.ins.rewards[location] *
                    self.var['w'][period, location, customer]
                    for period in self.ins.periods
                    for customer in self.ins.customers
                    for location in self.ins.captured_locations[customer]
                ) -
                sum(
                    self.ins.penalties[customer] *
                    self.ins.spawning[period][customer] *
                    (
                        1 - sum(
                            self.var['x'][period, location, customer]
                            for location in self.ins.captured_locations[customer]
                        )
                    )
                    for period in self.ins.periods
                    for customer in self.ins.customers
                )
            )

        else:

            exit('Wrong value for the intuitive objective')

    def set_constraints(self):

        self.create_c1()
        self.create_c2()
        self.create_c3()
        self.create_c4()
        self.create_c5()
        self.create_c6()
        # self.create_c7()
        self.create_c8()
        self.create_c9()

    def create_vrx(self):
        # Create x^{t}_{ij} variables

        lowers = [0. for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        uppers = [1. for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        coefs = [0. for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        types = ['B' for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        names = [
            'x~{}_{}_{}'.format(period, location, customer)
            for period in self.ins.periods
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
        ]
        tuples = [
            (period, location, customer)
            for period in self.ins.periods
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
        ]

        self.var['x'] = self.mip.addVars(tuples, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vrw(self):
        # Create w^{t}_{ij} variables

        lowers = [0 for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        coefs = [0 for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        types = ['C' for _ in self.ins.periods for customer in self.ins.customers for _ in self.ins.captured_locations[customer]]
        names = [
            'w~{}_{}_{}'.format(period, location, customer)
            for period in self.ins.periods
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
        ]

        tuples = [
            (period, location, customer)
            for period in self.ins.periods
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
        ]

        self.var['w'] = self.mip.addVars(tuples, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vrb(self):
        # Create b^{t}_{j} variables

        lowers = [0. for _ in self.ins.periods_with_start for _ in self.ins.customers]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods_with_start for _ in self.ins.customers]
        coefs = [0. for _ in self.ins.periods_with_start for _ in self.ins.customers]
        types = ['C' for _ in self.ins.periods_with_start for _ in self.ins.customers]
        names = [
            'b~{}_{}'.format(period, customer)
            for period in self.ins.periods_with_start
            for customer in self.ins.customers
        ]

        self.var['b'] = self.mip.addVars(self.ins.periods_with_start, self.ins.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_vrc(self):
        # Create c^{t}_{j} variables

        lowers = [0. for _ in self.ins.periods for _ in self.ins.customers]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.customers]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.customers]
        types = ['C' for _ in self.ins.periods for _ in self.ins.customers]
        names = [
            'c~{}_{}'.format(period, customer)
            for period in self.ins.periods
            for customer in self.ins.customers
        ]

        self.var['c'] =  self.mip.addVars(self.ins.periods, self.ins.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c2(self):
        # Create constraint 2

        self.mip.addConstrs(
            (
                self.var['b'][self.ins.start, customer] == 0
                for customer in self.ins.customers
            ),
            name = 'c2'
        )

    def create_c3(self):
        # Create constraint 3

        self.mip.addConstrs(
            (
                self.var['c'][period, customer] ==
                self.var['b'][period - 1, customer] +
                self.ins.spawning[period][customer]
                for period in self.ins.periods
                for customer in self.ins.customers
            ),
            name = 'c3'
        )

    def create_c4(self):
        # Create constraint 4

        self.mip.addConstrs(
            (
                self.var['b'][period, customer] ==
                self.var['c'][period, customer] -
                self.var['w'].sum(period, '*', customer)
                for period in self.ins.periods
                for customer in self.ins.customers
            ),
            name = 'c4'
        )

    def create_c6(self):
        # Create constraint 6

        self.mip.addConstrs(
            (
                self.var['x'][period, location, customer]
                <= self.var['y'][period, location]
                for period in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c6'
        )

    def create_c7(self):
        # Create constraint 7

        self.mip.addConstrs(
            (
                sum(
                    self.var['x'][period, location, customer]
                    for location in self.ins.captured_locations[customer]
                ) <= 1
                for period in self.ins.periods
                for customer in self.ins.customers
            ),
            name = 'c7'
        )

    def create_c8(self):
        # Create constraint 8

        self.mip.addConstrs(
            (
                sum(
                    self.var['x'][period, other, customer]
                    for other in self.ins.captured_locations[customer]
                ) >= self.var['y'][period, location]
                for period in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c8'
        )

    def create_c9(self):
        # Create constraint 9

        self.mip.addConstrs(
            (
                self.var['y'][period2, location] +
                sum(
                    self.var['x'][period2, other, customer]
                    for other in self.ins.less_preferred[customer][location]
                ) <= 1
                for period2 in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c9'
        )

class nonlinear(intuitive):

    # Not updated to have preference rankings

    def __init__(self, instance):

        super().__init__(instance, 'DSFLP-C-NLR')

    def create_c5(self):
        # Create constrain 5, nonlinear

        self.mip.addConstrs(
            (
                self.var['w'][period, location, customer] ==
                self.var['x'][period, location, customer] *
                self.var['c'][period, customer]
                for period in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c5'
        )

class linearized(intuitive):

    def __init__(self, instance):

        super().__init__(instance, 'DSFLP-C-LRZ')

    def create_c5(self):
        # Create constraint 5, linearized

        self.mip.addConstrs(
            (
                self.var['w'][period, location, customer] <=
                self.ins.limits[period][customer] *
                self.var['x'][period, location, customer]
                for period in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c5A'
        )
        self.mip.addConstrs(
            (
                self.var['w'][period, location, customer] <=
                self.var['c'][period, customer] +
                self.ins.limits[period][customer] *
                (1 - self.var['x'][period, location, customer])
                for period in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c5B'
        )
        self.mip.addConstrs(
            (
                self.var['w'][period, location, customer] >=
                -1 * self.ins.limits[period][customer] *
                self.var['x'][period, location, customer]
                for period in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c5C'
        )
        self.mip.addConstrs(
            (
                self.var['w'][period, location, customer] >=
                self.var['c'][period, customer] -
                self.ins.limits[period][customer] *
                (1 - self.var['x'][period, location, customer])
                for period in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c5D'
        )