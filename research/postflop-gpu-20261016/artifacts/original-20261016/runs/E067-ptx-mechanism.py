"""Read-only PTX CFG/actor-branch audit for the exact D049/E043 source form."""
import collections,json,re

def audit(text,arity):
    a=text.index('.visible .entry down_action(');b=text.index('{',a);i=b+1;depth=1
    while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
    text=text[a:i];raw=text.splitlines();instructions=[];labels={};pointer_tags={};actor_regs=set();dispatch=[];na_regs=set()
    for lineno,line in enumerate(raw,1):
        line=line.strip()
        if line.endswith(':'):labels[line[:-1]]=len(instructions);continue
        if not line.endswith(';') or line.startswith(('.', '//')):continue
        m=re.fullmatch(r'(?:(@!?%p[0-9]+)\s+)?([^\s]+)\s*(.*);',line)
        if not m:continue
        pred,op,args=m.groups();regs=re.findall(r'%[A-Za-z]+[0-9]+',args);dst=regs[0] if regs else None
        # SSA-like PTX address temps; integer loads deliberately terminate pointer provenance.
        if op.startswith('ld.param.u64'):
            param=re.search(r'down_action_param_([0-9]+)',args)
            if param:pointer_tags[dst]={int(param[1])}
        elif op.startswith('ld.global'):
            address=regs[1] if len(regs)>1 else None;tags=pointer_tags.get(address,set())
            if tags=={3}:actor_regs.add(dst)
            if tags=={4}:na_regs.add(dst)
            pointer_tags.pop(dst,None)
        elif dst and not op.startswith(('st.','bra','ret','call')):
            tags=set().union(*(pointer_tags.get(x,set()) for x in regs[1:])) if len(regs)>1 else set()
            if tags:pointer_tags[dst]=tags
        instructions.append({'line':lineno,'text':line,'predicate':pred,'op':op,'args':args,'regs':regs,'actor_definitions_so_far':sorted(actor_regs)})
        m=re.fullmatch(r'setp\.(eq|ne)\.s32',op)
        if m and len(regs)>=2 and regs[1] in na_regs:
            k=re.search(r',\s*([234])\s*$',args)
            if k:dispatch.append((dst,m[1],int(k[1])))
    assert len(dispatch)>=3 and {x[2] for x in dispatch[:3]}=={2,3,4},dispatch
    known={p:(arity==n if op=='eq' else arity!=n) for p,op,n in dispatch[:3]}
    graph={}
    for j,v in enumerate(instructions):
        op,pred=v['op'],v['predicate'];edges=[]
        if op.startswith('bra'):
            target=v['args'].strip();assert target in labels,target
            if pred:
                reg=pred.lstrip('@!');val=known.get(reg)
                if val is not None and pred.startswith('@!'):val=not val
                if val is not False:edges.append(labels[target])
                if val is not True and j+1<len(instructions):edges.append(j+1)
            else:edges=[labels[target]]
        elif op!='ret' and j+1<len(instructions):edges=[j+1]
        graph[j]=edges
    reached=set();todo=[0]
    while todo:
        j=todo.pop()
        if j in reached:continue
        reached.add(j);todo.extend(graph[j])
    actor_predicates={}
    for j in reached:
        v=instructions[j]
        if v['op'] in ['setp.eq.s32','setp.ne.s32'] and len(v['regs'])>=2 and v['regs'][1] in actor_regs and re.search(r',\s*0\s*$',v['args']):actor_predicates[v['regs'][0]]=j
    branches=[]
    for j in sorted(reached):
        v=instructions[j]
        if v['op'].startswith('bra') and v['predicate'] and v['predicate'].lstrip('@!') in actor_predicates:
            # A branch lies in a cycle iff some successor can reach it in this arity CFG.
            seen=set();pending=list(graph[j]);cyclic=False
            while pending:
                x=pending.pop()
                if x==j:cyclic=True;break
                if x in seen:continue
                seen.add(x);pending.extend(graph[x])
            branches.append({'line':v['line'],'instruction':v['text'],'predicate_definition_line':instructions[actor_predicates[v['predicate'].lstrip('@!')]]['line'],'inside_controlflow_cycle':cyclic})
    fp=collections.Counter(v['op'] for j,v in enumerate(instructions) if j in reached and '.f32' in v['op'] and not v['op'].startswith(('ld.','st.')))
    selected_maps=[]
    for j in sorted(reached):
        v=instructions[j]
        if v['op']=='selp.b64' and len(v['regs'])==4:
            tags=set().union(*(pointer_tags.get(x,set()) for x in v['regs'][1:3]))
            if tags=={8,9}:selected_maps.append({'line':v['line'],'instruction':v['text']})
    return {'arity':arity,'reachable_instructions':len(reached),'dispatch':dispatch[:3],'actor_load_registers':sorted(actor_regs),'actor_predicated_branches':branches,'actor_branches':len(branches),'actor_branches_in_cycles':sum(x['inside_controlflow_cycle'] for x in branches),'selected_map_pointer_sites':selected_maps,'floating_arithmetic_opcode_histogram':dict(sorted(fp.items())),'entry_source_lines':len(raw),'limits':'Static PTX CFG; reachability fixes only initialNA dispatch and allows both outcomes for all other conditions. Cycles conservatively cover loop-control paths, not measured dynamic counts or hardware branches. FP opcode equality is corroboration; exact source integer-only delta and fresh numerical evidence remain required.'}

def compare(baseline,candidate):
    rows=[]
    for na in [2,3,4]:
        b,c=audit(baseline,na),audit(candidate,na)
        gates={'baseline_has_actor_branches_in_hand_loops':b['actor_branches_in_cycles']>0,'candidate_no_actor_predicated_branches':c['actor_branches']==0,'one_selected_map_pointer_per_common_path':len(c['selected_map_pointer_sites'])==1,'same_floating_arithmetic_opcode_histogram':b['floating_arithmetic_opcode_histogram']==c['floating_arithmetic_opcode_histogram']}
        rows.append({'arity':na,'baseline':b,'candidate':c,'gates':gates})
    return {'rows':rows,'gates':{f"NA{x['arity']}:{k}":v for x in rows for k,v in x['gates'].items()},'performance_measured':False,'candidate_accepted':False,'limits':'Root source/CFG review, not external independent review, native SASS timing, numerical proof or speed evidence.'}
