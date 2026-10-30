import ast,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
parent=ROOT/'runs/D178-canonical-cache-control';engine=ROOT/'runs/D209-resident-engine-controls';resource=ROOT/'runs/D207-resident-resource';S=ROOT/'runs/E104-source';H=ROOT/'runs/D210-resident-canonical-controls';H.mkdir(exist_ok=False)
ER=ROOT/'comparisons/D209-resident-engine-controls/report.json';E=h.read(ER);assert E['cases']==36 and E['phase_pairs']==752 and h.read(engine/'execution/complete.json')['all_owned_compilers_native_readers_terminal'];h.pin(ER,h.read(engine/'execution/complete.json')['report_sha256'])
old=(parent/'baseline/mod.rs').read_text(encoding='utf-8');shim=old[old.index('pub mod plan {'):old.index('\nmod arena;')];suffix=old[old.index('\nimpl GpuSolver {\n    pub fn d166_snapshot'):];proof={}
for arm in ['baseline','candidate']:
 d=H/arm;d.mkdir();prod=(S/(arm+'-mod-r2.rs')).read_text(encoding='utf-8');src=prod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
 a=src.index('        static PTX:');b=src.index('            .clone()?;',a)+len('            .clone()?;');compileblock=src[a:b];binding='        assert_eq!(arch,"compute_120");\n        println!("D210_BIND '+arm+'");\n        let ptx=cudarc::nvrtc::Ptx::from_src(include_str!("../'+arm+'.ptx"));';src=src[:a]+binding+src[b:]
 back=src.replace(binding,compileblock,1).replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1);assert back==prod
 if arm=='candidate':
  needle='        Ok(true)\n    }';assert src.count(needle)==1;src=src.replace(needle,'        crate::d210_note_launch(p, reuse, blocks, self.resident.shared, self.num_levels);\n'+needle,1)
 observed=(engine/arm/'mod.rs').read_text(encoding='utf-8');observer=observed[observed.index('\nimpl GpuSolver {\n pub fn d209_state'):].replace('d209_state','d210_state')
 (d/'mod.rs').write_text(src+suffix+observer,encoding='utf-8',newline='\n');shutil.copyfile(parent/'baseline/arena.rs',d/'arena.rs');h.pin(d/'arena.rs',h.sha(h.REPO/'crates/solver/src/gpu/arena.rs'));shutil.copyfile(S/(arm+'-kernels.cu'),d/'kernels.cu')
 p=resource/('baseline-compute_120.ptx') if arm=='baseline' else resource/'execution/candidate-compute_120.ptx';shutil.copyfile(p,H/(arm+'.ptx'));proof[arm]={'raw_production_source_sha256':h.sha(S/(arm+'-mod-r2.rs')),'exact_reverse_after_only_old_plan_shim_sealed_PTX_and_diagnostic_marker':True,'adapted_sha256':h.sha(d/'mod.rs')}
 code=(parent/(arm+'-probe.rs')).read_text(encoding='utf-8').replace('D178','D210')
 for needle in ['        let mut gpu = GpuSolver::new(&host).expect("benchmark requires CUDA");','    let mut g=GpuSolver::new(&s).unwrap();']:
  assert code.count(needle)==1;var='gpu' if 'gpu =' in needle else 'g';code=code.replace(needle,needle+'println!("D210_CONSTRUCTOR {}",'+var+'.d210_state());std::io::stdout().flush().unwrap();',1)
 needle='json!({"stage":stage,"iteration":s.iteration,"ev_bits":ev,"info":info})';assert code.count(needle)==1;code=code.replace(needle,'json!({"stage":stage,"iteration":s.iteration,"ev_bits":ev,"info":info,"resident":g.d210_state()})',1)
 code+='\nfn d210_note_launch(p:usize,reuse:bool,blocks:u32,shared:u32,levels:usize){println!("D210_RESIDENT_LAUNCH {}",json!({"p":p,"reuse":reuse,"blocks":blocks,"shared":shared,"levels":levels,"parameter_bytes":3008}));std::io::stdout().flush().unwrap();}\n'
 (H/(arm+'-probe.rs')).write_text(code,encoding='utf-8',newline='\n')
for name in ['bench_spot.json','bounded_child.py','sampler.py']:shutil.copyfile(parent/name,H/name)
audit=(parent/'audit.py').read_text(encoding='utf-8').replace('D178-canonical-cache-control','D210-resident-canonical-controls').replace('D178_BIND','D210_BIND').replace("'id':'D178'","'id':'D210'")
needle="    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}";assert audit.count(needle)==1
audit=audit.replace(needle,"""    actual=[json.loads(x.split('D210_CONSTRUCTOR ',1)[1]) for x in text.splitlines() if x.startswith('D210_CONSTRUCTOR ')]
    req(len(actual)==6 and sum(x['selected'] for x in actual)==(4 if arm=='candidate' else 0),'all original initial/resumed constructor selections')
    for x in actual:
        req(x['candidate']==(arm=='candidate') and x['wrapper_bytes']==(4472 if arm=='candidate' else 4448),'actual arm/predeclared wrapper cost')
        req(x['selected']==(arm=='candidate' and 0<x['levels']<=64 and x['largest_phase']>=170),'actual shape eligibility')
        if x['selected']:req(x['largest_phase']>x['grid_capacity']>0,'full canonical repeated work per resident CTA')
    launches=[json.loads(x.split('D210_RESIDENT_LAUNCH ',1)[1]) for x in text.splitlines() if x.startswith('D210_RESIDENT_LAUNCH ')]
    if arm=='candidate':
        req(launches and all(0<x['blocks'] and x['parameter_bytes']==3008 for x in launches),'actual resident enqueue markers')
        req(all(any(x['p']==p and x['reuse']==reuse for x in launches) for p,reuse in [(0,False),(1,True)]),'actual full/p1reuse paths')
    else:req(not launches,'original arm no resident kernel')
"""+needle,1)
needle="        stage=bs['stage'];req(bs==cs,'every EV/iteration/fielddtype/count/geometry/graph/wrappermetadatabit exact')";assert audit.count(needle)==1
audit=audit.replace(needle,"""        stage=bs['stage']
        req(bs['info']['wrapper_bytes']==4448 and cs['info']['wrapper_bytes']==4472,'predeclared exact 24B wrapper cost')
        bx={k:v for k,v in bs.items() if k!='resident'};cx={k:v for k,v in cs.items() if k!='resident'}
        bx['info']={k:v for k,v in bs['info'].items() if k!='wrapper_bytes'};cx['info']={k:v for k,v in cs['info'].items() if k!='wrapper_bytes'}
        req(bx==cx,'all original EV/iteration/fielddtype/count/geometry/graph/hostmetadata exact except measured prospective wrapper cost')
        for obs,want in [(bs['resident'],False),(cs['resident'],name!='river')]:
            req(obs['selected']==want and len(obs['graphs'])==2,'actual selected capture/replay graph pairs')
            for graph in obs['graphs']:req(graph['cooperative_nodes']==int(want) and (not want or graph['kernel_nodes']==2),'actual 2kernel/1cooperative selected training graphs')
""",1)
audit=audit.replace("'scope':'Original three full", "'declared_wrapper_cost_bytes':{'baseline':4448,'candidate':4472,'delta':24},'actual_selected_candidate_constructors':4,'all_actual_selected_graphs_2kernel_1cooperative':True,'scope':'Original three full",1)
ast.parse(audit);(H/'audit.py').write_text(audit,encoding='utf-8',newline='\n')
execute=(parent/'execute.py').read_text(encoding='utf-8').replace('D178-canonical-cache-control','D210-resident-canonical-controls').replace('D178','D210').replace('CFV cache-hint','Resident cooperative traversal').replace('CFV cache hint','Resident cooperative traversal');ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
review=h.read(parent/'source-review.json');review.update(id='D210',at=h.now(),source='ExactE080/E104r2 full GPU host types with only original public plan/arena adapters, sealed D207 PTX, unchanged D166 66buffer observer and D209 actual selection/graph observer. All source prefixes reverse exactly to their frozen production copies.',source_reversal_proof=proof,wrapper_cost='4448/4472 (+24B) explicitly declared and measured before first CFR/native outcomes, from D208. Every other original metadata/numeric field remains exact; reader checks both actual wrapper costs.',scope='All original full 200/200/60 samequality targets/checks/cap; 12 CPU+12 entirephysicalGPUbuffer pairs and whole query/save/futureEV. Actual4selectedcandidate constructors/2riverfallback and selected2kernel1cooperative graphs required. Both fullflops must have more workitems than residentcapacity, proving sharedscratch CTA reuse in real CFR. Prebuilt PTX/giant observer clocks unscored.',failure='Any genuine raw/EV/liveness/graph/eligibility mismatch closes E104 without source/helper/width/threshold/flags/quality/numeric-field/sample rescue. Mechanical compiler/observer/reader errors preserved and may be fixed with no completed native cases repeated. Main/live/source/protectedPTX unchanged; all output X.')
h.save(H/'source-review.json',review)
deps=ROOT/'reference/accepted-e080-deps';commands={}
for arm in ['baseline','candidate']:
 cmd=['rustc',str(H/(arm+'-probe.rs')),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
 for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
 commands[arm]=cmd+['-o',str(H/(arm+'.exe'))]
oldP=h.read(parent/'protocol.json');files=[Path(__file__),parent/'protocol.json',parent/'source-review.json',parent/'audit.py',parent/'execute.py',S/'manifest-r2.json',S/'source-review.json',S/'host-source-review-r2.json',resource/'protocol.json',resource/'report.json',ER,engine/'reader-r2-protocol.json',engine/'execution/complete.json',ROOT/'runs/D208-resident-host-layout/report.json',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json',h.REPO/'crates/solver/tests/postflop_autoresearch.rs']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{**{k:v for k,v in oldP.items() if k not in ['id','at','input_sha256','rustc_commands','status']},'id':'D210','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_LARGE_RESIDENT_CFR_NATIVE','rustc_commands':commands,'expected_selected_constructors':{'baseline':0,'candidate':4},'declared_wrapper_bytes':{'baseline':4448,'candidate':4472},'input_sha256':{str(p):h.sha(p) for p in files},'scope':review['scope'],'failure':review['failure']})
evidence=[]
for folder,names in [(engine,['reader-r2-review.json','reader-r2-protocol.json','execution/complete.json']),(ER.parent,['report.json']),(H,['protocol.json','source-review.json'])]:
 for name in names:
  p=folder/name;key=folder.relative_to(ROOT).as_posix()+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  evidence.append({'label':folder.name+' '+name,'url':'evidence/'+key})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D209');item.update(status='measured',correctness='pass_36cases_full_engine_raw_lifecycle',stage='36cases/752phases/583324 reader checks passed',reason='All raw/CPU/query/save/EV/poison contracts exact,68actualselectedcandidateconstructors andactualcooperativegraphs. Native process terminal0. Reader log-path repair retained, no native/compiler repeats. No speed samples.');item.setdefault('evidence',[]).extend(evidence[:4]);s['experiments'].append({'id':'D210','title':'Resident full canonical raw state and lifecycle','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','correctness':'pending_full_canonical_raw','stage':'Full canonical 66device/CPU/raw/lifecycle controls frozen','reason':review['scope'],'evidence':evidence[4:]});item=next(x for x in s['experiments'] if x['id']=='E104');item.update(stage='Engine matrix passed; large canonical state frozen',reason='36cases/752phases/583324readerchecks exact. Actual cooperative training graphs proven. Fullsize scratchreuse/raw state and real NVRTC complete-speed still unqualified.');s.update(updated_at=h.now(),active_experiment='D210',stage='Resident full-size solver state prerequisite',activity='Small engine passes. Next original full workloads200/200/60 andwhole66GPU/CPUstates, query/save/resume, withstrictRAM/diskguards. E080/16/defaultaffinity unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n### D209 engine exact; D210 full canonical resident controls frozen\n\nD209 one compiler and one native36case process terminal0:752phasepairs/3528rawframes/583324readerchecks, all original numeric/poison/CPU/query/save/resume/EV state exact. Actual68eligiblecandidateconstructors/144PTXbindings and2kernel1cooperativetraininggraphsenqueuep0full,p1reuse,p1standalone verified. Originalreader fullycomparedraw then failed final loglookup(output/probe.stdout.log instead ofexecution); read-onlyR2pathrepair alloriginalgatesretained, terminal0, no native/compiler repeated. Explicit wrapper costs4448/4472 preserved. No performance sample or adoption.\n\nD210 freezesoriginal full canonical200/200/60 samequality/cadence/cap CPU/66device wholephysicalCFV andquery/save/futureEV lifecycle. TrueE080/E104r2productionhostprefix reversals; exactD207sealedPTX; alloriginalrawobserversunchanged. Addsactualpath/graphreadonlyobserver;4selectedcandidateinitial/resumeflopconstructors and2riverfallback, selectedgraphs2kernel1cooperative, andlargestphase>residentcapacityprove repeated work/sharedscratchreuse. Explicitwrappercost4448/4472checked;everyotheroriginalmetadata/numericfield exact. Twofreshcompilers/BthenCnativeprobes,256GiBrawreserve+64GiBheadroom/32GiBprocesscap/64before32duringavailableRAM. NoNVRTC/speed qualification;allgenuinefailureclosureandunchangedstrictcomplete1%/fresh16/material/broad/holdout/cumulative/applicationgatesremain. AlloutputX/mainliveE080unchanged.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: verify resident engine and freeze full canonical state controls'],cwd=h.REPO,check=True)
print(h.sha(H/'protocol.json'),flush=True)
