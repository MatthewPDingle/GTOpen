import collections,hashlib,json,shutil,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D179-shared-prefix-census';P=h.read(H/'protocol.json');h.pin(H/'protocol.json',sys.argv[1]);h.custody()
for p,digest in P['input_sha256'].items():h.pin(p,digest)
def fields(path):
 result={};identities={}
 with path.open('rb') as f:
  assert f.read(16)==b'D166-GPU-RAW1\0\0\0'
  while len(result)<len(P['selected_fields']):
   kind,length=struct.unpack('<II',f.read(8));assert 0<length<512;name=f.read(length).decode();words,=struct.unpack('<Q',f.read(8));assert words<=2**31 and kind in [0,2]
   if name in P['selected_fields']:
    assert name not in result;data=f.read(4 if kind==0 else words*4);assert len(data)==(4 if kind==0 else words*4)
    if kind==0:assert data==b'\0'*4;result[name]=[0]*words
    else:result[name]=[x[0] for x in struct.iter_unpack('<I',data)]
    identities[name]={'encoding':kind,'words':words,'retained_field_payload_sha256':hashlib.sha256(data).hexdigest()}
   else:f.seek(4 if kind==0 else words*4,1)
 return result,identities
cache={}
def demand(n):
 if n in cache:return cache[n]
 chunk=(n+127)//128;old=new=ideal=0
 for j in range(chunk):
  for warp in range(4):
   logical=[t*chunk+j for t in range(warp*32,(warp+1)*32) if t*chunk+j<n]
   if not logical:continue
   a=collections.Counter(k%32 for k in logical);b=collections.Counter((k+(k>>5))%32 for k in logical);old+=max(a.values());new+=max(b.values());ideal+=1
 out={'opponent_count':n,'chunk':chunk,'baseline_bank_phases':old,'padded_bank_phases':new,'active_warp_steps':ideal};cache[n]=out;return out
rows=[];hashes={};base_total=cand_total=weightedCTAs=0
for item in P['input_frames']:
 path=Path(item['path']);assert path.stat().st_size==item['wholeframe_identity_from_prior_full_reader']['bytes'];a,identity=fields(path);hashes[item['fixture']]=identity;slots=a['d_node_river_slot'];show=a['d_show_nodes'];nh=a['hands'];assert len(nh)==2 and all(0<x<=1326 for x in nh)
 for player in [0,1]:
  counts=a['d_riv_cnt['+str(1-player)+']'];assert len(counts)>0 and all(x<=nh[1-player] for x in counts);population=collections.Counter()
  for node in show:
   assert node<len(slots);slot=slots[node];assert slot<2**31 and slot<len(counts);population[counts[slot]]+=1
  b=c=ideal=0;improved=worse=same=0
  for n,ctas in population.items():
   d=demand(n);b+=ctas*d['baseline_bank_phases'];c+=ctas*d['padded_bank_phases'];ideal+=ctas*d['active_warp_steps'];improved+=ctas*(d['padded_bank_phases']<d['baseline_bank_phases']);worse+=ctas*(d['padded_bank_phases']>d['baseline_bank_phases']);same+=ctas*(d['padded_bank_phases']==d['baseline_bank_phases'])
  assert improved+worse+same==len(show);base_total+=b;cand_total+=c;weightedCTAs+=len(show);rows.append({'fixture':item['fixture'],'traverser':player,'opponent_hands':nh[1-player],'show_CTAs':len(show),'opponent_count_population':dict(sorted(population.items())),'baseline_bank_service_phases':b,'padded_bank_service_phases':c,'ideal_active_warp_steps':ideal,'model_improved_CTAs':improved,'model_worse_CTAs':worse,'model_same_CTAs':same,'modeled_phase_reduction_pct':100*(b-c)/b if b else 0})
D=ROOT/'comparisons/D179-shared-prefix-census';D.mkdir(exist_ok=False);report={'id':'D179','at':h.now(),'status':'fixed_structural_bank_demand_census_complete','protocol_sha256':sys.argv[1],'rows':rows,'per_opponent_count_models':list(sorted(cache.values(),key=lambda x:x['opponent_count'])),'selected_field_identities':hashes,'weighted_one_sweep_CTAs_both_traversers':weightedCTAs,'total_modeled_baseline_phases':base_total,'total_modeled_padded_phases':cand_total,'modeled_phase_reduction_pct':100*(base_total-cand_total)/base_total,'actual_GPU_bank_counters_or_stalls_measured':False,'complete_cycle_headroom_established':False,'source_or_native_candidate_admitted':False,'GPU_context_or_kernel_or_timing_runs':0,'candidate_accepted':False,'scope':'Exactarithmeticforfixed32bankmodelandallregisteredone-sweepshowCTAsfromalreadyretainedactualmetadata. Modeldoesnotincludehardwareports,scheduling,compilerinstructionforms,newindexinstructions,sharedcapacityorothergathers. Not measured conflict,stall,latency,speed or1%headroom;fullsource/novelty/resource/numeric/performanceadmissionstillrequired. No sourcechanged/flags/corpus/samplevariation.'};h.save(D/'report.json',report)
dst=h.ar.DASHBOARD/'evidence'/D.name/'report.json';dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(D/'report.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+D.name+'/report.json',timeout=20) as response:assert response.read()==(D/'report.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D179');item.update(status='measured',stage='Fixed metadata bank-demand census complete; no source admission',reason='Modeledphasechange '+str(report['modeled_phase_reduction_pct'])+'% in idealizedwordbankmodel only. Not measuredGPUstall/speed/headroom. Needs source/history/compiled/capacity/numericreview beforeanycandidate.');item['evidence'].append({'label':'All metadata populations and model outcomes','url':'evidence/'+D.name+'/report.json'});s.update(updated_at=h.now(),stage='Shared scan indexing source review next',activity='D179CPUonlyfixedmodelcomplete;noGPUcounters/kernel/timing or candidate. E096rejectionpreserved,acceptedE080/16/currentRAMbaselineunchanged.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(json.dumps({'weighted_CTAs':weightedCTAs,'modeled_phase_reduction_pct':report['modeled_phase_reduction_pct'],'rows':[{k:r[k] for k in ['fixture','traverser','show_CTAs','model_improved_CTAs','model_worse_CTAs','modeled_phase_reduction_pct']} for r in rows],'headroom_or_speed_measured':False}),flush=True)
