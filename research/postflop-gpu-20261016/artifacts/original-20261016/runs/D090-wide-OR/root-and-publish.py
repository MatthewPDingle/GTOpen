"""Raw CPU word/clock/order replay; close component probe without promotion."""
import datetime,functools,json,math,operator,re,statistics,struct,sys,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();P=old.read(H/'protocol-r2.json');original=old.read(H/'protocol.json');q=old.read(H/'report.json');E=H/'execution-r2';done=old.read(E/'complete.json')
assert done['all_children_terminal'] and done['report_sha256']==old.sha(H/'report.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8)
ck(all(P[k]==original[k] for k in ['order','pairs','expected_control_cases','baseline_representative_reference_ms','fresh_minimum_gain_pct','minimum_positive_pairs','command']),'all original source/sampling/numerical/performance gates unchanged')
ck(old.sha(H/'build/probe.exe')==P['compiled_binary_sha256'],'unchanged compiler binary after reader repair')
cg=old.read(H/'compiler-gate.json');ck(set(cg['helpers'])=={'portable_i16','portable_u16','wide_i16','wide_u16'},'four typed paths accounted')
ck(all(x['uses_256bit']==name.startswith('wide') for name,x in cg['helpers'].items()),'actual128/256bit compiled bodies')
w=(H/'typed-call-witness.asm.txt').read_text();calls=re.findall(r'callq\s+(\S+)',w);ck(len(calls)==4 and calls[0]==calls[1] and calls[2]==calls[3] and 'portable_i16' in calls[0] and 'wide_i16' in calls[2] and w.count('cmpw')==4,'all4actual typed calls and independent result checks retained')
control=old.read(H/'control-report.json');raw=(E/'control.bin').read_bytes();ck(old.sha(E/'control.bin')==control['raw_sha256'] and raw[:16]==b'D090-OR-RAW-v1\0\0','full raw control identity');at=16;words=0
lengths=[0,1,7,8,15,16,17,31,32,33,63,64,65,127,128,129,257,513,4097];descs=[(1,1,0,i) for i in range(65536)]+[(n,off,pattern,None) for n in lengths for off in range(4) for pattern in range(1,5)]
for index,(expected_n,expected_off,expected_pattern,single) in enumerate(descs):
 header=struct.unpack_from('<9I',raw,at);at+=36;identity,n,off,pattern,declared,*outputs=header;ck(identity==index and (n,off,pattern)==(expected_n,expected_off,expected_pattern),'raw case order and geometry')
 vectors=[]
 for _ in range(3):
  count,=struct.unpack_from('<Q',raw,at);at+=8;ck(count==n+off+3 and at+2*count<=len(raw),'full vector extent');v=struct.unpack_from('<'+str(count)+'H',raw,at);at+=2*count;vectors.append(v);words+=count
 before,u,s=vectors;ck(before==u==s and all(x==0xb1a5 for x in before[:off]+before[off+n:]),'complete typed images and all guards')
 data=[]
 for i in range(n):
  if pattern==0:x=single
  elif pattern==1:x=0
  elif pattern==2:x=1<<((i+off)%16) if i==n//2 else 0
  elif pattern==3:x=0x8000 if i+1==n else 0
  else:x=(i*1337+i//7+off*79)%65536
  data.append(x)
 ck(tuple(data)==before[off:off+n],'complete actual input values');expected=functools.reduce(operator.or_,data,0);ck(declared==expected and outputs==[expected]*4,'all4full result words')
ck(at==len(raw) and len(descs)==control['cases']==P['expected_control_cases']==65840 and words==control['full_input_post_and_guard_words'],'full raw endpoints and inventories')
last=None;results={};pins={}
for identity in ['control']+P['order']:
 receipt=old.read(E/(identity+'.exit.json'));start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);ck(receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None and start<=end and (last is None or last<=start),'serial successful native process');last=end
 for p in [E/(identity+'.stdout.log'),E/(identity+'.stderr.log'),E/(identity+'.invocation.json'),E/(identity+'.exit.json')]:pins[str(p)]=old.sha(p)
 if identity=='control':continue
 rows=[json.loads(x.split('D090 ',1)[1]) for x in (E/(identity+'.stdout.log')).read_text().splitlines() if x.startswith('D090 ')];ck(len(rows)==1 and rows[0]==q['results'][identity],'full raw benchmark row');r=rows[0]
 ck(r['fresh_results']==r['pretouched_results']==[0]*4 and r['nodes']==1346813 and r['cpu_arena_bytes']==1386321040 and r['shapes']==next(iter(q['results'].values()))['shapes'],'exact fresh solver dimensions/results');results[identity]=r
b=[results[p['baseline']]['fresh_ms'] for p in P['pairs']];a=[results[p['avx2']]['fresh_ms'] for p in P['pairs']];bm,am=statistics.median(b),statistics.median(a);gain=100*(bm-am)/bm;pairg=[100*(x-y)/x for x,y in zip(b,a)];blocks=[statistics.median(pairg[i:i+4]) for i in range(0,16,4)];orders={o:statistics.median(g for p,g in zip(P['pairs'],pairg) if p['order']==o) for o in ['BA','AB']};warm_b=statistics.median(results[p['baseline']]['pretouched_ms'] for p in P['pairs']);warm_a=statistics.median(results[p['avx2']]['pretouched_ms'] for p in P['pairs'])
gates={'baseline_fresh_representative':0.75*P['baseline_representative_reference_ms']<=bm<=1.25*P['baseline_representative_reference_ms'],'fresh_gain_at_least25pct':gain>=P['fresh_minimum_gain_pct'],'at_least13positive_pairs':sum(g>0 for g in pairg)>=P['minimum_positive_pairs'],'positive_paired_median':statistics.median(pairg)>0,'all4blocks_positive':all(x>0 for x in blocks),'both_orders_positive':all(x>0 for x in orders.values()),'pretouched_median_not_slower':warm_a<=warm_b}
ck(all(near(x,y) for x,y in zip(pairg,q['paired_gains_pct'])) and blocks==q['block_median_gains_pct'] and orders==q['order_median_gains_pct'],'all16pairs4blocks2orders arithmetic');ck(near(bm,q['fresh_baseline_median_ms']) and near(am,q['fresh_avx2_median_ms']) and near(gain,q['fresh_gain_pct']),'unrounded fresh medians/gain')
ck(gates==q['gates'] and q['status']==('admit_further_candidate_investigation' if all(gates.values()) else 'closed_component_gate_failed'),'all original gates and outcome');ck(q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0,'no excluded extended or pooled gain observations')
R=ROOT/'comparisons/D090-component-root-check';R.mkdir();report={'at':old.now(),'status':'verified_closed_component_probe' if not all(gates.values()) else 'verified_component_admission_only','checks_passed':checks,'raw_cases':65840,'full_before_after_and_guard_words':words,'four_typed_result_words_each_case':True,'all32native_processes_verified':True,'fresh_baseline_median_ms':bm,'fresh_avx2_median_ms':am,'fresh_gain_pct':gain,'fresh_median_difference_ms':bm-am,'positive_pairs':sum(g>0 for g in pairg),'paired_median_gain_pct':statistics.median(pairg),'blocks':blocks,'orders':orders,'pretouched_baseline_median_ms':warm_b,'pretouched_avx2_median_ms':warm_a,'gates':gates,'raw_sha256':old.sha(E/'control.bin'),'report_sha256':old.sha(H/'report.json'),'preserved_native_sha256':pins,'accepted_source':'E051','accepted_cumulative_gain_unchanged':12.4372274192464,'root_external_independent_review':False,'optimization_accepted':False,'solver_source_activated':False,'gpu_executions':0,'historical_gain_observations_pooled':0,'historical_reference_use':'D088187.8079ms used only as separately frozen representativeness reference; never pooled into current baseline/candidate medians or gains.','limits':'Private CPU q+scale component only, excludes GPU/constructor/snapshot and complete solve costs. New compile-only D089/D090binaries are not the timed E051executable. Source/binary unchanged by merged-symbol reader correction. No ISA/helper/factor/size rescue, native extension or production candidate follows a failed gate.'};old.save(R/'report.json',report);old.custody()
published={}
for directory,prefix in [(H,H.name),(R,R.name)]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb','.obj','.lib','.exp'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():ck(dst.read_bytes()==data,'immutable public artifact')
  else:dst.write_bytes(data)
  ck(urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20).read()==data,'public raw byte verification');published[key]=old.sha(src)
old.save(R/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='D090');e.update(status='rejected' if not all(gates.values()) else 'measured',stage='Closed component probe; no production candidate' if not all(gates.values()) else 'Component gate passed; source qualification pending',correctness='pass',accepted=False,reason=f'65840rawcases exact;32processes retained. Fresh {bm:.4f}to{am:.4f}ms,{gain:.4f}%component gain,{sum(g>0 for g in pairg)}/16positivepairs. Misses25%and13pair component gates. No full-solve claim, source activation or rescue.');e['evidence'] +=[{'label':'D090 full raw/component root replay','url':'evidence/'+R.name+'/report.json'},{'label':'D090 complete fixed isolated result','url':'evidence/'+H.name+'/report.json'}];s.update(state='running',updated_at=old.now(),stage='D090 closed; next independent GPU investigation',activity='Wide serial OR improves isolated fresh scans only11ms; component gate failed. AcceptedE05112.437227%full-cycle gain unchanged; no CPU/GPU source adopted.',active_experiment=None);old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'status':report['status'],'checks':report['checks_passed'],'fresh_gain_pct':gain,'difference_ms':bm-am,'positive_pairs':sum(g>0 for g in pairg),'pretouched_ms':[warm_b,warm_a],'published':len(published),'report_sha256':old.sha(R/'report.json')}),flush=True)
