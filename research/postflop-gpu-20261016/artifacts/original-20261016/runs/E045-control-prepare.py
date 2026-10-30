"""Freeze E045's one ordinary suite and native integer proof controls."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
HERE=ROOT/'runs/E045-control-plan';HERE.mkdir()
script='''"""E045 ordinary suite once after both compilers are terminal."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
ROOT=old.ROOT;old.custody();assert not (ROOT/'gpu-run.lock').exists()
B=ROOT/'runs/E045-final-build';D=old.read(B/'complete.json');T=old.read(B/'terminal.json')
assert D['all_compilers_terminal'] and T['returncode']==0 and T['complete_sha256']==old.sha(B/'complete.json')
for p,h in D['evidence_sha256'].items():old.pin(p,h)
M=old.read(P['source_manifest']);expected=M['accepted_source_sha256']|{n:v['candidate_sha256'] for n,v in M['owned'].items()}
binary=ROOT/'binaries/E045-solver.exe';mp=binary.with_suffix('.manifest.json');bm=old.read(mp);old.pin(binary,bm['binary_sha256'])
assert bm['source_sha256']==expected and bm['build_protocol_sha256']==P['build_protocol_sha256'] and bm['cargo_artifact']['features']==['gpu']
OUT=ROOT/'runs/E045-control-execution';assert not OUT.exists();OUT.mkdir()
identity=P['unit_id'];assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in old.read(old.ar.STATUS)['experiments'])
old.save(OUT/'invocation.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'build_terminal_sha256':old.sha(B/'terminal.json'),'all_ids_previously_absent':True})
cmd=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E045 ordinary and exact integer controls','--kind','validation','--binary',str(binary),'--build-manifest',str(mp),'--test','*','--not-ignored']
old.child(cmd,OUT,identity,old.env(),1200)
old.custody();r=old.read(ROOT/'runs'/identity/'report.json');rawp=ROOT/'runs'/identity/'stdout.log';old.pin(rawp,r['stdout_sha256']);raw=rawp.read_text(encoding='utf-8')
assert r['returncode']==0 and r['status']=='measured' and r['results']==[] and r['test_pass_count']==86
assert r['binary_sha256']==bm['binary_sha256'] and r['binary_build_manifest']['data']==bm and r['binary_build_manifest']['sha256']==old.sha(mp)
assert r['provenance']['source_sha256']==old.BASE and r['binary_build_manifest']['binary_hash_verified']
assert re.findall(r'test result: ok\\. (\\d+) passed; (\\d+) failed; (\\d+) ignored; (\\d+) measured; (\\d+) filtered out;',raw)==[('86','0','4','0','0')]
integer=[json.loads(x.split('E045_INTEGER_OR_CONTROL ',1)[1]) for x in raw.splitlines() if 'E045_INTEGER_OR_CONTROL ' in x]
predicate=[json.loads(x.split('E045_FULL_PREDICATE_CONTROL ',1)[1]) for x in raw.splitlines() if 'E045_FULL_PREDICATE_CONTROL ' in x]
assert len(integer)==len(predicate)==1 and integer[0]['checks']==3516 and integer[0]['threads']==[1,2,16]
assert integer[0]['inputs_unchanged'] and integer[0]['raw_integer_or_exact']
assert predicate==[{'cases':576,'inputs_unchanged':True,'accepted_original_exact':True}]
old.save(OUT/'complete.json',{'at':old.now(),'status':'pass_scoped_parallel_zero_proof','protocol_sha256':sys.argv[1],'unit_passed':86,'unit_ignored':4,'integer_or_checks':3516,'full_predicate_cases':576,'unit_report_sha256':old.sha(ROOT/'runs'/identity/'report.json'),'stdout_sha256':old.sha(rawp),'integer_marker':integer[0],'predicate_marker':predicate[0],'source_accepted162_restored':True,'main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Fixed CPU corpus against serial integer folds and exact accepted predicate; no universal timing, GPU-path or resource claim.'})
print('E045 ordinary86/4 and fixed integer controls passed; timing not measured.',flush=True)
'''
(HERE/'execute.py').write_text(script,encoding='utf-8')
P={'id':'E045-controls','at':old.now(),'status':'FROZEN_PRE_NATIVE','source_manifest':str(ROOT/'runs/E045-design/manifest.json'),'build_protocol_sha256':old.sha(ROOT/'runs/E045-build-plan/build-protocol.json'),'unit_id':'V045-unit','input_sha256':{str(p):old.sha(p) for p in [HERE/'execute.py',ROOT/'runs/E045-design/manifest.json',ROOT/'runs/E045-design/source-review.json',ROOT/'runs/E045-design/candidate-arena.rs',ROOT/'runs/E045-build-plan/build-protocol.json',ROOT/'runs/small-gain-confirmation-plan/common.py',old.ar.REPO/'tools/postflop_autoresearch.py']},'ordinary_tests_expected':86,'ordinary_ignored_expected':4,'integer_or_checks_expected':3516,'full_predicate_cases_expected':576,'runtime_authority':'User-authorized local ongoing research; root review only. No deployment or adoption.'}
old.save(HERE/'protocol.json',P)
print(old.sha(HERE/'protocol.json'))
