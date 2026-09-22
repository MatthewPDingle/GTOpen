"""Run one bounded, fail-closed sampled GPU batch correctness probe."""
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
PREFIX='sampled-gpu-batch-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    registration=OUT/(PREFIX+'-registration.json')
    result_path=OUT/(PREFIX+'-result.json')
    assert not registration.exists() and not result_path.exists()
    fixture=OUT/(PREFIX+'-fixture.json');data=json.loads(fixture.read_text())
    for p,h in data['inputs_sha256'].items():assert sha(ROOT/p)==h
    assert idle(),'Production is active; leave probe unstarted.'
    assert not (EVIDENCE/'running.lock').exists()
    kernel=OUT/'sampled_batch_v1.cu';exe=ROOT/'target/release/examples/hu_sampled_batch_probe.exe'
    inputs=[fixture,kernel,exe,Path(__file__),ROOT/'crates/solver/examples/hu_sampled_batch_probe.rs',
            ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',
            ROOT/'tools/research/hu_sampled_gpu_fixture_20260922.py',
            ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py',
            ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    record=dict(inputs=hashes,created_at_unix=time.time(),maximum_seconds=120,
        scope='Exact-control frozen GPU batches only; 60 information sets, 128 action slots, two rounds in each of two utility modes.',
        acceptance=dict(max_absolute_error=1e-10,repeated_output_bit_exact=True,
                        source_policy_unchanged=True,previous_state_unchanged=True),
        allocation_scope='Bounded fixture, fewer than 1000 samples per batch; no poker tree allocation.',
        no_automatic_retry=True,production_modified=False)
    registration.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    env=os.environ.copy();env['GTO_RESEARCH_MAX_SECONDS']='120'
    env['GTO_RESEARCH_PROTOCOL']=str(registration.relative_to(ROOT))
    cmd=[sys.executable,str(ROOT/'tools/research/loopback_research_validation.py'),str(exe),PREFIX,
         str(fixture.relative_to(ROOT)),str(kernel.relative_to(ROOT)),str(result_path.relative_to(ROOT))]
    run=subprocess.run(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ['.log','-status.json','-resources.json','-freeze.json']:
        source=EVIDENCE/(PREFIX+suffix)
        if source.exists():shutil.copyfile(source,OUT/(PREFIX+suffix))
    assert run.returncode==0,'Retain failure evidence; no automatic retry.'
    guard=json.loads((OUT/(PREFIX+'-status.json')).read_text())
    assert guard['error'] is None and guard['exit_code']==0
    result=json.loads(result_path.read_text());assert result['passed'] and not result['poker_trainer']
    assert len(result['results'])==4
    for row in result['results']:
        assert row['repeat_bit_exact'] and row['frozen_input_policy_preserved'] and row['old_state_preserved']
        assert max(row['maximum_errors'].values())<1e-10
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    review=dict(passed=True,result_sha256=sha(result_path),registration_sha256=sha(registration),
        inputs_verified=len(hashes),guard=guard,production_modified=False,
        strategic_accuracy_claim=False,poker_trainer_qualified=False)
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(review,indent=2))


if __name__=='__main__':main()
