"""Serial normal-feature release qualification, protected by the live-session guard."""
import sys,json,shutil
from pathlib import Path
from run_r03_v3 import HERE,run07

if __name__=='__main__':
    stage=sys.argv[1]
    assert json.loads((run07.RAW/'r03-overhead-v3-verified.json').read_text())['passed']
    assert json.loads((run07.RAW/'r03-v3-saved-verified.json').read_text())['passed']
    commands={
      'native':['cargo','test','--release','-p','solver','--features','gpu','--test','gpu','--test','preflop_gpu','--test','preflop_throughput','--','--test-threads=1'],
      'default':['cargo','test','--release','-p','solver'],
      'server-tests':['cargo','test','--release','-p','server','--features','gpu','--','--test-threads=1'],
      'server-build':['cargo','build','--release','-p','server','--features','gpu'],
    }
    inputs=[HERE/'R03_PROTOCOL.md',HERE/'R03_QUALIFICATION.md',HERE/'R03_V3.md',Path(__file__)]
    if stage.startswith('server'):
        inputs+=sorted(p for p in (run07.LAB/'crates/server').rglob('*') if p.suffix in ['.rs','.toml'])
    run07.run('r03-'+stage+'-v3',commands[stage],300,inputs,{})
    if stage=='server-build':
        exe=run07.LAB/'target/r03-v3-server-frozen.exe';assert not exe.exists()
        shutil.copyfile(run07.LAB/'target/release/gto-server.exe',exe)
        print(exe,flush=True)
