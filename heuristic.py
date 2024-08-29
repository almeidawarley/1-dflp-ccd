import gurobipy as gp
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

class progressive(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'PRG')

    def run(self):

        for frontier in self.ins.periods:

            local_objective = self.objective
            local_solution = self.ins.copy_solution(self.solution)

            for reference in reversed(self.ins.periods):

                if int(reference) <= int(frontier):

                    for location in self.ins.locations_extended:

                        # Copy partial solution
                        candidate = self.ins.copy_solution(self.solution)
                        # Insert location
                        candidate = self.ins.insert_solution(candidate, reference, location)
                        objective = self.ins.evaluate_solution(candidate)

                        if objective > local_objective:
                            local_solution = self.ins.copy_solution(candidate)
                            local_objective =  objective

            if local_objective > self.objective:
                self.objective = local_objective
                self.solution = self.ins.copy_solution(local_solution)

class forward(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'FRW')

    def run(self):

        for reference in self.ins.periods:

            for location in self.ins.locations_extended:

                # Copy partial solution
                candidate = self.ins.copy_solution(self.solution)
                # Insert location
                candidate[reference] = location
                objective = self.ins.evaluate_solution(candidate)

                if objective > self.objective:
                    self.solution = self.ins.copy_solution(candidate)
                    self.objective =  objective

class backward(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'BCW')

    def run(self):

        for reference in reversed(self.ins.periods):

            for location in self.ins.locations_extended:

                # Copy partial solution
                candidate = self.ins.copy_solution(self.solution)
                # Insert location
                candidate[reference] = location
                objective = self.ins.evaluate_solution(candidate)

                if objective > self.objective:
                    self.solution = self.ins.copy_solution(candidate)
                    self.objective =  objective

class random(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'RND')

    def run(self):

        np.random.seed(self.ins.parameters['seed'])

        # Create partial solution
        self.solution = {}
        for period in self.ins.periods:
            self.solution[period] = np.random.choice(self.ins.locations_extended)
        self.objective = self.ins.evaluate_solution(self.solution)

class emulation(heuristic):

    def __init__(self, instance):

        super().__init__(instance, 'EML')

    def run(self):

        candidate = self.ins.empty_solution()

        # Store previously calculated solutions
        stored = {}

        for period in self.ins.periods_with_start:
            stored[period] = {}
            for location in self.ins.locations_extended:
                    stored[period][location] = 0.

        for reference in self.ins.periods:

            local_objective = 0.
            local_location = self.ins.depot

            for location in self.ins.locations_extended:

                # Insert location
                candidate[reference] = location
                objective = self.ins.evaluate_solution(candidate)
                # Offset objective accordingly
                stored[reference][location] = objective
                objective -= stored[reference - 1][location]
                # Insert location
                candidate[reference] = self.ins.depot

                if objective > local_objective:
                    local_objective = objective
                    local_location = location

            # Fix location
            self.solution[reference] = local_location

        self.objective = self.ins.evaluate_solution(self.solution)