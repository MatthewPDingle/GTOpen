import math
import unittest
from run_paired_expansion import metadata_adapter


class MetadataChecks(unittest.TestCase):
    def test_only_float_roundtrip_is_accepted(self):
        job=dict(id='case',inclusion_probability=.011834319526627219,config=dict(pot=5))
        actual=dict(job,inclusion_probability=math.nextafter(job['inclusion_probability'],1))
        corrections={};seen=[]
        validate=metadata_adapter(lambda row,j,m:seen.append(row['job']==j),corrections)
        validate(dict(job=actual),job,{})
        self.assertEqual(seen,[True]);self.assertIn('case',corrections)
        self.assertNotEqual(actual['inclusion_probability'],job['inclusion_probability'])
        with self.assertRaises(AssertionError):
            validate(dict(job=dict(actual,config=dict(pot=6))),job,{})
        with self.assertRaises(AssertionError):
            validate(dict(job=dict(actual,inclusion_probability=.02)),job,{})


if __name__=='__main__':unittest.main()
