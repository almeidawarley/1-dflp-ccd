import gurobipy as gp
import variables as vb
import constraints as ct

def build_linear(instance):
    # Build linear DSFLP-DRA

    mip = gp.Model('DSFLP-DRA')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, mip),
        'w': vb.create_vrw(instance, mip),
        'd1': vb.create_vrd1(instance, mip),
        'd2': vb.create_vrd2(instance, mip),
        'd3': vb.create_vrd3(instance, mip),
        'z': vb.create_vrz(instance, mip)
    }

    # Maximize the total revenue
    mip.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # mip.setParam('OutputFlag', 0)

    # Create main constraints
    ct.create_c1(instance, mip, variable)
    ct.create_c2(instance, mip, variable)
    ct.create_c3(instance, mip, variable)
    ct.create_c4(instance, mip, variable)
    ct.create_c5(instance, mip, variable)
    ct.create_c6(instance, mip, variable)
    ct.create_c7(instance, mip, variable)
    ct.create_c8(instance, mip, variable)
    ct.create_c9(instance, mip, variable)
    # ct.create_c10(instance, mip, variable)
    # ct.create_c11(instance, mip, variable)

    return mip, variable

def warm_start(instance, mip, variable, solution):
    # Warm start with a feasible solution

    for period in instance.periods:
        for location in instance.locations:
            variable['y'][period, location].start  = 1. if location == solution[period] else 0.