"""Capture one owned module and inspect its two terminal entry sections."""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

H = ROOT / 'runs/D301-predicated-correction-native'
R = ROOT / 'runs/E122-resource'
BASE = ROOT / 'runs/D225-chunk-native-bypass'
assert len(sys.argv) >= 2

if sys.argv[1] == 'prepare':
    h.custody()
    h.ar.refuse_active(h.ar.live_status())
    assert not (ROOT / 'gpu-run.lock').exists()
    assert not (ROOT / 'epoch-sequence.lock').exists()
    resource = h.read(R / 'report.json')
    assert all(resource['gates'].values())
    assert h.read(ROOT / 'runs/D300-predicated-correction-PTX/report.json')['status'] == 'pass_scoped_predicated_correction_PTX_original_words_priority_and_barriers'
    H.mkdir(exist_ok=False)
    old = h.read(BASE / 'protocol.json')
    prior = h.read(BASE / 'capture-report.json')
    capture = Path(old['capture_binary'])
    disassemble = Path(old['nvdisasm'])
    h.pin(capture, old['input_sha256'][str(capture)])
    h.pin(disassemble, old['input_sha256'][str(disassemble)])
    ptx = R / 'execution/candidate-compute_120.ptx'
    h.pin(ptx, resource['PTX_sha256']['candidate-compute_120'])
    h.pin(R / 'baseline-compute_120.ptx', '4457a101f35369c5d1d9893409e4bc8a9dc027fc4234e325b72c621f73017c12')
    h.pin(BASE / 'execution/baseline/module-0.cubin', prior['captures']['baseline']['CUBIN_sha256'])
    h.pin(BASE / 'execution/baseline/disassemble.stdout.log', prior['captures']['baseline']['SASS_sha256'])
    files = [Path(__file__), ROOT / 'epoch/common.py', R / 'protocol.json', R / 'report.json',
             ROOT / 'runs/E122-source/manifest.json',
             ROOT / 'runs/D300-predicated-correction-PTX/protocol.json', ROOT / 'runs/D300-predicated-correction-PTX/report.json',
             BASE / 'protocol.json', BASE / 'capture-report.json', BASE / 'execution/before.json',
             BASE / 'execution/baseline/module-0.cubin', BASE / 'execution/baseline/disassemble.stdout.log',
             capture, disassemble, ptx] + list(Path(old['private_dll_dir']).glob('*.dll'))
    h.save(H / 'protocol.json', {
        'id': 'D301', 'at': h.now(),
        'status': 'FROZEN_PRE_MODULE_LOAD_AND_NATIVE_DISASSEMBLY',
        'candidate_PTX': str(ptx), 'capture_binary': str(capture), 'nvdisasm': str(disassemble),
        'private_dll_dir': old['private_dll_dir'], 'baseline_capture': str(BASE / 'capture-report.json'),
        'baseline_before': str(BASE / 'execution/before.json'),
        'baseline_SASS': str(BASE / 'execution/baseline/disassemble.stdout.log'),
        'GPU_uuid': old['GPU_uuid'], 'input_sha256': {str(p): h.sha(p) for p in files},
        'required_free_bytes': 8 * 1024**3,
        'scope': 'One existing checksum-bound CUPTI resource-module callback capture of sealed candidate PTX and one nvdisasm. Reuse exact accepted same-driver baseline. Two terminal sections. No new compiler/NVRTC/application kernel/counter/injection/solver/performance/source activation.',
        'next': 'Require actualnativeup_showFSEL30to0, bothoriginalrank-conditionedadditionoperand/prioritychains andalloriginalbarriers beforefullrawdirectGPUcontrols. Bounded readers do not replace full GPU/engine/canonical/broad/material/speed qualification. No source/encoding/mask/sentinel/width/helper/flags/quality/sample rescue after genuine failure.'
    })
    print(h.sha(H / 'protocol.json'), flush=True)
    sys.exit(0)

assert sys.argv[1] == 'execute' and len(sys.argv) == 3
P = h.read(H / 'protocol.json')
O = H / 'execution'

def verify():
    h.pin(H / 'protocol.json', sys.argv[2])
    h.custody()
    for path, digest in P['input_sha256'].items():
        h.pin(path, digest)

verify()
O.mkdir(exist_ok=False)
E = O / 'candidate'
E.mkdir()
B = O / 'baseline'
B.mkdir()
with h.ar.exclusive_lock(ROOT / 'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
    gpu = h.ar.read_command(['nvidia-smi', '--query-gpu=name,uuid,driver_version', '--format=csv,noheader'])
    assert gpu['returncode'] == 0 and gpu['stdout'] == h.read(P['baseline_before'])['gpu']['stdout']
    assert P['GPU_uuid'] in gpu['stdout']
    h.save(O / 'before.json', {'at': h.now(), 'gpu': gpu, 'same_baseline_device_driver': True, 'application_kernels': 0})
    os.environ['PATH'] = P['private_dll_dir'] + os.pathsep + os.environ.get('PATH', '')
    h.child([P['capture_binary'], P['candidate_PTX'], str(E)], E, 'capture', 180)
    verify()
    markers = {}
    for line in (E / 'capture.stdout.log').read_text(encoding='utf-8').splitlines():
        prefix, payload = line.split(' ', 1)
        assert prefix in ['D098_DEVICE', 'D098_KERNEL', 'D098_MODULE', 'D098_COMPLETE']
        markers.setdefault(prefix, []).append(json.loads(payload))
    base = h.read(P['baseline_capture'])['captures']['baseline']
    assert markers['D098_DEVICE'] == base['markers']['D098_DEVICE']
    assert markers['D098_COMPLETE'] == [{'callback_errors': 0, 'modules': 1, 'kernel_launches': 0, 'solver_executions': 0, 'performance_measured': False}]
    assert len(markers['D098_MODULE']) == 1
    assert markers['D098_MODULE'][0]['same_owned_context'] and markers['D098_MODULE'][0]['elf_magic']
    assert len(markers['D098_KERNEL']) == 9
    image = E / 'module-0.cubin'
    assert image.read_bytes()[:6] == b'\x7fELF\x02\x01'
    h.child([P['nvdisasm'], '--print-code', '--print-instruction-encoding', str(image)], E, 'disassemble', 180)
    verify()
    entries = {}
    for arm, text in [('baseline', Path(P['baseline_SASS']).read_text(encoding='utf-8')),
                      ('candidate', (E / 'disassemble.stdout.log').read_text(encoding='utf-8'))]:
        entries[arm] = {}
        for entry in ['up_fold', 'up_show']:
            marker = '//--------------------- .text.' + entry + ' '
            start = text.index(marker)
            end = text.find('//--------------------- .text.', start + len(marker))
            section = text[start:end if end >= 0 else None]
            path = O / arm / (entry + '.sass.txt')
            path.write_bytes(section.encode('utf-8'))
            entries[arm][entry] = {'path': str(path), 'sha256': h.sha(path)}

h.save(H / 'capture-report.json', {
    'id': 'D301', 'at': h.now(), 'status': 'captured_predicated_correction_native_operand_review_pending',
    'protocol_sha256': sys.argv[2], 'candidate_CUBIN_sha256': h.sha(image),
    'candidate_SASS_sha256': h.sha(E / 'disassemble.stdout.log'),
    'baseline_CUBIN_sha256': base['CUBIN_sha256'], 'baseline_SASS_sha256': base['SASS_sha256'],
    'entry_sections': entries, 'candidate_markers': markers,
    'all_owned_capture_disassembly_children_terminal': True,
    'new_compilers_NVRTC_applicationkernels_solver_or_speed_samples': 0,
    'candidate_adopted': False, 'limits': P['scope']
})
verify()
print('D301 native sections captured; explicit correction operand and selector review pending.', flush=True)
