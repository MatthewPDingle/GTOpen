"""Synthetic operational guards; never call a scientific worker or pipeline."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import copy
import hashlib
import json
from pathlib import Path
import time
import traceback
import tempfile
import stack_context_pressure_continuation_v2 as runner


def fixtures():
    progress={};outcomes={}
    for arm,n in runner.COUNTS.items():
        records=[dict(cycle=i,checkpoint=dict(file=str(i),sha256=str(i))) for i in range(1,n+1)]
        p=dict(registration_sha256=runner.REG_SHA,completed_cycles=n,checkpoint=records[-1]['checkpoint'],updates=records)
        progress[arm]=p
        outcomes[arm]=dict(arm=arm,pid=runner.OLD_WORKERS[arm][0],process_created=runner.OLD_WORKERS[arm][1],
            complete=False,stopped_at_complete_boundary=True,progress_sha256=runner.prefix_hash(p,n))
    failure=dict(error=runner.PRESSURE_ERROR,invocation=runner.INVOCATION,automatic_retry_allowed=False,
        original_registration_sha256=runner.REG_SHA)
    finished=dict(pid=runner.OLD_PARENT[0],created=runner.OLD_PARENT[1],phase='training',index=1,exit_code=1)
    return failure,finished,outcomes,progress


def main():
    attempt=runner.OUT/(runner.NAME+'-check-attempt.json');failed=runner.OUT/(runner.NAME+'-check-failure.json')
    runner.require(not any(p.exists() for p in (attempt,failed,runner.CONTROL)), 'Qualification already attempted')
    inputs={str(p):runner.sha(p) for p in (Path(__file__).resolve(),Path(runner.__file__).resolve(),runner.PLAN,
        Path(runner.original.__file__).resolve(),runner.original.CONTROL)}
    runner.save(attempt,dict(inputs=inputs,scientific_workers_launched=0,scientific_fits=0,native_calls=0))
    began=time.monotonic()
    try:
        f,e,o,p=fixtures();assert runner.validate_failure(f,e,o,p)==runner.COUNTS
        negatives=[]
        changes=[('failure-error',lambda f,e,o,p:f.update(error='Worker fit failed')),
            ('failure-invocation',lambda f,e,o,p:f.update(invocation='other')),
            ('failure-registration',lambda f,e,o,p:f.update(original_registration_sha256='0'*64)),
            ('failure-auto-retry',lambda f,e,o,p:f.update(automatic_retry_allowed=True)),
            ('exit-code',lambda f,e,o,p:e.update(exit_code=0)),
            ('exit-identity',lambda f,e,o,p:e.update(created=0)),
            ('exit-phase',lambda f,e,o,p:e.update(phase='evaluation')),
            ('missing-arm',lambda f,e,o,p:o.pop('A-relative'))]
        for arm in runner.COUNTS:
            changes.extend([(arm+'-worker-failed',lambda f,e,o,p,a=arm:o[a].update(failed=True)),
                (arm+'-worker-id',lambda f,e,o,p,a=arm:o[a].update(process_created=0)),
                (arm+'-partial',lambda f,e,o,p,a=arm:o[a].update(stopped_at_complete_boundary=False)),
                (arm+'-false-complete',lambda f,e,o,p,a=arm:o[a].update(complete=True)),
                (arm+'-prefix-changed',lambda f,e,o,p,a=arm:p[a]['updates'][0].update(extra='corruption')),
                (arm+'-reordered',lambda f,e,o,p,a=arm:p[a]['updates'][0].update(cycle=2)),
                (arm+'-detached-checkpoint',lambda f,e,o,p,a=arm:p[a].update(checkpoint={'file':'wrong'}))])
        for name,change in changes:
            values=copy.deepcopy((f,e,o,p));change(*values)
            try:runner.validate_failure(*values)
            except ValueError:negatives.append(name)
            else:raise AssertionError('Accepted corruption: '+name)
        # Actual prefix serialization must match independent raw JSON encoding.
        for arm,n in runner.COUNTS.items():
            assert runner.prefix_hash(p[arm],n)==hashlib.sha256(runner.encoded(p[arm])).hexdigest()
            future=copy.deepcopy(p[arm]);future['completed_cycles']=64
            for i in range(n+1,65):future['updates'].append(dict(cycle=i,checkpoint=dict(file=str(i),sha256=str(i))))
            future['checkpoint']=future['updates'][-1]['checkpoint']
            assert runner.prefix_hash(future,n)==o[arm]['progress_sha256']
        counts=dict(runner.COUNTS)
        assert runner.choose_arm(list(runner.ARMS),[],counts,50_000_000_000)=='A-relative'
        assert runner.choose_arm(['B-relative','A-baseline','B-baseline'],['A-relative'],counts,50_000_000_000)=='B-relative'
        assert runner.choose_arm(['A-baseline','B-baseline'],['A-relative','B-relative'],counts,50_000_000_000) is None
        assert runner.choose_arm(['B-baseline'],['A-baseline'],counts,54_000_000_000) is None
        assert runner.choose_arm(['A-baseline'],[],counts,54_000_000_000)=='A-baseline'
        assert runner.choose_arm(['A-baseline'],[],counts,62_000_000_000) is None
        # A simulator exercises admission/completion in distinct orders. No worker
        # invocation is mocked into success; this is a pure scheduling control.
        schedules=[]
        for completed_first in ('A-relative','B-relative'):
            waiting=list(runner.ARMS);active=[];c=dict(counts);starts=[];peak=0
            for _ in range(12):
                a=runner.choose_arm(waiting,active,c,50_000_000_000)
                if a:
                    waiting.remove(a);active.append(a);starts.append(a);peak=max(peak,len(active));continue
                if active:
                    done=completed_first if completed_first in active else active[0]
                    active.remove(done);c[done]=64;continue
                break
            assert not waiting and not active and set(starts)==set(runner.ARMS) and len(starts)==4 and peak==2
            schedules.append(dict(completed_first=completed_first,starts=starts,peak_active=peak))
        with tempfile.TemporaryDirectory(prefix='gtopen-retired-dir-control-') as folder:
            raw=Path(folder)/'retired';raw.mkdir();(raw/'empty-child').mkdir()
            assert runner.retired_raw(raw) and runner.retired_raw(Path(folder)/'absent')
            leftover=raw/'empty-child'/'unexpected.json';leftover.write_text('{}')
            assert not runner.retired_raw(raw)
        result=dict(complete=True,passed=True,inputs=inputs,coordinator_sha256=runner.sha(runner.__file__),
            negatives=negatives,negative_count=len(negatives),unchanged_prefix_controls=8,
            scheduling_controls=6,retirement_controls=3,completion_order_simulations=schedules,
            scientific_workers_launched=0,scientific_fits=0,native_calls=0,new_scientific_deals=0,
            actual_resource_run=False,scientific_accuracy_qualified=False,production_modified=False,
            seconds=time.monotonic()-began)
        runner.save(runner.CONTROL,result);print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))
    except BaseException as error:
        runner.save(failed,dict(error=repr(error),traceback=traceback.format_exc(),inputs=inputs,preserve_evidence=True));raise


if __name__=='__main__':main()
