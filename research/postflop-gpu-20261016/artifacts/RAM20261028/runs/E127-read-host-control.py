"""Independent full real-planner output/input replay against the frozen D313 model."""
import array,importlib.util,json,re,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E127-host-control';P=h.read(H/'protocol.json');O=H/'execution'
assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1])
for path,digest in P['input_sha256'].items():h.pin(path,digest)
model_root=ROOT/'runs/D313-action-star-ownership';source=h.read(model_root/'protocol.json');model=h.read(model_root/'report.json')
spec=importlib.util.spec_from_file_location('e127hostio',source['IO_path']);io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
schema=[row[0]for row in h.read(source['schema_path'])['fields']]
inventory=h.read(ROOT/'runs/D272-metadata-canonical-v2/source-review.json')['device_field_inventory']
def gpu_children(path):
    result=None
    with Path(path).open('rb')as f:
        assert f.read(16)==b'D166-GPU-RAW1\0\0\0'
        for name in['iteration','algorithm','hands']+inventory:
            kind,length=struct.unpack('<II',f.read(8));assert 0<length<512 and kind in[0,2]
            assert f.read(length).decode()==name;words=struct.unpack('<Q',f.read(8))[0]
            if kind==0:
                assert f.read(4)==b'\0'*4
                if name=='d_children':result=np.zeros(words,dtype=np.uint32)
            elif name=='d_children':
                data=f.read(words*4);assert len(data)==words*4;result=np.frombuffer(data,dtype='<u4')
            else:f.seek(words*4,1)
        assert not f.read(1)
    assert result is not None
    return result
def equal(actual,want,label):assert np.array_equal(np.asarray(actual),np.asarray(want)),label
log=(O/'control.stdout.log').read_text(encoding='utf-8');types=[json.loads(line.split('E127_HOST_TYPES ',1)[1])for line in log.splitlines()if'E127_HOST_TYPES 'in line]
negative=[json.loads(line.split('E127_HOST_NEGATIVE ',1)[1])for line in log.splitlines()if'E127_HOST_NEGATIVE 'in line]
native=[json.loads(line.split('E127_HOST_CASE ',1)[1])for line in log.splitlines()if'E127_HOST_CASE 'in line]
end=[json.loads(line.split('E127_HOST_COMPLETE ',1)[1])for line in log.splitlines()if'E127_HOST_COMPLETE 'in line]
assert len(types)==len(negative)==len(end)==1 and len(native)==6 and all(negative[0].values())
assert end==[{'cases':6,'CUDA_contexts':0,'application_kernel_launches':0,'solver_or_speed_samples':0}]
assert re.search(r'test result: ok\. 1 passed; 0 failed;',log)
assert types[0]['GpuSolver_bytes']<=4464 and types[0]['ActionStarGpu_bytes']<=256 and types[0]['LevelSpan_bytes']==8 and types[0]['LevelSpan_alignment']==4 and types[0]['OptionBox_bytes']==8
cases=h.read(H/'cases.json');results=[];input_words=output_words=0
for case,truth,observed in zip(cases,model['cases'],native):
    assert(case['fixture'],case['constructor'])==(truth['fixture'],truth['constructor'])==(observed['fixture'],observed['constructor'])
    h.pin(case['path'],case['sha256']);h.pin(truth['projection'],truth['projection_sha256'])
    inputs=io.read_projection(case['path']);raw=io.plans(case['original']['plan'],schema)
    assert set(inputs)=={'num_nodes','num_levels','cfv_blocks','action_nodes','action_spans','node_na','node_children_start','children','cc_child','cfv_slot','kinds'}
    for name in['num_nodes','num_levels','cfv_blocks']:equal(inputs[name],[struct.unpack('<Q',raw[name])[0]],'originalscalar:'+name)
    for name in['action_nodes','node_na','node_children_start','cc_child','cfv_slot']:equal(inputs[name],io.vec(raw[name],'I'),'originalvector:'+name)
    equal(inputs['action_spans'],[v for span in io.spans(raw['action_spans'])for v in span],'all original action spans')
    equal(inputs['children'],gpu_children(case['original']['gpu']),'all actual original GPU child IDs')
    equal(inputs['kinds'],np.frombuffer(Path(case['original']['kinds']).read_bytes(),dtype=np.uint8),'all original node kinds')
    frozen=io.read_projection(truth['projection']);heads=np.asarray(frozen['selected_parent_ids'],dtype=np.uint32);hp=np.asarray(frozen['selected_parent_phases'],dtype=np.uint32);remaining=np.asarray(frozen['remaining_action_ids'],dtype=np.uint32);rp=np.asarray(frozen['remaining_action_phases'],dtype=np.uint32)
    expected=[];regular=[];fused=[]
    for level in range(int(inputs['num_levels'][0])):
        part=remaining[rp==level];regular.extend([len(expected),len(part)]);expected.extend(map(int,part))
        part=np.sort(heads[hp==level]);fused.extend([len(expected),len(part)]);expected.extend(map(int,part))
    output=O/'raw'/case['output'];actual=io.read_projection(output)
    assert set(actual)=={'nodes','regular_spans','fused_spans','counts'}
    equal(actual['nodes'],expected,'every compiled planner worklist ID')
    equal(actual['regular_spans'],regular,'every compiled planner ordinary phase')
    equal(actual['fused_spans'],fused,'every compiled planner star phase')
    equal(actual['counts'],[truth['selected_disjoint_stars'],truth['selected_action_children']],'all counts')
    assert observed['nodes']==len(expected)<=truth['original_action_nodes']and observed['heads']==len(heads)and observed['children']==truth['selected_action_children']
    assert observed['nodes_capacity']==len(expected)and observed['regular_capacity']==observed['fused_capacity']==int(inputs['num_levels'][0])
    assert observed['CUDA_contexts_or_kernels']==0
    input_words+=sum(len(v)*v.itemsize//4 for v in inputs.values());output_words+=sum(len(v)*v.itemsize//4 for v in actual.values())
    results.append({'fixture':case['fixture'],'constructor':case['constructor'],'all_original_input_fields_literal_exact':True,'all_compiled_schedule_words_match_independent_model':True,
        'heads':len(heads),'children':truth['selected_action_children'],'new_worklist_words':len(expected),'new_worklist_GPU_logical_bytes':len(expected)*4,'host_span_retained_bytes':len(regular)*4+len(fused)*4,
        'input_sha256':case['sha256'],'output_sha256':h.sha(output),'output_bytes':output.stat().st_size,'all_observed_capacities':{k:observed[k]for k in['nodes_capacity','regular_capacity','fused_capacity']}})
    print('E127_HOST_READER_CASE',json.dumps(results[-1]),flush=True)
assert len(list((O/'raw').iterdir()))==6
h.save(H/'report.json',{'id':'E127-host-control','at':h.now(),'status':'pass_real_compiled_CPU_builder_all6_original_plans_and_types',
    'protocol_sha256':sys.argv[1],'actual_Rust_type_layouts':types[0],'actual_Rust_structural_controls':negative[0],'cases':results,
    'input_words_checked':input_words,'output_words_checked':output_words,'original_public_CPU_plan_and_FP_fields_not_modified':True,
    'scope':'ActualproductionplannercompiledinsiderealGPUmodule,fulloriginal11inputfieldsandcompleteoutputIDs/spans/countsmatchfrozenindependentD313model. ActualRusttypes/layoutscaptured. NoGPUconstructor/CUDAcontext/array/applicationkernels/NVRTC/CFR/numericalsolver/speed. Source/bodybindingtypechecknotactualGPUruntimeproofofhostlaunches/material/capacity/driverpeak.',
    'new_GPU_application_kernels':0,'new_solver_or_speed_samples':0,'candidate_adopted':False,'all_new_bulk_X_S_readonly_no_T':True})
print(json.dumps({'status':'pass','cases':6,'input_words':input_words,'output_words':output_words,'actual_types':types[0]}),flush=True)
