"""Freeze original-kernel disjoint/in-place numerical controls for the CFV layout."""
from pathlib import Path
import ast,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
CPU=R/'runs/E076-plan-control';q=old.read(CPU/'report.json');assert q['status']=='pass_compiled_CFV_layout_against_retained_model'and len(q['cases'])==12 and q['original_and_candidate_plan_unit_tests_pass']
for p,h in old.read(CPU/'protocol-r2.json')['input_sha256'].items():old.pin(p,h)
prior=R/'runs/E075-kernel-control';RES=R/'runs/E075-resource';S=R/'runs/E076-source';H=R/'runs/E076-kernel-control';assert not H.exists();H.mkdir()
ptx=RES/'execution/baseline-compute_120.ptx';resource=old.read(RES/'report.json');old.pin(ptx,resource['ptx_sha256']['baseline-compute_120'])
old.pin(old.REPO/'crates/solver/src/gpu/kernels.cu',old.BASE['crates/solver/src/gpu/kernels.cu'])
for arm in ['baseline','candidate']:shutil.copyfile(ptx,H/(arm+'.ptx'))
shutil.copyfile(prior/'discounts.rs',H/'discounts.rs')
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E075','E076')
def edit(a,b):
 global probe
 assert probe.count(a)==1,a;probe=probe.replace(a,b)
edit('let immutable=vec![nodes.clone()', '''let mut alias_slots=slots.clone();let mut alias_cfv=cfv.clone();
  if na==1 {alias_slots[4]=parent as u32;let child=slots[4] as usize;for i in 0..max {alias_cfv[parent*max+i]=cfv[child*max+i];}}
  let immutable=vec![nodes.clone()''')
edit('id(&mut input,index);words(&mut input,','let mut alias_immutable=immutable.clone();alias_immutable[10]=alias_slots.clone();\n  id(&mut input,index);words(&mut input,')
edit('for v in &immutable {words(&mut input,v);}for v in [&regret,&strategy,&cfv] {words(&mut input,&fb(v));}', '''for (images,seed) in [(&immutable,&cfv),(&alias_immutable,&alias_cfv)] {
   for v in images {words(&mut input,v);}for v in [&regret,&strategy,seed] {words(&mut input,&fb(v));}
  }''')
edit('let dslot=stream.clone_htod(&slots).unwrap();','')
edit('let mut dr=stream.clone_htod(&regret).unwrap();', '''let selected_cfv=if label=="candidate" {&alias_cfv}else{&cfv};
   let selected_immutable=if label=="candidate" {&alias_immutable}else{&immutable};
   let dslot=stream.clone_htod(if label=="candidate" {&alias_slots}else{&slots}).unwrap();
   let mut dr=stream.clone_htod(&regret).unwrap();''')
edit('let mut dv=stream.clone_htod(&cfv).unwrap();','let mut dv=stream.clone_htod(selected_cfv).unwrap();')
edit('assert_eq!(post,immutable,"immutable inputs case{index}/{label}");','assert_eq!(&post,selected_immutable,"immutable inputs case{index}/{label}");')
edit('let seeds=[fb(&regret),fb(&strategy),fb(&cfv)];','let seeds=[fb(&regret),fb(&strategy),fb(selected_cfv)];')
edit('if let Some(ref before)=expected {assert_eq!(&result,before,"original/candidate case{index}");}else{expected=Some(result.clone());}', '''if let Some(ref before)=expected {
    assert_eq!(&result[..2],&before[..2],"all regret/strategy words case{index}");
    let mut expected_cfv=fb(&alias_cfv);
    if count!=0 {expected_cfv[parent*max..parent*max+nh].copy_from_slice(&before[2][parent*max..parent*max+nh]);}
    assert_eq!(result[2],expected_cfv,"complete expected aliased CFV image case{index}");
   }else{expected=Some(result.clone());}''')
edit('"parent_child_rows_disjoint":true','"baseline_parent_child_rows_disjoint":true,"candidate_parent_child_alias":na==1')
probe=probe.replace('all_raw_exact','all_logical_outputs_and_owned_images_exact')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
audit=r'''"""Decode every physical image, guard and logical output for disjoint/in-place rows."""
from pathlib import Path
import json,struct,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
P=old.read(H/'protocol.json');C=old.read(H/'execution/complete.json');cases=old.read(H/'corpus.json')['cases'];checks=0
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in C['raw_file_sha256'].items():old.pin(p,h)
def req(v,label):
 global checks
 assert v,label;checks+=1
class Reader:
 def __init__(self,p,magic):self.data=Path(p).read_bytes();req(self.data.startswith(magic),'framing');self.at=len(magic)
 def id(self):n,=struct.unpack_from('<I',self.data,self.at);self.at+=4;return n
 def vec(self):
  n,=struct.unpack_from('<Q',self.data,self.at);self.at+=8;req(n<=1000000 and self.at+4*n<=len(self.data),'bounded complete array');v=memoryview(self.data)[self.at:self.at+4*n].cast('I');self.at+=4*n;return v
 def eof(self):req(self.at==len(self.data),'full endpoint')
raw=Path(P['raw_output']);readers=[Reader(raw/n,m)for n,m in [('inputs.bin',b'E076_IN1'),('baseline.bin',b'E076_OUT1'),('candidate.bin',b'E076_OUT1'),('baseline-inputs.bin',b'E076_IM1'),('candidate-inputs.bin',b'E076_IM1')]]
inp,base,cand,bi,ci=readers;output_words=immutable_words=guards=aliases=0
for case in cases:
 for r in readers:req(r.id()==case['id'],'fixed case order')
 req(list(inp.vec())==case['descriptor'],'exact case descriptor')
 nh,na,p,role,count=[case[k]for k in ['hands','actions','p','role','count']];nn=na+8;stride=nh+5
 images=[];seeds=[]
 for arm in range(2):images.append([inp.vec()for _ in range(12)]);seeds.append([inp.vec()for _ in range(3)])
 for arm,br,ir in [(0,base,bi),(1,cand,ci)]:
  imm=images[arm];seed=seeds[arm]
  req([len(x)for x in imm]==[3,nn,nn,2*nn,nn,na+4,nn,6*max(nh,1)+7,2*nn,5+na*nh+17,nn,3],'immutable geometry')
  req(list(imm[11])==case['discount_bits'],'production discount bits')
  req(imm[0][1]==2 and imm[1][2]==(1-p if role==2 else p)and imm[2][2]==na,'node/actor/arity')
  req(imm[3][4]==13 and imm[3][5]==0 and imm[4][2]==2 and imm[6][2]==3,'node offsets/reach')
  req(list(imm[8][4:6])==([5,0]if role==1 else[0xffffffff,0xffffffff]),'lock path')
  req(list(imm[5][2:2+na])==list(range(4,4+na)),'child indices')
  expected_slots=list(range(nn));expected_slots[4:4+na]=list(reversed(range(4,4+na)))
  if arm==1 and na==1:expected_slots[4]=2
  req(list(imm[10])==expected_slots,'only sole child may alias parent row')
  req([len(x)for x in seed]==[13+na*nh+17,13+na*nh+17,(nn+3)*stride+17],'seed geometry')
  result=[br.vec()for _ in range(3)];post=[ir.vec()for _ in range(12)]
  req(all(x==y for x,y in zip(imm,post)),'every actual immutable device word')
  req([len(x)for x in result]==[len(x)for x in seed],'full output lengths')
  for kind,(v,s)in enumerate(zip(result,seed)):
   lo=2*stride if kind==2 else13;size=(nh if kind==2 else na*nh)if count and(kind==2 or role==0)else0
   req(v[:lo]==s[:lo]and v[lo+size:]==s[lo+size:],'all nonowned and guard words unchanged')
   output_words+=len(v);guards+=len(v)-size
  immutable_words+=sum(len(x)for x in post)
  if arm==0:before=result
  else:
   req(all(x==y for x,y in zip(before[:2],result[:2])),'whole regret/strategy arrays bitwise exact')
   if count:req(before[2][2*stride:2*stride+nh]==result[2][2*stride:2*stride+nh],'whole logical parent CFV output bitwise exact')
   expected=list(seed[2])
   if count:expected[2*stride:2*stride+nh]=before[2][2*stride:2*stride+nh]
   req(list(result[2])==expected,'complete expected physical candidate CFV image')
 req(all(images[0][i]==images[1][i]for i in range(12)if i!=10),'all other arm metadata equal')
 req(seeds[0][0]==seeds[1][0]and seeds[0][1]==seeds[1][1],'identical mutable arena seeds')
 expected=list(seeds[0][2])
 if na==1:
  expected[2*stride:3*stride]=seeds[0][2][4*stride:5*stride];aliases+=1
 req(list(seeds[1][2])==expected,'candidate seed changes only by own child-row copy')
for reader in readers:reader.eof()
summary=C['raw_marker_summary'];req(summary['cases']==len(cases)==819 and summary['kernel_launches']==1638,'exact application launch inventory')
req((output_words,immutable_words,guards)==(summary['output_words_both_arms'],summary['immutable_words_both_arms'],summary['guard_words_both_arms']),'every raw word counted')
markers=[json.loads(x.split('E076_UNIT ',1)[1])for x in (H/'execution/probe.stdout.log').read_text(encoding='utf-8').splitlines()if 'E076_UNIT 'in x];req(len(markers)==820,'marker inventory')
for case,marker in zip(cases,markers[:-1]):
 req(marker['id']==case['id']and marker['baseline_parent_child_rows_disjoint']and marker['candidate_parent_child_alias']==(case['actions']==1),'per-case row contract')
 witnesses=marker['disjoint_device_ranges'];req([x['arm']for x in witnesses]==['baseline','candidate'],'both actual device witnesses')
 nh=case['hands'];na=case['actions'];stride=nh+5;nn=na+8
 lengths=[(13+na*nh+17)*4]*2+[((nn+3)*stride+17)*4]
 for witness in witnesses:
  regions=witness['regions'];req(len(regions)==3 and[x[1]for x in regions]==lengths,'physical mutable extents')
  req(all(isinstance(p,int)and p>0 and p+n<2**64 for p,n in regions),'valid owned pointers')
  req(all(regions[i][0]+regions[i][1]<=regions[j][0]or regions[j][0]+regions[j][1]<=regions[i][0]for i in range(3)for j in range(i+1,3)),'regret/strategy/CFV allocations disjoint')
old.custody();OUT=R/'comparisons/E076-kernel-control-root-check';assert not OUT.exists();OUT.mkdir()
report={'id':'E076-kernel-control','at':old.now(),'status':'pass_scoped_in_place_CFV_raw_equivalence','root_cross_check_only':True,'checks':checks,'cases':819,'alias_cases':aliases,'kernel_launches':1638,'output_words_both_arms':output_words,'immutable_words_both_arms':immutable_words,'guard_words_both_arms':guards,'logical_parent_and_full_regret_strategy_outputs_exact':True,'full_physical_images_and_actual_inputs_match_own_expected':True,'raw_file_sha256':C['raw_file_sha256'],'protocol_sha256':old.sha(H/'protocol.json'),'source_main_live_PTX_custody_pass':True,'performance_measured':False,'candidate_accepted':False,'limits':'Fixed corpus and root decoder only. Physical layouts intentionally differ; complete expected per-arm buffers are validated. Not universal NaN/alias proof or external independent audit. Integrated whole solver/state/graph/material and all performance gates remain.'};old.save(OUT/'report.json',report);print(json.dumps({k:report[k]for k in ['status','checks','cases','alias_cases','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']}),flush=True)
'''
audit=audit.replace('else13','else 13').replace('else0','else 0')
ast.parse(audit);(H/'audit.py').write_text(audit,encoding='utf-8',newline='\n')
execute=(prior/'execute.py').read_text(encoding='utf-8').replace('E075','E076')
execute=execute.replace("assert old.read(P['resource_report'])['status']=='pass_compiled_uniform_load_prerequisites'","assert old.read(P['plan_report'])['status']=='pass_compiled_CFV_layout_against_retained_model'")
execute=execute.replace('all_raw_exact','all_logical_outputs_and_owned_images_exact')
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
corpus=old.read(prior/'corpus.json');corpus.update(id='E076-in-place-CFV-corpus',at=old.now(),adaptation='Same819 case descriptors/order/discounts/values. For na1 only, candidate childslot aliases its parent and parent-row seed is copied from original child. Both full expected input images retained. No float operations or kernel changes.',alias_cases=sum(c['actions']==1 for c in corpus['cases']))
old.save(H/'corpus.json',corpus)
old.save(H/'source-review.json',{'id':'E076-alias-source-review','at':old.now(),'candidate_plan_sha256':old.sha(S/'candidate-plan.rs'),'plan_report_sha256':old.sha(CPU/'report.json'),'kernel_source_sha256':old.BASE['crates/solver/src/gpu/kernels.cu'],'kernel_PTX_sha256':old.sha(ptx),'source_reasoning':'Only one-action parents can share their unique action child. Existing learning path reads child CFV into vc[0], computes regret before final CFV store; locked and opponent paths read the same hand before final store. No cross-hand reads in up_action, and cfv is a single non-restrict mutable pointer. Disjoint pairs require child arity>=2; actual lifetime and graph controls exclude all other same-stage row collisions and any chance-orbit reference to the shared child. No CUDA recompilation, resource/counter query, early store, dispatch, float, update or schedule change.','compiled_resource_scope':'Exact accepted CUDA/PTX reused. Per-kernel registers/local/shared/ABI/launch unchanged by host allocator. Aggregate graph/device/host peak/capacity and CPU costs still require integrated measurement.','raw_control_scope':'819 disjoint/aliased cases. Full logical parent CFV, whole regret/strategy arrays, full expected physical output/guard images and all actual input bytes. Arity>1 remains disjoint, na1 in-place. No claim that distinct physical CFV layouts are byte-identical.'})
oldP=old.read(prior/'protocol.json');deps={p:h for p,h in oldP['input_sha256'].items()if Path(p).suffix in ['.rlib','.lib']}
for p,h in deps.items():old.pin(p,h)
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],*[p for p in S.iterdir()if p.is_file()],CPU/'protocol-r2.json',CPU/'report.json',D if False else R/'runs/D122-cfv-lifetimes/report.json',C/'common_e051_live.py',C/'protected-main.json',old.REPO/'crates/solver/src/gpu/kernels.cu',old.REPO/'crates/solver/src/cfr.rs']
P={'id':'E076-kernel-control','at':old.now(),'status':'FROZEN_PRE_FIRST_NUMERICAL_LAUNCH','rustc_command':[x.replace(str(prior),str(H))for x in oldP['rustc_command']],'input_sha256':deps|{str(p):old.sha(p)for p in paths},'plan_report':str(CPU/'report.json'),'raw_output':str(H/'evidence'),'expected_cases':819,'expected_launches':1638,'sealed_PTX_sha256':{arm:old.sha(H/(arm+'.ptx'))for arm in ['baseline','candidate']},'scope':'One Rust compiler, exactly one819pair/1638launch process using identical accepted saved PTX(noNVRTC), separate root raw decoder. Fixed descriptors with candidate na1 row alias. Preserve every expected input/output/guard word for each layout; no full physical-file equality requirement across changed row maps. No numeric retry/extensions/source/layout/placement variants after failure, no speed samples.','candidate_accepted':False};old.save(H/'protocol.json',P)
for p in H.iterdir():
 if not p.is_file():continue
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'all_prepared_inputs_HTTP_byte_verified':True,'numerical_launches':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E076');e.update(stage='819 disjoint/in-place GPU pairs',correctness='All12 compiled plan maps and51 other fields exact',reason='Compiled plans match frozen D122 for every slot; other51 fields/capacities/structs exact and original/candidate unit invariants pass. Same accepted PTX enters819 full raw disjoint/in-place numerical controls. No speed result.');e['evidence'].extend([{'label':'Completed standalone unit harness protocol','url':'evidence/E076-plan-control/protocol-r2.json'},{'label':'Frozen raw in-place controls','url':'evidence/E076-kernel-control/protocol.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E076',stage='E076 GPU in-place CFV accuracy controls',activity='All12 compiled CPU maps match the independent frozen lifetime model. Run fixed819 disjoint/in-place GPU pairs with full logical outputs and each expected physical image. E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'cases':819,'alias_cases':corpus['alias_cases'],'numerical_launches':0}),flush=True)
