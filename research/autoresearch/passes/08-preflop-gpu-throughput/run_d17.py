"""Guard build, freeze, extraction and actual occupancy measurement separately."""
import gzip,hashlib,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    stage=sys.argv[1];exe=run07.LAB/'target/d17-support-frozen.exe'
    if stage=='build':
        run07.run('d17-support-test-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research',
            '--lib','preflop::gpu::terminal_tiles::tile_identity_and_boundaries','--','--exact','--nocapture','--test-threads=1'],300,
            [HERE/'D17_PROTOCOL.md',HERE/'prepare_d17.py',Path(__file__),HERE/'artifacts/d17-v1-source-map.json'])
        return
    if stage=='freeze':
        rec=read(run07.RAW/'d17-support-test-v1-exit.json');assert rec['returncode']==0 and rec['reason'] is None
        log=(run07.RAW/'d17-support-test-v1.log').read_text(encoding='utf-8');assert '1 passed; 0 failed' in log
        source=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        assert not exe.exists();shutil.copyfile(source,exe)
        (run07.RAW/'d17-frozen.json').write_text(json.dumps(dict(executable=str(exe),sha256=sha(exe)),indent=2)+'\n',encoding='utf-8')
        return
    assert stage in ['small','large']
    assert sha(exe)==read(run07.RAW/'d17-frozen.json')['sha256']
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if stage=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';name=f'd17-{stage}-v1';out=run07.RAW/(name+'.json')
    witness=run07.LAB/f'target/{name}-witness.bin';support=run07.LAB/f'target/{name}-support.bin'
    snapshot(name,'before')
    run07.run(name,[exe,'preflop::gpu::terminal_tiles::terminal_tile_inventory_from_saved_state','--exact','--ignored','--nocapture','--test-threads=1'],180,
        [source,eq,exe,HERE/'D17_PROTOCOL.md',Path(__file__)],
        {'PREFLOP_GPU_TILE_INPUT':str(source),'PREFLOP_GPU_TILE_OUTPUT':str(out),'PREFLOP_GPU_TILE_EQUITY':str(eq),
         'PREFLOP_GPU_TILE_WITNESS':str(witness),'PREFLOP_GPU_SUPPORT_WITNESS':str(support)})
    snapshot(name,'after')
    rec=read(run07.RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None
    prior=read(run07.RAW/f'd10-{stage}-v1-witness-manifest.json')
    assert sha(witness)==prior['witness_sha256'] and read(out)==read(run07.RAW/f'd10-{stage}-v1.json')
    z=run07.RAW/(name+'-support.bin.gz');assert not z.exists();z.write_bytes(gzip.compress(support.read_bytes(),mtime=0))
    result=dict(save_sha256=sha(source),executable_sha256=sha(exe),original_witness_sha256=sha(witness),
        original_json_sha256=sha(out),support_sha256=sha(support),support_bytes=support.stat().st_size,
        compressed_sha256=sha(z),original_d10_exact=True)
    (run07.RAW/(name+'-manifest.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
