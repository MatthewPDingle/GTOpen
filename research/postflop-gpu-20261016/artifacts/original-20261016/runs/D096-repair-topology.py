"""Correct the omitted rake branch, retain completed pair, execute no repeats."""
import ast,collections,copy,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=ROOT/'runs/D096-two-tone-profile';E=H/'cohort-execution';original=old.read(H/'cohort-plan.json');retained=['D096B1','D096T1']
for name in retained:
    x=old.read(E/(name+'.exit.json'));assert x['returncode']==0 and x['error'] is None and x['cleanup'] is None
assert old.read(ROOT/'runs/D096-manager/cohort.exit.json')['returncode']==1
assert old.read(E/'failure.json')['completed_ids']==retained
for name in original['order'][2:]:assert not (ROOT/'runs'/name).exists()
assert not (H/'cohort-report.json').exists() and not (E/'complete.json').exists()
top=old.read(H/'topology-inputs.json');pattern=top['patterns'][1]
counts={name:sum(pattern[name]) for name in ['action_spans','chance_spans','chance_node_spans','fold_spans','show_spans']}
A=counts['action_spans'];C=counts['chance_spans'];K=counts['chance_node_spans'];F=counts['fold_spans'];S=counts['show_spans']
base=old.read(ROOT/'runs/D096B1/report.json')['results'][0];rake=base['config']['tree']['rake_pct'];assert rake==0.05
source=(old.REPO/'crates/solver/src/gpu/mod.rs').read_text()
assert 'let raked = solver.spot.tree.config.rake_pct > 0.0;' in source and source.count('for mode in 0..if raked { 2 } else { 1 }')==2 and 'self.eval_up(p, mode, mode == 0)?;' in source
down=1+A+C;training=down+F+S+K+A;br=F+S+K+A;average=K+A;eval_nodes=down+2*(br+average)
expected=2*training*200+eval_nodes*10
assert (training,eval_nodes,expected)==(63,147,26670)
family={'copy_root':410,'down_action':A*410,'down_chance':C*410,'up_fold':F*420,'up_show':S*420,'up_chance':K*440,'up_action':A*400,'up_action_eval':A*40};assert sum(family.values())==expected
repair={'id':'D096-raked-topology-repair','at':old.now(),'invalid_original_inference':'Matching nonempty work-list span patterns do not imply the same evaluation graph. Original prediction omitted the positive-rake branch, which runs average-EV sweeps in addition to BR. Original frozen prediction, first failed reader/manager and every completed run/trace remain preserved.','source':str(old.REPO/'crates/solver/src/gpu/mod.rs'),'source_sha256':old.sha(old.REPO/'crates/solver/src/gpu/mod.rs'),'config_rake_pct':rake,'span_counts':counts,'source_formula':{'eval_down':down,'training_each_player':training,'BR_up_each_player':br,'additional_average_up_each_player':average,'raked_eval_graph':eval_nodes,'total_kernel_records':expected},'expected_graph_kernel_nodes_sorted':[63,63,147],'expected_kernel_records':expected,'expected_kernel_family_counts':family,'original_graph_nodes':[63,63,103],'original_kernel_records':26230,'retained_ids':retained,'remaining_native_order':original['order'][2:],'no_completed_native_repeated':True,'same_binaries_observer_settings_quality_target_and_stop':True,'same_original10pct_clock_gates':True,'no_timing_exclusion_extension_or_pooling':True,'interpretation_limit':'Filtered two-tone runs in a fresh process: first-use NVRTC/context costs belong to this selected fixture here. In the primary3fixture process it runs second and PTX is already cached. Do not infer ordinary second-fixture initialization cost, causal cross-fixture speed or additive full-cycle gains.'}
old.save(H/'topology-repair-r2.json',repair)
retained_pins={}
for name in retained:
    for p in (ROOT/'runs'/name).rglob('*'):
        if p.is_file():retained_pins[str(p)]=old.sha(p)
    for p in E.glob(name+'.*'):
        if p.is_file():retained_pins[str(p)]=old.sha(p)
for p in [E/'failure.json',*list((E/'traces/D096T1').iterdir()),ROOT/'runs/D096-manager/cohort.exit.json',ROOT/'runs/D096-manager/cohort.stderr.log']:
    if p.is_file():retained_pins[str(p)]=old.sha(p)
old.save(H/'retained-pair-r2.json',{'at':old.now(),'ids':retained,'artifact_sha256':retained_pins,'native_returncodes':[0,0],'analysis_returncode':1,'no_native_rerun':True})
text=(H/'run-cohort.py').read_text()
def replace_once(a,b):
    global text
    assert text.count(a)==1,a[:120];text=text.replace(a,b)
replace_once("H/'cohort-plan.json'","H/'cohort-plan-r2.json'")
replace_once("verify();assert not (ROOT/'gpu-run.lock').exists() and not E.exists();E.mkdir();(E/'traces').mkdir();", "verify();assert not (ROOT/'gpu-run.lock').exists() and E.exists() and (E/'traces').exists();")
replace_once(" for identity in P['order']:\n", " for identity in P['order']:\n  retained=identity in P['retained_ids']\n")
replace_once("directory.mkdir();env['PATH']", "directory.mkdir(exist_ok=retained);env['PATH']")
line=next(x for x in text.splitlines() if x.startswith("  old.save(E/(identity+'.environment.json'),"));prefix="  old.save(E/(identity+'.environment.json'),";dictionary=line[len(prefix):-1]
replace_once(line,"  environment="+dictionary+"\n  if retained:\n   saved=old.read(E/(identity+'.environment.json'));assert {k:v for k,v in saved.items() if k!='at'}=={k:v for k,v in environment.items() if k!='at'}\n  else:old.save(E/(identity+'.environment.json'),environment)")
line=next(x for x in text.splitlines() if x.startswith('  cmd=') and ';started=time.monotonic();' in x)
cmd,rest=line.split(';started=time.monotonic();',1)
replace_once(line,cmd+"\n  if retained:\n   receipt=old.read(E/(identity+'.exit.json'));assert receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None and receipt['command']==cmd and old.read(E/(identity+'.invocation.json'))['command']==cmd\n   wrapper_ms[identity]=old.read(E/(identity+'.outer-wall.json'))['elapsed_ms']\n  else:\n   started=time.monotonic();"+rest+"\n  verify()")
replace_once("   assert counts==family_counts", "   assert counts==family_counts and counts==P['expected_kernel_family_counts']")
replace_once("E/'failure.json'", "E/'failure-r2.json'")
replace_once("print('D096 completed',identity,flush=True)","print('D096 retained replay' if retained else 'D096 completed',identity,flush=True)")
ast.parse(text);(H/'run-cohort-r2.py').write_text(text,encoding='utf-8',newline='\n')
root=(H/'root-and-publish-r2.py').read_text().replace("H/'cohort-plan.json'","H/'cohort-plan-r2.json'")
needle=" ck(identity+' all graph-node repeats',sorted(next(iter(g.values())) for g in groups.values())==[9,199,199] and all(len(set(g.values()))==1 for g in groups.values()))"
assert root.count(needle)==1
root=root.replace(needle,needle+"\n ck(identity+' source-derived graph kernel counts',sorted(len(g) for g in groups.values())==P['expected_graph_kernel_nodes_sorted'])")
root=root.replace("counts==q['traces'][identity]['kernel_family_counts'])", "counts==q['traces'][identity]['kernel_family_counts']==P['expected_kernel_family_counts'])")
root=root.replace('26230kernels','26670kernels').replace('Time outside phase brackets is excluded.','Time outside phase brackets is excluded. Filtered two-tone is first in a fresh process here; ordinary primary second-fixture initialization history differs.')
ast.parse(root);(H/'root-and-publish-r3.py').write_text(root,encoding='utf-8',newline='\n')
wrapper=(H/'run-and-root.py').read_text().replace("H/'cohort-plan.json'","H/'cohort-plan-r2.json'").replace("ROOT/'runs/D096-manager'","ROOT/'runs/D096-manager-r2'").replace("H/'run-cohort.py'","H/'run-cohort-r2.py'").replace("H/'root-and-publish-r2.py'","H/'root-and-publish-r3.py'")
ast.parse(wrapper);(H/'run-and-root-r2.py').write_text(wrapper,encoding='utf-8',newline='\n')
P=copy.deepcopy(original);P.update(id='D096-two-tone-cohort-r2',at=old.now(),status='ANALYSIS_REPAIR_BEFORE_REMAINING_FOUR_NATIVE_RUNS',retained_ids=retained,remaining_native_order=original['order'][2:],expected_graph_kernel_nodes_sorted=[63,63,147],expected_kernel_records=26670,expected_kernel_family_counts=family,analysis_repair_sha256=old.sha(H/'topology-repair-r2.json'),original_cohort_protocol_sha256=old.sha(H/'cohort-plan.json'))
P['trace_quality_rule']=P['trace_quality_rule'].replace('63/63/103','63/63/147').replace('26230','26670')
P['scope']+=' Filtered fixture is first in each fresh process; primary second-fixture NVRTC/context history differs. No second-fixture initialization apportionment or direct rainbow cohort comparison.'
P['input_sha256'].update(retained_pins)
P['input_sha256'].update({str(p):old.sha(p) for p in [H/'cohort-plan.json',H/'topology-repair-r2.json',H/'retained-pair-r2.json',H/'run-cohort-r2.py',H/'root-and-publish-r3.py',H/'run-and-root-r2.py',Path(__file__),old.REPO/'crates/solver/src/gpu/mod.rs']})
old.save(H/'cohort-plan-r2.json',P)
published={}
for p in [H/'topology-repair-r2.json',H/'retained-pair-r2.json',H/'run-cohort-r2.py',H/'root-and-publish-r3.py',H/'run-and-root-r2.py',H/'cohort-plan-r2.json',E/'failure.json',ROOT/'runs/D096-manager/cohort.exit.json']:
    prefix=H.name if p.parent==H else 'D096-original-analysis-failure';key='evidence/'+prefix+'/'+p.name;dest=old.ar.DASHBOARD/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
    published[key]=old.sha(p)
old.save(H/'pre-remaining-publication-r2.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'retained_native_runs':retained,'remaining_native_runs':original['order'][2:],'no_completed_run_repeated':True,'observer_clock_gates_unchanged':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='D096');e.update(stage='Corrected rake topology; retain first pair, run remaining four',reason='First pair exact with zero collector errors. Initial topology inference omitted positive-rake average-EV sweeps: source predicts147evaluation kernels and26,670total records. Preserve failed prediction/reader and native pair; correct analysis only. Same binaries/settings/six-run order/10%clocks, no repeats/exclusions/extensions.');e['evidence'].extend([{'label':'Preserved topology error and source-derived repair','url':'evidence/'+H.name+'/topology-repair-r2.json'},{'label':'Retained pair hashes; no repeat','url':'evidence/'+H.name+'/retained-pair-r2.json'},{'label':'Fixed cohort with analysis-only repair','url':'evidence/'+H.name+'/cohort-plan-r2.json'}]);s.update(updated_at=old.now(),stage='D096 remaining four matched runs',activity='Retain D096B1/T1 exactly; run only original remaining T2/B2/B3/T3. Corrected rake-aware topology, unchanged quality and observer gates.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'cohort-plan-r2.json'),'retained':retained,'remaining':original['order'][2:],'expected_kernel_records':expected,'expected_graph_nodes':[63,63,147],'published':len(published)}),flush=True)
