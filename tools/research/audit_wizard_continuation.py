"""Independent completed-panel accounting and decoded per-probe quality checks."""
import hashlib
import json
import sys
import wizard_continuation_study as s


def check_manifest(path):
    m=s.read(path)
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest()==m['id']
    for p,digest in m['inputs'].items():assert s.sha(s.ROOT/p)==digest,p
    return m


def audit(phase):
    parent=s.checked();probes=s.read(s.OUT/'fixtures.json')['probes']
    precision=check_manifest(s.OUT/'precision/manifest.json')
    refined={j['id'] for j in precision['jobs']}
    directory=s.OUT if phase=='precision' else s.OUT/phase
    manifest=parent if phase=='precision' else check_manifest(directory/'manifest.json')
    assert s.read((s.OUT/'precision' if phase=='precision' else directory)/'status.json')['stage']=='ready_for_review'
    gain=0.;accounting=0.;iterations=[]
    for j in manifest['jobs']:
        use_precision=phase=='precision' and j['id'] in refined
        r=s.read(directory/('precision/jobs' if use_precision else 'jobs')/(j['id']+'.json'))
        s.validate(r,j,precision if use_precision else manifest)
        decoded={h['hand']:h for h in r['hands'][0]}
        ranks=j['board'][::2]
        expected={h for h in probes if not (len(h)==2 and ranks.count(h[0])==3)}
        assert expected.issubset(decoded), (j['id'],expected-decoded.keys())
        gains=[decoded[h]['br_ev_bb']-decoded[h]['ev_bb'] for h in expected]
        assert max(gains)<=.05+1e-9,(j['id'],max(gains))
        gain=max(gain,max(gains))
        for p,hands in enumerate(r['hands']):
            mass=sum(h['pair_mass'] for h in hands)
            mean=sum(h['pair_mass']*h['ev_bb'] for h in hands)/mass
            error=abs(mean-r['means_bb'][p]);accounting=max(accounting,error)
            assert error<.0001,(j['id'],p,error)
        iterations.append(r['iterations'])
    assert len(manifest['jobs'])==80
    record=dict(phase=phase,jobs=80,decoded_max_probe_br_gain_bb=gain,max_mean_reconstruction_error_bb=accounting,
        minimum_iterations=min(iterations),maximum_iterations=max(iterations),manifest_id=manifest['id'],
        precision_manifest_id=precision['id'] if phase=='precision' else None,
        note='Reconstructed range means and probe gains from decoded per-hand records; all frozen input hashes verified.')
    s.write(directory/('precision-validation.json' if phase=='precision' else 'validation.json'),record)
    print(json.dumps(record,indent=2))


if __name__=='__main__':audit(sys.argv[1])
