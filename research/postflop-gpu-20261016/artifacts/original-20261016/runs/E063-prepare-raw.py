"""Freeze byte controls for E063's intentionally packed input representation."""
import ast,collections,hashlib,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E063-resource';resource=old.read(RES/'report.json');rp=old.read(RES/'protocol.json');S=ROOT/'runs/E063-source';C=ROOT/'runs/D102-card-cutoffs-r3'
assert resource['status']=='pass_resource_feasibility_only' and all(resource['gates'].values()) and resource['kernel_launches']==resource['solver_executions']==0
for p,h in rp['input_sha256'].items():old.pin(p,h)
for label in ['rustc','probe']:assert old.read(RES/'execution'/(label+'.exit.json'))['returncode']==0
def show(path):
 t=path.read_text(encoding='utf-8');a=t.index('.visible .entry up_show(');b=t.index('.visible .entry ',a+1);return t[a:b]
bt=show(RES/'execution/baseline-compute_120.ptx');ct=show(RES/'execution/candidate-compute_120.ptx')
def counts(t):
 return {'entry_lines':len(t.splitlines()),'register_threshold_unsigned_lt_sites':len(re.findall(r'setp\.lt\.u32\s+%p\d+,\s*%r\d+,\s*%r\d+;',t)),'global11bit_masks':len(re.findall(r'and\.b32\s+%r\d+,\s*%r\d+,\s*2047;',t)),'local6bit_masks':len(re.findall(r'and\.b32\s+%r\d+,\s*%r\d+,\s*63;',t)),'local11shifts':len(re.findall(r'shr\.u32\s+%r\d+,\s*%r\d+,\s*11;',t)),'local17shifts':len(re.findall(r'shr\.u32\s+%r\d+,\s*%r\d+,\s*17;',t))}
bs,cs=counts(bt),counts(ct);assert bs['register_threshold_unsigned_lt_sites']>0 and cs['register_threshold_unsigned_lt_sites']==0
assert cs['global11bit_masks']==2 and cs['local6bit_masks']==4 and cs['local11shifts']==cs['local17shifts']==2
old.save(RES/'compiled-mechanism.json',{'at':old.now(),'baseline':bs,'candidate':cs,'ptx_sha256':{v:old.sha(RES/'execution'/(v+'-compute_120.ptx')) for v in ['baseline','candidate']},'resource_report_sha256':old.sha(RES/'report.json'),'status':'expected_packed_cutoff_mechanism_emitted','root_review_only':True,'observation':'Original register-threshold unsigned less-than sites disappear;2global masks and4local count extractions emitted. Three-loop code has a larger static PTX body.','limits':'Static virtual-code sites/line counts are not dynamic branches, machine instruction bytes, instruction-cache counters or speed. Current actual driver resource/occupancy filters pass,38to40nominal registers same allocated bucket.'})
H=ROOT/'runs/E063-kernel-control';assert not H.exists();H.mkdir();prior=ROOT/'runs/E062-kernel-control'
for n in ['accepted-evaluator.rs','corpus.json']:(H/n).write_bytes((prior/n).read_bytes())
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
(H/'helper.rs').write_bytes((C/'helper.rs').read_bytes())
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E062_EXACT','E063_EXACT');probe='//! E063: packed per-card cutoff representation vs accepted E051, no timing.\n'+probe.split('\n',1)[1]
adapter=r'''
struct GpuPlan {num_slots:usize,hand_c1:[Vec<u32>;2],hand_c2:[Vec<u32>;2],riv_off:[Vec<u32>;2],riv_cnt:[Vec<u32>;2],riv_sorted_idx:[Vec<u32>;2],riv_lower:[Vec<u32>;2],riv_upper:[Vec<u32>;2],riv_card_off:[Vec<u32>;2],riv_card_pos:[Vec<u32>;2]}
include!("helper.rs");
// Apply the exact staged constructor helper to the one active direction/slot.
// Corpus padding and all unrelated device words remain untouched.
fn packed_geometry(g:&Value)->Value {
 let a=&g["arrays"];let pb=words(&a["p_off"])[1] as usize;let m=n(g,"m_p");let co=words(&a["o_card_off"]);let cp=words(&a["o_card_pos"]);let cb=co[53] as usize;let ce=co[105] as usize;
 let pl=words(&a["p_lower"]);let pu=words(&a["p_upper"]);let pi=words(&a["p_idx"]);
 let plan=GpuPlan{num_slots:1,hand_c1:[words(&a["pc1"]),Vec::new()],hand_c2:[words(&a["pc2"]),Vec::new()],riv_off:[vec![0],vec![0]],riv_cnt:[vec![m as u32],vec![0]],riv_sorted_idx:[pi[pb..pb+m].to_vec(),Vec::new()],riv_lower:[pl[pb..pb+m].to_vec(),Vec::new()],riv_upper:[pu[pb..pb+m].to_vec(),Vec::new()],riv_card_off:[vec![0;53],co[53..106].iter().map(|x|*x-cb as u32).collect()],riv_card_pos:[Vec::new(),cp[cb..ce].to_vec()]};
 let (lo,hi)=pack_show_bounds(&plan);let mut lower=pl;let mut upper=pu;lower[pb..pb+m].copy_from_slice(&lo[0]);upper[pb..pb+m].copy_from_slice(&hi[0]);let mut out=g.clone();out["arrays"]["p_lower"]=json!(lower);out["arrays"]["p_upper"]=json!(upper);out
}
'''
needle='fn upload_u32(';assert probe.count(needle)==1;probe=probe.replace(needle,adapter+'\n'+needle)
needle='  let (after,cc,cw,csnap)=run_variant(&s,&cf,g,c,128,&active)?;';assert probe.count(needle)==1;probe=probe.replace(needle,'  let cg=packed_geometry(g);\n  let (after,cc,cw,csnap)=run_variant(&s,&cf,&cg,c,128,&active)?;')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(prior/'execute.py').read_text(encoding='utf-8').replace('E062','E063').replace('prefix address mapping','packed per-card cutoff')
expected=r'''
def packed_expected(g):
 a=g['arrays'];lo=list(a['p_lower']);hi=list(a['p_upper']);b=a['p_off'][1]
 for j in range(b,b+g['m_p']):
  h=a['p_idx'][j];lb=a['p_lower'][j];ub=a['p_upper'][j]
  for x,key in enumerate(['pc1','pc2']):
   card=a[key][h];v=a['o_card_pos'][a['o_card_off'][53+card]:a['o_card_off'][54+card]]
   # Independent linear classification, not the Rust helper's partition_point.
   l=sum(pos<lb for pos in v);u=sum(pos<ub for pos in v);assert 0<=l<=u<=51 and 0<=lb<=ub<=1326
   if x==0:lo[j]=lb|(l<<11)|(u<<17)
   else:hi[j]=ub|(l<<11)|(u<<17)
 return lo,hi
'''
needle='verify()\nwith old.ar.exclusive_lock';assert runner.count(needle)==1;runner=runner.replace(needle,expected+'\n'+needle)
needle="expected={n:g['arrays'][key] for n,key in names.items()}|{'reach':case['reach_o_bits']};assert {v['buffer']:v['actual_device_words'] for v in snapshot}==expected"
assert runner.count(needle)==1;runner=runner.replace(needle,"expected={n:g['arrays'][key] for n,key in names.items()}|{'reach':case['reach_o_bits']}\n    if arm=='candidate':expected['pl'],expected['pu']=packed_expected(g)\n    assert {v['buffer']:v['actual_device_words'] for v in snapshot}==expected")
needle='assert snapshots[0]==snapshots[1];';assert runner.count(needle)==1;runner=runner.replace(needle,"assert [v for v in snapshots[0] if v['buffer'] not in ['pl','pu']]==[v for v in snapshots[1] if v['buffer'] not in ['pl','pu']];")
needle="'all_actual_device_inputs_exact':True,";assert runner.count(needle)==1;runner=runner.replace(needle,needle+"'boundary_representation_intentionally_differs':True,'each_arm_actual_metadata_matches_independent_expected_words':True,'limits':'Full direct kernel outputs and every actual immutable buffer word. Candidate pl/pu intentionally packed by exact staged Rust helper; independently expected via Python linear classification. Other19inputs byte-identical across arms. No solver/state/graph/capacity/speed claim.',")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
oldp=old.read(prior/'execution-plan.json');P={k:oldp[k] for k in ['cases','kernel_launches','retained_corpus_protocol_sha256']};P.update(id='E063-kernel-control-execution',at=old.now(),status='FROZEN_PRE_FIRST_NUMERICAL_LAUNCH',source_manifest_sha256=old.sha(S/'manifest.json'),resource_report_sha256=old.sha(RES/'report.json'),rustc_command=[s.replace(str(prior),str(H)) for s in oldp['rustc_command']],scope='Same364retained physical geometry/reach cases,728fresh kernels. Baseline uses original global bounds. Candidate uses exact staged constructor helper via a mirror field struct and one-slot adapter; validate every actual post-device word against independent linear-classification packing, unchanged lower11bits and all unrelated buffers. Full outputs/guards and rank/nonfinite/zero/count/tail/rounding controls exact. Fail closes fixed form without algorithm variant or extra cases. No timing.',performance_measured=False,candidate_accepted=False)
paths=[*H.iterdir(),*S.iterdir(),RES/'report.json',RES/'protocol.json',RES/'compiled-mechanism.json',C/'report.json',C/'helper.rs',Path(__file__),old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in oldp['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'execution-plan.json',P)
published={}
for folder in [RES,H]:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.bin']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'native_numerical_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E063');e.update(stage='Complete raw numerical matrix',reason='Current10shape resource/ABI filters pass:38to40registers same allocated bucket, no occupancy/local/shared/fit loss. Compiled cutoff extractions emitted; register-threshold unsigned comparisons removed; static PTX grows. Numerical/whole-cycle qualification still required.');e['evidence'].extend([{'label':'Compiled mechanism and code growth','url':'evidence/E063-resource/compiled-mechanism.json'},{'label':'First raw GPU protocol','url':'evidence/E063-kernel-control/execution-plan.json'}]);st.update(updated_at=old.now(),stage='E063 raw packed-metadata numerical controls',activity='364fixed differential cases. Verify all output/guard bits and each arm actual metadata, including intentionally packed boundaries. No speed result yet.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'raw_matrix_frozen','execution_plan_sha256':old.sha(H/'execution-plan.json'),'baseline_mechanism':bs,'candidate_mechanism':cs,'published':len(published)}),flush=True)
