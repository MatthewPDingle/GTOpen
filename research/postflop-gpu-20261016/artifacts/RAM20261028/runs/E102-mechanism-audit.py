import json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E102-resource';P=h.read(H/'protocol.json');q=h.read(H/'report.json')
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
assert q['status']=='stage1_pass_parent_load_loop_review_required' and all(q['gates'].values())
for p,digest in P['input_sha256'].items():h.pin(p,digest)
assert h.read(H/'execution/complete.json')['all_owned_compiler_native_children_terminal']
for name in ['rustc','probe']:
    receipt=h.read(H/'execution'/(name+'.exit.json'))
    assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None

def inspect(source):
    rows=source.splitlines();origins={};values={};loads=[];stores=[];labels={};branches=[]
    for i,raw in enumerate(rows,1):
        line=raw.split('//',1)[0].strip()
        label=re.fullmatch(r'(\$L__BB\d+_\d+):',line)
        if label:labels[label[1]]=i;continue
        branch=re.fullmatch(r'(?:@!?%p\d+\s+)?bra(?:\.uni)?\s+(\$L__BB\d+_\d+);',line)
        if branch:branches.append({'line':i,'target':branch[1],'instruction':line});continue
        param=re.fullmatch(r'ld\.param\.u64\s+(%rd\d+),\s*\[down_chance_parent_param_(\d+)\];',line)
        if param:origins[param[1]]={int(param[2])};continue
        load=re.fullmatch(r'ld\.global(?:\.[a-z]+)*\.(u64|u32|f32)\s+(%\w+),\s*\[(%rd\d+)(?:\+\d+)?\];',line)
        if load:
            tag=origins.get(load[3],set()).copy();origins.pop(load[2],None);values.pop(load[2],None)
            if load[1]=='f32':
                assert len(tag)==1 and next(iter(tag)) in [12,13],(i,line,tag)
                role=next(iter(tag));values[load[2]]={role};loads.append({'line':i,'instruction':line,'role_param':role,'value_register':load[2]})
            continue
        select=re.fullmatch(r'selp\.f32\s+(%f\d+),\s*0f00000000,\s*(%f\d+),\s*%p\d+;',line)
        if select:
            assert select[2] in values
            values[select[1]]=values[select[2]]|{'positivezero'};continue
        store=re.fullmatch(r'st\.global\.f32\s+\[(%rd\d+)\],\s*(%f\d+);',line)
        if store:
            address=origins.get(store[1],set());data=values.get(store[2],set())
            assert len(address)==1 and next(iter(address)) in [12,13] and data==address|{'positivezero'},(i,line,address,data)
            stores.append({'line':i,'instruction':line,'role_param':next(iter(address)),'value_register':store[2],'value_is_original_parent_or_positivezero':True});continue
        op=re.fullmatch(r'(?:@!?%p\d+\s+)?(?:add|sub|mul|mad|shl|shr|mov|cvt|cvta)(?:\.[A-Za-z0-9_]+)*\s+(%\w+),\s*(.*);',line)
        if op:
            origins[op[1]]=set().union(*(origins.get(x,set()) for x in re.findall(r'%\w+',op[2])))
    assert not re.search(r'\bbrx\b',source)
    backedges=[]
    for branch in branches:
        assert branch['target'] in labels
        if labels[branch['target']]<branch['line']:
            backedges.append({**branch,'start_line':labels[branch['target']]})
    assert len(loads)==2 and {x['role_param'] for x in loads}=={12,13}
    assert len(stores)>0 and all(len([x for x in loads if x['role_param']==p])==1 for p in [12,13])
    proof=[]
    for load in loads:
        owned=[s for s in stores if s['role_param']==load['role_param']]
        assert owned
        enclosing=[b for b in backedges if b['start_line']<=load['line']<b['line'] and all(b['start_line']<=s['line']<b['line'] for s in owned)]
        assert len(enclosing)==1
        inner=[b for b in backedges if any(b['start_line']<=s['line']<b['line'] for s in owned) and not (b['start_line']<=load['line']<b['line'])]
        assert inner and all(load['line']<b['start_line'] for b in inner)
        proof.append({'parent_load':load,'all_copy_store_sites':owned,'outer_hand_backedge':enclosing[0],'card_backedges':inner,
            'one_parent_f32_load_per_logical_hand_in_source_loop':True,'no_parent_f32_load_inside_card_backedge':True,'all_original_or_zero_stores_within_same_hand_loop':True})
    return {'parent_loads':loads,'stores':stores,'all_backward_branch_ranges':backedges,'per_player_hoisting_and_copy_proof':proof}

# Test origin and value checks against the actual parser's supported statements.
fixture='''ld.param.u64 %rd1, [down_chance_parent_param_12];
cvta.to.global.u64 %rd2, %rd1;
$L__BB0_1:
ld.global.f32 %f1, [%rd2];
$L__BB0_2:
selp.f32 %f2, 0f00000000, %f1, %p1;
st.global.f32 [%rd2], %f2;
@%p2 bra $L__BB0_2;
@%p3 bra $L__BB0_1;
ld.param.u64 %rd3, [down_chance_parent_param_13];
cvta.to.global.u64 %rd4, %rd3;
$L__BB0_3:
ld.global.f32 %f3, [%rd4];
$L__BB0_4:
selp.f32 %f4, 0f00000000, %f3, %p4;
st.global.f32 [%rd4], %f4;
@%p5 bra $L__BB0_4;
@%p6 bra $L__BB0_3;'''
assert len(inspect(fixture)['per_player_hoisting_and_copy_proof'])==2
for broken in [fixture.replace('0f00000000, %f1','0f00000000, %f99'),fixture.replace('st.global.f32 [%rd2], %f2','st.global.f32 [%rd4], %f2'),fixture.replace('ld.global.f32 %f1, [%rd2];\n$L__BB0_2:','$L__BB0_2:\nld.global.f32 %f1, [%rd2];')]:
    try:inspect(broken)
    except AssertionError:pass
    else:raise AssertionError('Negative reader fixture unexpectedly passed')
path=Path(q['new_entry_bodies']['compute_120']['path']);h.pin(path,q['new_entry_bodies']['compute_120']['sha256'])
proof=inspect(path.read_text(encoding='utf-8'))
R=ROOT/'comparisons/E102-parent-load-mechanism';R.mkdir(exist_ok=False)
h.save(R/'report.json',{'id':'E102-parent-load-mechanism','at':h.now(),'status':'pass_actual_NVRTC_parent_load_hoisting_and_copy_prerequisites',
    'resource_report_sha256':h.sha(H/'report.json'),'full_actual_entry_sha256':h.sha(path),'proof':proof,
    'reader_positive_and_negative_fixtures':4,'new_compilers_NVRTC_module_queries_application_kernels_or_solver_runs':0,
    'source_activated':False,'candidate_accepted':False,
    'limits':'Static actual compute120 PTX address/value origin and backward-branch ranges, with source and D194 disjoint ownership. Not final SASS, dynamic load count, occupancy, universal arithmetic, GPU raw-state or speed proof. Compatibility75 retained original9/ABI/copy-only/resource compiler checks; no other-GPU qualification.',
    'next_required':'Full original edge controls plus fixed parent/group/orbit/nonfinite/tail/countzero/reuse cases, complete engine/canonical physical state, ordinary builds/tests and unchanged complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application qualification.'})
N=ROOT/'runs/E102-prerequisite-checkpoint';N.mkdir(exist_ok=False)
h.save(N/'report.json',{'id':'E102-prerequisite-checkpoint','at':h.now(),'status':'compiled_prerequisites_pass_raw_controls_pending',
    'resource_sha256':h.sha(H/'report.json'),'mechanism_sha256':h.sha(R/'report.json'),'D194_integer_census_sha256':h.sha(ROOT/'comparisons/D194-parent-chance-census/report.json'),
    'all_owned_compiler_native_readers_terminal':True,'application_kernels':0,'solver_runs':0,'speed_samples':0,
    'actual_new_registers':40,'actual_original_registers':30,'new_local_bytes':0,'default128thread_theoretical_residency_old_new':[12,12],
    'warning':'Registers increase30->40; same default occupancy/local/shared/maxthread feasibility is not material neutrality or a gain.',
    'accepted_source_main_live_protected_PTX_unchanged':True,'new_gain_accepted_or_deployed':False,'best_qualified':'E080 / GPU / compressed /16 workers','last_primary_baseline':'B313','raw_and_complete_qualification_remaining':True})
published=[]
for folder,names in [(R,['report.json']),(N,['report.json'])]:
    for filename in names:
        p=folder/filename;dst=h.ar.DASHBOARD/'evidence'/folder.name/filename;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+filename,timeout=20) as response:assert response.read()==p.read_bytes()
        published.append({'label':folder.name+' result','url':'evidence/'+folder.name+'/'+filename})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='E102')
    item.update(stage='Compiled prerequisites passed; raw GPU controls next',correctness='pending_GPU_raw_controls',reason='Original9 entries/ABIs preserved. New entry has no float arithmetic, and both parent reach loads stay outside the card loops. Registers rise30 to40 with the same theoretical default residency and no local/shared growth. Numerical state, full solves and material costs remain unqualified.')
    item['evidence'].extend(published)
    status.update(updated_at=h.now(),stage=item['stage'],activity='E102 passed the frozen metadata and compiler prerequisites. Full GPU raw equivalence is next; no speed or accuracy gain is claimed. E080 with 16 workers remains live.')
    h.ar.atomic_json(h.ar.STATUS,status)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:assert response.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('''

### E102 actual compiled copy/parent-load prerequisites pass

Frozen42b4f295abf004e35371dc18a4f96076056a68bf9e8e094b279fbbc61fdddc70 completed1Rustcompiler/1module-only resource process/4NVRTC12.9compiles actual120+compat75; bothchildren terminal0, no appkernels/solves. Original9alpha-normalized entries/ABIs remainexact onbotharches. New16parameterentry haszero barriers/floating arithmetic. Old down_chance resource rows exact; newparententry registers30->40/local0/shared0, maxthread/defaultstack/feasibility unchanged and64/128/256theoretical occupancy24/12/6same. Register warning disclosed; no material-neutrality or speed inference.

Separate read-only static actual120 entry audit passes: address-origin tracing identifies exactlyone parentf32load per player (params12/13), every output is the same player's loaded parent bits orpositivezero, and all store sites are inside that handloop. Both parentloads precede representative-card backwardbranch ranges and are outside those loops; no float operation orhiddenparentreload. Retained source/D194ownership supports reusing the parent value. Positive and3negative reader fixtures cover unknownvalue, cross-role store and misplacedload rejection. Entireentryhash/loads/stores/backedges retained. This is PTX static mechanism evidence, not finalSASS/dynamicload/occupancy/GPUexactness/speed proof.

Compiler/resource/mechanism checkpoint and current status published/HTTP-byteverified. Fulloriginal edge corpus and fixed newparent/group/orbit/nonfinite/tail/zero/reuse controls, wholeengine/canonical physical state, ordinary builds/tests and all unchanged complete1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gates remain before adoption. No actualGPUapplicationkernel, newquality/speed result orlivechange. All ownedcompilers/native/readers terminal; acceptedsource/main/live/protectedPTX exact, locksabsent. E080/GPU/compressed/16live unchanged, lastprimaryB313; allnewartifactsX/archive readonly/noT. Goalactive, E102pending rawcontrols.
''')
h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: verify parent chance load hoisting before raw GPU controls'],cwd=h.REPO,check=True)
print(json.dumps({'E102':'compiled prerequisites pass','parent_f32_load_sites':len(proof['parent_loads']),'copy_store_sites':len(proof['stores']),'application_kernels':0,'raw_controls':'pending','new_gain_adopted':False}),flush=True)
