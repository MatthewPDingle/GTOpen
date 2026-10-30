import collections,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D282-zero-tie-PTX';R=ROOT/'runs/E118-resource';S=ROOT/'runs/E118-source';D=ROOT/'runs/D281-zero-tie-scout'
def instructions(text):
    out=[]
    for line in text.splitlines():
        m=re.match(r'^\s*(?:(@!?%p\d+)\s+)?([a-z][\w.]*)\s+([^;]+);\s*$',line)
        if m:out.append((m[1],m[2],[x.strip()for x in m[3].split(',')],line.strip()))
    return out
def definitions(text):
    out=collections.defaultdict(list)
    for pred,op,args,line in instructions(text):
        if args and re.fullmatch(r'%[rf]\w*\d+',args[0])and not op.startswith(('st.','bra','bar.')):out[args[0]].append((op,args[1:],line))
    return out
def ancestors(reg,defs,seen=None):
    seen=set()if seen is None else seen
    if reg in seen:return set()
    seen.add(reg);out=set()
    for op,args,line in defs.get(reg,[]):
        if op.startswith('ld.param.'):
            for value in args:
                match=re.search(r'up_show_param_(\d+)',value)
                if match:out.add(int(match[1]))
        else:
            for operand in args:
                for parent in re.findall(r'%[rf]\w*\d+',operand):out |=ancestors(parent,defs,seen)
    return out
def card_loads(region):
    ins=instructions(region);defs={};records=[]
    for pred,op,args,line in ins:
        if op=='ld.shared.f32'and len(args)==2:
            addr=args[1].strip('[]');base_def=defs.get(addr)
            if base_def and base_def[0]=='add.s64':
                operands=base_def[1]
                for product in operands:
                    mul=defs.get(product)
                    if not mul or mul[0]!='mul.wide.u32'or mul[1][1]!='4':continue
                    pos=mul[1][0];origin=defs.get(pos)
                    if origin and origin[0]=='ld.shared.u32':
                        value=args[0];adds=[r[3]for r in ins if r[1]=='add.f32'and value in r[2][1:]];records.append({'reach_value':value,'position':pos,'reach_address':addr,'position_load':origin[2],'reach_load':line,'adds_using_same_word':adds,'add_count':len(adds)})
        if args and re.fullmatch(r'%[rf]\w*\d+',args[0])and not op.startswith(('st.','bra','bar.')):defs[args[0]]=(op,args[1:],line)
    assert records
    return records
def inspect(text):
    defs=definitions(text);barriers=re.findall(r'\bbar\.(?:sync|red)(?:\.[\w]+)*[^;]*;',text);assert len(barriers)==5 and barriers[0].startswith('bar.red.or.pred')and all(x.startswith('bar.sync')for x in barriers[1:])
    pre=text[:text.index('bar.red.or.pred')];loads=re.findall(r'ld\.global\.nc\.f32\s+(%f\d+),\s*\[(%rd\d+)\];',pre);assert len(loads)==1;reach,address=loads[0];assert 8 in ancestors(address,defs)
    stored=re.search(r'st\.shared\.f32\s+\[%rd\d+\],\s*'+re.escape(reach)+r';',pre);assert stored
    convert=re.search(r'mov\.b32\s+(%r\d+),\s*'+re.escape(reach)+r';',pre);assert convert;bits=convert[1]
    cmp=re.search(r'setp\.gt\.u32\s+(%p\d+),\s*'+re.escape(bits)+r',\s*1736441856;',pre);assert cmp
    choose=re.search(r'selp\.u32\s+(%r\d+),\s*1,\s*0,\s*'+re.escape(cmp[1])+r';',pre);assert choose
    acc=re.search(r'or\.b32\s+(%r\d+),\s*\1,\s*'+re.escape(choose[1])+r';',pre);assert acc;accumulator=acc[1];assert re.search(r'mov\.(?:b32|u32)\s+'+re.escape(accumulator)+r',\s*0;',pre)
    red=re.search(r'setp\.ne\.u32\s+(%p\d+),\s*'+re.escape(accumulator)+r',\s*0;\s*bar\.red\.or\.pred\s+(%p\d+),\s*0,\s*\1;\s*selp\.u32\s+(%r\d+),\s*1,\s*0,\s*\2;',text);assert red;any_bad=red[3]
    # Explicit payout-prefix multiply/FMA and finite-nonzero branch.
    pfx=re.search(r'mul\.rn\.f32\s+(%f\d+),\s*(%f\d+),\s*(%f\d+);\s*fma\.rn\.f32\s+(%f\d+),\s*(%f\d+),\s*(%f\d+),\s*\1;',text);assert pfx
    product,lose,higher,first,win,lower=pfx.groups();assert 4 in ancestors(lose,defs)and 3 in ancestors(win,defs);assert not({3,5}&ancestors(lose,defs))and not({4,5}&ancestors(win,defs))
    gate=re.match(r'\s*mov\.b32\s+(%r\d+),\s*'+re.escape(first)+r';\s*and\.b32\s+(%r\d+),\s*\1,\s*2147483647;\s*add\.s32\s+(%r\d+),\s*\2,\s*-1;\s*setp\.lt\.u32\s+(%p\d+),\s*\3,\s*2139095039;\s*@\4\s+bra\s+(\$L__BB\d+_\d+);',text[pfx.end():]);assert gate
    branch_end=pfx.end()+gate.end();join=gate[5];join_pos=text.index(join+':',branch_end);replay=text[branch_end:join_pos];store=re.match(r'\s*(?:add\.s64[^;]+;\s*shl\.b64[^;]+;\s*add\.s64[^;]+;\s*)st\.global\.f32\s+\[(%rd\d+)\],\s*'+re.escape(first)+r';',text[join_pos+len(join)+1:]);assert store
    assert not any(op.startswith(('add.f','sub.f','mul.f','fma.'))for pred,op,args,line in instructions(text[join_pos+len(join)+1:join_pos+len(join)+1+store.end()]))
    # The actual total-card replay, same-combo read and original final FMA
    # lie strictly between branch and join, not on the taken store path.
    same=[]
    for pred,op,args,line in instructions(replay):
        if op.startswith('ld.global.')and len(args)==2:
            addr=args[1].strip('[]')
            if 19 in ancestors(addr,defs):same.append(line)
    assert len(same)==1
    final=re.search(r'fma\.rn\.f32\s+'+re.escape(first)+r',\s*(%f\d+),\s*(%f\d+),\s*(%f\d+);',replay);assert final;assert 5 in ancestors(final[1],defs)
    replay_loads=card_loads(replay);assert all(x['add_count']==1 for x in replay_loads)
    # Actual CTA guard rejects bad reach, m_o outside1..1326, nonpositive/
    # unordered total, nonzero tie, and nonfinite win/lose before fast loop.
    guard=re.search(r'setp\.ne\.s32\s+(%p\d+),\s*'+re.escape(any_bad)+r',\s*0;\s*add\.s32\s+(%r\d+),\s*(%r\d+),\s*-1;\s*setp\.gt\.u32\s+(%p\d+),\s*\2,\s*1325;\s*or\.pred\s+(%p\d+),\s*\1,\s*\4;\s*setp\.leu\.f32\s+(%p\d+),\s*(%f\d+),\s*0f00000000;\s*or\.pred\s+(%p\d+),\s*\5,\s*\6;\s*@\8\s+bra\s+(\$L__BB\d+_\d+);',text);assert guard;fallback=guard[9];assert 15 in ancestors(guard[3],defs);assert text.index(fallback+':')>join_pos
    finite_guard=text[guard.end():pfx.start()];tie=re.search(r'mov\.b32\s+(%r\d+),\s*(%f\d+);\s*and\.b32\s+(%r\d+),\s*\1,\s*2147483647;\s*setp\.ne\.s32\s+(%p\d+),\s*\3,\s*0;',finite_guard);assert tie and 5 in ancestors(tie[2],defs)
    assert re.search(r'abs\.f32\s+(%f\d+),\s*'+re.escape(win)+r';\s*setp\.equ\.f32\s+(%p\d+),\s*\1,\s*0f7F800000;',finite_guard);assert re.search(r'abs\.f32\s+(%f\d+),\s*'+re.escape(lose)+r';\s*setp\.equ\.f32\s+(%p\d+),\s*\1,\s*0f7F800000;',finite_guard)
    main=text[guard.end():pfx.start()];fast_loads=card_loads(main);assert all(x['add_count']==2 for x in fast_loads)
    assert '.ftz'not in pfx[0]
    return{'reach_load':reach,'reach_address':address,'reach_domain_bit_register':bits,'reach_bad_accumulator':accumulator,'CTA_any_bad_register':any_bad,'payout_registers':{'win':win,'lose':lose,'tie':tie[2]},'prefix_register':first,'prefix_ops':pfx[0],'prefix_guard_unsigned_identity':'u32((absbits)-1) <0x7f7fffff iff absbits in1..0x7f7fffff; complete32bitdomain, not samples','nonzero_finite_branch':gate[0],'store_join':join,'fallback_label':fallback,'skip_same_combo_read':same,'skipped_final_tie_FMA':final[0],'all5semantic_barriers':barriers,'fast_card_reach_loads':fast_loads,'replay_card_reach_loads':replay_loads,'proof_scope':'Operand/CFG witness, not fullPTX simulator/actualnativeIEEE/speedproof. Actualbarrierlegality,inputextents,unfilteredoriginalcorpus/caller/fullstate still mandatory.'}
if len(sys.argv)==1:
    h.custody();H.mkdir(exist_ok=False);assert all(h.read(R/'report.json')['gates'].values());paths=[Path(__file__),ROOT/'epoch/common.py',R/'protocol.json',R/'report.json',S/'manifest.json',D/'arithmetic-contract.json',D/'hit-classification.json',D/'static-payout-census.json']+[R/'execution'/(arm+'-compute_120-up_show.ptx.txt')for arm in['baseline','candidate']]
    h.save(H/'protocol.json',{'id':'D282','at':h.now(),'status':'FROZEN_PRE_READ_ONLY_EMITTED_MECHANISM_READER','input_sha256':{str(p):h.sha(p)for p in paths},'requirements':'Actualboundedunsignedroclassifierfeedsfirstbar.red.or withsameglobal/sharedvalue;4laterbar.sync retained. Actualbad/mo/total/tie/finitepayoffuniformguardsbranchtooriginalfallback. Actualnativebaseline-orderedmul.rn(lose,higher)+fma.rn(win,lower,product) withnonzerofiniteunsignedbitguard branchesdirectlytooriginalprefixstore, skippingtot_c replay/same_p/valid/tied/finaltieFMA. Fastcardposition-reachloads feed2orderedcorrectionadds;replayfeeds1totaladd. Checkwrongthreshold/branch/register/thirdsum/storemutations fail before anyapplicationkernel. No source/helper/predicate/arch/samplechange.','scope':'SealedPTX/sourceCPUstructuralreaderonly; no newGPU/module/kernel/solver/speed. Rootreviewnotexternalindependentaudit.'});print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;P=h.read(H/'protocol.json');h.pin(H/'protocol.json',sys.argv[1]);h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
text=(R/'execution/candidate-compute_120-up_show.ptx.txt').read_text(encoding='utf-8');witness=inspect(text);fixtures=[]
mutations=[('bad_reach_threshold',text.replace('1736441856;','1736441857;',1)),('inf_prefix_accepted',text.replace('2139095039;','2139095040;',1)),('store_wrong_prefix',re.sub(r'(st\.global\.f32\s+\[%rd\d+\],\s*)'+re.escape(witness['prefix_register'])+r';',r'\g<1>%f999999;',text,count=1)),('wrong_prefix_product',text.replace(witness['prefix_ops'],witness['prefix_ops'].replace(witness['payout_registers']['lose'],witness['payout_registers']['win'],1),1))]
load=witness['fast_card_reach_loads'][0]['reach_load'];value=witness['fast_card_reach_loads'][0]['reach_value'];mutations.append(('unexpected_third_card_sum',text.replace(load,load+'\n add.f32 %f999999, %f999999, '+value+';',1)))
for name,wrong in mutations:
    assert wrong!=text
    try:inspect(wrong)
    except AssertionError:fixtures.append({'fixture':name,'rejected':True})
    else:raise AssertionError('negative fixture accepted '+name)
h.save(H/'report.json',{'id':'D282','at':h.now(),'status':'pass_scoped_zero_tie_PTX_guard_bypass_prefix_and_card_recurrence','protocol_sha256':sys.argv[1],'candidate_entry_sha256':h.sha(R/'execution/candidate-compute_120-up_show.ptx.txt'),'witness':witness,'negative_reader_fixtures':fixtures,'application_kernel_launches_solver_or_speed_samples':0,'candidate_accepted':False,'limits':P['scope']});h.custody();print(json.dumps({'status':'pass','fast_card_load_sites':len(witness['fast_card_reach_loads']),'replay_card_load_sites':len(witness['replay_card_reach_loads']),'negative_reader_fixtures':len(fixtures)}),flush=True)
