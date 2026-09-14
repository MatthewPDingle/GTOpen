"""Independent combined-release audit: source, binary, numerical and HTTP evidence."""
import json,re,socket,shutil
from run_c23 import HERE,RAW,read,run07
def main():
 counts={};source=None
 for stage,version,expected in [('selection','v3',4),('cohorts','v1',10),('native','v1',20),('default','v1',181),('server-tests','v1',20),('server-build','v1',None)]:
  name=f'r05-{stage}-{version}';r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None
  if source is None:source=r['solver_source_files']
  else:assert source==r['solver_source_files']
  if expected is not None:
   parsed=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;', (RAW/(name+'.log')).read_text(encoding='utf-8'))
   assert all(int(f)==0 for _,f in parsed) and sum(int(p) for p,_ in parsed)==expected
   counts[stage]=expected
 for p,h in source.items():assert run07.digest(run07.LAB/p)==h,p
 ordinary=read(RAW/'r05-ordinary-v1-exit.json');assert ordinary['returncode']==0 and ordinary['reason'] is None
 # Later source difference only adds the ignored normal-selection saved-game harness.
 for p,h in ordinary['solver_source_files'].items():
  if not p.replace('\\','/').endswith('static_cdf/ordinary/tests.rs'):assert source[p]==h,p
 assert '4 passed; 0 failed' in (RAW/'r05-ordinary-v1.log').read_text(encoding='utf-8');counts['ordinary']=4
 for folder,reference in [('r05-ordinary-v1','c24-native-artifacts-v1'),('r05-current-artifacts-v1','c24-native-artifacts-v1'),('r05-integrated-v1','r04-integrated-v1')]:
  for f in ['candidate.cu','candidate.ptx']:assert (RAW/folder/f).read_bytes()==(RAW/reference/f).read_bytes()
 for stage in ['current','server-live','current-server']:
  r=read(RAW/f'r05-{stage}-v1-exit.json');assert r['returncode']==0 and r['reason'] is None
 current=read(RAW/'r05-current-v1.json');ref=read(RAW/'c24-current-candidate-full1-bench.json')
 for k in ['arena_fingerprint','arena_entries','batch','final_device_bytes']:assert current[k]==ref[k]
 for a,b in zip(current['rows'],ref['rows']):
  for k in ['iteration','gaps','evs']:assert a[k]==b[k]
 server=read(RAW/'r05-server-live-v1.json');native=read(RAW/'r05-current-server-v1.json')
 exe=run07.LAB/'target/r05-server-frozen.exe';sha=run07.digest(exe)
 assert sha==read(RAW/'r05-server-frozen.json')['sha256']==server['executable_sha256']==native['executable_sha256']
 for x in [server,native]:assert x['passed'] and x['owned_port_closed'] and x['port']==56710
 assert len(server['static_cdf_selections'])==10
 for selection in server['static_cdf_selections']:assert selection['static_cdf'] and selection['mode']=='retained_cohorts' and selection['static_cdf_fallback_reason'] is None
 for x in server['fixtures'].values():assert x['exact_saved_reference'] and x['exact_resume_replay'] and x['resume_a']['sha256']==x['resume_b']['sha256']
 for k in ['arena_fingerprint','arena_entries']:assert native[k]==ref[k]
 for x in native['checkpoints']:
  assert x['root_reload_exact'];expected=ref['rows'][x['iteration']-54]
  for k in ['gaps','evs']:assert x['status'][k]==expected[k]
 with socket.socket() as s:assert s.connect_ex(('127.0.0.1',56710))!=0
 archive=HERE/'artifacts/r05-release';archive.mkdir(exist_ok=True)
 for p in source:
  src=run07.LAB/p
  if src.suffix in ['.rs','.cu'] and ('static_cdf' in p or p.endswith(('gpu.rs','adaptive_throughput.rs','cross_player_inventory.rs','preflop_throughput.rs'))):
   dest=archive/p.replace('\\','__').replace('/','__');shutil.copyfile(src,dest)
 result=dict(verified=True,admitted=True,retained=False,ready_for_deployment=True,deployed=False,
  status='C23 + C24 release qualified; deployment next',server_executable=str(exe),server_sha256=sha,
  tests=counts,source_files=source,current_game_exact=True,normal_http_save_reload_exact=True,
  active_stop_replay_exact=True,kernels_identical_to_retained_experiments=True,
  scope='Combined normal-app integration. No new optimization percentage; C23 and C24 use separate benchmark controls.')
 (RAW/'r05-release-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 (RAW/'r05-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k!='source_files'},indent=2))
if __name__=='__main__':main()
