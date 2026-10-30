"""One outcome-triggered, bounded extension; no interim acceptance or further extension."""
import json, os, shutil, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
out=ar.RESEARCH/'runs/E016-extension'
arms={'original':('baseline-complete','f2b93f5088f8395baaac9b47e7cdb89cfc92e7e33d9af50702b0ee8485e6ee6f'),
      'E016':('E016-postflop_autoresearch','bab2bf04b107dba790a875efd611831e73dc47e5f6faa13e6351f88202dc2bcf')}
pairs=[{'baseline':f'B{n+43:03d}','candidate':f'E016C{n}',
        'order':[f'E016C{n}',f'B{n+43:03d}'] if n%2==0 else [f'B{n+43:03d}',f'E016C{n}']} for n in range(4,10)]
old=[{'baseline':'B044','candidate':'E016C1'},{'baseline':'B045','candidate':'E016C2'},{'baseline':'B046','candidate':'E016C3'}]
protocol_path=out/'protocol.json'
if sys.argv[1:] == ['seal']:
    out.mkdir(exist_ok=False)
    assert ar.sha256(repo/'crates/solver/src/gpu/mod.rs')=='0ca68663e9eeaf168b6769b36bd266d59ddc0c0d4838641ce0dd350c40d2abed'
    evidence={}
    for name,expected in arms.values():
        binary=ar.RESEARCH/'binaries'/(name+'.exe')
        assert ar.sha256(binary)==expected
        manifest=ar.RESEARCH/'binaries'/(name+'.manifest.json')
        assert json.loads(manifest.read_text(encoding='utf-8'))['binary_sha256']==expected
        evidence[str(binary)]=expected;evidence[str(manifest)]=ar.sha256(manifest)
    for pair in old:
        for identity in pair.values():
            path=ar.RESEARCH/'runs'/identity/'report.json';evidence[str(path)]=ar.sha256(path)
    for relative in ('comparisons/E016-cumulative-comparison/report.json','comparisons/E016-independent-review/cumulative-validation.json','comparisons/D028-three-arm-review/report.json'):
        path=ar.RESEARCH/relative;evidence[str(path)]=ar.sha256(path)
    for pair in pairs:
        for identity in pair['order']:assert not (ar.RESEARCH/'runs'/identity).exists(),identity
    protocol={'id':'E016-extension','sealed_at':ar.now(),
      'classification':'Outcome-triggered protocol amendment. Not an untouched confirmatory trial or significance test.',
      'rationale':'Initial three cumulative pairs failed the river guard. D028 did not reproduce a consistent original/E015/E016 river penalty; initialization distributions overlap. Two independent critics support one finite extension retaining all failures.',
      'fixed_inputs':'Unchanged original and E016 native binaries, frozen evaluator/workload, full fixture order, compressed storage, 16 CPU threads, unprofiled warm-cache protocol; serialized GPU runs and no concurrent builds.',
      'arms':arms,'earlier_pairs':old,'new_pairs':pairs,'pooled_pairs':old+pairs,
      'diagnostic_exclusion':'D028 remains diagnostic and is excluded from qualification by its original protocol. No result from either cumulative cohort is excluded.',
      'decision_rules':[
        'Run exactly six additional alternating pairs, in the sealed order, without interim acceptance.',
        'Report initial three, new six and pooled nine cohorts separately. Initial failure retains its original verdict.',
        'BOTH new-six and pooled-nine must independently satisfy >=2% reduction in the unchanged sum of per-fixture median complete-cycle times.',
        'BOTH must pass the unchanged fixture guard: reject any fixture whose median regression exceeds 3% AND whose paired regressions above 3% form a strict majority, minimum two. This is at least 4/6 new pairs and 5/9 pooled pairs.',
        'Require all complete non-timing results exact with unchanged source/binary identities; prior primary and broader correctness checks must remain passing.',
        'If either cohort fails any gate, reject E016. No further sample-size extension, selective rerun, exclusion, binary edit or reclassification may rescue this candidate.',
        'A run failure stops execution and leaves qualification incomplete; retain all evidence and make no acceptance claim.',
        'If both pass, disclose the initial failure and adaptive enlargement alongside the measured gain. No significance, general absence of regression, cold-start, arbitrary-tree or deployment claim.'
      ],'verified_artifacts':evidence,'source_identity':ar.source_identity(),'script_sha256':ar.sha256(Path(__file__))}
    ar.atomic_json(protocol_path,protocol)
    public=ar.DASHBOARD/'evidence/E016-extension/protocol.json';public.parent.mkdir(parents=True,exist_ok=True)
    assert not public.exists();shutil.copyfile(protocol_path,public)
    print(json.dumps({'protocol':str(protocol_path),'sha256':ar.sha256(protocol_path),'order':[i for p in pairs for i in p['order']]}))
elif sys.argv[1:] == ['run']:
    protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
    assert ar.sha256(Path(__file__))==protocol['script_sha256']
    assert ar.source_identity()['source_sha256']==protocol['source_identity']['source_sha256']
    for path,expected in protocol['verified_artifacts'].items():assert ar.sha256(Path(path))==expected,path
    assert not (out/'started.json').exists()
    ar.atomic_json(out/'started.json',{'at':ar.now(),'protocol_sha256':ar.sha256(protocol_path)})
    for pair in protocol['new_pairs']:
        for identity in pair['order']:
            candidate=identity==pair['candidate'];name=arms['E016' if candidate else 'original'][0]
            env=os.environ.copy()
            for key in ('POSTFLOP_AUTORESEARCH_PROFILE','POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE'):env.pop(key,None)
            subprocess.run([sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title','E016 bounded extension: candidate' if candidate else 'E016 bounded extension: original reference',
              '--kind','candidate' if candidate else 'baseline','--binary',str(ar.RESEARCH/'binaries'/(name+'.exe')),
              '--build-manifest',str(ar.RESEARCH/'binaries'/(name+'.manifest.json')),'--test','postflop_complete_cycle'],cwd=repo,env=env,check=True)
    assert ar.source_identity()['source_sha256']==protocol['source_identity']['source_sha256']
    ar.atomic_json(out/'completed.json',{'at':ar.now(),'runs_completed':12,'protocol_sha256':ar.sha256(protocol_path),'accepted':False})
    print('All 12 extension runs complete. Both new and pooled terminal gates remain to be assessed.',flush=True)
else:raise SystemExit('Use seal or run')
