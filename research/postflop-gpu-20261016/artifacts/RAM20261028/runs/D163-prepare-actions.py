import sys,json,shutil,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
RESOURCE=ROOT/'runs/D162-private-dependency-repair';result=h.read(ROOT/'comparisons/D162-private-dependency-repair/report.json')
assert result['status']=='admit_exact_raw_numerical_controls_only' and all(result['gates'].values())
H=ROOT/'runs/D163-action-compiler-controls';H.mkdir(exist_ok=False)
shutil.copyfile(ROOT/'runs/D163-execute-actions.py',H/'execute.py');ast.parse((H/'execute.py').read_text(encoding='utf-8'))
down=ROOT/'runs/D163-down-action';up=ROOT/'runs/D163-up-action';down.mkdir(exist_ok=False);up.mkdir(exist_ok=False)
orig_down=ROOT/'runs/E091-raw-control';orig_up=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\E085-kernel-control')
relocations=[]
for path,names in [(down,['probe.rs','corpus.json']),(up,['probe.rs','corpus.json','discounts.rs'])]:
    original=orig_down if path==down else orig_up
    for name in names:
        shutil.copyfile(original/name,path/name);assert h.sha(original/name)==h.sha(path/name)
        relocations.append({'original':str(original/name),'local':str(path/name),'sha256':h.sha(path/name)})
    for arm in ['baseline','candidate']:shutil.copyfile(RESOURCE/'execution'/(arm+'.ptx'),path/(arm+'.ptx'))
# Only the old environment-variable output adapter becomes this child's path argument.
src=(up/'probe.rs').read_text(encoding='utf-8');needle='std::env::var_os("E085_KERNEL_CONTROL_DIR").expect("fresh output dir required")'
assert src.count(needle)==1;src=src.replace(needle,'std::env::args_os().nth(1).expect("fresh output dir required")',1)
(up/'probe.rs').write_bytes(src.encode())
down_audit=(ROOT/'runs/E091-raw-audit.py').read_text(encoding='utf-8')
down_audit=down_audit.replace("ROOT=Path(__file__).resolve().parent.parent","ROOT=Path(__file__).resolve().parents[2]",1).replace('E091-raw-control','D163-down-action')
(down/'audit.py').write_bytes(down_audit.encode());ast.parse(down_audit)
up_audit=(orig_up/'audit.py').read_text(encoding='utf-8');needle="sys.path.insert(0,str(HERE.parent/'accepted-E080-live-20261018'));import common_e080_live as old"
assert up_audit.count(needle)==1;up_audit=up_audit.replace(needle,"sys.path.insert(0,str(HERE.parents[1]/'epoch'));import common as old",1).replace('E085-kernel-control-root-check','D163-up-action-root-check')
(up/'audit.py').write_bytes(up_audit.encode());ast.parse(up_audit)
dc=h.read(down/'corpus.json');uc=h.read(up/'corpus.json')['cases'];assert len(dc)==1530 and len(uc)==819
deps=ROOT/'reference/accepted-e080-deps';commands={}
for label,folder in [('down',down),('up',up)]:
    cmd=['rustc',str(folder/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
    for name,file in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
    commands[label]=cmd+['-o',str(folder/'probe.exe')]
h.save(H/'source-review.json',{'at':h.now(),'id':'D163','status':'frozen_existing_full_direct_action_corpora','kernel_targets':['down_action','up_action'],'compiled_PTX_origin':'Exact sealed12.9and13.0PTX from D162,nothing recompiled or source transformed. No production integration.','corpus':'Existing original1530down and819up cases retained without filtering. Both actor/traverser orientations,asymmetric/boundary0..1326hands,NA1/2/3/4/5/8/9/16/17,legal1/32/64/128/256threads,locked/opponent paths,DCFR/CFR+ actual discounts/iterations,signed zeros,subnormals,infinities,overflow,NaN payloads,count0 andguard/disjoint device ownership. Native all-word comparisons plus retained direct byte/vector readers.','adapters':'Down probe and corpus exact. Up only replaces output environment-variable read by child argument; numerical statements and discounts exact. Readers change only common helper imports,root paths and new output IDs;raw format/geometry/guards/oracles unchanged. Native markers retain historical labels as file format,not extra historical observations.','relocation':relocations,'scope':'First two of9changed kernels. This is not complete compiler/engine/accuracy or performance qualification. All other kernels,actual full engine/canonical rawstate/quality/stop/save/continuation/resources and integration/runtime compiler clocks remain required. Any actual numerical mismatch closes fixed13compiler form without source/flag/version/input/sample rescue. Stop before up if down fails;do not pool with historical outputs.'})
files=[Path(__file__),ROOT/'runs/D163-execute-actions.py',ROOT/'runs/E091-raw-audit.py',orig_up/'audit.py',orig_up/'probe.rs',orig_up/'discounts.rs',RESOURCE/'protocol.json',ROOT/'comparisons/D162-private-dependency-repair/report.json',RESOURCE/'execution/complete.json']
files += [p for folder in [H,down,up] for p in folder.iterdir() if p.is_file()]+[deps/'libcudarc-ba3140064b5903a3.rlib',deps/'libserde_json-83a0670a02a34a4d.rlib']
common_inputs={str(p):h.sha(p) for p in files}
for label,folder in [('down',down),('up',up)]:
    h.save(folder/'protocol.json',{'id':'D163-'+label+'-action','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_KERNELS','cases':len(dc) if label=='down' else len(uc),'kernel_launches':2*(len(dc) if label=='down' else len(uc)),'raw_output':str(folder/'output'),'rustc_command':commands[label],'input_sha256':common_inputs,'scope':'Existing finite raw corpus,unchanged science,exact sealed compiler PTX;no solver/performance. Actual mismatch stops compiler form without rescue.'})
h.save(H/'protocol.json',{'id':'D163','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_DIRECT_GPU_KERNELS','category_order':['down','up'],'folders':{'down':str(down),'up':str(up)},'category_protocol_sha256':{x:h.sha(folder/'protocol.json') for x,folder in [('down',down),('up',up)]},'rustc_commands':commands,'input_sha256':common_inputs,'required_free_bytes':80*1024**3,'raw_reservation_bytes':12*1024**3,'expected_cases':2349,'expected_kernel_launches':4698,'scope':'Two fresh Rustcompilers/two serialized direct GPU processes and two full retained readers,down first then up only if down passes. No NVRTC repeat,source/corpus/shape/tolerance/sample rescue,engine,performance or adoption claim.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
