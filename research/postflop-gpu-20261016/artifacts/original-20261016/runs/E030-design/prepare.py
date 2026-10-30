from pathlib import Path
import hashlib,json,difflib,shutil
HERE=Path(__file__).resolve().parent
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
BULK=HERE.parent.parent
ACCEPTED=BULK/'binaries/E020-postflop_autoresearch.manifest.json'
OWNED=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/continuation_capacity.rs','crates/solver/src/game.rs']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b)
def put(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8',newline='') as f:f.write(s)
assert not (HERE/'manifest.json').exists()
assert shutil.disk_usage(HERE).free>=50*1024**3
pins=json.loads(ACCEPTED.read_text(encoding='utf8'))['source_sha256']
assert len(pins)==162
assert all(sha(ROOT/p)==h for p,h in pins.items())
base={p:(ROOT/p).read_bytes().decode('utf8') for p in OWNED}
for p,s in base.items():put(HERE/'base'/p,s)
candidate=dict(base)
p=OWNED[0]
candidate[p]=replace(base[p],
'''    for (int card = threadIdx.x; card < 52; card += blockDim.x) {
        float sum = 0.0;''',
'''    for (int task = threadIdx.x; task < 52; task += blockDim.x) {
        u32 card = card_off[53 + task];
        float sum = 0.0;''')
p=OWNED[1]
s=replace(base[p],'let mut fold_card_off = [Vec::with_capacity(53), Vec::with_capacity(53)];','let mut fold_card_off = [Vec::with_capacity(105), Vec::with_capacity(105)];')
s=replace(s,'            fold_card_off[p].push(fold_card_idx[p].len() as u32);\n        }\n\n        Ok(GpuSolver {','            fold_card_off[p].push(fold_card_idx[p].len() as u32);\n            append_fold_card_order(&mut fold_card_off[p]);\n        }\n\n        Ok(GpuSolver {')
s=replace(s,'/// Per-node offset (-1 = unlocked) plus concatenated locked sigmas.', '''/// Append a card-task permutation without changing offsets or within-card hand order.
fn append_fold_card_order(offsets: &mut Vec<u32>) {
    assert_eq!(offsets.len(), 53);
    assert!(offsets.windows(2).all(|w| w[0] <= w[1]));
    let mut order: [u32; 52] = std::array::from_fn(|card| card as u32);
    order.sort_by_key(|&card| {
        let c = card as usize;
        (std::cmp::Reverse(offsets[c + 1] - offsets[c]), card)
    });
    offsets.extend_from_slice(&order);
}

/// Per-node offset (-1 = unlocked) plus concatenated locked sigmas.''')
s=replace(s,'    fn reach_reuse_solver(storage: crate::store::Storage, algo: Algorithm, compact: bool, menu: &str) -> Solver {','''    #[test]
    fn fold_card_order_preserves_offsets_and_permutation() {
        fn check(counts: [u32; 52], expected: &[u32]) {
            let mut offsets = vec![0u32];
            for count in counts {
                offsets.push(offsets.last().copied().unwrap() + count);
            }
            let original = offsets.clone();
            append_fold_card_order(&mut offsets);
            assert_eq!(offsets.len(), 105);
            assert_eq!(&offsets[..53], original.as_slice());
            assert_eq!(&offsets[53..], expected);
            let mut seen = [false; 52];
            for &card in &offsets[53..] {
                assert!(card < 52 && !seen[card as usize]);
                seen[card as usize] = true;
                let c = card as usize;
                assert_eq!(offsets[c + 1] - offsets[c], counts[c]);
            }
            assert!(seen.into_iter().all(|v| v));
        }
        let ascending: Vec<u32> = (0..52).collect();
        check([0; 52], &ascending); // no hands: every zero-length card is still assigned
        check([51; 52], &ascending); // complete two-card deck: all lengths tie
        let mut counts = [0; 52];
        for [a, b] in [[0, 1], [0, 2], [0, 3], [1, 2], [50, 51]] {
            counts[a] += 1;
            counts[b] += 1;
        }
        let expected: Vec<u32> = [0, 1, 2, 3, 50, 51].into_iter().chain(4..50).collect();
        check(counts, &expected); // unequal lengths, positive ties and zero ties
        assert_eq!(crate::game::GPU_FOLD_CARD_TASK_BYTES, 2 * 52 * 4);
    }

    fn reach_reuse_solver(storage: crate::store::Storage, algo: Algorithm, compact: bool, menu: &str) -> Solver {''')
candidate[p]=s
p=OWNED[2]
s=replace(base[p],'    /// Total bytes of GPU staging (reach + cfv) this plan needs.','    /// GPU staging (reach + cfv) plus immutable fold-card task IDs for admission.')
s=replace(s,'            + self.cfv_blocks as u64 * self.nh_max as u64) * 4\n','            + self.cfv_blocks as u64 * self.nh_max as u64) * 4\n            + crate::game::GPU_FOLD_CARD_TASK_BYTES\n')
s=replace(s,'                assert_eq!(plan.cfv_slot[0], 0);','''                assert_eq!(plan.cfv_slot[0], 0);
                let scratch = ((plan.reach_blocks[0] * plan.nh[0]
                    + plan.reach_blocks[1] * plan.nh[1]
                    + plan.cfv_blocks * plan.nh_max) * std::mem::size_of::<f32>()) as u64;
                assert_eq!(plan.staging_bytes() - scratch, 416);
                let full_arenas = (spot.tree.data_size[0] + spot.tree.data_size[1]) * 8;
                assert!(spot.vram_estimate_bytes()
                    >= plan.staging_bytes() + full_arenas + 512 * 1024 * 1024);''')
candidate[p]=s
p=OWNED[3]
candidate[p]=replace(base[p],'    n+(p.num_nodes*8) as u64+4+12+(4*p.nh_max*4) as u64 // unlocked table, sigma, discounts, eval roots','''    // The original 53 offsets per player above are followed by 52 task IDs.
    n+crate::game::GPU_FOLD_CARD_TASK_BYTES+(p.num_nodes*8) as u64+4+12+(4*p.nh_max*4) as u64 // unlocked table, sigma, discounts, eval roots''')
p=OWNED[4]
s=replace(base[p],'#[derive(Debug, Clone)]\npub struct HandInfo {','''/// Two immutable 52-card GPU task permutations, appended to the fold offsets.
pub(crate) const GPU_FOLD_CARD_TASK_BYTES: u64 = 2 * 52 * 4;

#[derive(Debug, Clone)]
pub struct HandInfo {''')
s=replace(s,'        staging + arenas + 512 * 1024 * 1024','        staging + arenas + GPU_FOLD_CARD_TASK_BYTES + 512 * 1024 * 1024')
candidate[p]=s
patch=''
for p in OWNED:
 put(HERE/'candidate'/p,candidate[p])
 patch+=''.join(difflib.unified_diff(base[p].splitlines(keepends=True),candidate[p].splitlines(keepends=True),fromfile='a/'+p,tofile='b/'+p))
put(HERE/'candidate.patch',patch)
print(json.dumps({'owned':OWNED,'candidate_sha256':{p:sha(HERE/'candidate'/p) for p in OWNED},'patch_sha256':sha(HERE/'candidate.patch')},indent=2))
