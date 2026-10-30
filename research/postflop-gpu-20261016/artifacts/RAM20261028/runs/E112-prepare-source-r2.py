import difflib,json,sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();primitive=ROOT/'comparisons/D253-constant-controls/report.json';assert h.read(primitive)['kernel_executions']==240
base={n:(h.REPO/'crates/solver/src/gpu'/n).read_bytes()for n in['kernels.cu','mod.rs','continuation_capacity.rs']};cuda=base['kernels.cu'].decode();host=base['mod.rs'].decode();capacity=base['continuation_capacity.rs'].decode();assert cuda.count('\n')==cuda.count('\r\n')and '\r\n'not in host and '\r\n'not in capacity
param='    const float* __restrict__ disc, // [pos, neg, strat] — device-resident so\r\n                                    // captured graphs stay iteration-invariant\r\n';globaldecl='extern "C" { __constant__ float gto_postflop_discounts[3] = {0.f, 0.f, 0.f}; }\r\n\r\n'
cuda_edits=[(param,'',2),('    float pos = disc[0], neg = disc[1], ds = disc[2];','    float pos = gto_postflop_discounts[0], neg = gto_postflop_discounts[1], ds = gto_postflop_discounts[2];',1),('cfv_slot, cfv, disc, nh_p, nh_max','cfv_slot, cfv, nh_p, nh_max',4),('template<int NA>\r\n__device__ __forceinline__ void up_action_impl(',globaldecl+'template<int NA>\r\n__device__ __forceinline__ void up_action_impl(',1)]
for old,new,count in cuda_edits:assert cuda.count(old)==count,(old,cuda.count(old));cuda=cuda.replace(old,new)
methods='''    // The module owns this symbol. Views borrow the module/stream and never free it.
    fn discount_symbol(&self) -> Result<cudarc::driver::CudaViewMut<'_, u8>, String> {
        let symbol = self._module.get_global("gto_postflop_discounts", &self.stream).map_err(e)?;
        if symbol.len() != self.discount_symbol_bytes || symbol.len() != 12 {
            return Err("unexpected postflop discount symbol size".into());
        }
        Ok(symbol)
    }

    fn upload_discounts(&self, values: [f32; 3]) -> Result<(), String> {
        let mut bytes = self.discount_symbol()?;
        // Exactly three f32 words, size checked above; the temporary typed view
        // cannot outlive the module borrow. Same-stream ordering precedes grids.
        let mut typed = unsafe { bytes.transmute_mut::<f32>(3).unwrap() };
        self.stream.memcpy_htod(&values, &mut typed).map_err(e)
    }

'''
query='''        let discount_symbol_bytes = {
            let symbol = module.get_global("gto_postflop_discounts", &stream).map_err(e)?;
            if symbol.len() != 12 { return Err("unexpected postflop discount symbol size".into()); }
            symbol.len()
        };
'''
host_edits=[('    d_disc: CudaSlice<f32>,','    discount_symbol_bytes: usize,',1),('        let func = |name: &str| module.load_function(name).map_err(e);','        let func = |name: &str| module.load_function(name).map_err(e);\n'+query,1),('            d_disc: stream.alloc_zeros::<f32>(3).map_err(e)?,','            discount_symbol_bytes,',1),('        self.stream.memcpy_htod(&[disc.pos, disc.neg, disc.strat], &mut self.d_disc).map_err(e)?;','        self.upload_discounts([disc.pos, disc.neg, disc.strat])?;',1),('        self.stream\n            .memcpy_htod(&[disc.pos, disc.neg, disc.strat], &mut self.d_disc)\n            .map_err(e)?;','        self.upload_discounts([disc.pos, disc.neg, disc.strat])?;',2),('                        .arg(&self.d_disc)\n','',1),('        gpu.stream.memcpy_htod(&[d.pos, d.neg, d.strat], &mut gpu.d_disc).unwrap();','        gpu.upload_discounts([d.pos, d.neg, d.strat]).unwrap();',1),('    pub fn new(solver: &Solver) -> Result<GpuSolver, String> {',methods+'    pub fn new(solver: &Solver) -> Result<GpuSolver, String> {',1),('// into CUDA graphs. Kernels read discounts from d_disc, so the','// into CUDA graphs. Kernels read the module discount symbol, so the',1)]
for old,new,count in host_edits:assert host.count(old)==count,(old,host.count(old));host=host.replace(old,new)
capacity_edits=[('        d_cfv_slot:u32,d_eval_roots:f32,d_disc:f32);','        d_cfv_slot:u32,d_eval_roots:f32);',1),('    n\n}\n\npub fn stored_capacity_plan','    n + g.discount_symbol_bytes as u64\n}\n\npub fn stored_capacity_plan',1),('/// Actual CUDA slice payloads, excluding the seven borrowed mutable buffers.','/// Actual CUDA slices plus queried module discount bytes, excluding seven borrowed buffers.',1)]
for old,new,count in capacity_edits:assert capacity.count(old)==count,(old,capacity.count(old));capacity=capacity.replace(old,new)
changes={'kernels.cu':(cuda,cuda_edits),'mod.rs':(host,host_edits),'continuation_capacity.rs':(capacity,capacity_edits)}
for name,(text,edits)in changes.items():
 back=text
 for old,new,count in reversed(edits):
  if not new:
   # Exact insertion anchors for the only two deletion forms.
   if name=='kernels.cu':
    for marker in ['void up_action_impl(','void up_action(']:
     begin=back.index(marker);end=back.index('{',begin);header=back[begin:end];needle='    int nh_p, int nh_max)';assert header.count(needle)==1;back=back[:begin]+header.replace(needle,old+needle,1)+back[end:]
   elif name=='mod.rs':
    begin=back.index('.launch_builder(&self.f_up_action)');end=back.index('.map_err(e)?;',begin);launch=back[begin:end];needle='                        .arg(&nh_p)\n                        .arg(&nh_max)\n                        .launch(Self::cfg(sp.count, 0))';assert launch.count(needle)==1;back=back[:begin]+launch.replace(needle,old+needle,1)+back[end:]
   else:raise AssertionError(name)
  else:assert back.count(new)==count,(name,new,back.count(new));back=back.replace(new,old)
 assert back.encode()==base[name],name
S=ROOT/'runs/E112-source';S.mkdir(exist_ok=False);owned={}
for name,(text,edits)in changes.items():
 old=base[name];new=text.encode();(S/('baseline-'+name)).write_bytes(old);(S/('candidate-'+name)).write_bytes(new);(S/(name+'.patch')).write_bytes(''.join(difflib.unified_diff(old.decode().splitlines(True),text.splitlines(True),fromfile='E080/'+name,tofile='E112/'+name)).encode());owned['crates/solver/src/gpu/'+name]={'base':str(S/('baseline-'+name)),'candidate':str(S/('candidate-'+name)),'base_sha256':h.sha(S/('baseline-'+name)),'candidate_sha256':h.sha(S/('candidate-'+name))}
h.save(S/'manifest.json',{'id':'E112','at':h.now(),'status':'FROZEN_OFF_TREE_NOT_ACTIVATED','owned':owned,'accepted_source_sha256':h.custody(),'candidate_owned_sha256':{n:v['candidate_sha256']for n,v in owned.items()},'tracked_owned_paths':list(owned),'new_owned_paths':[],'byte_exact_reverse':True,'original_line_endings_preserved':True})
h.save(S/'source-review.json',{'id':'E112','at':h.now(),'D253_report_sha256':h.sha(primitive),'replacements':{n:[{'old':a,'new':b,'count':c}for a,b,c in e]for n,(_,e)in changes.items()},'mechanism':'Replace the single12byte global discount slice by the single12byte explicitly initialized module constant symbol. Three originalpos/neg/strategy loads keep their original placement and exact arithmetic expressions/order. Existing128thread dispatch/arity/loop/reduction/locks/sigma/actionworklists/quality stay unchanged. Remove only discountpointer formal/argument from private up_action ABI20to19; allother8global kernels/ABIs exact. No E055conditional orE075ldu mechanism composed.','host_and_lifetime':'CudaModule/stream remain owned. Every update uses size-checked borrowed byteview and ephemeral typed f32view, no owning upgrade/free. Constructor queries actual symbol12bytes; only its size is retained for observed metadata. Same-stream HtoD copies complete/order before original eager/graph work; no same-symbol concurrent writer/reader introduced. D253 proves finite independent module isolation and changing graph values only; full solver/owner/error/paging controls remain.','payload_accounting':'Existing estimated12discountbytes unchanged; actual observed metadata replaces slice length by actual queried symbol size12, counted once. No second persistent buffer or new scratch. Driver module/constant rounding/allocation/responsiveness costs are not captured by logical payload and require actual material/capacity qualification.','prospective_costs':['Extra module-symbol query per original update and one constructor query; all runtime costs included.','Modified constant access/cache path and module allocation/JIT/code costs.','Wrapper shrinks after removing CudaSlice; actual compiled size/alignment and all capacity/graph owners must be checked.','New symbol query errors propagate; unsupporteddevices and CUDA75compile compatibility must remain qualified.'],'gates':'Both120/75ABI20to19exact ordinal mapping,8otherentrybodies/resources exact,actual3constantloadsboundtooriginalpos/neg/stratoperands,no newlocal/dynamic/stack/maxthread loss/defaultfit. Positive original64/128/256occupancies. Then full rawdirect/engine/canonical/ordinary/1%strictfixture/fresh16/broad/material/holdout/cumulative/app before adoption.','failure':'Genuine mechanism/ABI/resource/numerical/state/lifecycle/capacity/material/performance failure closes fixedconstantform withoutsource/helper/width/loop/placement/flags/threshold/entrysubset/quality/sample rescue. Mechanical reader/binding/preparation defects additive, no completed scientifickernels repeated.'})
for name in ['manifest.json','source-review.json']:
 p=S/name;dst=h.ar.DASHBOARD/'evidence'/S.name/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+S.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);assert not any(x['id']=='E112'for x in s['experiments']);s['experiments'].append({'id':'E112','title':'Module constant discounts for action updates','kind':'optimization','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Frozen off-tree source; compiler controls pending','reason':'Replace12globaldiscountbytes with12moduleconstantbytes. Same float operations/order; privateABI20to19,observed payload counted once. Actual resource/host/accuracy/material/speed gates remain.','evidence':[{'label':n,'url':'evidence/'+S.name+'/'+n}for n in ['manifest.json','source-review.json']]});s.update(updated_at=h.now(),active_experiment='E112',stage='Constant discount source prototype',activity='Standalone symbol/graph bit transport passed. Fixed solver source frozen off-tree; no poker candidate kernel or speed measurement. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(S/'manifest.json'),flush=True)
