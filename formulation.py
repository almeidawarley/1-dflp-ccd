import gurobipy as gp
import variables as vb
import constraints as ct
import validation as vd

def build_simple(instance, method):
    # Build the 1-DFLP

    mip = gp.Model('1-DFLP')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    # mip.setParam('NumericFocus', 3)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', 60 * 60 * 6)

    # Create main constraints
    ct.create_c1(instance, mip, variable)

    # Create cumulative demands
    cumulative = {}
    for customer in instance.customers:
        cumulative[customer] = instance.starts[customer]

    # Compute capturable demands
    for period in instance.periods:
        if method in ['2', '3']:
            cumulative = vd.apply_replenishment(instance, cumulative)
        for location in instance.locations:
            coefficient = vd.evaluate_location(instance, cumulative, location)
            variable['y'][period, location].obj = coefficient
        if method in ['3']:
            cumulative = vd.apply_absorption(instance, cumulative, location, -1)
            cumulative = vd.apply_consolidation(instance, cumulative)

    return mip, variable

def build_fancy(instance):
    # Build the 1-DFLP-DRA

    mip = gp.Model('1-DFLP-DRA')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, mip),
        'w': vb.create_vrw(instance, mip),
        'd1': vb.create_vrd1(instance, mip),
        'd2': vb.create_vrd2(instance, mip),
        'd3': vb.create_vrd3(instance, mip),
        's': vb.create_vrs(instance, mip),
        't': vb.create_vrt(instance, mip),
        'u': vb.create_vru(instance, mip),
        'v': vb.create_vrv(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)
    # mip.setParam('NumericFocus', 3)
    mip.setParam('Threads', 1)
    mip.setParam('TimeLimit', 60 * 60 * 6)

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c2(instance, mip, variable)
    ct.create_c3A(instance, mip, variable)
    ct.create_c3B(instance, mip, variable)
    ct.create_c3C(instance, mip, variable)
    ct.create_c3D(instance, mip, variable)
    ct.create_c4(instance, mip, variable)
    ct.create_c5A(instance, mip, variable)
    ct.create_c5B(instance, mip, variable)
    ct.create_c5C(instance, mip, variable)
    ct.create_c5D(instance, mip, variable)
    ct.create_c6A(instance, mip, variable)
    ct.create_c6B(instance, mip, variable)
    ct.create_c6C(instance, mip, variable)
    ct.create_c6D(instance, mip, variable)
    ct.create_c6E(instance, mip, variable)
    ct.create_c6F(instance, mip, variable)
    ct.create_c6G(instance, mip, variable)
    ct.create_c6H(instance, mip, variable)

    return mip, variable

def warm_start(instance, variable, solution):
    # Warm start with a feasible solution

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].start  = 1. if location == solution[period] else 0.