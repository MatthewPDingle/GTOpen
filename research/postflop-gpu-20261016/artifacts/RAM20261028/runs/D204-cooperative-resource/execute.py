import sys,shutil,json,re
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')})
 h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('D204_RESOURCE ',1)[1]) for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'D204_RESOURCE ' in x]
assert [x['stage'] for x in markers]==['compiled','resources','compiled','complete'];r=markers[1];gates={'positive_resident_grid':r['resident_blocks_per_SM']>0 and r['max_cooperative_grid_blocks']>=170,'fixed128threads_supported':r['max_threads']>=128,'no_local_spill':r['local_bytes_per_thread']==0,'fits_default_shared':r['static_shared_bytes']<=r['device_shared_limit'],'no_default_stack_growth':r['context_stack_after']<=r['context_stack_before']}
for arch in ['compute_120','compute_75']:
 text=(O/('primitive-'+arch+'.ptx')).read_text();names=re.findall(r'\.visible\s+\.entry\s+(\w+)\(',text);gates[arch+':single_original_primitive_entry']=names==['d204_grid_order'];header=text[text.index('.visible .entry'):text.index('{',text.index('.visible .entry'))];gates[arch+':six_parameter_ABI']=header.count('.param ')==6
passed=all(gates.values());h.save(H/'report.json',{'id':'D204','at':h.now(),'status':'pass_compiled_cooperative_primitive_resources' if passed else 'closed_cooperative_primitive_resource_failure','protocol_sha256':sys.argv[1],'gates':gates,'resources':r,'PTX_sha256':{a:h.sha(O/('primitive-'+a+'.ptx')) for a in ['compute_120','compute_75']},'all_owned_compiler_native_children_terminal':True,'application_kernels':0,'solver_or_speed_samples':0,'new_gain_accepted':False,'scope':'Vendorheader/accepted12.9NVRTC actual120 andcompat75 primitivecompile andactual120module/resources only. No primitivebarrier execution,graph capture,equivalence,CFRprototypeorperformanceadmitted. Rawcrossblockvisibility/guards/capture/replaycontrols mandatorybeforeoptimizerdesign.'});h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'application_kernels':0});verify();print(json.dumps({'status':'pass' if passed else 'closed','gates':gates,'resources':r}),flush=True)
