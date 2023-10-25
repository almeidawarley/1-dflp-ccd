import unittest
import instance as ic
import heuristic as hr
import formulation as fm
import validation as vd
import pandas as pd

class test_nonlinear_mip(unittest.TestCase):

    def test_objective(self):

        reference = pd.read_csv('experiments/reference.csv')

        reference = reference[reference['absorption'] == 'complete']
        reference = reference[reference['rewards'] != 'directly']
        reference = reference[reference['character'] == 'homogeneous']

        for _, row in reference.iterrows():

            instance = ic.instance(row['keyword'], 'testing')
            instance.print_instance()

            _, frw_objective = hr.forward_algorithm(instance)
            bcw_solution, bcw_objective = hr.backward_algorithm(instance)
            _, prg_objective = hr.progressive_algorithm(instance)
            _, rnd_objective = hr.random_algorithm(instance)

            self.assertEqual(frw_objective, row['frw_objective'])
            self.assertEqual(vd.evaluate_solution(instance, bcw_solution), bcw_objective)
            self.assertEqual(bcw_objective, row['bcw_objective'])
            self.assertEqual(prg_objective, row['prg_objective'])
            self.assertEqual(rnd_objective, row['rnd_objective'])

            mip, _ = fm.build_linearized(instance)
            mip.optimize()
            mip_objective = round(mip.objVal, 2)
            self.assertEqual(mip_objective, row['mip_objective'])

if __name__ == '__main__':

    unittest.main()