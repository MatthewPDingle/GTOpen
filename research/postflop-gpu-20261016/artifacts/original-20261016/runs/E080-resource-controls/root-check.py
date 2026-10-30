"""Read-only independent CPU/GPU/host arithmetic from retained native observations."""
from pathlib import Path
import json,statistics,sys
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');q=old.read(H/'report.json');old.custody();assert not(R/'gpu-run.lock').exists();checks=0;rows={};pids=set()
def ck(ok,label):
    global checks
    assert ok,label;checks+=1
for spec in P['order']:
    folder=H/'execution'/spec['id'];r=old.read(folder/'parsed.json');receipt=old.read(folder/'native.exit.json');ck(receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None,'terminal');ck(receipt['PID']==r['PID']and r['PID']not in pids,'unique owned PID');pids.add(r['PID']);old.pin(folder/'native.stdout.log',r['stdout_sha256']);old.pin(folder/'GPU-samples.json',r['GPU_samples_sha256'])
    text=(folder/'native.stdout.log').read_text(encoding='utf-8');stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1])for x in text.splitlines()if'AUTORESEARCH_STAGE 'in x];native=[x for x in stages if x.get('stage')=='resource_fixture'];suite=next(x['OS']for x in stages if x.get('stage')=='resource_suite_complete');phase={x['fixture_id']:(x['os_timing_complete']['cpu_ticks100ns']-x['os_begin']['cpu_ticks100ns'])/10000.0 for x in native};all_os=[x[k]for x in native for k in['os_begin','os_timing_complete','os_after_fingerprint']]+[suite]
    ck(phase==r['phase_CPU_ms']and sum(phase.values())==r['phase_sum_CPU_ms'],'native CPU boundaries');ck(receipt['final_CPU']['CPU_ticks100ns']/10000.0==r['whole_process_CPU_ms'],'whole process CPU');ck(max(x['peak_working_bytes']for x in all_os)==r['peak_working_bytes'],'OS working-set highwater');ck(max(x['peak_commit_bytes']for x in all_os)==r['peak_total_commit_bytes'],'OS total commit highwater')
    samples=old.read(folder/'GPU-samples.json');ck(samples['PID']==r['PID'],'sample owner');data=samples['samples'];times=[x['sample_perf_ns']for x in data];ck(all(a<b for a,b in zip(times,times[1:])),'sample ordering')
    for name,key in[('Dedicated Usage','GPU_dedicated_peak_bytes'),('Shared Usage','GPU_shared_peak_bytes')]:
        values=[]
        for sample in data:
            counter=sample['counters'][name];items=counter['instances'];ck(all(x['instance'].lower().startswith('pid_'+str(r['PID'])+'_')and x['CStatus']in[0,1]and x['bytes']>=0 for x in items),'owned valid instances');ck(counter['sum_bytes']==(sum(x['bytes']for x in items)if items else None),'counter sum')
            if counter['sum_bytes']is not None:values.append(counter['sum_bytes'])
        ck(values and max(values)==r[key],'actual GPU peak replay')
    rows[spec['id']]=r
g=P['guards'];derived=[]
for metric in['rainbow','two-tone','river','phase_sum_CPU_ms','whole_process_CPU_ms','peak_working_bytes','peak_total_commit_bytes','GPU_dedicated_peak_bytes','GPU_shared_peak_bytes']:
    values={arm:[rows[p[arm]]['phase_CPU_ms'][metric]if metric in['rainbow','two-tone','river']else rows[p[arm]][metric]for p in P['pairs']]for arm in['baseline','candidate']};b,c=statistics.median(values['baseline']),statistics.median(values['candidate'])
    if metric in['peak_working_bytes','peak_total_commit_bytes']:limit=b+max(g['host_peak_minimum_allowance_bytes'],b*g['host_peak_fraction'])
    elif metric.startswith('GPU_'):limit=b+g['GPU_peak_allowance_bytes']
    else:limit=b*(g['CPU_phase_fixture_ratio']if metric in['rainbow','two-tone','river']else g['CPU_phase_sum_ratio']if metric=='phase_sum_CPU_ms'else g['CPU_whole_process_ratio'])+g['CPU_allowance_ms']
    declared=next(x for x in q['checks']if x['metric']==metric);ck((declared['baseline_median'],declared['candidate_median'],declared['limit'],declared['passed'])==(b,c,limit,c<=limit),'fixed resource guard replay');derived.append({'metric':metric,'baseline_median':b,'candidate_median':c,'limit':limit,'passed':c<=limit})
passed=all(x['passed']for x in derived);ck(q['all_material_guards_pass']==passed,'overall material outcome');old.custody();old.save(H/'root-report.json',{'at':old.now(),'status':'pass_material_arithmetic_and_observation_replay'if passed else'pass_rejected_material_replay','checks':checks,'derived':derived,'all_material_guards_pass':passed,'report_sha256':old.sha(H/'report.json'),'root_cross_check_only':True,'candidate_accepted':False,'source_main_live_PTX_unchanged':True,'limits':'Independent stdlib arithmetic and retained-record/owner checks by root; not an external independent audit or universal physical GPU peak proof. Original calibration and experimental research failures remain failed. Responsiveness and final compiled-resource/graph/scope audit remain.'});print(json.dumps({'status':'pass_material_replay'if passed else'pass_rejected_material_replay','checks':checks}),flush=True)
