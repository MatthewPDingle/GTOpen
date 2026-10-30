"""Read every frame/record, compare original pairs, apply frozen component budget."""
from pathlib import Path
import json,struct,sys,statistics,math
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=H/'execution';old.custody();assert not(R/'gpu-run.lock').exists();assert old.read(E/'complete.json')['all_owned_children_terminal'];checks=0
for p,h in P['input_sha256'].items():old.pin(p,h)
def ck(v,label):
    global checks
    assert v,label;checks+=1
def frame(path):
    data=path.read_bytes();ck(data[:16]==b'D134-FRAME-v1\0\0\0','frame magic');at=16;fields={};explicit=zero=0
    while at<len(data):
        kind,n=struct.unpack_from('<II',data,at);at+=8;ck(kind in[0,1]and n<256,'record header');name=data[at:at+n].decode();at+=n;count,=struct.unpack_from('<Q',data,at);at+=8;ck(name not in fields and count<2**32,'unique extent')
        if kind==0:
            value,=struct.unpack_from('<I',data,at);at+=4;ck(value==0,'full checked positive-zero run');zero+=count
        else:
            end=at+count*8;ck(end<=len(data),'explicit image bounds');a=memoryview(data)[at:at+count*4].cast('I');b=memoryview(data)[at+count*4:end].cast('I');ck(a==b,'full actual metadata/arena bytes');explicit+=count;at=end
        fields[name]={'kind':kind,'words':count}
    ck(at==len(data)and len(fields)==66,'entire66field frame');return{'fields':fields,'explicit_words':explicit,'verified_positive_zero_words':zero,'sha256':old.sha(path),'bytes':len(data)}
ability=old.read(E/'ability-report.json');ck(ability['status']=='pass_scoped_fresh_warm_compressed_F32_and_budget','ability passed');frames={};ability_frames={}
for p in(E/'ability').glob('*.bin'):ability_frames[p.name]=frame(p)
ck(len(ability_frames)==8,'all8ability images')
for name in ability_frames:
    if not name.startswith('B-'):continue
    other='C-'+name[2:];ck((E/'ability'/name).read_bytes()==(E/'ability'/other).read_bytes(),'ability full paired frame equality')
cases={};last=None
from datetime import datetime
for row in P['order']:
    identity=row['id'];receipt=old.read(E/(identity+'.exit.json'));ck(receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None,'terminal child');a,b=datetime.fromisoformat(receipt['started_at']),datetime.fromisoformat(receipt['finished_at']);ck(a<=b and(last is None or last<=a),'sequential process order');last=b
    q=old.read(E/(identity+'.parsed.json'));cases[identity]=q['cases'];ck(len(cases[identity])==3,'all3components')
    for path,h in q['frame_sha256'].items():old.pin(path,h)
    for mark in q['cases']:
        path=E/identity/(mark['id']+'-device-frame.bin');proof=frame(path);frames[str(path)]=proof;ck(mark['proof']['metadata_fields']==57 and mark['proof']['fields']==66,'full metadata inventory');ck(sum(x['words']for x in mark['proof']['records'])==proof['explicit_words']+proof['verified_positive_zero_words'],'all word inventories');ck(mark['all_four_host_stores_positive_zero']and mark['solver_iteration']==0 and mark['kernel_launches']==0,'fresh component scope');ck(len([x for x in proof['fields'].values()if x['kind']==0])==9,'nine complete zero runs')
derived=[]
for i,name in enumerate(P['workloads']):
    baseline=[cases[p['baseline']][i]for p in P['pairs']];candidate=[cases[p['candidate']][i]for p in P['pairs']]
    for b,c in zip(baseline,candidate):
        ck(b['board']==c['board']and b['nodes']==c['nodes']and b['storage']==c['storage'],'same workload');ck(b['proof']==c['proof'],'complete proof descriptors exact');bi=next(row['id']for row in P['order']if cases[row['id']][i]is b);ci=next(row['id']for row in P['order']if cases[row['id']][i]is c);ck((E/bi/(b['id']+'-device-frame.bin')).read_bytes()==(E/ci/(c['id']+'-device-frame.bin')).read_bytes(),'whole paired frame bytes exact')
    bv=[x['component_ms']for x in baseline];cv=[x['component_ms']for x in candidate];bc=[x['CPU_ms']for x in baseline];cc=[x['CPU_ms']for x in candidate];bm,cm=statistics.median(bv),statistics.median(cv);bcm,ccm=statistics.median(bc),statistics.median(cc);saving=bm-cm;improving=sum(a>b for a,b in zip(bv,cv));cpu_limit=bcm*1.02+15.625;wall_gate=i==2 or(saving>0 and improving>=2);cpu_gate=ccm<=cpu_limit
    derived.append({'fixture_id':name,'baseline_component_ms':bv,'candidate_component_ms':cv,'baseline_median_ms':bm,'candidate_median_ms':cm,'saving_of_medians_ms':saving,'improving_pairs':improving,'large_fixture_wall_gate':wall_gate,'baseline_CPU_ms':bc,'candidate_CPU_ms':cc,'baseline_CPU_median_ms':bcm,'candidate_CPU_median_ms':ccm,'CPU_limit_ms':cpu_limit,'CPU_guard_pass':cpu_gate})
total=sum(x['saving_of_medians_ms']for x in derived);budget=total>=P['minimum_saving_ms'];admit=budget and all(x['large_fixture_wall_gate']and x['CPU_guard_pass']for x in derived)
report={'at':old.now(),'id':'D134-zero-init-fence-component','status':'admit_one_integrated_trial'if admit else'closed_component_admission_failed','protocol_sha256':sys.argv[1],'checks':checks,'fixtures':derived,'sum_fixture_median_component_saving_ms':total,'minimum_saving_ms':P['minimum_saving_ms'],'component_budget_pass':budget,'all_complete_frames_exact':True,'ability_fresh_warm_compressed_F32_pass':True,'ability_frames':ability_frames,'frames':frames,'all_owned_children_terminal':True,'compiler_count':1,'ability_processes':1,'timing_processes':6,'initialization_components':18,'application_kernel_launches':0,'full_solver_executions':0,'admit_one_integrated_trial':admit,'candidate_accepted':False,'source_activated':False,'source_main_live_PTX_custody_pass':True,'limits':'Copied-constructor full GPU-initialization component only, not a complete solve or observed1%full-cycle gain. Every exposed device field compared to CPU references and paired frames. Full GPU positive-zero images were read and checked, represented losslessly as zero runs; no separate full raw zero files. CPU observer outside timing; full stage cost retained. No actual forced allocator/hardware failure. Material/whole-solver/graph/application/holdout/cumulative checks remain if admitted. No extensions, variants or retry rescue.'};old.save(H/'report.json',report);old.custody();print(json.dumps({'status':report['status'],'saving_ms':total,'minimum_ms':P['minimum_saving_ms'],'checks':checks,'fixtures':derived}),flush=True)
