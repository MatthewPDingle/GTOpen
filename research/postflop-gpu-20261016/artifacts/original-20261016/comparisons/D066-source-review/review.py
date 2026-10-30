import pathlib,json,hashlib,re,datetime
B=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016'); R=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016'); O=B/'comparisons/D066-source-review'; S=B/'runs/D066-fold-zero-census/source'; D=S.parent/'design'
pins={}; checks=[]
def ck(v,n):
    assert v,n
    checks.append(n)
def pin(p,h=None):
    p=pathlib.Path(p); a=hashlib.sha256(p.read_bytes()).hexdigest()
    if h is not None: ck(a==h,'sha '+str(p))
    pins[str(p)]=a;return a
def read(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
pin(S/'source-manifest.json','0df9774c514a3ad3260b96ee219e6154ac8f402307912dd6130f84e8111e2748'); m=read(S/'source-manifest.json')
for name,h in m['artifact_sha256'].items(): pin(S/name,h)
for path,h in m['reference_sha256'].items(): pin(path,h)
dm=read(D/'manifest.json')
for name,h in dm['artifact_sha256'].items(): pin(D/name,h)
base=read(B/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
ck(m['accepted_source_sha256']==base and len(base)==162,'exact accepted162 identity map')
for name,h in base.items(): pin(R/name,h)
ck(not (R/'crates/solver/src/gpu/fold_zero_census.rs').exists(),'new helper not activated')
b=(S/'base-mod.rs').read_bytes(); c=(S/'candidate-mod.rs').read_bytes()
ck(c==b+b'\n#[cfg(test)]\nmod fold_zero_census;\n','append-only test declaration bytes')
s=(S/'candidate-fold_zero_census.rs').read_text(encoding='utf-8'); old=(B/'runs/D045-sparse-event-diagnostic/source/candidate-graph_device_events.rs').read_text(encoding='utf-8')
anchors=read(D/'anchors.json'); literal=s.split('const ANCHORS_JSON: &str = r###"',1)[1].split('"###;',1)[0]
ck(json.loads(literal)==anchors,'literal anchors exact')
for rid in ['E020C1','B065']:
    report=read(B/f'runs/{rid}/report.json')
    raw=(B/f'runs/{rid}/stdout.log').read_text(encoding='utf-8')
    stages=[json.loads(l.split('AUTORESEARCH_STAGE ',1)[1]) for l in raw.splitlines() if 'AUTORESEARCH_STAGE ' in l]
    ck(stages==[x['data'] for x in report['stages']],rid+' raw stage objects exact')
    results=[json.loads(l.split('AUTORESEARCH_RESULT ',1)[1]) for l in raw.splitlines() if 'AUTORESEARCH_RESULT ' in l]
    ck(results==report['results'],rid+' raw results exact')
    for a in anchors:
        v=next(x for x in results if x['fixture_id']==a['fixture_id'])
        ck(a['config']==v['config'] and a['state_fingerprint']==v['state_fingerprint'] and a['nodes']==v['nodes'] and a['final_iteration']==v['iteration'],rid+' complete anchor '+a['fixture_id'])
        cv=[{'iteration':x['iteration'],'exploit_bits':x['exploit_bits']} for x in stages if x['stage']=='convergence_check' and x['fixture_id']==a['fixture_id']]
        ck(cv==a['convergence'],rid+' all checkpoint anchors '+a['fixture_id'])
def fn(text,name):
    start=text.index('fn '+name+'('); end=text.find('\nfn ',start+3)
    return text[start:end if end>=0 else len(text)].strip()
# Compare exact reused contiguous helpers, avoiding trailing new comments.
for name,nextname in [('compare_cpu','check_exploit')]:
    ck(s[s.index('fn '+name+'('):s.index('fn '+nextname+'(')]==old[old.index('fn '+name+'('):old.index('fn '+nextname+'(')],'exact D045 '+name)
ck(s[s.index('// Stream every byte'):s.index('const ANCHORS_JSON')].strip()==old[old.index('// Stream every byte'):old.index('const ANCHOR_JSON')].strip(),'exact inherited fingerprint implementation')
ck('let owner_contexts = [ordinary._ctx.clone(), observed._ctx.clone(), ctx.clone()];' in s and s.index('drop(ordinary); drop(observed);')<s.index('let errors: Vec<_>')<s.index('"cleanup_complete":true'),'all owner contexts checked after drop before success')
ck(all(x not in s for x in ['begin_capture(','.launch(', 'CudaEvent','compile_ptx','cuLaunchKernel']),'no added event/kernel/capture/compiler calls')
schema=read(S/'output-schema.json'); order=[]
for fixture,end in [('rainbow',200),('two-tone',200),('river',60)]:
    order.extend([{'fixture_id':fixture,'stage':'admission'},{'fixture_id':fixture,'stage':'geometry'}])
    for i in range(20,end+1,20):
        if i in [20,end]: order.append({'fixture_id':fixture,'stage':'snapshot','iteration':i})
        order.append({'fixture_id':fixture,'stage':'checkpoint','iteration':i})
    order.append({'fixture_id':fixture,'stage':'final_anchor_exact','iteration':end})
order.append({'stage':'complete'})
ck(schema['expected_stage_order']==order and len(order)==39,'39 fixed marker order')
ck(len(schema['expected_files'])==15 and len(set(schema['expected_files']))==15,'15 unique compact files')
ck(schema['native_summary']==dict(passed=1,failed=0,ignored=0,measured=0,filtered_out=88),'one ignored test selected and88 filtered')
# Installed implementation establishes per-wrapper, not primary-handle, error storage.
core=pathlib.Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\driver\safe\core.rs');pin(core)
ct=core.read_text();ck('error_state: AtomicU32::new(0)' in ct and 'self.error_state.swap(0, Ordering::Relaxed)' in ct,'cudarc wrapper-specific recorded errors')
report={'id':'D066','verdict':'PASS_SOURCE_ONLY_DIAGNOSTIC_REVIEW','independent_source_review_pass':True,'source_manifest_sha256':pins[str(S/'source-manifest.json')],'findings':[],
'resolved_finding':{'issue':'Separate admission-context check_err did not inspect either solver wrapper recorded destruction errors.','resolution':'Retain both solver owner context Arcs, drop both solvers, then inspect all three wrappers and aggregate errors before cleanup_complete.','preserved':'source/draft-r1 and correction.json'},
'source_reasoning':[
'Accepted iterate performs full p0 down then p0 up, followed by p1 down with nh1=0 and p1 up. Up sweeps do not write reaches. Final reach1 therefore remains the exact p0 fold opponent input; final reach0 is the exact p1 fold opponent input. Both arrays are read after paired iterations and before either evaluation.',
'Uploaded flat fold list, host spans, both reach-slot maps, node players and f32 payouts are compared against a separately built accepted GpuPlan. Contiguous spans cover every actual fold CTA; no uniqueness assumption or full-tree substitution.',
'Each physical reach allocation is exactly reach_blocks[q]*nh[q] and nh[q]>0. Absolute word index divided by logical nh carries row flags across chunks. Four disjoint word categories and three independent row bits preserve mixed rows; flag0 means every word bits0x00000000.',
'Finite selected f32 amount is a separate exponent-bit predicate using the exact up_fold player/payout selection. This does not imply positive-zero outputs or safe omitted stores.',
'Three fixtures retain ordinary20-iteration checks to200/200/60; six pre-evaluation snapshots,23 checkpoint records and three final complete q/scale pair comparisons plus original/E020 fingerprints. No numerical production method, CUDA source, evaluator, launch, event or graph modification.',
'Pairwise float buffers are bounded to8MiB. Existing D045 admission counts two solver payloads plus reserves; sequential fixtures, create-new15files, error-path solver drains and checked final destruction are retained.'],
'limits':['Source review only; no Rust typecheck, compiler, native or GPU execution by reviewer.','Retained mappings and row flags permit count recomputation. Raw float payloads and complete CPU stores are not retained: their exact equality depends on the pinned native checks if executed, not FNV alone.','Whole-reach word counts include non-fold rows and are not fold-CTA counts. Six snapshots do not measure all-iteration frequency, kernel cost, headroom, safe fast-path behavior or savings.','Final primary-context wrapper release after checked solver destruction follows existing cudarc ownership; no device reset or additional lifecycle experiment introduced.'],
'reviewer_correction':'Preserved reviewer-r1 failure: startswith omitted the suite_start marker after Rust test prefix; split at observed marker anywhere in line now matches complete raw/report stage objects. A second reviewer-only extraction used new plural anchor name in the old D045 file; corrected to its actual singular ANCHOR_JSON delimiter and preserved r2. No source or runtime evidence changed.','checks':checks,'input_sha256':pins,'compiler_native_gpu_executed':False,'candidate_accepted':False,'execution_authorized':False}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('D066 source-only review passes. One cleanup error-provenance issue was corrected before seal and its draft preserved. The census reads the exact retained opponent inputs before evaluation, classifies positive-zero bits without summation, and counts actual uploaded fold work through verified mappings. It provides snapshot incidence only; no performance or fast-path claim. No compiler/native/GPU work was performed. See report.json for pinned source/schema, controls and limits.\n',encoding='utf-8')
manifest={'id':'D066-source-review','verdict':report['verdict'],'artifact_sha256':{name:hashlib.sha256((O/name).read_bytes()).hexdigest() for name in ['report.json','README.md','review.py','review-r1.py','review-r2.py','reviewer-correction.json','reviewer-correction-r2.json']}}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'pins':len(pins),'report_sha256':manifest['artifact_sha256']['report.json'],'manifest_sha256':hashlib.sha256((O/'manifest.json').read_bytes()).hexdigest()}))
