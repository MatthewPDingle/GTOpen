"""Wait up to five minutes for unchanged admission checks; start at most once.

The first two direct invocations declined admission before registration or work.
This wrapper waits for the same original available() predicate, changing no
threshold, scientific input, timed operation or ownership guard. No completed or
partial registered workload is retried. The imported main captures this source
in its input registration. The original 60-minute invocation limit includes wait.
"""
import json
import time
import two_arm_training_throughput_control_v1 as control

available=control.pilot.available


def await_admission():
    began=time.monotonic()
    while True:
        ready,probe=available()
        print(json.dumps(dict(admission_ready=ready,waited=time.monotonic()-began,gpu=probe)),flush=True)
        if ready or time.monotonic()-began>=300:return ready,probe
        assert not any(p.exists() for p in (control.REG,control.RESULT,control.STORE))
        time.sleep(10)


if __name__=='__main__':
    control.pilot.available=await_admission
    control.main(run=True)
