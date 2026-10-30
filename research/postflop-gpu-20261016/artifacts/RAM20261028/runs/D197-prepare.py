import ast,json,shutil,sys,urllib.request,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
engine=ROOT/'comparisons/D196-parent-chance-engine/report.json';E=h.read(engine)
assert E['cases']==36 and E['phase_pairs']==752 and h.read(ROOT/'runs/D196-parent-chance-engine/execution/complete.json')['all_owned_children_terminal']
assert h.read(ROOT/'comparisons/D195-parent-chance-controls/report.json')['cases']==8345
parent=ROOT/'runs/D178-canonical-cache-control';H=ROOT/'runs/D197-parent-chance-canonical';H.mkdir(exist_ok=False)
S=ROOT/'runs/E102-source';resource=ROOT/'runs/E102-resource';R=h.read(resource/'report.json')
production=(S/'baseline-mod.rs').read_text();start=production.index('        static PTX:');end=production.index('            .clone()?;',start)+len('            .clone()?;');compile_block=production[start:end]
prior=(parent/'baseline/mod.rs').read_text();shim=prior[prior.index('pub mod plan {'):prior.index('\nmod arena;')];proof={}
for arm in ['baseline','candidate']:
 d=H/arm;d.mkdir();p=resource/'execution'/(arm+'-compute_120.ptx');h.pin(p,R['ptx_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
 shutil.copyfile(parent/arm/'arena.rs',d/'arena.rs');h.pin(d/'arena.rs',h.sha(h.REPO/'crates/solver/src/gpu/arena.rs'));shutil.copyfile(S/(arm+'-kernels.cu'),d/'kernels.cu')
 prod=(S/(arm+'-mod.rs')).read_text();binding='        assert_eq!(arch,"compute_120");\n        println!("D197_BIND '+arm+'");\n        let ptx=cudarc::nvrtc::Ptx::from_src(include_str!("../'+arm+'.ptx"));'
 source=prod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1).replace(compile_block,binding,1)
 oldprod=production;oldbinding='        assert_eq!(arch,"compute_120");\n        println!("D178_BIND baseline");\n        let ptx=cudarc::nvrtc::Ptx::from_src(include_str!("../baseline.ptx"));'
 oldprefix=oldprod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1).replace(compile_block,oldbinding,1)
 assert prior.startswith(oldprefix);suffix=prior[len(oldprefix):]
 assert source.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1).replace(binding,compile_block,1)==prod
 candidate=arm=='candidate';anchor='        let nh = plan.nh;';expr='true' if candidate else 'false';marker='\n        println!("D197_PARENT_BIND {}",serde_json::json!({"arm":"'+arm+'","hands":nh,"candidate":'+expr+',"down_name":"'+('down_chance_parent' if candidate else 'down_chance')+'","parents":plan.chance_node_spans.iter().map(|s|s.count as usize).sum::<usize>(),"edges":plan.chance_spans.iter().map(|s|s.count as usize).sum::<usize>()}));'
 assert source.count(anchor)==1;marked=source.replace(anchor,anchor+marker,1);assert marked.replace(anchor+marker,anchor,1)==source
 (d/'mod.rs').write_text(marked+suffix,encoding='utf-8',newline='\n')
 proof[arm]={'exact_host_projection_after_only_existing_publicplan_PTX_and_marker_adapters':True,'raw_host_source_sha256':h.sha(S/(arm+'-mod.rs')),'adapted_module_sha256':h.sha(d/'mod.rs')}
 code=(parent/(arm+'-probe.rs')).read_text().replace('D178','D197');(H/(arm+'-probe.rs')).write_text(code,encoding='utf-8',newline='\n')
for name in ['bench_spot.json','bounded_child.py','sampler.py']:shutil.copyfile(parent/name,H/name)
audit=(parent/'audit.py').read_text().replace('D178-canonical-cache-control','D197-parent-chance-canonical').replace('D178_BIND','D197_BIND').replace("'id':'D178'","'id':'D197'")
anchor="    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}";assert audit.count(anchor)==1
audit=audit.replace(anchor,'''    binds=[json.loads(x.split('D197_PARENT_BIND ',1)[1]) for x in text.splitlines() if x.startswith('D197_PARENT_BIND ')]
    req(len(binds)==6,'all initial/resumed constructor markers')
    for x in binds:
        req(x['arm']==arm and x['candidate']==(arm=='candidate') and x['down_name']==('down_chance_parent' if arm=='candidate' else 'down_chance'),'actual literal arm entry binding')
    req(sum(x['parents']>0 for x in binds)==4 and sum(x['parents']==0 for x in binds)==2,'original flop and river chance geometry')
'''+anchor,1)
ast.parse(audit);(H/'audit.py').write_text(audit,encoding='utf-8',newline='\n')
execute=(parent/'execute.py').read_text().replace('D178-canonical-cache-control','D197-parent-chance-canonical').replace('D178','D197').replace('CFV cache-hint','Parent chance fanout').replace('CFV cache hint','Parent chance fanout')
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
review=h.read(parent/'source-review.json');review.update(id='D197',at=h.now(),source='Exact accepted E080/E102 GPU hosts with only original public-plan adapter, sealed PTX binding and literal constructor markers. Original full canonical benchmark/lifecycle observer unchanged. All66device fields/full physical CFV/CPU query/save/futureEV contracts retained, no omissions or exceptions.',source_reversal_proof=proof,failure='Any genuine canonical/scientific/raw state mismatch closes E102 parent-fanout without source/grouping/width/guard/caller/helper/field/flags/samples rescue. Every speed/material/capacity/adoption gate remains.',candidate_accepted=False)
h.save(H/'source-review.json',review)
deps=ROOT/'reference/accepted-e080-deps';commands={}
for arm in ['baseline','candidate']:
 cmd=['rustc',str(H/(arm+'-probe.rs')),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
 for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
 commands[arm]=cmd+['-o',str(H/(arm+'.exe'))]
oldP=h.read(parent/'protocol.json')
files=[Path(__file__),parent/'protocol.json',parent/'source-review.json',parent/'audit.py',parent/'execute.py',S/'manifest.json',S/'source-review.json',resource/'protocol.json',resource/'report.json',engine,ROOT/'runs/D196-parent-chance-engine/protocol.json',ROOT/'runs/D196-parent-chance-engine/execution/complete.json',ROOT/'comparisons/D195-parent-chance-controls/report.json',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json',h.REPO/'crates/solver/tests/postflop_autoresearch.rs']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{**{k:v for k,v in oldP.items() if k not in ['id','at','input_sha256','rustc_commands','status']},'id':'D197','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_CANONICAL_RAW_NATIVE','rustc_commands':commands,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Original3canonical fixtures at unchanged quality/stops/cadence/cap.2fresh probes/2fixedbaseline-then-candidateGPUprocesses/1fullrawreader. AllCPU+66actualdevicebuffers/fullphysicalCFV/query/save/futureEV exact,no padding/field/type exception. ActualE080/E102hosts withsame sealed resourcePTX;honestprebuiltPTX clock excluded.256GiBrawreserve+64headroom/32GiBprocesscap/64before32duringavailableRAM unchanged. No newNVRTC/performance/sourceactivation/adoption. Any genuinefailure closes E102 exactform withoutrescue.'})
for folder,names in [(engine.parent,['report.json']),(ROOT/'runs/D196-parent-chance-engine/execution',['complete.json']),(H,['protocol.json','source-review.json'])]:
 for name in names:
  p=folder/name;key=folder.relative_to(ROOT).as_posix()+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D196');item.update(status='measured',correctness='pass_engine_raw_lifecycle',stage='All36cases/752phases exact',reason='66constructor arrays to CPU oracle,all65nonCFV arrays andCPU/query/save/resume exact; CFV poison/logical regeneration,graph/locks and32changing-root sweeps passed.');item['evidence'].append({'label':'Full engine raw report','url':'evidence/comparisons/D196-parent-chance-engine/report.json'})
 s['experiments'].append({'id':'D197','title':'Parent chance full canonical raw state','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','correctness':'pending_full_canonical_raw','stage':'Frozen original full canonical raw state/lifecycle','reason':'Original same-quality3fixtures andallphysicalCFV/device/CPU/query/save/futureEV; strict RAM/disk guards. No speed claim.','evidence':[{'label':n,'url':'evidence/runs/D197-parent-chance-canonical/'+n} for n in ['protocol.json','source-review.json']]});s.update(updated_at=h.now(),active_experiment='D197',stage='Parent chance full canonical state prerequisite',activity='8345direct pairs and36engine cases exact. Next original fullsize200/200/60iteration fixtures andcontinued/locked/resumed raw state. E080/GPU/compressed/16 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n### D196 engine controls pass; D197 full canonical prerequisite\n\nE102 original36engine cases pass752raw/poison phases,324EVpairs,32changing-root sweeps. All66constructor arrays match CPU reference,65nonCFV arrays/CPU/q/scales/query/save/resume exact, fullphysical poison seeds and regeneratedlogicalCFV exact. All144PTX/host entry bindings verified,68candidate chance-bearing constructors plus4river. Compiler/native/reader terminal; no speed claim.\n\nD197 freezes original3full canonical fixtures at identical quality/cadence/cap/stops, fullphysicalCFV and66devicebuffers/CPU/query/save/futureEV across continued/locked/resumed lifecycle. Actual E080/E102 hosts source-reversed after only original observer adapters and sealed PTX. Diagnostic clocks unscored;256GiBraw+64GiBheadroom,32GiBprocesscap and64/32GiBavailableRAM guards retained. Ordinary real-runtime compiler performance still required.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: pass parent chance engine controls and freeze canonical state'],cwd=h.REPO,check=True)
print(h.sha(H/'protocol.json'),flush=True)
