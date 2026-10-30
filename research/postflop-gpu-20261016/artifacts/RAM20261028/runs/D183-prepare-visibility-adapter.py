import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();parent=ROOT/'runs/D183-plan-phase-diagnostic';original=h.read(parent/'protocol.json');receipt=h.read(parent/'execution/rustc.exit.json');assert receipt['returncode']!=0 and not(parent/'probe.exe').exists() and not any((parent/'execution').glob('P*.exit.json'))
for p,digest in original['input_sha256'].items():h.pin(p,digest)
stderr=(parent/'execution/rustc.stderr.log').read_text();assert 'method `key` is private' in stderr and 'field `entries`' in stderr
H=parent/'visibility-adapter';H.mkdir(exist_ok=False)
for name in ['probe.rs','fixtures.json','schema.json','baseline-plan.rs']:shutil.copyfile(parent/name,H/name)
src=(parent/'observed-plan.rs').read_bytes().decode();changes=[('spot.river.key(&it.dealt)','d183_key(spot, &it.dealt)'),('spot.river.entries[key].as_deref().expect("river eval")','d183_eval(spot, key)')]
for old,new in changes:assert src.count(old)==1;src=src.replace(old,new,1)
helper='''
// Read-only visibility adapter: original key formula and public get by its inverse.
fn d183_key(spot:&Spot,dealt:&Dealt)->usize {
 match spot.board.len(){5=>0,4=>{debug_assert_eq!(dealt.len,1);dealt.cards[0] as usize},3=>{debug_assert_eq!(dealt.len,2);let(a,b)=(dealt.cards[0].min(dealt.cards[1]),dealt.cards[0].max(dealt.cards[1]));a as usize*52+b as usize},_=>unreachable!()}
}
fn d183_eval(spot:&Spot,key:usize)->&crate::game::RiverBoardEval {
 let dealt=match spot.board.len(){5=>Dealt::default(),4=>Dealt{cards:[key as u8,0],len:1},3=>Dealt{cards:[(key/52) as u8,(key%52) as u8],len:2},_=>unreachable!()};
 debug_assert_eq!(d183_key(spot,&dealt),key);spot.river.get(&dealt)
}
'''
reverse=src
for old,new in reversed(changes):assert reverse.count(new)==1;reverse=reverse.replace(new,old,1)
assert reverse.encode()==(parent/'observed-plan.rs').read_bytes();(H/'observed-plan.rs').write_bytes(src.encode()+helper.encode())
checks=0
for board in [3,4,5]:
 domain=[0] if board==5 else list(range(52)) if board==4 else [a*52+b for a in range(52) for b in range(a+1,52)]
 for key in domain:
  cards=[] if board==5 else [key] if board==4 else [key//52,key%52]
  rebuilt=0 if board==5 else cards[0] if board==4 else min(cards)*52+max(cards);assert rebuilt==key;checks+=1
  if board==3:assert min(reversed(cards))*52+max(reversed(cards))==key;checks+=1
scripts=[]
for name in ['execute','audit']:
 old=ROOT/'runs'/('D183-'+name+'.py');code=old.read_text();needle="H=ROOT/'runs/D183-plan-phase-diagnostic'";assert code.count(needle)==1;code=code.replace(needle,"H=ROOT/'runs/D183-plan-phase-diagnostic/visibility-adapter'",1)
 if name=='execute':
  code=code.replace("'compiler_runs':1,","'compiler_runs':1,'original_failed_preparation_compiler_runs':1,",1)
 else:
  code=code.replace("'status':'CPU_only_plan_phase_observation_complete'","'status':'CPU_only_plan_phase_observation_complete','read_only_visibility_adapter':True,'original_failed_preparation_compiler_runs':1",1)
  code=code.replace("'scope':'Every byte","'scope':'Two read-only key/table adapters replace inaccessible private calls; original key arithmetic and public get inverse preserved. Their lookup/control cost can perturb representative_DFS/river_tables phases; no claim these are instruction-identical production spans. Every byte",1)
 new=ROOT/'runs'/('D183-'+name+'-visibility-adapter.py');assert not new.exists();new.write_text(code,encoding='utf-8',newline='\n');ast.parse(code);scripts.extend([old,new])
h.save(H/'source-review.json',{'id':'D183-visibility-adapter','at':h.now(),'status':'mechanical_pre_native_visibility_correction','original_protocol_sha256':h.sha(parent/'protocol.json'),'original_failed_compiler_receipt':receipt,'original_stderr_sha256':h.sha(parent/'execution/rustc.stderr.log'),'compiler_error':'Original standalone module cannot call crate-private RiverTable::key or read entries. No native measurements/outputs existed. Preserve original source/protocol/failure; this is not an optimization rescue.','exactly_two_replacements':changes,'adapter_reversal_to_original_observed_source_byte_exact':True,'original_phase_marker_reversal_to_accepted_plan_byte_exact':True,'pure_key_inverse_domain_checks':checks,'original_game_source_sha256':h.sha(h.REPO/'crates/solver/src/game.rs'),'adapter_contract':'For supported root board lengths3/4/5, same min/max key expression. Decode each existing unique key into Dealt and call unchanged public RiverTable::get; get internally indexes original entries using original key. Entire all-field raw comparison against original library remains mandatory. No new numerical operation/order, config/field/phase/order/sample/clock/quality/gate.','timing_limits':'This necessary public adapter can alter instructions in representative_DFS/river_tables. Report those as adapted component spans with paired original outer observer difference; never assert exact production timings, causal removable headroom or a fullcycle gain. Other phases remain literal original operations plus marks.','new_optimizer_or_native_or_GPU_admitted':False})
command=[x.replace(str(parent/'probe.rs'),str(H/'probe.rs')).replace(str(parent/'probe.exe'),str(H/'probe.exe')) for x in original['rustc_command']]
files=[Path(__file__),parent/'protocol.json',parent/'execution/rustc.exit.json',parent/'execution/rustc.stderr.log',ROOT/'epoch/common.py']+scripts+[p for p in H.iterdir() if p.is_file()]+[Path(p) for p in original['input_sha256'] if str(ROOT/'reference') in p]
h.save(H/'protocol.json',{**{k:v for k,v in original.items() if k not in ['at','input_sha256','rustc_command','status']},'at':h.now(),'status':'FROZEN_PRE_CORRECTED_COMPILER_AND_ZERO_NATIVE','rustc_command':command,'original_preparation_protocol_sha256':h.sha(parent/'protocol.json'),'original_failed_compiler_runs':1,'new_compiler_runs':1,'read_only_visibility_adapter':True,'input_sha256':{str(p):h.sha(p) for p in files},'scope':original['scope']+' Original failed compiler preserved; exactly2 read-only private-visibility substitutions with key inverse helpers, no original native observations repeated. Adapter cost disclosed, actual production allphase timing not asserted.'})
for name in ['source-review.json','protocol.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/'D183-visibility-adapter'/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/D183-visibility-adapter/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D183');item.update(stage='Pre-native private-visibility adapter',reason='Original compiler caught two private RiverTable accesses. Frozen read-only public-get adapter preserves formula/order/fields and fixed3process cohort, with explicit timing limitations. No original measurements or repeated native data.');item['evidence'].append({'label':'Visibility correction and timing scope','url':'evidence/D183-visibility-adapter/source-review.json'});s.update(updated_at=h.now(),stage='CPU planner visibility adapter',activity='D183 private-field compiler failure preserved; two read-only API bindings corrected before any native. Same all-field comparison and fixed cohort; E080/16 unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
