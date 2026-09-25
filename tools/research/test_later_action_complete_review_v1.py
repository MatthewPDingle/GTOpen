"""Semantic rejection checks on the previously archived trained-bank fixture."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from later_average_support_v1 import OUT,read,load_complete_cache
from hu_later_action_complete_review_20260925 import verify_batch


class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=OUT/'crossed-trained-bank-control-v1-result.json'
        if not p.exists():raise unittest.SkipTest('Requires the registered local trained-bank control fixture')
        r=read(p);assert r['passed']
        cls.store=Path('T:/GTOpen-research/crossed-trained-bank-control-v1')
        reader=ArchivedEvaluationReader(cls.store,{'test-000000':r['archive_manifest_sha256']},external_files=[],guard=lambda:None)
        names=['query-batch.json','conditional-batch.json','queries.json','profiles.json','native.json','residuals.json','summary.json']
        cls.raw={n:reader.read_bytes(cls.store/'test-000000'/n) for n in names}
        cls.batch=json.loads(cls.raw['query-batch.json'])
        cls.source=(OUT/'bb-context-candidate.json').read_text();cls.cache=load_complete_cache()

    def check(self, name=None, mutate=None):
        raw=copy.deepcopy(self.raw)
        if name:
            value=json.loads(raw[name]);mutate(value)
            raw[name]=(json.dumps(value,separators=(',',':'))+'\n').encode()
            if name!='summary.json':
                summary=json.loads(raw['summary.json'])
                summary['artifacts'][name]=hashlib.sha256(raw[name]).hexdigest()
                raw['summary.json']=(json.dumps(summary,separators=(',',':'))+'\n').encode()
        class MemoryReader:
            def read_bytes(self,p):return raw[p.name]
        return verify_batch(MemoryReader(),self.store/'test-000000',self.batch,self.source,self.cache)

    def test_original(self):
        values,count,_=self.check();self.assertEqual(len(values),1);self.assertEqual(count,455)

    def test_changed_paired_gain(self):
        def corrupt(v):v['values'][0][0]+=.01
        with self.assertRaises(AssertionError):self.check('residuals.json',corrupt)

    def test_changed_actor_policy_even_with_rehashed_artifact(self):
        def corrupt(v):
            row=next(r for r in v['profiles'][1]['policies'] if r['actor']==0)
            row['probabilities']=[1.,0.,0.,0.]
        with self.assertRaises(AssertionError):self.check('profiles.json',corrupt)

    def test_changed_native_deal_index(self):
        def corrupt(v):v['profiles'][0]['deals'][0]['deal_index']=1
        with self.assertRaises(AssertionError):self.check('native.json',corrupt)

    def test_changed_payoff_conservation(self):
        def corrupt(v):v['profiles'][0]['deals'][0]['expected_rake']+=.01
        with self.assertRaises(AssertionError):self.check('native.json',corrupt)

    def test_changed_summary_values(self):
        def corrupt(v):v['values'][0][0][0][0]+=.01
        with self.assertRaises(AssertionError):self.check('summary.json',corrupt)


if __name__=='__main__':unittest.main()
