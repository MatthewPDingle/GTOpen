from pathlib import Path
import difflib,hashlib
out=Path(__file__).parent
base_path=out.parent/'live-terminal-work'/'kernels.cu'
base=base_path.read_text(encoding='utf-8')
c=base
def replace(old,new):
    global c
    assert c.count(old)==1,(old[:100],c.count(old))
    c=c.replace(old,new)
replace('    u32 h, int nopponents, const u32* opponent_slots, const float* cdf,',
        '    u32 h, int nopponents, const size_t* opponent_bases, const float* cdf,')
replace('    u32 sample_start, u32 sample_count, u32 batch_capacity)\n{\n    float sum = 0.f;',
        '    u32 sample_start, u32 sample_count)\n{\n    float sum = 0.f;')
replace('            size_t base = ((size_t)opponent_slots[q] * batch_capacity + local) * (NC + 1);',
        '            size_t base = opponent_bases[q] + (size_t)local * (NC + 1);')
replace('    __shared__ u32 opponent_slots[9];','    __shared__ size_t opponent_bases[9];')
replace('''                opponent_slots[nopponents++] = compact
                    ? compact_slots[(size_t)p * union_slots + global_slot] : global_slot;''',
'''                u32 cdf_slot = compact
                    ? compact_slots[(size_t)p * union_slots + global_slot] : global_slot;
                // Batch-invariant CDF origin, in float elements. Cast before
                // multiplying: large union/compact caches exceed 32-bit offsets.
                opponent_bases[nopponents++] = (size_t)cdf_slot * batch_capacity * (NC + 1);''')
old='(h, nopponents, opponent_slots, cdf, lower, upper, sample_start, sample_count, batch_capacity)'
assert c.count(old)==4,c.count(old)
c=c.replace(old,'(h, nopponents, opponent_bases, cdf, lower, upper, sample_start, sample_count)')
rel='crates/solver/src/preflop/kernels.cu'
patch=''.join(difflib.unified_diff(base.splitlines(True),c.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(out/'cdf-base.patch').write_text(patch,encoding='utf-8',newline='\n')
(out/'kernels.cu').write_bytes(c.replace('\n','\r\n').encode('utf-8'))
(out/'base.txt').write_text(str(base_path)+'\n'+hashlib.sha256(base_path.read_bytes()).hexdigest()+'\n',encoding='utf-8')
# Address arithmetic only: independent range-edge checks, no solver or GPU work.
cases=0
for slot in [0,1,388081,760577,2**31,2**32-1]:
    for capacity in [1,7,32,1024]:
        for local in {0,capacity-1}:
            for rank in [0,1,169]:
                old=((slot*capacity)+local)*170+rank
                new=slot*capacity*170+local*170+rank
                assert old==new and new<2**64
                cases+=1
print(f'Kernel-only proposal written; {cases} pure-integer address edge checks passed.')
