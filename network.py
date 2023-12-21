import formulation as fm

class network(fm.formulation):

    def __init__(self, instance):

        super().__init__(instance, 'DSFLP-C-NET')

    def set_variables(self):

        self.create_vry()
        self.create_vrz()

    def set_objective(self):

        self.mip.setObjective(
            sum([self.ins.revenues[period2][location] *
                self.ins.accumulated_demand(period1, period2, customer) *
                self.var['z'][period1, period2, location, customer]
                for period1 in self.ins.periods_with_start
                for period2 in self.ins.periods
                for location in self.ins.locations
                for customer in self.ins.customers]))

    def set_constraints(self):

        self.create_c1()
        self.create_c2()
        self.create_c3()
        self.create_c4()
        self.create_c5()

    def create_vrz(self):
        # Create z^{kt}_{ij} variables

        lowers = [0. for _ in self.ins.periods_with_start for _ in self.ins.periods_with_end for _ in self.ins.locations for _ in self.ins.customers]
        uppers = [1. for _ in self.ins.periods_with_start for _ in self.ins.periods_with_end for _ in self.ins.locations for _ in self.ins.customers]
        coefs = [0. for _ in self.ins.periods_with_start for _ in self.ins.periods_with_end for _ in self.ins.locations for _ in self.ins.customers]
        types = ['C' for _ in self.ins.periods_with_start for _ in self.ins.periods_with_end for _ in self.ins.locations for _ in self.ins.customers]
        names = [
            'z~{}_{}_{}_{}'.format(period1, period2, location, customer)
            for period1 in self.ins.periods_with_start
            for period2 in self.ins.periods_with_end
            for location in self.ins.locations
            for customer in self.ins.customers
        ]

        self.var['z'] = self.mip.addVars(self.ins.periods_with_start, self.ins.periods_with_end, self.ins.locations, self.ins.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c2(self):
        # Create constraint 2

        self.mip.addConstrs((sum(self.var['z'][period1, period2, location, customer] for period1 in self.ins.periods_with_start if self.ins.is_before(period1, period2)) == self.ins.catalogs[location][customer] * self.var['y'][period2, location] for period2 in self.ins.periods for location in self.ins.locations for customer in self.ins.customers), name = 'c2')

    def create_c3(self):
        # Create constraint 3

        self.mip.addConstrs((sum(self.var['z'].sum(period1, period2, '*', customer) for period1 in self.ins.periods_with_start if self.ins.is_before(period1, period2)) == sum(self.var['z'].sum(period2, period1, '*', customer) for period1 in self.ins.periods_with_end if self.ins.is_after(period1, period2)) for period2 in self.ins.periods for customer in self.ins.customers), name = 'c3')

    def create_c4(self):
        # Create constraint 4

        self.mip.addConstrs((self.var['z'].sum('0', '*', '*', customer) == 1 for customer in self.ins.customers), name = 'c4')

    def create_c5(self):
        # Create constraint 5

        self.mip.addConstrs((self.var['z'].sum('*', self.ins.end, '*', customer) == 1 for customer in self.ins.customers), name = 'c5')