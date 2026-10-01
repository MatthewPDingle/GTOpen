"""Original report calculations with explicit clean-resume terminal provenance.

Preserve the v1 report and old failed handoff. Never open an incomplete result
or use a recovered handoff as a substitute for the independent scientific audit.
"""
import argparse
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,r'T:\Dev\GTOpen\tools\research')
import stack_context_final_report_v1 as base

ROOT,OUT=base.ROOT,base.OUT
NAME='stack-context-final-report-v3'
READER='stack-context-matched-readback-v7'
OLD_READER='stack-context-matched-readback-v6'
OLD_READBACK_RUN='stack-context-resumed-readback-v1'
CONTROL=OUT/'stack-context-final-report-v3-control-result.json'
CORRECTION_PINS={
    'stack-context-corrected-readback-check-v1-result.json':'a215f406f77318218fd4324defc04e3e570ed1ac89704e09507ea42a28bfb4ac',
    'stack-context-corrected-readback-v1-explicit-review.json':'eae15c39abe75f899cbbbe9320dc5805344053c4d466b37290ff41d08269acdc',
    'stack-context-corrected-readback-v1-admitted-review.json':'31793fe523eafa0f178d40bde6eb6221e57c438c6ff2eb4278164ac2e8514ed3',
}
RESUME='stack-context-clean-boundary-resume-v1'
READBACK_RUN='stack-context-corrected-readback-v1'
STORE=Path('S:/GTOpen-research/stack-context-matched-evaluation-v5')
REVIEW_SHA='afe9873ce9718c9bc45abb386f25302ddbe005853c242f6d6b26e1224812ac9a'
LOCKS=(*base.LOCKS,OUT/(RESUME+'-owner.json'),OUT/(READBACK_RUN+'-owner.json'),OUT/(OLD_READBACK_RUN+'-owner.json'))
require,read,sha=base.require,base.read,base.sha

def terminal_evidence(*,include_reader=True):
    required_names=['stack-context-pressure-continuation-v2-training',base.THROUGHPUT,RESUME,base.EVALUATION]
    if include_reader:required_names += [READER,READBACK_RUN]
    required=[OUT/(name+'-result.json') for name in required_names]
    failures=[OUT/(name+'-failure.json') for name in
        ('stack-context-pressure-continuation-v2',base.THROUGHPUT,RESUME,base.EVALUATION,READER,READBACK_RUN)]
    require(all(p.is_file() for p in required),'Successful complete terminal evidence required; no interim look')
    require(not any(p.exists() for p in (*LOCKS,*failures)),'Live ownership or current scientific failure')
    inputs={}
    def bound(path):
        inputs[str(path)]=sha(path);return read(path)
    def exited(prefix,command,attempt=None):
        start=bound(Path(str(prefix)+'-started.json'));ended=bound(Path(str(prefix)+'-finished.json'))
        require(start['command']==command and all(ended[k]==start[k] for k in start)
                and ended['exit_code']==0 and ended['finished_unix']>=start['unix']
                and not base.live(start,'created'),'Unsuccessful, live or detached child')
        if attempt is not None:
            require(start['pid']==attempt['pid']
                    and abs(start['created']-attempt['process_created'])<.01,'Child differs from immutable attempt')
        for stream in ('stdout','stderr'):
            path=Path(str(prefix)+'-'+stream+'.log');inputs[str(path)]=sha(path)
            require(inputs[str(path)]==ended[stream+'_sha256'],'Changed immutable child log')
        return start,ended
    def command(script,*flags):return ['C:/Program Files/Python312/python.exe','-B',str(ROOT/'tools/research'/script),*flags]
    training=bound(required[0]);throughput=bound(required[1])
    require(training['training_complete'] is True and training['production_modified'] is False
            and set(training['arms'])=={'A-baseline','A-relative','B-baseline','B-relative'}
            and all(r['completed_cycles']==64 for r in training['arms'].values()),'Incomplete original training')
    require(all(throughput[k] is True for k in
        ('complete','passed','full_played_banks_64','cuda_passed','reference_agreement_passed'))
        and throughput['production_modified'] is False,'Original full-bank CUDA/reference gate required')
    review_path=OUT/(RESUME+'-review.json');review=bound(review_path)
    require(inputs[str(review_path)]==REVIEW_SHA and review['complete'] and review['passed']
            and review['qualified_clean_boundary_continuation']
            and review['verified_registered_inputs']==4607 and review['remaining_deals']==1888
            and not review['partial_scientific_batch_retry_allowed'],'Not the explicitly reviewed clean boundary')
    for path,digest in review['inputs'].items():
        if Path(path)!=OUT/(base.EVALUATION+'-status.json'):
            inputs[path]=sha(path);require(inputs[path]==digest,'Preserved original review evidence changed')
    old_failure=bound(OUT/(base.HANDOFF+'-failure.json'))
    old_owner=bound(OUT/(base.HANDOFF+'-attempt.json'))
    require(old_failure['error']=="ValueError('Child returned without terminal completion; no automatic resume')"
            and old_failure['automatic_retry_allowed'] is False and old_failure['preserve_evidence'] is True
            and not base.live(old_owner,'created'),'Unrecognized old handoff failure or live old owner')
    reg_path=OUT/(base.EVALUATION+'-registration.json');reg=bound(reg_path)
    original=bound(OUT/(base.EVALUATION+'-attempt.json'))
    require(original['registration_sha256']==inputs[str(reg_path)]==review['registration_sha256']
            and original['admitted_unix']==review['original_admitted_unix']
            and original['admitted_unix']+reg['maximum_evaluation_seconds']==review['original_evaluation_deadline_unix']
            and reg['maximum_evaluation_seconds']==72*3600 and reg['maximum_invocation_seconds']==12*3600,
            'Changed original admission, registration or time windows')
    for path in (OUT/(base.THROUGHPUT+'-result.json'),ROOT/'tools/research/stack_context_matched_evaluation_v5.py'):
        require(sha(path)==reg['inputs'][str(path)],'Changed registered gate or evaluator source')
    exited(OUT/(base.HANDOFF+'-002-evaluation'),command('stack_context_matched_evaluation_v5.py','--run'),original)
    throughput_attempt=bound(OUT/(base.THROUGHPUT+'-attempt.json'))
    exited(OUT/(base.HANDOFF+'-001-throughput'),command('stack_context_final_bank_throughput_v4.py','--run'),throughput_attempt)
    launcher=bound(OUT/(RESUME+'-attempt.json'));resume=bound(OUT/(RESUME+'-result.json'))
    require(not base.live(launcher,'created') and launcher['review_sha256']==REVIEW_SHA
            and launcher['runner_sha256']==sha(ROOT/'tools/research/stack_context_clean_boundary_resume_v1.py')
            and all(resume[k] is True for k in ('complete','passed','original_attempt_preserved',
                'original_helper_failure_preserved','only_unstarted_remaining_batches_allowed','original_budgets_and_sources_unchanged')),
            'Explicit continuation has not completed and released ownership')
    started,ended=exited(OUT/(RESUME+'-evaluation'),command('stack_context_matched_evaluation_v5.py','--run','--resume'))
    require(started['parent_pid']==launcher['pid'] and resume['unix']>=ended['finished_unix']
            and ended['finished_unix']<=review['original_evaluation_deadline_unix']
            and started['original_attempt_sha256']==sha(OUT/(base.EVALUATION+'-attempt.json')),
            'Unbound continuation or changed original admission')
    invocation_paths=list(STORE.glob('invocation-*.json'));invocations=[bound(p) for p in invocation_paths]
    require(len(invocations)==2 and sum(r['resume'] is False and r['pid']==original['pid']
            and abs(r['process_created']-original['process_created'])<.01 for r in invocations)==1
            and sum(r['resume'] is True and r['pid']==started['pid']
            and abs(r['process_created']-started['created'])<.01 for r in invocations)==1,'Unexpected/repeated scientific invocation')
    terminal_path=OUT/(base.EVALUATION+'-result.json');terminal=bound(terminal_path)
    bank_path=STORE/'bank-identities.json';banks=bound(bank_path)
    require(terminal['fixed_policy_evaluation_complete'] is True and terminal['production_modified'] is False
            and terminal['registration_sha256']==inputs[str(reg_path)]
            and banks==reg['banks'] and terminal['bank_identities_sha256']==inputs[str(bank_path)]
            and resume['evaluation_result_sha256']==inputs[str(terminal_path)]
            and resume['evaluation_registration_sha256']==inputs[str(reg_path)],'Incomplete or unbound final evaluation')
    require(set(terminal['journals'])=={str(d) for d in base.DEPTHS}
            and all(r['completed_deals']==4096 for r in terminal['journals'].values())
            and len(terminal['range_exports'])==28,'Incomplete original final population')
    for path,digest in terminal['range_exports'].items():
        inputs[path]=sha(path);require(inputs[path]==digest,'Changed final range export')
    correction=corrected_terminal_provenance(bound,inputs)
    reader=None
    if include_reader:
        reader_path=OUT/(READER+'-result.json');reader=bound(reader_path)
        reader_attempt=bound(OUT/(READER+'-attempt.json'))
        readback_owner=bound(OUT/(READBACK_RUN+'-attempt.json'));readback=bound(OUT/(READBACK_RUN+'-result.json'))
        require(not base.live(readback_owner,'created') and readback['complete'] and readback['passed']
                and readback['reader_result_sha256']==inputs[str(reader_path)]
                and readback['evaluation_result_sha256']==inputs[str(terminal_path)],'Readback wrapper not terminal and bound')
        rs,re=exited(OUT/(READBACK_RUN+'-reader'),command('stack_context_matched_readback_v7.py','--run'),reader_attempt)
        require(rs['parent_pid']==readback_owner['pid'] and readback['unix']>=re['finished_unix'],'Detached independent reader')
        require(all(reader[k] is True for k in ('corrected_checker','failed_readback_preserved'))
                and readback['independent_readback_complete'] is True and readback['failed_readback_preserved'] is True
                and readback['new_scientific_work'] is False
                and reader['preserved_failed_readback_sha256']==correction['failure_sha256']
                and reader['original_audit_deadline_unix']==reader_attempt['original_audit_deadline_unix']
                ==readback_owner['original_audit_deadline_unix']==readback['original_audit_deadline_unix']==correction['deadline']
                and re['finished_unix']<=readback['unix']<correction['deadline']
                and reader_attempt['maximum_seconds']==43200 and reader_attempt['torch_threads']==4
                and reader_attempt['new_scientific_work'] is False and reader_attempt['test_batch_starts']==[0,4064]
                and readback_owner['control_sha256']==readback['control_sha256']==correction['qualification_sha256']
                and readback_owner['reader_sha256']==correction['reader_sha256']
                and readback_owner['runner_sha256']==correction['runner_sha256']
                and readback_owner['provenance_sha256']==correction['provenance_sha256'],
                'Corrected audit detached from qualified failed-checker review or original scope/deadline')
        for path,digest in reader['inputs'].items():
            inputs[path]=sha(path);require(inputs[path]==digest,'Changed consumed independent audit evidence')
        require(all(reader[k] is True for k in ('complete','passed','independent_readback_complete',
                'training_heldout_stack_separation_verified')) and reader['production_modified'] is False
                and reader['evaluation_result_sha256']==inputs[str(terminal_path)]
                and reader['evaluation_registration_sha256']==inputs[str(reg_path)],'Independent reader did not pass on this evaluation')
        require(reader['original_archive_batches']==896 and reader['reference_policy_replay_batches']==14
                and reader['reference_complete_preflop_range_replays']==28 and reader['independent_chance_cycles']==256
                and reader['strictly_board_disjoint_test'] is False
                and reader['native_payoff_oracle_independent'] is False,'Changed scientific audit scope')
        base.validate_comparison(terminal['comparison'],reader['arithmetic'])
    for path in (Path(__file__).resolve(),Path(base.__file__).resolve()):inputs[str(path)]=sha(path)
    require(sha(Path(base.__file__))=='633d3fc863bbb8b2f5d573ba48fb4955ccfa0b546b9103b4715b5ac232460b30',
            'Original qualified report/render functions changed')
    return terminal,reader,inputs

def corrected_terminal_provenance(bound,inputs):
    """Authenticate the exact reviewed checker defect and its qualified replacement."""
    proofs={}
    for name,digest in CORRECTION_PINS.items():
        path=OUT/name;record=bound(path)
        require(inputs[str(path)]==digest and record['complete'] is True and record['passed'] is True
                and record['production_modified'] is False,'Unrecognized corrected-checker review')
        for p,identity in record['inputs'].items():
            inputs[p]=sha(p);require(inputs[p]==identity,'Changed corrected-checker review evidence')
        proofs[name]=record
    qualification=proofs['stack-context-corrected-readback-check-v1-result.json']
    admission=proofs['stack-context-corrected-readback-v1-explicit-review.json']
    require(qualification['unchanged_numerical_and_authenticity_checks'] is True
            and qualification['unchanged_evaluation_functions_verified'] is True
            and qualification['full_scope']==dict(training_chance_cycles=256,evaluation_archives=896,
                preflop_reference_replays=28,postflop_reference_batches=14,comparisons=56,torch_threads=4)
            and qualification['new_scientific_work'] is False
            and admission['explicit_corrected_readonly_admission'] is True and admission['failed_checker_preserved'] is True
            and admission['scientific_attempt_retried'] is False
            and qualification['original_deadline_unix']==admission['original_audit_deadline_unix']==1790934006.0150957,
            'Expanded or unqualified corrected checker')
    for name,field in (('stack_context_matched_readback_v7.py','reader_sha256'),
                       ('stack_context_corrected_readback_v1.py','runner_sha256'),
                       ('stack_context_corrected_audit_provenance_v1.py','provenance_sha256'),
                       ('stack_context_matched_readback_v6.py','original_reader_sha256')):
        path=ROOT/'tools/research'/name;inputs[str(path)]=sha(path)
        require(inputs[str(path)]==qualification[field],'Qualified checker source changed')
    failed_path=OUT/(OLD_READER+'-failure.json');failed=bound(failed_path)
    attempt=bound(OUT/(OLD_READER+'-attempt.json'))
    helper=bound(OUT/(OLD_READBACK_RUN+'-attempt.json'))
    helper_failure=bound(OUT/(OLD_READBACK_RUN+'-failure.json'))
    start=bound(OUT/(OLD_READBACK_RUN+'-reader-started.json'))
    end=bound(OUT/(OLD_READBACK_RUN+'-reader-finished.json'))
    require(failed['error']=="ValueError('Undocumented correction/recovery')"
            and failed['automatic_retry_allowed'] is False and failed['preserve_evidence'] is True
            and helper_failure['error']=="ValueError('Independent reader failed; preserve without retry')"
            and helper_failure['automatic_retry_allowed'] is False and helper_failure['preserve_evidence'] is True
            and attempt['pid']==start['pid']==116480 and abs(start['created']-1790890806.0150957)<.01
            and abs(attempt['process_created']-start['created'])<.01
            and start['parent_pid']==helper['pid']==114432
            and all(end[k]==start[k] for k in start) and end['exit_code']==1
            and not base.live(start,'created') and not base.live(helper,'created')
            and not (OUT/(OLD_READER+'-result.json')).exists(), 'Different failed original checker or live old owner')
    for stream in ('stdout','stderr'):
        path=OUT/(OLD_READBACK_RUN+'-reader-'+stream+'.log');inputs[str(path)]=sha(path)
        require(inputs[str(path)]==end[stream+'_sha256'],'Changed preserved failed checker log')
    require(attempt['maximum_seconds']==43200 and attempt['torch_threads']==4
            and attempt['new_scientific_work'] is False and attempt['test_batch_starts']==[0,4064]
            and attempt['process_created']+attempt['maximum_seconds']==qualification['original_deadline_unix'],
            'Changed original failed checker budget or scope')
    return dict(deadline=qualification['original_deadline_unix'],failure_sha256=inputs[str(failed_path)],
        qualification_sha256=CORRECTION_PINS['stack-context-corrected-readback-check-v1-result.json'],
        reader_sha256=qualification['reader_sha256'],runner_sha256=qualification['runner_sha256'],
        provenance_sha256=qualification['provenance_sha256'])


def main(render=False):
    if not render:
        print(json.dumps(dict(prepared=True,terminal_evaluation=(OUT/(base.EVALUATION+'-result.json')).exists(),
            terminal_readback=(OUT/(READER+'-result.json')).exists(),comparison_values_read=False)));return
    paths={kind:OUT/(NAME+suffix) for kind,suffix in
        (('table','.md'),('figure','.png'),('values','-comparison.json'),('receipt','-receipt.json'))}
    require(not any(p.exists() for p in paths.values()),'Preserve existing final report')
    control=read(CONTROL)
    require(control['complete'] is True and control['passed'] is True
            and control['candidate_source_sha256']==sha(__file__)
            and control['original_renderer_sha256']==sha(base.__file__), 'Qualified current report provenance required')
    terminal,reader,inputs=terminal_evidence();inputs[str(CONTROL)]=sha(CONTROL);comparison=terminal['comparison']
    paths['table'].write_text(base.markdown(comparison),encoding='utf-8');base.figure(comparison,paths['figure'])
    paths['values'].write_text(json.dumps(comparison,allow_nan=False,sort_keys=True,separators=(',',':')),encoding='utf-8')
    require(all(sha(p)==digest for p,digest in inputs.items()),'Evidence changed during rendering')
    receipt=dict(complete=True,unix=time.time(),inputs=inputs,outputs={str(p):sha(p) for k,p in paths.items() if k!='receipt'},
        comparison_count=56,pooled_comparison_count=8,independent_readback_complete=True,
        recognized_clean_resume_only=True,original_failed_handoff_preserved=True,
        original_render_functions_unchanged=True,scientific_decision_changed=False,
        qualified_corrected_reader_verified=True,failed_reader_and_wrapper_preserved=True,
        plain_english_analysis_complete=False,range_interpretation_complete=False,
        new_scientific_deals=False,fitting=False,native_execution=False,gpu_used=False,production_modified=False,broad_goal_complete=False)
    paths['receipt'].write_text(json.dumps(receipt,allow_nan=False,sort_keys=True,separators=(',',':')),encoding='utf-8')
    print(json.dumps(dict(complete=True,outputs={k:str(p) for k,p in paths.items()})))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');main(parser.parse_args().render)
