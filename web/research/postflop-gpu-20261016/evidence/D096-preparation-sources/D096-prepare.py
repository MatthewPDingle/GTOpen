"""Prepare a fresh two-tone CUPTI cohort, same accepted solver and observer DLL."""
import array,copy,difflib,json,re,shutil,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3
H=ROOT/'runs/D096-two-tone-profile';prior=ROOT/'runs/D087-cupti-driver-profile';assert not H.exists();H.mkdir()
schema=old.read(ROOT/'runs/D092-action-arity-order/field-schema.json')['fields'];metadata=old.read(ROOT/'runs/D092-action-arity-order/report.json')
selected=[metadata['cases'][i] for i in [3,7]]
def span_pattern(case):
    path=Path(case['raw_file']);old.pin(path,case['raw_sha256']);out={}
    wanted={'action_spans','chance_spans','chance_node_spans','fold_spans','show_spans','num_levels'}
    with path.open('rb') as f:
        assert f.read(16)==b'D092-PLAN-RAW1\0\0';identity,n=struct.unpack('<II',f.read(8));assert identity==case['id'] and n==53;f.read(16)
        for i,d in enumerate(schema):
            field,=struct.unpack('<I',f.read(4));assert field==i
            for arm in range(4):
                n,=struct.unpack('<Q',f.read(8))
                if arm==2 and d['name'] in wanted:
                    a=array.array('Q');a.fromfile(f,n)
                    if sys.byteorder!='little':a.byteswap()
                    if d['name']=='num_levels':assert len(a)==1;out[d['name']]=a[0]
                    else:assert len(a)==1+2*a[0];out[d['name']]=[bool(a[2+2*k]) for k in range(a[0])]
                else:f.seek(n*8,1)
    return out
patterns=[span_pattern(c) for c in selected];assert patterns[0]==patterns[1]
oldq=old.read(prior/'cohort-report.json');groups=list(oldq['traces'].values())[0]['graph_groups'];nodes=sorted(g['kernel_nodes'] for g in groups);assert nodes==[63,63,103]
records=sum(g['kernel_nodes']*(g['repeats_each_node']+1) for g in groups);assert records==26230
old.save(H/'topology-inputs.json',{'at':old.now(),'scope':'CPU work-list nonempty patterns only. Same accepted solver launch code and fixed200iteration/10check trajectory imply unchanged kernel graph node counts. Grid dimensions/metadata/transfer counts and durations may differ.','input_metadata':[{'case':c['id'],'board':c['board'],'sha256':c['raw_sha256'],'path':c['raw_file']} for c in selected],'patterns':patterns,'patterns_equal':True,'retained_rainbow_graph_kernel_nodes':nodes,'expected_two_tone_graph_kernel_nodes_sorted':nodes,'expected_kernel_records':records,'formula':'sum over3graphs: kernel_nodes*(captured replays+1first eager invocation). Training2*63*200, evaluation103*10.','retained_profile_report_sha256':old.sha(prior/'cohort-report.json'),'performance_measured':False})
source=(prior/'evaluator.rs').read_text(encoding='utf-8');needle='assert_eq!(filter.as_deref(),Some("rainbow"),"D087 diagnostic fixture");';assert source.count(needle)==1
evaluator=source.replace(needle,'assert_eq!(filter.as_deref(),Some("two-tone"),"D096 diagnostic fixture");')
(H/'evaluator.rs').write_text(evaluator,encoding='utf-8',newline='\n')
(H/'evaluator.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),evaluator.splitlines(True),fromfile='retained-D087-evaluator.rs',tofile='D096-evaluator.rs')),encoding='utf-8',newline='\n')
for name in ['build-diagnostic.py','run-cohort.py','root-and-publish.py']:
    text=(prior/name).read_text(encoding='utf-8')
    if name=='build-diagnostic.py':text=text.replace('D087 diagnostic evaluator compiled','D096 diagnostic evaluator compiled')
    else:
        text=text.replace("'rainbow'","'two-tone'").replace('reference[0][0]','reference[0][1]').replace('D087T','D096T')
        text=text.replace("'D087 '+identity","'D096 '+identity").replace("'D087 completed'","'D096 completed'")
        if name=='run-cohort.py':
            oldline="   assert sorted(repeats)==P['expected_graph_kernel_node_repeat_counts']"
            assert oldline in text
            text=text.replace(oldline,oldline+"\n   assert sorted(len(v) for v in groups.values())==P['expected_graph_kernel_nodes_sorted'] and len(kernels)==P['expected_kernel_records']")
        else:
            text=text.replace('==26230 and len(apis)',"==P['expected_kernel_records'] and len(apis)")
            text=text.replace('D087-driver-phase-root-check','D096-two-tone-root-check').replace("e['id']=='D087'","e['id']=='D096'").replace('Only fixed rainbow/thisGPU','Only fixed two-tone/thisGPU')
            text=text.replace('D087 root API/phase/raw clock replay','D096 root API/phase/raw clock replay').replace('D087 complete matched observer results','D096 complete matched observer results').replace('D087 native API correlation control','Retained D087 API correlation control')
            text=text.replace('D087 measured; inspect phase/API evidence','D096 measured; inspect two-tone phase/API evidence')
    (H/name).write_text(text,encoding='utf-8',newline='\n')
shutil.copyfile(prior/'ability-report.json',H/'ability-report.json')
old.save(H/'proposal.json',{'id':'D096-two-tone-profile','at':old.now(),'previous_goal_turn':'Progress: D094 allocation materiality/prospective helper and D095/E058 codegen closure. All native jobs terminal.','objective':'Measure actual device/kernel-family and DriverAPI/phase overlaps on the registered two-tone workload before selecting another optimization. Current reliable D085/D087 observer cohorts are rainbow-only; eager profiles are not normal graph-time evidence.','source_delta':'Fresh diagnostic evaluator differs from retained D087 evaluator only in the fixed fixture guard and diagnostic message. Same exact accepted E051solver rlib, CUDA source and existing D087Collector DLL/import library; unchanged callbacks, trace schema/magic, D087_TRACE_FILE/D087_META_FILE keys, phase hooks and explicit lifetime. Retain D087 names where they identify the actual binary API. No tracked source activation or primary evaluator edit.','plan':'Fresh3pairs BC/CB/BC, six separate processes, same two-tone configuration/compressedDCFR/.3%target/check20/max400/stop200. Every full non-timing result fingerprint payload and10checkpoints must match the two-tone accepted anchor. No old timing pooled/excluded/repeated.','observer_gate':'All fixed pairs must have <=10% absolute changes in complete-cycle, native-process and outer-runner clocks, same as D087. This is diagnostic usefulness, not a confidence or per-family bias bound. No rescue/exclusions/extensions.','trace_quality':'Zero errors/drops/invalid/outstanding buffers; six ordered timestamps. Correlate every kernel to expected driver API, three graph groups with kernel nodes63/63/103 and repeats199/199/9,407graph launches,26230kernel records pertrace. CPU work-list nonempty pattern proof preserved. Other transfer/API counts may differ.','scope':'Two-tone fixture only on current RTX5090, no optimization or whole-suite gain claim. Phase/API/device overlaps are not removable overhead; medians and family sums are not additive full-cycle partitions.','capability_basis':'Retained D08713kernel graph/API control and exact unchanged collector/DLL/SDK binary hashes. Fresh cohort independently checks all outputs and trace quality for this fixture. No elevation, injection, profiling counters, driver/global environment modification or live restart.','reviewer':'Root source/evidence review, not external independent review','candidate_accepted':False})
P=old.read(prior/'diagnostic-build-plan.json');oldout=P['output_dir'];P.update(id='D096-diagnostic-build',at=old.now(),status='FROZEN_BEFORE_COMPILE_OR_NATIVE',output_dir=str(H/'diagnostic-build'),source_sha256=old.BASE,source_relationship='Exact accepted E051solver rlib and retained D087observer implementation. Only diagnostic fixture guard/message changed to two-tone; accepted solver/evaluator/binaries and collector stay unchanged.',diagnostic_scope='Two-tone diagnostic only; fresh matched BC/CB/BC cohort must pass full result/checkpoint/observer/trace quality gates before using family/phase evidence. No speed acceptance.')
P['command']=[x.replace(str(prior/'evaluator.rs'),str(H/'evaluator.rs')).replace(oldout,str(H/'diagnostic-build')).replace('d087_rainbow_trace','d096_two_tone_trace') for x in P['command']]
inputs={p:h for p,h in P['input_sha256'].items() if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll'] or Path(p).name=='common_e051.py'}
inputs.update({str(p):old.sha(p) for p in [*H.iterdir(),Path(__file__),prior/'evaluator.rs',prior/'collector.cpp',prior/'build/D087Collector.dll',prior/'build/D087Collector.lib',prior/'cohort-report.json',ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'crates/solver/tests/postflop_autoresearch.rs',old.REPO/'bench_spot.json'] if p.is_file()})
P['input_sha256']=inputs;old.save(H/'diagnostic-build-plan.json',P)
published={}
for p in H.iterdir():
    if not p.is_file():continue
    key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
    published[key]=old.sha(p)
old.save(H/'pre-build-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert not any(e['id']=='D096' for e in s['experiments'])
    s['experiments'].append({'id':'D096','at':old.now(),'title':'Two-tone device and API phase profile','kind':'diagnostic','status':'running','correctness':'pending','stage':'Frozen off-tree diagnostic evaluator build','reason':'Reuse exact accepted E051solver and retained D087observer DLL. Fresh evaluator changes only fixture guard; fresh fixed3pairs will assess observer clocks, exact results and complete traces. No optimization or gain claim.','evidence':[{'label':'Two-tone diagnostic scope and fixed rules','url':'evidence/D096-two-tone-profile/proposal.json'},{'label':'CPU topology input proof','url':'evidence/D096-two-tone-profile/topology-inputs.json'},{'label':'Diagnostic evaluator guard-only delta','url':'evidence/D096-two-tone-profile/evaluator.patch'}]})
    s.update(updated_at=old.now(),state='running',active_experiment='D096',stage='D096 two-tone observer build',activity='Build one off-tree two-tone diagnostic with the unchanged accepted solver and observer. No primary/evaluator source activation or speed claim.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'build_protocol_sha256':old.sha(H/'diagnostic-build-plan.json'),'published':len(published),'expected_kernel_records':records,'graph_nodes':nodes}),flush=True)
