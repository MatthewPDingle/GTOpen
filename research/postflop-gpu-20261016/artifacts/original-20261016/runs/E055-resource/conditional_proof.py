"""Conservative PTX reachability for immutable discount reads and role guards."""
import re
def analyze(path):
 text=path.read_text(encoding='utf-8');begin=text.index('.visible .entry up_action(');brace=text.index('{',begin);end=text.index('.visible .entry up_action_eval',brace);body=text[brace+1:end]
 instructions=[];labels={}
 for line in body.splitlines():
  line=line.split('//',1)[0].strip()
  if not line:continue
  if line.endswith(':'):labels[line[:-1]]=len(instructions)
  elif line.endswith(';') and not line.startswith('.'):instructions.append(line)
 roots={};tags={};predicates={};loads={};roles=locks=arity_guards=0
 for i,raw in enumerate(instructions):
  match=re.match(r'@(!?%p\d+)\s+(.*)',raw);guard=match.group(1) if match else None;line=match.group(2) if match else raw
  opcode=line.split()[0];regs=re.findall(r'%[A-Za-z]+\d+',line);dest=regs[0] if regs and re.match(r'\S+\s+%[A-Za-z]+\d+\s*,',line) else None
  newroot=None;newtag=None
  m=re.match(r'ld\.param\.(u32|u64)\s+(%\w+),\s*\[up_action_param_(\d+)\]',line)
  if m:
   index=int(m.group(3));newroot=index if m.group(1)=='u64' else None;newtag='traverser' if index==3 else None
  elif opcode.startswith(('cvta.','mov.','cvt.')) and len(regs)>=2:
   newroot=roots.get(regs[1]);newtag=tags.get(regs[1])
  elif opcode.startswith(('add.','mad.')) and dest:
   choices={roots[r] for r in regs[1:] if roots.get(r) is not None};newroot=next(iter(choices)) if len(choices)==1 else None
  if opcode.startswith('ld.global'):
   address=re.search(r'\[(%\w+)(?:[+-]\d+)?\]',line);root=roots.get(address.group(1)) if address else None
   if root==4 and opcode.endswith('u32'):newtag='actor'
   if root==5 and opcode.endswith('u32'):newtag='arity'
   if root==13 and opcode.endswith('u64'):newtag='lock'
   if root==17 and opcode.endswith('f32'):
    width=re.search(r'\.v([24])\.',opcode);loads[i]={'words':int(width.group(1)) if width else 1,'instruction':raw,'guard':guard}
  if dest:roots[dest]=newroot;tags[dest]=newtag
  m=re.match(r'setp\.(eq|ne|lt|ge|gt|le)\.(s32|u32|s64)\s+(%p\d+),\s*([^,]+),\s*([^;]+);',line)
  if m and not guard:
   compare,kind,p,a,b=m.groups();a=a.strip();b=b.strip()
   if compare in ['eq','ne'] and {tags.get(a),tags.get(b)}=={'actor','traverser'}:
    predicates[p]=('own',compare=='eq');roles+=1
   elif tags.get(a)=='arity' and b.lstrip('-').isdigit():predicates[p]=('arity',(compare,int(b),False));arity_guards+=1
   elif tags.get(b)=='arity' and a.lstrip('-').isdigit():predicates[p]=('arity',(compare,int(a),True));arity_guards+=1
   elif kind=='s64':
    if tags.get(a)=='lock' and b=='0' and compare in ['lt','ge']:predicates[p]=('unlocked',compare=='lt');locks+=1
    elif a=='0' and tags.get(b)=='lock' and compare in ['gt','le']:predicates[p]=('unlocked',compare=='gt');locks+=1
 def walk(own,unlocked,arity=None):
  stack=[0];visited=set();seen=set()
  while stack:
   i=stack.pop()
   if i in visited or i>=len(instructions):continue
   visited.add(i);raw=instructions[i];m=re.match(r'@(!?%p\d+)\s+(.*)',raw);guard=m.group(1) if m else None;line=m.group(2) if m else raw;value=None
   if guard:
    token=guard.lstrip('!')
    if token in predicates:
     field,polarity=predicates[token]
     if field=='arity':
      if arity is not None:
       compare,constant,reverse=polarity;a,b=(constant,arity) if reverse else (arity,constant);value={'eq':a==b,'ne':a!=b,'lt':a<b,'ge':a>=b,'gt':a>b,'le':a<=b}[compare]
     else:value=(own if field=='own' else unlocked)==polarity
     if guard.startswith('!') and value is not None:value=not value
   else:value=True
   if i in loads and value is not False:seen.add(i)
   branch=re.match(r'bra(?:\.uni)?\s+(\S+);',line)
   if branch:
    assert branch.group(1) in labels
    if value is not False:stack.append(labels[branch.group(1)])
    if value is not True:stack.append(i+1)
   elif line.startswith('ret'):
    if value is not True:stack.append(i+1)
   else:stack.append(i+1)
  return {'reachable_words':sum(loads[i]['words'] for i in seen),'reachable_loads':[loads[i]['instruction'] for i in sorted(seen)]}
 per_arity={str(a):{'opponent':walk(False,False,a),'locked_own':walk(True,False,a),'unlocked_own':walk(True,True,a)} for a in [1,2,3,4,5,8,9,16,17]}
 return {'role_predicates_identified':roles,'lock_predicates_identified':locks,'arity_predicates_identified':arity_guards,'static_discount_words':sum(x['words'] for x in loads.values()),'static_discount_loads':[x['instruction'] for x in loads.values()],'opponent':walk(False,False),'locked_own':walk(True,False),'unlocked_own':walk(True,True),'per_arity':per_arity}
def review(baseline,candidate):
 b,c=analyze(baseline),analyze(candidate)
 gates={'baseline_all12reads_reachable_for_all3roles':all(b[k]['reachable_words']==12 for k in ['opponent','locked_own','unlocked_own']),'candidate_role_lock_arity_guards_identified':c['role_predicates_identified']>=1 and c['lock_predicates_identified']>=1 and c['arity_predicates_identified']>=3,'baseline_each_arity_reads3words_all3roles':all(v[k]['reachable_words']==3 for v in b['per_arity'].values() for k in ['opponent','locked_own','unlocked_own']),'candidate_opponent_no_discount_reads':c['opponent']['reachable_words']==0,'candidate_locked_no_discount_reads':c['locked_own']['reachable_words']==0,'candidate_each_arity_unlocked3words':all(v['unlocked_own']['reachable_words']==3 for v in c['per_arity'].values())}
 return {'baseline':b,'candidate':c,'gates':gates,'status':'pass_conditional_read_mechanism' if all(gates.values()) else 'failed_conditional_read_mechanism','limits':'Root PTX static overapproximation: source-identified actor/traverser equality, signed lock<0 and declared arity comparisons may be fixed; all other conditions explore both successors. Supported immutable3float discount buffer only. Perarity checks cover1/2/3/4/5/8/9/16/17, allowing compiler body merging. No dynamic frequency, timing or universal numeric proof.'}
