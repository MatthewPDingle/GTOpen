from pathlib import Path
import hashlib, json, difflib

HERE=Path(__file__).resolve().parent
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
BULK=HERE.parents[1]
owned=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/continuation_capacity.rs','crates/solver/src/game.rs']
pins=json.loads((BULK/'binaries/E020-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))['source_sha256']
sha=lambda b:hashlib.sha256(b).hexdigest()
for rel,h in pins.items():
    assert sha((ROOT/rel).read_bytes())==h,rel
base={r:(ROOT/r).read_bytes().decode('utf-8') for r in owned}
c=base.copy()
def change(r,old,new,count=1):
    assert c[r].count(old)==count,(r,c[r].count(old),old)
    c[r]=c[r].replace(old,new)

p=owned[2]
change(p,'    pub riv_sorted_idx: [Vec<u32>; 2],','''    pub riv_sorted_idx: [Vec<u32>; 2],
    /// Exact complement per slot, in ascending root-hand order. Slot s starts
    /// at s*nh[p]-riv_off[p][s] and has nh[p]-riv_cnt[p][s] entries.
    pub riv_missing_idx: [Vec<u32>; 2],''')
change(p,'impl GpuPlan {','''// The root range contains at most C(52,2) distinct two-card hands. Keep
// construction scratch on the stack; no extra heap allocation per river slot.
fn append_river_missing(
    nh: usize, slot: usize, present_start: usize, present: &[u32], missing: &mut Vec<u32>,
) {
    let mut seen = [false; 1326];
    assert!(nh <= seen.len());
    let start = slot.checked_mul(nh).and_then(|n| n.checked_sub(present_start))
        .expect("river complement offset");
    assert_eq!(missing.len(), start);
    let count = nh.checked_sub(present.len()).expect("river hand count");
    let end = start.checked_add(count).expect("river complement length");
    for &index in present {
        let index = index as usize;
        assert!(index < nh && !seen[index], "river hand indices must be unique and in range");
        seen[index] = true;
    }
    missing.extend((0..nh).filter(|&i| !seen[i]).map(|i| i as u32));
    assert_eq!(missing.len(), end);
}

impl GpuPlan {''')
change(p,'        let mut riv_sorted_idx = [Vec::new(), Vec::new()];','''        let mut riv_sorted_idx = [Vec::new(), Vec::new()];
        let mut riv_missing_idx = [Vec::new(), Vec::new()];''')
change(p,'            for &key in &slots {','            for (slot, &key) in slots.iter().enumerate() {')
change(p,'                riv_off[p].push(riv_sorted_idx[p].len() as u32);','''                let present_start = riv_sorted_idx[p].len();
                riv_off[p].push(u32::try_from(present_start).expect("river sorted offset"));''')
change(p,'                for c in 0..52 {','''                append_river_missing(nh[p], slot, present_start,
                    &riv_sorted_idx[p][present_start..], &mut riv_missing_idx[p]);
                for c in 0..52 {''')
change(p,'            riv_sorted_idx,','            riv_sorted_idx,\n            riv_missing_idx,')
change(p,'    /// Total bytes of GPU staging (reach + cfv) this plan needs.','''    /// Immutable complement payload, included once in admission alongside staging.
    pub fn showdown_missing_bytes(&self) -> u64 {
        // Empty lists own one unused u32 so no zero-byte allocation is needed.
        self.riv_missing_idx.iter().map(|v| v.len().max(1) as u64 * 4).sum()
    }

    /// Reach/CFV staging plus immutable showdown-complement payload. Existing
    /// admission callers use this total once; continuation metadata accounts
    /// for the complement separately from its seven mutable workspace buffers.''')
change(p,'            + self.cfv_blocks as u64 * self.nh_max as u64) * 4','            + self.cfv_blocks as u64 * self.nh_max as u64) * 4\n            + self.showdown_missing_bytes()')
change(p,'    fn river_bounds_match_strength_comparisons() {','''    fn river_bounds_match_strength_comparisons() {
        // Full, empty and mixed slots share one flattened coordinate system.
        // Include nonzero starts and a zero-hand plan without a CUDA allocation.
        let mut missing = Vec::new();
        append_river_missing(4, 0, 0, &[3, 1, 0, 2], &mut missing);
        assert!(missing.is_empty());
        append_river_missing(4, 1, 4, &[], &mut missing);
        assert_eq!(missing, [0, 1, 2, 3]);
        append_river_missing(4, 2, 4, &[2, 0], &mut missing);
        assert_eq!(missing, [0, 1, 2, 3, 1, 3]);
        append_river_missing(4, 3, 6, &[1, 3, 0, 2], &mut missing);
        assert_eq!(missing.len(), 6);
        append_river_missing(0, 0, 0, &[], &mut Vec::new());
        for present in [&[1, 1][..], &[4][..]] {
            assert!(std::panic::catch_unwind(|| {
                append_river_missing(4, 0, 0, present, &mut Vec::new());
            }).is_err());
        }''')
change(p,'                assert_eq!(plan.cfv_slot[0], 0);','''                assert_eq!(plan.cfv_slot[0], 0);
                let missing_bytes = plan.riv_missing_idx.iter().map(|v| v.len().max(1) as u64 * 4).sum::<u64>();
                assert_eq!(plan.showdown_missing_bytes(), missing_bytes);
                let workspace = (plan.reach_blocks[0] as u64 * plan.nh[0] as u64
                    + plan.reach_blocks[1] as u64 * plan.nh[1] as u64
                    + plan.cfv_blocks as u64 * plan.nh_max as u64) * 4;
                assert_eq!(plan.staging_bytes(), workspace + missing_bytes);
                let all_slot_missing = (0..2).map(|p| {
                    spot.river.entries.iter().flatten()
                        .map(|r| plan.nh[p] - r.sorted[p].len()).sum::<usize>().max(1) as u64 * 4
                }).sum::<u64>();
                assert!(all_slot_missing >= missing_bytes);
                assert!(spot.vram_estimate_bytes() >= plan.staging_bytes()
                    + (spot.tree.data_size[0] + spot.tree.data_size[1]) * 8 + 512 * 1024 * 1024);''')
change(p,'                        let ob = plan.riv_off[1 - p][slot] as usize;','''                        let missing_start = slot * plan.nh[p] - start;
                        let missing_end = missing_start + plan.nh[p] - (end - start);
                        let absent = &plan.riv_missing_idx[p][missing_start..missing_end];
                        assert!(absent.windows(2).all(|w| w[0] < w[1]));
                        let mut coverage = vec![0u8; plan.nh[p]];
                        for &i in plan.riv_sorted_idx[p][start..end].iter().chain(absent) {
                            assert!((i as usize) < plan.nh[p]);
                            coverage[i as usize] += 1;
                        }
                        assert!(coverage.iter().all(|&n| n == 1));
                        if slot + 1 == plan.num_slots {
                            assert_eq!(missing_end, plan.riv_missing_idx[p].len());
                        }
                        let ob = plan.riv_off[1 - p][slot] as usize;''')

k=owned[0]
change(k,'    const u32* __restrict__ p_idx,','    const u32* __restrict__ p_idx, const u32* __restrict__ p_missing_idx,')
change(k,'''    // zero my full cfv span (hands missing from this river's sorted list stay 0)
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x)
        cfv[(u64)cfv_slot[n] * nh_max + i] = 0.f;''','''    // Present hands receive their original final output below; zero only
    // the exact complement. Host construction validates this derived span.
    int m_p = p_cnt[slot];
    u32 pb = p_off[slot];
    u64 missing_start = (u64)slot * nh_p - pb;
    for (int k = threadIdx.x; k < nh_p - m_p; k += blockDim.x) {
        u32 i = p_missing_idx[missing_start + k];
        cfv[(u64)cfv_slot[n] * nh_max + i] = 0.f;
    }''')
change(k,'''    int m_p = p_cnt[slot];
    u32 pb = p_off[slot];
    for (int k = threadIdx.x; k < m_p; k += blockDim.x) {''','''    for (int k = threadIdx.x; k < m_p; k += blockDim.x) {''')

m=owned[1]
change(m,'    d_riv_idx: [CudaSlice<u32>; 2],','''    d_riv_idx: [CudaSlice<u32>; 2],
    d_riv_missing_idx: [CudaSlice<u32>; 2],''')
change(m,'        let upi32 = |v: &Vec<i32>| stream.clone_htod(v).map_err(e);','''        let up_missing = |v: &Vec<u32>| {
            if v.is_empty() { stream.alloc_zeros::<u32>(1).map_err(e) } else { up32(v) }
        };
        let upi32 = |v: &Vec<i32>| stream.clone_htod(v).map_err(e);''')
change(m,'            d_riv_idx: [up32(&plan.riv_sorted_idx[0])?, up32(&plan.riv_sorted_idx[1])?],','''            d_riv_idx: [up32(&plan.riv_sorted_idx[0])?, up32(&plan.riv_sorted_idx[1])?],
            d_riv_missing_idx: [up_missing(&plan.riv_missing_idx[0])?, up_missing(&plan.riv_missing_idx[1])?],''')
change(m,'                        .arg(&self.d_riv_idx[p])','''                        .arg(&self.d_riv_idx[p])
                        .arg(&self.d_riv_missing_idx[p])''',2)

a=owned[3]
change(a,'+bytes(&p.riv_cnt[q])+bytes(&p.riv_sorted_idx[q])+bytes(&p.riv_lower[q])','+bytes(&p.riv_cnt[q])+bytes(&p.riv_sorted_idx[q])+(p.riv_missing_idx[q].len().max(1)*4) as u64+bytes(&p.riv_lower[q])')
change(a,'d_riv_cnt:u32,d_riv_idx:u32,d_riv_lower:u32,','d_riv_cnt:u32,d_riv_idx:u32,d_riv_missing_idx:u32,d_riv_lower:u32,')

g=owned[4]
change(g,'        staging + arenas + 512 * 1024 * 1024','''        // Every available river slot conservatively covers the GPU's visited
        // subset for either isomorphism setting. These immutable u32 lists
        // contain exactly the root hands absent from each sorted list.
        // Each entirely empty list owns one unused u32, matching GPU upload.
        let missing_bytes = [nh0, nh1].into_iter().enumerate().map(|(p, nh)| {
            self.river.entries.iter().flatten()
                .map(|r| nh.checked_sub(r.sorted[p].len() as u64).expect("river hand count"))
                .sum::<u64>().max(1) * 4
        }).sum::<u64>();
        staging + arenas + missing_bytes + 512 * 1024 * 1024''')

patch=''
for r in owned:
    for sub,s in [('base',base[r]),('candidate',c[r])]:
        f=HERE/sub/r;f.parent.mkdir(parents=True,exist_ok=True)
        f.write_bytes(s.encode('utf-8'))
    patch+=''.join(difflib.unified_diff(base[r].splitlines(True),c[r].splitlines(True),fromfile='a/'+r,tofile='b/'+r))
(HERE/'candidate.patch').write_bytes(patch.encode('utf-8'))
print(json.dumps({'candidate_sha256':{r:sha(c[r].encode('utf-8')) for r in owned},'patch_sha256':sha(patch.encode('utf-8'))}))
