"""Read raw activity independently of execution, compare resources/counts exactly."""
from pathlib import Path
from collections import Counter,defaultdict
import json,re,struct,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');old.custody()
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in old.read(H/'binary-binding.json')['sha256'].items():old.pin(p,h)
assert old.read(H/'execution/complete.json')['all_owned_children_terminal']and not(R/'gpu-run.lock').exists()
checks=[]
def ck(label,value):
    checks.append({'label':label,'passed':bool(value)});assert value,label
reference=old.historical.exact_raw('E020C1');anchor=reference[0][0];trajectory=[x for x in reference[1]if x['fixture_id']=='rainbow']
names={int(n):name for name,n in re.findall(r'CUPTI_DRIVER_TRACE_CBID_(\w+)\s*=\s*(\d+)',Path(P['driver_cbid_header']).read_text())}
resource={};traces={};pins={};schema=struct.Struct('<6I4Q10I80s')
for arm in P['order']:
    d=H/'execution'/arm;raw=(d/'native.stdout.log').read_text();results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1])for x in raw.splitlines()if'AUTORESEARCH_RESULT 'in x];ck(arm+' full exact result',len(results)==1 and{k:v for k,v in results[0].items()if k not in old.historical.EXCLUDED}==anchor)
    stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1])for x in raw.splitlines()if'AUTORESEARCH_STAGE 'in x];cs=[{k:x[k]for k in['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}for x in stages if x.get('stage')=='convergence_check'];ck(arm+' ten exact checkpoints',cs==trajectory and len(cs)==10)
    data=(d/'trace.bin').read_bytes();ck(arm+' framing',data[:16]==b'D087-TRACE-v1\0\0\0'and(len(data)-16)%176==0);rows=list(schema.iter_unpack(data[16:]));meta=[json.loads(x)for x in(d/'collector.jsonl').read_text().splitlines()];q=meta[-1]
    ck(arm+' collector quality',len(meta)==8 and[x['event']for x in meta]==['start']+['phase']*6+['complete']and q['records']==len(rows)and all(q[k]==0 for k in['errors','dropped','invalid_timestamps','outstanding_buffers']))
    ck(arm+' phase order',[x['marker']for x in meta[1:-1]]==list(range(1,7))and all(a['timestamp_ns']<b['timestamp_ns']for a,b in zip(meta[1:-2],meta[2:-1])))
    ck(arm+' valid raw rows',all(x[0]in[1,2,3,4,10]and x[1]==0 and x[6]>0 and x[7]>=x[6]for x in rows))
    ks=[x for x in rows if x[0]in[3,10]];apis=[x for x in rows if x[0]==4];ai={x[4]:x for x in apis};ck(arm+' counts',len(ks)==q['kernels']==26230 and len(apis)==q['driver_api_records']and len(ai)==len(apis))
    ck(arm+' kernel launch API joins',all(x[4]in ai and names[ai[x[4]][5]]in(['cuGraphLaunch','cuGraphLaunch_ptsz']if x[10]else['cuLaunchKernel','cuLaunchKernel_ptsz'])for x in ks))
    gs=[x for x in apis if names[x[5]]in['cuGraphLaunch','cuGraphLaunch_ptsz']];ck(arm+' 407 graph launches',len(gs)==407 and all(x[10]==0 for x in gs))
    def desc(x):return(x[20].split(b'\0',1)[0].decode(),*x[11:20])
    graphs=defaultdict(lambda:defaultdict(list))
    for x in ks:
        if x[10]or x[9]:ck(arm+' graph IDs positive',x[10]>0 and x[9]>0);graphs[x[10]][x[9]].append(x)
    group=[];repeats=[]
    for graph,nodes in graphs.items():
        lens={len(v)for v in nodes.values()};ck(arm+' uniform graph repeats',len(lens)==1);n=next(iter(lens));repeats.append(n)
        ck(arm+' per-node descriptor invariant',all(len({desc(x)for x in v})==1 for v in nodes.values()));counter=Counter(desc(v[0])for v in nodes.values());group.append({'repeats':n,'nodes':len(nodes),'descriptors':sorted((list(k),v)for k,v in counter.items())})
    ck(arm+' all three graph repeat groups',sorted(repeats)==[9,199,199])
    descriptors=Counter(desc(x)for x in ks);resource[arm]={x[20].split(b'\0',1)[0].decode():set()for x in ks}
    for x in ks:resource[arm][x[20].split(b'\0',1)[0].decode()].add((x[17],x[18],x[19]))
    traces[arm]={'records':len(rows),'kernels':len(ks),'graph_launches':len(gs),'driver_api_counts_and_returns':sorted((names[k[0]],k[1],v)for k,v in Counter((x[5],x[10])for x in apis).items()),'kernel_descriptors_and_counts':sorted((list(k),v)for k,v in descriptors.items()),'graph_groups':sorted(group,key=lambda x:(x['repeats'],x['nodes'],str(x['descriptors']))),'collector':q,'all_results_and_checkpoints_exact':True}
    for name in['trace.bin','collector.jsonl','native.stdout.log','native.stderr.log','native.exit.json','native.invocation.json']:pins[str(d/name)]=old.sha(d/name)
for key in['kernels','graph_launches','driver_api_counts_and_returns','kernel_descriptors_and_counts','graph_groups']:ck('exact baseline candidate '+key,traces['baseline'][key]==traces['candidate'][key])
d=H/'execution/resources';raw=(d/'native.stdout.log').read_text();rr=[json.loads(x.split('E080_RESOURCE ',1)[1])for x in raw.splitlines()if'E080_RESOURCE 'in x];ck('all18 resource records',len(rr)==18)
compiled={arm:{x['kernel']:{k:v for k,v in x.items()if k!='arm'}for x in rr if x['arm']==arm}for arm in P['order']};ck('all nine function resources exactly equal',len(compiled['baseline'])==9 and compiled['baseline']==compiled['candidate'])
ck('complete compiled PTX bytes exactly equal',(d/'baseline.ptx').read_bytes()==(d/'candidate.ptx').read_bytes())
for arm in P['order']:
    for name,launched in resource[arm].items():
        attrs=compiled[arm][name];ck(arm+' launched register/static shared '+name,{(x[0],x[1])for x in launched}=={(attrs['registers'],attrs['static_shared_bytes'])})
    ck(arm+' launched family subset of compiled resources',set(resource[arm])<=set(compiled[arm]))
for p in d.iterdir():
    if p.is_file():pins[str(p)]=old.sha(p)
report={'at':old.now(),'status':'pass_registered_graph_and_compiled_resource_equivalence','checks_passed':len(checks),'all_checks_pass':True,'checks':checks,'protocol_sha256':sys.argv[1],'traces':traces,'compiled_resources':compiled,'raw_sha256':pins,'native_trace_processes':2,'resource_probe_processes':1,'full_results_exact':2,'checkpoints_exact':20,'timing_score':False,'candidate_adopted':False,'limits':'Largest registered fixture only for actual graph/kernel invocation equivalence. Driver resource probe uses byte-identical accepted/E080 CUDA and original compile options. Same full PTX and all nine local/register/shared/occupancy resources; actual launched register/shared attributes cross-checked. No hardware counters, occupancy measurement, speed estimate, statistical timing or universal resource claim. Whole-workload memory and CPU qualification is separate. Original failed research symmetry and combined calibration gates remain failed.'}
old.save(H/'report.json',report);old.custody();print(json.dumps({'status':report['status'],'checks':len(checks),'compiled_resources':compiled['candidate']}),flush=True)
