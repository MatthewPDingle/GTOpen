"""Resume C23 timing after the original pre-launch idle refusal.

Pair 1 has only a preserved GPU snapshot: no benchmark process was started.
Use pair 2 for the first completed comparison rather than overwriting evidence.
"""
import hashlib,json,sys
from pathlib import Path
import run_c23
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def main():
    assert run_c23.read(RAW/'c23-integration-verified.json')['admitted']
    run_c23.run07.idle() # Refuse before creating another GPU snapshot.
    assert not (RAW/'c23-large-control-1-exit.json').exists()
    assert not (RAW/'c23-large-control-1.log').exists()
    a=run_c23.run('large','control',pair=2)
    b=run_c23.run('large','candidate',pair=2)
    ratio=run_c23.compare(a,b)
    receipt=dict(first_completed_pair=2,first_pair_ratio=ratio,passed_screen=ratio<=.99,numerical_equal=True,
        retry_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        deferred_attempt='Pair 1 idle guard refused before launch; GPU-before snapshot retained.')
    out=RAW/'c23-timing-screen.json';assert not out.exists();out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
