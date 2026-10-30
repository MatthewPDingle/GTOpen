"""Original prefix replay with explicit admission of an empty rebooted app."""
import json
import sys
from pathlib import Path
import hu_visible_hybrid_trial_review_20260923 as original
from reboot_research_idle_v1 import idle
from sampled_physical_root_evaluation_v1 import sha, save


if __name__ == '__main__':
    assert sys.argv[1:] == ['--prefix', '48']
    registration = original.OUT/'sampled-visible-hybrid-resume-prefix-audit-v1-registration.json'
    paths = [Path(__file__), Path(original.__file__), Path(__file__).with_name('reboot_research_idle_v1.py')]
    evidence = {str(p): sha(p) for p in paths}
    assert not registration.exists()
    save(registration, dict(inputs=evidence, completed_iterations=48,
        scope='Unchanged original 48-update replay; only the activity probe also admits a verified absent preflop session.'))
    original.idle = idle
    original.main()
    for p,h in evidence.items():
        assert sha(p) == h
