"""Freeze real-type CPU-only Cargo observer and original input projections."""
import array,ast,importlib.util,json,shutil,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/E127-host-control';H.mkdir(exist_ok=False)
P=h.read(ROOT/'runs/D313-action-star-ownership/protocol.json');schema=[v[0]for v in h.read(P['schema_path'])['fields']]
spec=importlib.util.spec_from_file_location('d314io',P['IO_path']);io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
S=ROOT/'runs/E127-host-source';M=h.read(S/'manifest.json');inputs=[]
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    for c in P['cases']:
        for name in['plan','kinds','gpu']:h.pin(c[name],c[name+'_sha256'])
        raw=io.plans(c['plan'],schema);gpu=io.gpu_metadata(c['gpu']);kind=Path(c['kinds']).read_bytes()
        fields={name:array.array('Q',[struct.unpack('<Q',raw[name])[0]])for name in['num_nodes','num_levels','cfv_blocks']}
        for name in['action_nodes','node_na','node_children_start','cc_child','cfv_slot']:fields[name]=io.vec(raw[name],'I')
        fields['action_spans']=array.array('I',[v for span in io.spans(raw['action_spans'])for v in span]);fields['children']=gpu['d_children'];fields['kinds']=array.array('I',(int(v)for v in kind))
        name=c['fixture']+'-'+c['constructor'];path=H/(name+'.input.bin');io.write_projection(path,fields)
        inputs.append({'fixture':c['fixture'],'constructor':c['constructor'],'path':str(path),'sha256':h.sha(path),'output':name+'.output.bin','original':c})
        print('Projected',name,flush=True)
    h.custody()
h.save(H/'cases.json',inputs)
owned={name:dict(value)for name,value in M['owned'].items()}
observer=ROOT/'runs/E127-host-control.rs';shutil.copyfile(observer,H/'observer.rs')
mod=Path(owned['crates/solver/src/gpu/mod.rs']['candidate']).read_bytes()
mod+=b'\n#[cfg(test)]\n#[path = "e127_host_control.rs"]\nmod e127_host_control;\n'
(H/'observer-mod.rs').write_bytes(mod)
owned['crates/solver/src/gpu/mod.rs']['candidate']=str(H/'observer-mod.rs');owned['crates/solver/src/gpu/mod.rs']['candidate_sha256']=h.sha(H/'observer-mod.rs')
owned['crates/solver/src/gpu/e127_host_control.rs']={'base':None,'base_sha256':None,'candidate':str(H/'observer.rs'),'candidate_sha256':h.sha(H/'observer.rs')}
files=[Path(__file__),ROOT/'runs/E127-build-host-control.py',ROOT/'runs/E127-read-host-control.py',ROOT/'epoch/common.py',S/'manifest.json',S/'design.json',ROOT/'runs/D313-action-star-ownership/protocol.json',ROOT/'runs/D313-action-star-ownership/report.json',ROOT/'runs/D313-action-star-ownership/root-report.json',ROOT/'runs/E127-native/control-report.json',observer,H/'observer.rs',H/'observer-mod.rs',H/'cases.json']
files += [Path(value[k])for value in owned.values()for k in['base','candidate']if value[k]]
files += [Path(c['path'])for c in inputs]
target=ROOT/'build-e127-host-control';assert not target.exists()
h.save(H/'protocol.json',{'id':'E127-host-control','at':h.now(),'status':'FROZEN_PRE_REAL_TYPE_COMPILER_CPU_EXECUTION',
    'owned':owned,'accepted_source_sha256':h.read(ROOT/'epoch/accepted-source.json')['source_sha256'],
    'candidate_owned_sha256':{name:value['candidate_sha256']for name,value in owned.items()},
    'tracked_owned_paths':[name for name,value in owned.items()if value['base']is not None],
    'new_owned_paths':[name for name,value in owned.items()if value['base']is None],
    'input_sha256':{str(p):h.sha(p)for p in files},'target':str(target),'required_free_bytes':80*1024**3,
    'test_name':'gpu::e127_host_control::e127_host_mapping','features':['gpu','preflop-research'],
    'scope':'Onefreshordinaryoffline/lockedfeatureCargo test compile ofexact4filehostformplustemporaryignoredCPUobserverinsideactualgpu module. No GPUconstructor/context/array/NVRTC/CFR/speedtest. RunonlyoneignoredCPUtest:actualproductionpurebuilderover6originalfullinputprojections,actualrealGpuSolver/ActionStarGpu/LevelSpanRusttypes/layoutandfixedsyntheticforeignread/nohead/chancecontrols. Thenindependentcompleteinput/outputreader. Temporaryownedfilesrestoredacceptedaftercompiler, includingremoveverifiednewmodules; executecompiledtestonly. No source/model/gate/sample rescueaftergenuinefailure.',
    'type_bounds':'GpuSolver<=4448+16;ActionStarGpu<=256;OptionBox8;LevelSpan8align4;newGPUlistlen<=originalactioncount;retainedspans2*levels withactualcapacitiesreported. Realmaterial/driver/capacity costsnotinferred.',
    'failure':'Anyactualmapping/type/bindingsfailureclosesfixedhostform; mechanicallyincorrectobserver/launchercanberepairedadditivelywithoutcompletednativecase/compilerrepeats. Allrecordsretained;no applicationkerneluntilfullhostandphysicalcostcontractvalidated.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E127')
    row.update(at=h.now(),stage='Full host source frozen; actual planner and type checks next',correctness='source_resource_control_checks_pass',reason='Native control and parameter checks passed. The staged host source preserves original plans and binds current buffers at each sweep, including continuation paths. A CPU-only build will compare the actual planner with six independent model projections and check real Rust layouts. No GPU numerical or speed result yet.')
    status.update(updated_at=h.now(),active_experiment='E127',stage=row['stage'],activity=row['reason']);h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'cases':len(inputs),'input_bytes':sum(Path(c['path']).stat().st_size for c in inputs)}),flush=True)
