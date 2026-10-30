import sys,shutil,re,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
scope=ROOT/'runs/D168-RAM-thread-config-scope/scope-review.json';S=h.read(scope)
for path,digest in S['source_files_to_pin'].items():h.pin(path,digest)
parent=ROOT/'runs/D166-canonical-compiler-control';H=ROOT/'runs/D168-worker-raw-control';H.mkdir(exist_ok=False)
shutil.copytree(parent/'baseline',H/'gpu');shutil.copyfile(parent/'baseline.ptx',H/'baseline.ptx');shutil.copyfile(parent/'bench_spot.json',H/'bench_spot.json')
source=(parent/'baseline-probe.rs').read_text(encoding='utf-8');needle='#[path="baseline/mod.rs"]mod observed;';assert source.count(needle)==1;source=source.replace(needle,'#[path="gpu/mod.rs"]mod observed;',1)
wrapper='''
#[test]
#[ignore]
fn d168_worker_controls(){
    postflop_complete_cycle();
    // All clocks,fixtures,raw/lifecycle work and their destructors have finished.
    let requested:usize=std::env::var("RAYON_NUM_THREADS").unwrap().parse().unwrap();
    assert!([8,16,32].contains(&requested));let actual=rayon::current_num_threads();assert_eq!(actual,requested);
    println!("D168_POOL {}",serde_json::json!({"requested":requested,"actual":actual,"observation_after_entire_suite_and_lifecycle":true}));
    std::io::stdout().flush().unwrap();
}
'''
(H/'probe.rs').write_bytes((source+wrapper).encode())
base=(parent/'bounded_child.py').read_text(encoding='utf-8');base=base.replace('def run(command,out,label,h,limits,raw_root,output):','def run(command,out,label,h,limits,raw_root,output,workers):',1)
needle="env=h.env();env['D156_OUTPUT']=str(output)";assert base.count(needle)==1;base=base.replace(needle,needle+";assert workers in [8,16,32];env['RAYON_NUM_THREADS']=str(workers)",1)
base=base.replace("'output_env':{'D156_OUTPUT':str(output)}","'output_env':{'D156_OUTPUT':str(output),'RAYON_NUM_THREADS':str(workers)}",1)
(H/'bounded_child.py').write_bytes(base.encode());ast.parse(base);shutil.copyfile(parent/'sampler.py',H/'sampler.py')
for name in ['audit','execute']:shutil.copyfile(ROOT/'runs'/('D168-'+name+'.py'),H/(name+'.py'));ast.parse((H/(name+'.py')).read_text(encoding='utf-8'))
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
review=h.read(parent/'source-review.json');review.update(at=h.now(),id='D168',configuration_workers=[8,16,32],source_scope='Exactaccepted-E080D166baselinePTX/source/observer/lifecycle code;onlymodulepathadapterandappendedtestwrapper. Wrappercalls originalwholefunction thenqueries actualglobalRayoncountafterallclockedwork,rawcapture,lifecycle anddestructors. NoThreadPoolBuilder/preinitialization/scheduling/arithmetic/clock/source change. Rayonpoolalreadynecessarilyusedby nonemptycanonicalparallelpreparation/readback;sourcehasno explicitcountoverride exceptunrelatedCLI. Sameonebinaryfreshprocessperconfig;onlychild RAYON_NUM_THREADS changes. Existinggenericrunnerforced16 isnotused. Alltimesdiagnostic/unscored.',timing_qualification_samples=0)
h.save(H/'source-review.json',review)
limits=h.read(parent/'protocol.json')['limits'];files=[Path(__file__),scope,parent/'baseline-probe.rs',parent/'bounded_child.py',parent/'audit.py',parent/'protocol.json',ROOT/'comparisons/D166-canonical-compiler-control/report.json',ROOT/'epoch/exact-anchor.json',ROOT/'runs/D168-audit.py',ROOT/'runs/D168-execute.py']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D168','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_CONFIG_RAW_CONTROLS','rustc_command':cmd,'sequence':[{'id':'reference16','workers':16},{'id':'workers8','workers':8},{'id':'workers32','workers':32}],'lifecycle_stages':['converged','continued','locked','resumed'],'expected_unique_full_records':9,'expected_unique_checkpoints':69,'expected_unique_CPU_frames':36,'expected_unique_GPU69field_frames':36,'expected_query_pairs_vs_reference':12,'expected_save_pairs_vs_reference':6,'expected_future_EV_pairs_vs_reference':18,'limits':limits,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Threefresh serializedprocesses,sameacceptedE080sealed12PTXandfullcanonicalraw/lifecyclematrix,onlychildCPUworker countdiffers. Actualpoolsize queriedafterallsuitework,neverprewarmed. Everyfullrawpair(scales/CPU/66GPUbuffers/entireCFV/host/query/save/EV) mustequalreference16. Alloriginalscience/stop/checkpoint fields exact. Existinghonestprebuilt-NVRTCflagfalseexceptiononly. No speedqualification,numerical/source/corpus/count/affinity/power/OS/resampling rescue. Actualfailure closesaffectedconfiguration;allobservationspreserved.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
