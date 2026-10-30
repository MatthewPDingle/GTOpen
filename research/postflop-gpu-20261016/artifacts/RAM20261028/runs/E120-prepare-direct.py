import ast,copy,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>96*1024**3
A=ROOT/'runs/E118-kernel-control';S=ROOT/'runs/E120-source';RES=ROOT/'runs/E120-resource';N=ROOT/'runs/D294-sparse-card-native';H=ROOT/'runs/E120-kernel-control';q=h.read(RES/'report.json')
assert all(q['gates'].values())and h.read(N/'report.json')['status']=='pass_scoped_sparse_card_native_guard_compaction_fallback_and_join_witness';assert h.read(ROOT/'runs/D293-sparse-card-PTX/report.json')['status']=='pass_scoped_sparse_card_PTX_guard_compaction_endpoint_and_barrier_witness'
H.mkdir(exist_ok=False)
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
for arm in ['baseline','candidate']:
 p=RES/('baseline-compute_120.ptx'if arm=='baseline'else'execution/candidate-compute_120.ptx');h.pin(p,q['PTX_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
shutil.copyfile(A/'accepted-evaluator.rs',H/'accepted-evaluator.rs');old=h.read(A/'corpus.json');c=copy.deepcopy(old);assert len(c['cases'])==2428 and len(c['geometries'])==244
profiles=['alternating_zero','runs17','isolated_positive','last_positive','zero_subnormal_cycle','zero_bound_cycle','negative_zero_fallback','negative_finite_fallback','inf_fallback','qnan_fallback','snan_fallback','above_bound_fallback','unlisted_above_bound_fallback']
basegs=[g for g in old['geometries'][:36]if g['target_m']in[0,1,257,1081]];assert len(basegs)==16;provenance=[]
for g in basegs:
 template=next(x for x in old['cases']if x['geometry']==g['id']and x['profile']=='seeded_ordinary'and x['count']==2);nh=g['nh_o'];rows=sorted({g['arrays']['rsrc_o'][node]for node in[2,5]});ob=g['arrays']['o_off'][1];mo=g['arrays']['o_cnt'][1];listed=set(g['arrays']['o_idx'][ob:ob+mo]);unlisted=next(i for i in range(nh)if i not in listed)
 for profile in profiles:
  nc=copy.deepcopy(template);nc.update(id=g['id']+'-sparse-card-'+profile,profile='stress_sparse_card_'+profile,payout_test=True,sparse_card_test=True)
  for row in rows:
   start=row*nh
   if profile=='alternating_zero':data=[0 if i%2==0 else 0x3f800000 for i in range(nh)]
   elif profile=='runs17':data=[0 if(i//17)%2==0 else 0x3f800000 for i in range(nh)]
   elif profile=='isolated_positive':data=[0x3f800000 if i%17==0 else 0 for i in range(nh)]
   elif profile=='last_positive':data=[0]*(nh-1)+[0x3f800000]
   elif profile=='zero_subnormal_cycle':data=[[0,1,0,2,0,0x007fffff,0,0x00800000][i%8]for i in range(nh)]
   elif profile=='zero_bound_cycle':data=[[0,0x67800000,0,0x677fffff][i%4]for i in range(nh)]
   else:
    data=[0 if i%2==0 else 0x3f800000 for i in range(nh)];bits={'negative_zero_fallback':0x80000000,'negative_finite_fallback':0xbf800000,'inf_fallback':0x7f800000,'qnan_fallback':0x7fc12345,'snan_fallback':0x7f812345,'above_bound_fallback':0x67800001,'unlisted_above_bound_fallback':0x67800001}[profile];data[unlisted if profile=='unlisted_above_bound_fallback'else 0]=bits
   assert len(data)==nh;nc['reach_o_bits'][start:start+nh]=data
  c['cases'].append(nc);provenance.append({'case':nc['id'],'geometry':g['id'],'profile':profile,'source_rows':rows,'unlisted_index':unlisted})
assert c['cases'][:2428]==old['cases']and c['geometries']==old['geometries'];assert len(c['cases'])==2636 and len({x['id']for x in c['cases']})==2636
c.update(id='E120-full-showdown-sparse-card-lists',sparse_card_case_provenance=provenance);h.save(H/'corpus.json',c)
gs={g['id']:g for g in c['geometries']};pairs=len(c['cases'])*5;launches=pairs*2;active=5*sum(2*gs[x['geometry']]['nh_p']if x['count']else 0 for x in c['cases']);guards=5*sum(2*(len(gs[x['geometry']]['output_initial'])-(2*gs[x['geometry']]['nh_p']if x['count']else 0))for x in c['cases'])
parent=h.read(A/'protocol.json');probe=(A/'probe.rs').read_text().replace('E118','E120').replace('bounded zero-tie prefix bypass','stable positivezero card-list compaction')
for oldv,newv in [('cs.len(),2428','cs.len(),2636'),('"comparison_pairs":12140',f'"comparison_pairs":{pairs}'),('launches,24280',f'launches,{launches}'),('active_words,6974120',f'active_words,{active}'),('guard_checks,57976920',f'guard_checks,{guards}'),('input_checks,509880',f'input_checks,{pairs*42}')]:assert oldv in probe,oldv;probe=probe.replace(oldv,newv)
(H/'probe.rs').write_bytes(probe.encode())
for name in ['execute.py','audit.py']:
 code=(A/name).read_text().replace('E118','E120').replace('12143',str(pairs+3)).replace('12140',str(pairs)).replace('24280',str(launches)).replace('pass_scoped_full_zero_tie_raw_equivalence','pass_scoped_full_sparse_card_raw_equivalence');ast.parse(code);(H/name).write_bytes(code.encode())
wrapper=ROOT/'runs/E120-run-direct.py';assert not wrapper.exists()
code='''import sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E120-kernel-control';h.pin(H/'protocol.json',sys.argv[1]);O=ROOT/'runs/E120-direct-audit';O.mkdir(exist_ok=False)
h.child([sys.executable,str(H/'execute.py'),sys.argv[1]],O,'capture',1200);h.custody()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());h.child([sys.executable,str(H/'audit.py')],O,'reader',1200);h.custody()
Q=ROOT/'comparisons/E120-kernel-control-root-check/report.json';q=h.read(Q);assert q['inventory']['comparison_pairs']==13180 and q['kernel_launches']==26360
dst=h.ar.DASHBOARD/'evidence'/Q.parent.name/Q.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(Q,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+Q.parent.name+'/'+Q.name,timeout=20)as z:assert z.read()==Q.read_bytes()
h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'protocol_sha256':sys.argv[1],'report_sha256':h.sha(Q),'new_speed_samples':0,'candidate_adopted':False});h.custody();print(q['status'],q['inventory'],flush=True)
''';ast.parse(code);wrapper.write_bytes(code.encode())
cmd=[x.replace(str(A),str(H))for x in parent['rustc_command']];files=[Path(__file__),wrapper,RES/'report.json',N/'report.json',ROOT/'runs/D293-sparse-card-PTX/report.json',ROOT/'epoch/common.py']+[p for p in H.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]+[A/n for n in ['probe.rs','execute.py','audit.py','corpus.json','protocol.json']]
h.save(H/'protocol.json',{'id':'E120-kernel-control','at':h.now(),'status':'FROZEN_PRE_FIRST_APPLICATION_KERNEL','rustc_command':cmd,'input_sha256':{str(p):h.sha(p)for p in files},'resource_report':str(RES/'report.json'),'native_mechanism_report':str(N/'report.json'),'widths':[1,32,64,128,256],'base_cases':2636,'geometries':244,'original_cases_retained_exact':2428,'sparse_card_profiles':profiles,'extra_sparse_card_cases':208,'expected_pairs':pairs,'expected_application_launches':launches,'expected_active_words':active,'expected_guard_word_checks':guards,'sealed_PTX_sha256':{a:h.sha(H/(a+'.ptx'))for a in ['baseline','candidate']},'scope':'Entire E1182428case matrix retained byteexact prefix, including original764cases/rankoracles/2roundingwitnesses. Add208positivezero/sparse/17runs/subnormal/exactbound/negativezero/negative/inf/qnan/snan/abovebound/unlistedfallbackcases across16originalphysicalgeometries. Allfivewidths/21actualinputbuffers/wholephysicaloutput/guards. No source/NVRTC/solver/timing; no filters/omittedrawfields/tolerances. Anygenuinefailureclosesonefixed E120form without source/guard/bound/width/architecture/helper/flags/quality/sample rescue. Fullrawcanonical/engine/broad/material/fresh16/holdout/currentRAMcumulative/app beforeadoption.','admission_free_bytes':shutil.disk_usage(ROOT).free,'raw_output_cap_bytes':8*1024**3,'peak_reservation_bytes':32*1024**3,'minimum_free_bytes':64*1024**3,'candidate_adopted':False,'performance_measurement':False})
for p in [ROOT/'runs/D293-sparse-card-PTX/report.json',N/'report.json',H/'protocol.json']:
 key=p.parent.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E120');e.update(stage='Frozen full raw showdown controls',correctness='Scoped compiled resources/PTX/native mechanism checks passed',reason='13,180 pairs/26,360 launches; complete original matrix plus 208 sparse/fallback cases, all outputs/inputs/guards. Register38to40/shared+208B warnings retained; broad/speed/material adoption gates remain.');e['evidence'] +=[{'label':p.parent.name,'url':'evidence/'+p.parent.name+'/'+p.name}for p in [ROOT/'runs/D293-sparse-card-PTX/report.json',N/'report.json',H/'protocol.json']];s.update(updated_at=h.now(),stage=e['stage'],activity=e['reason']);h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'pairs':pairs,'launches':launches,'active_words':active,'guard_words':guards}),flush=True)
