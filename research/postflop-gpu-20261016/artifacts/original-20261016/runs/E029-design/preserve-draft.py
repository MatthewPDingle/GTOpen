from pathlib import Path
import hashlib,json,difflib
h=Path(__file__).resolve().parent
owned=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/continuation_capacity.rs','crates/solver/src/game.rs']
c={r:(h/'candidate'/r).read_text(encoding='utf-8') for r in owned}
def r(path,a,b):
    assert c[path].count(a)==1,(path,a)
    c[path]=c[path].replace(a,b)
r(owned[1],'''        let up_missing = |v: &Vec<u32>| {
            if v.is_empty() { stream.alloc_zeros::<u32>(1).map_err(e) } else { up32(v) }
        };
''','')
r(owned[1],'d_riv_missing_idx: [up_missing(&plan.riv_missing_idx[0])?, up_missing(&plan.riv_missing_idx[1])?]','d_riv_missing_idx: [up32(&plan.riv_missing_idx[0])?, up32(&plan.riv_missing_idx[1])?]')
r(owned[2],'''        // Empty lists own one unused u32 so no zero-byte allocation is needed.
        self.riv_missing_idx.iter().map(|v| v.len().max(1) as u64 * 4).sum()''','        self.riv_missing_idx.iter().map(|v| v.len() as u64 * 4).sum()')
r(owned[2],'let missing_bytes = plan.riv_missing_idx.iter().map(|v| v.len().max(1) as u64 * 4).sum::<u64>();','let missing_bytes = plan.riv_missing_idx.iter().map(|v| v.len() as u64 * 4).sum::<u64>();')
r(owned[2],'''                let all_slot_missing = (0..2).map(|p| {
                    spot.river.entries.iter().flatten()
                        .map(|r| plan.nh[p] - r.sorted[p].len()).sum::<usize>().max(1) as u64 * 4
                }).sum::<u64>();''','''                let all_slot_missing = spot.river.entries.iter().flatten().map(|r| {
                    ((plan.nh[0] - r.sorted[0].len()) + (plan.nh[1] - r.sorted[1].len())) as u64 * 4
                }).sum::<u64>();''')
r(owned[3],'(p.riv_missing_idx[q].len().max(1)*4) as u64','bytes(&p.riv_missing_idx[q])')
r(owned[4],'''        // Each entirely empty list owns one unused u32, matching GPU upload.
        let missing_bytes = [nh0, nh1].into_iter().enumerate().map(|(p, nh)| {
            self.river.entries.iter().flatten()
                .map(|r| nh.checked_sub(r.sorted[p].len() as u64).expect("river hand count"))
                .sum::<u64>().max(1) * 4
        }).sum::<u64>();''','''        let missing_bytes = self.river.entries.iter().flatten().map(|r| {
            (nh0.checked_sub(r.sorted[0].len() as u64).expect("river hand count")
                + nh1.checked_sub(r.sorted[1].len() as u64).expect("river hand count")) * 4
        }).sum::<u64>();''')
expected=['bf865236270454e13fb7dd2deaf85146310aa364abbc47e00df47bcb0a391841','a6ac37131f1709622456240d0fc14b90bd7fc13df4043619bc517974598db666','6edaf24356db94368e679f9dd20f0140c44d774e705898acff1446c7f945cfc9','06546319d86c9b0f355cec69cef3e385a7cb413432a629d30622d84cc74fe8b3','4e0cd3ce84a1dd5dfa3789f8d53603b1d71754bcc649f722ad65fa4ece10ab33']
sha=lambda b:hashlib.sha256(b).hexdigest()
patch=''
for path,want in zip(owned,expected):
    assert sha(c[path].encode())==want,path
    patch+=''.join(difflib.unified_diff((h/'base'/path).read_text(encoding='utf-8').splitlines(True),c[path].splitlines(True),fromfile='a/'+path,tofile='b/'+path))
assert sha(patch.encode())=='ac341f00671f1d72766c616a130011417e289374d3f63e9a079668323f74c758'
d=h/'draft-r1';d.mkdir(exist_ok=False)
(d/'candidate.patch').write_bytes(patch.encode())
(d/'preservation.json').write_text(json.dumps({'status':'unused_preseal_draft','patch_sha256':sha(patch.encode()),'candidate_sha256':dict(zip(owned,expected)),'note':'Reconstructed exact already-recorded draft1 bytes, hash verified, before final seal. Final candidate adds explicitly accounted one-word ownership for empty complement buffers; no numerical or runtime sample was executed.'},indent=2)+'\n',encoding='utf-8')
print('Draft1 exact patch preserved: '+sha(patch.encode()))
