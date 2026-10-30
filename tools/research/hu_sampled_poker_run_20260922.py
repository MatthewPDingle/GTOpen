"""Register and guard integrated sampled-poker correctness qualification."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
EVIDENCE=ROOT/'research/preflop-evolution/representative-coverage-20260919'
PREFIX='sampled-poker-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    registration=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    assert not registration.exists() and not result_path.exists()
    assert idle(),'Production active; do not start research.'
    assert not (EVIDENCE/'running.lock').exists()
    fixture=OUT/(PREFIX+'-fixture.json')
    for p,h in json.loads(fixture.read_text())['inputs'].items():assert sha(ROOT/p)==h,p
    prior_paths=[]
    for name in ['sampled-geometry-gpu-v1','sampled-showdown-gpu-v1']:
        rp=OUT/(name+'-registration.json');vp=OUT/(name+'-review.json');v=json.loads(vp.read_text())
        assert v['passed'] and sha(rp)==v['registration_sha256']
        for p,h in json.loads(rp.read_text())['inputs'].items():assert sha(ROOT/p)==h,p
        prior_paths.extend([rp,vp])
    exe=ROOT/'target/release/examples/hu_sampled_poker_gpu.exe'
    context=OUT/'bb-context-candidate.json'
    header=ROOT/'crates/solver/examples/research_sampled/postflop_state_v1.cuh'
    evaluator=ROOT/'crates/solver/examples/research_sampled/evaluator_v1.cuh'
    kernel=OUT/'sampled_poker_v1.cu'
    paths=[exe,context,fixture,header,evaluator,kernel,Path(__file__),
        ROOT/'crates/solver/examples/hu_sampled_poker_gpu.rs',
        ROOT/'crates/solver/examples/research_sampled/poker_reference_v1.rs',
        ROOT/'crates/solver/examples/research_sampled/state.rs',
        ROOT/'crates/solver/src/evaluator.rs',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']+prior_paths
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=180,
        purpose='Complete BB preflop/postflop sampled traversal, exact sparse observation lookup, frozen-batch signed-regret and opponent-average updates.',
        gates={'max_record_or_root_error':1e-9,'max_accumulated_state_error':1e-8,
            'all_three_branches':True,'exact_keys_and_arity':True,'repeat_bit_exact':True,
            'overflow_rejected':True,'frozen_input_preserved':True},
        limits='8192 unique sampled physical deals, six batches, 24576 traversals. No convergence/production/full-memory claim. Host reduction is temporary and timed.',
        no_automatic_retry=True)
    registration.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    env=os.environ.copy();env['GTO_RESEARCH_MAX_SECONDS']='180';env['GTO_RESEARCH_PROTOCOL']=str(registration.relative_to(ROOT))
    cmd=[sys.executable,str(ROOT/'tools/research/loopback_research_validation.py'),str(exe),PREFIX,
        *[str(p.relative_to(ROOT)) for p in [context,fixture,header,evaluator,kernel,result_path]]]
    run=subprocess.run(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ['.log','-status.json','-resources.json','-freeze.json']:
        p=EVIDENCE/(PREFIX+suffix)
        if p.exists():shutil.copyfile(p,OUT/(PREFIX+suffix))
    assert run.returncode==0,'Retain failure evidence; no automatic retry.'
    guard=json.loads((OUT/(PREFIX+'-status.json')).read_text());assert guard['exit_code']==0 and guard['error'] is None
    result=json.loads(result_path.read_text());assert result['passed'] and result['total_traversals']==24576
    assert result['frozen_repeat_bit_exact'] and result['hard_capacity_negative_control'] and result['exact_observation_key_controls']
    assert result['maximum_record_or_root_error']<1e-9
    assert all(r['repeated_key_occurrences']>0 for r in result['rounds'])
    assert all(r['visited_preflop_nodes']==[0,3,6,9,12] for r in result['rounds'])
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    review=dict(passed=True,registration_sha256=sha(registration),result_sha256=sha(result_path),inputs_verified=len(frozen),guard=guard,
                production_modified=False,convergence_qualified=False,full_study_capacity_qualified=False)
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(review,indent=2))

if __name__=='__main__':main()
