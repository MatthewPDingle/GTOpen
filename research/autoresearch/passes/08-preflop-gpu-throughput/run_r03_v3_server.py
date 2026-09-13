"""Launch the frozen server qualification under the shared live-session guard."""
import sys
from pathlib import Path
from run_r03_v3 import HERE,run07

if __name__=='__main__':
    lab=run07.LAB
    inputs=[HERE/'R03_PROTOCOL.md',HERE/'R03_V3.md',HERE/'r03_server_qualify_v3.py',Path(__file__),lab/'target/r03-v3-server-frozen.exe',
        lab/'target/convergence/behavioral-fixed-e0-v1/final.gtop',lab/'target/convergence/eight-native-a/final.gtop',
        lab/'cache/preflop_eq169.bin',lab/'cache/realization_fit.json']
    inputs+=sorted(p for p in (lab/'crates/server').rglob('*') if p.suffix in ['.rs','.toml'])
    inputs+=sorted(p for p in (lab/'web').rglob('*') if p.suffix in ['.js','.html','.css'])
    run07.run('r03-server-live-v3',[sys.executable,HERE/'r03_server_qualify_v3.py'],600,inputs,{})
