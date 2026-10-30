from pathlib import Path
import json,hashlib,re,datetime
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');D=R/'runs/E031-show-card-offset-resource';REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016');O=R/'comparisons/E031-resource-review';pins={};checks=[]
def ok(v,s):
 assert v,s
 checks.append(s)
def pin(p,v=None):
 p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest()
 if v is not None:ok(h==v,'hash '+str(p))
 pins[str(p)]=h;return h
def read(p):pin(p);return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(s,name):
 m=re.search(r'\.visible\s+\.entry\s+'+re.escape(name)+r'\(',s);assert m
 b=s.index('{',m.start());end=b+1;depth=1
 while depth:
  if s[end]=='{':depth+=1
  elif s[end]=='}':depth-=1
  end+=1
 return s[m.start():end]
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def main():
 m=read(D/'prepared-manifest.json');pin(D/'prepared-manifest.json','fd50fe183d77d697ce43e8a79d0cdf9d466c720fd452aad39d61c98592f51f16')
 for k,v in m['artifact_sha256'].items():pin(D/k,v)
 for v in m['references'].values():pin(v['path'],v['sha256'])
 for v in m['dependency_rlibs'].values():pin(v['path'],v['sha256'])
 for k,v in m['protected_checkout_sha256'].items():pin(REPO/k,v)
 ok(len(m['protected_checkout_sha256'])==162,'all162 accepted checkout sources unchanged')
 a=read(R/'runs/E031-root-decisions/resource-execution.json');pin(R/'runs/E031-root-decisions/resource-execution.json','0f72f4b644449de4c72abc5f8bf4512bd419647fdefbc3550bafff7d84f46d1d')
 for k,v in a['evidence_sha256'].items():pin(k,v)
 protocol=read(D/'protocol.json');report=read(D/'report.json');pin(D/'report.json','275631d98386a203173dd1e49037cd18c385c5cefd2eb98c36a7b8d0abf22cda')
 execution=read(D/'execution-manifest.json');started=read(D/'execution-started.json');commands=[read(D/(n+'.command.json')) for n in ['rustc','probe']]
 ok(report['commands']==commands and all(x['returncode']==0 and x['cleanup'] is None and 'error' not in x for x in commands),'two terminalzero commands; no cleanup/error')
 ok(dt(a['at'])<dt(started['at'])<=dt(commands[0]['started_at'])<dt(commands[1]['started_at']),'root authorization before one rustc then one probe')
 ok((dt(commands[1]['started_at'])-dt(commands[0]['started_at'])).total_seconds()>=commands[0]['elapsed_seconds'],'compile completes before resource executable')
 ok(commands[0]['args']==execution['compile_command'] and commands[1]['args']==[str(D/'probe.exe')],'exact recorded compiler and sole resource executable commands')
 ok(all(x['cwd']==str(D) and x['timeout_seconds']==600 for x in commands),'isolated workingdirectory and fixed timeout')
 ok(execution['input_sha256_before']==report['input_sha256_after']==m['artifact_sha256'],'input maps unchanged before and after')
 ok(execution['prepared_manifest_sha256']==report['prepared_manifest_sha256']==pins[str(D/'prepared-manifest.json')],'execution/terminal prepared seal bound')
 pin(execution['rustc_executable'],execution['rustc_executable_sha256'])
 for k,v in execution['nvrtc_dll_sha256'].items():pin(Path(execution['nvrtc_directory'])/k,v)
 binary=pin(D/'probe.exe','8a1847ad65e3daf68c93aed20223229dd3b921dfca376a6957c40d48538ace1d');ok(binary==report['binary_sha256'],'terminal binary identity')
 blob=(D/'probe.exe').read_bytes()
 for variant in ['baseline','candidate']:ok(blob.count((D/(variant+'.cu')).read_bytes())==1,'binary contains exact '+variant+' source once')
 pre=read(D/'preflight.json');launch=read(D/'launch-preflight.json')
 for label,v in [('root',a['live_status_before']),('preflight',pre['live_status']),('launch',launch)]:ok(v['/api/status']['state']=='idle' and v['/api/preflop/status']['state'] in ['', 'idle'] and v['/api/reports/status']['running'] is False,'recorded live idle '+label)
 ok(pre['free_bytes']>=pre['minimum_free_reserve_bytes']+pre['output_reservation_bytes'] and pre['lock']==str(R/'gpu-run.lock'),'shared lock and disk reserve recorded')
 raw=(D/'probe.stdout.log').read_text(encoding='utf-8');rows=[json.loads(l.split('E031_RESOURCE ',1)[1]) for l in raw.splitlines() if l.startswith('E031_RESOURCE ')]
 ok(rows==report['records'] and len(rows)==22,'all22 raw markers equal complete report')
 shapes=protocol['resource_shapes'];rr=rows[1:-1];device=rows[0]
 ok(device['stage']=='device' and rows[-1]==report['complete'] and rows[-1]['stage']=='complete' and rows[-1]['resource_rows']==20,'device/20resource/complete marker contract')
 ok(device['device']=='NVIDIA GeForce RTX 5090' and device['architecture']=='compute_120','expected runtime device/architecture')
 ok([(x['source_variant'],x['shape']) for x in rr]==[(a,s['id']) for a in ['baseline','candidate'] for s in shapes],'fixed baseline then candidate ten-shape order')
 for row in rows:ok(row['kernel_launches']==0 and row['performance_measurement'] is False,'row scope '+row['stage'])
 screen={};failed=[]
 for shape in shapes:
  pair=[next(x for x in rr if x['source_variant']==a and x['shape']==shape['id']) for a in ['baseline','candidate']]
  for row in pair:
   expected=m['source_variants'][row['source_variant']]
   ok(row['source_fnv1a64']==expected['fnv1a64'] and row['source_bytes']==expected['bytes'],'source bytes/FNV '+row['source_variant']+'/'+shape['id'])
   ok(row['block_threads']==128 and row['kernel']=='up_show' and row['nh_o']==shape['nh_o'] and row['max_valid_opponent_hands']==shape['m_max'],'shape identity '+row['source_variant']+'/'+shape['id'])
   ok(row['dynamic_shared_bytes']==shape['dynamic_shared_bytes']==4*shape['nh_o']+16*shape['m_max'],'dynamic size '+row['source_variant']+'/'+shape['id'])
   ok(row['static_plus_dynamic_shared_bytes']==row['static_shared_bytes']+row['dynamic_shared_bytes'],'combined allocation '+row['source_variant']+'/'+shape['id'])
   fit=row['static_plus_dynamic_shared_bytes']<=device['max_shared_bytes_per_block_default'] and row['max_threads_per_block']>=128 and device['max_threads_per_block']>=128
   ok(row['fits_queried_default_shared_and_thread_limits']==fit,'independent capacity arithmetic '+row['source_variant']+'/'+shape['id'])
   ok(row['occupancy_warps_per_sm_128']==row['occupancy_blocks_per_sm_128']*4,'warp count '+row['source_variant']+'/'+shape['id'])
  old,new=pair
  q={'no_new_local_bytes':new['local_bytes_per_thread']<=old['local_bytes_per_thread'],'no_theoretical_active_block_decrease':new['occupancy_blocks_per_sm_128']>=old['occupancy_blocks_per_sm_128'],'default_capacity_fits':all(x['fits_queried_default_shared_and_thread_limits'] for x in pair),'positive_theoretical_occupancy':all(x['occupancy_blocks_per_sm_128']>0 for x in pair),'same_dynamic_bytes_and128threads':old['dynamic_shared_bytes']==new['dynamic_shared_bytes'] and old['block_threads']==new['block_threads']==128}
  screen[shape['id']]=q
  if not all(q.values()):failed.append({'shape':shape['id'],'baseline_blocks_per_sm':old['occupancy_blocks_per_sm_128'],'candidate_blocks_per_sm':new['occupancy_blocks_per_sm_128']})
 ok(screen==report['resource_screen_checks'],'independent fixed screen recomputation exact')
 ok(failed==[{'shape':'rainbow_p0','baseline_blocks_per_sm':12,'candidate_blocks_per_sm':11},{'shape':'two_tone_p0','baseline_blocks_per_sm':12,'candidate_blocks_per_sm':11}],'only two specified occupancy failures')
 ok(report['resource_screen_pass'] is False and report['resource_screen_verdict']=='REJECTED_RESOURCE_SCREEN' and report['capacity_prerequisite_pass'] is True,'capacity feasible but prospective no-occupancy-loss screen rejected')
 ok({(x['registers'],x['local_bytes_per_thread'],x['static_shared_bytes']) for x in rr[:10]}=={(38,0,1040)} and {(x['registers'],x['local_bytes_per_thread'],x['static_shared_bytes']) for x in rr[10:]}=={(39,0,1248)},'physical resource triplets all ten shapes')
 pt={a:(D/(a+'.ptx')).read_text(encoding='utf-8') for a in ['baseline','candidate']};names={a:re.findall(r'\.visible\s+\.entry\s+(\w+)\(',t) for a,t in pt.items()}
 ok(names['baseline']==names['candidate'] and len(names['baseline'])==9,'nine unchanged entry identities')
 unchanged={n:entry(pt['baseline'],n)==entry(pt['candidate'],n) for n in names['baseline'] if n!='up_show'}
 ok(len(unchanged)==8 and all(unchanged.values()) and unchanged==report['other_entry_ptx_byte_equality'],'eight other entries independently byte-exact')
 for a in ['baseline','candidate']:ok((entry(pt[a],'up_show')+'\n')==(D/(a+'-up_show.ptx')).read_text(encoding='utf-8'),'extracted '+a+' up_show exact')
 ok(entry(pt['baseline'],'up_show').split('{',1)[0]==entry(pt['candidate'],'up_show').split('{',1)[0],'up_show ABI exact')
 for name in ['rustc.stdout.log','rustc.stderr.log','probe.stdout.log','probe.stderr.log']:
  t=(D/name).read_text(encoding='utf-8');ok(not any(s in t for s in ['panicked at','error[E','thread \'main\' panicked']),'error scan '+name)
 ok((D/'probe.stderr.log').stat().st_size==0 and not (D/'failure.json').exists(),'no native stderr/failure record')
 live=Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe');pin(live,'b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd')
 for f in D.iterdir():
  if f.is_file():pin(f)
 pin(__file__)
 result={'id':'E031-resource-review','verdict':'PASS_AUDIT_REJECTED_RESOURCE_SCREEN','custody_pass':True,'resource_screen_pass':False,'resource_screen_verdict':'REJECTED_RESOURCE_SCREEN','failed_shapes':failed,'baseline_resources':{'registers':38,'local_bytes':0,'static_shared_bytes':1040},'candidate_resources':{'registers':39,'local_bytes':0,'static_shared_bytes':1248},'other_entry_ptx_exact':8,'changed_entry_ptx_review':'Separate ptx-review.json; this file checks its ABI and retained extraction only.','source_entries_unchanged':162,'live_desktop_binary_unchanged':True,'root_kernel_launches':0,'root_solver_executions':0,'numerical_validation':'not executed','performance_measurement':False,'candidate_accepted':False,'no_direct_primary_or_rescue':True,'interpretation':'The predeclared theoretical occupancy condition failed for two shapes. This is a resource-screen rejection, not a measured runtime speed regression or numerical rejection.','reviewer_native_compiler_gpu_execution':False,'reviewer_failures':[],'checks_passed':checks,'input_sha256':pins,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (O/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'verdict':result['verdict'],'checks':len(checks),'pins':len(pins),'sha256':hashlib.sha256((O/'validation.json').read_bytes()).hexdigest()}))
if __name__=='__main__':main()
