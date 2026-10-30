import sys, json, struct, array
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D144-incidence'
P = h.read(H / 'protocol-r2.json')
C = h.read(H / 'execution-r2/native-complete.json')
for p, digest in P['input_sha256'].items():
    h.pin(p, digest)
for p, digest in C['raw_sha256'].items():
    h.pin(p, digest)
assert h.exact('D144R1') == h.read(h.EPOCH / 'exact-anchor.json')
checks = 0
def req(value, label):
    global checks
    assert value, label
    checks += 1
def read_frame(path):
    fields = {}
    with path.open('rb') as f:
        req(f.read(16) == b'D144-REACH-v1\0\0\0', 'frame magic')
        while True:
            head = f.read(8)
            if not head:
                break
            req(len(head) == 8, 'field header')
            kind, n = struct.unpack('<II', head)
            name = f.read(n).decode()
            count = struct.unpack('<Q', f.read(8))[0]
            req(name not in fields and kind in [0, 2], 'field kind/name')
            if kind == 0:
                req(f.read(4) == bytes(4), 'all positive-zero run')
                values = array.array('I', [0]) * count
            else:
                values = array.array('I')
                values.frombytes(f.read(count * 4))
                req(len(values) == count, 'full field words')
            fields[name] = values
    req(len(fields) == 13, 'all thirteen fields')
    return fields
rows = []
for fixture, iterations in [('rainbow', [20, 200]), ('two-tone', [20, 200]), ('river', [20, 60])]:
    for iteration in iterations:
        path = H / 'output' / f'{fixture}-{iteration}.bin'
        d = read_frame(path)
        req(list(d['iteration']) == [iteration], 'fixed sample iteration')
        nhs = d['hands']
        req(len(nhs) == 2 and min(nhs) > 0, 'logical hands')
        nn = len(d['node_player'])
        req(len(d['node_na']) == nn and len(d['node_children_start']) == nn and len(d['rsrc0']) == len(d['rsrc1']) == nn and len(d['lock_off']) == 2 * nn, 'metadata geometry')
        req(len(set(d['action_nodes'])) == len(d['action_nodes']), 'unique action node IDs')
        statistics = []
        for p in range(2):
            nh = nhs[p]
            reach = d[f'reach{p}']
            rsrc = d[f'rsrc{p}']
            req(len(reach) % nh == 0, 'unmodified dense reach pitch')
            blocks = len(reach) // nh
            writers = set()
            for node in d['action_nodes']:
                req(node < nn and d['node_player'][node] in [0, 1], 'actual action metadata')
                if d['node_player'][node] != p:
                    continue
                start = d['node_children_start'][node]
                na = d['node_na'][node]
                req(na > 0 and start + na <= len(d['children']), 'child list bounds')
                for child in d['children'][start:start + na]:
                    req(child < nn, 'action child node bound')
                    slot = rsrc[child]
                    req(0 < slot < blocks and slot not in writers, 'unique action owner slot')
                    writers.add(slot)
            for child in d['chance_children']:
                req(child < nn, 'chance child node bound')
                slot = rsrc[child]
                req(0 < slot < blocks and slot not in writers, 'unique chance owner slot')
                writers.add(slot)
            visits = zeros = negative_zeros = nonfinite = output_visits = zero_outputs = nodes = 0
            for node in d['action_nodes']:
                if d['node_player'][node] != p:
                    continue
                req(d['lock_off'][2 * node + 1] == 0xffffffff and d['lock_off'][2 * node] == 0xffffffff, 'baseline node unlocked')
                slot = rsrc[node]
                req(slot < blocks and (slot == 0 or slot in writers), 'input owner exists')
                values = reach[slot * nh:(slot + 1) * nh]
                positive = values.count(0)
                negative = values.count(0x80000000)
                bad = sum((v & 0x7f800000) == 0x7f800000 for v in values)
                nodes += 1
                visits += nh
                zeros += positive + negative
                negative_zeros += negative
                nonfinite += bad
                na = d['node_na'][node]
                output_visits += nh * na
                zero_outputs += (positive + negative) * na
            statistics.append({'actor': p, 'actual_pass_represented': 'second traverser sweep (p1)' if p == 0 else 'first traverser sweep (p0); retained through p1', 'action_nodes': nodes, 'hand_visits': visits, 'signed_zero_hand_visits': zeros, 'negative_zero_hand_visits': negative_zeros, 'nonfinite_parent_hand_visits': nonfinite, 'zero_hand_fraction': zeros / visits, 'action_output_visits': output_visits, 'zero_action_output_visits': zero_outputs, 'zero_action_output_fraction': zero_outputs / output_visits, 'unique_nonroot_writer_rows': len(writers), 'physical_reach_rows': blocks})
        rows.append({'fixture_id': fixture, 'iteration': iteration, 'actual_subsets': statistics})
req(len(rows) == 6, 'exact six samples')
worth_screen = any(x['signed_zero_hand_visits'] > 0 for row in rows if row['fixture_id'] != 'river' for x in row['actual_subsets'])
D = ROOT / 'comparisons/D144-incidence'
D.mkdir(exist_ok=False)
report = {'id': 'D144', 'at': h.now(), 'status': 'pass_finite_zero_reach_incidence', 'protocol_sha256': h.sha(H / 'protocol-r2.json'), 'reader_checks': checks, 'samples': rows, 'full_results_exact': 3, 'convergence_checkpoints_exact': 23, 'writer_ownership_and_full_bounds_pass': True, 'sampled_flop_zero_reach_present': worth_screen, 'decision': 'eligible_for_frozen_whole_solve_screen' if worth_screen else 'decline_no_observed_zero_reach', 'performance_gain_claimed': False, 'candidate_accepted': False, 'scope': 'All actual parent reach words in two declared per-iteration subsets: actor0 from p1 sweep and actor1 from p0 sweep retained through p1 reuse. Unique physical writers and bounds checked from actual device metadata; unchanged ordered down-before-up source proves final owner rows equal consumed inputs. p0 actor0 is intentionally unobserved. Zero reach is a necessary condition only: finite regret-sum guard, dynamic branch cost, all-iteration incidence, production time share and speed benefit are unmeasured. Full ordinary solve records/checkpoints are exact; snapshot I/O makes timings diagnostic only.', 'raw_sha256': C['raw_sha256']}
h.save(D / 'report.json', report)
h.custody()
print(json.dumps({'status': report['status'], 'checks': checks, 'decision': report['decision'], 'samples': [{'fixture': row['fixture_id'], 'iteration': row['iteration'], 'zero_fraction_by_actor': [x['zero_hand_fraction'] for x in row['actual_subsets']]} for row in rows]}), flush=True)
