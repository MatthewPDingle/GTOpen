"""One fresh two-phase server build, inventory and ordinary unit suite."""
import server_common as c
import json,re,shutil,subprocess,sys
assert len(sys.argv)==2;c.initialize('build',sys.argv[1])
O=c.ROOT/'runs/E051-server-final-build';U=c.ROOT/'runs/V051-server-unit'
with c.ar.exclusive_lock(c.ROOT/'gpu-run.lock'):
 c.verify();c.ar.refuse_active(c.ar.live_status());assert shutil.disk_usage(c.ROOT).free>=66*1024**3
 assert not O.exists() and not U.exists() and not c.TARGET.exists()
 for stem in ['E051-gto-server','E051-server-tests']:
  assert not (c.ROOT/'binaries'/(stem+'.exe')).exists() and not(c.ROOT/'binaries'/(stem+'.manifest.json')).exists()
 O.mkdir();c.TARGET.mkdir();before=c.live_identity();c.heartbeat('Building the qualified E051 server in a fresh S target. Live server and sessions unchanged; no new speed claim.')
 c.save(O/'started.json',{'at':c.now(),'protocol_sha256':sys.argv[1],'live_identity':before,'rustc':c.capture(['rustc','-Vv']),'cargo':c.capture(['cargo','-V']),'fresh_target':True})
 outputs=[]
 try:
  for verb,stem in [('build','E051-gto-server'),('test','E051-server-tests')]:
   cmd=['cargo',verb,'--release','--locked','--offline','-p','server','--features','gpu','--bin','gto-server']
   if verb=='test':cmd+=['--no-run']
   cmd+=['--message-format=json'];c.old.child(cmd,O,verb,c.env(True),1800);c.verify()
   logs=[json.loads(x) for x in (O/(verb+'.stdout.log')).read_text(encoding='utf-8').splitlines()]
   assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in logs)
   artifacts=[x for x in logs if x.get('reason')=='compiler-artifact']
   for x in artifacts:
    for f in x.get('filenames',[])+([x['executable']] if x.get('executable') else []):assert c.Path(f).resolve().is_relative_to(c.TARGET.resolve()),f
   rows=[x for x in artifacts if x.get('executable') and x['target']['name']=='gto-server'];assert len(rows)==1
   item=rows[0];assert item['profile']['test']==(verb=='test') and item['fresh'] is False
   assert c.Path(item['manifest_path']).resolve()==c.REPO/'crates/server/Cargo.toml' and c.Path(item['target']['src_path']).resolve()==c.REPO/'crates/server/src/main.rs'
   sol=[x for x in artifacts if x['target']['name']=='solver' and x['target']['kind']==['lib']];assert len(sol)==1 and sol[0]['features']==['gpu']
   if verb=='build':assert sol[0]['fresh'] is False
   dest=c.ROOT/'binaries'/(stem+'.exe');shutil.copyfile(item['executable'],dest)
   manifest={'candidate':'E051','source_root':str(c.REPO),'source_commit':c.P['research_commit'],'source_sha256':c.SOURCES,'binary_sha256':c.sha(dest),'protocol_sha256':sys.argv[1],'acceptance':c.P['acceptance'],'built_at':c.now(),'cargo_artifact':item,'solver_artifact':sol[0],'target_dir':str(c.TARGET),'command':cmd,'build_log_sha256':c.sha(O/(verb+'.stdout.log')),'build_stderr_sha256':c.sha(O/(verb+'.stderr.log')),'embedded_cuda_occurrences':c.embedded(dest),'dependency_sha256':{f:c.sha(f) for x in artifacts for f in x.get('filenames',[]) if c.Path(f).suffix in {'.rlib','.rmeta','.lib','.dll'}},'live_executable_touched':False,'scope':'Server application qualification; no new performance evidence or deployment'}
   c.save(dest.with_suffix('.manifest.json'),manifest);outputs.append({'path':str(dest),'sha256':c.sha(dest),'manifest_sha256':c.sha(dest.with_suffix('.manifest.json'))})
  unit,mp=c.binary('E051-server-tests')
  c.old.child([str(unit),'--list','--format','terse'],O,'inventory',c.env(),60)
  names=sorted(x[:-6] for x in (O/'inventory.stdout.log').read_text(encoding='utf-8').splitlines() if x.endswith(': test'))
  expected=c.read(c.HERE/'unit-inventory.json');assert names==expected['expected_test_names']
  U.mkdir();command=[str(unit),'--nocapture','--test-threads=1'];c.heartbeat('E051 server builds complete. Running the21 registered server tests, one intentionally ignored, on the isolated binary.')
  c.old.child(command,U,'native',c.env(),600)
  raw=(U/'native.stdout.log').read_text(encoding='utf-8');assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('20','0','1','0','0')]
  assert sorted(re.findall(r'^test ([\w:]+) \.\.\.',raw,re.M))==names and 'test report_tests::report_adaptation_benchmark ... ignored' in raw
  shutil.copyfile(U/'native.stdout.log',U/'stdout.log')
  c.save(U/'report.json',{'status':'measured','at':c.now(),'returncode':0,'test_pass_count':20,'ignored':1,'binary_sha256':c.sha(unit),'manifest_sha256':c.sha(mp),'command':command,'stdout_sha256':c.sha(U/'stdout.log'),'test_names':names,'ordinary_CUDA_test_passed':True,'all_owned_children_terminal':True})
  c.verify();assert c.live_identity()==before
  c.save(O/'report.json',{'status':'pass','at':c.now(),'outputs':outputs,'ordinary_server_units_passed':20,'ignored':1,'unit_report_sha256':c.sha(U/'report.json'),'source_unchanged':True,'all_compilers_and_unit_children_terminal':True,'server_launched':False,'live_executable_touched':False})
 except BaseException as e:
  c.save(O/'failure.json',{'at':c.now(),'error':repr(e),'preserve_all_evidence':True});raise
print('E051 isolated server build and unit qualification passed',flush=True)
