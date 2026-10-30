"""Control handoff ordering/ownership using synthetic completed boundaries.

No scientific child invocation, fitting, native execution or CUDA allocation.
"""
import copy
import json
from pathlib import Path
import time
import traceback
from unittest.mock import patch
import psutil
import stack_context_completion_handoff_v2 as h

NAME='stack-context-completion-handoff-v2'
OUT=h.OUT


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    attempt,result,failure=(OUT/(NAME+'-check-'+suffix+'.json') for suffix in ('attempt','result','failure'))
    folder=OUT/(NAME+'-check-fixtures')
    assert not any(p.exists() for p in (attempt,result,failure,folder))
    paths=[Path(__file__).resolve(),Path(h.__file__).resolve(),OUT/'STACK-CONTEXT-COMPLETION-HANDOFF-V2-PLAN.md',h.REG,
        OUT/'stack-context-durable-recovery-entry-v1-admission.json',
        OUT/'stack-context-durable-recovery-entry-v1-parallel-training-started.json',
        OUT/'stack-context-durable-lifetime-probe-v1-result.json']
    paths += [h.ROOT/'tools/research'/v['script'] for v in h.PHASES.values()]
    inputs={str(p):h.sha(p) for p in paths}
    h.save(attempt,dict(inputs=inputs,qualification_only=True,synthetic_boundary_fixtures=True,
        scientific_samples=0,fits=0,native_calls=0,child_launches=0,gpu=False))
    began=time.monotonic();negative=[];decisions=[]
    def reject(name,operation):
        try:operation()
        except (ValueError,TypeError,KeyError,OSError):negative.append(name)
        else:raise AssertionError('Accepted '+name)
    def state(**changes):
        stages={p:dict(started=False,alive=False,complete=False) for p in ('throughput','evaluation','readback')}
        return dict(failure=[],external_owner=False,training_alive=False,training_complete=False,
            clean_training_boundary=False,training_deadline_expired=False,**stages)|changes
    try:
        cases=[(state(training_alive=True),'wait-training'),(state(clean_training_boundary=True),'training'),
            (state(),'review-training'),(state(clean_training_boundary=True,training_deadline_expired=True),'review-deadline'),
            (state(failure=['retained failure'],training_alive=True),'review-failure'),
            (state(external_owner=True,clean_training_boundary=True),'wait-owner')]
        for complete_count in range(4):
            s=state(training_complete=True)
            for p in ('throughput','evaluation','readback')[:complete_count]:s[p]=dict(started=True,alive=False,complete=True)
            cases.append((s,('throughput','evaluation','readback','done')[complete_count]))
        for phase in ('throughput','evaluation','readback'):
            s=state(training_complete=True)
            for p in ('throughput','evaluation','readback'):
                if p==phase:break
                s[p]=dict(started=True,alive=False,complete=True)
            live=copy.deepcopy(s);live[phase]=dict(started=True,alive=True,complete=False)
            partial=copy.deepcopy(s);partial[phase]=dict(started=True,alive=False,complete=False)
            cases += [(live,'wait-'+phase),(partial,'review-'+phase)]
        for s,expected in cases:
            assert h.decide(s)==expected;decisions.append(dict(state=s,expected=expected))
        assert len(decisions)==16
        # Every combination of active owner/failure/active trainer must refuse
        # to launch any next stage, irrespective of downstream completion flags.
        guarded=0
        for phase_mask in range(8):
            for guard in ('failure','external_owner','training_alive'):
                s=state(training_complete=True)
                for i,p in enumerate(('throughput','evaluation','readback')):
                    s[p]=dict(started=bool(phase_mask&(1<<i)),alive=False,complete=bool(phase_mask&(1<<i)))
                s[guard]=['failure'] if guard=='failure' else True
                assert h.decide(s).startswith(('wait-','review-'));guarded+=1
        folder.mkdir()
        counts={a:2 for a in h.ARMS};counts['B-relative']=64
        original={a:1 for a in h.ARMS};original['B-relative']=64
        terminal=dict(stage='complete-boundary-awaiting-resume',completed_cycles=counts,pid=876543210,
            process_created=12345.)
        def fixture(name,patch=None):
            root=folder/name;root.mkdir()
            invocation=root/(h.TRAIN_NAME+'-invocation-qualification.json')
            h.save(invocation,dict(pid=terminal['pid'],process_created=terminal['process_created'],boundaries=original))
            for arm in h.ARMS:
                (root/arm).mkdir();h.save(root/arm/'progress.json',dict(completed_cycles=counts[arm]))
                if original[arm]==64:continue
                value=dict(arm=arm,complete=False,stopped_at_complete_boundary=True,
                    progress_sha256=h.sha(root/arm/'progress.json'))
                if patch and patch[0]==arm:value.update(patch[1])
                h.save(root/(h.TRAIN_NAME+'-qualification-'+arm+'.json'),value)
            return root
        good=fixture('good');proof=h.boundary(terminal,counts,train=good)
        assert proof['counts']==counts and proof['invocation_sha256']==h.sha(good/(h.TRAIN_NAME+'-invocation-qualification.json'))
        for name,patch in (('failed arm',{'failed':True}),('missing successful boundary',{'stopped_at_complete_boundary':False}),
            ('wrong progress digest',{'progress_sha256':'0'*64}),('false arm completion',{'complete':True})):
            root=fixture(name.replace(' ','-'),('A-baseline',patch))
            reject(name,lambda root=root:h.boundary(terminal,counts,train=root))
        root=fixture('duplicate-invocation')
        h.save(root/(h.TRAIN_NAME+'-invocation-duplicate.json'),dict(pid=terminal['pid'],process_created=terminal['process_created'],boundaries=original))
        reject('ambiguous invocation',lambda:h.boundary(terminal,counts,train=root))
        root=fixture('partial-next-cycle');(root/'A-baseline'/'cycle-0003').mkdir()
        reject('unpublished partial cycle',lambda:h.boundary(terminal,counts,train=root))
        root=fixture('partial-next-archive');(root/'A-baseline'/'archive-0003').mkdir()
        reject('unpublished partial archive',lambda:h.boundary(terminal,counts,train=root))
        for name,patch in (('nonterminal status',{'stage':'parallel-training'}),
            ('wrong count snapshot',{'completed_cycles':{a:3 for a in h.ARMS}}),
            ('wrong invocation PID',{'pid':876543211}),('wrong invocation creation',{'process_created':12346.})):
            reject(name,lambda patch=patch:h.boundary(terminal|patch,counts,train=good))
        reject('missing complete64 result',lambda:h.boundary(terminal|{'completed_cycles':{a:64 for a in h.ARMS}},
            {a:64 for a in h.ARMS},train=good))
        reject('wrong expected live script',lambda:h.process_alive(h.INITIAL[0],h.INITIAL[1],'different_script.py'))
        assert h.process_alive(h.INITIAL[0],h.INITIAL[1],h.PHASES['training']['script'])
        assert not h.process_alive(h.INITIAL[0],h.INITIAL[1]-100,h.PHASES['training']['script'])
        class Child:
            def __init__(self,codes):self.codes=iter(codes)
            def poll(self):return next(self.codes)
        with patch.object(h,'process_alive',return_value=False):
            assert h.poll_child(Child([None,0]),h.INITIAL,'unused.py')==0
            reject('live child with mismatched identity',lambda:h.poll_child(Child([None,None]),h.INITIAL,'unused.py'))
        with patch.object(h,'process_alive',side_effect=ValueError('command changed')):
            assert h.poll_child(Child([None,0]),h.INITIAL,'unused.py')==0
            reject('live child with wrong command',lambda:h.poll_child(Child([None,None]),h.INITIAL,'unused.py'))
        with patch.object(h,'process_alive',side_effect=psutil.NoSuchProcess(876543210)):
            assert h.poll_child(Child([None,0]),h.INITIAL,'unused.py')==0
        with patch.object(h,'process_alive',return_value=True):
            assert h.poll_child(Child([None]),h.INITIAL,'unused.py') is None
        assert h.poll_child(Child([0]),h.INITIAL,'unused.py')==0
        live=h.observe([h.INITIAL]);assert live['training_alive'] and not live['training_complete']
        assert h.decide(live)=='wait-training' and not live['failure']
        for phase in h.PHASES:
            cmd=h.command(phase);assert cmd[-1]=='--run' and '--resume' not in cmd
            assert Path(cmd[2])==h.ROOT/'tools/research'/h.PHASES[phase]['script']
        h.verify_inputs(inputs)
        answer=dict(complete=True,passed=True,runner_sha256=h.sha(h.__file__),seconds=time.monotonic()-began,
            inputs=inputs,qualification_only=True,decision_controls=decisions,guarded_combinations=guarded,
            successful_completed_boundary=proof,corruption_rejections=negative,live_observation=live,
            scientific_samples=0,fits=0,native_calls=0,child_launches=0,gpu=False,
            actual_full_bank_resource_check=False,scientific_evaluation_complete=False,production_modified=False,
            normal_exit_race_controls=5,original_v1_qualification_preserved=True,
            synthetic_boundary_artifacts={str(p):h.sha(p) for p in folder.rglob('*') if p.is_file()})
        h.save(result,answer)
        print(json.dumps(dict(passed=True,seconds=answer['seconds'],decisions=len(decisions),
            guard_combinations=guarded,negative_cases=len(negative),live_counts=live['counts'])))
    except BaseException as error:
        h.save(failure,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True,automatic_retry_allowed=False));raise


if __name__=='__main__':main()
