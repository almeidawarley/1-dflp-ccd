import simplification as sp
import network as nt
import common as cm
import numpy as np
import time as tm

class heuristic:

    def __init__(self, instance, name):

        self.ins = instance
        self.name = name
        self.solution = self.ins.empty_solution()
        self.objective = 0.

    def solve(self, label = ''):

        label = label + '_' if len(label) > 0 else label

        start = tm.time()
        self.run()
        end = tm.time()

        metadata = {
            '{}objective'.format(label): self.objective,
            '{}runtime'.format(label): round(end - start, cm.PRECISION),
            '{}solution'.format(label): self.ins.pack_solution(self.solution)
        }

        return metadata

class forward(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'FRW')

    def run(self):

        # Create standard network formulation
        model = nt.network(self.ins)

        self.solution = self.ins.empty_solution()

        print('Running FRW heuristic')

        # Set upper bound of variables y^{t}_{i} to 0
        for period in self.ins.periods:
            for location in self.ins.locations:
                model.var['y'][period, location].ub = 0

        time_left = cm.TIMELIMIT
        for period in self.ins.periods:
            # Reset upper bound of variables y^{t}_{i} to 1
            for location in self.ins.locations:
                model.var['y'][period, location].ub = 1
            model.mip.setParam('TimeLimit', time_left)
            model.mip.setParam('OutputFlag', 0)
            model.mip.optimize()
            time_left -= model.mip.runtime
            time_left = max(60, time_left)
            # Retrieve set of locations for some period
            locations = []
            for location in self.ins.locations:
                if model.var['y'][period, location].x > 0.:
                    locations.append(location)
                model.var['y'][period, location].lb = model.var['y'][period, location].x
                model.var['y'][period, location].ub = model.var['y'][period, location].x
            self.solution[period] = locations
            print('Period {}: {}'.format(period, self.solution[period]))

        self.objective = self.ins.evaluate_solution(self.solution)

class backward(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'BCW')

    def run(self):

        # Create standard network formulation
        model = nt.network(self.ins)

        self.solution = self.ins.empty_solution()

        print('Running BCW heuristic')

        # Set upper bound of variables y^{t}_{i} to 0
        for period in self.ins.periods:
            for location in self.ins.locations:
                model.var['y'][period, location].ub = 0

        time_left = cm.TIMELIMIT
        for period in reversed(self.ins.periods):
            # Reset upper bound of variables y^{t}_{i} to 1
            for location in self.ins.locations:
                model.var['y'][period, location].ub = 1
            model.mip.setParam('TimeLimit', time_left)
            model.mip.setParam('OutputFlag', 0)
            model.mip.optimize()
            time_left -= model.mip.runtime
            time_left = max(60, time_left)
            # Retrieve set of locations for some period
            locations = []
            for location in self.ins.locations:
                if model.var['y'][period, location].x > 0.:
                    locations.append(location)
                model.var['y'][period, location].lb = model.var['y'][period, location].x
                model.var['y'][period, location].ub = model.var['y'][period, location].x
            self.solution[period] = locations
            print('Period {}: {}'.format(period, self.solution[period]))

        self.objective = self.ins.evaluate_solution(self.solution)

class emulation(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'EML')

    def run(self):

        self.solution = self.ins.empty_solution()

        print('Running EML heuristic')

        time_left = cm.TIMELIMIT
        for period in self.ins.periods:
            model = sp.simplification(self.ins, period)
            model.mip.setParam('TimeLimit', time_left)
            self.solution[period] = model.run()
            time_left -= model.mip.runtime
            time_left = max(60, time_left)
            print('Period {}: {}'.format(period, self.solution[period]))

        self.objective = self.ins.evaluate_solution(self.solution)

class random(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'RND')

    def run(self):

        np.random.seed(self.ins.parameters['seed'])

        # Create a random solution
        print('Running RND heuristic')

        self.solution = self.ins.empty_solution()
        for period in self.ins.periods:
            self.solution[period] = list(np.random.choice(self.ins.locations, self.ins.facilities[period]))
            print('Period {}: {}'.format(period, self.solution[period]))
        self.objective = self.ins.evaluate_solution(self.solution)