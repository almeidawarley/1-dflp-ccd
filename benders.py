import formulation as fm
import subproblem as sb
import gurobipy as gp
import common as cm
import time as tm
import cProfile, pstats

class benders(fm.formulation):

    def __init__(self, instance, type):

        super().__init__(instance, 'DSFLP-MASTER')

        self.subproblems = {}

        for customer in self.ins.customers:
            if type == 'analytical':
                self.subproblems[customer] = sb.analytical(self.ins, customer)
            elif type == 'duality':
                self.subproblems[customer] = sb.duality(self.ins, customer)
            elif type == 'maxQ':
                self.subproblems[customer] = sb.maxQ(self.ins, customer)
            else:
                exit('Invalid method for solving suproblems')

    def solve_std(self, label = ''):

        # Standard Benders implementation
        '''
        for customer in self.ins.customers:
            self.add_inequality(self.ins.unpack_solution('0-3'), customer)
        self.mip.write('refactoring-master.lp')
        '''

        label = label + '_' if len(label) > 0 else label

        lower_bound, upper_bound = 0., gp.GRB.INFINITY
        incumbent = self.ins.empty_solution()
        time_elapsed, time_remaining = 0., cm.TIMELIMIT
        time_subproblems = 0.
        loop_counter = 0

        while not cm.compare_obj(upper_bound, lower_bound) and time_remaining > cm.TIMENOUGH:

            # Optimize master problem
            self.mip.setParam('TimeLimit', time_remaining)
            self.heaten(incumbent)
            self.mip.optimize()
            # self.mip.write('master-{}.lp'.format(loop_counter))

            # Update upper bound
            proven_bound = round(self.mip.objBound, cm.PRECISION)
            upper_bound = min(upper_bound, proven_bound)
            time_elapsed += round(self.mip.runtime, cm.PRECISION)
            solution = self.ins.format_solution(self.var['y'])

            '''
            profiler = cProfile.Profile()
            profiler.enable()
            for customer in self.ins.customers:
                self.subproblems[customer].cut()
            profiler.disable()
            stats = pstats.Stats(profiler).sort_stats('tottime')
            stats.print_stats()
            _ = input('wait...')
            '''

            # Solve subproblems
            start = tm.time()
            current_bound = 0.
            for customer in self.ins.customers:
                dual_objective = self.add_inequality(solution, customer)
                current_bound += dual_objective
            end = tm.time()

            time_elapsed += round(end - start, cm.PRECISION)
            time_subproblems += round(end - start, cm.PRECISION)

            # Update lower bound
            current_bound = round(current_bound, 2)
            if current_bound > lower_bound:
                lower_bound = current_bound
                incumbent = self.ins.copy_solution(solution)
            loop_counter += 1

            # Print iteration log
            print('-----------------------------------------------------------------------------------\n\n')
            print('Iteration: {}'.format(loop_counter))
            print('Lower bound: {}'.format(lower_bound))
            print('Current bound: {}'.format(current_bound))
            print('Upper bound: {}'.format(upper_bound))
            print('Current solution: {}'.format('-'.join(solution.values())))
            print('Current incumbent: {}'.format('-'.join(incumbent.values())))
            print('Optimality gap: {}'.format(cm.compute_gap(upper_bound, lower_bound)))
            print('\n\n-----------------------------------------------------------------------------------')

            # _ = input('next iteration...')

            time_remaining = cm.TIMELIMIT - time_elapsed

        metadata = {
            '{}iterations'.format(label): loop_counter,
            '{}objective'.format(label): lower_bound,
            '{}runtime'.format(label): time_elapsed,
            '{}subtime'.format(label): time_subproblems,
            '{}optgap'.format(label): cm.compute_gap(upper_bound, lower_bound),
            '{}solution'.format(label): self.ins.pack_solution(incumbent)
        }


        return metadata

    def solve_bbc(self, label = ''):

        # Branch-and-Benders cut

        label = label + '_' if len(label) > 0 else label

        incumbent = self.ins.empty_solution()
        for customer in self.ins.customers:
            self.add_inequality(incumbent, customer)

        # Activate lazy constraints
        self.mip.setParam('LazyConstraints', 1)

        data = {}
        data['time_subproblems'] = 0.
        data['loop_counter'] = 0

        def callback(model, where):

            if where == gp.GRB.Callback.MIPSOL:

                solution = model.cbGetSolution(self.var['y'])

                # Format raw solution
                incumbent = self.ins.empty_solution()
                for period in self.ins.periods:
                    for location in self.ins.locations:
                        value = solution[period, location]
                        if cm.is_equal_to(value, 1.):
                            incumbent[period] = location

                start = tm.time()
                for customer in self.ins.customers:

                    self.subproblems[customer].update(incumbent)
                    _, inequality = self.subproblems[customer].cut()

                    rhs = inequality['b']
                    for period in self.ins.periods:
                        for location in self.ins.captured_locations[customer]:
                            rhs += inequality['y'][period][location] * self.var['y'][period, location]

                    # Add inequality for some customer
                    model.cbLazy(self.var['v'][customer] <= rhs)
                end = tm.time()
                data['time_subproblems'] += round(end - start, cm.PRECISION)
                data['loop_counter'] += 1

        self.mip.optimize(callback)

        objective = round(self.mip.objVal, 2)
        incumbent = self.ins.format_solution(self.var['y'])
        try:
            optgap = round(self.mip.MIPGap, cm.PRECISION)
        except:
            optgap = 1.
        time_elapsed = round(self.mip.runtime, cm.PRECISION)

        metadata = {
            '{}iterations'.format(label): data['loop_counter'],
            '{}objective'.format(label): objective,
            '{}runtime'.format(label): time_elapsed,
            '{}subtime'.format(label): data['time_subproblems'],
            '{}optgap'.format(label): optgap,
            '{}solution'.format(label): self.ins.pack_solution(incumbent)
        }

        return metadata

    def add_inequality(self, solution, customer, lazy = 3):

        self.subproblems[customer].update(solution)
        dual_objective, inequality = self.subproblems[customer].cut()

        rhs = inequality['b']
        for period in self.ins.periods:
            for location in self.ins.captured_locations[customer]:
                rhs += inequality['y'][period][location] * self.var['y'][period, location]

        self.mip.addConstr(self.var['v'][customer] <= rhs).lazy = lazy

        return dual_objective

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
            sum([self.var['v'][customer]
                for customer in self.ins.customers]))

    def set_constraints(self):

        self.create_c1()

    def create_vrv(self):
        # Create v_{j} variables

        lowers = [0. for _ in self.ins.customers]
        uppers = [gp.GRB.INFINITY for _ in self.ins.customers]
        coefs = [0. for _ in self.ins.customers]
        types = ['C' for _ in self.ins.customers]
        names = [
            'v~{}'.format(customer)
            for customer in self.ins.customers
        ]

        self.var['v'] = self.mip.addVars(self.ins.customers, lb = lowers, ub = uppers, obj = coefs, vtype = types, name = names)