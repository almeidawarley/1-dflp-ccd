import gurobipy as gp
import variables as vb
import constraints as ct

def build(instance):
    # Build linear DSFLP-DRA

    model = gp.Model('DSFLP-DRA')

    # Create decision variables
    variable = {
        'y': vb.create_vry(instance, model),
        'w': vb.create_vrw(instance, model),
        'd1': vb.create_vrd1(instance, model),
        'd2': vb.create_vrd2(instance, model),
        'd3': vb.create_vrd3(instance, model),
        'z': vb.create_vrz(instance, model)
    }

    # Maximize the total revenue
    model.setAttr('ModelSense', -1)

    # Turn off GUROBI logs
    model.setParam('OutputFlag', 0)

    # Create main constraints
    ct.create_c1(instance, model, variable)
    ct.create_c2(instance, model, variable)
    ct.create_c3(instance, model, variable)
    ct.create_c4(instance, model, variable)
    ct.create_c5(instance, model, variable)
    ct.create_c6(instance, model, variable)
    ct.create_c7(instance, model, variable)
    ct.create_c8(instance, model, variable)
    ct.create_c9(instance, model, variable)
    ct.create_c10(instance, model, variable)
    ct.create_c11(instance, model, variable)

    return model, variable