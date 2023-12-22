import gurobipy as gp
import formulation as fm

class original(fm.formulation):

    def __init__(self, instance, name):

        super().__init__(instance, name)

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

        self.mip.addConstrs((self.var['b'][self.ins.start, customer] == 0 for customer in self.ins.customers), name = 'c2')

    def create_c3(self):
        # Create constraint 3

        self.mip.addConstrs((self.var['c'][period, customer] == self.var['b'][period - 1, customer] + self.ins.spawning[period][customer] for period in self.ins.periods for customer in self.ins.customers), name = 'c3')

class nonlinear(original):

    def __init__(self, instance):

        super().__init__(instance, 'DSFLP-C-NLR')

    def set_variables(self):

        self.create_vry()
        self.create_vrw()
        self.create_vrc()
        self.create_vrb()

    def set_objective(self):

        self.mip.setObjective(
            sum([self.ins.rewards[period][location] *
                self.ins.catalogs[location][customer] *
                self.var['w'][period, customer] *
                self.var['y'][period, location]
                for period in self.ins.periods
                for location in self.ins.locations
                for customer in self.ins.customers]))

    def set_constraints(self):

        self.create_c1()
        self.create_c2()
        self.create_c3()
        self.create_c4()
        self.create_c5()

    def create_vrw(self):
        # Create w^{t}_{j} variables

        lowers = [0 for _ in self.ins.periods for _ in self.ins.customers]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.customers]
        coefs = [0 for _ in self.ins.periods for _ in self.ins.customers]
        types = ['C' for _ in self.ins.periods for _ in self.ins.customers]
        names = [
            'w~{}_{}'.format(period, customer)
            for period in self.ins.periods
            for customer in self.ins.customers
        ]

        self.var['w'] = self.mip.addVars(self.ins.periods, self.ins.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c4(self):
        # Create constraint 4, nonlinear

        self.mip.addConstrs((self.var['b'][period, customer] == self.var['c'][period, customer] - self.var['w'][period, customer] for period in self.ins.periods for customer in self.ins.customers), name = 'c4')

    def create_c5(self):
        # Create constrain 5, nonlinear

        self.mip.addConstrs((self.var['w'][period, customer] == sum(self.var['y'][period, location] * self.ins.catalogs[location][customer] for location in self.ins.locations) * self.var['c'][period, customer] for period in self.ins.periods for customer in self.ins.customers), name = 'c5')

class linearized(original):

    def __init__(self, instance):

        super().__init__(instance, 'DSFLP-C-LRZ')

    def set_variables(self):

        self.create_vry()
        self.create_vrw()
        self.create_vrc()
        self.create_vrb()

    def set_objective(self):

        self.mip.setObjective(
            sum([self.ins.rewards[period][location] *
                self.var['w'][period, location, customer]
                for period in self.ins.periods
                for location in self.ins.locations
                for customer in self.ins.customers]))

    def set_constraints(self):

        self.create_c1()
        self.create_c2()
        self.create_c3()
        self.create_c4()
        self.create_c5()

    def create_vrw(self):
        # Create w^{t}_{ij} variables

        lowers = [0 for _ in self.ins.periods for _ in self.ins.locations for _ in self.ins.customers]
        uppers = [gp.GRB.INFINITY for _ in self.ins.periods for _ in self.ins.locations for _ in self.ins.customers]
        coefs = [0 for _ in self.ins.periods for _ in self.ins.locations for _ in self.ins.customers]
        types = ['C' for _ in self.ins.periods for _ in self.ins.locations for _ in self.ins.customers]
        names = [
            'w~{}_{}_{}'.format(period, location, customer)
            for period in self.ins.periods
            for location in self.ins.locations
            for customer in self.ins.customers
        ]

        self.var['w'] = self.mip.addVars(self.ins.periods, self.ins.locations, self.ins.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c4(self):
        # Create constraint 4, linearized

        self.mip.addConstrs((self.var['b'][period, customer] == self.var['c'][period, customer] - self.var['w'].sum(period, '*', customer) for period in self.ins.periods for customer in self.ins.customers), name = 'c4')

    def create_c5(self):
        # Create constraint 5, linearized

        self.mip.addConstrs((self.var['w'][period, location, customer] <= self.ins.limits[period][customer] * self.ins.catalogs[location][customer] * self.var['y'][period, location] for period in self.ins.periods for location in self.ins.locations for customer in self.ins.customers), name = 'c5A')
        self.mip.addConstrs((self.var['w'][period, location, customer] <= self.var['c'][period, customer] + self.ins.limits[period][customer] * (1 - self.ins.catalogs[location][customer] * self.var['y'][period, location]) for period in self.ins.periods for location in self.ins.locations for customer in self.ins.customers), name = 'c5B')
        self.mip.addConstrs((self.var['w'][period, location, customer] >=  -1 * self.ins.limits[period][customer] * self.ins.catalogs[location][customer] * self.var['y'][period, location] for period in self.ins.periods for location in self.ins.locations for customer in self.ins.customers), name = 'c5C')
        self.mip.addConstrs((self.var['w'][period, location, customer] >= self.var['c'][period, customer] - 1 * self.ins.limits[period][customer] * (1 - self.ins.catalogs[location][customer] * self.var['y'][period, location]) for period in self.ins.periods for location in self.ins.locations for customer in self.ins.customers), name = 'c5D')
