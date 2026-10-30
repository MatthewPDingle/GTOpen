"""Finish original observations without rerunning or clearing the baseline failure."""
from pathlib import Path
import json,re,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
sys.path.insert(0,str(old.REPO/'tools'));import postflop_validate_controls as vc
assert len(sys.argv)==2;old.pin(H/'continuation-protocol.json',sys.argv[1]);P=old.read(H/'continuation-protocol.json');original=old.read(H/'protocol.json');E=R/'runs/E080-broader-controls-execution';M=R/'runs/E080-broader-observation-manager';O=R/'comparisons/E080-broader-observations'
def verify():
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
def summary(text):return re.findall(r'test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)
def scientific_lines(text):return[x for x in text.splitlines()if x.startswith(('FIXED ','KsQs2d:','KsQs2s:','KsQh2d:','gpu: '))]
verify();assert not M.exists()and not O.exists()and not(R/'gpu-run.lock').exists();M.mkdir();O.mkdir();completed=[]
for row in P['remaining_rows']:
    verify();old.ar.refuse_active(old.ar.live_status());assert not(R/'runs'/row['id']).exists();b=original['binaries'][row['binary']]
    with old.ar.exclusive_lock(R/'gpu-run.lock'):old.child([b['path'],'--list'],E,row['id']+'-inventory',old.env(),120)
    listed=re.findall(r'^(.+): test$',(E/(row['id']+'-inventory.stdout.log')).read_text(encoding='utf-8'),re.M);selected=listed if row['test']=='*'else[x for x in listed if row['test']in x];assert len(selected)==row['passes']
    env=old.env();env['POSTFLOP_AUTORESEARCH_STORAGE']=row['storage']
    if row['suite']=='stored':
        root=Path(row['stored_root']);assert not root.exists();root.mkdir(parents=True);env['GTO_SSD_STUDY_DIR']=str(root)
    cmd=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',row['id'],'--title','E080 broader '+row['id'],'--kind','validation','--binary',b['path'],'--build-manifest',b['manifest'],'--test',row['test']]
    if row['ordinary']:cmd.append('--not-ignored')
    failed=False
    try:old.child(cmd,E,row['id'],env,1200)
    except AssertionError:
        failed=True;receipt=old.read(E/(row['id']+'.exit.json'));assert row['suite']=='symmetry'and receipt['returncode']==1 and receipt['error']is receipt['cleanup']is None
    verify();r=old.read(R/'runs'/row['id']/'report.json');log=R/'runs'/row['id']/'stdout.log';old.pin(log,r['stdout_sha256']);text=log.read_text(encoding='utf-8')
    assert r['binary_sha256']==b['sha256']and r['binary_build_manifest']['sha256']==b['manifest_sha256']and r['provenance']['source_sha256']==old.BASE
    if row['suite']=='symmetry':
        baseline=old.read(R/'runs/V080-symmetry-baseline/report.json');bl=R/'runs/V080-symmetry-baseline/stdout.log';old.pin(bl,baseline['stdout_sha256']);bt=bl.read_text(encoding='utf-8')
        assert failed and r['status']==baseline['status']=='invalid'and r['returncode']==baseline['returncode']==101
        assert summary(text)==summary(bt)==[('FAILED','2','1','0','0','0')]
        message='Original equivalence gates failed on ["KsQs2d", "KsQs2s"]';assert message in text and message in bt
        assert scientific_lines(text)==scientific_lines(bt);assert len(scientific_lines(text))>=20
        old.save(O/'known-symmetry-failure.json',{'at':old.now(),'status':'failed_research_test_unchanged_between_baseline_and_candidate','baseline_run':'V080-symmetry-baseline','candidate_run':row['id'],'baseline_source_is_accepted':True,'both_native_exit_codes':101,'both_test_summaries':summary(text),'all_scientific_metric_and_allocation_lines_exact':True,'scientific_lines_compared':len(scientific_lines(text)),'preserved_scientific_lines':scientific_lines(text),'historical_document':P['historical_failure_document'],'historical_document_sha256':old.sha(P['historical_failure_document']),'original_test_pass':False,'thresholds_changed':False,'research_path_cleared':False,'candidate_adopted':False,'limits':'The original absolute research gate remains failed in both arms. The repository documented the same abrupt-changing-range mismatch before E080. Equality is regression evidence, not a certificate that the experimental compact trajectory is accurate or approved.'})
    else:
        assert not failed and r['returncode']==0 and r['status']=='measured'and summary(text)==[('ok','1','0','0','0',str(len(listed)-1))]
        passes=[json.loads(x.split('GPU_STORED_PASS ',1)[1])for x in text.splitlines()if'GPU_STORED_PASS 'in x];totals=[json.loads(x.split('GPU_STORED_SUMMARY ',1)[1])for x in text.splitlines()if'GPU_STORED_SUMMARY 'in x]
        assert len(passes)==720 and len({(x['entry'],x['iteration'],x['player'])for x in passes})==720 and all(x['passed']is True for x in passes)
        assert len(totals)==1 and totals[0]['passes']==720 and all(totals[0][k]is True for k in['full_device_arrays_bitwise_equal','restored_arrays_bitwise_equal','values_bitwise_equal'])
    completed.append({'id':row['id'],'suite':row['suite'],'status':r['status'],'native_returncode':r['returncode'],'report_sha256':old.sha(R/'runs'/row['id']/'report.json'),'stdout_sha256':old.sha(log)});print('Completed remaining original observation',row['id'],flush=True)
arms=[[vc.read_run(original['suite_ids'][arm][suite],suite)for suite in vc.SUITES]for arm in['baseline','candidate']];states=vc.compare(*arms);assert states['status']=='pass'and states['total_snapshots_each']==160
for suite in vc.SUITES:
    for arm in['baseline','candidate']:assert vc.canonical(vc.read_run(original['suite_ids'][arm][suite],suite)['records'])==vc.canonical(vc.read_run(original['historical_accepted_controls'][suite],suite)['records'])
for arm in['baseline','candidate']:assert old.historical.exact_raw('V080-f32-'+arm)==old.historical.exact_raw(original['f32_accepted_anchor'])
def equal(a,b):
    assert a.stat().st_size==b.stat().st_size
    with a.open('rb')as x,b.open('rb')as y:
        while True:
            left,right=x.read(8*1024*1024),y.read(8*1024*1024);assert left==right
            if not left:break
saves={arm:{}for arm in['baseline','candidate']}
for name in original['saved_names']:
    files={arm:Path(original['io_roots'][arm])/'target/research-fixtures'/name for arm in['baseline','candidate']};equal(files['baseline'],files['candidate'])
    for arm,p in files.items():saves[arm][name]={'path':str(p),'sha256':old.sha(p),'bytes':p.stat().st_size}
old.child([sys.executable,'-B',str(H/'warm.py'),P['original_protocol_sha256']],M,'large-warm',old.env(),2100)
warm=old.read(R/'comparisons/E080-large-warm-controls/report.json');assert warm['status']=='pass_six_full_raw_large_warm_states_each';verify();assert not(R/'gpu-run.lock').exists()
old.save(O/'report.json',{'id':'E080-broader-observations','at':old.now(),'status':'completed_with_known_failed_research_gate','original_frozen_absolute_batch_pass':False,'original_failed_test_rerun':False,'completed_original_remaining_rows':completed,'state_menu_resume':states,'snapshots_each':160,'F32_full_non_timing_exact':True,'postflop_GPU_tolerance_tests_each':6,'preflop_GPU_tolerance_tests_each':15,'paging_sweeps_each':160,'stored_full_state_passes_each':720,'latest_complete_saves':saves,'latest_complete_save_bytes_exact':True,'known_research_failure_report_sha256':old.sha(O/'known-symmetry-failure.json'),'large_warm_report_sha256':old.sha(R/'comparisons/E080-large-warm-controls/report.json'),'large_warm_all_full_raw_bytes_exact':True,'no_new_source_or_test_thresholds':True,'no_completed_observation_reexecuted':True,'all_owned_children_terminal':True,'candidate_adopted':False,'research_equivalence_cleared':False,'source_main_live_PTX_unchanged':True,'limits':'The experimental changing-range symmetric-continuation test remains failed in both arms, with exact scientific output parity and the same mismatch documented before this optimization. This does not turn the failed absolute batch green or clear that research path. State/save/F32/ordinary GPU/paging/stored and additional full raw large warm checks pass. Material, holdout, cumulative and a scope audit remain before any adoption.'})
old.save(M/'complete.json',{'at':old.now(),'all_owned_children_terminal':True,'report_sha256':old.sha(O/'report.json'),'known_baseline_failure_preserved':True,'original_absolute_batch_pass':False,'candidate_adopted':False});print('Remaining original observations terminal; baseline research failure remains visible.',flush=True)
