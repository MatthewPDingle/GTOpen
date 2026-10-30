"""Freeze one structural selection rule before reading any new ownership-model outcomes."""
import ast,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/D313-action-star-ownership';H.mkdir(exist_ok=False)
prior=ROOT/'comparisons/D272-metadata-canonical-v2/report.json';R=h.read(prior)
assert R['status']=='pass_scoped_full_canonical_all_device_and_CPU_raw_lifecycle'
base=ROOT/'runs/D272-metadata-canonical-v2';old=h.read(base/'protocol.json');cases=[]
for fixture in['rainbow','two-tone','river']:
    for constructor in['initial','resumed']:
        prefix=base/'baseline-output'/(fixture+'-'+constructor+'.map')
        plan=prefix.with_suffix('.map.plan.bin');kinds=prefix.with_suffix('.map.kinds.bin')
        gpu=base/'baseline-output'/(fixture+('-converged'if constructor=='initial'else'-resumed')+'.gpu.bin')
        identity=R['whole_compared_raw_file_sha256'][str(gpu)];assert gpu.stat().st_size==identity['bytes']
        cases.append({'fixture':fixture,'constructor':constructor,'plan':str(plan),'plan_sha256':h.sha(plan),'kinds':str(kinds),'kinds_sha256':h.sha(kinds),'gpu':str(gpu),'gpu_bytes':identity['bytes'],'gpu_sha256':identity['sha256']})
reader=ROOT/'runs/D313-model-action-stars.py';ast.parse(reader.read_text(encoding='utf-8'))
inputs=[Path(__file__),reader,ROOT/'epoch/common.py',ROOT/'runs/D267b-model-io.py',prior,base/'protocol.json',base/'source-review.json',Path(old['schema_path']),h.REPO/'crates/solver/src/gpu/plan.rs',h.REPO/'crates/solver/src/gpu/mod.rs',h.REPO/'crates/solver/src/gpu/kernels.cu']
h.save(H/'protocol.json',{'id':'D313','at':h.now(),'status':'FROZEN_PRE_FIRST_OWNERSHIP_MODEL_OUTCOME',
    'input_sha256':{str(p):h.sha(p)for p in inputs},'cases':cases,'schema_path':old['schema_path'],'IO_path':str(ROOT/'runs/D267b-model-io.py'),
    'selection':'Onlyactiveactionparentwith>=1actionchild,nochancechild;allactionchildrenatnextoriginalleveluniquelyactionparent-ownedandnotchance-orbitreferenced. OriginalCFVmappingfixed:parentoutputrowmusthavenoexistingnext-levelactionreadersoutsideitsownstar. Allothersoriginalfallback. Amongeligibleheads choosemaximaldisjointstarsdeepestparentlevelfirstthenascendingoriginalnodeID; no threshold/shape/fixture/parity/order tuning.',
    'schedule':'Originaldown/eval/terminal/chancepathsunchangedconceptually. Atchildleveloriginalactionstage, selectedheadCTA executesallitsactionchildreninoriginalactionindexorderwithsame128threadhelperoperations, thenCTAbarrier, thenoriginalparenthelper. Unselectedactionsremainoriginalphase. Eachselectedparentremovedfromoldphase/childrenremovedfromoldCTAworklist; everyoriginalnodeupdatedonce. No extra FPoperations removed/reassociated. GlobalCFVbuffer/mapping/payloadunchanged.',
    'safety_model':'Original2parityscratchallowsparentoutputaliasgrandchildrow. Rejectanystarwhereforeignalready-scheduledactionCTAreadsparentoutputrow. SameCTAreadscompletebeforewrite. Parentreadsofimmediatechildrowsoppositeparity;terminalsuniquecached. Disjointstars/oneupdatepernode,originalsame-levelwritesdistinct,lastwriterforeachphysicalCFVslotunchangedrequired. ThisfiniteintegergraphmodelisnotanactualGPUmemoryvisibility/numericalproof.',
    'distinct_from_closed':'E078fusesfoldterminalproducerandchangedsharedscratch; E104persistentallphasegridbarriers; E076changesCFVlifetimeallocator. Newaction-onlytwo-levelstarsretainoriginalCFVmap/no extra shared/dataarrays/mathchange. No closedhunk/kernel/helper composed. Boundedhistoryaudit andformalactualsourceproofstillrequiredbeforeanyE127candidate.',
    'reserved_output_bytes':64*1024**2,'required_free_bytes':64*1024**3,'maximum_reader_seconds':1200,
    'scope':'Read6previousacceptedCPUplans/kindsandwholeSHA-verifiedcorrespondingGPUframes(onlychildren/locksparsed). No newcompiler/nativeGPU/appkernel/CFR/solver/speed orcandidate source. Projectionretainseveryselectedhead/child/remainingIDandphase. Structuralcountsarenotfullcyclesaving/headroom/no-tradeoffproof.',
    'prospective_later_costs':'Anyimplementationmustfreezeallnewhostworklist/schedule/handle/payload/lifetimecostsandcapacitybeforefirstappkernel. Actualresource/local/stack/maxthread/defaultlimitsgate; fullraw/CPUengine/canonical/ordinary/fixed3pairs1%strictfixture/fresh16/broad/material/capacity/holdout/freshoriginal/app beforeadoption. No source/scope/layout/helper/phase/sample rescue after genuinefailure.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D313'for x in status['experiments'])
    status['experiments'].append({'id':'D313','at':h.now(),'title':'Action-node fusion: ownership and memory model','kind':'diagnostic','status':'running','accepted':False,'stage':'Frozen read-only scheduling and alias checks','correctness':'not_yet_checked','reason':'Check whether a block can compute action children and their parent without overwriting another block’s live CFV input. Keep the original scratch layout. No kernel candidate or speed claim.','evidence':[]})
    status.update(updated_at=h.now(),active_experiment='D313',stage='Action-node fusion: checking original scratch ownership',activity='Read-only model over six retained accepted plans. A foreign-reader hazard rejects a group; surviving work counts do not establish a speedup.')
    h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'cases':len(cases),'full_GPU_bytes_to_verify':sum(x['gpu_bytes']for x in cases)}),flush=True)
