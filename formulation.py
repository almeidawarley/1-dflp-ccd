import gurobipy as gp
import variables as vb
import constraints as ct
import common as cm

def warm_start(instance, variable, solution):
    # Warm start with a feasible solution

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].start  = 1. if location == solution[period] else 0.

def build_simplified_mip(instance):
    # Build the MIP of the simplified DSFLP-C (i.e., DSFLP)

    mip = gp.Model('DSFLP')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', cm.TIMELIMIT)

    mip.setObjective(
        sum([instance.revenues[period][location] *
         instance.accumulated_demand(instance.start, period, customer) *
         instance.catalogs[location][customer] *
         variable['y'][period, location]
         for period in instance.periods
         for location in instance.locations
         for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)

    return mip, variable

def build_linearized_mip(instance):
    # Build the MIP of the linearized DSFLP-C

    mip = gp.Model('DSFLP-C-LRZ')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'w': vb.create_vrw(instance, mip),
        'b': vb.create_vrb(instance, mip),
        'c': vb.create_vrc(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', cm.TIMELIMIT)

    # Set objective function
    mip.setObjective(
        sum([instance.revenues[period][location] *
             variable['w'][period, location, customer]
             for period in instance.periods
             for location in instance.locations
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c2(instance, mip, variable)
    ct.create_c3(instance, mip, variable)
    ct.create_c4(instance, mip, variable)
    ct.create_c5A(instance, mip, variable)
    ct.create_c5B(instance, mip, variable)
    ct.create_c5C(instance, mip, variable)
    ct.create_c5D(instance, mip, variable)

    return mip, variable

def relax_linearized_mip(instance, mip, variable):
    # Build the LPR of the linearized DSFLP-C

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].vtype = 'C'

    # mip.setParam('OutputFlag', 0)

    return mip, variable

def build_networked_mip(instance):
    # Build the MIP of the networked DSFLP-C

    mip = gp.Model('DSFLP-C-NET')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'z': vb.create_vrz(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', cm.TIMELIMIT)

    # Set objective function
    mip.setObjective(
        sum([instance.revenues[period2][location] *
         instance.accumulated_demand(period1, period2, customer) *
         variable['z'][period1, period2, location, customer]
         for period1 in instance.periods_with_start
         for period2 in instance.periods
         for location in instance.locations
         for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c6(instance, mip, variable)
    ct.create_c7(instance, mip, variable)
    ct.create_c8(instance, mip, variable)

    return mip, variable

def relax_networked_mip(instance, mip, variable):
    # Build the LPR of the networked DSFLP-C

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].vtype = 'C'

    return mip, variable

def build_nonlinear_mip(instance):
    # Build the MIP of the nonlinear DSFLP-C

    mip = gp.Model('DSFLP-C-NLR')

    # Create decision variables
    variable = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'w': vb.create_vrw_2(instance, mip),
        'b': vb.create_vrb(instance, mip),
        'c': vb.create_vrc(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', cm.TIMELIMIT)

    # Set objective function
    mip.setObjective(
        sum([instance.revenues[period][location] *
             instance.catalogs[location][customer] *
             variable['w'][period, customer] *
             variable['y'][period, location]
             for period in instance.periods
             for location in instance.locations
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c2(instance, mip, variable)
    ct.create_c3(instance, mip, variable)
    ct.create_c4_NL(instance, mip, variable)
    ct.create_c5_NL(instance, mip, variable)

    return mip, variable

def build_master(instance):
    # Build MIP of the master problem within Benders

    # Creater master program
    mip = gp.Model('DSFLP-C-MP')

    # Create decision variables
    var = {
        # Main decision variables
        'y': vb.create_vry(instance, mip),
        'v': vb.create_vrv(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', cm.TIMELIMIT)
    # Activate lazy constraints
    mip.setParam('LazyConstraints', 1)

    # Set objective function
    mip.setObjective(
        sum([var['v'][customer]
             for customer in instance.customers]))

    # Create main constraints
    ct.create_c1(instance, mip, var)

    return mip, var

def build_subproblem(instance, customer):
    # Build MIP of the subproblem within Benders

    mip = gp.Model('DSFLP-C-S{}'.format(customer))
    var = {
        # Main decision variables
        'p': vb.create_vrp(instance, mip),
        'q': vb.create_vrq(instance, mip)
    }

    # Minimize dual objective
    mip.setAttr('ModelSense', 1)

    # Turn off GUROBI logs
    mip.setParam('OutputFlag', 0)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', cm.TIMELIMIT)

    # Update slave programs
    mip.setObjective(
        var['q'][instance.start]
    )

    ct.create_c9(instance, mip, var, customer)

    return mip, var