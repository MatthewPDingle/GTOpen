import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('migrate_postflop', Path(__file__).with_name('migrate_postflop_contexts.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def evidence():
    return dict(schema=1, site='Ignition', stake='NL10 regular', source_content_sha256=m.CORPUS_SHA,
                source_files=574, audit={'accepted': 34466}, contextual_bets=[
                    dict(street=0, kind='donk', pot_type='three_bet_plus', opportunities=911, bets=131)])


def model():
    return dict(name='Renamed custom library copy', id='keep-id', opaque={'future': [1, 2]},
        source=dict(site='Ignition', stakes='NL10 regular', type='anonymous_pool', unique_hands=34466,
                    sessions=555, date_from='2025-08-20', date_to='2025-12-02', version='some-prior-version'),
        stats=dict(vpip=44, dataset=dict(site='Ignition NL10 regular', rows=[{'painted': [.1, .2, .3]}])),
        postflop=copy.deepcopy(m.BASE_POSTFLOP))


class MigrationTests(unittest.TestCase):
    def test_renamed_copy_matches_provenance_and_preserves_everything_else(self):
        source = [model()]
        before = copy.deepcopy(source)
        output, summary = m.migrate(source, evidence())
        self.assertEqual(len(summary['updated']), 1)
        self.assertEqual(source, before)
        self.assertEqual(output[0]['postflop'].pop('contextual_betting'), m.wrapper(evidence()))
        self.assertEqual(output, before)

    def test_matching_name_without_provenance_is_not_evidence(self):
        source = model()
        source['name'] = 'Data · Ignition · NL10 regular · Pool'
        source.pop('source')
        output, summary = m.migrate([source], evidence())
        self.assertEqual(output, [source])
        self.assertEqual(len(summary['skipped']), 1)

    def test_edited_postflop_fields_are_preserved(self):
        for field, value in [('donk', 25.26), ('raise_bet', 9), ('cbet', [62.72,55.23,50.95]),
                             ('fold_to_bet', [44.69,45.7,53.87]), ('bet_size', 'max')]:
            with self.subTest(field=field):
                source = model()
                source['postflop'][field] = value
                output, summary = m.migrate([source], evidence())
                self.assertEqual(output, [source])
                self.assertEqual(len(summary['skipped']), 1)

    def test_float32_roundoff_is_accepted(self):
        source = model()
        source['postflop']['cbet'][0] = 62.72999954223633
        self.assertEqual(len(m.migrate([source], evidence())[1]['updated']), 1)

    def test_wrong_stake_or_population_is_skipped(self):
        for field, value in [('stakes', 'NL10 Zone'), ('type', 'loose_passive'), ('unique_hands', 34465)]:
            source = model()
            source['source'][field] = value
            self.assertEqual(len(m.migrate([source], evidence())[1]['skipped']), 1)

    def test_existing_context_is_idempotent_or_preserved(self):
        upgraded, _ = m.migrate([model()], evidence())
        again, summary = m.migrate(upgraded, evidence())
        self.assertEqual(again, upgraded)
        self.assertEqual(len(summary['unchanged']), 1)
        upgraded[0]['postflop']['contextual_betting']['source'] = 'Custom model'
        again, summary = m.migrate(upgraded, evidence())
        self.assertEqual(again, upgraded)
        self.assertEqual(len(summary['skipped']), 1)

    def test_null_context_is_upgraded_without_other_changes(self):
        source = model()
        source['postflop']['contextual_betting'] = None
        self.assertEqual(len(m.migrate([source], evidence())[1]['updated']), 1)

    def test_wrong_source_and_impossible_counts_rejected(self):
        for edit in [lambda e: e.update(stake='NL25 regular'),
                     lambda e: e.update(source_content_sha256='x'*64),
                     lambda e: e['contextual_bets'][0].update(bets=912),
                     lambda e: e['contextual_bets'][0].update(opportunities=True),
                     lambda e: e['contextual_bets'][0].update(street=1),
                     lambda e: e['contextual_bets'].append(e['contextual_bets'][0].copy())]:
            value = evidence()
            edit(value)
            with self.assertRaises(ValueError):
                m.migrate([model()], value)

    def test_dryrun_writes_nothing_and_explicit_output_preserves_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            library, ev, out = root/'library.json', root/'evidence.json', root/'out.json'
            library.write_text(json.dumps([model()]))
            ev.write_text(json.dumps(evidence()))
            raw = library.read_bytes()
            with patch('builtins.print'):
                result = m.run(library, ev)
                self.assertTrue(result['dry_run'])
                m.run(library, ev, out, dry_run=True)
                self.assertFalse(out.exists())
                result = m.run(library, ev, out)
            self.assertTrue(out.exists())
            self.assertEqual(library.read_bytes(), raw)
            self.assertEqual(len(result['updated']), 1)

    def test_inplace_and_live_output_forbidden_even_dryrun(self):
        for output in ['input.json', m.LIVE_LIBRARY, 'evidence.json']:
            with self.assertRaises(ValueError):
                m.run('input.json', 'evidence.json', output, dry_run=True)

    def test_source_newlines_and_trailing_newline_are_preserved(self):
        for newline, trailing in [('\n', ''), ('\n', '\n'), ('\r\n', '\r\n'), ('\r\n', '\r\n\r\n')]:
            with self.subTest(newline=newline, trailing=trailing), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                library, ev, out = root/'library.json', root/'evidence.json', root/'out.json'
                original = [model()]
                library.write_bytes((json.dumps(original, indent=2).replace('\n', newline)+trailing).encode())
                ev.write_text(json.dumps(evidence()))
                with patch('builtins.print'):
                    m.run(library, ev, out)
                expected, _ = m.migrate(original, evidence())
                expected_bytes = (json.dumps(expected, ensure_ascii=False, indent=2).replace('\n', newline)+trailing).encode()
                self.assertEqual(out.read_bytes(), expected_bytes)


if __name__ == '__main__':
    unittest.main()
