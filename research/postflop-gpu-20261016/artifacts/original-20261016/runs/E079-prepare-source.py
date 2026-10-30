"""Integrate the one D130-admitted setup overlap without changing its tested form."""
from pathlib import Path
import difflib,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());D=R/'runs/D130-plan-context-overlap';q=old.read(D/'report.json');assert q['admit_one_integrated_trial']and q['fixed_six_fresh_processes_complete']and q['ability_mock_controls']==18
S=R/'runs/E079-source';assert not S.exists();S.mkdir();path=old.REPO/'crates/solver/src/gpu/mod.rs';raw=path.read_bytes();base=raw.decode('utf-8');assert '\r\n'not in base
probe=(D/'probe.rs').read_text(encoding='utf-8');a=probe.index('fn coordinate<');b=probe.index('fn plan_budget(',a);helper=probe[a:b].replace('fn coordinate<','fn coordinate_initialization<',1)
assert helper.replace('fn coordinate_initialization<','fn coordinate<',1)==probe[a:b]
doc='''/// Join the original CPU plan/budget work and CUDA ownership setup before
/// returning either result. Budget errors keep their original priority.
/// Small trees keep the original serial path; OS spawn failure falls back.
''';helper=doc+helper
needle='fn build_lock_table(solver: &Solver)';assert base.count(needle)==1;candidate=base.replace(needle,helper+needle)
a=base.index('        let mut plan = GpuPlan::build(&solver.spot, solver.use_isomorphism);');b=base.index('        let ctx = CudaContext::new(0).map_err(e)?;',a);z=base.index('        // Compile the PTX for the device we actually found:',b);original=base[a:z];plan=base[a:b];gpu=base[b:z]
assert 'Storage::F32' in plan and 'needed > budget_bytes' in plan and gpu.count('CudaContext::new(0)')==1 and gpu.count('ctx.new_stream()')==1 and gpu.count('ctx.disable_event_tracking()')==1
replacement='''        let (plan, (ctx, stream)) = coordinate_initialization(
            solver.spot.tree.nodes.len() >= 65_536,
            || {
'''+''.join('    '+line if line.strip()else line for line in plan.splitlines(True))+'''                Ok(plan)
            },
            || {
'''+''.join('    '+line if line.strip()else line for line in gpu.splitlines(True))+'''                Ok((ctx, stream))
            },
        )?;
        // The context/stream may have been created on the scoped worker.
        ctx.bind_to_thread().map_err(e)?;

''';assert candidate.count(original)==1;candidate=candidate.replace(original,replacement,1)
mocka=probe.index(' for eligible in[false,true]{');mockb=probe.index(' assert!(cpu_ticks()>=before);',mocka);loops=probe[mocka:mockb].replace('coordinate(eligible,','coordinate_initialization(eligible,')
unit='''    #[test]
    fn context_plan_initialization_error_priority_and_cleanup() {
        use std::sync::atomic::{AtomicUsize, Ordering};
        struct Mock(Arc<AtomicUsize>);
        impl Drop for Mock { fn drop(&mut self) { self.0.fetch_add(1, Ordering::SeqCst); } }
        let mut controls = 0;
'''+loops+'''        assert_eq!(controls, 18);
    }

    #[test]
    fn context_worker_stream_roundtrip_with_active_primary_owner() {
        // Match the existing CUDA-test convention when CUDA is unavailable.
        let Ok(primary) = CudaContext::new(0) else { return; };
        for eligible in [false, true] {
            let (_, (ctx, stream)) = coordinate_initialization(eligible, || Ok(()), || {
                let ctx = CudaContext::new(0).map_err(e)?;
                let stream = ctx.new_stream().map_err(e)?;
                unsafe { ctx.disable_event_tracking() };
                Ok((ctx, stream))
            }).unwrap();
            ctx.bind_to_thread().unwrap();
            assert!(*ctx == *primary);
            let input: Vec<u32> = (0..257u32).map(|i| i.wrapping_mul(0x9e37_79b9) ^ 0x7fc0_1234).collect();
            let device = stream.clone_htod(&input).unwrap();
            let output = stream.clone_dtoh(&device).unwrap();
            stream.synchronize().unwrap();
            assert_eq!(input, output);
        }
    }

''';needle2='    fn reach_reuse_solver(';assert candidate.count(needle2)==1;candidate=candidate.replace(needle2,unit+needle2,1)
reverse=candidate.replace(unit,'',1).replace(replacement,original,1).replace(helper,'',1);assert reverse==base
(S/'baseline-mod.rs').write_bytes(raw);old.pin(S/'baseline-mod.rs',old.BASE['crates/solver/src/gpu/mod.rs']);(S/'candidate-mod.rs').write_text(candidate,encoding='utf-8',newline='\n');(S/'coordinate-initialization.rs').write_text(helper,encoding='utf-8',newline='\n');(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='crates/solver/src/gpu/mod.rs',tofile='crates/solver/src/gpu/mod.rs')),encoding='utf-8',newline='\n')
old.save(S/'manifest.json',{'id':'E079','at':old.now(),'accepted_source_sha256':old.BASE,'candidate_owned_sha256':{'crates/solver/src/gpu/mod.rs':old.sha(S/'candidate-mod.rs')},'owned':{'crates/solver/src/gpu/mod.rs':{'base':str(S/'baseline-mod.rs'),'candidate':str(S/'candidate-mod.rs')}},'D130_report_sha256':old.sha(D/'report.json'),'scope':'One host file only. For original trees>=65536nodes, unchanged serial CPUplan/fullF32/compressedbudget work overlaps a scoped worker creating the original primary context/stream with originaleventtracking setting. Join before result/error; budget error priority and panic/error cleanup as exactD130coordinator. Smaller trees serial, OSspawnfailurefallsback. Explicit root rebind in both paths as component. No contextcache/lifetimeextension,newplanparallelism,CUDA/kernel/compilerflags/math/quality/storage/layout/payload/graph/savechange. Added18mock unit andactualworker/rootstreamrawcopy withactiveprimaryowner. Productionfilecurrentlyofftree;testsnotyetexecuted.','candidate_accepted':False})
old.save(S/'source-review.json',{'at':old.now(),'original_plan_budget_body_verbatim':plan,'original_GPU_context_stream_body_verbatim':gpu,'coordinator_body_exact_from_D130_except_name_and_comment':True,'all_other_source_reversal_exact':True,'CUDA_source_sha256_unchanged':old.BASE['crates/solver/src/gpu/kernels.cu'],'original_fullF32_budget_branch_retained':True,'PcfrPlus_guard_before_any_worker_unchanged':True,'risk_and_counterevidence':'D130component screen passed145.855ms sum saving/CPUguards, but rivercomponent serialfallback was31.3545ms slower andall3pairs slower. It is not fixed or exempted here. Full complete-solve strictfixturegate must rejectifitpersists. D041serverVRAMqueryretainsprimarycontext,warmservergainmayvanish. Addedworker/TLS/bind/errorbudgetresourcecostsrequireactualmaterialchecksbeforeadoption. No universal/no-tradeoff/fullcyclegainclaim.','lifetime':'Every worker joined before usingresults or propagatingplanbudgeterror. Oncallerplanpanic,threadscopewaits;18mockcasespassinD130. GPUerrors/panicspropagateonlyafteradmittedplan,OSspawnfailurefallbackreview-only. Primarycontextowner/streamareexistingGpuSolverfieldswithoriginaldestructionorder. No global retainedowner/newmutablepayload. Fullactualconstructor/F32/warm/errors/locks/graphs/continuation/currentthreadbindingnotyetqualified.','tests':'ExactD13018mockloopplusactualserial/scopedstreamcopy withactiveprimaryowner,all257u32rawwords. TestskipswhenCUDAunavailableconsistentwithexistingGPUunits;researchqualificationmustconfirmactualCUDAexecution. NoOSspawnresourcefailureinjection orforceddriverunavailabletest.'})
paths=[Path(__file__),D/'protocol.json',D/'execution-plan.json',D/'report.json',D/'probe.rs',*[p for p in S.iterdir()if p.is_file()],C/'common_e051_live.py',C/'protected-main.json'];old.save(S/'preparation.json',{'at':old.now(),'status':'STAGED_NOT_FROZEN_FOR_COMPILER_NATIVE','input_sha256':{str(p):old.sha(p)for p in paths},'source_activated':False,'compiler_or_solver_executions':0,'candidate_accepted':False})
pub=[]
for p in S.iterdir():
 if p.is_file():
  key=S.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
  pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(S/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'production_source_unchanged':True,'compiler_or_solver_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='E079'for x in s['experiments']);s['experiments'].append({'id':'E079','at':old.now(),'title':'Overlap CPU planning with CUDA ownership setup','kind':'candidate','status':'pending','correctness':'D130fullplan/lifecyclecomponentcontrols pass; integratedsource staged only','fixture':'Original fixed full-solve suite; not run yet','stage':'Integrated source prepared','reason':'Exact D130 form staged in one host file. Component saved145.855ms, but a31.3545ms river setup regression remains unresolved. No source variant or exemption; full-solve strict fixture and material gates remain. CUDA/math/quality/plan/storage unchanged.','accepted':False,'evidence':[{'label':'Exact one-file source manifest','url':'evidence/E079-source/manifest.json'},{'label':'Source obligations and river counterevidence','url':'evidence/E079-source/source-review.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E079',stage='Preparing E079 integrated correctness and full-solve trial',activity='The context/plan overlap component passed its fixed admission screen. Exact one-file source is staged; no build or solver result yet. River setup slowdown remains unresolved and will face the unchanged full-solve guard. Accepted/live gain remains12.44%.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';b=ledger.read_bytes();assert b'### E079 plan-context integration source'not in b
entry=f'''

### E079 plan-context integration source

D130fixed component admits one source trial:145.855ms aggregate component saving andeligibleCPUguards pass,18fullplan snapshots/18errorcleanupmockspass. River serialfallback component is31.3545ms slower with3/3slowerpairs; this remains unresolved, not changed/exempted/resampled. Full-solve strictfixtureguard still applies; no claimed speedgain or notradeoff.

One off-treehostfileSHA{old.sha(S/'candidate-mod.rs')}. Genericcoordinator body mechanically exactfromD130 exceptname/doc; originalCPUplan/fullF32/compressedbudget bodyandoriginalcontext/stream/eventtrackingbody copiedverbatim intoclosures,originalunsupportedalgorithmguard remainsfirst. Fixedoriginalnodes>=65536eligibility,smallserialpath,scopejoin/errorpriority/OSspawnfallback/rootbind identicalcomponent. Originalconstructorrest/datafields/graphs/droporder/CUDA/compilerflags/quality/storage/save unchanged; removingalladdedpartsreversesexactlytoacceptedE051. Two meaningful unit sources:exact18mocks andserial/scopedrawstreamroundtrip withactiveprimaryowner. No compiler/current-sourceactivation/solver/sampleyet. Actualwarmserver/TLS/binding/budgeterrorresourcecosts,fullF32/state/menu/locks/graphs/save/resume/continuation,actualmaterial/1%/strictfixture/fresh16/holdout/cumulativeallremain. All{len(pub)}source/review/preparationartifacts HTTPbyteverified;accepted162/main163/live/protected2PTXunchanged. E051accepted/deployed12.4372274192%,lastprimaryB249 unchanged,goalactive.
''';nl=b'\r\n'if b'\r\n'in b else b'\n';ledger.write_bytes(b+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: stage the exact plan-context overlap host integration','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':'source_staged_only','candidate_sha256':old.sha(S/'candidate-mod.rs'),'CUDA_source_unchanged':True,'river_component_regression_unresolved':True}),flush=True)
