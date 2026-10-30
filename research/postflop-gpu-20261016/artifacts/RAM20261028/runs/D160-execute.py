import sys,shutil,importlib.util,json,statistics,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
verify();O=H/'execution';O.mkdir(exist_ok=False)
def publish(folder,names):
    for name in names:
        path=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(exist_ok=True,parents=True)
        if dest.exists():assert dest.read_bytes()==path.read_bytes()
        else:shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
publish(H,['protocol.json','source-review.json','fixtures.json','probe.rs'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D160' for x in status['experiments'])
    status['experiments'].append({'id':'D160','title':'Large numeric arena allocation lifecycle','kind':'diagnostic','status':'running','accepted':False,'correctness':'pending_component_only','measurement_epoch':'RAM20261028','stage':'Frozen CPU allocation/touch/free component and process-resource screen','reason':'Compare actual mimalloc ArenaBuf constructor against ordinary Win32 allocation for>=64MiB q arrays. Full initial zero scan,two dense write/all-bit verification rounds,and frees included. Six fixed fresh CPU-only runs. No GPU/solver/performance qualification or source activation.','evidence':[{'label':'Prospective fixed component protocol','url':'evidence/D160-arena-lifecycle/protocol.json'},{'label':'API/source/history obligations','url':'evidence/D160-arena-lifecycle/source-review.json'}]})
    status.update(updated_at=h.now(),active_experiment='D160',stage='CPU arena lifecycle scout',activity='Testing whether distinct large numeric allocation backend has enough inclusive headroom before any production implementation. Existing zero checks retained; all memory touched and freed. E08010.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
spec=importlib.util.spec_from_file_location('sampler',H/'sampler.py');sampler=importlib.util.module_from_spec(spec);spec.loader.exec_module(sampler)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    h.child(P['rustc_command'],O,'rustc',1200);verify();h.save(O/'binary.json',{'path':str(H/'probe.exe'),'sha256':h.sha(H/'probe.exe')})
    nvml=sampler.Nvml()
    try:
        for item in P['sequence']:
            verify();h.ar.refuse_active(h.ar.live_status());sampler.run([str(H/'probe.exe'),item['arm']],O,item['id'],h,nvml,300);verify()
    finally:nvml.close()
    rows={};resources={};gates={};reference=None;fixtures=h.read(H/'fixtures.json')
    for item in P['sequence']:
        ident=item['id'];r=h.read(O/(ident+'.resource.json'));resources[ident]=r
        lines=(O/(ident+'.stdout.log')).read_text(encoding='utf-8').splitlines();x=[json.loads(t.split('D160_ARENA ',1)[1]) for t in lines if t.startswith('D160_ARENA ')]
        assert [a['fixture'] for a in x]==P['fixture_order'];rows[ident]=x
        science=[{k:a[k] for k in ['fixture','CPU_arena_bytes','q_entries','scale_entries','all_elements_verified','checksums','threads','GPU_calls']} for a in x]
        if reference is None:reference=science
        gates[ident+':all_elements_bit_exact']=science==reference and all(a['all_elements_verified'] and a['GPU_calls']==0 and a['threads']==16 for a in x)
        gates[ident+':geometry_exact']=all(a['CPU_arena_bytes']==b['CPU_arena_bytes'] and a['q_entries']==b['entries'] and a['scale_entries']==b['nodes'] for a,b in zip(x,fixtures))
        gates[ident+':allocations_released']=all(a['VM_allocations']==a['VM_releases']==(4 if item['arm']=='candidate' and a['fixture']!='river' else 0) for a in x)
        gates[ident+':sample_coverage']=r['sample_count']>=P['minimum_process_samples'] and r['max_sample_gap_ms']<=P['max_sample_gap_ms']
    summary=[];baseline_total=candidate_total=0
    for index,fixture in enumerate(P['fixture_order']):
        b=[rows['B'+str(i)][index]['complete_ns']/1e6 for i in [1,2,3]];c=[rows['C'+str(i)][index]['complete_ns']/1e6 for i in [1,2,3]]
        bm=statistics.median(b);cm=statistics.median(c);baseline_total+=bm;candidate_total+=cm
        slower=sum(c0>b0 for b0,c0 in zip(b,c));failed=cm>bm and slower>=2
        gates[fixture+':strict_fixture_slowdown_clear']=not failed
        summary.append({'fixture':fixture,'baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'slower_pairs':slower,'strict_guard_failed':failed})
    saving=baseline_total-candidate_total;gates['inclusive_component_saving_proxy']=saving>=P['minimum_component_saving_ms']
    resource_summary={}
    for metric in ['CPU_ms','lifetime_ms']:
        b=[resources['B'+str(i)]['terminal_process_times'][metric] for i in [1,2,3]];c=[resources['C'+str(i)]['terminal_process_times'][metric] for i in [1,2,3]]
        delta=(statistics.median(c)/statistics.median(b)-1)*100
        gates[metric+':process_regression_clear']=delta<=P['process_CPU_or_lifetime_max_regression_pct'];resource_summary[metric]={'baseline':b,'candidate':c,'median_regression_pct':delta}
    for metric in ['reported_working_set_high_water_bytes','reported_commit_high_water_bytes']:
        b=[resources['B'+str(i)][metric] for i in [1,2,3]];c=[resources['C'+str(i)][metric] for i in [1,2,3]]
        gates[metric+':median_allowance_clear']=statistics.median(c)<=statistics.median(b)+P['reported_memory_max_added_bytes']
        gates[metric+':max_allowance_clear']=max(c)<=max(b)+P['reported_memory_max_added_bytes']
        resource_summary[metric]={'baseline':b,'candidate':c,'median_added_bytes':statistics.median(c)-statistics.median(b),'max_added_bytes':max(c)-max(b)}
    passed=all(gates.values());D=ROOT/'comparisons/D160-arena-lifecycle';D.mkdir(exist_ok=False)
    report={'id':'D160','at':h.now(),'status':'admit_source_design_only' if passed else 'declined_component_lifecycle_or_resources','protocol_sha256':h.sha(H/'protocol.json'),'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'fixture_lifecycle_summary':summary,'baseline_sum_fixture_medians_ms':baseline_total,'candidate_sum_fixture_medians_ms':candidate_total,'component_saving_ms':saving,'required_effort_proxy_ms':P['minimum_component_saving_ms'],'resource_summary':resource_summary,'all_native_component_rows':rows,'all_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'performance_qualification_samples':0,'new_production_source_created':False,'candidate_accepted':False,'scope':'CPU-only component and process-cost effort selection. Every initial zero bit and both full pattern rounds validated before frees; synthetic dense16-thread writes differ from actual quantizer scheduling/GPU transport. Memory counters sampled while alive;late peak may be missed. No full-solve or universally removable saving,accuracy,capacity or adoption claim. Failure closes this backend form without threshold/touch/schedule/fixture/sample/source rescue.'}
    h.save(D/'report.json',report);verify();h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(D/'report.json'),'all_owned_children_terminal':True,'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D160')
    item.update(status='measured',correctness='component_all_bits_exact',stage='Source-design prerequisite admitted' if passed else 'Declined inclusive component/resource screen',reason=f'All18 fixture component records exact,all VM reservations released. Inclusive component difference {saving:.3f}ms versus fixed104.564ms effort proxy. Failed gates: '+(','.join(report['failed_gates']) or 'none')+'. CPU-only;no production implementation or full-solve gain.')
    item.setdefault('evidence',[]).append({'label':'Inclusive allocation/touch/free outcome','url':'evidence/D160-arena-lifecycle/report.json'})
    status.update(updated_at=h.now(),active_experiment='D160',stage='Arena lifecycle scout complete',activity=f'CPU-only arena component saved {saving:.3f}ms; '+('admitted source-design review only.' if passed else 'declined fixed prerequisite screen.')+' No current-RAM gain adopted;E08010.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({k:report[k] for k in ['status','failed_gates','component_saving_ms','resource_summary']}),flush=True)
