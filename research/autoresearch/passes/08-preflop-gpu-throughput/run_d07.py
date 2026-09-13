"""Guarded immutable D07 topology extraction; no GPU workload."""
import gzip,hashlib,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    exit=json.loads((run07.RAW/'d07-invariants-v1-exit.json').read_text())
    assert exit['returncode']==0 and exit['reason'] is None
    log=(run07.RAW/'d07-invariants-v1.log').read_text()
    assert '1 passed; 0 failed; 1 ignored' in log
    exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    frozen=run07.LAB/'target/d07-inventory-frozen.exe'
    assert not frozen.exists();shutil.copyfile(exe,frozen)
    manifest={'executable_sha256':sha(frozen),'fixtures':{}}
    for fixture,save in [('small','behavioral-fixed-e0-v1'),('large','eight-native-a')]:
        source=run07.LAB/f'target/convergence/{save}/final.gtop'
        witness=run07.LAB/f'target/d07-{fixture}-topology-v1.bin'
        name=f'd07-{fixture}-v1';out=run07.RAW/(name+'.json')
        run07.run(name,[frozen,'preflop::gpu::terminal_locality::terminal_locality_inventory_from_save','--exact','--ignored','--nocapture','--test-threads=1'],180,
            [source,run07.LAB/'cache/preflop_eq169.bin',frozen,HERE/'D07_PROTOCOL.md'],
            {'PREFLOP_GPU_LOCALITY_INPUT':str(source),'PREFLOP_GPU_LOCALITY_OUTPUT':str(out),'PREFLOP_GPU_LOCALITY_WITNESS':str(witness)})
        compressed=run07.RAW/f'd07-{fixture}-topology-v1.bin.gz'
        assert not compressed.exists()
        compressed.write_bytes(gzip.compress(witness.read_bytes(),mtime=0))
        manifest['fixtures'][fixture]={'save_sha256':sha(source),'witness_sha256':sha(witness),'witness_bytes':witness.stat().st_size,'compressed_sha256':sha(compressed),'output_sha256':sha(out)}
    path=run07.RAW/'d07-witness-manifest.json';assert not path.exists()
    path.write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
