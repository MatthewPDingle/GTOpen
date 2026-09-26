"""Re-evaluate archived policies with root actions forced; no inference or new deals.

Small transport/mixture control before any archived-population variance study.
Preserves all original evidence and every generated control input/output.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import psutil
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from reboot_research_idle_v1 import idle
from hu_root_retained_storage_admitted_study_20260924 import measure, LIMIT, METADATA_RESERVE

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'frozen-root-action-control-v1'
SOURCE = 'later-action-recovered-evaluation-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
EXE = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
PROFILE_INDICES = (0, 3, 4, 7)
ACTION_NAMES = ('fold', 'call', 'raise', 'jam')
CAP = 400_000_000


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def save(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, separators=(',', ':'), allow_nan=False)


def cls(cards):
    a,b=cards; lo,hi=sorted((a//4,b//4))
    return hi*13+lo if a%4==b%4 or hi==lo else lo*13+hi


def transform(original):
    profiles=[]
    for index in PROFILE_INDICES:
        src=original['profiles'][index]
        profiles.append(src)
        for a,name in enumerate(ACTION_NAMES):
            rows=[]
            for row in src['policies']:
                if int(row['hi'])==1:
                    assert row['actor']==0 and row['n']==4
                    row=dict(row, probabilities=[float(k==a) for k in range(4)])
                rows.append(row)
            profiles.append(dict(name=src['name']+':force-'+name,policies=rows))
    return dict(format=1,context_source=original['context_source'],
                batch_source=original['batch_source'],profiles=profiles)


def verify(source, actual, native, old_native, batch):
    """Read-back of root-only edits, original reproduction and mixture identities."""
    assert set(actual)==set(source) and actual['format']==source['format']==1
    assert actual['context_source']==source['context_source']
    assert actual['batch_source']==source['batch_source']
    assert len(actual['profiles'])==len(native['profiles'])==20
    assert native['fixed_policy_evaluation_only'] and not native['bounds_best_response_above']
    assert native['terminal_estimator']=='conditional-preflop-allin-v1'
    assert native['postflop_outcomes']=='sampled-board'
    context=json.loads(source['context_source']); invested=context['nodes'][0]['invested'][0]
    error=0.; changed=0; rows=[]
    for bank,source_index in enumerate(PROFILE_INDICES):
        original=source['profiles'][source_index]; root_p={}
        for row in original['policies']:
            if int(row['hi'])!=1: continue
            k=int(row['lo']); c=cls([k&63,(k>>6)&63])
            if c in root_p: assert root_p[c]==row['probabilities']
            root_p[c]=row['probabilities']
        base=bank*5
        assert actual['profiles'][base]==original
        assert native['profiles'][base]['name']==original['name']
        assert native['profiles'][base]['deals']==old_native['profiles'][source_index]['deals']
        for action,name in enumerate(ACTION_NAMES):
            altered=actual['profiles'][base+action+1]
            assert altered['name']==original['name']+':force-'+name
            assert native['profiles'][base+action+1]['name']==altered['name']
            assert len(altered['policies'])==len(original['policies'])
            assert len(native['profiles'][base+action+1]['deals'])==len(batch['deals'])
            for old,new in zip(original['policies'],altered['policies']):
                if int(old['hi'])==1:
                    assert {k:v for k,v in old.items() if k!='probabilities'}=={k:v for k,v in new.items() if k!='probabilities'}
                    assert new['probabilities']==[float(k==action) for k in range(4)]
                    changed+=1
                else: assert new==old
        for did,deal in enumerate(batch['deals']):
            c=cls(deal[:2]); weight=root_p[c]
            outcomes=[native['profiles'][base+a+1]['deals'][did] for a in range(4)]
            baseline=native['profiles'][base]['deals'][did]
            assert all(d['deal_index']==did and abs(d['terminal_mass']-1)<1e-12 for d in outcomes)
            assert outcomes[0]['values']==[-invested,context['dead_money']+invested]
            assert outcomes[0]['expected_rake']==0
            for player in range(2):
                mixed=math.fsum(w*d['values'][player] for w,d in zip(weight,outcomes))
                error=max(error,abs(mixed-baseline['values'][player]))
            mixed=math.fsum(w*d['expected_rake'] for w,d in zip(weight,outcomes))
            error=max(error,abs(mixed-baseline['expected_rake']))
            rows.append(dict(bank=bank,deal=did,hand_class=c,
                root_action_values=[d['values'][0] for d in outcomes]))
    assert error<1e-10
    assert 0<=native['maximum_forward_cashflow_error']<1e-10
    assert 0<=native['maximum_conservation_error']<1e-10
    return dict(maximum_root_mixture_error=error,root_policy_edits=changed,rows=rows)


def run(review_only=False):
    started=time.monotonic(); acquired=False; error=None
    reg_path=OUT/f'{PREFIX}-registration.json'
    if review_only:
        reg=read(reg_path); result=read(OUT/f'{PREFIX}-result.json')
        assert result['passed'] and result['registration_sha256']==sha(reg_path)
    else:
        assert idle() and not LOCK.exists() and not OTHER.exists()
        assert not STORE.exists() and not reg_path.exists()
    def guard():
        assert time.monotonic()-started<600 and idle() and not OTHER.exists()
        assert psutil.virtual_memory().available>=20_000_000_000
        assert shutil.disk_usage('S:/').free>=40_000_000_000
    source_path=OUT/f'{SOURCE}-result.json'; original_result=read(source_path)
    review_path=OUT/f'{SOURCE}-independent-review.json'; original_review=read(review_path)
    assert original_result['complete'] and original_review['passed']
    assert original_review['source_result_sha256']==sha(source_path)
    source_reg_path=OUT/f'{SOURCE}-registration.json'
    assert original_result['registration_sha256']==sha(source_reg_path)
    original_reg=read(source_reg_path)
    assert sha(EXE)==original_reg['inputs'][str(EXE)]
    source_store=Path(original_result['store'])
    reader=ArchivedEvaluationReader(source_store,original_result['archive_manifest_hashes'],external_files=[],guard=guard)
    if not review_only:
        inputs={str(p):sha(p) for p in [Path(__file__).resolve(),EXE,source_path,review_path,source_reg_path,
            ROOT/'tools/research/archived_evaluation_reader_v1.py',ROOT/'tools/research/sampled_evidence_archive_v1.py',
            ROOT/'tools/research/reboot_research_idle_v1.py']}
        inventory=measure(); projection=sum(x['allocated_file_bytes'] for x in inventory)+CAP+METADATA_RESERVE
        assert projection<=LIMIT
        save(reg_path,dict(prefix=PREFIX,inputs=inputs,source=SOURCE,store=str(STORE),
            source_batches=['test-000000','test-000032'],profile_indices=list(PROFILE_INDICES),
            actions=list(ACTION_NAMES),fresh_deals=False,distinct_deals=64,
            maximum_output_bytes=CAP,maximum_seconds=600,projected_allocated_bytes=projection,
            storage_inventory=inventory,gpu_used=False,production_modified=False))
        reg=read(reg_path)
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    jobs=[]
    try:
        if not review_only:
            with LOCK.open('x') as f:f.write(str(os.getpid()))
            acquired=True;STORE.mkdir()
        for name in reg['source_batches']:
            guard(); folder=STORE/name; src=source_store/name
            original=reader.read_json(src/'profiles.json')
            old_native=reader.read_json(src/'native.json')
            batch=reader.read_json(src/'query-batch.json')
            if not review_only:
                folder.mkdir(); actual=transform(original)
                save(folder/'profiles.json',actual)
                (folder/'conditional-batch.json').write_text(original['batch_source'],encoding='utf-8')
                (folder/'context.json').write_text(original['context_source'],encoding='utf-8')
                before=time.monotonic()
                cp=subprocess.run([str(EXE),str(folder/'context.json'),str(folder/'conditional-batch.json'),
                    str(folder/'profiles.json'),str(folder/'native.json')],cwd=ROOT,
                    capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
                assert cp.returncode==0,cp.stderr[-2000:]
                native_seconds=time.monotonic()-before
            else:
                record=next(j for j in result['jobs'] if j['name']==name)
                for p,h in record['artifacts'].items(): assert sha(folder/p)==h,p
                native_seconds=record['native_seconds']
            actual=read(folder/'profiles.json');native=read(folder/'native.json')
            checked=verify(original,actual,native,old_native,batch)
            if not review_only: save(folder/'check.json',checked)
            else: assert checked==read(folder/'check.json')
            artifacts={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
            jobs.append(dict(name=name,native_seconds=native_seconds,artifacts=artifacts,
                maximum_root_mixture_error=checked['maximum_root_mixture_error']))
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<=CAP
        for p,h in reg['inputs'].items(): assert sha(p)==h,p
        if review_only:
            save(OUT/f'{PREFIX}-readback.json',dict(passed=True,source_result_sha256=sha(OUT/f'{PREFIX}-result.json'),
                checked_deals=64,checked_banks=4,checked_actions=4,jobs=jobs,seconds=time.monotonic()-started,
                scope='Separate-process archived transport and mixture readback; no independent poker solve.'))
        else:
            save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(reg_path),jobs=jobs,
                logical_bytes=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()),
                seconds=time.monotonic()-started,fresh_deals=False,gpu_used=False,accuracy_qualified=False))
            child=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--review'],cwd=ROOT,
                capture_output=True,text=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
            assert child.returncode==0,child.stderr[-2000:]
            assert read(OUT/f'{PREFIX}-readback.json')['passed']
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
            save(OUT/f'{PREFIX}-status.json',dict(state='failed' if error else 'complete',error=error,
                seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__':
    assert sys.argv[1:] in (['--run'],['--review'])
    run(sys.argv[1]=='--review')
