"""Freeze complete retained showdown controls plus the zero-tie boundary matrix."""
import ast,copy,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>96*1024**3
A=ROOT/'runs/E107-kernel-control';S=ROOT/'runs/E118-source';RES=ROOT/'runs/E118-resource';N=ROOT/'runs/D283-zero-tie-native';H=ROOT/'runs/E118-kernel-control'
q=h.read(RES/'report.json');assert all(q['gates'].values())and h.read(N/'report.json')['status']=='pass_scoped_native_zero_tie_prefix_bypass_and_payout_chain'
assert not H.exists();H.mkdir()
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
for arm in ['baseline','candidate']:
 p=RES/('baseline-compute_120.ptx'if arm=='baseline'else'execution/candidate-compute_120.ptx');h.pin(p,q['PTX_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
shutil.copyfile(A/'accepted-evaluator.rs',H/'accepted-evaluator.rs')
old=h.read(A/'corpus.json');c=copy.deepcopy(old);assert len(old['geometries'])==116 and len(old['cases'])==764
patterns={'unit_positive_zero':[0x3f800000,0xbf800000,0],'unit_negative_zero':[0x3f800000,0xbf800000,0x80000000],'negative_zero_prefix':[0x80000000,0x80000000,0],'positive_zero_prefix':[0,0,0x80000000],'overflow_prefix':[0x7f7fffff,0xff7fffff,0],'subnormal_prefix':[1,0x80000001,0],'nonfinite_payout_guard':[0x7fc12345,0xbf800000,0],'nonzero_tie_guard':[0x3f800000,0xbf800000,1]}
profiles=['ordinary','all_zero','bound_below','bound_exact','bound_above','subnormal_cycle','negative_zero_mixed','negative_finite_mixed','positive_inf_mixed','quiet_nan_mixed','signaling_nan_mixed','unlisted_bound_above']
provenance=[]
basegs=[g for g in old['geometries'][:36]if g['target_m']in[0,1,257,1081]];assert len(basegs)==16
for g in basegs:
 original=next(x for x in old['cases']if x['geometry']==g['id']and x['profile']=='seeded_ordinary'and x['count']==2)
 for name,triplet in patterns.items():
  ng=copy.deepcopy(g);ng['id']=g['id']+'-zero-tie-'+name
  other=[triplet[1],triplet[0],triplet[2]^0x80000000]
  for i,key in enumerate(['node_twin','node_tlose','node_ttie']):ng['arrays'][key][2]=triplet[i];ng['arrays'][key][5]=other[i]
  c['geometries'].append(ng)
  selected_rows=sorted({ng['arrays']['rsrc_o'][node]for node in[2,5]});nh=ng['nh_o'];slot=1;ob=ng['arrays']['o_off'][slot];mo=ng['arrays']['o_cnt'][slot]
  listed=set(ng['arrays']['o_idx'][ob:ob+mo]);unlisted=next(i for i in range(nh)if i not in listed)
  for profile in profiles:
   nc=copy.deepcopy(original);nc.update(id=ng['id']+'-'+profile,geometry=ng['id'],profile='stress_zero_tie_'+profile,payout_test=True,zero_tie_test=True)
   for row in selected_rows:
    start=row*nh;assert start+nh<len(nc['reach_o_bits'])
    if profile!='ordinary':
     fill={'all_zero':0,'bound_below':0x677fffff,'bound_exact':0x67800000,'bound_above':0x67800001}.get(profile,0x3f800000)
     nc['reach_o_bits'][start:start+nh]=[fill]*nh
    if profile=='subnormal_cycle':nc['reach_o_bits'][start:start+nh]=[[1,2,0x007fffff,0][i%4]for i in range(nh)]
    exceptional={'negative_zero_mixed':0x80000000,'negative_finite_mixed':0xbf800000,'positive_inf_mixed':0x7f800000,'quiet_nan_mixed':0x7fc12345,'signaling_nan_mixed':0x7f812345}
    if profile in exceptional:nc['reach_o_bits'][start]=exceptional[profile]
    if profile=='unlisted_bound_above':nc['reach_o_bits'][start+unlisted]=0x67800001
   c['cases'].append(nc)
  nc=copy.deepcopy(original);nc.update(id=ng['id']+'-count0',geometry=ng['id'],profile='stress_zero_tie_count0',count=0,payout_test=True,zero_tie_test=True);c['cases'].append(nc)
  provenance.append({'geometry':ng['id'],'base_geometry':g['id'],'pattern':name,'node2_triplet':triplet,'node5_triplet':other,'source_rows':selected_rows,'unlisted_opponent_index':unlisted})
assert c['geometries'][:116]==old['geometries']and c['cases'][:764]==old['cases']
assert len(c['geometries'])==244 and len(c['cases'])==2428 and len({x['id']for x in c['cases']})==2428
c.update(id='E118-full-showdown-zero-tie-boundaries',zero_tie_case_provenance=provenance);h.save(H/'corpus.json',c)
gs={g['id']:g for g in c['geometries']};pairs=len(c['cases'])*5;launches=pairs*2;active=5*sum(2*gs[x['geometry']]['nh_p']if x['count']else 0 for x in c['cases']);guards=5*sum(2*(len(gs[x['geometry']]['output_initial'])-(2*gs[x['geometry']]['nh_p']if x['count']else 0))for x in c['cases'])
probe=(A/'probe.rs').read_text(encoding='utf-8').replace('E107','E118').replace('accepted versus earlier payout-load scheduling','accepted versus bounded zero-tie prefix bypass')
replacements={'gs.len(),116':'gs.len(),244','cs.len(),764':'cs.len(),2428','"geometries":116':'"geometries":244','"comparison_pairs":3820':f'"comparison_pairs":{pairs}','launches,7640':f'launches,{launches}','active_words,2018600':f'active_words,{active}','guard_checks,16703320':f'guard_checks,{guards}','input_checks,160440':f'input_checks,{pairs*42}'}
for a,b in replacements.items():assert a in probe,a;probe=probe.replace(a,b)
(H/'probe.rs').write_bytes(probe.encode('utf-8'))
for name in ['execute.py','audit.py']:
 t=(A/name).read_text(encoding='utf-8').replace('E107','E118').replace('pass_compiled_prerequisites_numerical_pending','pass_compiled_resources_mechanism_pending').replace('pass_scoped_full_early_payout_raw_equivalence','pass_scoped_full_zero_tie_raw_equivalence')
 t=t.replace('3823',str(pairs+3)).replace('3820',str(pairs)).replace('7640',str(launches))
 ast.parse(t);(H/name).write_bytes(t.encode('utf-8'))
cmd=[x.replace(str(RES),str(H))for x in h.read(RES/'protocol.json')['rustc_command']]
files=[Path(__file__),RES/'report.json',N/'report.json',ROOT/'runs/D282-zero-tie-PTX/report.json',ROOT/'epoch/common.py']+[p for p in H.iterdir()if p.is_file()]+[p for p in (ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]+[A/n for n in ['probe.rs','execute.py','audit.py','corpus.json','protocol.json']]
h.save(H/'protocol.json',{'id':'E118-kernel-control','at':h.now(),'status':'FROZEN_PRE_FIRST_APPLICATION_KERNEL','rustc_command':cmd,'input_sha256':{str(p):h.sha(p)for p in files},'resource_report':str(RES/'report.json'),'native_mechanism_report':str(N/'report.json'),'widths':[1,32,64,128,256],'base_cases':2428,'geometries':244,'original_cases_retained_exact':764,'zero_tie_payout_patterns':patterns,'zero_tie_reach_profiles':profiles,'extra_zero_tie_cases':1664,'expected_pairs':pairs,'expected_application_launches':launches,'expected_active_words':active,'expected_guard_word_checks':guards,'sealed_PTX_sha256':{a:h.sha(H/(a+'.ptx'))for a in ['baseline','candidate']},'scope':'All original764cases retained as exact prefix;128extra physical geometries across2boards/4range extents/bothplayers/8payouts, each12reach profiles plus count0. All5widths,21complete actual device input images, whole physical output and guards. Original zero/anti-vacuity/rounding assertions retained for original764; all inputs/outputs/guards mandatory for every additionalstresscase. Original accepted evaluate7 metadata oracle. Onecompiler/one native process/one fullraw reader, no NVRTC/sourceactivation/solver/performance. Genuine failure closes E118 mechanism; no predicate, bounds, loop placement, architecture, width, payout, flag, input, quality, or sample rescue. Finite controls do not prove allIEEEinputs or runtime speed.','admission_free_bytes':shutil.disk_usage(ROOT).free,'raw_output_cap_bytes':8*1024**3,'peak_reservation_bytes':32*1024**3,'minimum_free_bytes':64*1024**3,'candidate_accepted':False,'performance_measurement':False})
files=[RES/'report.json',ROOT/'runs/D282-zero-tie-PTX/report.json',N/'report.json',H/'protocol.json'];verified=[]
for p in files:
 rel=Path(p.parent.name)/p.name;dst=h.ar.DASHBOARD/'evidence'/rel;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+rel.as_posix(),timeout=20)as z:assert z.read()==p.read_bytes()
 verified.append({'url':rel.as_posix(),'sha256':h.sha(p)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E118');e.update(stage='Frozen full showdown controls and zero-tie boundary matrix',correctness='Resource_PTX_and_native_mechanism_pass',reason='12140 fixed pairs/24280launches across5widths; original764cases retained; signedzeros/subnormals/overflow/nonfinite/unlistedreach and guardboundaries added. 38to40registers,sameworstcaseoccupancy; no numerical/speed/adoptionclaim.')
 e['evidence'] +=[{'label':p.parent.name+' '+p.name,'url':'evidence/'+p.parent.name+'/'+p.name}for p in files];s.update(updated_at=h.now(),stage='E118 fixed direct numerical controls',activity='E118PTXanddriverbypasspassed. Fullphysical-input/output matrix frozen; E080live, no newgainadopted.');h.ar.atomic_json(h.ar.STATUS,s)
h.save(H/'preparation-publication.json',{'at':h.now(),'HTTP_byte_verified':verified,'protocol_sha256':h.sha(H/'protocol.json')});h.custody();print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'pairs':pairs,'launches':launches,'active_words':active,'guards':guards}),flush=True)
