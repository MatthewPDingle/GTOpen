"""Read-only bounded CPU suit-orbit census; does not merge trained state."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-suit-census-v1'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    reg=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    assert not reg.exists() and not result_path.exists() and idle()
    prior=OUT/'sampled-growth-v1-review.json';review=json.loads(prior.read_text());assert review['passed']
    checkpoint=ROOT/'target/research-sampled/sampled-growth-v1-state.bin';assert sha(checkpoint)==review['checkpoint_sha256']
    exe=ROOT/'target/release/examples/hu_sampled_suit_census.exe'
    paths=[checkpoint,exe,ROOT/'crates/solver/examples/hu_sampled_suit_census.rs',Path(__file__),prior,ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    reg.write_text(json.dumps(dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=120,cpu_threads=4,gpu_used=False,
        purpose='Count occupied full-observation suit orbits without merging or changing regret/average values.',
        no_automatic_retry=True),indent=2)+'\n',encoding='utf-8',newline='\n')
    started=time.monotonic()
    with (OUT/(PREFIX+'.log')).open('x',encoding='utf-8') as log:
        run=subprocess.run([str(exe),str(checkpoint),str(result_path)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                           timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    assert run.returncode==0
    result=json.loads(result_path.read_text());assert result['passed'] and result['source_entries']==sum(result['original_by_street'])
    assert result['suit_orbits']==sum(result['suit_orbits_by_street']) and result['orbit_invariance_controls']==6144
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    record=dict(passed=True,registration_sha256=sha(reg),result_sha256=sha(result_path),inputs_verified=len(frozen),
        checkpoint_preserved=True,wall_seconds=time.monotonic()-started,gpu_used=False,production_modified=False)
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
