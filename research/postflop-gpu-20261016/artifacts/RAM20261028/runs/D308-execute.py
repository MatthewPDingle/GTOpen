"""Own compiler/module/capture/disassembly only, with no kernel launches."""
import json, os, re, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D308-packed-arithmetic'
assert len(sys.argv) == 2
P = h.read(H / 'protocol.json')
O = H / 'execution'

def verify():
    h.pin(H / 'protocol.json', sys.argv[1])
    h.custody()
    for path, digest in P['input_sha256'].items():
        h.pin(path, digest)

def entries(text):
    result = {}
    for match in re.finditer(r'\.visible \.entry (\w+)\(', text):
        opening = text.index('{', match.end())
        index, depth = opening + 1, 1
        while depth:
            depth += (text[index] == '{') - (text[index] == '}')
            index += 1
        result[match[1]] = text[match.start():index]
    return result

def normalized(text):
    text = re.sub(r'\$L__BB\d+_(\d+)', r'$L__BB_FUNCTION_\1', text)
    text = re.sub(r'__local_depot\d+', '__local_depot_FUNCTION', text)
    return re.sub(r'\$L__func_(begin|end)\d+', r'$L__func_\1_FUNCTION', text)

verify()
O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT / 'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
    gpu = h.ar.read_command(['nvidia-smi', '--query-gpu=name,uuid,driver_version', '--format=csv,noheader'])
    assert gpu['stdout'] == h.read(P['baseline_before'])['gpu']['stdout'] and P['GPU_uuid'] in gpu['stdout']
    h.save(O / 'before.json', {'at': h.now(), 'gpu': gpu, 'application_kernels': 0})
    h.child(P['rustc_command'], O, 'rustc', 300)
    verify()
    h.child([str(H / 'probe.exe'), str(O)], O, 'probe', 300)
    verify()
    markers = [json.loads(line.split('D308_RESOURCE ', 1)[1]) for line in (O / 'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'D308_RESOURCE ' in line]
    assert len(markers) == 21 and markers[-1]['resource_rows'] == 20
    assert markers[-1]['application_kernel_launches'] == markers[-1]['device_array_allocations'] == markers[-1]['solver_or_speed_runs'] == 0
    baseline = entries((H / 'accepted-baseline.ptx').read_text(encoding='utf-8'))
    candidate = entries((O / 'primitive-compute_120.ptx').read_text(encoding='utf-8'))
    assert set(baseline) == set(P['original_entries']) and set(candidate) == set(baseline) | {'scalar_regret_pair', 'packed_regret_pair'}
    rows = {(row['variant'], row['kernel']): row for row in markers[:-1]}
    gates = {}
    keys = ['registers', 'local_bytes_per_thread', 'constant_bytes', 'static_shared_bytes', 'dynamic_shared_bytes', 'max_threads', 'occupancy_by_threads', 'context_stack_after']
    for name in P['original_entries']:
        gates[name + ':original_PTX_alpha_exact'] = normalized(baseline[name]) == normalized(candidate[name])
        gates[name + ':original_resources_exact'] = all(rows['baseline', name][key] == rows['diagnostic', name][key] for key in keys)
    a, b = candidate['scalar_regret_pair'], candidate['packed_regret_pair']
    gates['primitive_same6paramABI'] = a.split('{', 1)[0].replace('scalar_regret_pair', 'PAIR') == b.split('{', 1)[0].replace('packed_regret_pair', 'PAIR') and a.split('{', 1)[0].count('.param ') == 6
    gates['one_packed_SUB_and_FMA_noFTZ'] = b.count('sub.rn.f32x2') == b.count('fma.rn.f32x2') == 1 and '.ftz' not in b
    for name in ['scalar_regret_pair', 'packed_regret_pair']:
        row = rows['diagnostic', name]
        gates[name + ':ordinary_fit'] = row['local_bytes_per_thread'] == row['static_shared_bytes'] == row['dynamic_shared_bytes'] == 0 and row['max_threads'] >= 256 and all(count > 0 for width, count in row['occupancy_by_threads'])
    h.save(H / 'resource-report.json', {'id': 'D308-resource', 'at': h.now(), 'gates': gates, 'resource_rows': markers[:-1],
        'all_gates_pass': all(gates.values()), 'PTX_sha256': h.sha(O / 'primitive-compute_120.ptx'), 'application_kernel_launches': 0})
    assert all(gates.values()), [key for key, value in gates.items() if not value]
    E = O / 'capture'
    E.mkdir()
    os.environ['PATH'] = P['private_dll_dir'] + os.pathsep + os.environ.get('PATH', '')
    h.child([P['capture_binary'], str(O / 'primitive-compute_120.ptx'), str(E)], E, 'capture', 180)
    verify()
    complete = [json.loads(line.split(' ', 1)[1]) for line in (E / 'capture.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('D098_COMPLETE ')]
    assert complete == [{'callback_errors': 0, 'modules': 1, 'kernel_launches': 0, 'solver_executions': 0, 'performance_measured': False}]
    cubin = E / 'module-0.cubin'
    assert cubin.read_bytes()[:6] == b'\x7fELF\x02\x01'
    h.child([P['nvdisasm'], '--print-code', '--print-instruction-encoding', str(cubin)], E, 'disassemble', 180)
    verify()
    sass = (E / 'disassemble.stdout.log').read_text(encoding='utf-8')
    sections = {}
    for name in ['scalar_regret_pair', 'packed_regret_pair']:
        marker = '//--------------------- .text.' + name + ' '
        start = sass.index(marker)
        end = sass.find('//--------------------- .text.', start + len(marker))
        section = sass[start:end if end >= 0 else None]
        path = E / (name + '.sass.txt')
        path.write_bytes(section.encode())
        sections[name] = {'path': str(path), 'sha256': h.sha(path)}
    h.save(H / 'capture-report.json', {'id': 'D308-capture', 'at': h.now(), 'status': 'native_primitive_sections_captured_review_pending',
        'sections': sections, 'PTX_sha256': h.sha(O / 'primitive-compute_120.ptx'), 'CUBIN_sha256': h.sha(cubin),
        'all_owned_children_terminal': True, 'application_kernel_launches': 0, 'solver_or_speed_runs': 0,
        'scope': 'OneNVRTCcompile/twooriginal+diagnosticresource modules/oneCUPTIcapture+nvdasm, no arrays/kernels/counters/solver/sourceactivation.'})
verify()
print(json.dumps({'resource_pass': all(gates.values()), 'native_sections': sections, 'application_kernel_launches': 0}), flush=True)
