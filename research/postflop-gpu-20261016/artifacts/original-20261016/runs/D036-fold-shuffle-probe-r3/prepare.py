"""Preparation only: immutable source/corpus generation. No compiler or CUDA calls."""
from pathlib import Path
import difflib, hashlib, json, math, struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DESIGN = ROOT / 'runs/D036-fold-shuffle-design'
OLD = ROOT / 'runs/D031-child-slot-probe'

def sha(data): return hashlib.sha256(data).hexdigest()
def save(name, data):
    with (HERE/name).open('xb') as f: f.write(data)
def js(name, value): save(name, (json.dumps(value, indent=2, allow_nan=False)+'\n').encode())
def bits(value): return struct.unpack('<I', struct.pack('<f', value))[0]
def fnv(data):
    h = 0xcbf29ce484222325
    for b in data: h = ((h ^ b) * 0x100000001b3) & ((1 << 64)-1)
    return f'{h:016x}'

baseline = (DESIGN/'source/kernels.cu').read_bytes()
assert sha(baseline) == '8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0'
text = baseline.decode()
fold_begin = text.index('extern "C" __global__ void up_fold(')
fold_end = text.index('// Up sweep, showdown terminals:', fold_begin)
old = '''    for (int step = blockDim.x >> 1; step > 0; step >>= 1) {
        if (threadIdx.x < (u32)step)
            total_parts[threadIdx.x] += total_parts[threadIdx.x + step];
        __syncthreads();
    }
'''
new = '''    if (blockDim.x == 128 && blockDim.y == 1 && blockDim.z == 1) {
        for (int step = 64; step >= 32; step >>= 1) {
            if (threadIdx.x < (u32)step)
                total_parts[threadIdx.x] += total_parts[threadIdx.x + step];
            __syncthreads();
        }
        if (threadIdx.x < 32) {
            float v = total_parts[threadIdx.x];
            for (int step = 16; step > 0; step >>= 1) {
                float rhs = __shfl_down_sync(0xffffffffu, v, step);
                if (threadIdx.x < (u32)step) v = v + rhs;
            }
            if (threadIdx.x == 0) total_parts[0] = v;
        }
        __syncthreads();
    } else {
''' + ''.join('    '+line+'\n' for line in old.rstrip('\n').splitlines()) + '    }\n'
fold = text[fold_begin:fold_end]
assert fold.count(old) == 1
candidate = (text[:fold_begin] + fold.replace(old, new) + text[fold_end:]).encode()
save('baseline.cu', baseline)
save('candidate.cu', candidate)
save('candidate.patch', ''.join(difflib.unified_diff(text.splitlines(True), candidate.decode().splitlines(True), fromfile='baseline.cu', tofile='candidate.cu')).encode())

# The supplementary oracle copies the original partial and reduction body verbatim.
partial_start = fold.index('    float partial = 0.0;')
partial_end = fold.index('    float T = total_parts[0];')
raw_header = '''// Supplementary raw-total exposure only; full up_fold is authoritative.
typedef unsigned int u32;
extern "C" __global__ void raw_total(const float* data, const u32* offsets,
    const u32* lengths, u32 count, u32* out) {
    u32 b = blockIdx.x;
    if (b >= count) return;
    int nh_o = lengths[b];
    const float* ro = data + offsets[b];
    __shared__ float total_parts[256];
'''
raw_tail = '    if (threadIdx.x == 0) out[2 + b * 3] = __float_as_uint(total_parts[0]);\n}\n'
raw_base = raw_header + fold[partial_start:partial_end] + raw_tail
raw_candidate = raw_header + fold.replace(old,new)[partial_start:fold.replace(old,new).index('    float T = total_parts[0];')] + raw_tail
save('raw-baseline.cu', raw_base.encode())
save('raw-candidate.cu', raw_candidate.encode())

lengths = [0,1,31,32,33,63,64,65,127,128,129,255,256,257,319,1326]
patterns = ['positive_zero','negative_zero','mixed_zero','ones','realistic_sparse',
            'random_exponents','rounding_boundary','subnormal','min_normal_edge',
            'tiny_large','alternating_cancellation','negative_finite','lane_boundary','finite_overflow']
seed = 0xd036_2026_1016_5eed
def values(n, pattern, salt):
    state = (seed ^ (n<<24) ^ (salt<<8) ^ patterns.index(pattern)) & ((1<<64)-1)
    result=[]
    for i in range(n):
        state ^= state >> 12; state ^= (state << 25) & ((1<<64)-1); state ^= state >> 27
        r = (state * 0x2545f4914f6cdd1d) & ((1<<64)-1)
        if pattern=='positive_zero': v=0
        elif pattern=='negative_zero': v=0x80000000
        elif pattern=='mixed_zero': v=0x80000000 if i%2 else 0
        elif pattern=='ones': v=bits(1.0)
        elif pattern=='realistic_sparse': v=0 if r%5==0 else bits((r%65537)/65536.0)
        elif pattern=='random_exponents': v=((80+r%61)<<23) | ((r>>16)&0x7fffff)
        elif pattern=='rounding_boundary': v=[0x3f800000,0x33800000,0x33800001,0x3f800001,0x33000000][i%5]
        elif pattern=='subnormal': v=[1,2,0x7fffff,0x800001,0x80000001,0][i%6]
        elif pattern=='min_normal_edge': v=[0x800000,0x7fffff,1,0x800001,0x80800000][i%5]
        elif pattern=='tiny_large': v=[0x5d800000,0x00800000,0x3f800000,1][i%4]
        elif pattern=='alternating_cancellation': v=[0x4b800000,0x3f800000,0xcb800000,0xbf800000,0x33800000][i%5]
        elif pattern=='negative_finite': v=bits(-((r%4096)+1)/4096.0)
        elif pattern=='lane_boundary': v=bits(1.0) if i%32 in [0,15,16,31] else bits(2**-24)
        else: v=0x7f7fffff
        assert ((v>>23)&255)!=255
        result.append(v)
    return result

# Overflow is a separately reported domain: observed GPU output bits still must
# match exactly, but no CPU nonfinite-payload or general NaN-input guarantee follows.
hands=[(a,b) for a in range(52) for b in range(a+1,52)]
assert len(hands)==1326 and math.gcd(997,1326)==1 and math.gcd(577,1326)==1
guard=0x4b123456
raw=[]
scenarios=[]
for index,n in enumerate(lengths):
    own_count={0:1,1:33,257:319,319:257,1326:1326}.get(n,[1,33,129,257][index%4])
    for pattern in patterns:
        raw.append({'id':f'n{n}-{pattern}', 'required':pattern!='finite_overflow', 'bits':values(n,pattern,0)})
    opp=[hands[(i*997+17)%1326] for i in range(n)]
    own=[hands[(i*577+17)%1326] for i in range(own_count)]
    lookup={h:i for i,h in enumerate(opp)}
    card_idx=[]; card_off=[0]
    for card in range(52):
        card_idx.extend(i for i,h in enumerate(opp) if card in h)
        card_off.append(len(card_idx))
    assert len(card_idx)==2*n
    nh_max=max(n,own_count)+7
    n_nodes=len(patterns)*4
    # A bijection over physical nodes, with guard node IDs outside the launch.
    order=list(reversed(range(n_nodes)))
    rsrc0=[2*i+1 for i in range(n_nodes)]
    rsrc1=[2*(n_nodes-1-i)+1 for i in range(n_nodes)]
    slots=[2*((i*5)%n_nodes)+1 for i in range(n_nodes)]
    assert len(set(slots))==n_nodes
    reach0=[guard]*max(1,((2*n_nodes+1)*n))
    reach1=reach0.copy()
    nodes_meta=[]
    for i in range(n_nodes):
        pattern=patterns[i//4]
        a=values(n,pattern,i%4)
        b=list(reversed(a))
        reach0[rsrc0[i]*n:rsrc0[i]*n+n]=a
        reach1[rsrc1[i]*n:rsrc1[i]*n+n]=b
        nodes_meta.append({'pattern':pattern,'required':pattern!='finite_overflow','owner':i%2,
                           'twin_bits':[bits(1),bits(3.25),bits(78.5),bits(0)][i%4],
                           'tlose_bits':[bits(-1),bits(-2.5),bits(-41.75),bits(-0.0)][i%4]})
    scenarios.append({'id':f'n{n}-own{own_count}','nh_o':n,'nh_p':own_count,'nh_max':nh_max,
        'nodes':[0xffffffff,0xfffffffe]+order+[0xfffffffd], 'start':2,'count':n_nodes,
        'node_meta':nodes_meta,'rsrc0':rsrc0,'rsrc1':rsrc1,'cfv_slot':slots,
        'reach0_bits':reach0,'reach1_bits':reach1,'pc1':[a for a,b in own],
        'pc2':[b for a,b in own], 'same_p':[lookup.get(h,0xffffffff) for h in own],
        'opponent_hands':opp,'own_hands':own,'card_off':card_off,'card_idx':card_idx,
        'cfv_words':(2*n_nodes+1)*nh_max})
# Explicit zero-own-hands case retains real opponent inputs and checks no writes.
empty=dict(scenarios[-2]); empty.update(id='n319-own0', nh_p=0, pc1=[], pc2=[], same_p=[], own_hands=[])
scenarios.append(empty)
js('corpus.json', {'schema':1,'seed_hex':hex(seed),'guard_bits':guard,'lengths':lengths,
   'patterns':patterns,'blocks':[128,16,32,64,256], 'required_patterns':patterns[:-1],
   'raw_cases':raw,'full_scenarios':scenarios,'source':'deterministic constructed poker hand lists and reach bits; not solver timing'})
for name in ['run.py','probe.rs']:
    assert (HERE/name).exists(), f'Write {name} before preparing generated inputs'
save('runner-primitives-source.py',(OLD/'runner-primitives-source.py').read_bytes())
js('source-checks.json', {'accepted_kernel_sha256':sha(baseline), 'candidate_kernel_sha256':sha(candidate),
    'outside_up_fold_unchanged':True,'only_reduction_replaced':True,'original_reduction_occurrences_in_up_fold':1,
    'fallback_original_loop_verbatim_after_indentation':True,
    'raw_partial_reduction_extracted_from_exact_full_kernel':True,
    'required_lengths':lengths,'patterns':patterns,'raw_cases':len(raw),'full_scenarios':len(scenarios),
    'full_node_count_per_scenario':len(patterns)*4, 'full_pair_cases':len(scenarios)*2*5+2*5,
    'proof_domain':'All observed GPU bits exact including overflow; finite-domain cases additionally must remain finite; no NaN/Inf inputs',
    'builds_executed':0,'gpu_calls_executed':0,'production_edits':0})
js('source-variants.json',{v:{'sha256':sha((HERE/f'{v}.cu').read_bytes()),
    'fnv1a64':fnv((HERE/f'{v}.cu').read_bytes()),'bytes':(HERE/f'{v}.cu').stat().st_size}
    for v in ['baseline','candidate','raw-baseline','raw-candidate']})
print(json.dumps({'prepared_sources_and_corpus':True,'directory':str(HERE),'raw_cases':len(raw),'full_scenarios':len(scenarios)}))
