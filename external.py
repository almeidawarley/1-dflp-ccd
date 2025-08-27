import subproblem as sb
from ctypes import *

class external(sb.subproblem):

    def __init__(self, instance, customer):

        super().__init__(instance, customer)

        self.library = cdll.LoadLibrary('./libanalytical.so')
        self.master_y = (c_float * (len(self.ins.periods) * len(self.ins.locations)))()
        self.primal_x = (c_float * (len(self.ins.periods_with_final) * len(self.ins.periods_with_final) * len(self.ins.locations)))()
        self.dual_q = (c_float * (len(self.ins.periods_with_start)))()
        self.dual_o = (c_float * (len(self.ins.periods) * len(self.ins.locations)))()
        self.dual_p = (c_float * (len(self.ins.periods) * len(self.ins.locations)))()
        self.patronization = (c_int * (len(self.ins.periods_with_start) * len(self.ins.locations)))()
        self.futurecapture = (c_int * (len(self.ins.periods_with_start) * len(self.ins.locations)))()

    def cut(self):

        # gcc -Wall -g -shared -o libanalytical.so -fPIC analytical.c

        # Update sequence
        for period in self.ins.periods:
            for location in self.ins.locations:
                if location in self.solution[period]:
                    self.master_y[(int(period) - 1) * len(self.ins.locations) + int(location) - 1] = 1.
                else:
                    self.master_y[(int(period) - 1) * len(self.ins.locations) + int(location) - 1] = 0.

        # Call external implementation in C
        self.library.procedure(
            int(self.customer),
            self.ins.c_nb_locations,
            self.ins.c_nb_customers,
            self.ins.c_nb_periods,
            byref(self.ins.c_dt_catalogs),
            byref(self.ins.c_dt_coefficients),
            byref(self.master_y),
            byref(self.primal_x),
            byref(self.dual_q),
            byref(self.dual_o),
            byref(self.dual_p),
            byref(self.patronization),
            byref(self.futurecapture),
            1
        )

        # Warning: changed to the single facility case structure!
        dual_objective = (
            self.dual_q[self.ins.start] +
            sum(
                self.dual_p[(int(period) - 1) * len(self.ins.locations) + int(location) - 1]
                for period in self.ins.periods
                for location in self.ins.captured_locations[self.customer]
            )
        )
        '''
        self.checker.update(self.solution)
        estimated, _ = self.checker.cut()
        if not cm.is_equal_to(dual_objective, estimated):
            print('External {} vs Analytical {}'.format(dual_objective, estimated))
            _ = input('Discrepancy identified at iteration {}, customer {}'.format(self.counter, self.customer))
        '''
        '''
        import os
        if not os.path.exists('subprbms/{}'.format(self.counter)):
            os.makedirs('subprbms/{}'.format(self.counter))
        with open('subprbms/{}/EXT_customer_{}.sol'.format(self.counter, self.customer), 'w') as content:
            for period2 in self.ins.periods:
                for location in self.ins.captured_locations[self.customer]:
                    content.write('p~{}_{} {}\n'.format(period2, location, self.dual_p[(int(period2) - 1) * len(self.ins.locations) + int(location) - 1]))
            for period1 in self.ins.periods_with_start:
                content.write('q~{} {}\n'.format(period1, self.dual_q[int(period1)]))
            for period2 in self.ins.periods:
                for location in self.ins.captured_locations[self.customer]:
                    content.write('o~{}_{} {}\n'.format(period2, location, self.dual_o[(int(period2) - 1) * len(self.ins.locations) + int(location) - 1]))
        '''

        # Build optimality cut
        for period in self.ins.periods:
            for location in self.ins.captured_locations[self.customer]:
                self.inequality['y'][period][location] = (
                    # self.dual_o[(int(period) - 1) * len(self.ins.locations) + int(location) - 1] -
                    # Warning: changed to the single facility case structure!
                    self.dual_p[(int(period) - 1) * len(self.ins.locations) + int(location) - 1]
                )
        self.inequality['b'] = self.dual_q[self.ins.start]

        self.counter += 1

        return dual_objective, self.inequality