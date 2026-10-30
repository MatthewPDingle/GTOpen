"""Run the frozen E040 control once after all compilers have terminated."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2
old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
for key in ['source_manifest','build_protocol']:old.pin(P[key]['path'],P[key]['sha256'])
M=old.read(P['source_manifest']['path']);BASE=M['accepted_source_sha256']
expected=BASE|{n:v['candidate_sha256'] for n,v in M['owned'].items()}
build=old.ROOT/'runs/E040-final-build';complete=old.read(build/'complete.json');terminal=old.read(build/'terminal.json')
assert complete['all_compilers_terminal'] and terminal['returncode']==0 and terminal['complete_sha256']==old.sha(build/'complete.json')
for p,h in complete['evidence_sha256'].items():old.pin(p,h)
binary=Path(P['binary']);manifest=Path(P['manifest']);b=old.read(manifest)
old.pin(binary,b['binary_sha256']);assert b['source_sha256']==expected
assert b['build_protocol_sha256']==P['build_protocol']['sha256'] and b['cargo_artifact']['features']==['gpu']
old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
OUT=old.ROOT/'runs/E040-gpu-control-execution';assert not OUT.exists();OUT.mkdir()
assert not Path(P['output_dir']).exists() and not (old.ROOT/'runs'/P['native_id']).exists()
old.save(OUT/'invocation.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'execute_script_sha256':old.sha(HERE/'execute.py'),'binary_sha256':old.sha(binary),'manifest_sha256':old.sha(manifest),'build_terminal_sha256':old.sha(build/'terminal.json'),'raw_output_dir':P['output_dir'],'ids_and_output_previously_absent':True})
env=old.env();env['E040_CONTROL_DIR']=P['output_dir']
command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',P['native_id'],'--title','E040 exact async readback and drain control','--kind','validation','--binary',str(binary),'--build-manifest',str(manifest),'--test',P['test_filter']]
old.child(command,OUT,'native',env,1200)
old.custody()
r=old.read(old.ROOT/'runs'/P['native_id']/'report.json');rawpath=old.ROOT/'runs'/P['native_id']/'stdout.log';old.pin(rawpath,r['stdout_sha256']);raw=rawpath.read_text(encoding='utf-8')
assert r['returncode']==0 and r['status']=='measured' and r['test_pass_count']==1 and r['results']==[]
assert r['binary_sha256']==old.sha(binary) and r['binary_build_manifest']['data']==b and r['binary_build_manifest']['sha256']==old.sha(manifest)
assert r['provenance']['source_sha256']==BASE and r['binary_build_manifest']['binary_hash_verified']
assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','90')]
assert 'READBACK_DRAIN_ERROR' not in raw and 'E040_CONTROL_CLEANUP_ERROR' not in raw
summary=old.read(Path(P['output_dir'])/'evidence.json')
markers=[json.loads(x.split('E040_READBACK_CONTROL ',1)[1]) for x in raw.splitlines() if 'E040_READBACK_CONTROL ' in x]
assert len(markers)==5 and markers[-1]==summary and summary['stage']=='complete' and len(summary['cases'])==4
for i,c in enumerate(summary['cases']):
 assert c['forced_pipelined_arenas']==P['expected_forced_pipelined_arenas'][i]
 assert c['default_pipelined_arenas']==P['expected_default_pipelined_arenas'][i]
 assert c['mixed_pipelined_arenas']==P['expected_mixed_pipelined_arenas'][i]
 assert c['full_raw_equality'] and c['query_save_exact'] and c['repeat_restores_first'] and c['cleanup_complete'] and c['staging_identity_and_device_lengths_unchanged']
 assert len(c['faults'])==(2 if i<2 else 0)
 for f in c['faults']:
  assert f['drain_calls']==1 and all(f[k] for k in ['stream_ready_before_extra_sync','cpu_untouched','gpu_unchanged','reused_exact'])
old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'selected_passed':1,'cases':4,'full_raw_payloads_retained':True,'injected_exits':4,'native_report_sha256':old.sha(old.ROOT/'runs'/P['native_id']/'report.json'),'raw_summary_sha256':old.sha(Path(P['output_dir'])/'evidence.json'),'accepted162_restored':True,'main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False})
print('E040 control passed; performance remains unmeasured.',flush=True)
