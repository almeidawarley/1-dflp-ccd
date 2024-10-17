import formulation as fm
import subproblem as sb
import gurobipy as gp
import common as cm
import time as tm
import cProfile, pstats

class benders(fm.formulation):

    def __init__(self, instance, separation, fractional = False):

        super().__init__(instance, 'DSFLP-MASTER')

        self.subproblems = {}
        self.separation = separation
        self.fractional = fractional

        for customer in self.ins.customers:
            if separation == 'analytical':
                self.subproblems[customer] = sb.analytical(self.ins, customer)
            elif separation == 'external':
                self.subproblems[customer] = sb.external(self.ins, customer)
            elif separation == 'duality':
                self.subproblems[customer] = sb.duality(self.ins, customer)
            else:
                exit('Invalid method for solving suproblems')

    def solve(self, label = ''):

        # Branch-and-Benders cut

        label = label + '_' if len(label) > 0 else label

        # Activate lazy constraints
        self.mip.setParam('LazyConstraints', 1)

        # Initiate global variables
        information = {}
        information['subtime_integer'] = 0.
        information['subtime_fractional'] = 0.
        information['cuts_integer'] = 0
        information['cuts_fractional'] = 0

        # content = open('cuts-{}.txt'.format(label), 'w')

        def callback(model, where):

            if where == gp.GRB.Callback.MIPNODE:

                # Visit a MIP node, with fractional or integer solution
                status = model.cbGet(gp.GRB.Callback.MIPNODE_STATUS)
                nodes = model.cbGet(gp.GRB.Callback.MIPNODE_NODCNT)

                # Check if separating fractional solutions, and if at root node
                if self.fractional and status == gp.GRB.OPTIMAL and nodes == 0:

                    # Retrieve raw and formatted solution
                    solution = [] # Formatted solution not available
                    raw_solution = model.cbGetNodeRel(self.var['y'])

                    # Generate an optimality cut per customer
                    start = tm.time()

                    for customer in self.ins.customers:

                        self.subproblems[customer].update(solution, raw_solution)
                        _, inequality = self.subproblems[customer].cut()

                        rhs = inequality['b']
                        for period in self.ins.periods:
                            for location in self.ins.captured_locations[customer]:
                                rhs += inequality['y'][period][location] * self.var['y'][period, location]

                        # Add the optimality cut to the model
                        model.cbLazy(self.var['v'][customer] <= rhs)

                    end = tm.time()

                    # Update global variables accordingly
                    information['subtime_fractional'] += end - start
                    information['cuts_fractional'] += 1

            if where == gp.GRB.Callback.MIPSOL:

                # Visit a MIP node, with a feasible integer solution

                # Retrieve raw and formatted solution
                raw_solution = model.cbGetSolution(self.var['y'])
                solution = {}
                for period in self.ins.periods:
                    solution[period] = []
                    for location in self.ins.locations:
                        value = raw_solution[period, location]
                        if cm.is_equal_to(value, 1.):
                            solution[period].append(location)
                raw_solution = {} # Forcing the formatted solution

                # content.write('#{}: {}\n'.format(information['cuts_integer'], self.ins.pack_solution(solution)))

                # Generate an optimality cut per customer
                start = tm.time()

                for customer in self.ins.customers:

                    self.subproblems[customer].update(solution, raw_solution)
                    value, inequality = self.subproblems[customer].cut()

                    rhs = inequality['b']
                    for period in self.ins.periods:
                        for location in self.ins.captured_locations[customer]:
                            rhs += inequality['y'][period][location] * self.var['y'][period, location]

                    # content.write('{} {}\n'.format(customer, inequality))
                    # content.flush()

                    # Add the optimality cut to the model
                    model.cbLazy(self.var['v'][customer] <= rhs)

                end = tm.time()

                # Update global variables accordingly
                information['subtime_integer'] += end - start
                information['cuts_integer'] += 1

        # Call Gurobi to optimize the model
        self.mip.optimize(callback)

        # Retrieve solution and simulate objective value
        solution = self.ins.format_solution(self.var['y'])
        objective = self.ins.evaluate_solution(solution)

        metadata = {
            '{}cuts_fractional'.format(label): information['cuts_fractional'],
            '{}subtime_fractional'.format(label): round(information['subtime_fractional'], cm.PRECISION),
            '{}cuts_integer'.format(label): information['cuts_integer'],
            '{}subtime_integer'.format(label): round(information['subtime_integer'], cm.PRECISION),
            '{}status'.format(label): self.mip.status,
            '{}objective'.format(label): round(self.mip.objVal, cm.PRECISION),
            '{}bound'.format(label): round(self.mip.objBound, cm.PRECISION),
            '{}nodes'.format(label): self.mip.nodeCount,
            '{}runtime'.format(label): round(self.mip.runtime, cm.PRECISION),
            #'{}mipgap'.format(label): self.mip.MIPGap, # optgap? not really
            '{}optgap'.format(label): cm.compute_gap(self.mip.objBound, self.mip.objVal),
            '{}solution'.format(label): self.ins.pack_solution(solution)
        }

        cm.mark_section('Reporting summary of metadata')
        for key, value in metadata.items():
            print('{}: {}'.format(key, value))

        assert cm.compare_obj(self.mip.objVal, objective)

        # content.close()

        return metadata

    def set_parameters(self):

        # Maximize the total reward
        self.mip.setAttr('ModelSense', -1)
        # Turn off GUROBI logs
        # mip.setParam('OutputFlag', 0)
        # Constrain Gurobi to 1 thread
        self.mip.setParam('Threads', 1)
        # Set experimental time limit
        self.mip.setParam('TimeLimit', cm.TIMELIMIT)

    def set_variables(self):

        self.create_vry()
        self.create_vrv()

    def set_objective(self):

        self.mip.setObjective(
            self.var['v'].sum('*')
        )

    def set_constraints(self):

        self.create_c1()

    def create_vrv(self):
        # Create v_{j} variables

        lowers = [-gp.GRB.INFINITY for _ in self.ins.customers]
        uppers = [cm.INFINITY for _ in self.ins.customers]
        coefs = [0. for _ in self.ins.customers]
        types = ['C' for _ in self.ins.customers]
        names = [
            'v~{}'.format(customer)
            for customer in self.ins.customers
        ]

        self.var['v'] = self.mip.addVars(self.ins.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)