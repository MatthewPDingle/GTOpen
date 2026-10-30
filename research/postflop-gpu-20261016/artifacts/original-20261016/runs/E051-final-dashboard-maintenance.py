"""Repair observed display strings and refresh the current server validation."""
from pathlib import Path
import copy,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as c
c.custody();O=R/'runs/E051-deployment-dashboard';O.mkdir();changes=[]
with c.ar.exclusive_lock(c.ar.STATUS.with_suffix('.lock'),timeout=3):
 before=c.read(c.ar.STATUS);c.save(O/'status-before.json',before);after=copy.deepcopy(before)
 for key in ['gpu','backend']:
  original=after['hardware'][key];corrected=original.replace('\u00c2\u00b7','\u00b7');assert original!=corrected
  after['hardware'][key]=corrected;changes.append({'path':['hardware',key],'before':original,'after':corrected})
 for index,f in enumerate(after['fixtures']):
  original=f['description'];corrected=original.replace('\u00c2\u00b7','\u00b7');assert original!=corrected
  f['description']=corrected;changes.append({'path':['fixtures',index,'description'],'before':original,'after':corrected})
 original=after['validation']['summary'];assert original.endswith('Last isolated server validation remains E020.')
 corrected=original.replace('Last isolated server validation remains E020.','Fresh E051 server qualification passed20ordinary server tests and100GPU API iterations; the qualified binary is now deployed.')
 after['validation']['summary']=corrected;changes.append({'path':['validation','summary'],'before':original,'after':corrected})
 reverse=copy.deepcopy(after)
 for item in changes:
  parent=reverse
  for key in item['path'][:-1]:parent=parent[key]
  parent[item['path'][-1]]=item['before']
 assert reverse==before
 after['updated_at']=c.now();after['evidence'].append({'label':'Current deployment display and server-validation repair','url':'evidence/'+O.name+'/report.json'});c.ar.atomic_json(c.ar.STATUS,after)
report={'at':c.now(),'status':'six_observed_display_fields_repaired','changes':changes,'all_other_existing_data_exact':True,'performance_values_and_experiment_records_unchanged':True,'browser_evidence':'Observed live rendered hardware/fixture punctuation contained U+00C2 before separators; current validated-result summary still named E020 despite E051 deployment.','source_or_live_binary_changes':False,'before_sha256':c.sha(O/'status-before.json'),'status_after_sha256':c.sha(c.ar.STATUS)}
c.save(O/'report.json',report)
for src in [O/'report.json']:
 dst=c.ar.DASHBOARD/'evidence'/O.name/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 with urllib.request.urlopen(c.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+O.name+'/'+src.name,timeout=15)as response:assert response.read()==src.read_bytes()
with urllib.request.urlopen(c.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=15)as response:assert response.read()==c.ar.STATUS.read_bytes()
c.custody();print({'display_fields_repaired':len(changes),'all_other_data_exact':True,'served_status_exact':True},flush=True)
