import instance as ic

class debugging(ic.instance):

    def __init__(self, keyword, project):

        super().__init__(keyword, project)

    def create_instance(self):

        # Decide instance type
        if self.keyword == 'jopt':
            # Create JOPT instance
            self.create_jopt()
        elif self.keyword == 'approx':
            # Create approx instance
            self.create_approx()
        elif self.keyword == 'spp':
            # Create SPP instance
            self.create_spp()
        elif self.keyword == 'proof':
            # Create proof instance
            self.create_proof()
        else:
            exit('Invalid instance keyword')

    def create_spp(self, K = 5):
        # Create SPP instances

        elements = ['1', '2', '3', '4', '5']
        collections = [['1', '2', '3', '4', '5'], ['1'], ['2'], ['3'], ['4'], ['5']]

        self.locations = [str(i + 1) for i in range(0, len(collections))]
        self.customers = [e for e in elements]
        self.periods = [int(i + 1) for i in range(0, K)]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if customer in collections[int(location)-1] else 0

        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                self.rewards[period][location] =  1/len(collections[int(location)-1])
                if location == '1':
                    # Avoid ambiguity for heuristic
                    self.rewards[period][location] = 0.21

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1. if period == 1 else 0.

    def create_proof(self, K = 2):
        # Create proof instance

        elements = ['1', '2']
        collections = [['1'], ['2'], ['1', '2']]

        self.locations = [str(i + 1) for i in range(0, len(collections))]
        self.customers = [e for e in elements]
        self.periods = [int(i + 1) for i in range(0, K)]

        self.catalogs = {}
        for location in self.locations:
            self.catalogs[location] = {}
            for customer in self.customers:
                self.catalogs[location][customer] = 1 if customer in collections[int(location)-1] else 0

        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                self.rewards[period][location] =  1/len(collections[int(location)-1])
                if location == '3':
                    # Avoid ambiguity for heuristic
                    self.rewards[period][location] = 0.51

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1. if period == 1 else 0.

    '''
        Create instance used for approximation proof
    '''
    def create_approx(self):
        # Create approx instance

        self.locations = ['1', '2', '3']
        self.customers = ['A','B', 'C', 'D', 'E']
        self.periods = [1, 2]

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

        # Create rewards
        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                self.rewards[period][location] =  1

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1. if period == 1 else 0.

    '''
        Create instance used for JOPT presentation
    '''
    def create_jopt(self):
        # Create JOPT instance

        self.locations = ['1', '2', '3', '4']
        self.customers = ['A', 'B', 'C']
        self.periods = [1, 2, 3]#, 4]

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

        rewards = {'1': 4., '2': 4., '3': 4., '4': 3.}

        # Create rewards
        self.rewards = {}
        for period in self.periods:
            self.rewards[period] = {}
            for location in self.locations:
                self.rewards[period][location] = rewards [location]

        # Create spawning
        self.spawning = {}
        for period in self.periods:
            self.spawning[period] = {}
            for customer in self.customers:
                self.spawning[period][customer] = 1.