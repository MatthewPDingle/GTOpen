from pathlib import Path
import json,hashlib,datetime,difflib,ast
HERE=Path(__file__).resolve().parent
BULK=HERE.parent.parent
OLD=HERE.parent/'E029-primary-plan'
DESIGN=HERE.parent/'E030-design'
SCRIPTS=['compile_check.py','build.py','primary.py','assess.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def put(name,s):
 with (HERE/name).open('x',encoding='utf8',newline='\n') as f:f.write(s)
def jput(name,x):put(name,json.dumps(x,indent=2)+'\n')
def rename(s):
 for a,b in [('E029','E030'),('e029','e030'),('B095','B098'),('B096','B099'),('B097','B100')]:s=s.replace(a,b)
 return s
assert not (HERE/'scripts-manifest.json').exists()
design=load(DESIGN/'manifest.json')
assert sha(DESIGN/'manifest.json')=='0ad81cd54e33062d2cfc53dfebd3f0db60d3675b9d10458799e4f95aeb3f6681'
old_protocol=load(OLD/'protocol.json')
p=json.loads(rename(json.dumps(old_protocol)))
p.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),production_scope='Fixed descending52-card fold-task order with ascending cardID ties; append52 IDs after each unchanged53-offset prefix. All original per-card FP order, total reduction, barriers,128threads, ABI and shared allocations unchanged;416bytes immutable growth.',unit_screen='GPU-only ordinary library85passed,0failed,4ignored,0measured,0filtered; one new host permutation unit and existing geometry/accounting assertions.',candidate_source_authorization='Root pins exact five candidate sources, independent source/script reviews and independent terminal180-pair direct exact PASS before any activation. Separate root decision required after direct feasibility; no automatic primary authorization.',expected_unit_passed=85,design_sha256=sha(DESIGN/'README.md'),source_archive_sha256=sha(DESIGN/'manifest.json'),candidate_owned_sha256=design['candidate_owned_sha256'])
p['prerequisites']=['formal immutable E020 acceptance record','terminal successful E020 server qualification evidence','independent E030 source review','independent E030 primary script review','independent terminal exact E030-direct180pairs360launches PASS','separate root activation and execution authorization after direct feasibility']
p['conditional_fold_checks']=p.pop('conditional_complement_checks')
p['conditional_fold_checks']='Before adoption, exact immutable-old/candidate complete states for F32/compressed, training/evaluation, locks/warm/standalone and continuation paths; actual two105-word fold offset allocations, planned/observed immutable metadata and tight-budget admission. Seven mutable buffers and11workspace components unchanged.'
p['wide_turn_holdout_if_pass']['admission']='Unchanged2GiB constructor budget,4GiB device free/30GiB total,16GiB host available,50GiB S reserve plus outputs; hands1128/1128,river max1081/1081,48river cards,node bound11691. Candidate admission accounts for exactly416bytes added immutable task IDs. No duplicate planning pass, budget relaxation or rescue.'
p['wide_turn_holdout_if_pass']['resource']='All physical launch shapes and dynamic shared allocations remain E020-identical, including128-thread up_fold. Full-range card lengths tie, giving no structural proxy reduction. No speed claim or arbitrary register/occupancy gate; normal admission and native fixed holdout guard apply.'
p['direct_prerequisite']={'path':str(BULK/'comparisons/E030-direct-independent-review/validation.json'),'prepared_manifest_path':str(BULK/'runs/E030-fold-card-order-exact/prepared-manifest.json'),'prepared_manifest_sha256_binding':'Root authorization.evidence_sha256 pins canonical prepared manifest; terminal report must match that hash.','id':'E030-direct','verdict':'PASS_EXACT_COMPLETE_UP_FOLD_COMPARISON','comparison_pairs':180,'kernel_launches':360,'production_threads':128,'block_shapes':[128,16,32,64,256],'each_pair_same_block_shape':True,'performance_measurement':False,'candidate_accepted':False}
p['cuda_provenance']='Fresh GPU-only binaries embed complete E030 CUDA and omit full E020 CUDA. Exactly5changed accepted-map entries;157unowned entries/evaluator unchanged. Feature library no-run uses a separate fresh target.'
jput('protocol.json',p)
protocol_hash=sha(HERE/'protocol.json')
old_kernel=old_protocol['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu'];new_kernel=design['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu']
old_prepared=old_protocol['direct_prerequisite']['prepared_manifest_sha256']
new_prepared_guard="""_prepared_path=Path(r'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E030-fold-card-order-exact\\prepared-manifest.json')
assert _direct['prepared_manifest_sha256']==authorization['evidence_sha256'][str(_prepared_path)]
assert __import__('hashlib').sha256(_prepared_path.read_bytes()).hexdigest()==_direct['prepared_manifest_sha256']"""
patch=''
for name in SCRIPTS:
 original=(OLD/name).read_text(encoding='utf8');s=rename(original)
 s=s.replace(sha(OLD/'protocol.json'),protocol_hash).replace(old_kernel,new_kernel)
 s=s.replace('direct_up_show','direct_up_fold').replace('PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON','PASS_EXACT_COMPLETE_UP_FOLD_COMPARISON')
 line="assert _direct['prepared_manifest_sha256']=='"+old_prepared+"'"
 assert s.count(line)==1;s=s.replace(line,new_prepared_guard)
 line="assert (_direct['baseline_physical_threads'],_direct['candidate_physical_threads'],_direct['logical_scan_threads'])==(128,128,128)"
 assert s.count(line)==1;s=s.replace(line,"assert _direct['production_threads']==128 and _direct['block_shapes']==[128,16,32,64,256]\nassert _direct['each_pair_same_block_shape'] is True")
 s=s.replace("_direct['comparison_pairs']==152 and _direct['kernel_launches']==304","_direct['comparison_pairs']==180 and _direct['kernel_launches']==360")
 s=s.replace('All five reviewed complement-zeroing source files must change','All five reviewed fold-card-order source files must change')
 s=s.replace('E030 complement-only showdown zeroing candidate','E030 fixed fold-card task-order candidate')
 s=s.replace('Building the five-file complement-zeroing candidate','Building the five-file fold-card task-order candidate')
 s=s.replace('E030 showdown complement-only zeroing candidate','E030 fixed fold-card task-order candidate')
 s=s.replace('Complement-only initial showdown zero stores with immutable missing-index metadata and matching admission/capacity accounting.','Fixed descending card-list-length task order with416byte immutable ID tails and matching admission/capacity accounting.')
 assert 'logical_scan_threads' not in s and 'complement' not in s and 'up_show' not in s
 ast.parse(s);put(name,s)
 patch+=''.join(difflib.unified_diff(original.splitlines(keepends=True),s.splitlines(keepends=True),fromfile='E029-primary-plan/'+name,tofile='E030-primary-plan/'+name))
put('script-adaptation.patch',patch)
put('wide-turn-fixture.json',(OLD/'wide-turn-fixture.json').read_text(encoding='utf8'))
a=json.loads(rename((OLD/'authorization.example.json').read_text(encoding='utf8')).replace('direct_up_show','direct_up_fold').replace('E030-show-complement-exact','E030-fold-card-order-exact'))
a['direct_up_fold_exact_pass']=False
for role in ['E030_source_review','E030_script_review']:
 a['prerequisites'][role]['sha256']='ROOT_FILL_'+role.upper()+'_SHA256'
a['candidate_sources']={rel:{'path':str(DESIGN/'candidate'/rel),'sha256':h} for rel,h in design['candidate_owned_sha256'].items()}
a['evidence_sha256']={str(HERE/'scripts-manifest.json'):'ROOT_FILL_FROZEN_SCRIPT_SEAL',str(HERE/'protocol.json'):protocol_hash,str(DESIGN/'manifest.json'):sha(DESIGN/'manifest.json'),str(BULK/'runs/E030-fold-card-order-exact/prepared-manifest.json'):'ROOT_FILL_DIRECT_PREPARED_MANIFEST_SHA256'}
for pin in a['prerequisites'].values():a['evidence_sha256'][pin['path']]=pin['sha256']
a['scope']='Example only. Root creates immutable authorization after source/script review and terminal exact/compiler direct feasibility, then separately decides to activate/build. False fields/placeholders never authorize execution. Five sources, no auxiliaries.'
jput('authorization.example.json',a)
commands=json.loads(rename((OLD/'commands.json').read_text(encoding='utf8')))
commands['prerequisite']='Independent source/script reviews and terminal180pair/360launch complete-up_fold direct exact/compiler PASS; root then separately decides activation/execution. This prospective plan alone grants no approval.'
jput('commands.json',commands)
put('README.md','''# E030 prospective fixed primary plan

Unexecuted reuse of E029's fixed build/primary/assessment scripts. The single candidate is the frozen E020-based fold-card task permutation; no rescue/alternative orders. Source and exact-kernel feasibility reviews do not automatically authorize primary activation. Root must make that decision and fill a separate immutable authorization.

Root sequence is in commands.json: feature-gated library compile-only in a fresh separate target, fresh GPU-only library/evaluator build,85-pass/4-ignored unit screen, then B098/E030R1,E030R2/B099,B100/E030R3, followed by assessment. Frozen evaluator, complete-cycle boundaries,18 complete results/138 convergence records,2%aggregate gate and repeated3%fixture guard remain unchanged. All failures and runs stay preserved; no extensions.

Each script requires canonical comparisons/E030-direct-independent-review/validation.json with actual complete-up_fold exact PASS,180pairs/360launches, production128 and same paired shape among[128,16,32,64,256]. No fictional logical-scan field. The root authorization pins canonical runs/E030-fold-card-order-exact/prepared-manifest.json; its hash must match the terminal review. Independent source/script reviews, accepted E020/server evidence and exact five candidate sources are also pinned.

The build keeps accepted162-source identity except exactly five owned files, fresh Cargo artifacts and target containment, full candidate CUDA embedded/full accepted CUDA absent, compiler-override refusal, live-idle/GPU lock, disk reserve, bounded owned process lifetime and pre/post source checks. No shared target or force-clean workaround.

A qualifying primary is not acceptance. Independent audit, original state/menu/resume controls, F32/GPU/continuation metadata/admission checks, unchanged wide-turn full-range holdout against E020 and fresh-original cumulative qualification remain required. No conditional machinery is implemented here.
''')
print(json.dumps({'protocol_sha256':protocol_hash,'draft_scripts':SCRIPTS,'prepared_direct_pin':'Root supplies canonical hash after separately reviewed preparation, before execution'},indent=2))
