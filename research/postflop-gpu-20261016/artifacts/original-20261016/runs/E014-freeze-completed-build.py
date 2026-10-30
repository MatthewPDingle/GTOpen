"""Freeze E014 completed build after identifying an unrelated uncompiled test addition."""
import json,sys,shutil
from pathlib import Path
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016');sys.path.insert(0,str(ROOT/'tools'));import postflop_autoresearch as ar
raw=ar.RESEARCH/'runs';before=json.loads((raw/'E014-source-before-build.json').read_text());after=ar.source_identity();a=before['source_sha256'];b=after['source_sha256']
assert all(b.get(k)==v for k,v in a.items()),'a prebuild input changed'
added=set(b)-set(a);assert added=={'crates/solver/tests/postflop_direct3_controls.rs'},added
log=raw/'E014-build.jsonl';err=raw/'E014-build.stderr.log';messages=[json.loads(x) for x in log.read_text().splitlines() if x.startswith('{')]
assert messages[-1]['reason']=='build-finished' and messages[-1]['success'] is True
executables=[d for d in messages if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable')]
assert {d['target']['name'] for d in executables}=={'solver','postflop_autoresearch'}
record={'id':'E014-build-freeze-recovery','created_at':ar.now(),'compiler_success':True,'initial_freeze_failure':'source snapshot equality assertion failed after completed Cargo build','changed_or_removed_prebuild_inputs':[],'added_uncompiled_files':{k:b[k] for k in added},'compiled_test_targets':[d['target']['name'] for d in executables],'reason':'A separate supplemental test was created during compilation but was neither an input to nor a target of this explicit --lib --test postflop_autoresearch build. Every prebuild source/input hash remains exact. No runtime evidence was recorded before resolving the freeze check.','after_snapshot':after}
ar.atomic_json(raw/'E014-build-freeze-recovery.json',record)
command=['cargo','test','--release','-p','solver','--features','gpu','--lib','--test','postflop_autoresearch','--no-run','--message-format=json']
for d in executables:
 name=d['target']['name'];dest=ar.RESEARCH/'binaries'/f'E014-{name}.exe';assert not dest.exists();shutil.copyfile(d['executable'],dest)
 manifest={'binary_sha256':ar.sha256(dest),'built_at':ar.now(),**before,'build_command':command,'build_log':str(log),'build_log_sha256':ar.sha256(log),'build_stderr_log':str(err),'patch':str(raw/'E014.patch'),'patch_sha256':ar.sha256(raw/'E014.patch'),'source_copies':str(raw/'E014-source'),'source_matches_prebuild':True,'source_match_scope':'All prebuild source/input hashes; separate uncompiled supplemental-test addition documented','freeze_recovery':str(raw/'E014-build-freeze-recovery.json'),'freeze_recovery_sha256':ar.sha256(raw/'E014-build-freeze-recovery.json'),'candidate':'E014','change':'Stable same-level direct-three action partition and unchanged arithmetic in dedicated kernel'}
 ar.atomic_json(dest.with_suffix('.manifest.json'),manifest);print(name,manifest['binary_sha256'])
