import sys,shutil,re,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists()
raw=ROOT/'comparisons/D168-worker-raw-control/report.json';proof=h.read(raw)
assert proof['status']=='pass_actual_worker_counts_and_full_canonical_raw_state' and proof['actual_workers']=={'reference16':16,'workers8':8,'workers32':32}
H=ROOT/'runs/D169-worker-comparison';H.mkdir(exist_ok=False)
original=h.REPO/'crates/solver/tests/postflop_autoresearch.rs';text=original.read_text(encoding='utf-8');source,n=re.subn(r'^//!','//',text,flags=re.M);assert n==7
assert source.count('#![cfg(feature = "gpu")]\n')==1 and source.count('include_str!("../../../bench_spot.json")')==1
source=source.replace('#![cfg(feature = "gpu")]\n','',1).replace('include_str!("../../../bench_spot.json")','include_str!("bench_spot.json")',1)
wrapper='''
#[test]
#[ignore]
fn d169_worker_cycle(){
    postflop_complete_cycle();
    let requested:usize=std::env::var("RAYON_NUM_THREADS").unwrap().parse().unwrap();
    assert!([8,16,32].contains(&requested));let actual=rayon::current_num_threads();assert_eq!(requested,actual);
    println!("D169_POOL {}",serde_json::json!({"actual":actual,"requested":requested,"after_entire_suite_and_destructors":true}));
    std::io::Write::flush(&mut std::io::stdout()).unwrap();
}
'''
(H/'probe.rs').write_bytes((source+wrapper).encode());shutil.copyfile(h.REPO/'bench_spot.json',H/'bench_spot.json')
for name in ['execute','assess']:shutil.copyfile(ROOT/'runs'/('D169-'+name+'.py'),H/(name+'.py'));ast.parse((H/(name+'.py')).read_text(encoding='utf-8'))
shutil.copyfile(ROOT/'runs/D157-sampler.py',H/'sampler.py')
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
unit=ROOT/'binaries/E080-solver.exe';unit_manifest=unit.with_suffix('.manifest.json');m=h.read(unit_manifest);h.pin(unit,m['binary_sha256']);assert m['source_sha256']==h.custody()
units=[{'id':'D169-U'+str(w),'workers':w,'kind':'unit'} for w in [16,8,32]]
warm=[{'id':'D169-W'+str(w),'workers':w,'kind':'warmup'} for w in [16,8,32]]
blocks=[[16,8,32],[8,32,16],[32,16,8]];scored=[{'id':f'D169-T{w}-R{b+1}','workers':w,'kind':'scored','block':b+1} for b,order in enumerate(blocks) for w in order]
for row in units+warm+scored:assert not(ROOT/'runs'/row['id']).exists()
h.save(H/'source-review.json',{'at':h.now(),'id':'D169','solver':'Unmodified acceptedE080solver librarybinary/source,CUDA/math/cache/allocations/launches/quality/bench_spot. Sameonefreshstandaloneharness executableheldconstant across8/16/32. Originalacceptedbenchmarkbinaries remainuntouched.','harness':'Fulloriginalbenchmark functionbody unchanged except7doccomment/cfg/path relocation adapters. Appendedtestwrapper callstheoriginalfunction exactlyonce,thenobservesactualglobalpoolafterentiresuiteanddestructors. Noquery/prewarm/clocked codeinsertion or new solveralgorithm. Newharness binary isnotclaimed byte-identicaloriginalCargoexe;matched16control uses sameharness,neverhistoricaltimingpooling. Adoptionstillneedsoriginalapplication qualification.','timing':'OriginalruntimeNVRTC12/JIT andfullcomplete clocks restored;no prebuiltPTX/giantobservers/extra lifecycle. Everyfullscience recordand23checkpoints mustexactoriginalanchor;actualpoolmetadataafterallscore. OnlychildRAYON_NUM_THREADS varies. ReadonlyterminalCPU/FILETIME capturethroughdestructors,noalivepollingtointerferewithclocks.','frozen_design':'3ordinaryunitprocesses,3prespecifiedunscoredwarmups(16/8/32),then9scored freshprocesses in3balancedblocks16-8-32/8-32-16/32-16-8. Shared16controlperblock prospectivelydeclaredforbothconfigcomparisons. Noothercounts/affinity/power/priority/OS/driver/source/flags,exclusions/extensionsorhistorical/RAMbaseline samples.','policy':'Each8or32form independentlyneedsunrounded>=1%sumfixturemedian gainvs16,strictpositivefixturemedian+>=2/3slowerpairguardclear,and<=1%medianwholeprocessCPU/lifetime regression. Reportremainingpeak/responsiveness/nonpostflop risks,not zero-cost claims. Anyadvance requiresseparatefresh16 andallbroad/material/capacity/holdout/freshoriginal/servergates. No globalCPU/preflop/reportchangehere.'})
files=[Path(__file__),raw,ROOT/'runs/D168-worker-raw-control/protocol.json',ROOT/'runs/D168-worker-raw-control/execution/complete.json',ROOT/'runs/D168-RAM-thread-config-scope/scope-review.json',original,unit,unit_manifest,ROOT/'epoch/exact-anchor.json',ROOT/'epoch/common.py']+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D169','at':h.now(),'status':'FROZEN_PRE_COMPILER_UNITS_WARMUPS_AND_FIRST_TIMING','rustc_command':cmd,'unit_binary':str(unit),'unit_binary_sha256':h.sha(unit),'sequence':units+warm+scored,'scored_blocks':blocks,'reference_workers':16,'candidate_workers':[8,32],'required_units_per_config':86,'required_unit_ignored':4,'expected_scored_results':27,'expected_scored_checkpoints':207,'minimum_aggregate_gain_pct':1.0,'max_process_CPU_or_lifetime_median_regression_pct':1.0,'strict_fixture_guard':'Failifcandidatefixturemedian>referenceandatleast2of3matchedblockpairsslower,withnominimumslowdownthreshold.','required_free_bytes':16*1024**3,'native_timeout_seconds':1200,'all_samples_required':True,'excluded_or_extension_samples_allowed':False,'historical_timing_pooling_allowed':False,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'One acceptedE080 solver/onefreshmatchedharness,threechildCPUworkerconfigs. Allsameoriginalcompleteclocks/quality/science,actualworkerobservationafterallwork. Exact86units/configthen3equalprespecifiedwarmups,9scoredbalancedprocesses. Eachconfigscreenindependentvsprospectivelyshared16controls. TerminalCPU/lifetimechecksavoidcostshifting. Nostatisticalsignificance/adoptionfromsmallinitialscreen;failedformsclosedwithoutcounts/source/flags/resampling rescue.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
