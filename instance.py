import json as js
import random as rd
import numpy as np

class instance:

    def __init__(self, keyword, project):
        # Initiate instance class

        # Store instance keyword
        instance.keyword = keyword
        # Store project keyword
        instance.project = project

        # Store parameters
        self.parameters = {}

        # Standard seed
        self.parameters['seed'] = 0

        # Decide instance type
        if keyword == 'jopt':
            # Create JOPT instance
            self.create_jopt()
        elif keyword == 'approx':
            # Create approx instance
            self.create_approx()
        elif keyword == 'spp':
            # Create SPP instance
            self.create_spp()
        elif '.cnf' in keyword:
            # Create 3SAT instance
            self.create_3sat()
        elif 'rnd1' in keyword:
            # Create RND1 instance
            self.create_rnd1()
        elif 'rnd2' in keyword:
            # Create RND2 instance
            self.create_rnd2()
        elif 'rnd' in keyword:
            # Create rnd-based instance
            self.create_planB()
        else:
            exit('Invalid instance keyword')

        # Set proper big M values
        self.limits = {}
        for customer in self.customers:
            limit = self.starts[customer]
            for _ in self.periods:
                limit = (1 + self.alphas[customer]) * limit + self.betas[customer]
            self.limits[customer] = np.ceil(limit)

        # Set proper big M values (2nd)
        cumulatives = {}
        for customer in self.customers:
            cumulatives[customer] = {}
            limit = self.starts[customer]
            for period in self.periods:
                limit = (1 + self.alphas[customer]) * limit + self.betas[customer]
                cumulatives[customer][period] = limit

        self.frontiers = {}
        for period in self.periods:
            self.frontiers[period] = 0.
            for location in self.locations:
                frontier = 0.
                for customer in self.customers:
                    frontier += self.catalogs[location][customer] * cumulatives[customer][period]
                if frontier > self.frontiers[period]:
                    self.frontiers[period] = frontier

        # Set start and end periods

        self.periods_with_start = ['0'] + [period for period in self.periods]
        self.periods_with_end = [period for period in self.periods] + [str(len(self.periods) + 1)]

    def create_rnd(self, folder = 'instances/synthetic'):
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

        if self.parameters['patronizing'] == 'none':
            patronizing = 0.00
        elif self.parameters['patronizing'] == 'weak':
            patronizing = 0.10
        elif self.parameters['patronizing'] == 'medium':
            patronizing = 0.30
        elif self.parameters['patronizing'] == 'strong':
            patronizing = 0.50
        else:
            exit('Wrong value for patronizing parameter')

        consideration_size = int(np.ceil(patronizing * number_locations))

        consideration_sets = {}
        for customer in self.customers:
            consideration_sets[customer] = np.random.choice(self.locations, consideration_size)

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location in consideration_sets[customer] or location == customer else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                popularity = sum([self.catalogs[location][customer] for customer in self.customers])
                if self.parameters['rewards'] == 'identical':
                    coefficient = 1.
                elif self.parameters['rewards'] == 'inversely':
                    coefficient = 1. / popularity
                elif self.parameters['rewards'] == 'directly':
                    coefficient = 1. - 1. / popularity
                else:
                    exit('Wrong value for rewards parameter')
                self.revenues[period][location] = np.ceil(coefficient * 10)

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
                    return abs((self.starts[customer] + self.intensities[customer] * len(self.periods)) - result)
                def minimize_combination():
                    best_alpha = 0.01
                    best_beta = 0.1
                    best_value = 10**4
                    for alpha in range(1, 101):
                        local_alpha = float(alpha/1000)
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

    def create_planB(self, folder = 'instances/synthetic'):
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
                self.catalogs[location][customer] = 1. if location in consideration_sets[customer] or location == customer else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                popularity = sum([self.catalogs[location][customer] for customer in self.customers])
                if self.parameters['rewards'] == 'identical':
                    coefficient = 1.
                elif self.parameters['rewards'] == 'inversely':
                    coefficient = 1. / popularity
                else:
                    exit('Wrong value for rewards parameter')
                self.revenues[period][location] = np.ceil(coefficient * 10)

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

    def create_spp(self, K = 5):
        # Create SPP instances

        elements = ['1', '2', '3', '4', '5']
        collections = [['1', '2', '3', '4', '5'], ['1'], ['2'], ['3'], ['4'], ['5']]

        self.locations = [str(i + 1) for i in range(0, len(collections))]
        self.customers = [e for e in elements]
        self.periods = [str(i + 1) for i in range(0, K)]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if customer in collections[int(location)-1] else 0.

        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1/len(collections[int(location)-1])
                if location == '1':
                    # Avoid ambiguity for heuristic
                    self.revenues[period][location] = 0.21

        self.alphas = {}
        self.betas = {}
        self.starts = {}
        for customer in self.customers:
            self.alphas[customer] = 0
            self.betas[customer] = 0
            self.starts[customer] = 1

    def create_3sat(self, folder = 'instances/3sat'):
        # Create 3SAT instances

        with open('{}/{}'.format(folder, self.keyword), 'r') as content:
            clauses = []
            for line in content:
                if 'p' in line:
                    line = line.strip().split(' ')
                    variables = [str(i + 1) for i in range(0, int(line[2]))]
                elif 'c' not in line:
                    line = line.strip().split(' ')
                    if len(line) == 4:
                        clauses.append([line[0], line[1], line[2]])
                    else:
                        print('Skipped: {}'.format(line))
                else:
                    print('Skipped: {}'.format(line))

        self.locations = [variable for variable in variables] + ['-' + variable for variable in variables]
        self.customers = ['c{}'.format(index + 1) for index, _ in enumerate(clauses)] + ['v{}'.format(variable) for variable in variables]
        self.periods = [variable for variable in variables]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for index, customer in enumerate(self.customers):
                if 'c' in customer:
                    self.catalogs[location][customer] = 1. if location in clauses[int(customer.replace('c', '')) - 1] else 0.
                elif 'v' in customer:
                    self.catalogs[location][customer] = 1. if int(customer.replace('v', '')) == int(location.replace('-','')) else 0.
                else:
                    print('customer: {}'.format(customer))
                    exit('Error, unexpected type of customer')

        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1

        self.alphas = {}
        self.betas = {}
        self.starts = {}
        for customer in self.customers:
            self.starts[customer] = 1
            self.alphas[customer] = 0
            self.betas[customer] = 0

    def create_rnd1(self):
        # Create RND1 instance

        '''
            Previous key RND1 example could be fixed with a tie breaking rule.
            Here are the configurations: S = 1, T = 4, I = J = 10, delta = 4 * beta
        '''

        seed = int(self.keyword.replace('rnd1', ''))
        self.parameters['seed'] = seed

        self.parameters['S'] = seed
        self.parameters['T'] = 5
        self.parameters['I'] = 10
        self.parameters['J'] = 10

        rd.seed(self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location == customer else 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 1

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.starts = {}

        for customer in self.customers:
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.alphas[customer] = 0
            self.betas[customer] = rd.sample([0,1,2,3,4,5,7,8,9], 1)[0]

    def create_rnd2(self):
        # Create RND2 instance

        seed = int(self.keyword.replace('rnd2', ''))
        self.parameters['seed'] = seed

        self.parameters['S'] = seed
        try:
            self.parameters['T']
        except:
            self.parameters['T'] = 3
        self.parameters['I'] = 5
        self.parameters['J'] = 5

        rd.seed(self.parameters['S'])

        # Set instance size
        number_locations = int(self.parameters['I'])
        number_customers = int(self.parameters['J'])
        number_periods = int(self.parameters['T'])

        self.locations = [str(i + 1) for i in range(number_locations)]
        self.customers = [str(i + 1) for i in range(number_customers)]
        self.periods = [str(i + 1) for i in range(number_periods)]

        # Create catalogs
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            maximum = rd.sample([0.1 * self.parameters['J'], 0.3 * self.parameters['J'], 0.5 * self.parameters['J']], 1)[0]
            assigned = 0
            for customer in self.customers:
                self.catalogs[location][customer] = 1. if location == customer else rd.sample([0.,1.], 1)[0]
                assigned += self.catalogs[location][customer]
                if location != customer and assigned > maximum:
                    self.catalogs[location][customer] = 0.

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = 1

        # Handle customers
        self.alphas = {}
        self.betas = {}
        self.starts = {}

        for customer in self.customers:
            self.starts[customer] = rd.sample([1,2,3,4,5,6,7,8,9,10], 1)[0]
            self.alphas[customer] = 0
            self.betas[customer] = rd.sample([0,1,2,3,4,5,7,8,9], 1)[0]

    '''
        Create instance used for approximation proof
    '''
    def create_approx(self):
        # Create approx instance

        self.locations = ['1', '2', '3']
        self.customers = ['A','B', 'C', 'D', 'E']
        self.periods = ['1', '2']

        # Create catalogs
        considerations = {}
        considerations ['A'] = ['1', '3']
        considerations ['B'] = ['1', '2']
        considerations ['C'] = ['1', '2', '3']
        considerations ['D'] = ['2']
        considerations ['E'] = ['3']
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in considerations[customer] else 0

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] =  1

        # Create alphas
        self.alphas = {}
        for customer in self.customers:
            self.alphas[customer] = 0

        # Create betas
        self.betas = {}
        for customer in self.customers:
            self.betas[customer] = 0

        # Create start values
        self.starts = {}
        for customer in self.customers:
            self.starts[customer] = 1

    '''
        Create instance used for JOPT presentation
    '''
    def create_jopt(self):
        # Create JOPT instance

        self.locations = ['1', '2', '3', '4']
        self.customers = ['A', 'B', 'C']
        self.periods = ['1', '2', '3']

        # Create catalogs
        considerations = {}
        considerations ['A'] = ['1', '2', '4']
        considerations ['B'] = ['1', '3', '4']
        considerations ['C'] = ['2', '3', '4']
        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if location in considerations[customer] else 0

        revenues = {'1': 4., '2': 4., '3': 4., '4': 3.}

        # Create revenues
        self.revenues = {}
        for period in self.periods:
            self.revenues[period] = {}
            for location in self.locations:
                self.revenues[period][location] = revenues [location]

        # Create alphas
        self.alphas = {}
        for customer in self.customers:
            self.alphas[customer] = 0

        # Create betas
        self.betas = {}
        self.betas['A'] = 1
        self.betas['B'] = 1
        self.betas['C'] = 1

        # Create start values
        self.starts = {}
        self.starts['A'] = 0.
        self.starts['B'] = 0.
        self.starts['C'] = 0.

    def print_instance(self):
        # Print stored instance

        print('Keyword: <{}>'.format(self.keyword))

        print('Customers: {}'.format(self.customers))
        print('\t| j: a\tb\ts\t[L]\t(M)')
        for customer in self.customers:
            print('\t| {}: {}\t{}\t{}\t{}\t({})'.format(
                customer,
                self.alphas[customer],
                self.betas[customer],
                self.starts[customer],
                self.captured_locations(customer),
                self.limits[customer]))

        print('Locations: {}'.format(self.locations))
        for location in self.locations:
            print('\t| {} ({}) : {}'.format(location, self.revenues['1'][location], self.captured_customers(location)))

    def captured_customers(self, location):
        # Retrieve customers captured by some location

        return [customer for customer in self.customers if self.catalogs[location][customer] == 1]

    def captured_locations(self, customer):
        # Retrieve locations capturing some customer

        return [location for location in self.locations if self.catalogs[location][customer] == 1]

    def partial_demand(self, lastly, current, customer):
        # Compute phi function within formulations

        lastly, current = int(lastly), int(current)

        accumulated = .0

        if lastly == 0:
            accumulated += self.starts[customer]

        for period in self.periods:

            if int(period) > lastly and int(period) <= current:

                accumulated += self.alphas[customer] * accumulated + self.betas[customer]

        '''
        if current == len(self.periods) + 1:
            exit('This should never happen!')
        elif lastly == 0:
            return self.starts[customer] +  current * self.betas[customer]
        else:
            return self.betas[customer] * (current - lastly)
        '''

        return accumulated

    def is_identical_rewards(self):
        # Verify if rewards are identical or not

        for period in self.periods:
            for location in self.locations:
                if self.revenues[period][location] != self.revenues[self.periods[0]][self.locations[0]]:
                    return False

        return True

    def is_absolute_replenishment(self):
        # Verify if there is no relative replenishment

        for customer in self.customers:
            if self.alphas[customer] != 0:
                return False

        return True