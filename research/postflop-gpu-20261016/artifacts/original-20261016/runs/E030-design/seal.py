from pathlib import Path
import json,hashlib,re,subprocess,datetime,ast
HERE=Path(__file__).resolve().parent
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
BULK=HERE.parent.parent
OWNED=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/continuation_capacity.rs','crates/solver/src/game.rs']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return p.read_bytes().decode('utf8')
def put(name,x):
 with (HERE/name).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
assert not (HERE/'manifest.json').exists()
accepted_path=BULK/'binaries/E020-postflop_autoresearch.manifest.json'
pins=json.loads(read(accepted_path))['source_sha256']
assert len(pins)==162
assert all(sha(ROOT/p)==h for p,h in pins.items())
base={p:read(HERE/'base'/p) for p in OWNED}
cand={p:read(HERE/'candidate'/p) for p in OWNED}
assert all(sha(HERE/'base'/p)==pins[p] for p in OWNED)
# Exact reversal of the only CUDA delta proves all other text unchanged.
old='    for (int card = threadIdx.x; card < 52; card += blockDim.x) {'
new='    for (int task = threadIdx.x; task < 52; task += blockDim.x) {\n        u32 card = card_off[53 + task];'
assert cand[OWNED[0]].count(new)==1
assert cand[OWNED[0]].replace(new,old)==base[OWNED[0]]
def block(s,marker):
 start=s.index(marker);opening=s.index('{',start);depth=1;i=opening+1
 while depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[start:i]
entries=re.findall(r'extern "C" __global__ void (\w+)\(',base[OWNED[0]])
assert len(entries)==9
assert all(block(base[OWNED[0]],'extern "C" __global__ void '+n)==block(cand[OWNED[0]],'extern "C" __global__ void '+n) for n in entries if n!='up_fold')
bfold=block(base[OWNED[0]],'extern "C" __global__ void up_fold')
cfold=block(cand[OWNED[0]],'extern "C" __global__ void up_fold')
assert bfold[bfold.index('    float partial ='):]==cfold[cfold.index('    float partial ='):]
assert bfold.count('__syncthreads()')==cfold.count('__syncthreads()')
assert cand[OWNED[1]].count('.arg(&self.d_fold_card_off[1 - p])')==2
# Host source outside intended insertion/replacements is preserved; no constructor move changes.
assert cand[OWNED[1]].index('append_fold_card_order(&mut fold_card_off[p]);')<cand[OWNED[1]].index('        Ok(GpuSolver {')
for marker in ['fn iterate(', 'fn iterate_profiled(', 'fn exploitability(', 'fn sweep(', 'fn update_locks(']:
 assert block(base[OWNED[1]],marker)==block(cand[OWNED[1]],marker),marker
assert block(base[OWNED[3]],'pub(super) fn observed_metadata')==block(cand[OWNED[3]],'pub(super) fn observed_metadata')
assert block(base[OWNED[3]],'pub fn stored_capacity_plan')==block(cand[OWNED[3]],'pub fn stored_capacity_plan')
inventory={p:{'before_tests':base[p].count('#[test]'),'after_tests':cand[p].count('#[test]'),'before_ignore':base[p].count('#[ignore'),'after_ignore':cand[p].count('#[ignore')} for p in OWNED}
assert sum(v['after_tests']-v['before_tests'] for v in inventory.values())==1
assert all(v['before_ignore']==v['after_ignore'] for v in inventory.values())
unit_log=read(BULK/'runs/V020-unit/stdout.log')
assert '84 passed; 0 failed; 4 ignored;' in unit_log
# Bounded host integer examples, independent expected orders; not Rust/GPU execution.
ascending=list(range(52));asymmetric=[0]*52
for a,b in [[0,1],[0,2],[0,3],[1,2],[50,51]]:asymmetric[a]+=1;asymmetric[b]+=1
host_cases=[]
for name,counts,want in [('empty',[0]*52,ascending),('full_deck',[51]*52,ascending),('asymmetric',asymmetric,[0,1,2,3,50,51]+list(range(4,50)))]:
 got=sorted(range(52),key=lambda c:(-counts[c],c));assert got==want and sorted(got)==ascending
 host_cases.append({'name':name,'counts':counts,'expected_order':want,'passed':True})
syntax=[]
for p in OWNED[1:]:
 cmd=['rustfmt','--edition','2021','--emit','stdout','--config','skip_children=true',str(HERE/'candidate'/p)]
 r=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=60)
 assert r.returncode==0,(p,r.stderr.decode('utf8',errors='replace'))
 syntax.append({'path':p,'command':cmd,'exit_code':r.returncode,'scope':'syntax only, not typecheck/build'})
cmd=['git','apply','--check',str(HERE/'candidate.patch')]
r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
assert r.returncode==0,r.stderr.decode('utf8',errors='replace')
ast.parse(read(HERE/'prepare.py').lstrip('\ufeff'))
assert all(sha(ROOT/p)==h for p,h in pins.items())
checks={'id':'E030-source-checks','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted_source_count':162,'accepted_current_sha256_exact':True,'owned_count':5,'only_cuda_mapping_changed':True,'other_cuda_entries_byte_exact':[n for n in entries if n!='up_fold'],'up_fold_total_reduction_output_suffix_exact':True,'up_fold_barriers_unchanged':bfold.count('__syncthreads()'),'training_eval_opponent_arguments_unchanged':True,'iterate_profiled_exploitability_sweep_lock_methods_byte_exact':True,'constructor_partial_move_audit':'Only local fold-offset vectors are sorted before all struct field moves; no new plan borrows.','accounting':{'added_immutable_bytes':416,'new_mutable_workspace_bytes':0,'new_device_allocations':0,'staging_bytes':'includes416 once for admission; callers only budget/estimate/log','public_estimate':'CPU feature-safe constant416 once','continuation_planned_metadata':'adds416 once','observed_metadata':'unchanged actual slice lengths','workspace_and_host_capacity_formula':'unchanged seven buffers and eleven published components'},'test_declarations':inventory,'prospective_gpu_only_inventory':{'passed':85,'ignored':4,'total':89},'host_integer_examples':host_cases,'syntax_only':syntax,'patch_applicability':{'command':cmd,'exit_code':0},'compiler_native_gpu_execution':False,'tests_executed':False,'candidate_accepted':False}
put('source-checks.json',checks)
refs=[accepted_path,BULK/'runs/D055-next-hypothesis-scout/report.json',BULK/'runs/D055-next-hypothesis-scout/manifest.json',BULK/'runs/D055-next-hypothesis-scout/card-work-proxy.json',BULK/'comparisons/D055-independent-source-review/report.json',BULK/'comparisons/D055-independent-source-review/manifest.json',BULK/'runs/V020-unit/report.json',BULK/'runs/V020-unit/stdout.log',BULK/'runs/D036-fold-shuffle-probe-r3/protocol.json',BULK/'runs/D036-fold-shuffle-probe-r3/corpus.json']
manifest={'id':'E030-design','status':'FROZEN_OFF_TREE_UNEXECUTED','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted_base':'E020','accepted_source_sha256':pins,'owned_sources':OWNED,'accepted_owned_sha256':{p:sha(HERE/'base'/p) for p in OWNED},'candidate_owned_sha256':{p:sha(HERE/'candidate'/p) for p in OWNED},'artifact_sha256':{p.relative_to(HERE).as_posix():sha(p) for p in sorted(HERE.rglob('*')) if p.is_file()},'reference_sha256':{str(p):sha(p) for p in refs},'prospective_unit_inventory':{'passed':85,'ignored':4,'total':89},'direct_validation':{'status':'separate preparation, no execution','scope':'complete immutable E020 versus candidate up_fold only','comparison_pairs':180,'launches':360,'production_threads':128,'supplemental_threads':[16,32,64,256],'raw_total_helpers':False},'next_decision':'root-authorized independently reviewed exact/compiler feasibility only; no automatic primary approval','compiler_or_native_execution':False,'checkout_changed':False,'candidate_accepted':False}
put('manifest.json',manifest)
print(json.dumps({'manifest_sha256':sha(HERE/'manifest.json'),'source_checks_sha256':sha(HERE/'source-checks.json'),'patch_sha256':sha(HERE/'candidate.patch'),'candidate_owned_sha256':manifest['candidate_owned_sha256'],'artifacts':len(manifest['artifact_sha256'])},indent=2))
