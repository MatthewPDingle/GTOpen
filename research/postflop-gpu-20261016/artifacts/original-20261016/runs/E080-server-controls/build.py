"""Compile exact E080 host changes, restore source, then run server units."""
from pathlib import Path
import json,os,re,shutil,subprocess,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');B=H/'build';target=Path(P['target']);MAIN=Path(P['main'])
def inputs():
    old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
    for n,h in P['server_source_sha256'].items():old.pin(old.REPO/n,h);old.pin(MAIN/n,h)
def active():
    inputs();assert old.ar.source_identity()['source_sha256']==P['candidate_source_sha256']
    assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=old.REPO,text=True).splitlines())==set(P['owned'])
    m=old.read(R/'runs/accepted-E051-live-20261018/protected-main.json');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=MAIN,text=True).strip()==m['git_head']
    for n,h in m['source_sha256'].items():old.pin(MAIN/n,h)
    old.pin(m['live_path'],m['live_sha256'])
    for n,v in old.read(R/'runs/E080-build-plan/build-protocol.json')['protected_ptx'].items():old.pin(old.REPO/n,v['sha256'])
inputs();old.custody();assert not B.exists()and not target.exists();B.mkdir();target.mkdir();env=old.env();env['CARGO_TARGET_DIR']=str(target)
for k in env:
    assert k not in {'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}and not k.startswith('CARGO_PROFILE_RELEASE_')and not(k.startswith('CARGO_TARGET_')and k.endswith('_RUSTFLAGS')),k
outputs=[]
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
    try:
        for n,x in P['owned'].items():shutil.copyfile(x['candidate'],old.REPO/n)
        active()
        for verb,label,key in [('build','server','output_binary'),('test','unit','output_unit_binary')]:
            cmd=['cargo',verb,'--release','--locked','--offline','-p','server','--features','gpu','--bin','gto-server']+(['--no-run']if verb=='test'else[])+['--message-format=json'];out=B/label;out.mkdir();old.child(cmd,out,'cargo',env,1800);active()
            rows=[json.loads(x)for x in(out/'cargo.stdout.log').read_text().splitlines()];assert any(x.get('reason')=='build-finished'and x.get('success')is True for x in rows);art=[x for x in rows if x.get('reason')=='compiler-artifact'];items=[x for x in art if x.get('executable')and x['target']['name']=='gto-server'];assert len(items)==1;item=items[0]
            assert item['fresh']is False and item['profile']['test']==(verb=='test')and Path(item['manifest_path']).resolve()==old.REPO/'crates/server/Cargo.toml'
            sol=[x for x in art if x['target']['name']=='solver'and x['target']['kind']==['lib']];assert len(sol)==1 and sol[0]['features']==['gpu']
            if verb=='build':assert sol[0]['fresh']is False
            for x in art:
                for p in x.get('filenames',[])+([x['executable']]if x.get('executable')else[]):assert Path(p).resolve().is_relative_to(target.resolve())
            dest=Path(P[key]);assert not dest.exists();shutil.copyfile(item['executable'],dest);assert(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()in dest.read_bytes()
            manifest={'at':old.now(),'candidate':'E080','binary_sha256':old.sha(dest),'source_sha256':P['candidate_source_sha256']|P['server_source_sha256'],'protocol_sha256':sys.argv[1],'cargo_artifact':item,'solver_artifact':sol[0],'build_command':cmd,'target_dir':str(target),'source_root':str(old.REPO),'dependency_sha256':{f:old.sha(f)for x in art for f in x.get('filenames',[])if Path(f).suffix in['.rlib','.rmeta','.lib','.dll']},'source_copies':P['owned'],'candidate_adopted':False,'live_executable_touched':False};old.save(dest.with_suffix('.manifest.json'),manifest);outputs.append({'binary':str(dest),'sha256':old.sha(dest),'manifest_sha256':old.sha(dest.with_suffix('.manifest.json'))})
    except BaseException as exc:
        old.save(B/'failure.json',{'at':old.now(),'error':repr(exc),'preserve_all_evidence':True});raise
    finally:
        for n,x in P['owned'].items():
            assert old.sha(old.REPO/n)in[x['base_sha256'],x['candidate_sha256']];shutil.copyfile(x['base'],old.REPO/n)
        old.custody();old.save(B/'restoration.json',{'at':old.now(),'accepted_source_restored':True,'live_source_executable_unchanged':True})
    unit=P['output_unit_binary'];out=B/'tests';out.mkdir();old.child([unit,'--list','--format','terse'],out,'inventory',old.env(),60);names=sorted(x[:-6]for x in(out/'inventory.stdout.log').read_text().splitlines()if x.endswith(': test'));assert names==P['expected_unit_names']
    old.child([unit,'--nocapture','--test-threads=1'],out,'native',old.env(),600);raw=(out/'native.stdout.log').read_text();assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('20','0','1','0','0')];assert sorted(re.findall(r'^test ([\w:]+) \.\.\.',raw,re.M))==names
    inputs();old.custody();old.save(B/'report.json',{'at':old.now(),'status':'pass_fresh_server_build_and_ordinary_units','outputs':outputs,'unit_pass_count':20,'ignored':1,'unit_inventory_exact':True,'all_compilers_and_unit_children_terminal':True,'live_untouched':True,'candidate_adopted':False})
print('E080 fresh server build and 20 units passed; accepted source restored.',flush=True)
