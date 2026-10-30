import json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
assert len(sys.argv) == 2
H = ROOT / 'runs/D268-record-layout'
P = h.read(H / 'protocol.json')
def verify():
    h.pin(H / 'protocol.json', sys.argv[1])
    h.pin(H / 'layout.rs', P['source_sha256'])
    for path, digest in P['input_sha256'].items():
        h.pin(path, digest)
    h.custody()
verify()
O = H / 'execution'
O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT / 'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
    h.child(['rustc', '-vV'], O, 'compiler-identity', 120)
    h.child(P['compile_command'], O, 'compile', 180)
    h.child([str(H / 'layout.exe')], O, 'layout', 120)
    rows = {}
    for line in (O / 'layout.stdout.log').read_text(encoding='utf-8').splitlines():
        tag, name, size, alignment, *offsets = line.split('|')
        assert tag == 'D268_LAYOUT' and name not in rows
        fields = ['node', 'host', 'device', 'len'] if name.endswith('ActiveBlock') else ['node', 'host', 'len', 'initial']
        if name.startswith('Proposed'):
            fields += ['device_node']
        assert len(offsets) == len(fields)
        rows[name] = {'bytes': int(size), 'alignment': int(alignment), 'offsets': dict(zip(fields, map(int, offsets)))}
    gates = {}
    for record in ['ActiveBlock', 'InactiveBlock']:
        baseline = rows['Baseline' + record]
        proposal = rows['Proposed' + record]
        gates[record + '_baseline_size'] = baseline['bytes'] == P['prospective_gate']['baseline_sizes'][record]
        gates[record + '_zero_growth'] = proposal['bytes'] == baseline['bytes']
        gates[record + '_alignment'] = baseline['alignment'] == proposal['alignment'] == 8
        offsets = proposal['offsets']
        widths = {'node': 4, 'device_node': 4, 'host': 8, 'device': 8, 'len': 8, 'initial': 16}
        occupied = []
        for field, start in offsets.items():
            occupied.extend(range(start, start + widths[field]))
        gates[record + '_nonoverlap_bounds'] = len(occupied) == len(set(occupied)) and min(occupied) >= 0 and max(occupied) < proposal['bytes']
    assert len(rows) == 4
    verify()
    h.save(H / 'report.json', {
        'id': 'D268', 'at': h.now(), 'protocol_sha256': sys.argv[1],
        'status': 'pass_record_padding_only' if all(gates.values()) else 'declined_exact_field_form',
        'rows': rows, 'gates': gates,
        'compiler_identity': (O / 'compiler-identity.stdout.log').read_text(encoding='utf-8'),
        'compiled_executable_sha256': h.sha(H / 'layout.exe'),
        'all_owned_children_terminal': True,
        'solver_constructors_CUDA_APIs_kernels_solves_performance_runs': 0,
        'accepted_main_live_protected_PTX_unchanged': True,
        'limits': P['scope'],
    })
    print(json.dumps({'status': h.read(H / 'report.json')['status'], 'rows': rows, 'gates': gates}), flush=True)
