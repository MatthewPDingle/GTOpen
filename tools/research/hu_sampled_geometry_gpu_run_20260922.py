"""Guard the GPU port of the qualified lazy betting transitions."""
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
PREFIX='sampled-geometry-gpu-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    registration=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    assert not registration.exists() and not result_path.exists()
    prior=json.loads((OUT/'sampled-geometry-v1-review.json').read_text())
    assert prior['passed']
    prior_reg=OUT/'sampled-geometry-v1-registration.json'
    assert sha(prior_reg)==prior['registration_sha256']
    old=json.loads(prior_reg.read_text())['inputs']
    context=OUT/'bb-context-candidate.json'
    state=ROOT/'crates/solver/examples/research_sampled/state.rs'
    for p in [state,context]:assert sha(p)==old[str(p.relative_to(ROOT))]
    assert idle(),'Production active; do not start research.'
    assert not (EVIDENCE/'running.lock').exists()
    exe=ROOT/'target/release/examples/hu_sampled_geometry_gpu.exe'
    header=ROOT/'crates/solver/examples/research_sampled/postflop_state_v1.cuh'
    kernel=OUT/'sampled_geometry_v1.cu'
    paths=[exe,header,kernel,state,context,Path(__file__),prior_reg,OUT/'sampled-geometry-v1-review.json',
        ROOT/'crates/solver/examples/hu_sampled_geometry_gpu.rs',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=120,
        purpose='Qualify actual GPU on-demand transitions for every betting-history template in all three BB continuations.',
        max_numeric_error=1e-10,integer_fields_exact=True,repeat_bit_exact=True,no_automatic_retry=True,
        limits='Card identities factored out only for transition testing. No policies merged; no training/equity/key implementation claim.')
    registration.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    env=os.environ.copy();env['GTO_RESEARCH_MAX_SECONDS']='120';env['GTO_RESEARCH_PROTOCOL']=str(registration.relative_to(ROOT))
    cmd=[sys.executable,str(ROOT/'tools/research/loopback_research_validation.py'),str(exe),PREFIX,
         str(context.relative_to(ROOT)),str(header.relative_to(ROOT)),str(kernel.relative_to(ROOT)),str(result_path.relative_to(ROOT))]
    run=subprocess.run(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ['.log','-status.json','-resources.json','-freeze.json']:
        p=EVIDENCE/(PREFIX+suffix)
        if p.exists():shutil.copyfile(p,OUT/(PREFIX+suffix))
    assert run.returncode==0,'Retain failure evidence; no automatic retry.'
    guard=json.loads((OUT/(PREFIX+'-status.json')).read_text());assert guard['error'] is None and guard['exit_code']==0
    result=json.loads(result_path.read_text());assert result['passed'] and result['repeat_bit_exact'] and result['integer_fields_exact']
    assert result['max_numeric_error']<1e-10 and [x['preflop_leaf'] for x in result['branches']]==[2,5,8]
    assert sum(x['betting_history_templates'] for x in result['branches'])==result['templates']
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    review=dict(passed=True,result_sha256=sha(result_path),registration_sha256=sha(registration),
        inputs_verified=len(frozen),guard=guard,production_modified=False,poker_trainer_qualified=False)
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(review,indent=2))


if __name__=='__main__':main()
