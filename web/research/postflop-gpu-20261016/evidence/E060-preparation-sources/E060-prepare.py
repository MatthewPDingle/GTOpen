"""Freeze one common-arity guarded reciprocal-refinement reuse candidate."""
import difflib,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
S=ROOT/'runs/E060-source';H=ROOT/'runs/E060-resource';assert not S.exists() and not H.exists();S.mkdir();H.mkdir()
base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();old.pin(old.REPO/'crates/solver/src/gpu/kernels.cu','a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647')
text=base.decode('utf-8').replace('\r\n','\n');newline='\r\n' if b'\r\n' in base else '\n'
needle='template<int NA>\n__device__ __forceinline__ void up_action_impl('
assert text.count(needle)==1
helper='''// Reuse only the denominator refinement observed in the compute_120
// driver's normal division path. Other architectures retain native division.
// Exceptional values and small numerators retain that division as well.
__device__ __forceinline__ float action_divide_with_refinement(
    float numerator, float denominator, float refined_inverse)
{
    float quotient = __fmaf_rn(numerator, refined_inverse, 0.f);
    float residual = __fmaf_rn(-denominator, quotient, numerator);
    return __fmaf_rn(refined_inverse, residual, quotient);
}

'''
text=text.replace(needle,helper+needle)
begin=text.index(needle);end=text.index('extern "C" __global__ void up_action(',begin)
body=text[begin:end]
needle2='''            float uni = 1.f / (float)na;
            float reach = rp[i];'''
assert body.count(needle2)==1
body=body.replace(needle2,'''            float uni = 1.f / (float)na;
            bool reuse_division = false;
            float refined_inverse = 0.f;
#if __CUDA_ARCH__ == 1200
            // Every positive regret is <= its rounded nonnegative sum.
            // This bounds nonzero selected numerators and all quotients
            // away from underflow/overflow in the reused normal path.
            if (NA != 0 && sum > 1e-12f && sum <= 0x1p60f) {
                float inverse;
                asm("rcp.approx.ftz.f32 %0, %1;" : "=f"(inverse) : "f"(sum));
                float residual = __fmaf_rn(-sum, inverse, 1.f);
                refined_inverse = __fmaf_rn(inverse, residual, inverse);
                reuse_division = true;
            }
#endif
            float reach = rp[i];''')
needle3='''                float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni;'''
assert body.count(needle3)==1
body=body.replace(needle3,'''                float numerator = r > 0.f ? r : 0.f;
                float sig;
                if (sum > 1e-12f) {
                    if (reuse_division && (numerator == 0.f || numerator >= 0x1p-60f))
                        sig = action_divide_with_refinement(numerator, sum, refined_inverse);
                    else
                        sig = numerator / sum;
                } else {
                    sig = uni;
                }''')
text=text[:begin]+body+text[end:]
candidate=text.replace('\n',newline).encode('utf-8')
(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(candidate)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(keepends=True),candidate.decode().splitlines(keepends=True),fromfile='accepted-E051/kernels.cu',tofile='E060/kernels.cu')),encoding='utf-8',newline='')
review={'id':'E060-source','at':old.now(),'mechanism':'Compute the denominator-only reciprocal approximation/refinement once per hand in common2/3/4 up_action; reuse for the original numerator-specific3FMA sequence seen in D098 driver SASS. Only compute120, valid positive denominator <=2^60 and numerator0 or >=2^-60. Original division for every other branch and architecture.','source_contract':['sum is an ordered sum of nonnegative r>0?r:0 terms; finite sum is >=every positive term by monotonic correctly-rounded nonnegative additions','selected sum>1e-12 is normal and <=2^60, so reciprocal is normal; numerator0 or >=2^-60 and <=sum bounds nonzero quotient >=2^-120 and <=1','if sum overflows/infinite or numerator is too tiny, original numerator/sum operation remains; NaN/nonpositive sums use original uniform branch','regret reads/order/threshold, child CFV/strategy/regret expression order, graph, allocations, menus, locks, quality and ABI unchanged','generic NA0 and other architecture preprocessor paths retain division arithmetic; require actual compiled comparisons not source claims'], 'precision_status':'UNPROVEN_PENDING_GPU_RAW_EXACTNESS. Matching observed normal-path operations and conservative domain is a source hypothesis, not proof of CUDA division equivalence or portability. No direct reciprocal multiplication replacement.','frozen_next_gates':'Allocated/resource gate first. If pass, require actual compiled reciprocal/refinement sharing and unchanged other8entries/ABI. Then raw scalar denominator/numerator and complete up_action kernel inputs/outputs/guards including boundary/nonfinite/native fallback cases, exact primary states/checkpoints, then same initial1%/fixture/fresh16/broader/material/holdout/cumulative policy. Stop on any numerical failure. No denominator-window, math, arity, placement or guard variants rescuing closed outcome.','tradeoff_risks':['extra lane predicates/divergence/fallback code and registers/local storage may outweigh eliminated reciprocal work','same occupancy alone does not establish equal allocated registers','source guard does not establish all actual device results'],'candidate_sha256':old.sha(S/'candidate.cu'),'independent_review':False,'d098_report_sha256':old.sha(ROOT/'comparisons/D098-static-root-check/report.json'),'no_source_activation':True}
old.save(S/'source-review.json',review)
old.save(S/'manifest.json',{'id':'E060','at':old.now(),'accepted_source':'E051','owned_sources':['crates/solver/src/gpu/kernels.cu'],'source_sha256':old.BASE|{'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')},'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'precision_unproven':True,'no_native_runs':True})
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
parent=ROOT/'runs/E059-resource'
probe=(parent/'probe.rs').read_text().replace('E059','E060').replace('up_chance','up_action');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(parent/'execute.py').read_text().replace('E059','E060').replace('up_chance','up_action')
line=" from branch_proof import compare as branch_compare\n branch=branch_compare(OUT/'baseline.ptx',OUT/'candidate.ptx');old.save(HERE/'blocker-branch-proof.json',branch);gates.update({'branch:'+k:v for k,v in branch['gates'].items()})\n"
assert runner.count(line)==1;runner=runner.replace(line,'')
line=" report['blocker_branch_proof_sha256']=old.sha(HERE/'blocker-branch-proof.json');"
assert runner.count(line)==1;runner=runner.replace(line,'')
runner=runner.replace('pass_resource_and_mechanism_prerequisites','pass_resource_prerequisite')
(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
anchor=parent/'execution/baseline.ptx';t=anchor.read_text();a=t.index('.entry up_action(');b=t.index('.visible .entry ',a+10);header=t[a:b].split('{',1)[0]
abi=[m[0] for m in re.findall(r'\.param\s+\.(u\d+)((?:\s+\.ptr\s+\.align\s+\d+)?)\s+up_action_param_\d+',header)];assert len(abi)==21,abi
P=old.read(parent/'protocol.json');P.update(id='E060-resource',at=old.now(),source_manifest_sha256=old.sha(S/'manifest.json'),changed_entries=['up_action'],expected_abi={'up_action':{'baseline':abi,'candidate':abi}},fixed_gates='Only up_action body changes, unchanged21parameter ABI and other8entries exact. D094 allocation/resource gates frozen. Resource prerequisite only; sharing mechanism/GPU scalar and kernel precision still unproven. No guard/window/arity/math/factor variants rescuing failure.')
P.pop('address_proof',None)
P['rustc_command']=[x.replace(str(parent),str(H)) for x in P['rustc_command']]
inputs=[*S.iterdir(),*H.iterdir(),Path(__file__),ROOT/'comparisons/D098-static-root-check/report.json',ROOT/'runs/D098-driver-machine-code-r2/capture-report.json',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in inputs if p.is_file()};P['input_sha256'].update({p:h for p,h in old.read(parent/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']})
old.save(H/'protocol.json',P)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='E060' for e in s['experiments'])
 s['experiments'].append({'id':'E060','at':old.now(),'title':'Share guarded action denominator refinement','kind':'candidate','status':'running','correctness':'pending','stage':'Frozen allocated-resource gate before precision/timing','reason':'One compute120 common-arity guarded reciprocal-refinement form from D098 actual SASS. Native division fallback retained; numerical equivalence unproven. Extra control/register costs gated before kernel execution.','evidence':[]})
 s.update(updated_at=old.now(),state='running',active_experiment='E060',stage='E060 compiler/resource prerequisite',activity='Testing one shared denominator-refinement form. Exactness and speed remain unproven; accepted E051 unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'abi_parameters':len(abi),'source_activated':False}),flush=True)
