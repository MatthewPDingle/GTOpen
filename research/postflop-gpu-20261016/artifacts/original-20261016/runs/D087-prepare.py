"""Retained device-gap census, then freeze an explicit driver-API observer."""
import json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D087-cupti-driver-profile';H.mkdir();prior=ROOT/'runs/D085-cupti-activity'
schema=struct.Struct('<6I4Q10I80s');reference=old.read(ROOT/'comparisons/D085-activity-root-check/report.json')
def union(spans):
 result=[]
 for a,b in sorted(spans):
  if not result or a>result[-1][1]:result.append([a,b])
  else:result[-1][1]=max(result[-1][1],b)
 return result
def duration(spans):return sum(b-a for a,b in union(spans))
census={};inputs={}
for identity in ['D085T1','D085T2','D085T3']:
 p=prior/'cohort-execution/traces'/identity/'trace.bin';old.pin(p,reference['preserved_raw_sha256'][str(p)]);inputs[str(p)]=old.sha(p)
 data=p.read_bytes();assert data[:16]==b'D085-TRACE-v1\0\0\0' and (len(data)-16)%176==0
 rows=list(schema.iter_unpack(data[16:]));assert all(r[0] in [1,2,3,10] and r[6]>0 and r[7]>=r[6] for r in rows)
 kernels=[r for r in rows if r[0] in [3,10]];assert len(kernels)==26230
 active=union([(r[6],r[7]) for r in rows]);lo,hi=active[0][0],active[-1][1];kl=min(r[6] for r in kernels);kh=max(r[7] for r in kernels)
 gaps=[{'start_ns':a[1],'end_ns':b[0],'ms':(b[0]-a[1])/1e6} for a,b in zip(active,active[1:]) if b[0]>a[1]]
 inside=[(max(r[6],kl),min(r[7],kh)) for r in rows if r[7]>=kl and r[6]<=kh]
 census[identity]={'activity_span_ms':(hi-lo)/1e6,'device_activity_union_ms':duration([(r[6],r[7]) for r in rows])/1e6,'uncovered_inside_activity_span_ms':((hi-lo)-duration([(r[6],r[7]) for r in rows]))/1e6,'kernel_span_ms':(kh-kl)/1e6,'kernel_union_ms':duration([(r[6],r[7]) for r in kernels])/1e6,'uncovered_by_any_device_activity_within_kernel_span_ms':((kh-kl)-duration(inside))/1e6,'activity_before_first_kernel_span_ms':(kl-lo)/1e6,'activity_after_last_kernel_span_ms':(hi-kh)/1e6,'largest_uncovered_gaps':sorted(gaps,key=lambda x:x['ms'],reverse=True)[:12]}
old.save(H/'gap-census.json',{'id':'D087-retained-gap-census','at':old.now(),'root_replay_only':True,'native_executions':0,'optimization_accepted':False,'traces':census,'input_sha256':inputs,'motivation':'Separate uncovered observed device spans from busy-kernel time. Add direct Driver API activity and phase markers to determine where host/API work lies, instead of treating all gaps as removable GPU headroom.','limits':'Only retained D085 rainbow device timeline. Does not cover CPU time before first device event or after last. Uncovered intervals may be dependencies or observer effects, not removable delay or complete-cycle gains.'})
s=(prior/'collector.cpp').read_text(encoding='utf-8').replace('D085','D087')
s=s.replace("'D','0','8','5'","'D','0','8','7'")
s=s.replace('sets{0},badTimes','sets{0},apis{0},badTimes')
s=s.replace('enabled[3]={false,false,false}','enabled[4]={false,false,false,false}')
s=s.replace('kinds[3]={CUPTI_ACTIVITY_KIND_CONCURRENT_KERNEL,CUPTI_ACTIVITY_KIND_MEMCPY,CUPTI_ACTIVITY_KIND_MEMSET}','kinds[4]={CUPTI_ACTIVITY_KIND_CONCURRENT_KERNEL,CUPTI_ACTIVITY_KIND_MEMCPY,CUPTI_ACTIVITY_KIND_MEMSET,CUPTI_ACTIVITY_KIND_DRIVER}')
s=s.replace('i<3','i<4')
needle='        }else {errors.fetch_add(1);continue;}'
assert s.count(needle)==1
s=s.replace(needle,'''        }else if(activity->kind==CUPTI_ACTIVITY_KIND_DRIVER){
            auto *a=(CUpti_ActivityAPI*)activity;
            row.context=a->processId;row.stream=a->threadId;row.correlation=a->correlationId;row.detail=a->cbid;
            row.start=a->start;row.end=a->end;row.graph=a->returnValue;apis.fetch_add(1);
        }else {errors.fetch_add(1);continue;}''')
needle='extern "C" __declspec(dllexport) uint32_t D087StartTrace() {'
assert s.count(needle)==1
phase='''// Host phase timestamp in CUPTI's activity time domain, diagnostic only.
extern "C" __declspec(dllexport) uint32_t D087PhaseTrace(uint32_t marker) {
    if(state!=1||!metaFile)return 0;
    uint64_t timestamp=0;if(!check(cuptiGetTimestamp(&timestamp),"phase_timestamp")||!timestamp)return 0;
    AcquireSRWLockExclusive(&fileLock);
    fprintf(metaFile,"{\\"event\\":\\"phase\\",\\"marker\\":%u,\\"timestamp_ns\\":%llu}\\n",marker,(unsigned long long)timestamp);fflush(metaFile);
    ReleaseSRWLockExclusive(&fileLock);return errors.load()==0;
}
'''
s=s.replace(needle,phase+needle)
s=s.replace('\\"memsets\\":%llu,','\\"memsets\\":%llu,\\"driver_api_records\\":%llu,')
s=s.replace('copies.load(),sets.load(),dropped.load()','copies.load(),sets.load(),apis.load(),dropped.load()')
assert 'driver_api_records' in s and 'D085' not in s and s.count('i<4')==2
(H/'collector.cpp').write_text(s,encoding='utf-8',newline='\n')
a=(prior/'ability.rs').read_text(encoding='utf-8').replace('D085','D087').replace('d085','d087')
a=a.replace('fn D087StartTrace()->u32;','fn D087StartTrace()->u32;fn D087PhaseTrace(marker:u32)->u32;')
a=a.replace(' let ctx=CudaContext::new(0)', ' assert_eq!(unsafe{D087PhaseTrace(1)},1);\n let ctx=CudaContext::new(0)')
a=a.replace('assert_eq!(unsafe{D087FlushTrace()},1);','assert_eq!(unsafe{D087PhaseTrace(6)},1);assert_eq!(unsafe{D087FlushTrace()},1);')
(H/'ability.rs').write_text(a,encoding='utf-8',newline='\n')
(H/'build.py').write_text((prior/'build-r3.py').read_text(encoding='utf-8').replace('D085','D087').replace('build-plan-r3.json','build-plan.json'),encoding='utf-8',newline='\n')
oldP=old.read(prior/'build-plan-r3.json');p=dict(oldP);p.update(id='D087-build',at=old.now(),build_dir=str(H/'build'))
def remap(x):
 return x.replace(str(prior/'collector.cpp'),str(H/'collector.cpp')).replace(str(prior/'ability.rs'),str(H/'ability.rs')).replace(str(prior/'build-r3'),str(H/'build')).replace('D085Collector','D087Collector').replace('d085_ability','d087_ability')
p['collector_command']=[remap(x) for x in p['collector_command']];p['ability_command']=[remap(x) for x in p['ability_command']]
p['private_dll_dirs']=[str(H/'build'),str(prior/'vendor/cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive/lib')]
header=prior/'vendor/cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive/include/cupti_driver_cbid.h'
old.save(H/'proposal.json',{'at':old.now(),'id':'D087','type':'diagnostic_only','prior_goal_turn':'progress: D085 profiler validated and E054 exact full-cycle screen rejected','accepted_source':'E051','proposal':'Add CUPTI Driver API activity records and six explicit init/solve/readback phase timestamps to separate host/API costs from device work. Preserve direct collector lifecycle and accepted solver library.','evidence_basis':str(H/'gap-census.json'),'schema':'Existing176byte row; kind4 has cbid in detail, processId/context, threadId/stream, returnValue/graph, unique correlationId; no kernel-node fields reused for interpretation. Names decoded offline from matching SDK cbid header.','quality_gates':'Ability13kernel/4graphlaunch/4kernelAPIcall complete control, exact data/guards, valid API timestamps/correlation and0errors/drops. Then fixed3matched ordinary/observed rainbow pairs, exact6states/60checks, per-pair absolute complete/native/outer observer change<=10%, no exclusions/pooling/extensions.','phase_ids':{'1':'GPUinitbegin after collector start','2':'GPUinitend after GPU synchronize','3':'solvebegin','4':'solveend after GPU synchronize','5':'readbackbegin','6':'readbackend after GPU synchronize'},'limits':'No new solver change or optimization accepted. API time can include waiting on device and overlap GPU intervals; not additive to kernel time or a removable-speedup bound. No admin, counters, injection, driver/global installation or setting changes.','source_current_policy':str(old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md')})
p['input_sha256']=dict(oldP['input_sha256'])|{str(x):old.sha(x) for x in [H/'collector.cpp',H/'ability.rs',H/'build.py',H/'gap-census.json',H/'proposal.json',header,ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/E054-closure/decision.json']}
for f,h in p['input_sha256'].items():old.pin(f,h)
old.save(H/'build-plan.json',p)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='D087' for e in st['experiments']);st['experiments'].append({'id':'D087','title':'Driver API and phase timeline profiling','kind':'diagnostic','status':'preparing','stage':'Retained device gaps measured; collector build next','reason':'Use directAPI records and timestamp brackets to investigate init/readback/graph boundaries. No optimizer source change or accepted speedup.','evidence':[]});st.update(state='running',stage='D087 API timeline feasibility',activity='Existing traces expose uncovered device intervals. Build private direct-CUPTI driver observer; gate usefulness before interpreting host/API timing.',active_experiment='D087',updated_at=old.now());old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'build_protocol_sha256':old.sha(H/'build-plan.json'),'gap_census':{i:{k:v for k,v in q.items() if k!='largest_uncovered_gaps'} for i,q in census.items()}}),flush=True)
