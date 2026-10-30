"""Freeze one stable positive-zero card-list compaction form off-tree."""
import ast,hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
D=ROOT/'runs/D292-sparse-card-scout';D.mkdir(exist_ok=False);seen={};hits=[];inventories=[]
pattern=re.compile(r'(?:card_pos_sh\s*\[\s*(?:dst|write|out|packed|nz)\w*\s*\]|(?:sparse|compact|nonzero|zero_skip)\w*card|card\w*(?:compact|nonzero|sparse))',re.I)
for folder in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'),ROOT/'runs']:
 paths=subprocess.check_output(['rg','--files',str(folder),'-g','*.cu'],text=True).splitlines();inventories.append({'root':str(folder),'CUDA_files':len(paths)})
 for name in paths:
  data=Path(name).read_bytes();digest=hashlib.sha256(data).hexdigest()
  if digest in seen:continue
  seen[digest]=name;t=data.decode('utf-8');a=t.find('extern "C" __global__ void up_show(')
  if a<0:continue
  b=t.find('extern "C" __global__',a+20);body=t[a:b if b>=0 else len(t)]
  matches=[{'line':body[:m.start()].count('\n')+1,'text':body[max(0,m.start()-100):m.end()+130]}for m in pattern.finditer(body)]
  if matches:hits.append({'path':name,'sha256':digest,'matches':matches})
revs=subprocess.check_output(['git','log','--all','--format=%H','--','crates/solver/src/gpu/kernels.cu'],cwd=h.REPO,text=True).splitlines();localhits=[]
for rev in revs:
 data=subprocess.check_output(['git','show',rev+':crates/solver/src/gpu/kernels.cu'],cwd=h.REPO);t=data.decode();a=t.find('extern "C" __global__ void up_show(')
 if a>=0:
  b=t.find('extern "C" __global__',a+20);body=t[a:b if b>=0 else len(t)]
  if pattern.search(body):localhits.append({'revision':rev,'body_matches':[m.group()for m in pattern.finditer(body)]})
assert not hits and not localhits,'Matching source needs semantic review before admission'
h.save(D/'history.json',{'at':h.now(),'inventories':inventories,'unique_CUDA_hashes':len(seen),'local_all_ref_revisions':len(revs),'retained_matches':hits,'local_matches':localhits,'regex':pattern.pattern,'limits':'Bounded literal/local scan, not exhaustive semantic or remote novelty proof. E036/E037 wholezero-row/outputshortcut,E066 sharedoffsetcache,E068 bit-selected rankaccumulation,E077 prefixdemand,E084 firstcardfloatcache and E118 zero-tie payout omission remain closed. None of those hunks composed. New mechanism stably filters positivezero opponent reach positions inside existing per-card shared list intervals; full original prefix, allownoutputs and complete three-term payout remain.'})
checks=0;records=[]
for length in range(13):
 for mask in range(1<<length):
  original=list(range(length));storage=original.copy();write=0
  for read in range(length):
   assert write<=read;pos=storage[read]
   if mask>>pos&1:storage[write]=pos;write+=1
  expected=[p for p in original if mask>>p&1];assert storage[:write]==expected;checks+=1
  for lb,ub in [(0,0),(0,length),(length,length),(length//3,2*length//3)]:
   assert [p for p in storage[:write]if p<lb]==[p for p in original if(mask>>p&1)and p<lb]
   assert [p for p in storage[:write]if p>=ub]==[p for p in original if(mask>>p&1)and p>=ub];checks+=2
for width in range(1,257):
 groups=[list(range(t,52,width))for t in range(width)];flat=[x for a in groups for x in a];assert sorted(flat)==list(range(52));records.append({'width':width,'exactly_one_writer_per_card':True})
h.save(D/'dependency-and-FP-contract.json',{'at':h.now(),'stable_compaction_integer_checks':checks,'all_masks_lengths0_through12':True,'card_writer_widths1_through256':records,'partition_invariant':'Original52disjointascendingintervals partition2*m_o physical card positions. Per-cardwriter scans ascending;write<=read means in-place stores never overwrite an unread element in any interval. Only keptoriginalpositions,originalorder,originalboundarypredicates. Endpoints are relative to unchanged card_base; no global/index payload change.','barriers':'Existingfirstbarrier becomes OR guard reduction. Originalsecondbarrier publishes complete reach_sh before per-card compaction. The existing third barrier after chunk_sum assignment joins every card-writer before any card-list consumer; same5logicalCTAbarriers, no extra barrier. Prefix arrays and per-card cache/end arrays disjoint.','FP_guard':'Allactualnh_o original-order reaches must have uintbits<=0x67800000 (+2^80), nh_o<=1326. This includes all positive finite/subnormal/+0, excludes negative/negativezero/nonfinite; OR at firstbarrier makes guardCTAuniform. Unsafe CTA retains alloriginalpositions/ends.','FP_omission_argument':'Only +0bits are removed. For eligible CTA every original tot_c/lower_c/higher_c recurrence starts +0, uses nonnegative finite terms, and has <=2*1326terms. With defaultRNandnoFTZ each partial remains nonnegative finite (<2^93 conservative bound), including positivezero; adding +0 is bit identity. Original nonzero selected subsequences remain in original order; prefix, subtractions, same/valid/tied/payout and writes remain unchanged. This is a bounded real/IEEEsource argument, not compiledNaN/payload/rounding/GPU proof. Unsafe values retain original full list and arithmetic.','required_next':'Actual emitted guard, stable shared compaction/endpointconsumer and all5barriers; complete original plus sparse/exceptional direct raw corpus. No source proof substitutes GPU results.'})
S=ROOT/'runs/E120-source';S.mkdir(exist_ok=False);original=(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();assert original.count(b'\n')==original.count(b'\r\n');text=original.decode();a=text.index('extern "C" __global__ void up_show(');b=text.index('extern "C" __global__ void up_chance(',a);body=text[a:b];edits=[]
def edit(old,new):
 global body
 old=old.replace('\n','\r\n');new=new.replace('\n','\r\n');assert body.count(old)==1;body=body.replace(old,new,1);edits.append({'old':old,'new':new})
edit('    extern __shared__ char shraw[];','''    extern __shared__ char shraw[];
#if __CUDA_ARCH__ == 1200
    __shared__ u32 kept_card_end[52];
#endif''')
edit('    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];','''#if __CUDA_ARCH__ == 1200
    int unsafe_card_reach = nh_o < 0 || nh_o > 1326;
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) {
        float r = ro_g[j];
        ro_sh[j] = r;
        unsafe_card_reach |= __float_as_uint(r) > 0x67800000u;
    }
#else
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];
#endif''')
edit('''        card_pos_sh[j] = o_card_pos[card_base + j];
    __syncthreads();''','''        card_pos_sh[j] = o_card_pos[card_base + j];
#if __CUDA_ARCH__ == 1200
    bool compact_cards = !__syncthreads_or(unsafe_card_reach);
#else
    __syncthreads();
#endif''')
edit('''    __syncthreads();
    // Blocked inclusive scan:''','''    __syncthreads();
#if __CUDA_ARCH__ == 1200
    for (int card = threadIdx.x; card < 52; card += blockDim.x) {
        u32 begin = o_card_off[(u64)slot * 53 + card] - card_base;
        u32 end = o_card_off[(u64)slot * 53 + card + 1] - card_base;
        u32 write = begin;
        if (compact_cards) {
            for (u32 read = begin; read < end; read++) {
                u32 pos = card_pos_sh[read];
                if (__float_as_uint(reach_sh[pos]) != 0u)
                    card_pos_sh[write++] = pos;
            }
        } else {
            write = end;
        }
        kept_card_end[card] = write;
    }
#endif
    // Blocked inclusive scan:''')
edit('''            u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];''','''#if __CUDA_ARCH__ == 1200
            u32 c1 = card_base + kept_card_end[cc[x]];
#else
            u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];
#endif''')
candidate=(text[:a]+body+text[b:]).encode();inverse=candidate
for e0 in reversed(edits):assert inverse.count(e0['new'].encode())==1;inverse=inverse.replace(e0['new'].encode(),e0['old'].encode(),1)
assert inverse==original;(S/'baseline.cu').write_bytes(original);(S/'candidate.cu').write_bytes(candidate)
h.save(S/'manifest.json',{'id':'E120','at':h.now(),'status':'FROZEN_OFF_TREE_PRE_COMPILER','baseline_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu'),'edits':edits,'entire_CRLF_source_inverse_exact':True,'target':'up_show only compute120 stable positivezero card-position compaction','unchanged':'Allprefixfloatingrecurrences,nonzero correction order,boundarypredicates,fullsame/valid/tied/three-term payout/allwrites. Allhost,ABI27,physicalglobalarrays/launch/block/dynamicshared/quality/stopping/saveunchanged;compute75originaltokens.','added_costs':'52u32 staticshared endpoints208B, wholeCTA integerguardOR, all52cardinterval scans and sharedrewrites each eligible CTA, fallbackendpublish eachineligibleCTA,code/JIT/register/residency risk. Same5logicalCTAbarriers;firstisOR. No material or speed guarantee.','history_and_contract_sha256':{n:h.sha(D/n)for n in ['history.json','dependency-and-FP-contract.json']},'closure':'No source/predicate/bound/cardlist/width/architecture/helper/flags/quality/sample rescue after any genuine failure.'})
h.save(D/'report.json',{'id':'D292','at':h.now(),'status':'pass_scoped_source_stable_compaction_and_bounded_FP_contract','history_sha256':h.sha(D/'history.json'),'contract_sha256':h.sha(D/'dependency-and-FP-contract.json'),'source_manifest_sha256':h.sha(S/'manifest.json'),'integer_checks':checks,'new_compiler_GPU_kernel_solver_or_speed_samples':0,'candidate_adopted':False,'limits':'Bounded source/integer/IEEEargument only; actual compiled resources/guard/boundedorderedrecurrences/fallback/physicalindices and GPUfullrawmustpass. No dynamiczero incidence/time/headroom or universal correctness claim.'})
R=ROOT/'runs/E120-resource';R.mkdir(exist_ok=False);shutil.copyfile(S/'candidate.cu',R/'candidate.cu')
for arch in ['compute_120','compute_75']:shutil.copyfile(ROOT/'runs/E118-resource'/('baseline-'+arch+'.ptx'),R/('baseline-'+arch+'.ptx'))
(R/'probe.rs').write_bytes((ROOT/'runs/E118-resource/probe.rs').read_bytes().replace(b'E118_RESOURCE',b'E120_RESOURCE'))
code=(ROOT/'runs/E118-resource-execute.py').read_text().replace('E118','E120').replace('zero-tie fastpath and FP mechanism pending','stable sparse-card mechanism pending').replace('Finite zero-tie output prefix; actual guarded absence of tot_c/same/valid/tied work and exact baseline-prefix FP provenance plus barrier/caller reviews remain','Stable card-list compaction; actual finitepositiveguard, stable shared list/endpoints, original fullprefix/payout/fallback and barrier/caller proofs remain')
ast.parse(code);script=ROOT/'runs/E120-resource-execute.py';assert not script.exists();script.write_bytes(code.encode())
parent=h.read(ROOT/'runs/E118-resource/protocol.json');cmd=[v.replace('E118-resource','E120-resource')for v in parent['rustc_command']]
files=[Path(__file__),script,ROOT/'epoch/common.py',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',h.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',ROOT/'runs/E118-resource-execute.py',ROOT/'runs/E118-resource/probe.rs']+[p for folder in[D,S,R]for p in folder.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(R/'protocol.json',{'id':'E120-resource','at':h.now(),'status':'FROZEN_PRE_ONE_COMPILER_AND_MODULE_ONLY_PROCESS','rustc_command':cmd,'GPU_uuid':parent['GPU_uuid'],'original_entries':parent['original_entries'],'target_entries':['up_show'],'required_free_bytes':16*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'resource_gates':'All9headers/8untargetedbodies/resources exact,120showbodychanged,75all9bodiesexact. Same5logicalbarriers;firstOR. No local/constant/dynamic/stackgrowth/maxthreadloss/defaultlimitloss;positive64/128/256occupancy, register/static/residency disclosed underD108.','mechanism_prerequisite':'Actualfirstcopy unsignedreachbound0x67800000/nh_o<=1326 OR at originalfirstbarrier; prefixpublished atsecond;stable within-original disjointcardinterval leftcompaction droppingonly+0;unsafefallbackoriginalend; originalthirdbarrierjoins allwriters beforeendpoint/positionconsumers; alloriginalprefix/correctionnonzeroorder/fullpayout unchanged.','prospective_test_order':'Emittedresources/mechanism ->full original E1182428case/fivewidth12140pair corpus plus any prospectively frozen targeted sparse cases ->ordinary86units ->initialfixed3paircompletecycles withallscience/EV/fingerprints/stops/checkpointsexact. Fullrawcanonical/engine/broad/material and fresh16/holdout/currentRAMcumulative/app mandatorybeforeadoption. Noacceptancegateweakened or historicalsamplepooling.','failure':'Close one fixedsource/guard/bound/list/width/architecture/helper/flags/quality/sample form on genuinefailure, no rescue variants. No main/live/sourceactivation.'})
published=[]
for folder,names in [(D,['report.json','history.json','dependency-and-FP-contract.json']),(S,['manifest.json']),(R,['protocol.json'])]:
 for name in names:
  p=folder/name;key=folder.name+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  published.append({'url':'evidence/'+key,'sha256':h.sha(p)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);assert not any(e['id']in['D292','E120']for e in s['experiments']);s['experiments'] +=[{'id':'D292','title':'Stable sparse card-list source and rounding review','kind':'diagnostic','status':'measured','accepted':False,'stage':'Source and integer dependency review passed','reason':'Omit only +0 terms under a uniform finite nonnegative reach bound; original nonzero order and full payout retained. Compiled/GPU correctness remains unproven.','evidence':[{'label':n,'url':'evidence/'+D.name+'/'+n}for n in ['report.json','history.json','dependency-and-FP-contract.json']]},{'id':'E120','title':'Stable positive-zero card-list compaction','kind':'candidate','status':'staged','accepted':False,'stage':'Frozen compiler/resource prerequisite','reason':'One CUDA-only form; compacts existing shared card-position intervals, 208B static endpoint cost, same5barriers/host/globalpayload. No GPU numerical or speed result yet.','evidence':[{'label':'Fixed source','url':'evidence/'+S.name+'/manifest.json'},{'label':'Compiled resource gates','url':'evidence/'+R.name+'/protocol.json'}]}];s.update(updated_at=h.now(),active_experiment='E120',stage='Sparse card lists: resources and emitted-code checks',activity='E119 closed. Testing a distinct stable positive-zero card-position compaction form. E080 remains live; no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
h.save(R/'preparation-publication.json',{'at':h.now(),'HTTP_byte_verified':published,'protocol_sha256':h.sha(R/'protocol.json')});h.custody();print(json.dumps({'protocol_sha256':h.sha(R/'protocol.json'),'candidate_sha256':h.sha(S/'candidate.cu'),'unique_CUDA':len(seen),'integer_checks':checks}),flush=True)
