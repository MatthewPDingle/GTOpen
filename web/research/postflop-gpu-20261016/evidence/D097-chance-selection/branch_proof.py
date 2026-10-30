"""Conservative PTX data-flow check for branches dependent on hand-mask bits."""
import re
from pathlib import Path
REG=re.compile(r'%[A-Za-z]+[0-9]+')
def entry(path):
    s=Path(path).read_text();m=re.search(r'\.visible \.entry\s+up_chance\(',s);assert m
    a=s.index('{',m.end());i=a+1;depth=1
    while depth:
        depth+=(s[i]=='{')-(s[i]=='}');i+=1
    return s[m.start():i]
def analyze(path):
    text=entry(path);instructions=[];arg_seeds=set();unknown=[]
    for line in text.splitlines():
        match=re.match(r'\s*(?:@(!?%p[0-9]+)\s+)?([a-z][a-z0-9_.]*)\s*(.*?)\s*;\s*$',line)
        if not match:continue
        pred,op,operands=match.groups();parts=operands.split(',',1)
        dest=REG.findall(parts[0]);src=REG.findall(parts[1]) if len(parts)>1 else []
        if op.startswith(('st.','bra','ret','bar.','call','exit')):dest=[];src=REG.findall(operands)
        if op.startswith('call'):unknown.append(line.strip())
        instructions.append({'pred':pred,'op':op,'dest':dest,'src':src,'operands':operands,'text':line.strip()})
        if op=='ld.param.u64' and '[up_chance_param_9]' in operands:arg_seeds.update(dest)
    assert len(arg_seeds)==1,'Expected unchanged mask pointer parameter9'
    pointer=set(arg_seeds)
    for _ in range(len(instructions)+1):
        before=set(pointer)
        for ins in instructions:
            if ins['op'].startswith(('ld.','st.','setp.')):continue
            if set(ins['src'])&pointer:pointer.update(ins['dest'])
        if pointer==before:break
    loads=[ins for ins in instructions if re.fullmatch(r'ld\.global(?:\.nc)?\.u64',ins['op']) and set(ins['src'])&pointer]
    taint={r for ins in loads for r in ins['dest']}
    for _ in range(len(instructions)+1):
        before=set(taint)
        for ins in instructions:
            if ins['op'].startswith(('ld.','st.','bra','ret','bar.','call','exit')):continue
            if set(ins['src'])&taint:taint.update(ins['dest'])
        if taint==before:break
    branches=[ins['text'] for ins in instructions if ins['op'].startswith('bra') and ins['pred'] and ins['pred'].lstrip('!') in taint]
    comparisons=[ins['text'] for ins in instructions if ins['op'].startswith('setp.') and set(ins['dest'])&taint]
    return {'mask_pointer_registers':sorted(arg_seeds),'mask_load_instructions':[ins['text'] for ins in loads],'mask_value_tainted_registers':sorted(taint),'mask_dependent_comparisons':comparisons,'mask_dependent_branches':branches,'unknown_calls':unknown,'fp_add_sites':sum(ins['op']=='add.f32' for ins in instructions),'entry_instruction_count':len(instructions),'limits':'Conservative explicit register-data taint from loads through unchanged mask-pointer parameter9. No implicit control taint or final-SASS/dynamic divergence claim. Unsupported call-outs or missing mask loads cannot pass.'}
def compare(baseline,candidate):
    b=analyze(baseline);c=analyze(candidate)
    gates={'baseline_mask_loads_found':bool(b['mask_load_instructions']),'candidate_mask_loads_found':bool(c['mask_load_instructions']),'baseline_blocker_branches_found':len(b['mask_dependent_branches'])>0,'candidate_blocker_branches_absent':not c['mask_dependent_branches'],'no_unknown_calls':not b['unknown_calls'] and not c['unknown_calls']}
    return {'status':'pass_blocker_branch_removal' if all(gates.values()) else 'compiled_blocker_branch_prerequisite_failed','baseline':b,'candidate':c,'gates':gates,'kernel_launches':0,'performance_measured':False,'numerical_equivalence_proved':False}
