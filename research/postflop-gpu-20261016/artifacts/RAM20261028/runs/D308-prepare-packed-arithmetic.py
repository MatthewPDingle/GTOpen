"""Freeze an owned module-only packed FP32 arithmetic capability probe."""
import hashlib, json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
H = ROOT / 'runs/D308-packed-arithmetic'
H.mkdir(exist_ok=False)
seen, hits, inventories = {}, [], []
pattern = re.compile(r'(?:sub|fma)\.[^;\n]{0,30}f32x2')
for folder in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'), ROOT / 'runs']:
    paths = subprocess.check_output(['rg', '--files', str(folder), '-g', '*.cu'], text=True).splitlines()
    inventories.append({'root': str(folder), 'CUDA_files': len(paths)})
    for name in paths:
        blob = Path(name).read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if digest in seen:
            continue
        seen[digest] = name
        if pattern.search(blob.decode('utf-8')):
            hits.append({'path': name, 'sha256': digest})
revisions = subprocess.check_output(['git', 'log', '--all', '--format=%H', '--', 'crates/solver/src/gpu/kernels.cu'], cwd=h.REPO, text=True).splitlines()
local = []
for revision in revisions:
    text = subprocess.check_output(['git', 'show', revision + ':crates/solver/src/gpu/kernels.cu'], cwd=h.REPO).decode('utf-8')
    if pattern.search(text):
        local.append(revision)
h.save(H / 'history.json', {'at': h.now(), 'inventories': inventories, 'unique_CUDA_hashes': len(seen),
    'recognized_packed_arithmetic_matches': hits, 'local_all_ref_revisions': len(revisions), 'local_matches': local,
    'classification': 'Independent action-pair arithmetic, not adjacent-hand memory vectorization E099, twohand chance accumulation E114, arity split E005/E014, division/refinement E060/E124 or dtype reduction. None of those hunks composed. Capability-only stage; full solver candidate not admitted.',
    'limits': 'Bounded recognized opcode/all-local-ref search, not exhaustive semantic/remote novelty.'})
assert not hits and not local, 'Review prior packed arithmetic form before probe'
words = [0, 0x80000000, 1, 0x007fffff, 0x00800000, 0x3f800000, 0xbf800000, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000, 0x7fc12345, 0x7f812345]
for lo in words:
    for hi in words:
        packed = lo | hi << 32
        assert packed & 0xffffffff == lo and packed >> 32 == hi
h.save(H / 'source-contract.json', {'at': h.now(),
    'primary_reference': 'https://docs.nvidia.com/cuda/archive/12.9.0/parallel-thread-execution/index.html#floating-point-instructions-fma',
    'secondary_reference': 'https://docs.nvidia.com/cuda/archive/12.9.0/parallel-thread-execution/index.html#floating-point-instructions-sub',
    'source_semantics': 'PTX8.8 specifies two independent binary32 components, RN options and default subnormal support; f32x2 operands are64bit bit containers. This probe uses explicitRN/noFTZ/noSAT/noapprox/no dtypeconversion. Targetsupport sm100+ is virtual ISA support, not proof of native SIMD issue savings onSM120.',
    'intended_formula': 'Each component independently RN_FMA(r,d,RN_SUB(v,out)); same final regret expression as existing scalar helper. Existing baselinePTX shows sub.f32 then fma.rn.f32 before regretstores. No sum/reduction or crosscomponent arithmetic. Full original solver FP-DAG/address/NaN/caller equivalence remains mandatory before any integration/adoption.',
    'pack_unpack': 'low32=r0/high32=r1; integerbit masks/shifts invert for every u32pair algebraically;169special-pattern pairs checked onCPU. Actual compiler/register/IEEE andNaNpayload behavior unqualified.',
    'scope': 'Two new diagnostickernels appended after entire exactaccepted9kernel sourceprefix, preserve originals byteexact. No solver code change, kernel launch, array allocation, numerical orspeed execution. One compiler/one NVRTC120module probe then oneownedCUPTIcapture/nvdisasm onlyif resource prerequisitespass.',
    'hard_native_gate': 'Packed primitive must provide fewer actual issued FP arithmetic instruction sites per2results than scalar2SUB+2FMAreference, with actual2component packed instruction/dataflow. One or both packedoperations mayqualify; vectorvirtualop alone, load/store/address or globalhistogram changes do not. Same4scalararithmetic sites means decline without solverprototype. Packing/register/codecosts remainreal and later wholecycle tests required.',
    'failure': 'Close tested packedaction arithmetic form without width/componentcount/handpair/scope/guard/helper/flags/precision/source/sample rescue if unsupported/scalarized/resourcefailed. Do not substitute FP16/BF16/TF32.'})
original = (h.REPO / 'crates/solver/src/gpu/kernels.cu').read_bytes()
suffix = r'''

// Diagnostic pair represents two independent action updates, not two hands.
extern "C" __global__ void scalar_regret_pair(
    const float* __restrict__ r, const float* __restrict__ d,
    const float* __restrict__ v, const float* __restrict__ node_out,
    float* __restrict__ result, int count)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) return;
    int j = 2 * i;
    float out = node_out[i];
    result[j] = r[j] * d[j] + (v[j] - out);
    result[j + 1] = r[j + 1] * d[j + 1] + (v[j + 1] - out);
}

extern "C" __global__ void packed_regret_pair(
    const float* __restrict__ r, const float* __restrict__ d,
    const float* __restrict__ v, const float* __restrict__ node_out,
    float* __restrict__ result, int count)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) return;
    int j = 2 * i;
    float r0 = r[j], r1 = r[j + 1], d0 = d[j], d1 = d[j + 1];
    float v0 = v[j], v1 = v[j + 1], out = node_out[i];
    float new0, new1;
    asm(
        "{\n\t"
        ".reg .b64 rp, dp, vp, op, delta, updated;\n\t"
        "mov.b64 rp, {%2,%3};\n\t"
        "mov.b64 dp, {%4,%5};\n\t"
        "mov.b64 vp, {%6,%7};\n\t"
        "mov.b64 op, {%8,%8};\n\t"
        "sub.rn.f32x2 delta, vp, op;\n\t"
        "fma.rn.f32x2 updated, rp, dp, delta;\n\t"
        "mov.b64 {%0,%1}, updated;\n\t"
        "}"
        : "=f"(new0), "=f"(new1)
        : "f"(r0), "f"(r1), "f"(d0), "f"(d1), "f"(v0), "f"(v1), "f"(out));
    result[j] = new0;
    result[j + 1] = new1;
}
'''.replace('\n', '\r\n').encode()
(H / 'accepted.cu').write_bytes(original)
(H / 'module.cu').write_bytes(original + suffix)
assert (H / 'module.cu').read_bytes()[:len(original)] == original
h.save(H / 'source-manifest.json', {'at': h.now(), 'accepted_prefix_sha256': h.sha(H / 'accepted.cu'),
    'diagnostic_module_sha256': h.sha(H / 'module.cu'), 'suffix_bytes': len(suffix), 'original9kernel_prefix_byteexact': True})
shutil.copyfile(ROOT / 'runs/E124-resource/baseline-compute_120.ptx', H / 'accepted-baseline.ptx')
rust = r'''
use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn emit(v:serde_json::Value){println!("D308_RESOURCE {v}");std::io::stdout().flush().unwrap();}
fn main(){
 let out=PathBuf::from(std::env::args().nth(1).unwrap());
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let originals=["copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","copy_span","up_action_eval"];
 for arm in ["baseline","diagnostic"]{
  let ptx=if arm=="baseline"{Ptx::from_src(include_str!("accepted-baseline.ptx"))}else{
   let p=compile_ptx_with_opts(include_str!("module.cu"),CompileOptions{arch:Some("compute_120"),..Default::default()}).unwrap();
   let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("primitive-compute_120.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();p};
  let m=ctx.load_module(ptx).unwrap();let mut names=originals.to_vec();if arm=="diagnostic"{names.extend(["scalar_regret_pair","packed_regret_pair"]);}
  for name in names{
   let f=m.load_function(name).unwrap();let dynamic=match name{"up_fold"=>1326*4,"up_show"=>1326*20,_=>0};
   let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|t|(t,f.occupancy_max_active_blocks_per_multiprocessor(t,dynamic,None).unwrap())).collect();
   emit(serde_json::json!({"stage":"resource","variant":arm,"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"constant_bytes":f.const_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"dynamic_shared_bytes":dynamic,"max_threads":f.max_threads_per_block().unwrap(),"occupancy_by_threads":occupancy,"device_shared_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap(),"device_thread_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap(),"context_stack_after":ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap(),"application_kernels":0}));
  }drop(m);ctx.check_err().unwrap();
 }
 drop(ctx);emit(serde_json::json!({"stage":"complete","candidate_NVRTC_compiles":1,"resource_rows":20,"application_kernel_launches":0,"device_array_allocations":0,"solver_or_speed_runs":0}));
}
'''
(H / 'probe.rs').write_bytes(rust.encode())
old = h.read(ROOT / 'runs/E124-resource/protocol.json')
capture = h.read(ROOT / 'runs/D225-chunk-native-bypass/protocol.json')
files = [Path(__file__), ROOT / 'runs/D308-execute.py', ROOT / 'epoch/common.py', H / 'history.json', H / 'source-contract.json', H / 'source-manifest.json', H / 'accepted.cu', H / 'module.cu', H / 'accepted-baseline.ptx', H / 'probe.rs',
    ROOT / 'runs/D225-chunk-native-bypass/protocol.json', ROOT / 'runs/D225-chunk-native-bypass/execution/before.json', Path(capture['capture_binary']), Path(capture['nvdisasm'])]
files += list(Path(capture['private_dll_dir']).glob('*.dll'))
files += [p for p in (ROOT / 'reference/accepted-e080-deps').iterdir() if p.is_file()]
h.save(H / 'protocol.json', {'id': 'D308', 'at': h.now(), 'status': 'FROZEN_PRE_PRIMITIVE_COMPILER_MODULE_NATIVE_INSPECTION',
    'rustc_command': [x.replace('E124-resource', 'D308-packed-arithmetic') for x in old['rustc_command']],
    'original_entries': old['original_entries'], 'GPU_uuid': old['GPU_uuid'], 'capture_binary': capture['capture_binary'], 'nvdisasm': capture['nvdisasm'], 'private_dll_dir': capture['private_dll_dir'],
    'baseline_before': str(ROOT / 'runs/D225-chunk-native-bypass/execution/before.json'),
    'required_free_bytes': 16 * 1024**3, 'input_sha256': {str(path): h.sha(path) for path in files},
    'admission': 'Only capability/emitted-arithmetic gate; all9originalnormalizedPTXheaders/bodies/resources unchanged. Bothnewkernels same6paramABI and fit ordinary128/256widths/local0/static0; no testapplicationkernels. Captureonlyifresources/ABIpass. Native fewer-than4 issued FPsites/pair and actualpackedcomponentdataflow mandatory before any solvercandidate.',
    'scope': 'OneRustcompiler/oneNVRTC120compile/ownedmoduleresourcequery; oneexistingCUPTIresourcecallbackcapture+one nvdisasm ifgatespass. No sourceactivation/GPUarrays/applicationkernels/CFR/solver/counters/precisionflag/performanceexecution. No claimed speed or numericalequivalence.',
    'failure': 'Close fixedtwo-action packedSUB/FMA form without width/handpair/placement/guard/helper/flags/source/precision/sample rescue; preserveallartifacts. AllnewbulkX/Sreadonly/noT.'})
for name in ['history.json', 'source-contract.json', 'source-manifest.json', 'protocol.json']:
    path = H / name
    dst = h.ar.DASHBOARD / 'evidence' / H.name / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    assert not dst.exists()
    shutil.copyfile(path, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + H.name + '/' + name, timeout=20) as response:
        assert response.read() == path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    assert not any(row['id'] == 'D308' for row in status['experiments'])
    status['experiments'].append({'id': 'D308', 'at': h.now(), 'title': 'Native packed FP32 action arithmetic capability', 'kind': 'diagnostic', 'status': 'staged', 'accepted': False,
        'correctness': 'not_yet_numerically_tested', 'stage': 'Frozen module-only primitive probe',
        'reason': 'Two independent action-update components using RNFP32x2 sub/FMA, no reducedprecision/FTZ. Must observe fewer native arithmetic sites than scalar4before anysolvercandidate; virtualISA alone insufficient. Original9CUDAprefix exact. No kernels/solves/timing planned here.',
        'evidence': [{'label': name, 'url': 'evidence/D308-packed-arithmetic/' + name} for name in ['history.json', 'source-contract.json', 'protocol.json']]})
    status.update(updated_at=h.now(), active_experiment='D308', stage='Packed action arithmetic: native capability gate', activity='E124closed. D308testsactualRTX5090lowering of two independent FP32actionupdates without touching solver/source/live sessions. E080 remains qualified/live; no newgain adopted.')
    h.ar.atomic_json(h.ar.STATUS, status)
h.custody()
print(json.dumps({'protocol_sha256': h.sha(H / 'protocol.json'), 'unique_CUDA': len(seen)}), flush=True)
