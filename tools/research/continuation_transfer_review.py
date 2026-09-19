"""Audit frozen-policy transfer results, including deterministic controls."""
import json
from pathlib import Path
import sys
import struct
import numpy as np
import integrated_coverage_review as review

def run():
    result_path,source_path,kind=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
    assert kind in ['fold','call','fourbet','jam','import','development-two','heldout']
    data=json.loads(result_path.read_text());source=json.loads(source_path.read_text())
    frozen=source['records'][-1]['evaluation']['preflop_policy']
    audit=review.audit_result(data)
    assert data['preflop_unchanged'] is True
    for record in data['records']:
        e=record['evaluation'];assert e['preflop_policy']==frozen
        assert [struct.pack('d',v) for node in e['preflop_policy'] for row in node for v in row]==[struct.pack('d',v) for node in frozen for row in node for v in row]
        ev=np.array(e['ev']);restricted=ev+e['postflop_gaps'];full=np.array(e['best_response'])
        assert np.all(restricted>=ev-1e-5) and np.all(restricted<=full+1e-5)
        assert max(abs(np.array(e['postflop_gaps'])-e['independent_postflop_gaps']))<1e-5
        if kind=='fold':
            assert max(abs(ev-[-6,9.5]))<1e-5
            assert abs(e['expected_rake'])<1e-5 and abs(e['postflop_gap_total'])<1e-5
        elif kind=='jam':
            assert abs(e['expected_rake']-6)<1e-5 and abs(e['postflop_gap_total'])<1e-5
    last=data['records'][-1]
    if kind=='development-two':
        assert last['iteration']==2000 and last['evaluation']['postflop_gap_total']<.01
    out=dict(kind=kind,accounting=audit,preflop_exactly_preserved=True,
             iteration=last['iteration'],seconds=last['elapsed_seconds'],
             final={k:last['evaluation'][k] for k in ['ev','gaps','gap_total','postflop_gaps','postflop_gap_total','root_frequencies']})
    path=result_path.with_name(result_path.stem+'-review.json');assert not path.exists()
    path.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

if __name__=='__main__':run()
