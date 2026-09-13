"""Independently audit D08 artifacts; static instructions are not stall metrics."""
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / 'raw'
LAB = HERE.parents[3]

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def digest(path):
    return hashlib.file_digest(Path(path).open('rb'), 'sha256').hexdigest()

def instructions(path, name):
    text = path.read_text(encoding='utf-8')
    assert re.search(r'\.target\s+sm_86\b', text)
    start = text.index('\n.text.' + name + ':')
    end = text.find('\n//---------------------', start)
    body = text[start:end if end != -1 else len(text)]
    ops = re.findall(r'/\*[0-9a-f]+\*/\s+(?:@!?\w+\s+)?([A-Z][A-Z0-9_.]*)\b[^;]*;', body)
    assert ops
    counts = collections.Counter(ops)
    return dict(instructions=len(ops), non_nop=len(ops)-counts['NOP'], operations=dict(sorted(counts.items())))

def main():
    manifest = read(RAW/'d08-redistribution-manifest.json')
    tools = {}
    for component, file in [('nsight_compute','d08-tool-provenance.json'), ('cuda_nvdisasm','d08-disasm-provenance.json')]:
        p = read(RAW/file)
        spec = manifest[component]['windows-x86_64']
        archive = LAB/'target/research-tools'/Path(spec['relative_path']).name
        assert archive.stat().st_size == int(spec['size']) == p['archive_bytes']
        assert digest(archive) == spec['sha256'] == p['archive_sha256']
        assert digest(p['executable']) == p['executable_sha256']
        assert p['download_url'] == 'https://developer.download.nvidia.com/compute/cuda/redist/'+spec['relative_path']
        tools[component] = dict(version=manifest[component]['version'], sha256=p['archive_sha256'])
    assert digest(RAW/'d08-redistribution-manifest.json') == read(RAW/'d08-tool-provenance.json')['manifest_sha256']
    assert '2025.4.1.0' in (RAW/'d08-ncu-version.txt').read_text()
    runs = {}
    for name, code in [('d08-counter-smoke-v1',1), ('d08-native-v1',1), ('d08-native-v2',0)]:
        r = read(RAW/(name+'-exit.json'))
        assert r['returncode'] == code and r['reason'] is None and 0 < r['seconds'] < 120
        assert r['source_diff_sha256'] == hashlib.sha256(b'').hexdigest()
        for p, h in r['inputs'].items():
            source = Path(p)
            if name == 'd08-counter-smoke-v1' and source.name == 'D08_PROTOCOL.md':
                source = HERE/'artifacts/d08-counter-protocol.md'
            if name == 'd08-native-v1' and source.name == 'inspect_d08_native.py':
                source = HERE/'artifacts/d08-native-v1.py'
            assert digest(source) == h, str(source)
        if runs:
            assert r['solver_source_files'] == next(iter(runs.values()))['solver_source_files']
        runs[name] = r
    # Verify the source snapshot against its recorded Git state, independently of today's checkout.
    run = runs['d08-native-v2']
    for p,h in run['solver_source_files'].items():
        data = subprocess.check_output(['git','show',run['source_commit']+':'+Path(p).as_posix()], cwd=LAB)
        assert hashlib.sha256(data).hexdigest() == h, p
    smoke = (RAW/'d08-counter-smoke-v1.log').read_text()
    assert 'ERR_NVGPUCTRPERM' in smoke and '1 passed; 0 failed' in smoke and 'Disconnected from process' in smoke
    assert 'AssertionError' in (RAW/'d08-native-v1.log').read_text()
    native = RAW/'d08-native-v2'
    records = read(native/'manifest.json')
    assert records['cuda_driver_api_version'] == 13010 and len(records['records']) == 4
    for r in records['records']:
        assert digest(RAW/r['ptx_file']) == r['ptx_sha256']
        assert digest(native/(r['label']+'.cubin')) == r['cubin_sha256']
        assert (native/(r['label']+'.cubin')).stat().st_size == r['cubin_bytes']
        # The producer hashes subprocess text before Windows write_text expands LF.
        sass = (native/(r['label']+'.sass')).read_text(encoding='utf-8')
        assert hashlib.sha256(sass.encode('utf-8')).hexdigest() == r['sass_sha256']
        resources = r['resources']
        assert r['direct_and_linked_resources_equal'] == (resources['direct_ptx'] == resources['linked_cubin'])
        for mode, kernels in resources.items():
            for name, attrs in kernels.items():
                assert attrs['local_bytes'] == 0
                assert attrs['registers'] == (54 if 'terminal' in name else 26)
                assert attrs['shared_bytes'] == ((84 if mode == 'direct_ptx' else 80) if 'terminal' in name else 0)
    counts = {name:instructions(native/(name+'.sass'),'pf_predicated_cdf') for name in ['c12-reference','c12-candidate']}
    assert [counts[n]['non_nop'] for n in counts] == [187,182]
    for c in counts.values():
        assert c['operations']['SHFL.UP'] == 30 and c['operations']['FADD'] == 41
        assert c['operations']['SEL'] == 1 and not any(k.startswith('CALL') for k in c['operations'])
    assert instructions(native/'c09-exact.sass','pf_exact_reuse_cdf') == counts['c12-reference']
    result = dict(status='Diagnostic complete - counters unavailable', retained=False,
        hardware_counters_available=False, source_and_artifact_hashes_verified=True,
        tools=tools, static_cdf_counts=counts,
        archived_sass_byte_hashes={p.name:digest(p) for p in sorted(native.glob('*.sass'))},
        inference='The linked reference already has only one SEL; the PTX simplification saves five static non-NOP instructions, not thirty selections.',
        scope='Driver-link compilation differs from direct module loading. No exact runtime-binary, dynamic instruction, stall, throughput or convergence claim. Retained C09 unchanged.')
    output = RAW/'d08-verified.json'
    if output.exists():
        assert read(output) == result
    else:
        output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
