import ast,copy,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=66*1024**3
RES=ROOT/'runs/E107-resource';S=ROOT/'runs/E107-source';N=ROOT/'runs/D221-showdown-native-scheduling';A=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\E089-kernel-control');H=ROOT/'runs/E107-kernel-control'
q=h.read(RES/'report.json');assert all(q['gates'].values())and h.read(N/'report.json')['status']=='pass_static_native_payout_placement'
assert not H.exists();H.mkdir()
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
for arm in ['baseline','candidate']:
 p=RES/('baseline-compute_120.ptx'if arm=='baseline'else'execution/candidate-compute_120.ptx');h.pin(p,q['PTX_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
for n in ['corpus.json','accepted-evaluator.rs']:shutil.copyfile(A/n,H/('original-'+n if n=='corpus.json'else n))
original=h.read(H/'original-corpus.json');corpus=copy.deepcopy(original);assert len(corpus['cases'])==364 and len(corpus['geometries'])==36
patterns={'signed_zero_a':[0,0x80000000,0],'signed_zero_b':[0x80000000,0,0x80000000],'finite_reversed':[0xbf800000,0x3f800000,0xbf000000],'finite_extremes':[0x7f7fffff,0xff7fffff,0x00800000],'subnormals':[1,0x80000001,0x007fffff],'positive_infinity':[0x7f800000,0xbf800000,0],'negative_infinity':[0x3f800000,0xff800000,0x80000000],'mixed_infinities':[0x7f800000,0xff800000,0x7f800000],'quiet_nan_payloads':[0x7fc12345,0xffc23456,0x7fc54321],'signaling_nan_payloads':[0x7f812345,0xff823456,0x7f854321]}
provenance=[]
for g in original['geometries']:
 if g['board_text']!='Ks7h2dQhTc'or g['target_m']not in [0,1,257,1081]:continue
 for name,triplet in patterns.items():
  ng=copy.deepcopy(g);ng['id']=g['id']+'-payout-'+name
  for i,key in enumerate(['node_twin','node_tlose','node_ttie']):ng['arrays'][key][2]=triplet[i];ng['arrays'][key][5]=triplet[(i+1)%3]
  corpus['geometries'].append(ng)
  for profile,count in [('seeded_ordinary',2),('all_zero',2),('stress_signed_zero',2),('stress_nan_payloads',2),('seeded_ordinary',0)]:
   # Every existing geometry has the ordinary/zero profiles. Exceptional reach
   # profiles are taken from a fixed same-nh_o geometry only when available.
   matches=[c for c in original['cases']if c['geometry']==g['id']and c['profile']==profile and c['count']==2]
   if not matches and profile.startswith('stress_'):
    matches=[c for c in original['cases']if c['profile']==profile and len(c['reach_o_bits'])==g['nh_o']and c['count']==2]
   assert len(matches)>=1,(g['id'],profile)
   c=copy.deepcopy(matches[0]);c.update(id=ng['id']+'-'+profile+'-count'+str(count),geometry=ng['id'],profile=profile,count=count,payout_test=True);corpus['cases'].append(c)
  provenance.append({'geometry':ng['id'],'base_geometry':g['id'],'pattern':name,'node2_triplet':triplet,'node5_triplet':triplet[1:]+triplet[:1]})
assert corpus['geometries'][:36]==original['geometries']and corpus['cases'][:364]==original['cases']
assert len(corpus['geometries'])==116 and len(corpus['cases'])==764
assert len(set(c['id']for c in corpus['cases']))==764
corpus.update(id='E107-full-showdown-and-payout-matrix',payout_case_provenance=provenance);h.save(H/'corpus.json',corpus)
geometries={g['id']:g for g in corpus['geometries']};active=5*sum(2*geometries[c['geometry']]['nh_p']if c['count']else 0 for c in corpus['cases']);guards=5*sum(2*(len(geometries[c['geometry']]['output_initial'])-(2*geometries[c['geometry']]['nh_p']if c['count']else 0))for c in corpus['cases'])
pairs=764*5;launches=pairs*2;probe=(A/'probe.rs').read_text(encoding='utf-8').replace('E089','E107').replace('original/shared-producer versus serial-card-loop','accepted versus earlier payout-load scheduling')
replacements={'assert_eq!(gs.len(),36);assert_eq!(cs.len(),364);':'assert_eq!(gs.len(),116);assert_eq!(cs.len(),764);','"geometries":36,"comparison_pairs":1820':'"geometries":116,"comparison_pairs":3820','if c["profile"]=="all_zero"||n(g,"m_p")==0||n(g,"m_o")==0 {':'if !c["payout_test"].as_bool().unwrap_or(false) && (c["profile"]=="all_zero"||n(g,"m_p")==0||n(g,"m_o")==0) {','if count>0&&n(g,"target_m")>=127&&':'if !c["payout_test"].as_bool().unwrap_or(false) && count>0&&n(g,"target_m")>=127&&','if width==128&&count>0&&':'if !c["payout_test"].as_bool().unwrap_or(false) && width==128&&count>0&&','assert_eq!(launches,3640);assert_eq!(active_words,986200);assert_eq!(guard_checks,6464120);assert_eq!(input_checks,76440);':f'assert_eq!(launches,{launches});assert_eq!(active_words,{active});assert_eq!(guard_checks,{guards});assert_eq!(input_checks,{pairs*42});','"comparison_pairs":1820,"kernel_launches":launches':'"comparison_pairs":3820,"kernel_launches":launches'}
for a,b in replacements.items():assert probe.count(a)==1,a;probe=probe.replace(a,b,1)
(H/'probe.rs').write_bytes(probe.encode('utf-8'))
for name in ['execute.py','audit.py']:
 t=(A/name).read_text(encoding='utf-8').replace('E089','E107');imp="sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old";assert t.count(imp)==1;t=t.replace(imp,"sys.path.insert(0,str(R/'epoch'));import common as old")
 t=t.replace('pass_compiled_serial_card_loop_prerequisites','pass_compiled_prerequisites_numerical_pending').replace('pass_scoped_full_serial_card_loop_raw_equivalence','pass_scoped_full_early_payout_raw_equivalence')
 t=t.replace('1823','3823').replace('1820','3820').replace('3640','7640')
 if name=='execute.py':t=t.replace('raw.stat().st_size<2*1024**3','raw.stat().st_size<8*1024**3')
 else:
  a="if width==128 and case['count']and";assert t.count(a)==1;t=t.replace(a,"if not case.get('payout_test',False) and width==128 and case['count']and")
 ast.parse(t);(H/name).write_bytes(t.encode('utf-8'))
old=h.read(RES/'protocol.json');cmd=[x.replace(str(RES),str(H))for x in old['rustc_command']]
files=[Path(__file__),RES/'report.json',N/'report.json',ROOT/'epoch/common.py']+[p for p in H.iterdir()if p.is_file()]+[p for p in S.iterdir()if p.is_file()]+[p for p in (ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]+[A/n for n in ['probe.rs','execute.py','audit.py','corpus.json','protocol.json']]
h.save(H/'protocol.json',{'id':'E107-kernel-control','at':h.now(),'status':'FROZEN_PRE_FIRST_APPLICATION_KERNEL','rustc_command':cmd,'input_sha256':{str(p):h.sha(p)for p in files},'resource_report':str(RES/'report.json'),'native_mechanism_report':str(N/'report.json'),'widths':[1,32,64,128,256],'base_cases':764,'geometries':116,'original_cases_retained_exact':364,'payout_patterns':patterns,'payout_extra_cases':400,'expected_pairs':pairs,'expected_application_launches':launches,'expected_active_words':active,'expected_guard_word_checks':guards,'sealed_PTX_sha256':{a:h.sha(H/(a+'.ptx'))for a in ['baseline','candidate']},'scope':'Original364 physical showdown cases retained byte-for-byte as first cases; add400 cases from8 fixed geometries x10 payout triplets x4 reach profiles plus count0. Test all764 x5 widths,21 complete actual immutable buffers, entire physical output and all unowned guards. Original anti-vacuity/zero/rounding assertions retained for originalcases; exact input/output and guards mandatory for every new exceptional-payout case. One compiler/one fixed native process then complete raw reader. No NVRTC/source activation/solve/performance. Fail closes exact early-payout form; no placement/volatile/asm/helper/entry subset/flags/quality or extra-sample rescue. Finite matrix, no universal or unsupported-input guarantee.','candidate_accepted':False,'performance_measurement':False})
for name in ['protocol.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E107');e.update(stage='Frozen full-output showdown numerical controls',correctness='PTX_native_mechanism_and_resource_pass',reason='3820 fixed original/candidate raw pairs: original1820 plus2000 exceptional-payout/count controls. All21 actual input buffers, entire CFV and guards. No speed claim.');e['evidence'].append({'label':'Frozen direct numerical matrix','url':'evidence/'+H.name+'/protocol.json'});s.update(updated_at=h.now(),stage='E107 full showdown numerical controls',activity='Native code preserves early reads; numerical matrix frozen before application kernels. E080 remains live, no gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'pairs':pairs,'launches':launches,'active_words':active,'guards':guards}),flush=True)
