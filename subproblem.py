class subproblem:

    def __init__(self, instance, customer):

        self.ins = instance
        self.customer = customer
        self.solution = self.ins.empty_solution()
        self.raw_solution = {}
        self.counter = 0
        self.uncaptured = '-'
        self.placeholder = '?'

        # Create empty inequality
        self.inequality = {}
        self.inequality['b'] = 0.
        self.inequality['y'] = {}
        for period in self.ins.periods:
            self.inequality['y'][period] = {}
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = 0.

    def update(self, solution, raw_solution = {}):

        self.solution = solution
        self.raw_solution = raw_solution