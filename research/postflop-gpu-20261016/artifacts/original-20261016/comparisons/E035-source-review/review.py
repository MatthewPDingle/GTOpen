from pathlib import Path
import hashlib,json,re,struct
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
HERE=Path(__file__).resolve().parent
SRC=ROOT/'runs/E035-design'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
pins={}
def pin(p,h=None):
 p=Path(p);actual=sha(p)
 if h is not None: assert actual==h,(str(p),actual,h)
 pins[str(p)]=actual
 return actual
seal=pin(SRC/'manifest.json','044151bbf7a9118b96d71ddf8d08d4ee2c36122d1a87ecd3ffa098591320d126')
m=read(SRC/'manifest.json')
for n,h in m['artifact_sha256'].items():pin(SRC/n,h)
for n,h in m['reference_sha256'].items():pin(n,h)
accepted=read(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
assert m['accepted_source_sha256']==accepted and len(accepted)==162
for n,h in accepted.items():pin(REPO/n,h)
assert set(m['owned_sources'])=={'crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs'}
for n,h in m['accepted_owned_sha256'].items():assert sha(SRC/'base'/Path(n).name)==h==accepted[n]
for n,h in m['candidate_owned_sha256'].items():assert sha(SRC/'candidate'/Path(n).name)==h!=accepted[n]
b=(SRC/'base/kernels.cu').read_bytes();c=(SRC/'candidate/kernels.cu').read_bytes()
bm=(SRC/'base/mod.rs').read_bytes();cm=(SRC/'candidate/mod.rs').read_bytes();t=(SRC/'test-insertion.rs').read_bytes()
assert cm.count(t)==1 and cm.replace(t,b'',1)==bm
start=b.index(b'extern "C" __global__ void up_fold(')
end=b.index(b'\n}\n',start)+4
old=b[start:end]
ref=(SRC/'original-up_fold-reference.cu').read_bytes()
assert ref==b'typedef unsigned int u32;\ntypedef unsigned long long u64;\n#define SENTINEL 0xFFFFFFFFu\n\n'+old.replace(b'void up_fold(',b'void up_fold_reference(',1)
assert ref in t and b not in cm
old_load=b'    for (int j = threadIdx.x; j < nh_o; j += blockDim.x)\n        local_reach[j] = global_reach[j];\n    __syncthreads();\n'
cs=c.index(b'    u32 reach_bits = 0;');ce=c.index(b'    const float* ro = local_reach;',cs)
assert c[:cs]+old_load+c[ce:]==b
assert len(re.findall(rb'extern "C" __global__ void',b))==9
assert re.findall(rb'extern "C" __global__ void [^(]+\([^)]*\)',b)==re.findall(rb'extern "C" __global__ void [^(]+\([^)]*\)',c)
assert cm.count(b'#[test]')==bm.count(b'#[test]')+1 and cm.count(b'#[ignore]')==bm.count(b'#[ignore]')
assert m['gpu_only_unit_inventory']=={'passed':85,'ignored':4,'total':89}
assert t.count(b'.launch(LaunchConfig')==1 and b'block_dim:(128,1,1)' in t and b'grid_dim:(2,1,1)' in t
assert b'arch: Some(arch), ..Default::default()' in t
assert t.count(b'same_int!(')+t.count(b'same_float!(')==14
assert b'assert_eq!(outputs[0],outputs[1]' in t and b'assert_eq!((pairs,launches),(26,52))' in t
names=re.findall(rb'\("([a-z_]+)",\d,',t[t.index(b'let cases = ['):t.index(b'let mut pairs')])
design=read(SRC/'runtime-design.json')
assert [n.decode() for n in names]==[v['name'] for v in design['cases']]
assert len(names)==12 and sum(v['eligible'] for v in design['cases'])==4
hands=[(a,z) for a in range(52) for z in range(a+1,52)];op=hands[:257];own=[op[i] if i%2==0 else hands[257+i] for i in range(129)]
compatible=lambda h,k:not set(h).intersection(op[k])
witness=[sum(compatible(h,128) for h in own),sum(compatible(h,0)!=compatible(h,129) for h in own)]
assert witness==[113,64]
cases=[('zero_positive',[],0x40200000,True),('zero_negative',[],0xc0200000,True),('zero_positive_zero',[],0,True),('zero_negative_zero',[],0x80000000,True),('zero_positive_overflow',[],0x7f800000,False),('zero_negative_overflow',[],0xff800000,False),('zero_nan_payout',[],0x7fc12345,False),('negative_zero_tail',[(256,0x80000000)],0xc0200000,False),('positive_nonzero',[(128,0x3f000000)],0x40200000,False),('signed_cancellation',[(0,0x3f800000),(129,0xbf800000)],0xc0200000,False),('infinite_reach',[(256,0x7f800000)],0x40200000,False),('nan_reach',[(128,0x7fc12345)],0xc0200000,False)]
case_bits=[{'name':n,'reach_nonpositivezero_bits':[[i,f'{w:08x}'] for i,w in vals],'other_reach_words':'00000000','selected_payout_bits':f'{amt:08x}','expected_source_eligibility':elig} for n,vals,amt,elig in cases]
assert [x[0] for x in cases]==[n.decode() for n in names]
report={'id':'E035','verdict':'PASS_SCOPED_SOURCE_REVIEW','independent_source_review_pass':True,'source_manifest_sha256':seal,'candidate_owned_sha256':m['candidate_owned_sha256'],'findings':[],
'proofs':[
'Exact replacement of the new initial load/collective/guarded-store block recovers the complete accepted E020 CUDA bytes. All nine entry signatures, other eight kernels, fallback arithmetic/order, shared declarations and host launch/layout behavior remain unchanged.',
'Each non-exited CTA thread reaches the same collective; b>=count exits whole blocks before it. Bitwise OR covers exactly every logical staged reach word and rejects negative zero, nonzero and nonfinite words. Collective publication is retained. Payout selection and exponent guard are block-uniform; only finite payouts permit the uniform return.',
'Original all-positive-zero card sums, tree total and valid expression yield positive zero. Fast stores use the same selected amount multiplied by positive zero, preserving negative-zero results. Every logical output is written; padding/other rows remain outside the store range. Nonfinite selected payouts retain the exact fallback.',
'Exact removal of the single focused test insertion recovers all accepted mod.rs bytes. Test embeds only the renamed actual original up_fold fragment; fragment bytes match the accepted entry. Both variants compile for actual compute capability with default CompileOptions.',
'The fixed twelve source cases and both players bind the listed input/payout bits. One count-zero pair per player yields26 pairs/52 launches. 257/129 logical lengths,144 stride, nonzero node/list/reach/CFV offsets, excess block, same-hand/SENTINEL branches, poisoned complete outputs and all14 input readbacks are covered. Source-derived nonzero-compatible witnesses count113 and64; these are not executed numerical evidence.',
'All13 source artifacts,7 references and162 accepted checkout entries hash-match. The fixed evaluator is unchanged. One new unignored unit preserves the baseline test declarations, so85 passed/4 ignored is the prospective inventory.'
],
'case_bit_binding':case_bits,
'official_semantics':{'url':'https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/cpp-language-extensions.html#thread-block-synchronization-functions','reviewed_sections':'5.4.4.1; lines639-641,722,770-773 in fetched page','interpretation':'The OR collective retains block synchronization and participating-thread memory ordering while reporting whether any predicate is nonzero. The uniform control path is required.'},
'limits':['Source review only: no compilation, CUDA/native test or performance measurement. The focused original-GPU comparison remains a mandatory future ordinary-unit gate.','Fallback source identity is not a universal NaN payload guarantee or proof of compiled bit equality; the fixed observed cases must pass natively.','D066 reports incidence at retained snapshots, not cost or gains. Every other fold CTA pays predicate work. No acceptance follows from this source pass; separate root authorization and unchanged complete-cycle gates remain required.'],
'reviewer_correction':{'initial_host_check':'AssertionError when extracting original fold through the next entry declaration; this mistakenly included the intervening up_show comment.','correction':'Use the fold closing-brace/newline boundary; reference fragment and unchanged other source now compare exactly. Candidate and test bytes were not modified.','candidate_or_runtime_failure':False},
'input_sha256':pins,'compiler_native_gpu_executed':False,'candidate_accepted':False}
for name,value in [('report.json',report)]:
 p=HERE/name
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
manifest={'id':'E035-source-review','artifact_sha256':{n:sha(HERE/n) for n in ['review.py','report.json']},'source_manifest_sha256':seal}
with (HERE/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({'report':sha(HERE/'report.json'),'manifest':sha(HERE/'manifest.json'),'pins':len(pins)}))