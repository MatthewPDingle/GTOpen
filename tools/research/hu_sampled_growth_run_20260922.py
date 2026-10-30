"""Guard a bounded fresh-deal sparse-state growth run; audit complete checkpoint."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
EVIDENCE=ROOT/'research/preflop-evolution/representative-coverage-20260919'
PREFIX='sampled-growth-v1'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    registration=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    assert not registration.exists() and not result_path.exists()
    assert idle(),'Production active; do not start research.'
    assert not (EVIDENCE/'running.lock').exists()
    fixture=OUT/(PREFIX+'-deals.bin');metadata=OUT/(PREFIX+'-deals.json');m=json.loads(metadata.read_text())
    assert sha(fixture)==m['sha256'] and m['full_supported_classes']==[169,96]
    for p,h in m['inputs'].items():assert sha(ROOT/p)==h,p
    prior_reg=OUT/'sampled-poker-v1-registration.json';prior_review=OUT/'sampled-poker-v1-review.json';v=json.loads(prior_review.read_text())
    assert v['passed'] and sha(prior_reg)==v['registration_sha256']
    for p,h in json.loads(prior_reg.read_text())['inputs'].items():assert sha(ROOT/p)==h,p
    exe=ROOT/'target/release/examples/hu_sampled_growth_gpu.exe'
    context=OUT/'bb-context-candidate.json';header=ROOT/'crates/solver/examples/research_sampled/postflop_state_v1.cuh'
    evaluator=ROOT/'crates/solver/examples/research_sampled/evaluator_v1.cuh';kernel=OUT/'sampled_poker_v1.cu'
    progress=OUT/(PREFIX+'-progress.jsonl');checkpoint=ROOT/'target/research-sampled/sampled-growth-v1-state.bin'
    assert not progress.exists() and not checkpoint.exists()
    paths=[exe,context,fixture,metadata,header,evaluator,kernel,Path(__file__),prior_reg,prior_review,
        ROOT/'crates/solver/examples/hu_sampled_growth_gpu.rs',ROOT/'crates/solver/examples/research_sampled/poker_reference_v1.rs',
        ROOT/'crates/solver/examples/research_sampled/state.rs',ROOT/'crates/solver/src/evaluator.rs',ROOT/'crates/solver/src/tree.rs',
        ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=300,training_soft_seconds=180,
        purpose='Measure actual fresh-deal lookup reuse, per-street state growth and whole-batch cost before convergence admission.',
        budgets={'max_deals':262144,'batch_deals':2048,'max_infosets':8000000,'max_records_per_traversal':512},
        gates={'full_target_support':True,'no_eviction':True,'full_checkpoint_retained':True,'max_live_reference_error':1e-9,
               'no_partial_batch_when_entry_cap_reached':True},
        limits='Resource probe, not a convergence or poker accuracy experiment. No policy exported to preview or production.',no_automatic_retry=True)
    registration.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    env=os.environ.copy();env['GTO_RESEARCH_MAX_SECONDS']='300';env['GTO_RESEARCH_PROTOCOL']=str(registration.relative_to(ROOT))
    cmd=[sys.executable,str(ROOT/'tools/research/loopback_research_validation.py'),str(exe),PREFIX,
         *[str(p.relative_to(ROOT)) for p in [context,fixture,header,evaluator,kernel,result_path,progress,checkpoint]]]
    run=subprocess.run(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ['.log','-status.json','-resources.json','-freeze.json']:
        p=EVIDENCE/(PREFIX+suffix)
        if p.exists():shutil.copyfile(p,OUT/(PREFIX+suffix))
    assert run.returncode==0,'Keep failure evidence; no automatic restart.'
    guard=json.loads((OUT/(PREFIX+'-status.json')).read_text());assert guard['exit_code']==0 and guard['error'] is None
    result=json.loads(result_path.read_text());assert result['passed'] and result['maximum_live_reference_error']<1e-9
    assert result['final_infosets']<=8000000 and result['completed_deals']==2048*result['completed_batches']
    assert result['stop_reason'] in ['sample_budget','soft_time_budget','entry_capacity_before_batch_update']
    rows=[json.loads(line) for line in progress.read_text().splitlines()];assert rows==result['rounds']
    assert sum(r['records'] for r in rows)==result['accepted_records']
    with checkpoint.open('rb') as f:raw=f.read(32)
    assert raw[:8]==b'GTSAMP01'
    assert np.frombuffer(raw[8:],dtype='<u8').tolist()==[result['completed_batches'],result['completed_deals'],result['final_infosets']]
    assert checkpoint.stat().st_size==32+88*result['final_infosets']==result['state_bytes']
    dtype=np.dtype([('hi','<u8'),('lo','<u8'),('n','<u8'),('reg','<f8',(4,)),('avg','<f8',(4,))]);assert dtype.itemsize==88
    state=np.memmap(checkpoint,mode='r',offset=32,dtype=dtype,shape=(result['final_infosets'],))
    counts=np.zeros(4,dtype=int);last=None;nonzero_regrets=0;nonzero_averages=0
    for start in range(0,len(state),131072):
        block=state[start:start+131072];hi=block['hi'];lo=block['lo'];n=block['n']
        assert np.all((n>=1)&(n<=4))
        assert np.isfinite(block['reg']).all() and np.isfinite(block['avg']).all() and (block['avg']>=0).all()
        assert np.all((hi[1:]>hi[:-1])|((hi[1:]==hi[:-1])&(lo[1:]>lo[:-1])))
        if last is not None:assert (int(hi[0]),int(lo[0]))>last
        last=(int(hi[-1]),int(lo[-1]))
        stages=np.where((hi>>np.uint64(63))==0,0,np.where(((lo>>np.uint64(30))&np.uint64(63))==63,1,np.where(((lo>>np.uint64(36))&np.uint64(63))==63,2,3)))
        counts+=np.bincount(stages,minlength=4)
        nonzero_regrets+=int(np.any(block['reg']!=0,axis=1).sum());nonzero_averages+=int(np.any(block['avg']!=0,axis=1).sum())
        for a in range(4):assert np.all(block['reg'][:,a][n<=a]==0) and np.all(block['avg'][:,a][n<=a]==0)
    assert counts.tolist()==result['infosets_by_street'];del state
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    review=dict(passed=True,registration_sha256=sha(registration),result_sha256=sha(result_path),progress_sha256=sha(progress),
        checkpoint_sha256=sha(checkpoint),checkpoint_bytes=checkpoint.stat().st_size,checkpoint_infosets_by_street=counts.tolist(),
        entries_with_nonzero_regret=nonzero_regrets,entries_with_nonzero_average=nonzero_averages,
        inputs_verified=len(frozen),guard=guard,production_modified=False,convergence_qualified=False,full_study_capacity_qualified=False)
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(review,indent=2))

if __name__=='__main__':main()
