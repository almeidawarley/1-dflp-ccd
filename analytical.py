import subproblem as sb

class analytical(sb.subproblem):

    def __init__(self, instance, customer):

        super().__init__(instance, customer)

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
                    if other in self.ins.captured_locations[self.customer] and (location == self.uncaptured or self.ins.rewards[other] > self.ins.rewards[location]):
                        location = other
                patronization[period2] = location
        patronization[self.ins.start] = self.placeholder

        # Compute future capture at each time period
        futurecap = {period: self.ins.final for period in self.ins.periods_with_start}
        for period1 in self.ins.periods_with_start:
            for period2 in self.ins.periods:
                if period1 < period2:
                    if patronization[period2] != self.uncaptured:
                        futurecap[period1] = period2
                        break

        dual_objective = 0.

        # Assign zero values to variables o^t_i and p^t_i
        for period2 in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.dual_solution['o'][period2][location] = 0.
                self.dual_solution['p'][period2][location] = 0.

        # Compute variables q^l for CAPTURED periods only
        for period1 in reversed(self.ins.periods_with_start):
            # Compute estimated value, assuming variables p^t_i are zero

            if patronization[period1] != self.uncaptured:

                self.dual_solution['q'][period1] = max(
                    [
                        # This is the case where period2 is the final period
                        self.ins.coefficients[period1][self.ins.final][location][self.customer]
                        for location in self.ins.captured_locations[self.customer]
                    ] + [
                        self.ins.coefficients[period1][period2][location][self.customer] +
                        sum(self.dual_solution['p'][period2][other] for other in self.ins.captured_locations[self.customer]) +
                        self.dual_solution['q'][period2]
                        for period2 in self.ins.periods
                        for location in self.ins.captured_locations[self.customer]
                        if period1 < period2 and location in self.solution[period2]
                    ]
                )

                if futurecap[period1] != self.ins.final:
                    # Adjust variables p^t_k for CAPTURED periods
                    offset = sum(
                        self.dual_solution['p'][period2][other]
                        for period2 in self.ins.periods
                        for other in self.ins.captured_locations[self.customer]
                        if period1 < period2 and other in self.solution[period2]
                    )
                    period2, location = futurecap[period1], patronization[futurecap[period1]]
                    self.dual_solution['p'][period2][location] = self.dual_solution['q'][period1] - offset - self.ins.evaluate_customer(self.solution, self.customer, period1)

        # Compute variables q^l for UNCAPTURED periods only
        for period1 in reversed(self.ins.periods_with_start):
            # Compute estimated value, assuming variables p^t_i are zero

            if patronization[period1] == self.uncaptured:

                self.dual_solution['q'][period1] = max(
                    [
                        # This is the case where period2 is the final period
                        self.ins.coefficients[period1][self.ins.final][location][self.customer]
                        for location in self.ins.captured_locations[self.customer]
                    ] + [
                        self.ins.coefficients[period1][period2][location][self.customer] +
                        sum(self.dual_solution['p'][period2][other] for other in self.ins.captured_locations[self.customer]) +
                        self.dual_solution['q'][period2]
                        for period2 in self.ins.periods
                        for location in self.ins.captured_locations[self.customer]
                        if period1 < period2 and location in self.solution[period2]
                    ]
                )

        # Compute variables o^t_i for CAPTURED and UNCAPTURED periods
        for period2 in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                if location not in self.solution[period2]:
                    self.dual_solution['o'][period2][location] = max(
                            self.ins.coefficients[period1][period2][location][self.customer] -
                            self.dual_solution['q'][period1] + self.dual_solution['q'][period2] +
                            sum(self.dual_solution['p'][period2][other] for other in self.ins.captured_locations[self.customer])
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

        dual_objective = (
            self.dual_solution['q'][self.ins.start] -
            sum(
                self.dual_solution['p'][period2][location]
                for period2 in self.ins.periods
                for location in self.ins.captured_locations[self.customer]
                # if location in self.solution[period2]
            )
        )

        self.counter += 1

        return dual_objective, self.inequality