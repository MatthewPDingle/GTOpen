"""Final frozen-source controls and full native comparisons, serialized."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
from measure import HERE,LAB
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=LAB,text=True).strip()
expected='4878044924f2e170692a897de4179690357cf669'
assert source==expected
manifest=json.loads((HERE/'build-binaries.json').read_text(encoding='utf8'))
archives={}
for name in ['preflop_research_bench','preflop_budget_control','preflop_convergence_control','preflop_module_resources']:
    src=LAB/'target/release/examples'/f'{name}.exe'
    dest=LAB/'target/research-binaries'/f'final-{name}-4878044.exe'
    assert not dest.exists()
    shutil.copyfile(src,dest)
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    manifest.append({'path':str(dest),'sha256':digest,'source_commit':source,'harness':name,'kind':'final_preflop_candidate'})
    archives[name]=dest
(HERE/'build-binaries.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
def call(script,*args,env=None):
    subprocess.run([sys.executable,str(HERE/script),*map(str,args)],cwd=LAB,env=env,check=True)
for name,path,n in [('eight',HERE.parents[3]/'saves/preflop/Before preflop autoresearch 20260910 2104.gtop',6),('seven',HERE/'fixtures/seven.json',4),('six',HERE/'fixtures/six.json',6),('three',HERE/'fixtures/three.json',30)]:
    call('measure.py',f'final-{name}-a',path,n)
    if name=='eight':shutil.copyfile(LAB/'target/research-roundtrip.gtop',LAB/'target/fixtures/final-eight-80.gtop')
call('verify_gpu.py')
env=os.environ.copy();env['REALIZATION_FIT']=str(LAB/'cache/realization_fit.json');env['PREFLOP_GPU_LAYOUT_STATS']='1'
for name,fixture,budget,reference in [('19000','fresh-coupled-validated.gtop',19000,'literal-budget19000-six.gtop'),('21000','fresh-coupled-validated.gtop',21000,'literal-budget21000-six.gtop'),('frozen','coupled-iter80-freeze-non-btn.gtop',19000,'literal-coupled-frozen-six.gtop')]:
    call('run_guarded.py',f'final-modeled-{name}-a',archives['preflop_budget_control'],LAB/'target/fixtures'/fixture,6,budget,env=env)
    output=LAB/'target/fixtures'/f'final-modeled-{name}.gtop'
    assert not output.exists()
    shutil.copyfile(LAB/'target'/f'research-budget-control-roundtrip-{budget}.gtop',output)
    call('run_guarded.py',f'final-native-{name}-a',LAB/'target/release/examples/preflop_compare_saved.exe',LAB/'target/fixtures'/reference,output,LAB/'cache/preflop_eq169.bin')
    call('assert_saved_exact.py',f'final-native-{name}-a')
call('prepare_extended_protocol.py',archives['preflop_convergence_control'],source)
print('FINAL_CONTROLS_PASSED_PROTOCOL_FROZEN',flush=True)
