"""Root-only: run fixed broader controls and emit exact qualification evidence."""
import common as c

def main():
    assert len(c.sys.argv)==3,'authorization SHA and all-builds-ready SHA required'
    p=c.initialize(c.sys.argv[1]);ready,complete=c.build_ready(c.sys.argv[2])
    c.require_unused([x['id'] for x in p['controls']])
    out=c.Path(p['controls_execution_directory']);out.mkdir(exist_ok=False)
    state=c.Path(p['stored_directory']);state.mkdir(exist_ok=False)
    pins={name:c.binary_pair(name)[2] for name in {r['binary'] for r in p['controls']}}
    c.save(out/'invocation.json',{'at':c.ar.now(),'authorization_sha256':c.sys.argv[1],'all_builds_ready_sha256':c.sys.argv[2],'order':[x['id'] for x in p['controls']],'binary_pins':pins,'GTO_SSD_STUDY_DIR':str(state),'storage_note':'Unlimited-RAM stored-state test, not forced SSD spill'})
    seen={};checks=[];verified={};status='invalid';error=None
    try:
        for row in p['controls']:
            report,raw=c.native(row,pins);seen[row['id']]=(report,raw);verified.update(c.evidence(row['id']))
            if row['id'] in ['V023-state','V023-menu','V023-resume']:
                index=['V023-state','V023-menu','V023-resume'].index(row['id']);suite=list(c.vc.SUITES)[index]
                a=c.vc.read_run(p['original_controls'][index],suite);b=c.vc.read_run(row['id'],suite)
                assert c.vc.canonical(a['records'])==c.vc.canonical(b['records']),row['id']
            elif row['storage']=='f32':
                exact=c.results_exact(report,raw,'f32')
                if row['id']=='V023-f32-original':
                    anchor=dict(row,id=p['original_f32_anchor']);a,log=c.verify_run(anchor)
                    assert exact==c.results_exact(a,log,'f32'),'Original F32 anchor differs'
                    verified.update(c.evidence(p['original_f32_anchor']))
                else:
                    a,log=seen['V023-f32-original'];assert exact==c.results_exact(a,log,'f32')
            elif row['id']=='V023-continuation-paging':
                assert '160 alternating board/player sweeps' in raw
            elif row['id']=='V023-continuation-stored':
                passes=[c.json.loads(x.split('GPU_STORED_PASS ',1)[1]) for x in raw.splitlines() if 'GPU_STORED_PASS ' in x]
                summaries=[c.json.loads(x.split('GPU_STORED_SUMMARY ',1)[1]) for x in raw.splitlines() if 'GPU_STORED_SUMMARY ' in x]
                assert len(passes)==720 and all(x['passed'] is True for x in passes)
                assert len({(x['entry'],x['iteration'],x['player']) for x in passes})==720
                assert len(summaries)==1 and summaries[0]['passes']==720
                assert all(summaries[0][k] is True for k in ['full_device_arrays_bitwise_equal','restored_arrays_bitwise_equal','values_bitwise_equal'])
            checks.append({'id':row['id'],'passed':row['passes'],'exact_scope':next(x['gate'] for x in p['control_gates'] if x['id']==row['id'])})
        baseline=[c.vc.read_run(i,s) for s,i in zip(c.vc.SUITES,p['original_controls'])]
        candidate=[c.vc.read_run(i,s) for s,i in zip(c.vc.SUITES,['V023-state','V023-menu','V023-resume'])]
        controls=c.vc.compare(baseline,candidate);assert controls['status']=='pass' and controls['total_snapshots_each']==160
        c.save(c.ROOT/'comparisons'/p['controls_comparison_id']/'report.json',{**controls,'at':c.ar.now(),'accepted':False,'deployed':False,'scope':'Original160 snapshots, no performance claim'})
        c.verify_source();c.verify_binary_pins(pins);status='pass'
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        c.save(c.ROOT/'comparisons'/p['broader_comparison_id']/'report.json',{'status':status,'at':c.ar.now(),'error':error,'checks':checks,'verified_artifacts':verified,'invocation':{'path':str(out/'invocation.json'),'sha256':c.ar.sha256(out/'invocation.json')},'all_builds_ready_sha256':c.sys.argv[2],'original_snapshots':160 if status=='pass' else None,'f32_fixtures':3 if status=='pass' else None,'gpu_tests':6 if status=='pass' else None,'continuation_tests':3 if status=='pass' else None,'capacity_tests':1 if status=='pass' else None,'performance_claim':False,'accepted':False,'deployed':False})
    print('Broader qualification passed; holdout and independent audits still gate cumulative.',flush=True)

if __name__=='__main__':main()
