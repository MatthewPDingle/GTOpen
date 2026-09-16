"""Independent arithmetic audit of persisted N01 references and freeze order."""
import datetime as dt
import continuation_bridge_run as guard

study=guard.study


def audit():
    parts=[]
    for partition in ['development','evaluation']:
        m=study.checked(partition);checked=0;missing=0;max_error=0.;cpu=0.;gpu=0.
        for j in m['jobs']:
            path=study.OUT/partition/'jobs'/f"{j['id']}.json"
            if not path.exists():missing+=1;continue
            r=study.read(path);guard.validate_reference(r,j,m)
            max_error=max(max_error,abs(sum(r['means_bb'])-j['config']['tree']['starting_pot']))
            cpu=max(cpu,r['gap_pct']);gpu=max(gpu,r['gpu_gap_pct']);checked+=1
            if partition=='evaluation':
                frozen=study.read(study.OUT/'candidate-freeze.json')
                assert study.pilot.sha(study.OUT/'candidate.json')==frozen['sha256']
                assert frozen['evaluation_manifest_id']==m['id'] and frozen['evaluation_completed_jobs']==0
                time=dt.datetime.fromisoformat(frozen['frozen_at']).timestamp()
                assert path.stat().st_mtime>=time,'Reference predates the recorded model freeze'
        reused=0
        old=study.prior.checked()
        for source in m['reused']:
            path=study.ROOT/source['source'];assert study.pilot.sha(path)==source['sha256']
            r=study.read(path);j=next(j for j in old['jobs'] if j['id']==r['job']['id'])
            guard.validate_reference(r,j,old)
            assert study.same_job(j['config'],source['job']['config'])
            max_error=max(max_error,abs(sum(r['means_bb'])-j['config']['tree']['starting_pot']))
            cpu=max(cpu,r['gap_pct']);gpu=max(gpu,r['gpu_gap_pct']);reused+=1
        parts.append(dict(partition=partition,fresh_audited=checked,missing=missing,reused_audited=reused,
            max_pot_accounting_error_bb=max_error,max_cpu_gap_pct=cpu,max_gpu_gap_pct=gpu))
    result=dict(checked_at=study.night.now(),partitions=parts,complete=all(p['missing']==0 for p in parts),
        checks=['Exact manifest and configuration provenance','Full-enumeration query mode','Both numerical stopping gates',
            'Per-hand compatible masses reconcile with aggregate masses','Per-hand weighted EVs reconcile with player means',
            'Zero-rake player means sum to starting pot','Finite per-hand EV/equity/BR values',
            'Evaluation output timestamps follow the immutable candidate freeze'],production_enabled=False)
    study.night.dump(study.OUT/'reference-audit.json',result)
    print(result)


if __name__=='__main__':audit()
