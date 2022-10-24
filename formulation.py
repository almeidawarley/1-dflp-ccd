import gurobipy as gp
import variables as vb
import constraints as ct

def build(instance):
    # Build linear DSFLP-DRA

    model = gp.Model('DSFLP-DRA')

    # Create decision variables
    variable = {
        'ys': vb.create_vry(instance, model),
        'ws': vb.create_vrw(instance, model),
        'd1s': vb.create_vrd1(instance, model),
        'd2s': vb.create_vrd2(instance, model)
    }

    # Maximize the total revenue
    model.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    # model.setParam('OutputFlag', 0)

    # Create main constraints
    ct.create_c1(instance, model, variable)
    ct.create_c2(instance, model, variable)
    ct.create_c3(instance, model, variable)
    ct.create_c4(instance, model, variable)
    # ct.create_c5(instance, model, variable)
    ct.create_c6(instance, model, variable)
    # ct.create_c7(instance, model, variable)
    # ct.create_c8(instance, model, variable)
    ct.create_c9(instance, model, variable)
    ct.create_c10(instance, model, variable)
    ct.create_c11(instance, model, variable)

    return model, variable