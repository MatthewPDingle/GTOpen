"""Wait only for pre-start admission; never retry a started scientific study."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json
import time
import stack_board_error_diagnosis_v1 as study

def main():
    deadline=time.monotonic()+600
    attempts=0
    while True:
        # No existing registration, data or result may be retried by this helper.
        assert not any(p.exists() for p in (study.REG,study.RESULT,study.STORE))
        attempts+=1
        try:
            study.main(True)
            print(json.dumps(dict(admission_attempts=attempts,completed=True)),flush=True)
            return
        except AssertionError as error:
            if str(error)!='Other work takes priority':raise
            assert not any(p.exists() for p in (study.REG,study.RESULT,study.STORE))
            if time.monotonic()>=deadline:raise TimeoutError('Ten-minute admission wait; study not started') from error
            print(json.dumps(dict(admission_attempt=attempts,study_started=False,
                reason=str(error),gpu_snapshot=study.pilot.gpu_snapshot())),flush=True)
            time.sleep(5)

if __name__=='__main__':main()
