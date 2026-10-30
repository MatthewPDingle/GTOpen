from pathlib import Path
import ast,json,hashlib,datetime
HERE=Path(__file__).resolve().parent
BULK=HERE.parent.parent
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
OLD=HERE.parent/'E029-primary-plan'
DESIGN=HERE.parent/'E030-design'
SCRIPTS=['compile_check.py','build.py','primary.py','assess.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def put(name,x):
 with (HERE/name).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
assert not (HERE/'scripts-manifest.json').exists()
plan=load(HERE/'protocol.json');design=load(DESIGN/'manifest.json')
assert plan['order']==['V030-unit','B098','E030R1','E030R2','B099','B100','E030R3']
assert plan['candidate_owned_sha256']==design['candidate_owned_sha256'] and plan['accepted_owned_sha256']==design['accepted_owned_sha256']
assert plan['source_archive_sha256']==sha(DESIGN/'manifest.json')
assert plan['design_sha256']==sha(DESIGN/'README.md')
assert plan['expected_unit_passed']==85 and plan['expected_unit_ignored']==4
for name,h in design['artifact_sha256'].items():assert sha(DESIGN/name)==h,name
assert all(sha(ROOT/p)==h for p,h in design['accepted_source_sha256'].items())
status_path=Path(r'X:\Dev\GTOpen\web\research\postflop-gpu-20261016\status.json');status=load(status_path)
for identity in plan['order']:
 assert not (BULK/'runs'/identity).exists(),identity
 assert not any(row['id']==identity for row in status['experiments']),identity
for p in [Path(plan['build_target_root']),Path(plan['compile_check_target_root']),Path(plan['compile_check_output']),BULK/'runs/E030-build',BULK/'runs/E030-primary-execution',BULK/'runs/E030-assessment']:
 assert not p.exists(),str(p)
for name in ['E030-solver','E030-postflop_autoresearch']:
 for ext in ['exe','manifest.json']:assert not (BULK/'binaries'/f'{name}.{ext}').exists()
parsed=[]
for p in HERE.rglob('*.py'):
 if 'draft-r1' in p.parts:continue
 ast.parse(p.read_text(encoding='utf-8-sig'));parsed.append(p.relative_to(HERE).as_posix())
for name in SCRIPTS:
 s=(HERE/name).read_text(encoding='utf8')
 assert sha(HERE/'protocol.json') in s
 assert all(x not in s for x in ['V029','B095','B096','B097','logical_scan_threads','direct_up_show','E029','complement'])
 assert "_direct['each_pair_same_block_shape'] is True" in s
 assert "_direct['comparison_pairs']==180 and _direct['kernel_launches']==360" in s
 assert "_direct['production_threads']==128 and _direct['block_shapes']==[128,16,32,64,256]" in s
 assert plan['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu'] in s
assert "env.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)" in (HERE/'primary.py').read_text(encoding='utf8')
assert "expected_convergence_records_per_run']==23" in (HERE/'assess.py').read_text(encoding='utf8')
assert plan['wide_turn_holdout_if_pass']['fixture_sha256']==sha(HERE/'wide-turn-fixture.json')
oldseal=load(OLD/'scripts-manifest.json')
refs={p:h for p,h in oldseal['reference_sha256'].items() if '/E029' not in p.replace('\\','/') and '/E028' not in p.replace('\\','/') and '/E027' not in p.replace('\\','/')}
for p in [OLD/'scripts-manifest.json',OLD/'protocol.json',*[OLD/n for n in SCRIPTS],DESIGN/'manifest.json',DESIGN/'README.md',BULK/'comparisons/E030-source-review/report.json',BULK/'comparisons/E030-source-review/manifest.json']:
 refs[str(p)]=sha(p)
for p,h in refs.items():assert sha(Path(p))==h,p
prep={'id':'E030-primary-preparation','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted_source_count':162,'current_accepted_source_map_exact':True,'owned_sources':sorted(design['owned_sources']),'auxiliary_sources':[],'source_manifest_sha256':sha(DESIGN/'manifest.json'),'ast_parse_only':parsed,'unused_run_ids':plan['order'],'unused_fresh_targets':[plan['build_target_root'],plan['compile_check_target_root']],'fixed_gates_and_evaluator_unchanged':True,'expected_unit_inventory':{'passed':85,'ignored':4,'total':89},'direct_gate':plan['direct_prerequisite'],'direct_prepared_and_terminal_pins':'Future canonical artifacts must be included in immutable root execution authorization; no fabricated hash or execution permission in this plan.','pre_seal_corrections':['Inherited V029-unit identifier fixed to authorized V030-unit before seal; original complete draft preserved under draft-r1.','Host preparation script encoding alias typo corrected from utf8-sig to utf-8-sig; no native/compiler execution or evidence loss.'],'compiler_native_gpu_execution':False,'production_edits':False,'status_edits':False,'candidate_accepted':False}
put('preparation.json',prep)
support={p.relative_to(HERE).as_posix():sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name not in SCRIPTS+['protocol.json']}
# Preserve draft script bytes too; exclusion above is by root path only.
support.update({p.relative_to(HERE).as_posix():sha(p) for p in sorted((HERE/'draft-r1').rglob('*')) if p.is_file()})
seal={'candidate':'E030','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_PROSPECTIVE_NOT_EXECUTED','script_sha256':{n:sha(HERE/n) for n in ['protocol.json']+SCRIPTS},'supporting_sha256':support,'reference_sha256':refs,'independent_review':'Pending independent primary-script review. Direct terminal exact/compiler audit and separate root activation/execution decision are additionally mandatory. This seal is not authorization.','builds':0,'native_tests':0,'gpu_executions':0,'production_edits':0,'dashboard_edits':0}
put('scripts-manifest.json',seal)
print(json.dumps({'scripts_manifest_sha256':sha(HERE/'scripts-manifest.json'),'protocol_sha256':sha(HERE/'protocol.json'),'script_sha256':seal['script_sha256'],'supporting':len(support),'references':len(refs)},indent=2))
