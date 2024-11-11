import gurobipy as gp
import common as cm

class formulation:

    def __init__(self, instance, name):

        self.ins = instance
        self.mip = gp.Model(name)
        self.var = {}

        self.set_parameters()
        self.set_variables()
        self.set_objective()
        self.set_constraints()

    def solve(self, label = ''):

        label = label + '_' if len(label) > 0 else label

        # Provide a simple warm start solution
        for period in self.ins.periods:
            for location in self.ins.locations:
                self.var['y'][period, location].start = 0

        # Call Gurobi to optimize the model
        self.mip.optimize()

        # Retrieve solution and simulate objective value
        solution = self.ins.format_solution(self.var['y'])
        objective = self.ins.evaluate_solution(solution)

        metadata = {
            '{}status'.format(label): self.mip.status,
            '{}objective'.format(label): round(self.mip.objVal, cm.PRECISION),
            '{}bound'.format(label): round(self.mip.objBound, cm.PRECISION),
            '{}nodes'.format(label): self.mip.nodeCount,
            '{}runtime'.format(label): round(self.mip.runtime, cm.PRECISION),
            '{}mipgap'.format(label): round(self.mip.MIPGap, cm.PRECISION), # optgap?
            '{}optgap'.format(label): cm.compute_gap(self.mip.objBound, self.mip.objVal),
            '{}solution'.format(label): self.ins.pack_solution(solution)
        }

        cm.mark_section('Reporting summary for {}'.format(self.ins.keyword))
        for key, value in metadata.items():
            print('{}: {}'.format(key, value))

        if not cm.compare_obj(self.mip.objVal, objective):
            print('>> Actual objective found through simulation: {} <<<'.format(objective))
            assert self.mip.objVal < objective
            print('>>> Solution found by Benders improved by post-processing <<<')

        self.mip.reset()

        return metadata

    def bound(self, label = ''):

        label = label + '_' if len(label) > 0 else label

        # Relax integrality (binary) constraints
        self.relax()

        # Call Gurobi to optimize the model
        self.mip.optimize()

        if self.mip.solcount > 0:

            metadata = {
                '{}status'.format(label): self.mip.status,
                '{}objective'.format(label): self.mip.objVal,
                '{}bound'.format(label): self.mip.objBound,
                '{}runtime'.format(label): round(self.mip.runtime, cm.PRECISION)
            }

        else:

            metadata = {
                '{}status'.format(label): self.mip.status,
                '{}objective'.format(label): round(-cm.INFINITY, cm.PRECISION),
                '{}bound'.format(label): round(cm.INFINITY, cm.PRECISION),
                '{}runtime'.format(label): round(self.mip.runtime, cm.PRECISION)
            }

        self.mip.reset()

        self.tense()

        return metadata

    def heaten(self, solution):

        for period in self.ins.periods:
            for location in self.ins.locations:
                self.var['y'][period, location].start = 1 if location == solution[period] else 0
                # self.var['y'][period, location].ub = 1 if location == solution[period] else 0
                # self.var['y'][period, location].lb = 1 if location == solution[period] else 0

    def set_parameters(self):

        # Maximize the total reward
        self.mip.setAttr('ModelSense', -1)
        # Turn off GUROBI logs
        # mip.setParam('OutputFlag', 0)
        # Constrain Gurobi to 1 thread
        self.mip.setParam('Threads', 1)
        # Set experimental time limit
        self.mip.setParam('TimeLimit', cm.TIMELIMIT)

    def create_vry(self):
        # Create y^{t}_{i} variables

        lowers = [0. for _ in self.ins.periods for _ in self.ins.locations]
        uppers = [1. for _ in self.ins.periods for _ in self.ins.locations]
        coefs = [0. for _ in self.ins.periods for _ in self.ins.locations]
        types = ['B' for _ in self.ins.periods for _ in self.ins.locations]
        names = [
            'y~{}_{}'.format(period, location)
            for period in self.ins.periods
            for location in self.ins.locations
        ]

        self.var['y'] = self.mip.addVars(self.ins.periods, self.ins.locations, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)

    def create_c1(self):
        # Create constraint 1

        self.mip.addConstrs(
            (
                self.var['y'].sum(period, '*') <= self.ins.facilities[period]
                for period in self.ins.periods
            ),
            name = 'c1'
        )