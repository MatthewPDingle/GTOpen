"""Guard standalone static CDF qualification and freeze its executable."""
import hashlib,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=RAW
if __name__=='__main__':
    assert json.loads((RAW/'d19-verified.json').read_text(encoding='utf-8'))['admitted']
    run07.run('c23-static-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research',
        '--lib','preflop::gpu::static_cdf::static_cdf_matches_required_prefixes_and_hands',
        '--','--exact','--ignored','--nocapture','--test-threads=1'],300,
        [HERE/'C23_PROTOCOL.md',HERE/'prepare_c23.py',HERE/'c23_module.rs.txt',Path(__file__),HERE/'artifacts/c23-v1-source-map.json'],
        {'PREFLOP_GPU_STATIC_CDF_OUTPUT':str(RAW/'c23-static-v1')})
    rec=json.loads((RAW/'c23-static-v1-exit.json').read_text(encoding='utf-8'));assert rec['returncode']==0 and rec['reason'] is None
    log=(RAW/'c23-static-v1.log').read_text(encoding='utf-8');assert '1 passed; 0 failed; 0 ignored' in log
    source=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    exe=run07.LAB/'target/c23-static-frozen.exe';assert not exe.exists();shutil.copyfile(source,exe)
    out=dict(source_run='c23-static-v1',sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
    (RAW/'c23-static-frozen.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out),flush=True)
