"""Root-only candidate activation after the actual resource audit is reviewed."""
import json, shutil, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
base=ar.RESEARCH
here=Path(__file__).resolve().parent
assert len(sys.argv)==2, 'Root supplies the independently reviewed resource validation SHA256'
audit=base/'comparisons/D037-independent-review/validation.json'
assert ar.sha256(audit)==sys.argv[1]
pins={
 'runs/D037-showdown-cache-resource/prepared-manifest.json':'783bce1a84f29c90ef77175e9028898247e9ee4b7f9c8ec76da99c28e6eadf63',
 'runs/D037-showdown-cache-design/candidate/manifest.json':'0be733fa538bc03b97782f520b4eeb48a3dc10914882f977c90e1fc7ea2a7946',
 'comparisons/D037-candidate-source-review/review.md':'e71ba50de427ed136612e977f091cbc7e23098865ae3d5ae2acbfb8936af19dc',
 'comparisons/D037-candidate-source-review/manifest.json':'d3a2601a509e8c6a1be338ea88aec49779bdb21d275cfb85a85f9ef0782cc3d5',
 'comparisons/D037-resource-source-review/review.md':'4bf91abe242eddb3b63e9931ef17c512a97263cac6020328fefff74c5f424641',
 'comparisons/D037-resource-source-review/manifest.json':'3b71ee49d0a47f3577b84f556a4de348fb270fb493668780c1841f9166e7bd7c',
 'runs/E020-primary-plan/protocol.json':'b5fa09fac0e0e4b652fe1479e5749cc2b1bfd023fe9b30c923b0d79ea46d6b2b',
 'runs/E020-primary-plan/scripts-manifest.json':'5ea29d0b2373a27dc255be6f437614e679f5f8b650e0fbc7f55768636f4b4d9e',
 'comparisons/E020-harness-review/review.md':'7291b3e04a27d31af282b4aa924b73eb2909b63f04af35371168a1796d234c76',
 'comparisons/E020-harness-review/manifest.json':'a4705615f0efec1e8b7a2936b7df78f44f87439c2dc3d010149a0e5448aa013a',
}
for name,h in pins.items():assert ar.sha256(base/name)==h,name
for name,h in json.loads((here/'scripts-manifest.json').read_text(encoding='utf-8'))['script_sha256'].items():
    assert ar.sha256(here/name)==h,name
candidate_dir=base/'runs/D037-showdown-cache-design/candidate'
sources={
 'crates/solver/src/gpu/kernels.cu':{'path':str(candidate_dir/'kernels.cu'),'sha256':'075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b'},
 'crates/solver/src/gpu/mod.rs':{'path':str(candidate_dir/'mod.rs'),'sha256':'ce71fa3bfb797baade1efe50beba68e971b88c7da1c9547d306e0b6e9245ee8d'},
}
for v in sources.values():assert ar.sha256(Path(v['path']))==v['sha256']
resource=base/'runs/D037-showdown-cache-resource/report.json'
r=json.loads(resource.read_text(encoding='utf-8'))
assert r['status']=='completed_compiler_resource_diagnostic'
assert r['kernel_launches']==0 and r['solver_executions']==0 and not r['performance_measurement']
assert r['numerical_validation']=='not executed'
assert len(r['other_entry_ptx_byte_equality'])==8 and all(r['other_entry_ptx_byte_equality'].values())
rows=[v for v in r['records'] if v['stage']=='resource']
assert len(rows)==14 and all(v['fits_queried_default_shared_and_thread_limits'] and v['occupancy_blocks_per_sm_128']>0 and v['max_threads_per_block']>=128 for v in rows)
assert all(v['returncode']==0 and not v.get('error') for v in r['commands'])
assert not (base/'gpu-run.lock').exists()
ar.refuse_active(ar.live_status())
accepted_path=base/'binaries/E015-postflop_autoresearch.manifest.json'
assert ar.sha256(accepted_path)=='934c29e800d180397ee330340d425f1084078c24831ba87c4de5e74729821fd2'
accepted=json.loads(accepted_path.read_text(encoding='utf-8'))
before=ar.source_identity()
assert before['source_sha256']==accepted['source_sha256']
status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
assert not any(v['id']=='E020' for v in status['experiments'])
assert not (here/'authorization.json').exists()
for name in ['comparisons/D037-independent-review/validation.json','comparisons/D037-independent-review/summary.md',
             'comparisons/D037-independent-review/manifest.json','runs/D037-showdown-cache-resource/report.json',
             'runs/D037-showdown-cache-resource/execution-manifest.json']:
    pins[name]=ar.sha256(base/name)
out=base/'runs/E020-source'
out.mkdir(exist_ok=False)
ar.atomic_json(out/'source-before.json',before)
for name,v in sources.items():
    filename=Path(name).name
    shutil.copyfile(repo/name,out/('accepted-'+filename))
    shutil.copyfile(v['path'],out/('candidate-'+filename))
    shutil.copyfile(v['path'],repo/name)
after=ar.source_identity()
assert set(after['source_sha256'])==set(before['source_sha256'])
assert {k for k,v in before['source_sha256'].items() if after['source_sha256'][k]!=v}==set(sources)
ar.atomic_json(out/'source-after.json',after)
(out/'candidate.patch').write_bytes(subprocess.check_output(['git','diff','--binary','HEAD','--',*sources],cwd=repo))
ar.atomic_json(here/'authorization.json',{'at':ar.now(),'candidate':'E020','resource_probe_pass':True,
    'independent_source_review_pass':True,'candidate_sources':sources,
    'evidence_sha256':{str(base/k):v for k,v in pins.items()},
    'scope':'Frozen source and no-launch resource audit permit native build and fixed primary testing only; numerical equivalence and performance acceptance are pending.',
    'resource_limit':'Queried rainbow/derived-river residency unchanged. Conservative 1326-hand residency falls from five to three blocks; a prospective wide-range holdout is required if primary passes before unconditional adoption.'})
published=[]
for name in ['runs/D037-showdown-cache-resource/report.json','comparisons/D037-independent-review/summary.md',
             'comparisons/D037-candidate-source-review/review.md','runs/E020-primary-plan/protocol.json']:
    source=base/name
    target=ar.DASHBOARD/'evidence'/source.parent.name/source.name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert ar.sha256(target)==ar.sha256(source)
    else:shutil.copyfile(source,target)
    published.append('evidence/'+source.parent.name+'/'+source.name)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(v for v in s['experiments'] if v['id']=='D037')
    row.update(status='measured',correctness='pending',updated_at=ar.now(),stage='Resource feasibility audited; no numerical execution',
        reason='All 14 resource rows fit default shared/thread limits with nonzero theoretical occupancy. Registers 40 to 38, no local storage; eight other PTX entries exact. Queried rainbow/derived-river residency stays at 12 blocks. Conservative full-hand case drops from five to three blocks. No kernel launches, numerical validation or speed claim.')
    row['evidence'].extend([{'label':'Executed compiler/resource report','url':published[0]},{'label':'Independent resource audit','url':published[1]}])
    s['experiments'].append({'id':'E020','at':ar.now(),'title':'Shared cache for showdown card-position indices','kind':'candidate','status':'planned','correctness':'pending','fixture':'All three fixtures','stage':'Source-frozen build preparation',
      'reason':'Two-file integer-cache candidate passed source/resource reviews. Native exactness and fixed three-pair performance screen pending. A prospective wide-range holdout addresses the shared-memory risk if primary passes.',
      'evidence':[{'label':'Exact candidate source review','url':published[2]},{'label':'Resource feasibility audit','url':published[1]},{'label':'Fixed primary protocol','url':published[3]}]})
    s.update(updated_at=ar.now(),stage='Preparing E020 native build',active_experiment='E020',
        activity='D037 resource audit passed with a disclosed wide-range occupancy cost. Building E020 for the fixed exactness/performance screen; accepted result remains E015 at 9.62%.')
    ar.atomic_json(ar.STATUS,s)
print('Authorization SHA256:',ar.sha256(here/'authorization.json'))
