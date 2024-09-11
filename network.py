import formulation as fm

class network(fm.formulation):

    def __init__(self, instance):

        super().__init__(instance, 'DSFLP-C-NET')

    def set_variables(self):

        self.create_vry()
        self.create_vrx()

    def set_objective(self):

        '''
        # Check penalization part
        self.mip.setObjective(
            sum(
                self.ins.rewards[period2][location] *
                self.ins.accumulated[period1][period2][customer] *
                self.var['x'][period1, period2, location, customer]
                for period1 in self.ins.periods_with_start
                for period2 in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
                if period1 < period2
            ) -
            sum(
                self.ins.penalization *
                sum(
                    self.ins.spawning[period3][customer]
                    for period3 in self.ins.periods
                    if period1 <= period3 and period3 < period2
                ) *
                self.var['x'][period1, period2, location, customer]
                for period1 in self.ins.periods_with_start
                for period2 in self.ins.periods_with_end
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
                if period1 < period2
            )
        )
        '''
        self.mip.setObjective(
            sum(
                self.ins.rewards[period2][location] *
                self.ins.accumulated[period1][period2][customer] *
                self.var['x'][period1, period2, location, customer]
                for period1 in self.ins.periods_with_start
                for period2 in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
                if period1 < period2
            )
        )
        #'''

    def set_constraints(self):

        self.create_c1()
        self.create_c2()
        self.create_c3()
        self.create_c4()
        self.create_c5()

    def create_vrx(self):
        # Create x^{kt}_{ij} variables

        lowers = [0. for period1 in self.ins.periods_with_start for period2 in self.ins.periods_with_end for customer in self.ins.customers for _ in self.ins.captured_locations[customer] if period1 < period2]
        uppers = [1. for period1 in self.ins.periods_with_start for period2 in self.ins.periods_with_end for customer in self.ins.customers for _ in self.ins.captured_locations[customer] if period1 < period2]
        coefs = [0. for period1 in self.ins.periods_with_start for period2 in self.ins.periods_with_end for customer in self.ins.customers for _ in self.ins.captured_locations[customer] if period1 < period2]
        types = ['C' for period1 in self.ins.periods_with_start for period2 in self.ins.periods_with_end for customer in self.ins.customers for _ in self.ins.captured_locations[customer] if period1 < period2]
        names = [
            'x~{}_{}_{}_{}'.format(period1, period2, location, customer)
            for period1 in self.ins.periods_with_start
            for period2 in self.ins.periods_with_end
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
            if period1 < period2
        ]
        tuples = [
            (period1, period2, location, customer)
            for period1 in self.ins.periods_with_start
            for period2 in self.ins.periods_with_end
            for customer in self.ins.customers
            for location in self.ins.captured_locations[customer]
            if period1 < period2
        ]

        self.var['x'] = self.mip.addVars(tuples, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c2(self):
        # Create constraint 2

        self.mip.addConstrs(
            (
                sum(
                    self.var['x'][period1, period2, other, customer]
                    for period1 in self.ins.periods_with_start
                    for other in self.ins.captured_locations[customer]
                    if period1 < period2
                ) >= self.var['y'][period2, location]
                for period2 in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c2'
        )

    def create_c3(self):
        # Create constraint 3

        self.mip.addConstrs(
            (
                sum(
                    self.var['x'].sum(period1, period2, '*', customer)
                    for period1 in self.ins.periods_with_start
                    if period1 < period2
                ) ==
                sum(
                    self.var['x'].sum(period2, period1, '*', customer)
                    for period1 in self.ins.periods_with_end
                    if period1 > period2
                )
            for period2 in self.ins.periods
            for customer in self.ins.customers)
            ,
            name = 'c3'
        )

    def create_c4(self):
        # Create constraint 4

        self.mip.addConstrs(
            (
                self.var['x'].sum(self.ins.start, '*', '*', customer) == 1
                for customer in self.ins.customers
            ),
            name = 'c4'
        )

    def create_c5(self):
        # Create constraint 5

        self.mip.addConstrs(
            (
                sum(
                    self.var['x'][period1, period2, location, customer]
                    for period1 in self.ins.periods_with_start
                    if period1 < period2
                )
                <= self.var['y'][period2, location]
                for period2 in self.ins.periods
                for customer in self.ins.customers
                for location in self.ins.captured_locations[customer]
            ),
            name = 'c5'
        )