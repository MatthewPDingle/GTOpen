import json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
OLD=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not any((ROOT/x).exists() for x in ['gpu-run.lock','epoch-sequence.lock'])
H=ROOT/'runs/D191-node-record-history';H.mkdir(exist_ok=False)
commands=[
    ['git','log','--all','--format=%h %s','-G','NodeFields|NodeMeta|node_fields|node_meta|interleav|array.of.struct','--','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu'],
    ['rg','-n','-i','-m','2','NodeFields|NodeMeta|node_fields|node_meta|array.of.struct|interleav.{0,40}node',str(OLD/'runs'),'--glob','*.rs','--glob','*.cu','--glob','*review*.json','--glob','*.md'],
]
results=[]
for command in commands:
    p=subprocess.run(command,cwd=h.REPO,capture_output=True,text=True,encoding='utf-8')
    assert p.returncode in [0,1]
    results.append({'command':command,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
assert not results[0]['stdout'].strip()
hits=results[1]['stdout'].splitlines()
assert all('scenario["node_meta"]' in x or 'fn node_metadata_follows_limp_band_defense_contextual_and_point_lock_precedence()' in x for x in hits)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
original_ledger=ledger.read_text(encoding='utf-8')
sections={}
for heading,next_heading in [('## D076 bounded packing; E046 resource rejection','## D077 one-action routing'),('### E070 packed byte metadata integrated initial screen','### D115 and E071 parallel CPU planner')]:
    assert heading in original_ledger and next_heading in original_ledger
    sections[heading]=original_ledger.split(heading,1)[1].split(next_heading,1)[0]
h.save(H/'history.json',{'at':h.now(),'bounded_queries':results,'literal_hit_classification':'Fold harness JSON schema names and unrelated preflop model-test names only. Literal searches do not establish mechanism novelty; E046/E070 were found by semantic ledger review.','closed_family_ledger_sections':sections})
mod=h.REPO/'crates/solver/src/gpu/mod.rs';src=mod.read_text(encoding='utf-8')
fields=['d_node_player','d_node_na','d_node_children_start','d_node_twin','d_node_tlose','d_node_ttie','d_node_cdiv','d_node_river_slot','d_cc_start','d_cc_count','d_cfv_slot']
for field in fields:assert re.search(r'\b'+field+r': CudaSlice<(?:i32|u32|f32)>',src)
assert 'd_rsrc: [CudaSlice<u32>; 2]' in src and 'd_node_data_off: CudaSlice<u64>' in src
inputs=[mod,h.REPO/'crates/solver/src/gpu/kernels.cu',h.REPO/'crates/solver/src/gpu/plan.rs',OLD/'runs/E046-resource/report.json',OLD/'runs/E070-source/source-review.json',OLD/'comparisons/E070-three-pair-comparison/report.json',H/'history.json']
h.save(H/'report.json',{
    'id':'D191','at':h.now(),'status':'declined_closed_layout_family_scope_change_before_source',
    'prospect':'Interleave immutable per-node 32-bit fields into one record, keeping the original separate u64 data offset and all bits/widths.',
    'source_inventory':{'32bit_per_node_arrays':13,'separate_64bit_offset_arrays':1,'logical_bytes_per_node':60,'possible_unpadded_32bit_record_bytes':52,'calculation_is_not_native_resource_or_bandwidth_measurement':True},
    'classification':'No literal prior full node-record name found, but that is weak evidence. E046 already changes SoA metadata to interleaved records, including the same pinned-staging packing/drain and unchanged logical-payload idea. Moving the same layout mechanism to more fields/nodes is a scope change, not sufficient evidence of a distinct optimization. E070 compressed node attributes is separately closed; no narrowing or combination is admitted.',
    'closure':'Decline before source, compiler, CUDA query, metadata model or performance observation. Do not relabel an interleaving scope/width/field/padding/threshold change as a new candidate.',
    'implementation_obligations_not_executed':'All continuation/projection/capacity consumers would need coverage, including continuation.rs, continuation_storage.rs and continuation_capacity.rs. No layout/native/readback/capacity or material proof exists for this prospect.',
    'new_compiler_native_GPU_or_timing_processes':0,'source_candidate_written':False,'new_gain_accepted':False,
    'inputs':{str(p):h.sha(p) for p in inputs},
})
for name in ['history.json','report.json']:
    p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);assert not any(x['id']=='D191' for x in s['experiments'])
    s['experiments'].append({'id':'D191','at':h.now(),'title':'GPU node-record layout history review','status':'rejected','accepted':False,'correctness':'not_executed','stage':'Declined before source or execution','reason':'Interleaved node fields would broaden the closed E046 metadata-record layout mechanism. E070 compressed node attributes also remains closed. No source candidate, compiler, GPU call or speed sample.','evidence':[{'label':'Source inventory and semantic duplicate classification','url':'evidence/'+H.name+'/report.json'},{'label':'Retained queries and old closure sections','url':'evidence/'+H.name+'/history.json'}]})
    s.update(updated_at=h.now(),stage='Tree setup candidate closed; GPU source research continues',activity='E100 saved 17.6 ms in the CPU setup screen but did not advance. The GPU node-record layout prospect was declined from retained history before code or execution. E080 with 16 workers remains live; no new whole-solve gain adopted.')
    h.ar.atomic_json(h.ar.STATUS,s)
with ledger.open('a',encoding='utf-8',newline='\n') as f:
    f.write('\n\n### D191 semantic guard for node-record layout\n\nAfter actual D190/E100 full raw/component rejection, read-only source inventory counts 13 immutable 32-bit per-node arrays plus the separate u64 data offset (60 logical bytes/node). A possible 52-byte 32-bit-field record plus original offset would keep payload and bits, but no source/model/resource or speed trial was made. Literal local-all-ref/archive searches found only fold fixture JSON names and unrelated preflop test names; such a negative literal search is insufficient novelty evidence. Semantic ledger review found closed E046 interleaved chance records, including the same no-extra-payload/pinned-staging packing/drain idea. Broadening that record-layout mechanism to nodes/more fields is a source-scope change, so decline before implementation. E070 narrowing/width format remains separately closed and is not composed. Continuation projection/storage/capacity consumers were identified as additional obligations, not qualified. No new compiler/native/GPU/timing processes, no gain or new candidate. Both reports published and HTTP-byte verified, source/main/live/PTX unchanged, goal active.\n')
h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
subprocess.run(['git','commit','-m','research: retain semantic node layout duplicate guard'],cwd=h.REPO,check=True)
print(json.dumps({'D191':'declined closed interleaving scope variant','new_native_or_compiler_processes':0,'owned_children':'none started'}),flush=True)
