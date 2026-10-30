"""Freeze full compiled host-tag maps against the separate D124 integer model."""
from pathlib import Path
import ast,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
q=old.read(R/'runs/D125-index-address-audit/report.json');assert all(q['effective_gates'].values())and q['admit_compiled_host_and_full_raw_GPU_controls']
S=R/'runs/E077-source';D=R/'runs/D124-prefix-liveness';A=R/'runs/D092-action-arity-order';previous=R/'runs/E076-plan-control';H=R/'runs/E077-plan-control';assert not H.exists();H.mkdir()
for a,b in [('baseline-plan.rs','accepted-plan.rs'),('candidate-plan.rs','candidate-plan.rs')]:shutil.copyfile(S/a,H/b)
for n in ['game.rs','fixture-0.json','fixture-1.json','fixture-2.json','field-schema.json']:shutil.copyfile(A/n,H/n)
probe=(previous/'probe.rs').read_text(encoding='utf-8').replace('E076','E077')
needle='let a=a.unwrap();let b=b.unwrap();';assert probe.count(needle)==1
probe=probe.replace(needle,'let a=a.unwrap();let mut b=b.unwrap();assert_eq!(a.riv_sorted_idx,b.riv_sorted_idx,"public untagged plan indices");candidate::tag_prefix_reads(&mut b);')
for field,changed in [(36,False),(37,False),(46,True)]:
 line=next(l for l in probe.splitlines()if l.startswith(f'count+=field(&mut f,{field},'));replacement=line.rsplit(',',1)[0]+(','+'true);'if changed else',false);');probe=probe.replace(line,replacement)
probe=probe.replace('all_non_CFV_fields_bitwise_equal','all_non_tag_fields_bitwise_equal');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
decoder=r'''"""Full53 fields and actual compiled high-bit maps versus independently frozen images."""
from pathlib import Path
import array,struct
def vec(f):
 n,=struct.unpack('<Q',f.read(8));assert n<100000000
 v=array.array('Q');v.fromfile(f,n);assert len(v)==n;return v
def replay(path,case,reference,tags):
 checks=0;words=0
 with Path(tags).open('rb')as e:
  assert e.read(16)==b'D124-TAG-RAW1\0\0\0'and struct.unpack('<II',e.read(8))==(case,2)
  original=array.array('Q',[2]);encoded=array.array('Q',[2])
  for p in range(2):
   n,=struct.unpack('<Q',e.read(8));a=array.array('I');a.fromfile(e,n);b=array.array('I');b.fromfile(e,n)
   original.append(n);original.extend(a);encoded.append(n);encoded.extend(b)
  assert e.read(1)==b''
 with Path(path).open('rb')as f,Path(reference).open('rb')as r:
  assert f.read(16)==b'E077-PLAN-RAW1\0\0'and r.read(16)==b'D092-PLAN-RAW1\0\0'
  assert f.read(8)==r.read(8)==struct.pack('<II',case,53)
  sizes=f.read(16);assert sizes==r.read(16)and sizes[:8]==sizes[8:];checks+=4
  for field in range(53):
   assert f.read(4)==r.read(4)==struct.pack('<I',field)
   ac,bc,av,bv=[vec(f)for _ in range(4)];rc1,rc2,rv1,rv2=[vec(r)for _ in range(4)]
   assert ac==bc==rc1==rc2 and av==rv1;checks+=3;words+=len(av)
   if field==46:assert av==original and bv==encoded;checks+=2
   else:assert av==bv;checks+=1
  for _ in range(2):assert vec(f)==vec(r);checks+=1
  assert f.read(1)==r.read(1)==b'';checks+=1
 return {'case':case,'fields':53,'unchanged_fields':52,'baseline_words':words,'root_checks':checks,'all_non_tag_values_capacities_structs_exact':True,'compiled_tags_match_frozen_D124':True,'baseline_all53fields_match_retained_accepted_metadata':True,'raw_bytes':Path(path).stat().st_size}
'''
ast.parse(decoder);(H/'replay.py').write_text(decoder,encoding='utf-8',newline='\n')
execute=r'''"""One compiler per probe/test and exactly12 CPU maps; no GPU/solver timing."""
from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
 B=H/'build';E=H/'execution';assert not B.exists()and not E.exists();B.mkdir();E.mkdir()
 for label,cmd in P['compile_commands'].items():old.child(cmd,B,label,old.env(),600);verify()
 old.child([str(B/'tests.exe'),'--test-threads=1'],E,'unit',old.env(),300);verify();assert 'test result: ok. 3 passed;'in(E/'unit.stdout.log').read_text(encoding='utf-8')
 binary=old.sha(B/'probe.exe');results=[]
 for case in range(12):
  verify();old.ar.refuse_active(old.ar.live_status());old.pin(B/'probe.exe',binary)
  label=f'case-{case:02d}';raw=E/(label+'.bin');old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),180);verify()
  r=replay(raw,case,P['models'][case]['reference'],P['models'][case]['tags']);r['raw_sha256']=old.sha(raw);results.append(r);old.save(E/(label+'.replay.json'),r);print(json.dumps(r),flush=True)
 old.save(H/'report.json',{'id':'E077-plan-control','at':old.now(),'status':'pass_compiled_prefix_tags_against_retained_model','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'all52_other_fields_values_capacities_structs_exact':True,'original_public_plan_values_unchanged':True,'all12_compiled_tag_arrays_match_D124':True,'original_and_candidate_plan_tests_pass':True,'plan_tests':3,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'performance_measurement':False,'candidate_accepted':False,'limits':'Complete CPU metadata and compiled tag controls only. No GPU numerical/state or actual CPU/material/capacity/full-cycle performance conclusion. Root replay is not external independent audit.'});verify()
print('E077 compiled host maps and3 plan tests pass; no GPU numeric/speed result.',flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
P0=old.read(previous/'protocol-r2.json');command=[x.replace(str(previous),str(H)).replace('e076_plan_probe','e077_plan_probe')for x in P0['compile_commands']['rustc']]
testcmd=command.copy();testcmd[testcmd.index('-o')+1]=str(H/'build/tests.exe');testcmd.insert(1,'--test')
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
for p,h in deps.items():old.pin(p,h)
models=[{'case':i,'reference':str(A/'execution'/f'case-{i:02d}.bin'),'tags':str(D/f'case-{i:02d}-tags.bin')}for i in range(12)]
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],*[p for p in S.iterdir()if p.is_file()],D/'protocol.json',D/'report.json',R/'runs/D125-index-address-audit/protocol.json',R/'runs/D125-index-address-audit/report.json',R/'runs/D125-index-address-audit/finalization-repair.json',C/'common_e051_live.py',C/'protected-main.json',*[Path(v)for m in models for k,v in m.items()if k!='case']]
P={'id':'E077-plan-control','at':old.now(),'status':'FROZEN_PRE_COMPILER_NATIVE','compile_commands':{'rustc':command,'rustc-tests':testcmd},'input_sha256':deps|{str(p):old.sha(p)for p in paths},'models':models,'fixed_protocol':'One probe compiler, one test compiler, one three-test CPU invariant/tag/idempotence process and exactly12 complete raw CPU metadata processes. Public build values remain unchanged before tag; after private tagging all52 other fields/capacities/structs exact and full sorted-index vectors must match separate D124 raw maps. No repeats/extensions/source/helper/map variants after an actual mismatch. No GPU kernels/solver/speed or source activation.','candidate_accepted':False};old.save(H/'protocol.json',P)
for p in H.iterdir():
 if not p.is_file():continue
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'all_prepared_artifacts_HTTP_byte_verified':True,'compiler_or_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E077');e.update(stage='12 compiled host-tag maps and invariant tests',reason='Same frozen source that passed effective resource/byte-address prerequisites. Verify actual compiled in-place tags against D124 for every sorted-index word and all52 other fields, plus original/tag/idempotence plan tests. No GPU numeric or speed result.');e['evidence'].append({'label':'Frozen compiled host-tag controls','url':'evidence/E077-plan-control/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E077',stage='E077 compiled host-tag accuracy controls',activity='Run exactly12 full CPU metadata maps and3 plan tests before GPU numerical cases. No source/helper/flag/width changes or timing result. E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
print('E077 host protocol',old.sha(H/'protocol.json'),flush=True)
