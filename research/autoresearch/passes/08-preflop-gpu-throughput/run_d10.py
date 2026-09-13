"""Guarded D10 immutable extraction; no learning or candidate kernel."""
import gzip,hashlib,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=HERE/'raw'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    stage=sys.argv[1];exe=run07.LAB/'target/d10-inventory-frozen.exe'
    if stage=='freeze':
        record=json.loads((run07.RAW/'d10-invariants-v2-exit.json').read_text(encoding='utf-8'))
        log=(run07.RAW/'d10-invariants-v2.log').read_text(encoding='utf-8')
        assert record['returncode']==0 and record['reason'] is None
        assert '1 passed; 0 failed; 1 ignored' in log
        source=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        assert not exe.exists();shutil.copyfile(source,exe);print(sha(exe));return
    assert stage in ['small','large']
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if stage=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';name=f'd10-{stage}-v1'
    out=run07.RAW/(name+'.json');witness=run07.LAB/f'target/{name}-witness.bin'
    snapshot(name,'before')
    run07.run(name,[exe,'preflop::gpu::terminal_tiles::terminal_tile_inventory_from_saved_state','--exact','--ignored','--nocapture','--test-threads=1'],180,
        [source,eq,exe,HERE/'D10_PROTOCOL.md',Path(__file__)],
        {'PREFLOP_GPU_TILE_INPUT':str(source),'PREFLOP_GPU_TILE_OUTPUT':str(out),'PREFLOP_GPU_TILE_EQUITY':str(eq),'PREFLOP_GPU_TILE_WITNESS':str(witness)})
    snapshot(name,'after')
    compressed=run07.RAW/f'{name}-witness.bin.gz';assert not compressed.exists()
    compressed.write_bytes(gzip.compress(witness.read_bytes(),mtime=0))
    record={'save_sha256':sha(source),'executable_sha256':sha(exe),'witness_sha256':sha(witness),'witness_bytes':witness.stat().st_size,'compressed_sha256':sha(compressed),'output_sha256':sha(out)}
    (run07.RAW/f'{name}-witness-manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record),flush=True)
if __name__=='__main__':main()
