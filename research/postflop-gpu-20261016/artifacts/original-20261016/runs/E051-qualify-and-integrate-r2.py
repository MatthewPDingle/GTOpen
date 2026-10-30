"""Qualify E051 then integrate its exact tested CUDA source. No live deployment."""
import json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;REPO=old.REPO;APP=ar.APP;Q=ROOT/'comparisons/E051-qualification-r2';I=ROOT/'runs/E051-main-integration-r2'
old.custody();assert not (ROOT/'gpu-run.lock').exists();ar.refuse_active(ar.live_status());assert not Q.exists() and not I.exists();Q.mkdir();I.mkdir()
paths={'source':ROOT/'runs/E051-source/source-review.json','resource':ROOT/'comparisons/E051-resource-root-check/report.json','raw':ROOT/'comparisons/E051-kernel-control/report.json','primary':ROOT/'comparisons/E051-root-crosscheck/report.json','confirmation':ROOT/'comparisons/E051-fresh16-root-check/report.json','broader':ROOT/'comparisons/E051-broader-root-check/report.json','remaining':ROOT/'comparisons/E051-remaining-root-check/report.json','capacity':ROOT/'comparisons/E051-remaining-native-r3/capacity.json','holdout':ROOT/'comparisons/E051-remaining-native-r3/holdout.json','cumulative':ROOT/'comparisons/E051-remaining-native-r3/cumulative.json'}
r={k:old.read(p) for k,p in paths.items()}
assert r['resource']['status']=='pass_resource_feasibility_only' and r['resource']['exact_abi_other8_entries'] is True and r['resource']['registers_before_after']==[66,62] and r['resource']['local_bytes_per_thread']==64 and r['resource']['shared_bytes']==0
assert r['raw']['status']=='pass_scoped_up_action_raw_equivalence' and r['raw']['cases']==819 and r['raw']['full_raw_files_equal'] is True
assert r['confirmation']['status']=='pass_timing_only' and r['confirmation']['aggregate_gain_pct']>=1 and r['confirmation']['positive_pairs']>=13 and r['confirmation']['all96results_736checkpoints_exact'] is True
assert all(x>0 for x in r['confirmation']['block_median_gains_pct']) and all(x>0 for x in r['confirmation']['order_strata_median_gains_pct'].values()) and r['confirmation']['pair_median_gain_pct']>0
assert r['broader']['status']=='pass_broader_only' and r['remaining']['status']=='pass_remaining_root_replay' and r['remaining']['checks_passed']==153
assert r['capacity']['status']=='pass_exact_actual_owned_accounting' and r['capacity']['all6cases_owned_capacity_and_workspace_host_sizes_exact'] is True
assert r['holdout']['status']=='pass_fixed_holdout_nonregression' and r['holdout']['strict_guard_failed'] is False
assert r['cumulative']['status']=='pass_fresh_original_cumulative' and r['cumulative']['observed_gain_pct']>=1 and not any(x['failed'] for x in r['cumulative']['strict_fixture_guards'])
candidate=ROOT/'runs/E051-source/candidate.cu';rel='crates/solver/src/gpu/kernels.cu';candidatehash=old.sha(candidate);assert candidatehash=='a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647';newbase=old.BASE|{rel:candidatehash}
manifest=old.read(ROOT/'binaries/E051-postflop_autoresearch.manifest.json');assert manifest['source_sha256']==newbase
scope='Registered three-fixture compressed postflop complete cycles on RTX5090, warm driver cache. Includes tree/CPU allocation, GPU init/NVRTC/JIT, same-quality solve/checks and full readback. Excludes Cargo, fingerprints, final destruction, API/browser latency and saving. Separate fresh16-pair incremental confirmation and fresh3-pair original comparison; percentages are never added. Exact controls and allocation/resource evidence cover registered cases; no universal, cold-start, other-device or F32-speed claim.'
qual={'at':old.now(),'id':'E051-qualification','status':'qualified_for_source_integration','candidate':'E051','decision':'accept_no_observed_tradeoff_in_registered_scope','minimum_gain_pct':1.0,'initial_gain_pct':1.8437102310814113,'fresh16_gain_pct':r['confirmation']['aggregate_gain_pct'],'fresh16_positive_pairs':r['confirmation']['positive_pairs'],'fresh_original_cumulative_gain_pct':r['cumulative']['observed_gain_pct'],'holdout_gain_pct':r['holdout']['observed_gain_pct'],'exactness':{'raw_kernel_cases':819,'fresh_confirmation_full_results':96,'fresh_confirmation_checkpoints':736,'state_menu_resume_snapshots_each':160,'f32_fixtures_each':3,'gpu_cpu_tolerance_tests_each':6,'continuation_sweeps_each':160,'stored_bitwise_passes_each':720,'complete_save_files_each':3,'capacity_actual_cases_each':6,'holdout_full_raw_files':6,'cumulative_full_results':18},'material':'Actual owned metadata/canonical state/workspace/host sizes exact in6existing cases; identical host/graph topology and ABI; actual compiled registers66to62, local64/shared0 unchanged. Device-wide meminfo observations are preserved but not treated as solver-only allocations. Driver/module/allocator/temporary peak overhead and forced spill are outside owned-payload accounting. No new host allocation/graph/ABI/storage behavior introduced.','scope':scope,'source_sha256':newbase,'evidence_sha256':{str(p):old.sha(p) for p in paths.values()},'root_replay_external_independent_review':False,'source_integrated':False,'live_deployed':False}
old.save(Q/'pre-integration.json',qual)
# The sole production mutation is the already qualified and hashed CUDA file.
old.custody();beforeheads={name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() for name,root in [('research',REPO),('main',APP)]}
for name,root in [('research',REPO),('main',APP)]:
 p=root/rel;assert old.sha(p)==old.BASE[rel];assert subprocess.check_output(['git','diff','--cached','--name-only','--',rel],cwd=root,text=True).strip()==''
 (I/(name+'-before.cu')).write_bytes(p.read_bytes());p.write_bytes(candidate.read_bytes());assert old.sha(p)==candidatehash
 result=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--check','--',rel],cwd=root,text=True,capture_output=True);assert result.returncode==0,(name,result.stdout,result.stderr)
 assert ar.source_identity()['source_sha256']==newbase
 cmd=['git','-c','core.autocrlf=false','commit','--only','-m','perf: schedule postflop strategy stores with action expectations','--',rel]
 result=subprocess.run(cmd,cwd=root,text=True,capture_output=True);old.save(I/(name+'-commit.json'),{'at':old.now(),'command':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr});assert result.returncode==0
 heads={name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() for name,root in [('research',REPO),('main',APP)]}
 integration={'at':old.now(),'status':'source_integrated_exact_tested_cuda','heads_before':beforeheads,'heads_after':heads,'source_sha256':newbase,'only_production_file_changed':rel,'candidate_cuda_sha256':candidatehash,'live_deployed':False,'pre_integration_qualification_sha256':old.sha(Q/'pre-integration.json')}
old.save(I/'report.json',integration)
# Pin a NEW helper/protection epoch; never edit historical common.py or pins.
A=ROOT/'runs/accepted-E051';A.mkdir();old.save(A/'baseline.json',{'at':old.now(),'candidate':'E051','source_sha256':newbase,'primary_binary':str(ROOT/'binaries/E051-postflop_autoresearch.exe'),'primary_manifest':str(ROOT/'binaries/E051-postflop_autoresearch.manifest.json'),'qualification_pre_sha256':old.sha(Q/'pre-integration.json')})
protected=old.read(ROOT/'runs/small-gain-confirmation-plan/protected-main.json');protected.update(git_head=heads['main']);protected['source_sha256'][rel]=candidatehash;old.save(A/'protected-main.json',protected)
old.save(A/'preexisting-target-artifacts.json',old.P['preexisting_target_artifacts'])
helper='''"""Accepted E051 custody epoch; historical helpers remain unchanged."""
import sys,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path(r'S:\\GTOpen-research\\postflop-gpu-20261016')
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as historical
read,sha,pin,save,now,env,child=historical.read,historical.sha,historical.pin,historical.save,historical.now,historical.env,historical.child
ar,compare,REPO=historical.ar,historical.compare,historical.REPO
BASE=read(HERE/'baseline.json')['source_sha256']
def custody():
 assert ar.source_identity()['source_sha256']==BASE
 for n,r in read(HERE/'preexisting-target-artifacts.json').items():pin(REPO/n,r['sha256']);assert (REPO/n).stat().st_size==r['bytes']
 m=read(HERE/'protected-main.json');app=Path(m['root'])
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=app,text=True).strip()==m['git_head']
 for n,h in m['source_sha256'].items():pin(app/n,h)
 for n in m['absent_research_paths']:assert not (app/n).exists()
 pin(m['live_path'],m['live_sha256'])
 assert not subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=REPO,text=True).strip()
 assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=REPO,text=True).splitlines())==set(read(HERE/'preexisting-target-artifacts.json'))
 return BASE
'''
(A/'common_e051.py').write_text(helper,encoding='utf-8',newline='\n')
sys.path.insert(0,str(A));import common_e051 as current;current.custody()
qual.update(at=old.now(),status='accepted_source_integrated',source_integrated=True,live_deployed=False,integration_sha256=old.sha(I/'report.json'),new_epoch=str(A),new_epoch_sha256={str(p):old.sha(p) for p in A.iterdir() if p.is_file()},heads=heads)
old.save(Q/'report.json',qual)
old.save(I/'terminal.json',{'at':old.now(),'all_owned_children_terminal':True,'source_integrated':True,'no_compiler_or_native_rerun':True,'reason':'Byte-exact qualified compiled CUDA source; no host/evaluator change.','live_deployed':False})
print(json.dumps({'status':'accepted_source_integrated','incremental_gain_pct':qual['fresh16_gain_pct'],'cumulative_gain_pct':qual['fresh_original_cumulative_gain_pct'],'heads':heads,'qualification_sha256':old.sha(Q/'report.json'),'live_deployed':False}),flush=True)
