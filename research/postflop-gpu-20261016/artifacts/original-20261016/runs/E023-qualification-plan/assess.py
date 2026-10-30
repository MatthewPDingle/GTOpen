"""Assess the fixed cumulative cohort; publish qualifying/rejected, never accepted."""
import common as c

def main():
    assert len(c.sys.argv)==2,'authorization SHA required'
    p=c.initialize(c.sys.argv[1]);assert not (c.ROOT/'gpu-run.lock').exists()
    terminal=c.read(c.Path(p['cumulative_execution_directory'])/'complete.json')
    assert terminal['status']=='pass' and terminal['order']==[r['id'] for r in p['cumulative_order']]
    c.verify_binary_pins(terminal['binary_pins'])
    results={};reference=None
    for row in p['cumulative_order']:
        report,raw=c.verify_run(row);exact=c.results_exact(report,raw,'compressed')
        if reference is None:reference=exact
        assert exact==reference,row['id']
        results[row['id']]=report
    bids=[x['baseline'] for x in p['pairs']];cids=[x['candidate'] for x in p['pairs']]
    comparison=c.cmp.summarize([results[i] for i in bids],[results[i] for i in cids],c.cmp.source_hashes(c.read(c.ROOT/'baseline-manifest.json')))
    failures=c.cmp.rejection_reasons(comparison['performance'])
    out=c.ROOT/'runs/E023-cumulative-assessment';out.mkdir(exist_ok=False)
    command=[c.sys.executable,'-B','tools/postflop_compare.py','--id',p['cumulative_comparison_id'],'--candidate-id','E023R1','--baseline-runs',*bids,'--candidate-runs',*cids,'--warm-cache-cohort']
    if failures:command.append('--reject')
    c.save(out/'invocation.json',{'at':c.ar.now(),'command':command,'failures':failures,'authorization_sha256':c.sys.argv[1]})
    with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
        result=c.subprocess.run(command,cwd=c.REPO,stdout=stdout,stderr=stderr,creationflags=c.subprocess.CREATE_NO_WINDOW)
    c.save(out/'exit.json',{'at':c.ar.now(),'returncode':result.returncode})
    assert result.returncode==0,str(out/'stderr.log')
    report=c.read(c.ROOT/'comparisons'/p['cumulative_comparison_id']/'report.json')
    assert report['performance']==comparison['performance'] and report['decision']==('rejected' if failures else 'qualifying')
    assert report['accepted'] is False and report['deployed'] is False
    c.save(out/'complete.json',{'at':c.ar.now(),'status':'pass','decision':report['decision'],'all18_nontiming_objects_exact':True,'report':{'path':str(c.ROOT/'comparisons'/p['cumulative_comparison_id']/'report.json'),'sha256':c.ar.sha256(c.ROOT/'comparisons'/p['cumulative_comparison_id']/'report.json')},'independent_audit_pending':True,'accepted':False,'deployed':False})
    print(c.json.dumps({'decision':report['decision'],'performance':report['performance']},indent=2))

if __name__=='__main__':main()
