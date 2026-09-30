"""Independent reconstruction of matched chance from actual model/board bytes.

Does not call the training comparator or final-bank selector. Rebuilds the
registered seed/generation draw, authenticates the parent's sealed state, and
checks append-only receipts while retaining original raw input identities.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from owned_research_archive_v1 import unpack


def require(ok,message):
    if not ok:raise ValueError(message)


def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(value):return hashlib.sha256(compact(value)).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())


def reconstruct(plan,parent,config,generation):
    require(set(plan)=={'format','method','generation','parent_state_sha256','config_sha256','boards'}, 'Unknown board-plan fields')
    body={k:v for k,v in parent.items() if k!='state_sha256'}
    require(parent['state_sha256']==digest(body) and parent['config']==config
        and parent['format']==1 and parent['method']=='board-integrated-bb-root-regrets-v1'
        and parent['completed_updates']==generation and parent['board_draws']==generation*config['boards_per_generation']
        and len(parent['history'])==generation and config['chance']=='numpy-pcg64-seedsequence-seed-generation-v1',
        'Parent seal, configuration or generation differs')
    rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence([config['board_seed'],generation])))
    boards=[]
    for _ in range(config['boards_per_generation']):
        board=rng.choice(52,size=5,replace=False).tolist();board[:3]=sorted(board[:3]);boards.append(board)
    expected=dict(format=1,method='board-integrated-bb-root-targets-v1',generation=generation,
        parent_state_sha256=parent['state_sha256'],config_sha256=digest(config),boards=boards)
    require(plan==expected, 'Original plan differs from independent own-parent/draw reconstruction')
    chance={k:v for k,v in plan.items() if k!='parent_state_sha256'}
    return dict(chance_sha256=hashlib.sha256(compact(chance)+b'\n').hexdigest(),
        parent_state_sha256=parent['state_sha256'],generation=generation,boards=boards,config_sha256=digest(config))


def audit_documents(arm,cycle,record,receipt,parent_model_ref,parent_model,config,plans,*,registration,comparator):
    keys=config['context_order'];raw=record['paired_sources']
    expected=set()
    for key in keys:
        expected.update((key+'/board-plan.json',key+'/source-generation.json'))
        expected.update(key+f'/batch-{i:03d}/batch.json' for i in range(13))
    require(set(raw)==expected and set(plans)==set(keys) and parent_model_ref['generation']==cycle-1
        and parent_model['generation']==cycle-1, 'Missing original inputs or wrong parent generation')
    chance={};compared=dict(raw)
    for key in keys:
        value=reconstruct(plans[key],parent_model['local_states'][key]['board_root_state'],config['contexts'][key]['board_root'],cycle-1)
        chance[key]=value;compared[key+'/board-plan.json']=value['chance_sha256']
    expected_receipt=dict(format=1,arm=arm,cycle=cycle,registration_sha256=registration,parent_model=parent_model_ref,
        original_source_hashes=raw,board_chance=chance,matched_input_identities=compared,own_parent_validated=True,
        comparator_sha256=comparator)
    require(receipt==expected_receipt, 'Receipt does not reproduce independently reconstructed chance evidence')
    return compared


def load_cycle(root,arm,cycle,record,selected_receipt,parent_model_ref,parent_model,config,*,registration,comparator,amendment,guard):
    root=Path(root);folder=root/arm;archive=folder/f'archive-{cycle:04d}';receipt_path=folder/f'chance-{cycle:04d}.json'
    require(record['cycle']==cycle and record['archive']==str(archive.relative_to(root))
        and selected_receipt==dict(path=str(receipt_path),sha256=sha(receipt_path)), 'Selected cycle/receipt identity differs')
    require(sha(archive/'index.json')==record['archive_index_sha256']
        and sha(archive/'retired.json')==record['retirement_sha256'], 'Published cycle archive differs')
    index=read(archive/'index.json');plan=read(archive/'plan.json');retired=read(archive/'retired.json')
    require(index['format']==1 and index['plan_sha256']==sha(archive/'plan.json')
        and retired['index_sha256']==sha(archive/'index.json') and retired['raw_files_remaining']==0
        and plan['owner']==str(root) and plan['destination']==str(archive)
        and plan['source']==str(folder/f'cycle-{cycle:04d}') and len(index['bundles'])==len(plan['jobs']),
        'Cycle archive plan/owner/retirement binding differs')
    members={m['path']:m for m in plan['members']}
    require(len(members)==len(plan['members']), 'Duplicate original archive member')
    for name,identity in record['paired_sources'].items():
        require(name in members and members[name]['sha256']==identity, 'Original input hash differs from authenticated plan')
    boards={}
    for key in config['context_order']:
        guard();name=key+'/board-plan.json'
        jobs=[(j,r) for j,r in zip(plan['jobs'],index['bundles']) if any(m['path']==name for m in j['members'])]
        require(len(jobs)==1, 'Missing or duplicated board archive')
        job,row=jobs[0];path=Path(job['destination']);manifest=path.with_suffix('.xz.json')
        require(path.parent==archive and path.name==row['archive'] and sha(manifest)==row['manifest_sha256'], 'Board manifest/path changed')
        restored=unpack(path,read(manifest),guard=guard)
        data=restored['board-plan.json']
        require(hashlib.sha256(data).hexdigest()==record['paired_sources'][name], 'Original board-plan bytes changed')
        boards[key]=json.loads(data)
    original_count=2 if arm=='A-baseline' else 1
    if cycle>original_count:
        require(record['chance_receipt_sha256']==sha(receipt_path) and record['continuation_amendment_sha256']==amendment
            and record['recovered_without_scientific_repeat'] is (arm=='A-relative' and cycle==2), 'Undocumented correction/recovery')
    return audit_documents(arm,cycle,record,read(receipt_path),parent_model_ref,parent_model,config,boards,
        registration=registration,comparator=comparator)
