"""Bounded exact private-pair labels for one explicitly supplied deal stream.

No sampler, neural input, response selection, or GPU work occurs here. A caller
must freeze its response before supplying a held-out stream. Each output is new
and preserves the original unlabelled deals and provenance of reused rows.
"""
import json
from pathlib import Path
import subprocess
import time

from sampled_allin_protocol_v3 import AllinCache, canonical, BOARDS
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown


def build(deals, base, folder, *, maximum_new_keys, guard):
    if not isinstance(base, AllinCache):
        raise TypeError('An explicitly hash-checked base cache is required')
    if type(maximum_new_keys) is not int or maximum_new_keys < 0:
        raise ValueError('Nonnegative exact-enumeration budget required')
    if not isinstance(deals, list) or not deals:
        raise ValueError('A nonempty already supplied stream is required')
    keys = set()
    for deal in deals:
        if (not isinstance(deal, list) or len(deal) != 9
                or any(type(c) is not int or not 0 <= c < 52 for c in deal)
                or len(set(deal)) != 9):
            raise ValueError('Nine distinct physical cards required')
        keys.add(canonical(deal[:4]))
    keys = sorted(keys)
    missing = [k for k in keys if k not in base.rows]
    if len(missing) > maximum_new_keys:
        raise ValueError('New private-pair count exceeds the declared budget')
    guard()
    folder = Path(folder); folder.mkdir(exist_ok=False)
    started = time.monotonic()
    source = folder/'source-deals.json'; save(source, deals)
    keypath = folder/'keys.json'; save(keypath, keys)
    exe = ROOT/'target/release/examples/hu_allin_board_reference.exe'
    inputs = {str(p):sha(p) for p in (Path(__file__), exe,
        ROOT/'tools/research/sampled_allin_protocol_v3.py',
        ROOT/'tools/research/hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py')}
    save(folder/'registration.json', dict(inputs=inputs,source_sha256=sha(source),
        keys_sha256=sha(keypath),base_sha256=base.sha256,deal_count=len(deals),
        unique_keys=len(keys),new_keys=len(missing),maximum_new_keys=maximum_new_keys,
        batch_size=20,player_roles_fixed=True,production_modified=False))
    rows = {k:dict(base.rows[k]) for k in keys if k in base.rows}
    artifacts = {}; child = None; native_seconds = 0.
    try:
        with (folder/'native.log').open('x') as log:
            for offset in range(0,len(missing),20):
                guard(); selected = missing[offset:offset+20]
                cases = [dict(private_cards=list(k),
                    sampled_boards=[[c for c in range(52) if c not in k][:5]]) for k in selected]
                ip = folder/f'input-{offset:06d}.json'; op = folder/f'native-{offset:06d}.json'
                save(ip,dict(format=1,cases=cases))
                child = subprocess.Popen([str(exe),str(ip),str(op)],cwd=ROOT,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                while child.poll() is None:
                    time.sleep(.25); guard()
                if child.returncode:
                    raise RuntimeError(f'Exact-label enumeration failed at key {offset}')
                output = json.loads(op.read_text())
                assert len(output) == len(cases)
                for case,native in zip(cases,output):
                    assert native['private_cards'] == case['private_cards']
                    assert all(type(native[k]) is int and native[k] >= 0 for k in ('wins','ties','losses','exact_boards'))
                    assert native['wins']+native['ties']+native['losses'] == native['exact_boards'] == BOARDS
                    assert native['equity'] == (native['wins']+.5*native['ties'])/BOARDS
                    winner = showdown(case['private_cards']+case['sampled_boards'][0])
                    assert native['sampled_scores'] == [1 if winner < 0 else 2 if winner == 0 else 0]
                    rows[tuple(case['private_cards'])] = dict(private_cards=native['private_cards'],
                        wins=native['wins'],ties=native['ties'],losses=native['losses'],boards=BOARDS)
                    native_seconds += native['exact_seconds']
                artifacts.update({str(p):sha(p) for p in (ip,op)})
        assert sorted(rows) == keys
        cachepath = folder/'cache.json'
        save(cachepath,dict(format=1,player_roles_fixed=True,rows=[rows[k] for k in keys]))
        cache = AllinCache(cachepath,sha(cachepath))
        cache.labels(deals)  # Fail closed on incomplete or incompatible coverage.
        for p,h in inputs.items(): assert sha(p) == h,p
        for p,h in artifacts.items(): assert sha(p) == h,p
        guard()
        result = dict(passed=True,registration_sha256=sha(folder/'registration.json'),
            source_sha256=sha(source),base_sha256=base.sha256,cache_sha256=cache.sha256,
            cache_artifact=str(cachepath),deal_count=len(deals),unique_keys=len(keys),
            reused_keys=len(keys)-len(missing),new_keys=len(missing),
            exact_new_boards=BOARDS*len(missing),native_seconds=native_seconds,
            seconds=time.monotonic()-started,artifacts=artifacts,production_modified=False)
        save(folder/'result.json',result)
        return cache,result
    finally:
        if child is not None and child.poll() is None:
            child.terminate(); child.wait(timeout=20)
