"""Serialize one CPU SDK allocation calculation and replay all captured rows."""
import json, shutil, struct, sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
    old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
verify();B=H/'build';E=H/'execution';assert not B.exists() and not E.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3
    B.mkdir();E.mkdir();old.child(P['command'],B,'cl',old.env(),180);verify()
    binary=old.sha(B/'probe.exe');old.save(B/'complete.json',{'at':old.now(),'binary_sha256':binary,'compiler_terminal':True,'native_executions':0})
    old.child([str(B/'probe.exe')],E,'probe',old.env(),120);verify();old.pin(B/'probe.exe',binary)
    raw=(E/'probe.stdout.log').read_text();device=[];rows=[];complete=[]
    for line in raw.splitlines():
        if line.startswith('D094_DEVICE '):device.append(json.loads(line.split(' ',1)[1]))
        elif line.startswith('D094_ALLOC '):rows.append(json.loads(line.split(' ',1)[1]))
        elif line.startswith('D094_COMPLETE '):complete.append(json.loads(line.split(' ',1)[1]))
        else:assert not line.strip(),line
    assert len(device)==len(complete)==1;dev=device[0]
    assert dev['gpu']=='NVIDIA GeForce RTX 5090' and (dev['major'],dev['minor'],dev['warp_size'],dev['register_quantum_per_warp'])==(12,0,32,256)
    assert len(rows)==complete[0]['rows']==20480 and complete[0]['kernel_launches']==complete[0]['solver_executions']==0 and complete[0]['performance_measured'] is False
    historical=old.read(ROOT/'runs/E057-resource/report.json');shapes=old.read(ROOT/'runs/E057-resource/protocol.json')['shapes']
    expected=[(name,regs,threads) for name in shapes for regs in [38,40] for threads in range(1,1025)]
    assert [(r['shape'],r['nominal_registers'],r['threads']) for r in rows]==expected
    indexed={};checks=0;matches=0
    for row in rows:
        n=row['nominal_registers'];t=row['threads'];q=dev['register_quantum_per_warp'];w=dev['warp_size']
        expect=((n*w+q-1)//q)*q*((t+w-1)//w)
        assert row['allocated_registers_block']==expect;checks+=1
        indexed[row['shape'],n,t]=row
        if t in [64,128,256]:
            variant='baseline' if n==38 else 'candidate';observed=dict(historical['details'][row['shape']][variant]['occupancy_by_threads'])[t]
            assert row['active_blocks_sm']==observed,(row,observed)
            matches+=1;checks+=1
    for shape in shapes:
        for t in range(1,1025):
            b=dict(indexed[shape,38,t]);c=dict(indexed[shape,40,t]);b.pop('nominal_registers');c.pop('nominal_registers')
            assert b==c,(shape,t,b,c);checks+=1
    assert matches==60
    sample=[{'threads':t,'allocated_registers_block':indexed[shapes[0],38,t]['allocated_registers_block'],'nominal_counts':[38,40]} for t in [64,128,256]]
    report={'id':P['id'],'at':old.now(),'status':'pass_same_allocation_quantum_and_driver_occupancy','protocol_sha256':sys.argv[1],'device':dev,'sdk_allocation_rows':len(rows),'independent_formula_and_pair_checks':checks,'retained_driver_matches':matches,'all1024thread_counts_all10shapes_pairwise_equal':True,'rounded_register_samples':sample,'raw_stdout_sha256':old.sha(E/'probe.stdout.log'),'binary_sha256':binary,'sdk_header_sha256':P['sdk_header_sha256'],'e057_original_decision_unchanged':True,'historical_outcomes_unchanged':True,'source_activated':False,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'limits':'Allocated registers/shared and limiting factors are outputs of NVIDIA12.9.79 CPU occupancy code using live queried compute12.0 properties, not hardware allocation counters. Model occupancies independently match60 retained driver queries. No speed, numerical, global/host-memory or broad no-tradeoff qualification.'}
    old.save(H/'report.json',report);old.save(E/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True});verify()
print(json.dumps({k:report[k] for k in ['status','sdk_allocation_rows','independent_formula_and_pair_checks','retained_driver_matches','rounded_register_samples']}),flush=True)
