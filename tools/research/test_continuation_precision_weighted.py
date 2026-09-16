import unittest
import numpy as np
import continuation_precision_weighted as run


class WeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cases=run.study.fit.load_cases('train')[:2]

    def test_hundred_board_cases_reproduce_the_original_fit(self):
        original=run.study.fit.fit(self.cases,'shape',.1)
        for power in [0.,.5,1.]:
            model=run.fit(self.cases,power)
            for c in self.cases:
                np.testing.assert_allclose(run.study.fit.predict(c,model),run.study.fit.predict(c,original),atol=1e-11,rtol=0)

    def test_splitting_identical_weighted_copies_is_neutral(self):
        # Synthetic replication test: keep targets/features identical, split
        # the first case's unit precision weight into five 0.2-weight copies.
        original=run.fit(self.cases,1.)
        split=[dict(self.cases[0],rows=self.cases[0]['rows'][:20]) for _ in range(5)]+self.cases[1:]
        actual=run.fit(split,1.)
        self.assertAlmostEqual(actual['effective_case_weight'],original['effective_case_weight'])
        for c in self.cases:
            np.testing.assert_allclose(run.study.fit.predict(c,actual),run.study.fit.predict(c,original),atol=1e-11,rtol=0)


if __name__=='__main__':unittest.main()
