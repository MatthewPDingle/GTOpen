"""Preserve a source-only next lead, with no candidate or new observations."""
from pathlib import Path
import json
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
p=R/'runs/D134-zero-init-fences-r2/report.json';q=old.read(p)
rows=[]
for name,v in q['frames'].items():
    if Path(name).parent.name!='B1':continue
    fields=v['fields'];arena=[fields[f'arena-{i}-0']['words']for i in range(2)]
    rows.append({'frame':name,'frame_sha256':v['sha256'],'per_player_float_arena_words':arena,
        'current_host_pinned_staging_bytes':max(arena)*4})
assert len(rows)==3
note={'at':old.now(),'status':'source_only_unimplemented_next_lead',
    'lead':'Bound host pinned staging and stream complete-node transfer groups serially',
    'source_sha256':{n:old.BASE[n]for n in ['crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/arena.rs']},
    'accepted_source_facts':['Constructor allocates cached page-locked max(plan.arena_elements)float words before uploads.','Fresh zero compressed uploads do not need the staging image, but final full readback reuses it.','Warm compressed uploads currently decode a whole arena into staging. Compact inactive snapshots and full/F32 layouts need exact preservation.','Per-node quantization needs each full node vector to retain its original scale/encoding.'],
    'retained_actual_geometry_report_sha256':old.sha(p),'retained_actual_geometries':rows,
    'distinct_hypothesis':'Reduce actual pinned allocation size and use one serial bounded staging window for complete-node uploads/readbacks. Unlike closedE040, no two-window overlap/pipeline/work scheduling variation. This needs separate admission and must not compose or tune E040.',
    'risks':['More DMA submissions/stream waits and transfer descriptors may erase allocation/cache benefits.','Extra persistent metadata and all-thread CPU cost must be measured.','Accepted E080 overlaps existing allocation/setup with zero checks, so isolated allocation spans are not removable complete-cycle headroom.','Warm/F32/full/compact/inactive/materialization/state/error paths require full exact control; no fresh-zero-only fixture exemption.'],
    'next_action':'Audit closed history and existing transfer layout for a distinct fixed bounded-allocation form; freeze source/equivalence/component and actual material gates before any implementation/native process. No candidate/source/timing exists here.',
    'new_native_processes':0,'candidate_accepted':False,
    'limits':'Retained actual geometry and current source facts only; no predicted gain, current headroom, tested bounded allocation or performance result.'}
out=R/'runs/E086-turn-checkpoint/next-source-lead.json';old.save(out,note)
print(json.dumps({'source_only_geometry':rows,'new_native_processes':0}),flush=True)
