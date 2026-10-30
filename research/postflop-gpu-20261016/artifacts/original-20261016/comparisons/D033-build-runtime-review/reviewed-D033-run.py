"""Execute the frozen graph diagnostic once through the existing serialized runner."""
import json, os, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
assert not (ar.RESEARCH/'gpu-run.lock').exists(),'A build or GPU operation still holds the lock; do not start'
name='D033-solver';identity='D033R1'
path=ar.RESEARCH/'binaries'/(name+'.manifest.json')
manifest=json.loads(path.read_text(encoding='utf-8'))
binary=ar.RESEARCH/'binaries'/(name+'.exe')
assert ar.sha256(binary)==manifest['binary_sha256']
assert ar.source_identity()['source_sha256']==manifest['source_sha256']
for relative,expected in manifest['diagnostic_inputs_sha256'].items():
    assert ar.sha256(ar.RESEARCH/relative)==expected,relative
status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
assert not any(x['id']==identity for x in status['experiments'])
assert not (ar.RESEARCH/'runs'/identity).exists()
command=[sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title','D033 captured-graph device-event diagnostic',
 '--kind','diagnostic','--binary',str(binary),'--build-manifest',str(path),
 '--test','gpu::graph_device_events::captured_graph_device_event_diagnostic','--fixture','rainbow']
env=os.environ.copy()
env.update(POSTFLOP_AUTORESEARCH_PROFILE='0',POSTFLOP_AUTORESEARCH_STORAGE='compressed',RAYON_NUM_THREADS='16')
out=ar.RESEARCH/'runs/D033-execution';out.mkdir(exist_ok=False)
ar.atomic_json(out/'invocation.json',{'at':ar.now(),'command':command,'binary_sha256':manifest['binary_sha256'],
 'build_manifest_sha256':ar.sha256(path),'diagnostic_inputs_sha256':manifest['diagnostic_inputs_sha256'],
 'fixed_protocol_sha256':ar.sha256(ar.RESEARCH/'runs/D033-graph-event-design/protocol.json'),
 'actual_run':identity,'logical_dashboard_row':'D033','performance_acceptance':False,'build_complete_before_launch':True})
with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
    result=subprocess.run(command,cwd=repo,env=env,stdout=stdout,stderr=stderr)
ar.atomic_json(out/'exit.json',{'at':ar.now(),'returncode':result.returncode})
assert result.returncode==0,(out/'stderr.log').read_text(encoding='utf-8',errors='replace')
report=json.loads((ar.RESEARCH/'runs'/identity/'report.json').read_text(encoding='utf-8'))
assert report['status']=='measured' and report['test_pass_count']==1
print('D033R1 native diagnostic completed; independent raw-evidence assessment pending.',flush=True)
