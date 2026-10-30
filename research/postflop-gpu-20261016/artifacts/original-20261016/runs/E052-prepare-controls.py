"""Replay actual resources and prospectively freeze full raw GPU cache-width controls."""
import hashlib,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
R=ROOT/'runs/E052-resource';P=old.read(R/'protocol.json');r=old.read(R/'report.json');assert r['status']=='pass_resource_feasibility_only' and all(r['gates'].values())
for p,h in P['input_sha256'].items():old.pin(p,h)
def entries(path):
 t=path.read_text();out={};i=0
 while True:
  i=t.find('.visible .entry ',i)
  if i<0:break
  n=t.index('(',i);name=t[i+len('.visible .entry '):n].strip();a=t.index('{',n);j=a+1;depth=1
  while depth:
   if t[j]=='{':depth+=1
   elif t[j]=='}':depth-=1
   j+=1
  assert name not in out;out[name]=t[i:j];i=j
 return out
checks=[]
def ck(label,v):checks.append({'label':label,'passed':bool(v)});assert v,label
raw=[json.loads(x.split('E052_RESOURCE ',1)[1]) for x in (R/'execution/probe.stdout.log').read_text().splitlines() if 'E052_RESOURCE ' in x]
ck('22 raw resource rows equal report',raw==r['raw_markers'] and len(raw)==22)
for arch in ['compute_120','compute_75']:
 b,c=[entries(R/'execution'/(arm+'-'+arch+'.ptx')) for arm in ['baseline','candidate']]
 ck(arch+' exactly nine entries',set(b)==set(c)==set(P['expected_entries']))
 for name in b:ck(arch+' body '+name,(b[name]!=c[name]) if name=='up_show' else b[name]==c[name])
 sig=lambda t:re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+up_show_param_([0-9]+)',t.split('{',1)[0])
 ck(arch+' same27parameter ABI',sig(b['up_show'])==sig(c['up_show']) and len(sig(c['up_show']))==27)
 ck(arch+' actual16bit shared load/store',bool(re.search(r'ld\.shared(?:\.[a-z]+)*\.u16',c['up_show'])) and bool(re.search(r'st\.shared(?:\.[a-z]+)*\.(?:u16|b16)',c['up_show'])))
for name,detail in r['details'].items():
 b,c=detail['baseline'],detail['candidate'];nh,m=P['shape_dimensions'][name]
 ck(name+' equal raw row',b in raw and c in raw)
 ck(name+' actual register/local/static unchanged',(b['registers'],b['local_bytes_per_thread'],b['static_shared_bytes'])==(c['registers'],c['local_bytes_per_thread'],c['static_shared_bytes'])==(38,0,1040))
 ck(name+' exact reservations',b['dynamic_shared_bytes']==4*nh+16*m and c['dynamic_shared_bytes']==4*nh+12*m)
 ck(name+' maxthreads fits',b['max_threads']==c['max_threads']==1024 and b['fits_default_limits'] and c['fits_default_limits'])
 ck(name+' no occupancy loss',all(t==u and y>=x for (t,x),(u,y) in zip(b['occupancy_by_threads'],c['occupancy_by_threads'])) and len(c['occupancy_by_threads'])==3)
for name in ['rustc','probe']:
 e=old.read(R/'execution'/(name+'.exit.json'));ck(name+' terminal0',e['returncode']==0 and e['error'] is None and e['cleanup'] is None)
RR=ROOT/'comparisons/E052-resource-root-check';RR.mkdir();old.save(RR/'report.json',{'at':old.now(),'status':'pass_resource_feasibility_only','root_cross_check_only':True,'checks':checks,'checks_passed':len(checks),'resource_report_sha256':old.sha(R/'report.json'),'registers_before_after':[38,38],'local_bytes_per_thread':0,'static_shared_bytes':1040,'exact_abi_other8_entries_both_arches':True,'kernel_launches':0,'performance_measured':False,'candidate_accepted':False})
H=ROOT/'runs/E052-kernel-control';H.mkdir();parent=ROOT/'runs/D051-show-physical256-exact'
for name in ['accepted-evaluator.rs','check_corpus.py']:(H/name).write_bytes((parent/name).read_bytes())
corpus=old.read(parent/'corpus.json');geometries=corpus['geometries'];cases=corpus['cases'];assert len(geometries)==36 and len(cases)==148
stress={'stress_signed_zero':[0,0x80000000],'stress_infinities':[0x7f800000,0xff800000],'stress_nan_payloads':[0x7fc01234,0xffc05678,0x7fc00001,0x7fffffff],'stress_mixed':[0x7fc01234,0x7f800000,0xff800000,0,0x80000000,1,0x80000001,0x3f800000],'stress_signed_extremes':[0x7f7fffff,0xff7fffff,0x3f800000,0xbf800000,1,0x80000001]}
for g in geometries:
 base=next(c for c in cases if c['geometry']==g['id'] and c['count']==2)
 for name,pattern in stress.items():
  row=dict(base);row.update(id='E052-'+g['id']+'-'+name,profile=name,reach_o_bits=[pattern[(i*7+i//11)%len(pattern)] for i in range(len(base['reach_o_bits']))]);cases.append(row)
assert len(cases)==328 and len({c['id'] for c in cases})==328
old.save(H/'corpus.json',corpus)
for arm in ['baseline','candidate']:(H/(arm+'.cu')).write_bytes((ROOT/'runs/E052-source'/(arm+'.cu')).read_bytes())
source=(parent/'probe.rs').read_text().replace('D051','E052')
source=source.replace('//! E052: complete accepted128/candidate256 up_show differential; no timing.','//! E052: exact128thread u32/u16shared-cache differential; no timing.')
source=source.replace('width:u32,active:&[bool])->Result<(Vec<u32>,usize,usize)>','width:u32,narrow:bool,active:&[bool])->Result<(Vec<u32>,usize,usize,Vec<Value>)>')
source=source.replace('shared_mem_bytes:n(g,"dynamic_shared_bytes") as u32','shared_mem_bytes:(n(g,"dynamic_shared_bytes")-if narrow {4*n(g,"m_o")} else {0}) as u32')
source=source.replace('let mut checks=0;let mut input_words=0;','let mut checks=0;let mut input_words=0;let mut snapshots=Vec::new();')
source=source.replace('exact(&$h,&got,stringify!($h))?;checks+=1;','exact(&$h,&got,stringify!($h))?;snapshots.push(json!({"buffer":stringify!($h),"actual_device_words":got}));checks+=1;')
source=source.replace('exact(&bits(&$h),&bits(&got),stringify!($h))?;checks+=1;','exact(&bits(&$h),&bits(&got),stringify!($h))?;snapshots.push(json!({"buffer":stringify!($h),"actual_device_words":bits(&got)}));checks+=1;')
source=source.replace('Ok((out,checks,input_words))','Ok((out,checks,input_words,snapshots))')
source=source.replace('assert_eq!(cs.len(),148)','assert_eq!(cs.len(),328)').replace('"comparison_pairs":148','"comparison_pairs":328')
source=source.replace('for c in cs {for b in words(&c["reach_o_bits"])','for c in cs {if c["profile"].as_str().unwrap().starts_with("stress_"){continue;}for b in words(&c["reach_o_bits"])')
source=source.replace('(&cf,256)','(&cf,128)').replace('"candidate_physical_threads":256','"candidate_physical_threads":128')
source=source.replace('let (before,bc,bw)=run_variant(&s,&bf,g,c,128,&active)?','let (before,bc,bw,bs)=run_variant(&s,&bf,g,c,128,false,&active)?')
source=source.replace('let (after,cc,cw)=run_variant(&s,&cf,g,c,256,&active)?','let (after,cc,cw,csnap)=run_variant(&s,&cf,g,c,128,true,&active)?')
source=source.replace('"candidate_output_bits":after','"candidate_output_bits":after,"baseline_actual_device_inputs":bs,"candidate_actual_device_inputs":csnap')
source=source.replace('"dynamic_shared_bytes":g["dynamic_shared_bytes"],','"baseline_dynamic_shared_bytes":g["dynamic_shared_bytes"],"candidate_dynamic_shared_bytes":n(g,"dynamic_shared_bytes")-4*n(g,"m_o"),')
expected_active=sum(sum(bool(x) for x in g['output_active']) for c in cases for g in geometries if g['id']==c['geometry'] and c['count']>0)
expected_guard=sum(2*(len(g['output_initial'])-(sum(bool(x) for x in g['output_active']) if c['count']>0 else 0)) for c in cases for g in geometries if g['id']==c['geometry'])
source=source.replace('assert_eq!(launches,296);assert_eq!(active_words,78896);assert_eq!(guard_checks,525400);assert_eq!(input_checks,6216);',f'assert_eq!(launches,656);assert_eq!(active_words,{expected_active});assert_eq!(guard_checks,{expected_guard});assert_eq!(input_checks,13776);')
assert 'candidate256' not in source and 'run_variant(&s,&cf,g,c,256' not in source and 'Vec<Value>' in source
(H/'probe.rs').write_text(source,encoding='utf-8',newline='\n')
P2={'id':'E052-kernel-control','at':old.now(),'status':'FROZEN_BEFORE_KERNEL_LAUNCH','cases':328,'kernel_launches':656,'original148valid_geometry_cases_reused':True,'added_fixed180stress_cases':True,'geometries':36,'block_threads_each':128,'expected_active_words':expected_active,'expected_guard_checks':expected_guard,'expected_device_input_buffer_checks':13776,'actual_complete_device_input_snapshots_retained':True,'full_raw_output_snapshots_retained':True,'all_immutable_and_guard_bits_must_match':True,'performance_measured':False,'candidate_accepted':False,'resource_report_sha256':old.sha(R/'report.json'),'resource_root_sha256':old.sha(RR/'report.json'),'source_manifest_sha256':old.sha(ROOT/'runs/E052-source/manifest.json'),'input_sha256':{str(p):old.sha(p) for p in H.iterdir() if p.is_file()}|{str(p):old.sha(p) for p in [parent/'probe.rs',parent/'corpus.json',RR/'report.json',R/'report.json']}}
old.save(H/'protocol.json',P2)
for directory in [RR,H]:
 for src in directory.iterdir():
  key=directory.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E052');e.update(stage='Preparing fixed raw GPU controls',reason='Compiled resource gate passes:regs38/local0/static1040 unchanged; prescribed dynamic reduction, no occupancy loss. Wide-turn occupancy4to5. No speed/numerical claim yet.');e['evidence'] +=[{'label':'E052 root compiled-resource replay','url':'evidence/E052-resource-root-check/report.json'},{'label':'E052 frozen328case raw-control matrix','url':'evidence/E052-kernel-control/protocol.json'}];st.update(updated_at=old.now(),stage='E052 raw GPU control preparation',activity='Resource feasibility passed. Freeze328cases with same128threads; full actual device inputs/outputs/guards retained.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'resource_checks':len(checks),'cases':328,'active_words':expected_active,'guard_checks':expected_guard,'protocol_sha256':old.sha(H/'protocol.json')}),flush=True)
