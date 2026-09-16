import unittest
import continuation_prior_evaluation as evaluation


class PriorEvaluationChecks(unittest.TestCase):
    def test_registered_model_and_queries_match_the_unobserved_source(self):
        manifest,record=evaluation.registered()
        source=evaluation.bridge.checked('evaluation')
        self.assertEqual(manifest['jobs'],source['jobs'])
        self.assertEqual(manifest['boards'],source['boards'])
        self.assertEqual(len(manifest['jobs']),400)
        self.assertEqual(record['source_references_at_registration'],0)
        model=evaluation.study.read(evaluation.OUT/'candidate.json')
        self.assertFalse(set(model['training_families']) & {c['family'] for c in manifest['cases']})

    def test_runner_namespace_does_not_redirect_the_source(self):
        old=evaluation.bridge.OUT;original_fit=evaluation.study.fit
        runner=evaluation.adapter()
        self.assertEqual(runner.OUT,evaluation.OUT)
        self.assertEqual(evaluation.bridge.OUT,old)
        self.assertIs(evaluation.study.fit,original_fit)


if __name__=='__main__':unittest.main()
