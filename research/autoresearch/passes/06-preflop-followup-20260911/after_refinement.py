"""Run the final check-scheduling screen after conditional tests finish."""
from after_phase_a import guarded
from run_experiment import HERE,idle
import json,sys,time
if __name__=='__main__':
    started=time.monotonic()
    while True:
        done=0
        for label in ('native','sampled'):
            for suffix in ('','-local'):
                p=HERE/'raw'/f'refine-{label}-nested1000{suffix}-exit.json'
                if not p.exists(): continue
                try:r=json.loads(p.read_text())
                except json.JSONDecodeError:continue
                if r['returncode'] or r['reason']:raise RuntimeError(str(p))
                done+=1
        if done==4:break
        idle()
        if time.monotonic()-started>1500:raise RuntimeError('Refinement wait cap')
        time.sleep(1)
    guarded('phase-e-check-scheduling',[sys.executable,str(HERE/'run_check_schedule.py')],4800)
