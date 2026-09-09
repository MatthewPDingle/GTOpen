"""Self-contained scientific input-integrity checks; no private histories used."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

spec=importlib.util.spec_from_file_location('transfer_integrity',Path(__file__).with_name('transfer_validation.py'))
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)


class CollectionIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'histories';self.private=self.root/'private'
        self.out=self.root/'public';self.artifact=self.root/'artifact.json'
        self.artifact.write_text(json.dumps({'baseline':{}}),encoding='utf-8')
        for name in set(t.COLLECTOR_FILES+t.PREDICTOR_FILES):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('frozen fixture source',encoding='utf-8')
        self.constants=patch.multiple(t,ROOT=self.root,OUT=self.out,ARTIFACT=self.artifact,SHA=t.sha256(self.artifact))
        self.constants.start();self.addCleanup(self.constants.stop)
        for i,(stake,zone) in enumerate([(10,False)]+t.GROUPS):
            path=self.source/t.group_name(stake,zone)/'session.txt';path.parent.mkdir(parents=True)
            path.write_text(f'Ignition Hand #{100+i}\nfixture only\n',encoding='utf-8')
        self.analyzer=SimpleNamespace(source_paths=lambda source,stake=10,zone=False:sorted((source/t.group_name(stake,zone)).glob('*.txt')),run=self.fake_run)

    def fake_run(self,source,out,stake,zone):
        out.mkdir(parents=True,exist_ok=True)
        data=dict(schema=4,site='Ignition',stake=f'NL{stake} {"Zone" if zone else "regular"}',
            audit={'accepted':1},sessions=[dict(id='fixture',first='2026-01-01',last='2026-01-01',reraise_cells={})])
        (out/'analysis.json').write_text(json.dumps(data),encoding='utf-8')

    def collect(self):
        with patch.object(t,'module',return_value=self.analyzer),contextlib.redirect_stdout(io.StringIO()):
            t.collect(self.source,self.private)

    def manifest(self):return json.loads((self.private/t.MANIFEST).read_bytes())

    def write_manifest(self,value):
        (self.private/t.MANIFEST).write_text(json.dumps(value),encoding='utf-8')

    def test_collection_binds_inputs_and_public_result_has_only_manifest_digest(self):
        self.collect();inputs,digest=t.verify_collection(self.private)
        self.assertEqual(len(inputs),4)
        predictor=SimpleNamespace(observations=lambda sessions:(np.empty((0,8)),np.empty((0,3)),np.empty(0)))
        with patch.object(t,'module',return_value=predictor),contextlib.redirect_stdout(io.StringIO()):
            t.evaluate(self.private)
        result=json.loads((self.out/'evaluation.json').read_bytes())
        self.assertEqual(result['collection_manifest_sha256'],digest)
        self.assertNotIn('training',result);self.assertNotIn('overlap_check',result)
        text=json.dumps(result)
        self.assertNotIn('hand_ids',text);self.assertNotIn('session.txt',text)
        self.assertNotIn(str(self.source),text)

    def test_missing_manifest_refuses_before_loading_predictor(self):
        t.protocol()
        with patch.object(t,'module',side_effect=AssertionError('Predictor must not load')):
            with self.assertRaisesRegex(t.IntegrityError,'Missing collection manifest'):t.evaluate(self.private)

    def test_modified_analysis_rejected_and_existing_result_preserved(self):
        self.collect();path=self.private/'NL5-regular/analysis.json'
        path.write_bytes(path.read_bytes()+b' ')
        result=self.out/'evaluation.json';result.write_text('previous result')
        with self.assertRaisesRegex(t.IntegrityError,'Analysis hash mismatch'):t.evaluate(self.private)
        self.assertEqual(result.read_text(),'previous result')

    def test_schema_site_stake_and_bound_metadata_must_match_even_with_new_hash(self):
        self.collect();original_manifest=self.manifest();path=self.private/'NL5-regular/analysis.json';original_data=json.loads(path.read_bytes())
        for field,value in [('schema',3),('site','CoinPoker'),('stake','NL25 regular')]:
            with self.subTest(field=field):
                data={**original_data,field:value};path.write_text(json.dumps(data),encoding='utf-8')
                manifest=copy.deepcopy(original_manifest);manifest['groups']['NL5-regular']['analysis_sha256']=t.sha256(path)
                self.write_manifest(manifest)
                with self.assertRaisesRegex(t.IntegrityError,'Analysis metadata mismatch'):t.verify_collection(self.private)
        path.write_text(json.dumps(original_data),encoding='utf-8')
        manifest=copy.deepcopy(original_manifest);manifest['groups']['NL5-regular']['analysis_sha256']=t.sha256(path)
        manifest['groups']['NL5-regular']['analysis_metadata']['validated_sessions']=99;self.write_manifest(manifest)
        with self.assertRaisesRegex(t.IntegrityError,'Collection metadata mismatch'):t.verify_collection(self.private)

    def test_manifest_protocol_model_and_collector_changes_rejected(self):
        self.collect();original=self.manifest()
        for key in ['protocol_sha256','model_sha256','collector_sha256']:
            with self.subTest(key=key):
                m=copy.deepcopy(original);m[key]='stale';self.write_manifest(m)
                with self.assertRaises(t.IntegrityError):t.verify_collection(self.private)
        self.write_manifest(original)
        (self.root/t.COLLECTOR_FILES[1]).write_text('changed collector')
        with self.assertRaisesRegex(t.IntegrityError,'Collector source changed'):t.verify_collection(self.private)

    def test_each_transitive_predictor_helper_change_refuses_scoring(self):
        self.collect()
        for name in t.PREDICTOR_FILES:
            with self.subTest(helper=name):
                path=self.root/name;original=path.read_bytes()
                path.write_bytes(original+b'\nchanged helper')
                with patch.object(t,'module',side_effect=AssertionError('Predictor must not load')):
                    with self.assertRaisesRegex(t.IntegrityError,'Predictor source or helper changed'):t.evaluate(self.private)
                path.write_bytes(original)

    def test_training_or_cross_group_overlap_rejected_at_collection(self):
        for source_name in ['NL10-regular','NL5-regular']:
            with self.subTest(source=source_name):
                target=self.source/'NL25-zone/session.txt';saved=target.read_bytes()
                target.write_bytes((self.source/source_name/'session.txt').read_bytes())
                with self.assertRaisesRegex(t.IntegrityError,'Overlapping training/evaluation'):self.collect()
                self.assertFalse((self.private/t.MANIFEST).exists())
                target.write_bytes(saved)

    def test_manifest_recomputes_overlap_and_requires_complete_groups(self):
        self.collect();original=self.manifest()
        m=copy.deepcopy(original);m['groups']['NL25-zone']['hand_ids']=m['training']['hand_ids'];self.write_manifest(m)
        with self.assertRaisesRegex(t.IntegrityError,'Overlapping training/evaluation'):t.verify_collection(self.private)
        m=copy.deepcopy(original);m['overlap_check']['comparisons'][0]['overlapping_hand_ids']=1;self.write_manifest(m)
        with self.assertRaisesRegex(t.IntegrityError,'Overlap-check provenance mismatch'):t.verify_collection(self.private)
        m=copy.deepcopy(original);del m['groups']['NL25-zone'];self.write_manifest(m)
        with self.assertRaisesRegex(t.IntegrityError,'Collection group set mismatch'):t.verify_collection(self.private)

    def test_source_changes_during_recollection_invalidate_old_manifest(self):
        self.collect()
        def changed_run(source,out,stake,zone):
            self.fake_run(source,out,stake,zone)
            (source/t.group_name(stake,zone)/'session.txt').write_text('Ignition Hand #999\nchanged')
        self.analyzer.run=changed_run
        with self.assertRaisesRegex(t.IntegrityError,'Source changed during collection'):self.collect()
        self.assertFalse((self.private/t.MANIFEST).exists())


if __name__=='__main__':unittest.main()
