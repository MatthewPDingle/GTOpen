"""Freeze full actual-crate CPU replay before compilers or native cases."""
import array, ast, importlib.util, re, shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody(); h.ar.refuse_active(h.ar.live_status())
assert not (ROOT/'gpu-run.lock').exists() and not (ROOT/'epoch-sequence.lock').exists()
S=ROOT/'runs/E115-source-v2'; M=h.read(S/'manifest.json')
assert all(h.read(ROOT/'runs/D269-host-layout/report.json')['gates'].values())
P0=ROOT/'runs/D267b-node-order-model/protocol.json'; Q0=ROOT/'runs/D267b-node-order-model/model-report.json'
old=h.read(P0); model=h.read(Q0)
H=ROOT/'runs/D270-actual-metadata-CPU'; H.mkdir(exist_ok=False)
(H/'inputs').mkdir(); (H/'sources').mkdir()
spec=importlib.util.spec_from_file_location('d267io',ROOT/'runs/D267b-model-io.py')
io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
thin={}
for row in model['cases']:
    if not row['id'].endswith('-iso-on'): continue
    for key in ['projection','maps']:
        h.pin(row[key]['path'],row[key]['sha256'])
    maps=io.read_projection(row['maps']['path']); data=io.read_projection(row['projection']['path'])
    forward=maps['old_to_new']; inverse=maps['new_to_old']
    locks=array.array('Q',(data['d_lock_off'][forward[i]] for i in range(row['nodes'])))
    children=array.array('I',(v if v==0xffffffff else inverse[v] for v in data['tree.children']))
    files={}
    for name,values in [('locks',locks),('children',children)]:
        path=H/'inputs'/(row['fixture']+'.'+name+'.bin')
        with path.open('xb') as f: f.write(values.tobytes())
        files[name+'_path']=str(path)
        files[name+'_sha256']=h.sha(path)
        files[name+'_bytes']=path.stat().st_size
    thin[row['fixture']]=files
cases=[]
for item in old['raw_inputs']:
    f=dict(item['fixture']); f.update(thin[f['fixture']]); f['original_plan_path']=item['path']; f['original_plan_sha256']=item['sha256']
    row=next(x for x in model['cases'] if x['id']==f['id'])
    f['reference_projection']=row['projection']; f['reference_maps']=row['maps']
    cases.append(f)
h.save(H/'fixtures.json',cases)
probe=ROOT/'runs/D183-plan-phase-diagnostic/visibility-adapter/probe.rs'
text=probe.read_text(encoding='utf-8')
encoder=text[text.index('trait Encode '):text.index('fn dump_observed(')]
encoder='\n'.join(line for line in encoder.splitlines() if not line.startswith('impl Encode for observed::LevelSpan'))+'\n'
encoder=encoder.replace('solver::gpu::plan::','super::plan::')
assert encoder.count('field(&mut w,')==53 and encoder.count('fn dump_baseline(')==1
template=ROOT/'runs/D270-cpu-replay.template.rs'; observer=ROOT/'runs/D270-arena-observer.rs'
adapter=template.read_text(encoding='utf-8')
for before,after in [('@ENCODER@',encoder),('@FIXTURES@',str(H/'fixtures.json')),('@OUTPUT@',str(H/'output'))]:
    assert adapter.count(before)==1; adapter=adapter.replace(before,after)
owned={}
for name,v in M['owned'].items():
    h.pin(v['candidate'],v['candidate_sha256'])
    if v['base']: h.pin(h.REPO/name,v['base_sha256'])
    else: assert not (h.REPO/name).exists()
    data=Path(v['candidate']).read_bytes()
    extra=adapter.encode() if name.endswith('/mod.rs') else observer.read_bytes() if name.endswith('/arena.rs') else b''
    dest=H/'sources'/Path(name).name
    with dest.open('xb') as f:f.write(data+extra)
    assert dest.read_bytes()[:len(data)]==data
    owned[name]={'source':str(dest),'source_sha256':h.sha(dest),'candidate_prefix_sha256':v['candidate_sha256'],'candidate_prefix_bytes':len(data),'observer_append_bytes':len(extra),'original':v['base'],'original_sha256':v['base_sha256']}
paths=[Path(__file__),template,observer,probe,P0,Q0,ROOT/'runs/D267b-model-io.py',S/'manifest.json',S/'source-review.json',ROOT/'runs/D269-host-layout/report.json',ROOT/'epoch/common.py',ROOT/'runs/D270-root-replay.py',ROOT/'runs/D270-execute-cpu-replay.py',H/'fixtures.json',Path(old['schema_path'])]
for p in paths:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
paths+=list((H/'inputs').iterdir())
protocol={'id':'D270','at':h.now(),'status':'FROZEN_PRE_FULL_ACTUAL_CRATE_CPU_REPLAY','input_sha256':{str(p):h.sha(p) for p in paths},'owned':owned,'accepted_source_sha256':h.custody(),'fixtures':cases,'schema_path':old['schema_path'],'target':str(ROOT/'build-d270-actual-metadata-cpu'),'required_free_bytes':66*1024**3,'required_available_RAM_bytes':64*1024**3,'raw_output_reservation_bytes':8*1024**3,
 'arms':['actual','exceptional','selected'],'cases':18,
 'actual':'Real full crate GpuPlan::build and compressed CPU Solver/ArenaLayout::new from all six original configs, iso on/off. Dump all53 fields before/after, all23 GPU-bound metadata arrays plus full maps, full arena records/copies/initial/zeros/capacities. Actual metadata::eligible/prepare/children_image and real action-record lookups. Same source prefixes as D269; only appended observers. One fresh feature library compile and one exact CPU test process. No GpuSolver constructor/CUDA API/context/kernel/CFR iteration/GPU solve/timing sample.',
 'actual_arm':'Captured whole lock offsets and complete tree.children inverted from hash-bound D267 model (whose full GPU source inputs were already read/verified there); no re-reading large GPU images or trusting shapes alone. Native freshly built Spot children and all53 original plan fields must byte-match original inputs.',
 'exceptional_arm':'Same original plan/layout, seed all node_twin/tlose/ttie/cdiv scalar rows with bits [0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc00123,0x7f800123,0xffc00456,0xff800456] at index(i+3*field)%12; synthetic lock bits16*i wheni%3==0 elseu64MAX. Direct actual prepare and children function on all six plans, including ordinary river fallback plans. Whole-word test only, not a new poker/quality or performance fixture.',
 'selected_arm':'Emulate only actual CPU capability predicate and original/ordered metadata branch using real original arena layouts and original canonical staging length, no constructor called. Captured locks. False predicates retain every original53 field and identity node IDs. Actual constructor/fallback/pinned/CUDA/locks/projection callers still require GPU controls.',
 'boundaries':'On actual arm each original case: N multiplication overflow, children multiplication overflow, wrong first dead reach_src length, scratch one f32 below required, 4-byte misaligned scratch when length sufficient, each individual original full arena in mixed pair and both full. Restore every input before full original plan dump. Real full layouts from original use_full_action_arenas. Use aligned ordinary CPU u64-backed scratch at original arena max length, not actual pinned allocation. Whole unchanged scratch tail/front/back canaries and real record lookup for every node/player.',
 'reader':'Read all53 original and after fields and every23 projected array word/maps, exact known scalar seeding, all physical slot/offset values, complete children, all arena contents/capacities/records except required mapped device_node. All18 before files match original whole hashes. All16 ordered maps match existing independent D267 full maps;2 selected river identities. Whole output hashes/extents retained. 3 meaningful negative reader fixtures per ordered case plus identity rejection on2 fallbacks. Same-agent parser review not external/formal proof.',
 'gates':'Every original case/field/record/bit/canary/capacity test mandatory. Any genuine compiler/resource/projection/bit/shape failure closes exact E115 form; no helper/field/selection/scope/flags/source/sample rescue. Reader/observer failures preserved separately and completed native cases never repeated. Passing only advances actual GPU numerical/all-call-path tests; all original full quality/1%/strict fixture/fresh16/broad/material/holdout/cumulative/application gates remain.',
 'remaining':'Actual selected/fallback constructors, pinned alignment/capacity/upload fence/ownership and all locks/manual nonaction/symmetry/paged/stored callers; original36case engine/fullcanonical CPU/all66device/physical CFV/lifecycle equivalence. Fresh ordinary builds/units and full unchanged complete-solve/material/holdout/cumulative/app qualification. CPU allocations and all observer clocks are unscored; no material/no-tradeoff/speed claim.'}
h.save(H/'protocol.json',protocol)
dest=h.ar.DASHBOARD/'evidence'/H.name/'protocol.json';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(H/'protocol.json',dest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/protocol.json',timeout=20) as z:assert z.read()==(H/'protocol.json').read_bytes()
print(h.sha(H/'protocol.json'),flush=True)
