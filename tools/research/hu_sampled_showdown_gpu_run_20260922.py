"""Guard one exact-integer GPU hand-ranking qualification."""
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
PREFIX='sampled-showdown-gpu-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    registration=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    assert not registration.exists() and not result_path.exists()
    assert idle(),'Production active; do not start research.'
    assert not (EVIDENCE/'running.lock').exists()
    exe=ROOT/'target/release/examples/hu_sampled_showdown_gpu.exe'
    header=ROOT/'crates/solver/examples/research_sampled/evaluator_v1.cuh'
    kernel=OUT/'sampled_showdown_v1.cu'
    paths=[exe,header,kernel,Path(__file__),ROOT/'crates/solver/examples/hu_sampled_showdown_gpu.rs',
        ROOT/'crates/solver/src/evaluator.rs',ROOT/'crates/solver/src/cards.rs',ROOT/'Cargo.lock',
        ROOT/'crates/solver/Cargo.toml',ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=120,
        purpose='Exact GPU 7-card rank comparison; no aggregate equity approximation.',
        controls=dict(named_categories=9,generated_hands=200000,suit_order_variants=137*24,independent_best_of_21=4096,seed=20260922),
        acceptance='All encoded integer strengths identical to native, two repeated launches.',no_automatic_retry=True)
    registration.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    env=os.environ.copy();env['GTO_RESEARCH_MAX_SECONDS']='120';env['GTO_RESEARCH_PROTOCOL']=str(registration.relative_to(ROOT))
    cmd=[sys.executable,str(ROOT/'tools/research/loopback_research_validation.py'),str(exe),PREFIX,
        str(header.relative_to(ROOT)),str(kernel.relative_to(ROOT)),str(result_path.relative_to(ROOT))]
    run=subprocess.run(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ['.log','-status.json','-resources.json','-freeze.json']:
        p=EVIDENCE/(PREFIX+suffix)
        if p.exists():shutil.copyfile(p,OUT/(PREFIX+suffix))
    assert run.returncode==0,'Retain failure; no automatic retry.'
    guard=json.loads((OUT/(PREFIX+'-status.json')).read_text());assert guard['error'] is None and guard['exit_code']==0
    result=json.loads(result_path.read_text());assert result['passed'] and result['repeat_exact'] and result['native_integer_values_exact']
    assert result['cases']==203297 and result['independent_best_of_21_cases']==4096
    assert sum(result['category_counts'])==result['cases'] and all(n>0 for n in result['category_counts'])
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    review=dict(passed=True,result_sha256=sha(result_path),registration_sha256=sha(registration),
        inputs_verified=len(frozen),guard=guard,production_modified=False,poker_trainer_qualified=False)
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(review,indent=2))


if __name__=='__main__':main()
