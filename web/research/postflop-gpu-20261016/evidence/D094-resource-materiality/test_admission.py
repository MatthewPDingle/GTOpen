"""Admission checks at allocation boundaries and independent failure conditions."""
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
FILE=Path(r'X:\Dev\GTOpen-gpu-research-20261016\tools\postflop_resource_admission.py')
spec=importlib.util.spec_from_file_location('resource_admission',FILE)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
proof=json.loads((ROOT/'runs/D094-resource-materiality/report.json').read_text())
historical=json.loads((ROOT/'runs/E057-resource/report.json').read_text())

class Admission(unittest.TestCase):
    def pair(self):
        r=historical['details']['rainbow_p0']
        return copy.deepcopy(r['baseline']),copy.deepcopy(r['candidate'])

    def test_actual_retained_driver_geometries(self):
        for shape,pair in historical['details'].items():
            with self.subTest(shape=shape):
                result=module.evaluate_pair(pair['baseline'],pair['candidate'],proof)
                self.assertEqual(result['status'],'admit_numerical_controls')
                self.assertEqual(result['allocated_registers_per_warp'],[1280,1280])
                self.assertFalse(result['candidate_accepted'])
                self.assertFalse(result['performance_qualified'])

    def test_next_quantum_rejects_even_with_unchanged_occupancy(self):
        b,c=self.pair();c['registers']=41
        result=module.evaluate_pair(b,c,proof)
        self.assertEqual(result['allocated_registers_per_warp'],[1280,1536])
        self.assertEqual(result['status'],'reject_resource_prefilter')
        self.assertFalse(result['gates']['allocated_registers_not_increased'])

    def test_previous_quantum_boundary_and_reduction(self):
        b,c=self.pair();b['registers']=32;c['registers']=33
        self.assertEqual(module.evaluate_pair(b,c,proof)['status'],'reject_resource_prefilter')
        b['registers']=33;c['registers']=32
        self.assertEqual(module.evaluate_pair(b,c,proof)['status'],'admit_numerical_controls')

    def test_each_other_resource_cost_rejects(self):
        changes=[('local_bytes_per_thread',4),('static_shared_bytes',4),
                 ('dynamic_shared_bytes',4),('max_threads',-1)]
        for key,delta in changes:
            with self.subTest(cost=key):
                b,c=self.pair();c[key]=b[key]+delta
                self.assertEqual(module.evaluate_pair(b,c,proof)['status'],'reject_resource_prefilter')

    def test_driver_occupancy_or_limits_cannot_be_waived_by_rounding(self):
        b,c=self.pair();c['occupancy_by_threads'][1][1]-=1
        self.assertEqual(module.evaluate_pair(b,c,proof)['status'],'reject_resource_prefilter')
        b,c=self.pair();c['fits_default_limits']=False
        self.assertEqual(module.evaluate_pair(b,c,proof)['status'],'reject_resource_prefilter')

    def test_missing_or_wrong_device_proof_refuses_admission(self):
        for change in ['status','device','retained_driver_matches']:
            invalid=copy.deepcopy(proof);invalid.pop(change)
            b,c=self.pair()
            with self.subTest(missing=change),self.assertRaises(ValueError):
                module.evaluate_pair(b,c,invalid)

    def test_missing_or_misaligned_driver_observations_refuse_admission(self):
        b,c=self.pair();c['occupancy_by_threads'].pop()
        with self.assertRaises(ValueError):module.evaluate_pair(b,c,proof)
        b,c=self.pair();c['occupancy_by_threads'][0][0]=32
        with self.assertRaises(ValueError):module.evaluate_pair(b,c,proof)
        b,c=self.pair();c['registers']=True
        with self.assertRaises(ValueError):module.evaluate_pair(b,c,proof)

if __name__=='__main__':unittest.main(verbosity=2)
