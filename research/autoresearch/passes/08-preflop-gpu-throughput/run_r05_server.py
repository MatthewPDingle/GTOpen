"""Own one isolated server under the live-work guard; at most 180s per fixture."""
import sys
from pathlib import Path
from run_c23 import HERE,RAW,read,run07

assert read(RAW/'r05-current-v1-exit.json')['returncode']==0
for stage in ['default','server-tests','server-build']:
    r=read(RAW/('r05-'+stage+'-v1-exit.json'));assert r['returncode']==0 and r['reason'] is None
lab=run07.LAB
inputs=[HERE/'R05_PROTOCOL.md',HERE/'r05_server_qualify.py',HERE/'prepare_r05_server.py',Path(__file__),lab/'target/r05-server-frozen.exe',
    lab/'target/convergence/behavioral-fixed-e0-v1/final.gtop',lab/'target/convergence/eight-native-a/final.gtop',
    lab/'cache/preflop_eq169.bin',lab/'cache/realization_fit.json']
inputs+=sorted(p for p in (lab/'crates/server').rglob('*') if p.suffix in ['.rs','.toml'])
inputs+=sorted(p for p in (lab/'web').rglob('*') if p.suffix in ['.js','.html','.css'])
run07.run('r05-server-live-v1',[sys.executable,HERE/'r05_server_qualify.py'],480,inputs,{})
r=read(RAW/'r05-server-live-v1-exit.json');assert r['returncode']==0 and r['reason'] is None
