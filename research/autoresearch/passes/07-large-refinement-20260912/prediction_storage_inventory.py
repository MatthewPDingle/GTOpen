"""Reproduce allocation arithmetic from verified immutable fixture evidence."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def inventory():
    a = HERE/'raw/large-averaging-dcfr-v1-compare.json'
    b = HERE/'raw/large-normalized-pair-seed42-v1.log'
    x = json.loads(a.read_text(encoding='utf-8'))
    m = re.search(r'(\d+) nodes, (\d+) levels, (\d+) terminals', b.read_text(encoding='utf-8'))
    nodes, levels, terms = map(int,m.groups())
    assert nodes == x['nodes'] == 1567754 and x['all_learning'] and x['regrets_bit_exact']
    entries = x['regret_entries']; arena = entries*4; terminals = terms*169*8*4
    return dict(nodes=nodes,levels=levels,terminals=terms,players=8,hand_classes=169,
        action_entries=entries,one_action_array_bytes=arena,two_action_arrays_bytes=2*arena,
        dense_per_player_terminal_bytes=terminals,dense_terminals_plus_action_policy_bytes=terminals+arena,
        four_gib=4*1024**3,dense_terminals_alone_exceed_four_gib=terminals>4*1024**3,
        scope='Allocation arithmetic from verified fixture; not a measured predictive implementation',
        inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a,b]})


if __name__ == '__main__':
    print(json.dumps(inventory(),indent=2))
