"""CPU interruption/corruption checks with artificial contexts and fake payoffs.

No study test hands, trained banks, scientific labels, native solves or GPU use.
All synthetic artifacts are retained; this check never deletes raw evidence.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import time
import traceback
import numpy as np
from stack_context_evaluation_journal_v1 import EvaluationJournal, BATCH, DEALS, protocol
from owned_columnar_evaluation_archive_v1 import durable, digest, encoded, ARTIFACTS
from crossed_complete_policy_comparison_v1 import differences, PROFILE_NAMES
from sampled_physical_deals_v1 import PhysicalDeals

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'stack-context-matched-journal-check-v1'
STORE = Path('S:/GTOpen-research')/NAME
SOURCE = json.dumps(dict(config=dict(stack=20), dead_money=.5, synthetic_test_only=True,
    incoming_class_mass=[[float(i+1) for i in range(169)], [float(169-i) for i in range(169)]]), separators=(',', ':'))
ARGS = dict(context_source=SOURCE, registration_sha256='1'*64, bank_identities_sha256='2'*64,
            cache_sha256='3'*64, guard=lambda:None)
NEGATIVE = []


def canonical(value):
    return (json.dumps(value, separators=(',', ':'), allow_nan=False)+'\n').encode()


def fixture(folder, batch):
    """All values are artificial zero-sum formulae, unrelated to hand strength."""
    folder.mkdir()
    values = np.empty((BATCH,2,4,2))
    for i in range(BATCH):
        for seed in range(2):
            for pair,(bb,btn) in enumerate(((0,0),(0,1),(1,0),(1,1))):
                value = (i-16)/20 + seed/10 + bb*.6 - btn*.3
                values[i,seed,pair] = (value, .5-value)
    parts = {'query-batch.json':canonical(batch)}
    conditional = dict(batch, format=3, terminal_estimator='conditional-preflop-allin-v1',
                       allin_cache_sha256='3'*64, allin_counts=[])
    parts['conditional-batch.json'] = canonical(conditional)
    parts['queries.json'] = canonical(dict(context_source=SOURCE, batch_source=parts['query-batch.json'].decode(),
        observations=[dict(hi='1',lo='0',actor=0,n=2,own_history=[])]))
    profiles = [dict(name=name, policies=[dict(hi='1',lo='0',actor=0,n=2, probabilities=[.5,.5,0.,0.])])
                for name in PROFILE_NAMES]
    parts['profiles.json'] = canonical(dict(format=1, context_source=SOURCE,
        batch_source=parts['conditional-batch.json'].decode(), profiles=profiles))
    flat = values.reshape(BATCH,8,2)
    native = dict(format=2, terminal_estimator='conditional-preflop-allin-v1', postflop_outcomes='sampled-board',
        maximum_forward_cashflow_error=0., maximum_conservation_error=0.,
        profiles=[dict(name=name,deals=[dict(values=row.tolist()) for row in flat[:,i]])
                  for i,name in enumerate(PROFILE_NAMES)])
    parts['native.json'] = canonical(native)
    parts['residuals.json'] = canonical(dict(format=1,purpose='eight-paired-complete-policy-gains',
        values=differences(values).tolist(),bounds_best_response_above=False))
    summary = dict(format=1,purpose='crossed-complete-policy-effectiveness',deals=BATCH,
        values=values.tolist(),profile_order=list(PROFILE_NAMES),allin_cache_sha256='3'*64,
        maximum_forward_cashflow_error=0.,maximum_conservation_error=0.,
        artifacts={name:digest(raw) for name,raw in parts.items()})
    parts['summary.json'] = canonical(summary)
    for name,raw in parts.items():
        durable(folder/name,raw)
    return values, parts


def create(case):
    parent = STORE/case
    parent.mkdir()
    return EvaluationJournal.create(parent/'stack-20', **ARGS)


def rejects(name, fn):
    try:
        fn()
    except (ValueError, FileNotFoundError, KeyError):
        NEGATIVE.append(name)
    else:
        raise AssertionError('Incorrectly accepted: '+name)


class Interrupted(Exception):
    pass


def stop_at(wanted):
    def hook(stage):
        if stage == wanted:
            raise Interrupted(stage)
    return hook


def main():
    attempt = OUT/(NAME+'-attempt.json')
    output = OUT/(NAME+'-result.json')
    failed = OUT/(NAME+'-failure.json')
    if any(p.exists() for p in (STORE,attempt,output,failed)):
        raise ValueError('Preserve existing started or completed control')
    inputs = [Path(__file__).resolve(), Path(__file__).with_name('stack_context_evaluation_journal_v1.py'),
              Path(__file__).with_name('stack_context_matched_analysis_v1.py')]
    durable(attempt, encoded(dict(inputs={str(p):digest(p.read_bytes()) for p in inputs},
        store=str(STORE), synthetic_context_sha256=digest(SOURCE.encode()), actual_study_deals=False,
        maximum_seconds=60, maximum_store_bytes=16000000)))
    STORE.mkdir()
    began = time.monotonic()
    try:
        normal = create('normal')
        # An independent sequential sampler is the restart/chance oracle.
        replay = PhysicalDeals(SOURCE,mode='full_deck',seed=9309020)
        expected = []
        for index in range(2):
            batch,folder = normal.begin()
            assert batch['deals'] == replay.sample(BATCH)['deals']
            values,_ = fixture(folder,batch)
            expected.append(values)
            record = normal.recover_next()
            assert record['completed_deals'] == (index+1)*BATCH
            normal = EvaluationJournal(normal.root, **ARGS)
            restored = normal.prefix(verify_archives=True)
            assert restored['sampler'].checkpoint() == replay.checkpoint()
            assert np.array_equal(restored['values'], np.concatenate(expected))
            assert restored['comparison'].plan.alpha == .05/7
            assert restored['comparison'].plan.looks == (4096,)
        assert normal.recover_next() is None
        truth = differences(np.concatenate(expected))
        assert np.max(abs(np.array([row.mean for row in restored['comparison'].series])-truth.mean(0)))<1e-12
        assert np.max(abs(np.array([row.m2 for row in restored['comparison'].series])-truth.var(0,ddof=1)*(len(truth)-1)))<1e-12
        rejects('interim statistical look', restored['comparison'].finish)

        # A complete raw batch can be committed after interruption, without
        # another sampler/evaluator invocation.
        completed_raw = create('complete-raw')
        batch,folder = completed_raw.begin()
        values,_ = fixture(folder,batch)
        reopened = EvaluationJournal(completed_raw.root, **ARGS)
        assert reopened.recover_next()['completed_deals'] == BATCH
        assert np.array_equal(reopened.prefix(verify_archives=True)['values'],values)

        for stage in ('before-commit','committed'):
            journal = create(stage)
            batch,folder = journal.begin()
            values,_ = fixture(folder,batch)
            try:
                journal.recover_next(on_stage=stop_at(stage))
            except Interrupted:
                pass
            else:
                raise AssertionError('Interruption not injected')
            reopened = EvaluationJournal(journal.root, **ARGS)
            assert reopened.prefix(verify_archives=True)['completed_deals'] == (BATCH if stage=='committed' else 0)
            if stage == 'before-commit':
                assert reopened.recover_next()['completed_deals'] == BATCH
            else:
                assert reopened.recover_next() is None
            assert np.array_equal(reopened.prefix(verify_archives=True)['values'],values)

        incomplete = create('incomplete')
        batch,folder = incomplete.begin()
        rejects('duplicate sampling', incomplete.begin)
        rejects('missing scientific outputs', incomplete.recover_next)
        assert incomplete.prefix()['completed_deals'] == 0
        folder.mkdir()
        durable(folder/'query-batch.json',canonical(batch))
        rejects('partial scientific outputs', incomplete.recover_next)

        sampling = create('interrupted-sampling')
        _,claim,_ = sampling._paths(0)
        durable(claim,encoded(dict(journal_owner_sha256=sampling.owner,start=0)))
        rejects('interrupted sampling retry', sampling.begin)
        rejects('interrupted sampling recovery', sampling.recover_next)

        partial_archive = create('interrupted-archive')
        batch,folder = partial_archive.begin()
        fixture(folder,batch)
        durable(partial_archive.archive.root/'test-000000.xz',b'incomplete synthetic archive')
        rejects('partial archive republish', partial_archive.recover_next)

        damaged = create('damaged-inputs')
        batch,folder = damaged.begin()
        values,parts = fixture(folder,batch)
        intent,_ = damaged._intent(0,PhysicalDeals(SOURCE,mode='full_deck',seed=9309020))
        for name in ARTIFACTS-{'summary.json'}:
            changed = dict(parts)
            changed[name] += b' '
            rejects('changed member '+name, lambda changed=changed:damaged._evidence(changed,intent))
        for name,alter in (
            ('summary values',lambda v:v['values'][0][0][0].__setitem__(0,999.)),
            ('profile order',lambda v:v.__setitem__('profile_order',list(reversed(PROFILE_NAMES)))),
            ('allin cache',lambda v:v.__setitem__('allin_cache_sha256','4'*64)),
            ('wrong batch count',lambda v:v.__setitem__('deals',16))):
            changed = dict(parts)
            summary = json.loads(parts['summary.json'])
            alter(summary)
            changed['summary.json'] = canonical(summary)
            rejects(name,lambda changed=changed:damaged._evidence(changed,intent))
        rejects('changed bank identity',lambda:EvaluationJournal(normal.root,**dict(ARGS,bank_identities_sha256='4'*64)))
        rejects('changed registration',lambda:EvaluationJournal(normal.root,**dict(ARGS,registration_sha256='4'*64)))
        rejects('wrong stack',lambda:protocol(json.dumps(dict(json.loads(SOURCE),config=dict(stack=50))),'1'*64,'2'*64,'3'*64))
        rejects('outside owned root',lambda:EvaluationJournal.create(Path('S:/outside-stack-context-test'),**ARGS))

        # Completed prefix requires the original archived bytes, not a state
        # file claiming completion. Corrupt only this new synthetic fixture.
        packed = normal.archive.root/'test-000000.xz'
        raw = packed.read_bytes()
        with packed.open('wb') as stream:
            stream.write(raw[:-1]+bytes([raw[-1]^1]))
        rejects('archive corruption',lambda:normal.prefix(verify_archives=True))
        seconds = time.monotonic()-began
        allocated_logical = sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
        assert seconds<60 and allocated_logical<16000000
        result = dict(complete=True,passed=True,seconds=seconds,logical_bytes=allocated_logical,
            negative_cases=NEGATIVE,completed_prefix_replayed_deals=64,
            recovery_cases=['complete raw output','archive committed before checkpoint','checkpoint committed'],
            exact_chance_continuation=True,exact_saved_payoffs=True,independent_numpy_statistics=True,
            correct_per_depth_alpha=.05/7,one_final_look=4096,
            synthetic_context_only=True,scientific_test_deals=False,native_labels=False,fits=False,gpu=False,
            deletes=False,inputs=json.loads(attempt.read_bytes()))
        durable(output,encoded(result))
        print(json.dumps(dict(passed=True,seconds=seconds,logical_bytes=allocated_logical,negative_cases=len(NEGATIVE))))
    except Exception:
        durable(failed,encoded(dict(passed=False,seconds=time.monotonic()-began,traceback=traceback.format_exc())))
        raise


if __name__=='__main__':
    main()
