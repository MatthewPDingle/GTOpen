"""Full actual device images, guards, physical cards, and finite fold oracle."""
from pathlib import Path
import array,json,math,struct
def replay(folder,corpus):
 files={};checks=0;output_words=0;input_words=0;guard_words=0;oracle_words=0;cases=[];differences=[];oracle_differences=[]
 def ck(v,label):
  nonlocal checks
  assert v,label;checks+=1
 def vec(f):
  head=f.read(8);ck(len(head)==8,'vector header');n,=struct.unpack('<Q',head);ck(n<2000000,'bounded vector');v=array.array('I');v.fromfile(f,n);ck(len(v)==n,'full vector');return v
 def f32(v):
  try:return struct.unpack('<f',struct.pack('<f',v))[0]
  except OverflowError:return math.copysign(math.inf,v)
 def val(v):return struct.unpack('<f',struct.pack('<I',v))[0]
 def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
 allhands=[(a,b)for a in range(52)for b in range(a+1,52)]
 try:
  for name,magic in[('inputs',b'E078_IN1'),('baseline',b'E078_OUT1'),('candidate',b'E078_OUT1'),('baseline-inputs',b'E078_IM1'),('candidate-inputs',b'E078_IM1')]:
   files[name]=(Path(folder)/(name+'.bin')).open('rb');ck(files[name].read(len(magic))==magic,'file magic '+name)
  for spec in corpus['cases']:
   head=files['inputs'].read(4)
   if not head:break
   case,=struct.unpack('<I',head);ck(case==spec['id']==len(cases),'case sequence');desc=vec(files['inputs']);ck(list(desc)==spec['descriptor'],'full frozen descriptor');immut=[vec(files['inputs'])for _ in range(22)];seeds=[vec(files['inputs'])for _ in range(3)]
   nh,na,block,p,role,algo,t,mode,count,stride,start,parent,off,loff,no,folded,fold_action,fold_node=desc;nn=na+8;base=case//2
   ck(parent==2 and start==1 and off==13 and loff==5 and stride==max(nh,no)+5 and fold_node==4+fold_action and nh<=1326 and no<=1326,'geometry')
   ck(immut[0]==array.array('I',[0xdeadbeef,parent,0xdeadbeef])and immut[21]==array.array('I',[0xdeadbeef,fold_node,0xdeadbeef]),'both worklists')
   ck(immut[1][parent]==immut[1][fold_node]==(1-p if role==2 else p),'actor orientation')
   ck(immut[2][parent]==na and immut[2][fold_node]==(0 if folded else(2**32-7)),'baseline private marker seed')
   ck(immut[11]==array.array('I',spec['discount_bits']),'discount source bits')
   ck(immut[14][fold_node]==2 and immut[14][parent]==5 and len(immut[15])>=3*no,'opponent reach source distinction')
   ck(immut[16]==array.array('I',[h[0]for h in allhands[:nh]]+[0xdeadbeef]*7)and immut[17]==array.array('I',[h[1]for h in allhands[:nh]]+[0xdeadbeef]*7),'physical own cards and guards')
   opp=[allhands[(1325-j+base)%1326]for j in range(no)];offs=[];indices=[]
   for card in range(52):
    offs.append(len(indices));indices.extend(j for j,h in enumerate(opp)if card in h)
   offs.append(len(indices));ck(immut[18]==array.array('I',offs)and immut[19]==array.array('I',indices)and len(indices)==2*no,'full physical opponent ordered card lists')
   inverse={h:j for j,h in enumerate(opp)};same=[inverse.get(h,0xffffffff)for h in allhands[:nh]]+[0xffffffff]*7;ck(immut[20]==array.array('I',same),'full physical same-combo map')
   fold_slot=immut[10][fold_node];ck(fold_slot!=immut[10][parent]and len(set(immut[10][4:4+na]))==na,'distinct actual parent and child CFV rows')
   outputs={};posts={};case_diff=0
   for arm in['baseline','candidate']:
    f=files[arm];ck(f.read(4)==struct.pack('<I',case),'output case');out=[vec(f)for _ in range(3)];outputs[arm]=out;ck(all(len(x)==len(y)for x,y in zip(out,seeds)),'all full mutable lengths');output_words+=sum(map(len,out))
    f=files[arm+'-inputs'];ck(f.read(4)==struct.pack('<I',case),'actualinput case');post=[vec(f)for _ in range(22)];posts[arm]=post
    for field,(actual,expected)in enumerate(zip(post,immut)):
     if field==2 and arm=='candidate'and folded:expected=expected[:];expected[fold_node]=0xffffffff
     ck(actual==expected,'full actual immutable '+arm+'/'+str(case)+'/'+str(field));input_words+=len(actual)
    for kind,(actual,seed)in enumerate(zip(out,seeds)):
     for i,(a,b)in enumerate(zip(actual,seed)):
      owned=count!=0 and((role==0 and off<=i<off+na*nh)if kind<2 else(parent*stride<=i<parent*stride+nh or(folded and fold_slot*stride<=i<fold_slot*stride+nh)))
      if not owned:ck(a==b,'full guard/unowned '+str((case,arm,kind,i)));guard_words+=1
   for kind,(a,b)in enumerate(zip(outputs['baseline'],outputs['candidate'])):
    for i,(x,y)in enumerate(zip(a,b)):
     if x!=y:
      case_diff+=1
      if len(differences)<32:differences.append({'case':case,'kind':kind,'index':i,'baseline_bits':x,'candidate_bits':y})
   if folded and count and mode in[0,1,4]:
    reach=[val(x)for x in immut[15][2*no:3*no]];s=[]
    for card in range(52):
     total=0.0
     for j in indices[offs[card]:offs[card+1]]:total=f32(total+reach[j])
     s.append(total)
    partials=[]
    for thread in range(block):
     total=0.0
     for j in range(thread,no,block):total=f32(total+reach[j])
     partials.append(total)
    step=block>>1
    while step:
     for thread in range(step):partials[thread]=f32(partials[thread]+partials[thread+step])
     step>>=1
    amount=val(immut[13 if immut[1][fold_node]==p else 12][fold_node])
    for i in range(nh):
     same_r=0.0 if same[i]==0xffffffff else reach[same[i]];valid=f32(f32(f32(partials[0]-s[immut[16][i]])-s[immut[17][i]])+same_r);expected=bits(f32(amount*valid));actual=outputs['baseline'][2][fold_slot*stride+i];oracle_words+=1
     if expected!=actual and len(oracle_differences)<32:oracle_differences.append({'case':case,'hand':i,'expected_bits':expected,'actual_baseline_bits':actual})
   cases.append({'id':case,'has_fold':bool(folded),'full_output_mismatch_words':case_diff,'all_actual_inputs_and_guards_exact':True})
  for name,f in files.items():ck(f.read(1)==b'','complete raw endpoint '+name)
 finally:
  for f in files.values():f.close()
 return {'cases':cases,'completed_case_count':len(cases),'complete_frozen_corpus':len(cases)==len(corpus['cases']),'checks':checks,'output_words_both_arms':output_words,'actual_input_words_both_arms':input_words,'guard_words_both_arms':guard_words,'finite_fold_oracle_words':oracle_words,'first_output_differences':differences,'first_finite_fold_oracle_differences':oracle_differences,'all_full_output_words_exact':not differences,'all_finite_fold_oracle_words_exact':not oracle_differences,'all_actual_inputs_and_guards_exact':True}
