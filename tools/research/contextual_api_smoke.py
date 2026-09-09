"""Exercise contextual API/preview on an explicitly isolated local server.

Creates a compact throwaway preflop game, never writes saved profiles/games.
The installed user ports are deliberately rejected.
"""
import argparse
import copy
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def run(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in ('localhost', '127.0.0.1') or parsed.port in (3737, 43737, 43738, 43740):
        raise ValueError('Use a separate local test server; installed ports are protected')

    def req(path, body=None, error=None):
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(url + path, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                assert error is None, f'Expected HTTP {error}'
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if error != exc.code:
                raise RuntimeError(exc.read().decode()) from exc

    cfg = dict(positions=['UTG','HJ','CO','BTN','SB','BB'], stack=100., posts=[0,0,0,0,.5,1],
               ante=0., limp=False, open_raises=[2.5], raise_mults=[3.], max_raises=3,
               add_allin=False, rake_pct=5., rake_cap=3., realization='raw')
    version = 'ignition-nl10-reraise-v1'
    body = dict(version=version, cfg=cfg, seat=1,
                context=dict(entry='raised', raises=2, pot=13.5, invested=2.5, to_call=9.))
    prediction = req('/api/preflop/contextual-preview', body)
    assert prediction['version'] == version and len(prediction['policy']['call']) == 169
    assert abs(prediction['nominal_price'] - 6.5/20) < 1e-12
    req('/api/preflop/contextual-preview', dict(body, typo=True), error=422)
    req('/api/preflop/contextual-preview', dict(body, version='unknown-version'), error=400)
    req('/api/preflop/contextual-preview', dict(body, seat=6), error=400)
    invalid = copy.deepcopy(body)
    invalid['context']['pot'] = 0
    req('/api/preflop/contextual-preview', invalid, error=400)
    outside = copy.deepcopy(body)
    outside['cfg']['posts'][-2] = 1.
    fallback = req('/api/preflop/contextual-preview', outside)
    assert fallback['policy'] is None and 'inactive' in fallback['note'].lower()

    library = req('/api/preflop/archetypes')
    source = next(x for x in library if x['name'] == 'Data · Ignition · NL10 regular · Pool')
    candidate = next(x for x in library if x['name'] == 'Data · Ignition · NL10 regular · Contextual v1')
    assert source['stats']['dataset'].get('contextual_reraise') is None
    stripped = copy.deepcopy(candidate['stats'])
    assert stripped['dataset'].pop('contextual_reraise') == version
    assert stripped == source['stats'], 'New entry changed an existing measured situation'

    tree = req('/api/preflop/spot', cfg)
    req('/api/preflop/solve', dict(iterations=5, check_every=5, target_gap=0.))
    deadline = time.monotonic() + 120
    while req('/api/preflop/status')['state'] == 'running':
        if time.monotonic() > deadline:
            raise TimeoutError('Test solve exceeded two minutes')
        time.sleep(.1)
    generated = req('/api/preflop/generate', dict(seat=1, stats=candidate['stats'], name=candidate['name']))
    profile = generated['profile']
    assert profile['response']['contextual_reraise'] == version
    assert profile['response']['adaptive_from'] == .25
    before = req('/api/preflop/session')
    req('/api/preflop/contextual-preview', body)
    assert req('/api/preflop/session') == before, 'Preview mutated the live session'
    seats = [dict(frozen=False, profile=profile if i == 1 else None) for i in range(6)]
    req('/api/preflop/table', dict(seats=seats))
    req('/api/preflop/solve', dict(iterations=5, check_every=5, target_gap=0.))
    while req('/api/preflop/status')['state'] == 'running':
        if time.monotonic() > deadline:
            raise TimeoutError('Modeled test solve exceeded two minutes')
        time.sleep(.1)
    # HJ opens, BTN 3-bets, others fold: distinguish earlier raiser from caller.
    path = []
    for actor, kind, amount in [(0,'fold',None),(1,'raise',2.5),(2,'fold',None),(3,'raise',7.5),(4,'fold',None),(5,'fold',None)]:
        node = req('/api/preflop/node', dict(path=path))
        assert node['actor'] == actor, node
        path.append(next(i for i,a in enumerate(node['actions']) if a['kind'] == kind and (amount is None or abs(a['to']-amount)<1e-8)))
    node = req('/api/preflop/node', dict(path=path))
    status = node['contextual_prediction']
    assert status['active'] and status['context']['entry'] == 'raised'
    assert status['context']['raises'] == 2
    assert status['context']['invested'] == 2.5 and status['context']['to_call'] == 7.5
    return dict(passed=True, checks=['pure preview','strict request fields','version and seat validation',
                                    'unsupported fallback','separate library entry','profile generation',
                                    'session preservation','actual earlier-raiser context'],
                tree=tree, context=status, ui_test_path=path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:43739')
    parser.add_argument('--out', default='output/contextual-api-smoke.json')
    args = parser.parse_args()
    result = run(args.url.rstrip('/'))
    Path(args.out).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
