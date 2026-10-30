"""Prepare one original-schedule CFV interval-sharing prototype and CPU controls."""
from pathlib import Path
import ast, difflib, json, shutil, sys, urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
D=R/'runs/D122-cfv-lifetimes';d=old.read(D/'report.json')
assert d['status']=='pass_retained_lifetime_model_admit_one_Rust_prototype' and len(d['cases'])==12
S=R/'runs/E076-source';H=R/'runs/E076-plan-control';assert not S.exists() and not H.exists();S.mkdir();H.mkdir()
name='crates/solver/src/gpu/plan.rs';original=(old.REPO/name).read_text(encoding='utf-8');old.pin(old.REPO/name,old.BASE[name])
begin=original.index('        // Terminal CFVs stay resident')
end=original.index('        // --- Level-ordered work lists',begin)
replacement='''        // Cache terminals permanently. A scratch CFV lives from its producing
        // up-sweep level through the immediately preceding consuming level.
        // A one-action parent can overwrite its own action child's row at the
        // same hand index: up_action finishes all child reads before its final
        // store. Restrict sharing to disjoint pairs (child arity >= 2); chance
        // gathers and all other input/output dependencies remain disjoint.
        let (mut cfv_slot, mut cfv_blocks) = {
            let levels = max_level as usize + 1;
            let mut alias_parent = vec![false; n];
            let mut alias_child = vec![false; n];
            for (ni, node) in spot.tree.nodes.iter().enumerate() {
                if reached[ni] && node.kind == KIND_ACTION && node.num_children == 1 {
                    let child = spot.tree.children[node.children_start as usize] as usize;
                    let next = &spot.tree.nodes[child];
                    if reached[child] && next.kind == KIND_ACTION && next.num_children >= 2 {
                        alias_parent[ni] = true;
                        alias_child[child] = true;
                    }
                }
            }
            // Node-id order within a level makes both coloring and uploads
            // deterministic. A shared child's closed lifetime extends across
            // its parent to level(child)-2. Every other interval is [l-1,l].
            let mut groups = vec![Vec::<u32>::new(); levels];
            for (ni, node) in spot.tree.nodes.iter().enumerate() {
                if reached[ni] && (node.kind == KIND_ACTION || node.kind == KIND_CHANCE)
                    && !alias_parent[ni]
                {
                    groups[level[ni] as usize].push(ni as u32);
                }
            }
            let mut retired = vec![Vec::<u32>::new(); levels + 4];
            let mut free = Vec::<u32>::new();
            let mut slots = vec![u32::MAX; n];
            let mut blocks = 0usize;
            for l in (0..levels).rev() {
                // Endpoints are closed: a row consumed in stage l cannot be
                // assigned to another producer during the same stage.
                free.append(&mut retired[l + 3]);
                for &node in &groups[l] {
                    let ni = node as usize;
                    let slot = free.pop().unwrap_or_else(|| {
                        let slot = blocks as u32;
                        blocks += 1;
                        slot
                    });
                    slots[ni] = slot;
                    let retire = l + 1 - usize::from(alias_child[ni]);
                    retired[retire].push(slot);
                }
            }
            for (ni, node) in spot.tree.nodes.iter().enumerate() {
                if alias_parent[ni] {
                    let child = spot.tree.children[node.children_start as usize] as usize;
                    slots[ni] = slots[child];
                }
            }
            // Root readback uses physical row zero. Swapping colors preserves
            // every lifetime and avoids reserving an otherwise unused row.
            if spot.tree.nodes[0].kind == KIND_ACTION || spot.tree.nodes[0].kind == KIND_CHANCE {
                let root = slots[0];
                for (ni, node) in spot.tree.nodes.iter().enumerate() {
                    if reached[ni] && (node.kind == KIND_ACTION || node.kind == KIND_CHANCE) {
                        if slots[ni] == 0 { slots[ni] = root; }
                        else if slots[ni] == root { slots[ni] = 0; }
                    }
                }
            }
            (slots, blocks)
        };
        for (ni, node) in spot.tree.nodes.iter().enumerate() {
            if reached[ni] && node.kind != KIND_ACTION && node.kind != KIND_CHANCE {
                cfv_slot[ni] = cfv_blocks as u32;
                cfv_blocks += 1;
            }
        }

'''
candidate=original[:begin]+replacement+original[end:]
candidate=candidate.replace('/// CFV slots: persistent terminals plus alternating-level action/chance scratch.','/// CFV slots: persistent terminals plus lifetime-colored action/chance scratch.')
oldtest='''                        assert!(live[l].is_disjoint(&live[l - 1]), "a parent cannot overwrite child input storage");'''
newtest='''                        for &slot in live[l].intersection(&live[l - 1]) {
                            let find = |depth: usize| {
                                [(&plan.action_nodes, &plan.action_spans),
                                 (&plan.chance_nodes, &plan.chance_node_spans)]
                                    .into_iter().flat_map(|(nodes, spans)| {
                                        let span = spans[depth];
                                        nodes[span.start as usize..(span.start + span.count) as usize].iter()
                                    }).copied().find(|&node| plan.cfv_slot[node as usize] as usize == slot).unwrap()
                            };
                            let parent = find(l - 1) as usize;
                            let child = find(l) as usize;
                            let p = &spot.tree.nodes[parent];
                            let c = &spot.tree.nodes[child];
                            assert_eq!(p.kind, KIND_ACTION, "chance output cannot alias any child");
                            assert_eq!(p.num_children, 1, "only one-action parents may share inputs");
                            assert_eq!(spot.tree.children[p.children_start as usize] as usize, child,
                                "shared row must belong to this parent's sole child");
                            assert_eq!(c.kind, KIND_ACTION);
                            assert!(c.num_children >= 2, "shared pairs cannot form a chain");
                            assert!(!plan.cc_child.contains(&(child as u32)), "orbit gathers cannot share a row");
                        }'''
assert candidate.count(oldtest)==1;candidate=candidate.replace(oldtest,newtest)
assert candidate[:candidate.index('        // Cache terminals')].replace('lifetime-colored','alternating-level')==original[:begin]
for filename,text in [('baseline-plan.rs',original),('candidate-plan.rs',candidate)]:
 (S/filename).write_text(text,encoding='utf-8',newline='\n')
old.pin(S/'baseline-plan.rs',old.BASE[name])
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),candidate.splitlines(True),fromfile=name,tofile=name)),encoding='utf-8',newline='\n')
old.save(S/'manifest.json',{'id':'E076','at':old.now(),'accepted_source_sha256':old.BASE,'candidate_owned_sha256':{name:old.sha(S/'candidate-plan.rs')},'owned':{name:{'base':str(S/'baseline-plan.rs'),'candidate':str(S/'candidate-plan.rs')}},'source_scope':'One Rust CFV slot allocator plus its lifetime invariant test/documentation. No new persistent field, CUDA source, float operation, worklist, kernel/graph schedule, reach/terminal arithmetic, ABI, save or solve-quality change. Temporary CPU flags, buckets and color scans are included in complete-cycle and material qualification.','D122_report_sha256':old.sha(D/'report.json'),'candidate_accepted':False})
A=R/'runs/D092-action-arity-order'
for a,b in [('baseline-plan.rs','accepted-plan.rs'),('candidate-plan.rs','candidate-plan.rs')]:shutil.copyfile(S/a,H/b)
for n in ['game.rs','fixture-0.json','fixture-1.json','fixture-2.json','field-schema.json']:shutil.copyfile(A/n,H/n)
old.pin(H/'game.rs',old.BASE['crates/solver/src/game.rs'])
probe=(A/'probe.rs').read_text(encoding='utf-8').replace('D092','E076')
probe=probe.replace('use std::{fs::{File,OpenOptions},io::{BufWriter,Write},time::Instant};','use std::{fs::{File,OpenOptions},io::{BufWriter,Write}};')
a=probe.index('let mut a:Option<accepted::GpuPlan>');b=probe.index('let mut f=BufWriter',a)
probe=probe[:a]+'''let(mut a,mut b) = if id%2==0 {(Some(accepted::GpuPlan::build(&spot,iso)),Some(candidate::GpuPlan::build(&spot,iso)))}else{let b=candidate::GpuPlan::build(&spot,iso);(Some(accepted::GpuPlan::build(&spot,iso)),Some(b))};
if full {a.as_mut().unwrap().use_full_action_arenas(&spot);b.as_mut().unwrap().use_full_action_arenas(&spot);}
let a=a.unwrap();let b=b.unwrap();'''+probe[b:]
probe=probe.replace('b"E076-PLAN-RAW1\\0\\0"','b"E076-PLAN-RAW1\\0\\0"')
for field in [5,36,37]:
 line=next(l for l in probe.splitlines()if l.startswith(f'count+=field(&mut f,{field},'))
 probe=probe.replace(line,line.rsplit(',',1)[0]+(','+'true);' if field in [36,37] else ',false);'))
probe=probe.replace(',"baseline_plan_ms":ams,"candidate_plan_ms":bms','')
probe=probe.replace('all_nonpermuted_fields_bitwise_equal','all_non_CFV_fields_bitwise_equal')
assert 'Instant'not in probe and 'ams'not in probe and 'bms'not in probe
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
decoder=r'''"""Independent full raw field comparison against frozen metadata and D122 maps."""
from pathlib import Path
import array,struct
def vector(f):
 n,=struct.unpack('<Q',f.read(8));assert n<100000000
 v=array.array('Q');v.fromfile(f,n);assert len(v)==n;return v
def replay(path,case,reference,expected):
 checks=0;words=0;changed=0
 with Path(expected).open('rb')as e:
  assert e.read(16)==b'D122-CFV-MAP1\0\0\0';cid,n,os,ns,ob,nb=struct.unpack('<IQQQQQ',e.read(44));assert cid==case
  slots=array.array('I');slots.fromfile(e,n);assert e.read(1)==b''
 with Path(path).open('rb')as f,Path(reference).open('rb')as r:
  assert f.read(16)==b'E076-PLAN-RAW1\0\0';assert r.read(16)==b'D092-PLAN-RAW1\0\0'
  assert f.read(8)==r.read(8)==struct.pack('<II',case,53)
  sizes=f.read(16);assert sizes==r.read(16)and sizes[:8]==sizes[8:];checks+=4
  for field in range(53):
   assert f.read(4)==r.read(4)==struct.pack('<I',field)
   ac,bc,av,bv=[vector(f)for _ in range(4)];rc1,rc2,rv1,rv2=[vector(r)for _ in range(4)]
   assert ac==bc==rc1==rc2;assert av==rv1;checks+=3;words+=len(av)
   if field==36:
    assert bv[0]==n and len(bv)==n+1 and list(bv[1:])==list(slots);checks+=2
    changed=sum(x!=y for x,y in zip(av,bv))
   elif field==37:assert av==array.array('Q',[ob]) and bv==array.array('Q',[nb]);checks+=2
   else:assert av==bv;checks+=1
  for _ in range(2):assert vector(f)==vector(r);checks+=1
  assert f.read(1)==r.read(1)==b'';checks+=1
 return {'case':case,'fields':53,'unchanged_fields':51,'baseline_words':words,'nodes':n,'changed_slot_words':changed,'old_CFV_blocks':ob,'new_CFV_blocks':nb,'original_scratch_rows':os,'new_scratch_rows':ns,'checks':checks,'all_non_CFV_values_and_all_capacities_exact':True,'map_matches_frozen_lifetime_model':True,'baseline_matches_retained_accepted_metadata':True,'raw_bytes':Path(path).stat().st_size}
'''
ast.parse(decoder);(H/'replay.py').write_text(decoder,encoding='utf-8',newline='\n')
execute=r'''"""One compiler per fixed probe/test and twelve CPU-only complete metadata controls."""
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
 old.child([str(B/'tests.exe'),'--test-threads=1'],'execution'if False else E,'unit',old.env(),300)
 verify();assert 'test result: ok.'in (E/'unit.stdout.log').read_text(encoding='utf-8')
 results=[];binary=old.sha(B/'probe.exe')
 for case in range(12):
  verify();old.ar.refuse_active(old.ar.live_status());old.pin(B/'probe.exe',binary)
  label=f'case-{case:02d}';raw=E/(label+'.bin')
  old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),180)
  verify();model=P['models'][case]
  r=replay(raw,case,model['reference'],model['map']);r['raw_sha256']=old.sha(raw)
  old.save(E/(label+'.replay.json'),r);results.append(r)
  print(json.dumps(r),flush=True)
 assert len(results)==12
 old.save(H/'report.json',{'id':'E076-plan-control','at':old.now(),'status':'pass_compiled_CFV_layout_against_retained_model','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'all_51_other_fields_values_capacities_structs_exact':True,'all_12_baseline_fields_match_retained':True,'all_12_CFV_maps_match_frozen_D122':True,'original_and_candidate_plan_unit_tests_pass':True,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'performance_measurement':False,'candidate_accepted':False,'limits':'Full CPU metadata and compiled plan invariant controls only. No GPU numeric/alias/NaN proof, actual CPU temporary peak/capacity/responsiveness or complete-solve speed claim. Root decoder is not an external independent auditor.'});verify()
print('E076 CPU metadata and invariant controls terminal; no GPU/speed result.',flush=True)
'''
execute=execute.replace("'execution'if False else E","E")
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
P0=old.read(A/'protocol.json');command=[x.replace(str(A),str(H)).replace('d092_probe','e076_plan_probe')for x in P0['command']]
testcmd=command.copy();testcmd[testcmd.index('-o')+1]=str(H/'build/tests.exe');testcmd.insert(1,'--test')
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
for p,h in deps.items():old.pin(p,h)
models=[{'case':c['case'],'reference':str(A/'execution'/f"case-{c['case']:02d}.bin"),'map':str(D/f"case-{c['case']:02d}-cfv-map.bin")}for c in d['cases']]
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],*[p for p in S.iterdir()if p.is_file()],D/'protocol.json',D/'report.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[Path(v)for m in models for k,v in m.items()if k!='case']]
P={'id':'E076-plan-control','at':old.now(),'status':'FROZEN_PRE_COMPILER_NATIVE','compile_commands':{'rustc':command,'rustc-tests':testcmd},'input_sha256':deps|{str(p):old.sha(p)for p in paths},'models':models,'fixed_protocol':'One probe compiler, one test compiler, one CPU-only original/candidate plan unit process, exactly12 CPU metadata processes. Full53fields/raw capacities/structs and original baseline match retained D092; only36/37 differ and must exactly match separately frozen D122 maps. No repeats/source/layout/placement variants after an actual mismatch. No CUDA kernels, solve/speed samples, or source activation.','candidate_accepted':False}
old.save(H/'protocol.json',P)
pub=[]
for folder in [S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
  pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified_artifacts':pub,'compiler_or_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='E076'for x in s['experiments'])
 s['experiments'].append({'id':'E076','at':old.now(),'title':'Share CFV rows across disjoint single-action parent/child lifetimes','kind':'experiment','status':'running','correctness':'Frozen CPU metadata and lifetime controls','fixture':'12 retained accepted plan cases','stage':'Compile original-schedule layout prototype','reason':'One Rust allocator change; float kernels and level schedule unchanged. D122 exact graph model predicts smaller flop CFV payload. CPU temporary costs and GPU alias safety still need testing.','accepted':False,'evidence':[{'label':'Frozen source manifest','url':'evidence/E076-source/manifest.json'},{'label':'Frozen compiled plan control','url':'evidence/E076-plan-control/protocol.json'}]})
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E076',stage='E076 compiled CFV lifetime layout controls',activity='D122 passed all12 retained layouts. Compile one original-schedule CFV row-sharing Rust prototype, verify every metadata field and independent frozen map. No GPU or speed claim; accepted/live E051 gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'source_sha256':old.sha(S/'candidate-plan.rs'),'native_executions':0}),flush=True)
