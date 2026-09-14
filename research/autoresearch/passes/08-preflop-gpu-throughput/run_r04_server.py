"""Own one isolated server under the live-work guard; at most 180s per fixture."""
import sys
from pathlib import Path
from run_c23 import HERE,RAW,read,run07

assert read(RAW/'r04-saved-verified.json')['passed']
for stage in ['default','server-tests','server-build']:
    r=read(RAW/('r04-'+stage+'-v1-exit.json'));assert r['returncode']==0 and r['reason'] is None
lab=run07.LAB
inputs=[HERE/'R04_PROTOCOL.md',HERE/'r04_server_qualify.py',HERE/'prepare_r04_server.py',Path(__file__),lab/'target/r04-server-frozen.exe',
    lab/'target/convergence/behavioral-fixed-e0-v1/final.gtop',lab/'target/convergence/eight-native-a/final.gtop',
    lab/'cache/preflop_eq169.bin',lab/'cache/realization_fit.json']
inputs+=sorted(p for p in (lab/'crates/server').rglob('*') if p.suffix in ['.rs','.toml'])
inputs+=sorted(p for p in (lab/'web').rglob('*') if p.suffix in ['.js','.html','.css'])
run07.run('r04-server-live-v1',[sys.executable,HERE/'r04_server_qualify.py'],480,inputs,{})
r=read(RAW/'r04-server-live-v1-exit.json');assert r['returncode']==0 and r['reason'] is None
