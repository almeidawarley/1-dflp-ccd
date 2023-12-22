import instance as ic
import numpy as np
import json as js

class artificial(ic.instance):

    def __init__(self, keyword, project):

        super().__init__(keyword, project)

    def create_instance(self, folder = 'instances/artificial'):
        # Create rnd-based instances

        try:
            # Read specifications from file
            with open ('{}/{}.json'.format(folder, self.keyword), 'r') as content:
                self.parameters = js.load(content)
        except:
            print('No file found for keyword {}'.format(self.keyword))

        np.random.seed(self.parameters['seed'])

        # Set instance information
        number_locations = int(self.parameters['locations'])
        number_customers = int(self.parameters['customers'])
        number_periods = int(self.parameters['periods'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        if self.parameters['patronizing'] == 'small':
            patronizing = 1 / 2.01
        elif self.parameters['patronizing'] == 'medium':
            patronizing = 1
        elif self.parameters['patronizing'] == 'large':
            patronizing = 2.01
        else:
            exit('Wrong value for patronizing parameter')

        consideration_size = int(np.ceil((patronizing *number_locations)/number_periods))

        consideration_sets = {}
        for customer in self.customers:
            consideration_sets[customer] = np.random.choice(self.locations, consideration_size)

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in consideration_sets[customer] or location == customer else 0

        # Create rewards
        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                popularity = sum([self.catalogs[location][customer] for customer in self.customers])
                if self.parameters['rewards'] == 'identical':
                    coefficient = 1.
                elif self.parameters['rewards'] == 'inversely':
                    coefficient = 1. / popularity
                else:
                    exit('Wrong value for rewards parameter')
                self.rewards[period][location] = np.ceil(coefficient * len(self.locations))

        # Create parameters
        self.alphas = {}
        self.betas = {}
        self.starts = {}
        self.intensities = {}

        for customer in self.customers:
            self.starts[customer] = 1 if self.parameters['character'] == 'homogeneous' else np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            self.intensities[customer] = 1 if self.parameters['character'] == 'homogeneous' else np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            if self.parameters['replenishment'] == 'none':
                self.alphas[customer] = 0
                self.betas[customer] = 0
            elif self.parameters['replenishment'] == 'absolute':
                self.alphas[customer] = 0
                self.betas[customer] = self.intensities[customer]
            elif self.parameters['replenishment'] == 'relative':
                self.alphas[customer] = round(((number_periods * self.intensities[customer] + self.starts[customer])/self.starts[customer])**(1. / number_periods) - 1, 2)
                self.betas[customer] = 0
            elif self.parameters['replenishment'] == 'mixed':
                def evaluate_combination(alpha, beta):
                    result = self.starts[customer]
                    for _ in self.periods:
                        result += alpha * result + beta
                    return abs(2 * (self.starts[customer] + self.intensities[customer] * len(self.periods)) - result)
                def minimize_combination():
                    best_alpha = .0
                    best_beta = .0
                    best_value = 10**4
                    for alpha in range(1, 101):
                        local_alpha = float(alpha/100)
                        for beta in range(1, 11):
                            local_beta = float(beta)
                            value = evaluate_combination(local_alpha, local_beta)
                            if value < best_value:
                                best_value = value
                                best_alpha = local_alpha
                                best_beta = local_beta
                    return best_alpha, best_beta
                alpha, beta = minimize_combination()
                self.alphas[customer] = alpha
                self.betas[customer] = beta
            else:
                exit('Wrong value for replenishment parameter')