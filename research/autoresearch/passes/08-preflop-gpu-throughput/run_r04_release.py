"""Normal-build release checks; one guarded stage at a time."""
import hashlib,json,shutil,sys
from pathlib import Path
from run_c23 import HERE,RAW,read,run07

stage=sys.argv[1]
assert read(RAW/'r04-overhead-verified.json')['passed'] and read(RAW/'r04-saved-verified.json')['passed']
commands={
    'default':['cargo','test','--release','-p','solver'],
    'server-tests':['cargo','test','--release','-p','server','--features','gpu','--','--test-threads=1'],
    'server-build':['cargo','build','--release','-p','server','--features','gpu'],
}
inputs=[Path(__file__),HERE/'R04_PROTOCOL.md',RAW/'r04-overhead-verified.json',RAW/'r04-saved-verified.json']
if stage.startswith('server'):
    inputs+=sorted(p for p in (run07.LAB/'crates/server').rglob('*') if p.suffix in ['.rs','.toml'])
run07.run('r04-'+stage+'-v1',commands[stage],300,inputs,{})
r=read(RAW/('r04-'+stage+'-v1-exit.json'));assert r['returncode']==0 and r['reason'] is None
assert r['solver_source_files']==read(RAW/'r04-initial-verified.json')['solver_source_files']
if stage=='server-build':
    exe=run07.LAB/'target/r04-server-frozen.exe';assert not exe.exists()
    shutil.copyfile(run07.LAB/'target/release/gto-server.exe',exe)
    with exe.open('rb') as f:checksum=hashlib.file_digest(f,'sha256').hexdigest()
    (RAW/'r04-server-frozen.json').write_text(json.dumps({'path':str(exe),'sha256':checksum,'source_run':'r04-server-build-v1'},indent=2)+'\n',encoding='utf-8')
    print(checksum,flush=True)
