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

    def solve_std(self, label = '', cutoff = 0., incumbent = {}):

        # Standard Benders implementation
        '''
        for customer in self.ins.customers:
            self.add_inequality(self.ins.unpack_solution('0-3'), customer)
        self.mip.write('refactoring-master.lp')
        '''

        '''
        for location in self.ins.locations:
            incumbent = self.ins.stable_solution(location)
            # incumbent = self.ins.empty_solution()
            # incumbent[self.ins.finish-1] = location
            for customer in self.ins.customers:
                self.add_inequality(incumbent, customer)
        '''

        label = label + '_' if len(label) > 0 else label

        if len(incumbent) > 0:
            lower_bound, upper_bound = cutoff, gp.GRB.INFINITY
            incumbent = self.ins.copy_solution(incumbent)
        else:
            lower_bound, upper_bound = 0., gp.GRB.INFINITY
            incumbent = self.ins.empty_solution()
        time_elapsed, time_remaining = 0., cm.TIMELIMIT
        time_subprbs = 0.
        loop_counter = 0

        while not cm.compare_obj(upper_bound, lower_bound) and time_remaining > cm.TIMENOUGH:

            # Optimize master problem
            self.mip.setParam('TimeLimit', time_remaining)
            if loop_counter > 0:
                self.mip.setParam('Cutoff', max(lower_bound, cutoff))
            self.heaten(incumbent)
            self.mip.optimize()
            # self.mip.write('master-i{}.lp'.format(loop_counter))

            # Update upper bound
            proven_bound = self.mip.objBound
            upper_bound = min(upper_bound, proven_bound)
            time_elapsed += self.mip.runtime
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

            time_elapsed += end - start
            time_subprbs += end - start

            # Update lower bound
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
            '{}runtime'.format(label): round(time_elapsed, cm.PRECISION),
            '{}subtime'.format(label): round(time_subprbs, cm.PRECISION),
            '{}optgap'.format(label): cm.compute_gap(upper_bound, lower_bound),
            '{}solution'.format(label): self.ins.pack_solution(incumbent)
        }

        return metadata

    def solve_bbc(self, label = '', cutoff = 0., incumbent = {}):

        # Branch-and-Benders cut

        label = label + '_' if len(label) > 0 else label

        empty = self.ins.empty_solution()
        for customer in self.ins.customers:
            self.add_inequality(empty, customer)

        '''
        for location in self.ins.locations:
            incumbent = self.ins.stable_solution(location)
            # incumbent = self.ins.empty_solution()
            # incumbent[self.ins.finish-1] = location
            for customer in self.ins.customers:
                self.add_inequality(incumbent, customer)
        '''

        # Activate lazy constraints
        self.mip.setParam('LazyConstraints', 1)

        '''
        self.mip.setParam('Cuts', 0)
        self.mip.setParam('Heuristics', 0)
        self.mip.setParam('RINS', 0)
        self.mip.setParam('Presolve', 0)
        self.mip.setParam('Aggregate', 0)
        self.mip.setParam('Symmetry', 0)
        self.mip.setParam('Disconnected', 0)
        '''

        data = {}
        data['time_subprbs'] = 0.
        data['loop_counter'] = 0

        # content = open('cuts-{}.txt'.format(label), 'w')

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

                # content.write('#{} {}\n'.format(data['loop_counter'], self.ins.pack_solution(incumbent)))

                start = tm.time()
                for customer in self.ins.customers:

                    self.subproblems[customer].update(incumbent)
                    _, inequality = self.subproblems[customer].cut()

                    rhs = inequality['b']
                    for period in self.ins.periods:
                        for location in self.ins.captured_locations[customer]:
                            rhs += inequality['y'][period][location] * self.var['y'][period, location]

                    # content.write('{} {}\n'.format(customer, inequality))

                    # Add inequality for some customer
                    model.cbLazy(self.var['v'][customer] <= rhs)
                end = tm.time()
                data['time_subprbs'] += end - start
                data['loop_counter'] += 1

        self.mip.setParam('Cutoff', cutoff)
        self.heaten(incumbent)
        self.mip.optimize(callback)

        incumbent = self.ins.format_solution(self.var['y'])
        try:
            optgap = round(self.mip.MIPGap, cm.PRECISION)
        except:
            optgap = 1.

        metadata = {
            '{}iterations'.format(label): data['loop_counter'],
            '{}objective'.format(label): self.mip.objVal,
            '{}runtime'.format(label): round(self.mip.runtime, cm.PRECISION),
            '{}subtime'.format(label): round(data['time_subprbs'], cm.PRECISION),
            '{}optgap'.format(label): optgap,
            '{}solution'.format(label): self.ins.pack_solution(incumbent)
        }

        # content.close()

        return metadata

    def add_inequality(self, solution, customer, lazy = 1):

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
            self.var['v'].sum('*')
        )

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