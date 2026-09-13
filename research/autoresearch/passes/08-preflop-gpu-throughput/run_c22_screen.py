"""Guard standalone two-kernel qualification and freeze its executable."""
import hashlib,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=RAW
if __name__=='__main__':
    assert json.loads((RAW/'d18-verified.json').read_text(encoding='utf-8'))['admitted']
    run07.run('c22-pipeline-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research',
        '--lib','preflop::gpu::rank_pipeline::separate_products_preserve_hand_histories',
        '--','--exact','--ignored','--nocapture','--test-threads=1'],300,
        [HERE/'C22_PROTOCOL.md',HERE/'prepare_c22.py',HERE/'c22_test.rs.txt',Path(__file__),HERE/'artifacts/c22-v1-source-map.json'],
        {'PREFLOP_GPU_RANK_PIPELINE_OUTPUT':str(RAW/'c22-pipeline-v1')})
    rec=json.loads((RAW/'c22-pipeline-v1-exit.json').read_text(encoding='utf-8'));assert rec['returncode']==0 and rec['reason'] is None
    log=(RAW/'c22-pipeline-v1.log').read_text(encoding='utf-8');assert '1 passed; 0 failed; 0 ignored' in log
    source=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    exe=run07.LAB/'target/c22-pipeline-frozen.exe';assert not exe.exists();shutil.copyfile(source,exe)
    out=dict(source_run='c22-pipeline-v1',sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
    (RAW/'c22-pipeline-frozen.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out),flush=True)
