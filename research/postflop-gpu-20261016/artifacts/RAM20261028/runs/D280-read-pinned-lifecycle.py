import collections,datetime,hashlib,json,statistics,struct,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D280-pinned-registration-lifecycle';P=h.read(H/'protocol.json');O=H/'execution';assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1])
for p,d in P['input_sha256'].items():h.pin(p,d)
h.custody();checks=0;last=time.monotonic();files={};rows={};resources={};completions={};raw_words=0;raw_bytes=0
def req(x):
    global checks
    assert x;checks+=1
def note(label):
    global last
    if time.monotonic()-last>20:print(label,'checks',checks,flush=True);last=time.monotonic()
def read_file(path,words,round,page):
    global raw_words,raw_bytes
    digest=hashlib.sha256();size=path.stat().st_size;req(size==40+4*words)
    with path.open('rb')as f:
        header=f.read(40);req(header[:16]==b'D280-PIN-RAW1\0\0\0');n,r,p,bytes=struct.unpack('<QIIQ',header[16:]);req((n,r,p,bytes)==(words,round,page,words*4));digest.update(header);at=0
        while at<words:
            count=min(262144,words-at);data=f.read(count*4);req(len(data)==count*4);values=np.frombuffer(data,dtype='<u4');index=np.arange(at,at+count,dtype=np.uint64);seed=0x243f6a88^((round*0x85ebca6b)&0xffffffff);x=(index*np.uint64(0x9e3779b9)+np.uint64(seed))&np.uint64(0xffffffff);expected=(((x<<np.uint64(7))|(x>>np.uint64(25)))&np.uint64(0xffffffff))^np.uint64(0xa5a55a5a);req(np.array_equal(values,expected.astype('<u4')));at+=count;digest.update(data);note('Every raw roundtrip word')
        req(not f.read(1))
    raw_words+=words;raw_bytes+=size;files[str(path)]={'bytes':size,'words':words,'round':round,'page':page,'sha256':digest.hexdigest(),'every_word_independent_integer_oracle_exact':True};return files[str(path)]
fixtures=h.read(H/'fixtures.json');fixture_map={x['fixture']:x for x in fixtures};previous_exit=None
for item in P['sequence']:
    id=item['id'];receipt=h.read(O/(id+'.exit.json'));inv=h.read(O/(id+'.invocation.json'));req(receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None)
    if previous_exit is not None:req(previous_exit<=inv['at'])
    previous_exit=receipt['finished_at'];text=(O/(id+'.stdout.log')).read_text(encoding='utf-8');req('D280_CLEANUP_ERROR'not in(O/(id+'.stderr.log')).read_text(encoding='utf-8'))
    def extract(tag):return[json.loads(line.split(tag+' ',1)[1])for line in text.splitlines()if line.startswith(tag+' ')]
    cases=extract('D280_CASE');complete=extract('D280_COMPLETE');failure=extract('D280_FAILURE_CLEANUP');warm=item['role']=='warmup';expected_names=(['boundary-1','boundary-1023','boundary-1024','boundary-1025']if warm else[])+P['fixture_order'];req([x['fixture']for x in cases]==expected_names and len(complete)==1);c=complete[0];req(c['cases']==len(cases)and c['canonical_fixtures']==3 and c['arm']==item['arm']and c['warmup']==warm and c['all_host_and_device_ranges_released']and c['all_CUDA_objects_dropped']);req(c['CUDA_application_kernels']==c['NVRTC_compiles']==c['CFR_iterations']==0);req(c['original_PinnedBuf_bytes']==16 and c['registered_owner_bytes']==24 and c['component_enum_bytes']<=32)
    req(len(failure)==(1 if warm and item['arm']=='candidate'else 0))
    if failure:req(failure==[{'zero_byte_registration_rejected':True,'owned_VM_reservation_released':True,'no_unregister_for_failed_registration':True,'counter_delta':[0,0,1,1,1,0,0]}])
    expected_counts=[0]*7
    if failure:expected_counts=[0,0,1,1,1,0,0]
    expected_files=set()
    for case in cases:
        name=case['fixture'];words=fixture_map[name]['words']if case['canonical']else int(name.split('-')[1]);logical=words*4;page=case['page_size'];req(case['arm']==item['arm']and case['warmup']==warm and case['words']==words and case['logical_bytes']==logical and page>=4096 and page&(page-1)==0);req(case['backing_rounded_bytes']==(logical+page-1)//page*page)
        registered=item['arm']=='candidate'and logical>=P['registration_threshold_bytes'];delta=[0,0,1,1,1,1,1]if registered else[1,1,0,0,0,0,0];req(case['registered_route']==registered and case['counter_delta']==delta);expected_counts=[a+b for a,b in zip(expected_counts,delta)];req(case['all_words_full_bit_verified']and case['word_checks']==2*words and case['threads']==16 and case['CUDA_application_kernels']==case['CFR_iterations']==0)
        guards=[(0xd34db33f+i)&0xffffffff for i in range(64)]+[(0x78563412+i)&0xffffffff for i in range(64)];req(case['device_guard_words']==[guards,guards]);req(len(case['cycles_ns'])==2 and all(v>0 for v in[case['allocation_ns'],case['close_ns'],*case['cycles_ns']]));req(case['complete_component_ns']==case['allocation_ns']+case['close_ns']+sum(case['cycles_ns']))
        for round in range(2):
            path=H/id/(name+'-round'+str(round)+'.bin');expected_files.add(path.name);read_file(path,words,round,page)
    req({p.name for p in(H/id).iterdir()}==expected_files);req(c['counts']==expected_counts and expected_counts[0]==expected_counts[1]and expected_counts[2]==expected_counts[3]and expected_counts[5]==expected_counts[6]);rows[id]=cases;completions[id]=c;resource=h.read(O/(id+'.resource.json'));req(resource['returncode']==0 and resource['sample_count']>=P['minimum_process_samples']and resource['max_sample_gap_ms']<=P['max_sample_gap_ms']);req(all(s['system_memory']['available_physical_bytes']>=P['available_RAM_before_and_during_bytes']for s in resource['samples']));resources[id]=resource;print(id,'all complete raw outputs/counters exact',flush=True)
req(raw_bytes<=P['raw_reservation_bytes']);paired=[]
for pair in[{'baseline':'WB','candidate':'WC'},*P['pairs']]:
    b,c=pair['baseline'],pair['candidate'];req([x['fixture']for x in rows[b]]==[x['fixture']for x in rows[c]])
    for case in rows[b]:
        for round in range(2):
            name=case['fixture']+'-round'+str(round)+'.bin';left,right=H/b/name,H/c/name;req(files[str(left)]['bytes']==files[str(right)]['bytes']);compared=0
            with left.open('rb')as x,right.open('rb')as y:
                while True:
                    aa=x.read(4*1024**2);bb=y.read(4*1024**2);req(aa==bb)
                    if not aa:break
                    compared+=len(aa);note('Whole raw file pair comparison')
            req(compared==left.stat().st_size and files[str(left)]['sha256']==files[str(right)]['sha256']);paired.append({'baseline':str(left),'candidate':str(right),'each_bytes':compared,'entire_files_literal_equal':True})
gates={};performance=[];baseline_total=candidate_total=0
for fixture in P['fixture_order']:
    b=[next(x for x in rows[p['baseline']]if x['fixture']==fixture)['complete_component_ns']/1e6 for p in P['pairs']];c=[next(x for x in rows[p['candidate']]if x['fixture']==fixture)['complete_component_ns']/1e6 for p in P['pairs']];bm=statistics.median(b);cm=statistics.median(c);slower=sum(cc>bb for bb,cc in zip(b,c));failed=cm>bm and slower>=2;gates[fixture+':strict_fixture_clear']=not failed;baseline_total+=bm;candidate_total+=cm
    stages={}
    for stage in['allocation_ns','close_ns']:
        stages[stage]={'baseline_median_ms':statistics.median(next(x for x in rows[p['baseline']]if x['fixture']==fixture)[stage]for p in P['pairs'])/1e6,'candidate_median_ms':statistics.median(next(x for x in rows[p['candidate']]if x['fixture']==fixture)[stage]for p in P['pairs'])/1e6}
    performance.append({'fixture':fixture,'baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'slower_pairs':slower,'strict_guard_failed':failed,'component_stage_medians':stages})
saving=baseline_total-candidate_total;gates['component_effort_saving']=saving>=P['minimum_component_saving_ms'];costs={}
for label,get in [('CPU_ms',lambda r:r['terminal_process_times']['CPU_ms']),('native_lifetime_ms',lambda r:r['terminal_process_times']['lifetime_ms']),('parent_wall_ms',lambda r:r['parent_wall_ms'])]:
    b=[get(resources[p['baseline']])for p in P['pairs']];c=[get(resources[p['candidate']])for p in P['pairs']];bm=statistics.median(b);cm=statistics.median(c);req(bm>0 and cm>0);gates[label+':median_no_over1pct_cost']=cm<=bm*(1+P['process_CPU_lifetime_parent_wall_max_median_regression_pct']/100);costs[label]={'baseline':b,'candidate':c,'baseline_median':bm,'candidate_median':cm,'median_increase_pct':100*(cm/bm-1)}
for key in['reported_working_set_high_water_bytes','reported_commit_high_water_bytes','sampled_private_commit_max_bytes','sampled_system_commit_max_increment_bytes','sampled_global_GPU_increment_bytes']:
    b=[resources[p['baseline']][key]for p in P['pairs']];c=[resources[p['candidate']][key]for p in P['pairs']];bm=statistics.median(b);cm=statistics.median(c);limit=P['sampled_system_commit_max_added_bytes']if'system_commit'in key else P['sampled_global_GPU_max_added_bytes']if'GPU'in key else P['reported_memory_max_added_bytes'];gates[key+':median_added_within_limit']=cm<=bm+limit;costs[key]={'baseline':b,'candidate':c,'baseline_median':bm,'candidate_median':cm,'median_added':cm-bm,'limit_added':limit}
passed=all(gates.values());h.custody();h.save(H/'report.json',{'id':'D280','at':h.now(),'status':'pass_component_only_pending_actual_source'if passed else'decline_pinned_registration_component_effort_fixture_or_cost','protocol_sha256':sys.argv[1],'gates':gates,'failed_gates':[k for k,v in gates.items()if not v],'performance':performance,'baseline_sum_fixture_component_median_ms':baseline_total,'candidate_sum_fixture_component_median_ms':candidate_total,'component_saving_ms':saving,'minimum_component_saving_ms':P['minimum_component_saving_ms'],'process_costs':costs,'full_raw_files':files,'full_raw_pairs':paired,'raw_bytes_retained':raw_bytes,'every_raw_word_independent_oracle_checks':raw_words,'native_case_records':rows,'native_completions':completions,'reader_checks':checks,'all_owned_native_processes_confirmed_terminal':True,'new_CUDA_applicationkernels_NVRTC_CFR_solver_or_speed_samples':0,'optimizer_source_activated':False,'candidate_accepted':False,'limits':P['scope']+' '+P['material_gate']+' '+P['interpretation']});print(json.dumps({'status':'pass_component_only'if passed else'decline','saving_ms':saving,'failed_gates':[k for k,v in gates.items()if not v],'raw_bytes':raw_bytes,'raw_words':raw_words,'raw_pairs':len(paired)}),flush=True)
