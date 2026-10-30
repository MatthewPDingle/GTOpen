"""Authenticate the four recovered cycle boundaries before final selection.

Only the declared interruption is recognized. Later cycles retain the original
contract. Every retained original byte is bound to its completed archive plan.
This module does not collect targets, fit, draw test hands or choose a model.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE=Path('S:/GTOpen-research/stack-context-matched-learning-v1')
PREFIX='stack-context-interrupted-cycle-recovery-v1'
AMENDMENT=OUT/(PREFIX+'-amendment.json')
RESULT=OUT/(PREFIX+'-result.json')
FAILURE=OUT/(PREFIX+'-failure.json')
AUDIT=OUT/'stack-context-parallel-interruption-audit-v1-result.json'
REG=OUT/'stack-context-matched-learning-v1-registration.json'
CYCLES={'A-baseline':4,'A-relative':4,'B-baseline':4,'B-relative':3}
ACTIONS={a:('publish-already-complete-checkpoint' if a in ('A-baseline','B-relative')
    else 'continue-retained-partial-cycle') for a in CYCLES}


def require(ok,message):
    if not ok:raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_bytes())


def publication_sha(document):
    # Original atomic_json serializes insertion order, compact separators and LF.
    raw=(json.dumps(document,separators=(',',':'),allow_nan=False)+'\n').encode()
    return hashlib.sha256(raw).hexdigest()


def validate_prefixes(progress,outcome,*,amendment_sha256):
    require(outcome.get('complete') is True and outcome.get('passed') is True
        and outcome.get('boundaries')==CYCLES and outcome.get('amendment_sha256')==amendment_sha256,
        'Incomplete or detached interruption recovery result')
    require(outcome.get('original_parallel_v2_compatible') is True
        and outcome.get('full_training_complete') is False and outcome.get('scientific_evaluation_complete') is False
        and outcome.get('production_modified') is False,'Unexpected recovery scope')
    require(set(progress)==set(CYCLES) and len(outcome['arms'])==4,'Four recovered arms required')
    rows={r['arm']:r for r in outcome['arms']}
    require(set(rows)==set(CYCLES),'Duplicate or missing recovery outcomes')
    identities={}
    for arm,cycle in CYCLES.items():
        p=progress[arm];row=rows[arm]
        require(type(p['completed_cycles']) is int and cycle<=p['completed_cycles']<=64
            and len(p['updates'])==p['completed_cycles'],'Recovery prefix is incomplete')
        require(row['cycle']==cycle and row['action']==ACTIONS[arm]
            and row.get('all_preinterruption_bytes_preserved_in_archives') is True,'Wrong recovered boundary')
        for i,record in enumerate(p['updates'],1):
            require(record['cycle']==i,'Reordered or duplicated training cycle')
            expected_recovery=(i==cycle) or (arm=='A-relative' and i==2)
            if 'recovered_without_scientific_repeat' in record:
                require(record['recovered_without_scientific_repeat'] is expected_recovery,
                    'Unrecognized scientific recovery or retry')
            if i==cycle:
                require(record.get('interruption_recovery_amendment_sha256')==amendment_sha256
                    and record.get('recovery_action')==ACTIONS[arm]
                    and record.get('recovered_without_scientific_repeat') is True
                    and record['checkpoint']==row['checkpoint'],'Recovered record detached from its outcome')
            else:
                require('interruption_recovery_amendment_sha256' not in record
                    and 'recovery_action' not in record,'Recovery extended to an unregistered cycle')
        record=p['updates'][cycle-1]
        prefix=dict(p,completed_cycles=cycle,checkpoint=record['checkpoint'],updates=p['updates'][:cycle])
        digest=publication_sha(prefix)
        require(digest==row['progress_sha256'],'Published recovered prefix was changed')
        identities[arm]=digest
    return identities


def verify_recovery(train_result=None,*,guard=lambda:None):
    require(not FAILURE.exists(),'Recovery failure requires independent review')
    amendment,outcome,audit=read(AMENDMENT),read(RESULT),read(AUDIT)
    amendment_sha256=sha(AMENDMENT)
    require(amendment.get('format')==1 and amendment.get('arms')==CYCLES
        and amendment.get('original_invocation_pid')==75720 and amendment.get('original_stale_lock')=='75720'
        and amendment.get('original_stale_lock_sha256')==hashlib.sha256(b'75720').hexdigest()
        and amendment.get('old_processes_verified_absent') is True,'Unrecognized interrupted invocation')
    expected={'completed_cycles_refitted':False,'partial_cycles_discarded':False,
        'seeds_budgets_targets_unchanged':True,'original_deadline_unchanged':True,'evaluation_gates_unchanged':True,
        'maximum_concurrent_recovery_arms':2,'target_workers_per_arm':4,'board_workers_per_arm':1,
        'global_allocated_cap':800_000_000_000,'logical_reservation':70_000_000_000,
        'production_modified':False,'github_push':False}
    require(all(amendment.get(k)==v for k,v in expected.items()),'Recovery changed scientific or operational limits')
    require(amendment['allocated_including_reservation']<=800_000_000_000,'Unbounded recovery admission')
    paths={AMENDMENT,RESULT,AUDIT,REG,Path(__file__).resolve()}
    require(amendment.get('preserved_interruption_audit_sha256')==sha(AUDIT)
        and audit.get('read_only_audit_passed') is True and audit.get('original_processes_absent') is True
        and audit.get('scientific_inputs_modified') is False and audit.get('scientific_retries')==0,
        'Recovery detached from authenticated interruption evidence')
    for path,identity in amendment['inputs'].items():
        guard();require(sha(path)==identity,'Recovery input changed: '+path);paths.add(Path(path))
    require(amendment['inputs'].get(str(REG))==sha(REG),'Wrong original study registration')
    for prefix in ('stack-context-archive-recovery-check-v1','stack-context-archive-transport-recovery-v1',
                   'stack-context-retained-state-replay-check-v1','stack-context-river-transport-resume-check-v2',
                   'stack-context-partial-cycle-resume-check-v2'):
        path=OUT/(prefix+'-result.json');proof=read(path)
        require(amendment['inputs'].get(str(path))==sha(path) and proof.get('complete') is True
            and proof.get('passed') is True,'Missing or changed recovery qualification')
    if train_result is None:
        progress={a:read(STORE/a/'progress.json') for a in CYCLES}
    else:
        progress=train_result['arms']
        require(train_result.get('registration_sha256')==sha(REG),'Recovery used in another study')
    prefixes=validate_prefixes(progress,outcome,amendment_sha256=amendment_sha256)
    members={};archives={}
    for arm,cycle in CYCLES.items():
        row=audit['arms'][arm];archive=STORE/arm/f'archive-{cycle:04d}'
        raw=STORE/arm/f'cycle-{cycle:04d}';record=progress[arm]['updates'][cycle-1]
        require(Path(row['raw'])==raw and Path(row['archive'])==archive and row['interrupted_cycle']==cycle,
            'Audit identifies another cycle')
        require(record['archive']==str(archive.relative_to(STORE)),'Recovered archive path differs')
        plan,index,retired=(read(archive/n) for n in ('plan.json','index.json','retired.json'))
        require(plan['source']==str(raw) and plan['destination']==str(archive) and plan['owner']==str(STORE)
            and index['plan_sha256']==sha(archive/'plan.json')
            and sha(archive/'index.json')==record['archive_index_sha256']
            and sha(archive/'retired.json')==record['retirement_sha256']
            and retired['index_sha256']==sha(archive/'index.json') and retired['raw_files_remaining']==0,
            'Recovered archive/index/retirement identity differs')
        members[arm]={r['path']:r for r in plan['members']};archives[arm]=(raw,archive)
        require(len(members[arm])==len(plan['members']) and len(plan['jobs'])==len(index['bundles']),
            'Duplicate members or incomplete recovered archive')
        paths.update(archive/n for n in ('plan.json','index.json','retired.json'))
        require(sha(STORE/arm/'objects'/record['checkpoint']['file'])==record['checkpoint']['sha256'],
            'Recovered checkpoint object changed')
        paths.add(STORE/arm/'objects'/record['checkpoint']['file'])
    authenticated=0
    for row in audit['files']:
        guard();path=Path(row['path']);matched=False
        for arm,(raw,archive) in archives.items():
            if path.is_relative_to(raw):
                key=path.relative_to(raw).as_posix();member=members[arm].get(key)
                require(member is not None and member['sha256']==row['sha256'] and member['bytes']==row['bytes'],
                    'Preinterruption bytes omitted or changed in archive')
                matched=True;break
            if path.is_relative_to(archive):
                require(sha(path)==row['sha256'] and path.stat().st_size==row['bytes'],
                    'Original archive bytes changed during recovery')
                paths.add(path);matched=True;break
        require(matched,'Audit member escaped its recognized cycle');authenticated+=1
    require(authenticated==audit['hashed_files']==9400,'Incomplete interruption evidence coverage')
    identity=dict(format=1,amendment_sha256=amendment_sha256,result_sha256=sha(RESULT),audit_sha256=sha(AUDIT),
        recovered_cycles=CYCLES,recovered_actions=ACTIONS,recovered_prefix_sha256=prefixes,
        retained_files_bound=authenticated,original_registration_sha256=sha(REG),
        seeds_budgets_targets_unchanged=True,completed_cycles_refitted=False)
    return identity,paths
