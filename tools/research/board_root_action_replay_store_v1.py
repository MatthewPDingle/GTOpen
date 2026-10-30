"""Append-only completed-batch routes and exact-path owned scratch retirement."""
import json
import os
from pathlib import Path
import re
import time
import uuid
from board_root_action_decomposition_v1 import digest, encoded, require, unlinked
from board_prefix_publication_v1 import atomic_json

BATCH = re.compile(r'test-[0-9]{6}')
ATTEMPT = re.compile(r'attempt-[0-9a-f]{32}')
CHECKPOINT = re.compile(r'checkpoint-([0-9]{6})-([0-9a-f]{64})\.json')


def sha(path):
    return digest(Path(path).read_bytes())


def root(path):
    path=unlinked(path)
    require(path.is_relative_to(Path('S:/GTOpen-research')) and
        path != Path('S:/GTOpen-research') and path.is_dir(), 'Existing owned research descendant required')
    return path


def owner(store, registration_sha256):
    store=root(store)
    expected=dict(root=str(store),registration_sha256=registration_sha256)
    require(json.loads((store/'owner.json').read_bytes()) == expected, 'Changed replay owner')
    return store


def attempt(store, registration_sha256):
    store=owner(store,registration_sha256)
    folder=store/('attempt-'+uuid.uuid4().hex);folder.mkdir()
    atomic_json(folder/'owner.json',dict(root=str(folder),registration_sha256=registration_sha256,
        pid=os.getpid(),created=time.time()))
    return folder


def verify_receipt(store, registration_sha256, name, route, source_route):
    store=owner(store,registration_sha256)
    require(BATCH.fullmatch(name) and set(route) == {'attempt','receipt_sha256'}
        and ATTEMPT.fullmatch(route['attempt']), 'Invalid batch route')
    parent=unlinked(store/route['attempt']);folder=unlinked(parent/name)
    require(parent.parent == store and folder.parent == parent, 'Escaping completed batch')
    attempt_owner=json.loads((parent/'owner.json').read_bytes())
    require(attempt_owner['root'] == str(parent) and attempt_owner['registration_sha256'] == registration_sha256,
        'Changed attempt ownership')
    path=folder/'receipt.json'
    require(sha(path) == route['receipt_sha256'], 'Changed batch receipt')
    receipt=json.loads(path.read_bytes())
    require(receipt['name'] == name and receipt['registration_sha256'] == registration_sha256
        and receipt['source_route'] == source_route and receipt['deals'] == 32
        and receipt['root_only_deviation'] and receipt['later_behavior_fixed']
        and not receipt['original_native_rerun'] and receipt['maximum_mixture_error'] < 1e-10,
        'Changed receipt identity or evaluation meaning')
    require(set(receipt['artifacts']) == {'native.json','action-values.json'}, 'Unexpected retained artifacts')
    for n,h in receipt['artifacts'].items(): require(sha(folder/n) == h, 'Changed completed artifact')
    retirement=json.loads((folder/'retirement.json').read_bytes())
    require(retirement == dict(receipt_sha256=route['receipt_sha256'],retired=receipt['scratch_sha256']),
        'Scratch retirement not complete')
    require(all(not (folder/n).exists() for n in receipt['scratch_sha256']), 'Retired scratch reappeared')
    return receipt, folder


def retire(store, folder, receipt):
    store=owner(store,receipt['registration_sha256']);folder=unlinked(folder)
    require(folder.parent.parent == store and ATTEMPT.fullmatch(folder.parent.name)
        and BATCH.fullmatch(folder.name) and folder.name == receipt['name'], 'Unsafe scratch path')
    require(json.loads((folder/'owner.json').read_bytes()) == dict(root=str(folder),
        registration_sha256=receipt['registration_sha256'],name=receipt['name']), 'Changed scratch ownership')
    require(json.loads((folder/'receipt.json').read_bytes()) == receipt, 'Unpublished scratch receipt')
    require(set(receipt['scratch_sha256']) == {'conditional-batch.json','forced-profiles.json'}, 'Unexpected scratch names')
    for n,h in receipt['scratch_sha256'].items():
        target=unlinked(folder/n)
        require(target.parent == folder and sha(target) == h, 'Changed owned scratch input')
        # Retry only transient Windows sharing violations, for this exact file.
        for tries in range(8):
            try: target.unlink();break
            except PermissionError:
                if tries == 7: raise
                time.sleep(.1*(tries+1))
    atomic_json(folder/'retirement.json',dict(receipt_sha256=sha(folder/'receipt.json'),retired=receipt['scratch_sha256']))


def recover(store, registration_sha256, batches, source_routes, guard):
    store=owner(store,registration_sha256);found=[]
    for path in store.glob('checkpoint-*.json'):
        match=CHECKPOINT.fullmatch(path.name)
        require(match is not None, 'Unexpected checkpoint filename')
        raw=path.read_bytes();require(digest(raw) == match[2], 'Changed checkpoint bytes')
        doc=json.loads(raw);count=int(match[1])
        require(doc['registration_sha256'] == registration_sha256 and doc['completed_batches'] == count
            and 0 <= count <= len(batches) and list(doc['routes']) == batches[:count], 'Changed committed prefix')
        found.append((count,path,doc))
    found.sort(key=lambda v:v[0]);require(found and found[0][0] == 0,'Initial checkpoint required')
    require(len({n for n,_,_ in found}) == len(found),'Conflicting checkpoints')
    previous=None;routes={}
    for _,path,doc in found:
        require(doc['previous'] == previous and all(doc['routes'].get(k) == v for k,v in routes.items()),
            'Changed checkpoint lineage')
        routes=doc['routes'];previous=dict(file=path.name,sha256=sha(path))
    for name,route in routes.items():
        guard();verify_receipt(store,registration_sha256,name,route,source_routes[name])
    return routes,previous


def commit(store, registration_sha256, batches, routes, previous, previous_routes, source_routes, guard):
    store=owner(store,registration_sha256);count=len(routes)
    require(list(routes) == batches[:count] and all(routes.get(k) == v for k,v in previous_routes.items()),
        'Changed or reordered route prefix')
    if previous is None:
        require(not routes and not previous_routes and not list(store.glob('checkpoint-*.json')), 'Invalid initial checkpoint')
    else:
        require(count > len(previous_routes) and sha(store/previous['file']) == previous['sha256'],
            'Checkpoint must advance its existing predecessor')
        prior=json.loads((store/previous['file']).read_bytes())
        require(prior['routes'] == previous_routes and prior['registration_sha256'] == registration_sha256,
            'Changed predecessor contents')
    for name in list(routes)[len(previous_routes):]:
        guard();verify_receipt(store,registration_sha256,name,routes[name],source_routes[name])
    doc=dict(format=1,registration_sha256=registration_sha256,completed_batches=count,
        previous=previous,routes=routes)
    raw=encoded(doc)+b'\n'
    path=store/f'checkpoint-{count:06d}-{digest(raw)}.json'
    atomic_json(path,doc)
    require(sha(path) == digest(raw),'Checkpoint encoding differs')
    return dict(file=path.name,sha256=digest(raw))
