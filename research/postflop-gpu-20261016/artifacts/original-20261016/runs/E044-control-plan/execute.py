"""E044 ordinary suite and exact accepted-writer GPU lifecycle, each once."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2
old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
M=old.read(P['source_manifest']);BASE=M['accepted_source_sha256']
expected=BASE|{n:v['candidate_sha256'] for n,v in M['owned'].items()}
build=old.ROOT/'runs/E044-final-build';done=old.read(build/'complete.json');terminal=old.read(build/'terminal.json')
assert done['all_compilers_terminal'] and terminal['returncode']==0 and terminal['complete_sha256']==old.sha(build/'complete.json')
for p,h in done['evidence_sha256'].items():old.pin(p,h)
binary=Path(P['binary']);mp=Path(P['manifest']);b=old.read(mp)
old.pin(binary,b['binary_sha256']);assert b['source_sha256']==expected
assert b['build_protocol_sha256']==P['build_protocol_sha256'] and b['cargo_artifact']['features']==['gpu']
old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
OUT=old.ROOT/'runs/E044-control-execution';assert not OUT.exists();OUT.mkdir()
assert not Path(P['output_dir']).exists()
status=old.read(old.ar.STATUS)
for identity in [P['unit_id'],P['gpu_id']]:
 assert not (old.ROOT/'runs'/identity).exists() and not any(r['id']==identity for r in status['experiments'])
old.save(OUT/'invocation.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'execute_script_sha256':old.sha(HERE/'execute.py'),'binary_sha256':old.sha(binary),'manifest_sha256':old.sha(mp),'build_terminal_sha256':old.sha(build/'terminal.json'),'raw_output_dir':P['output_dir'],'ids_and_output_previously_absent':True})

def run(identity,test,ordinary):
 old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 env=old.env();env.pop('E044_CONTROL_DIR',None)
 if not ordinary:env['E044_CONTROL_DIR']=P['output_dir']
 command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E044 '+identity,'--kind','validation','--binary',str(binary),'--build-manifest',str(mp),'--test',test]
 if ordinary:command+=['--not-ignored']
 old.child(command,OUT,identity,env,1200)
 old.custody()
 r=old.read(old.ROOT/'runs'/identity/'report.json');rawp=old.ROOT/'runs'/identity/'stdout.log';old.pin(rawp,r['stdout_sha256']);raw=rawp.read_text(encoding='utf-8')
 assert r['returncode']==0 and r['status']=='measured' and r['results']==[]
 assert r['binary_sha256']==old.sha(binary) and r['binary_build_manifest']['data']==b and r['binary_build_manifest']['sha256']==old.sha(mp)
 assert r['provenance']['source_sha256']==BASE and r['binary_build_manifest']['binary_hash_verified']
 expected_inventory=[('84','0','5','0','0')] if ordinary else [('1','0','0','0','88')]
 assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==expected_inventory
 assert 'DISCOUNT_STAGE_DRAIN_ERROR' not in raw
 return r,raw

unit,uraw=run(P['unit_id'],'*',True)
assert unit['test_pass_count']==84
gpu,graw=run(P['gpu_id'],P['test_filter'],False)
summary=old.read(Path(P['output_dir'])/'evidence.json')
markers=[json.loads(x.split('E044_DISCOUNT_CONTROL ',1)[1]) for x in graw.splitlines() if 'E044_DISCOUNT_CONTROL ' in x]
assert len(markers)==15 and markers[-1]==summary and summary['stage']=='complete'
assert [c['name'] for c in summary['cases']]==P['cases']
for c in summary['cases']:
 r=c['result'];assert len(r['files'])==45 and r['iterations']==24 and r['profiled_iteration']==20
 assert r['pinned_pipeline_eligible'] is (not r['tiny'])
 for k in ['gpu_raw_exact','cpu_query_save_exact','locks_resume_exact','full_and_strategy_readback_reset_slots','staging_geometry_unchanged','cleanup_complete']:assert r[k]
assert len(summary['drop_controls'])==3
for d in summary['drop_controls']:assert d['drain_calls']==1 and d['stream_ready_before_field_release'] and d['cleanup_complete']
assert summary['candidate_solver_size']<=summary['original_solver_size']+32
old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'unit_passed':84,'unit_ignored':5,'gpu_selected_passed':1,'gpu_cases':14,'raw_files':630,'raw_pairs':308,'drop_modes':3,'unit_report_sha256':old.sha(old.ROOT/'runs'/P['unit_id']/'report.json'),'gpu_report_sha256':old.sha(old.ROOT/'runs'/P['gpu_id']/'report.json'),'raw_summary_sha256':old.sha(Path(P['output_dir'])/'evidence.json'),'accepted162_restored':True,'main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False})
print('E04414-case lifecycle and drop controls passed; no speed measured.',flush=True)
