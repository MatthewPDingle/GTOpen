"""Independently compare all actual53fields/caps and precise fold marker against accepted dumps."""
import array,json,struct,sys
from pathlib import Path
def replay(path,case,reference):
 checks=0;words=0;markers=0;folds=None
 def ck(v,label):
  nonlocal checks
  assert v,(case,label);checks+=1
 def vec(f):
  n,=struct.unpack('<Q',f.read(8));ck(n<100000000,'bounded vector');v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'complete vector');return v
 with Path(path).open('rb')as f,Path(reference).open('rb')as g:
  ck(f.read(16)==b'E078-PLAN-RAW1\0\0'and g.read(16)==b'D092-PLAN-RAW1\0\0','magic');ck(f.read(8)==g.read(8)==struct.pack('<II',case,53),'case and schema');sa,sb=struct.unpack('<QQ',f.read(16));ra,rb=struct.unpack('<QQ',g.read(16));ck(sa==sb==ra==rb,'allactualstruct sizes')
  for field in range(53):
   ck(f.read(4)==g.read(4)==struct.pack('<I',field),'fieldid');ca,cb,wa,wb=[vec(f)for _ in range(4)];rca,rcb,rwa,rwb=[vec(g)for _ in range(4)];ck(ca==cb==rca,'allactualfieldcapacities matchaccepted');ck(wa==rwa,'all53baselinefieldvalues matchaccepted');words+=len(wa)
   if field==13:ck(wa[0]==len(wa)-1,'fold vector');folds=wa[1:]
   if field==24:
    ck(folds is not None and wa[0]==len(wa)-1,'arity/fold framing');expected=wa[:]
    for node in folds:ck(node<wa[0]and wa[node+1]==0,'onlyoriginalzeroarityfold entry');expected[node+1]=(1<<64)-1;markers+=1
    ck(wb==expected,'allactualprivate marker bits onlyfolds')
   else:ck(wa==wb,'all52otherfullfieldvalues exact')
  ck(vec(f)==vec(g),'allnodekind words exact');ck(vec(f)==vec(g),'fullchildslot words exact');ck(f.read(1)==g.read(1)==b'','complete rawendpoints')
 native=[json.loads(x.split('E078 ',1)[1])for x in Path(path).with_suffix('.stdout.log').read_text(encoding='utf-8').splitlines()if x.startswith('E078 ')];ck(len(native)==1,'one nativecase');v=native[0];ck(v['id']==case and v['fields']==53 and v['baseline_words']==words and v['all_non_marker_fields_bitwise_equal']and v['all_vec_capacities_equal']and v['gpu_executions']==0,'nativeinventory')
 return {'case':case,'root_checks':checks,'accepted_baseline_words':words,'exact_private_fold_markers':markers,'all52otherfields_and53capacities_and_structs_exact':True,'all53baselinefields_match_retained_accepted':True,'native_summary':v}
