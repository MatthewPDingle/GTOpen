import hashlib, json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E101-resource';S=ROOT/'runs/E101-source'
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
P=h.read(H/'protocol.json');r=h.read(H/'report.json')
assert r['status']=='stage1_pass_separate_full_entry_bypass_review_required'
assert r['mechanism_proven'] is False and all(r['gates'].values())
for p,digest in P['input_sha256'].items():h.pin(p,digest)
for label in ['rustc','probe']:
    e=h.read(H/'execution'/(label+'.exit.json'))
    assert e['returncode']==0 and e['error'] is e['cleanup'] is None
assert h.read(H/'execution/complete.json')['all_owned_children_terminal']

def patterns(source):
    rows=source.splitlines();out=[]
    for i in range(len(rows)-2):
        a,b,c=(x.strip() for x in rows[i:i+3])
        cmp=re.fullmatch(r'setp\.gt\.f32\s+(%p\d+),\s*(%f\d+),\s*0f00000000;',a)
        div=re.fullmatch(r'div\.rn\.f32\s+(%f\d+),\s*(%f\d+),\s*(%f\d+);',b)
        sel=re.fullmatch(r'selp\.f32\s+(%f\d+),\s*(%f\d+),\s*0f00000000,\s*(%p\d+);',c)
        if cmp and div and sel and cmp[2]==div[2] and cmp[1]==sel[3] and div[1]==sel[2]:
            origin=[]
            for j in range(max(0,i-50),i):
                if re.search(r'\bld\.global(?:\.[\w]+)*\.f32\s+'+re.escape(cmp[2])+r',',rows[j]):
                    origin.append({'line':j+1,'instruction':rows[j].strip()})
            out.append({'compare_line_1based':i+1,'division_line_1based':i+2,'select_line_1based':i+3,
                'instructions':[a,b,c],'numerator_register':cmp[2],'denominator_register':div[3],
                'predicate_register':cmp[1],'quotient_register':div[1],
                'division_is_unpredicated':True,'no_intervening_branch_or_label':True,
                'nearby_actual_global_numerator_loads':origin,
                'symbolic_zero_numerator_witness':{'numerator_bits':'00000000','positive_sum_bits':'3f800000','predicate':False,'div_instruction_reached_before_result_selection':True,'selected_result_bits':'00000000','is_GPU_execution':False}})
    return out

# Reader fixtures check register/operand/control syntax rather than accepting counts.
valid='setp.gt.f32 %p1, %f1, 0f00000000;\ndiv.rn.f32 %f2, %f1, %f3;\nselp.f32 %f4, %f2, 0f00000000, %p1;'
assert len(patterns(valid))==1
assert patterns(valid.replace('div.rn.f32','@%p1 div.rn.f32'))==[]
assert patterns(valid.replace('div.rn.f32','@!%p1 bra SKIP;\ndiv.rn.f32'))==[]
assert patterns(valid.replace('selp.f32 %f4, %f2','selp.f32 %f4, %f9'))==[]
assert patterns(valid.replace('%p1;', '%p8;'))==[]
proof={};checks=5
for arch in ['compute_120','compute_75']:
    proof[arch]={}
    for name in P['targets']:
        path=H/'execution'/f'candidate-{arch}-{name}.ptx'
        source=path.read_text(encoding='utf-8')
        assert hashlib.sha256(source.encode()).hexdigest()==r['quotient_sites'][arch][name]['candidate']['full_entry_sha256']
        found=patterns(source)
        if arch=='compute_120':
            assert found and found[0]['nearby_actual_global_numerator_loads'],name
        proof[arch][name]={'entry_sha256':h.sha(path),'unpredicated_quotient_then_select_patterns':len(found),
            'every_matching_site':found,'baseline_native_division_sites':len(r['quotient_sites'][arch][name]['baseline']['native_division_sites']),
            'candidate_native_division_sites':len(r['quotient_sites'][arch][name]['candidate']['native_division_sites'])}
        checks+=1+len(found)*3
R=ROOT/'comparisons/E101-bypass-control-review';R.mkdir(exist_ok=False)
h.save(R/'report.json',{
    'id':'E101-bypass-control-review','at':h.now(),'status':'rejected_required_NVRTC_bypass_not_emitted',
    'resource_stage1_sha256':h.sha(H/'report.json'),'protocol_sha256':h.sha(H/'protocol.json'),
    'checks':checks,'candidate_entry_counterexamples':proof,
    'decision':'All three actual target entries contain reachable positive-sum/zero-numerator cases where an unpredicated div.rn.f32 executes between setp.gt and selp. The predicate selects the result only; it does not bypass quotient work at this NVRTC PTX stage. The required full-entry compiler bypass prerequisite is therefore not established. Close exact form without numerical or speed trials.',
    'limits':'Read-only static NVRTC PTX analysis and symbolic local zero/one witness, not a dynamic execution, final driver SASS proof, complete entry equivalence or speed prediction. Later driver transformations were not collected. Unchanged static division counts alone were not used as the rejection proof.',
    'additional_NVRTC_compilers_module_queries_appkernels_solvers_or_timing_samples':0,
    'candidate_accepted':False,'source_activated':False,
    'closure':'No conditional syntax, predicate, denominator, placement, helper, arity, entry-subset, flags, source or sample rescue. Original candidate/protocol/resource pass and all PTX retained unchanged.'
})
N=ROOT/'runs/E101-terminal-checkpoint';N.mkdir(exist_ok=False)
h.save(N/'report.json',{
    'id':'E101-close','at':h.now(),'status':'rejected_closed_required_compiler_bypass_absent',
    'resource_stage1_pass':True,'bypass_prerequisite_pass':False,
    'resource_report_sha256':h.sha(H/'report.json'),'bypass_report_sha256':h.sha(R/'report.json'),
    'all_owned_compiler_native_processes_terminal':True,'read_only_review_complete':True,
    'Rust_compilers':1,'module_query_processes':1,'NVRTC_compilations':4,
    'additional_compilers_module_queries_or_NVRTC_compiles':0,
    'application_kernels':0,'GPU_numerical_control_cases':0,'solver_runs':0,'performance_samples':0,
    'resource_warning':'up_action registers62->64; same local64 and 16/8/4 theoretical occupancy. Other two target resource rows unchanged. Stage1 ABI/barrier/other6entry/default-feasibility gates passed; no material or speed inference.',
    'accepted_source_main_live_protected_PTX_unchanged':True,
    'new_gain_accepted_or_deployed':False,'last_primary_baseline':'B313',
    'best_qualified':'E080 / GPU / compressed / 16 workers',
    'conditional_syntax_predicate_denominator_placement_helper_arity_entrysubset_flags_source_or_sample_rescue_allowed':False,
    'native_code_or_universal_speed_effect_claimed':False,
})
evidence=[]
for folder,names in [(R,['report.json']),(N,['report.json']),(S,['baseline.cu','candidate.cu']),(H,['probe.rs'])]:
    for filename in names:
        p=folder/filename;dst=h.ar.DASHBOARD/'evidence'/folder.name/filename
        dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+filename,timeout=20) as response:assert response.read()==p.read_bytes()
        if filename=='report.json':evidence.append({'label':folder.name+' result','url':'evidence/'+folder.name+'/'+filename})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='E101')
    item.update(status='rejected',accepted=False,stage='Closed: required compiler bypass not emitted',correctness='not_run',reason='Compiler feasibility passed, but all three changed entries still execute quotient instructions before selecting the zero result in NVRTC PTX. The required bypass was not emitted at this stage. No GPU numerical test or solve-speed sample was run. Exact source closed without syntax or scope variants.')
    item['evidence'].extend(evidence)
    status.update(updated_at=h.now(),active_experiment='E101',stage='Zero-numerator form closed; GPU source research continues',activity='E101 failed its required compiler-bypass check before numerical or timing trials. All retained resources and control-flow evidence are published. E080 with 16 workers remains live; no new gain adopted.')
    h.ar.atomic_json(h.ar.STATUS,status)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:assert response.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('''

### E101 compiler stage1 passes; required quotient bypass rejected

Frozen c7bddda839da4b78bf2f3db2602354a9717502e6c66ffcafb51659d3bcea9cac completed one Rust compiler, one module/resource-only process and four NVRTC12.9 actual120/compat75 compiles; both owned children terminal0. No application kernels/solves. All stage1 gates pass: unchanged18/20/17 ABIs, barriers, six other alpha-normalized entries onbotharches, allthree target bodies changed, unchanged payload/shapes/default stack/maxthreads and positive64/128/256occupancies. down_action40/local32 and eval40/local0 unchanged; up_action62->64/local64 with same16/8/4 theoretical occupancy, warning disclosed underD108. No no-tradeoff/numeric/speed claim.

Mandatory separate full-entry bypass review fails. Allthree actual120 candidate entries contain an adjacent setp.gt.f32 predicate on the raw numerator, UNPREDICATED div.rn.f32 of that numerator, then selp.f32 selecting quotient or +0. The predicate controls only result selection. Source-valid numerator+0 with other positive action mass (sum1) reaches the division even when predicatefalse; parent reach multiplication is still retained. The same patterns and fullentry hashes are recorded forcompat75. Static division-site counts remain18/16/7 on120 and25/23/7 on75; counts alone are not the proof. Reader positive and negative fixtures reject predicated division, intervening branch, wrong quotient and wrong predicate. Entire matches and nearby actual global numerator loads retained.

This is an NVRTC PTX control-flow prerequisite rejection, not a final driver SASS/dynamic cost/precision or universal performance conclusion. No additional module capture, NVRTC, appkernel, direct numerical, whole canonical, ordinary speed or broader/adoption trial follows. Exact conditional syntax/predicate/denominator/placement/helper/arity/entrysubset/flags/source/sample form CLOSED without rescue. Original resource stage1 pass is preserved unchanged beside failed mechanism report and terminal custody; source/protocol/allPTX/review evidence retained physicallyX and published HTTP-byteexact. All owned compiler/native/readers terminal, locks absent, accepted source/main/live/protectedPTX unchanged. E080/GPU/compressed/16 remains live, lastprimaryB313, no new gain, goal active.
''')
h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
subprocess.run(['git','commit','-m','research: close zero numerator compiler bypass screen'],cwd=h.REPO,check=True)
print(json.dumps({'E101':'rejected closed compiler bypass prerequisite','actual_counterexample_counts':{n:x['unpredicated_quotient_then_select_patterns'] for n,x in proof['compute_120'].items()},'review_checks':checks,'solver_runs':0,'new_gain_adopted':False}),flush=True)
