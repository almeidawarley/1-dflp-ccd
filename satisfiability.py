import instance as ic

class satisfiability(ic.instance):

    def __init__(self, keyword, project):

        super().__init__(keyword, project)

    def create_instance(self, folder = 'instances/satisfiability'):
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

        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                self.rewards[period][location] =  1

        self.alphas = {}
        self.betas = {}
        self.starts = {}
        for customer in self.customers:
            self.starts[customer] = 1
            self.alphas[customer] = 0
            self.betas[customer] = 0