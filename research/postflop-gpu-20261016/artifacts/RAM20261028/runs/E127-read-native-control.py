"""Bounded PTX control-graph/native barrier and actual captured parameter-layout reader."""
import collections,json,re,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E127-native';P=h.read(H/'control-protocol.json');R=ROOT/'runs/E127-resource/execution'
assert len(sys.argv)==2
h.pin(H/'control-protocol.json',sys.argv[1])
for path,digest in P['input_sha256'].items():h.pin(path,digest)
def ptx_graph(text):
    text=text[text.index('{')+1:text.rindex('}')];instructions=[];labels={}
    for line in text.splitlines():
        line=line.strip()
        if not line or line.startswith('//')or line.startswith('.')or line in['{','}']:continue
        if line.endswith(':'):
            assert re.fullmatch(r'\$L__BB\d+_\d+:',line),line
            labels[line[:-1]]=len(instructions);continue
        assert line.endswith(';'),line
        code=re.sub(r'\s+',' ',line[:-1]);m=re.fullmatch(r'(?:(@!?%p\d+) )?([\w.]+)(?: (.*))?',code);assert m,code
        instructions.append({'predicate':m[1],'opcode':m[2],'operands':m[3]or'','text':code})
    edges={};terminals=[]
    for index,ins in enumerate(instructions):
        op=ins['opcode']
        assert op not in['call','brx.idx','trap','exit'],op
        if op=='ret':edges[index]=[];terminals.append(index)
        elif op=='bra':
            assert ins['operands']in labels,ins
            edges[index]=[labels[ins['operands']]]+([index+1]if ins['predicate']else[])
        else:edges[index]=[index+1]
        assert all(0<=x<len(instructions)for x in edges[index])
    barriers=[i for i,x in enumerate(instructions)if x['opcode']=='bar.sync'];assert len(barriers)==1 and instructions[barriers[0]]['operands']=='0'
    assert len(terminals)==1
    branches=[i for i,x in enumerate(instructions)if x['opcode']=='bra'];first=branches[0];barrier=barriers[0]
    prefix=';\n'.join(x['text']for x in instructions[:first+1])+';'
    count=re.search(r'ld.param.u32 (%r\d+), \[up_action_star_param_2\]',prefix)[1]
    block=re.search(r'mov.u32 (%r\d+), %ctaid.x',prefix)[1]
    pred=re.search(r'setp.ge.u32 (%p\d+), '+re.escape(block)+', '+re.escape(count),prefix)[1]
    assert instructions[first]['predicate']=='@'+pred and edges[first][0]==terminals[0]
    assert not any(x['opcode'].startswith('st.global')for x in instructions[:first])
    def reach(start,stop=None):
        todo=[start];seen=set()
        while todo:
            at=todo.pop()
            if at in seen or at==stop:continue
            seen.add(at);todo.extend(edges[at])
        return seen
    valid=first+1;visited=reach(valid)
    assert barrier in visited and terminals[0]in visited
    assert terminals[0]not in reach(valid,barrier),'valid finite path exits before CTA barrier'
    assert not any(a>barrier and b<barrier for a,targets in edges.items()for b in targets),'parent region returns to child region'
    before=sum(x['opcode'].startswith('st.global')for x in instructions[:barrier]);after=sum(x['opcode'].startswith('st.global')for x in instructions[barrier+1:])
    assert before>0 and after>0
    return {'instruction_sites':len(instructions),'branch_sites':len(branches),'barrier_instruction_index':barrier,'valid_block_start_instruction':valid,'only_terminal_instruction':terminals[0],
        'first_uniform_count_guard':instructions[first]['text'],'barrier_postdominates_valid_block_finite_exits':True,'no_parent_to_child_control_edge':True,
        'global_store_sites_child_region':before,'global_store_sites_parent_region':after}
def actual120_bindings(text):
    # Fixed captures from the actual compiled120entry. All spans include base/operand provenance,
    # not just counts: original nodes,start,count -> root; originalchildren -> child;
    # childna controls first dispatch, original rootna controls post-barrier dispatch.
    witnesses={
      'root_from_original_worklist':['ld.param.u64 \t%rd172, [up_action_star_param_0];','ld.param.u32 \t%r235, [up_action_star_param_1];','mov.u32 \t%r1, %ctaid.x;','cvta.to.global.u64 \t%rd191, %rd172;','add.s32 \t%r240, %r235, %r1;','mul.wide.u32 \t%rd192, %r240, 4;','add.s64 \t%rd193, %rd191, %rd192;','ld.global.nc.u32 \t%r241, [%rd193];','cvt.u64.u32 \t%rd17, %r241;'],
      'root_children_start_and_arity':['ld.param.u64 \t%rd173, [up_action_star_param_5];','ld.param.u64 \t%rd174, [up_action_star_param_7];','cvta.to.global.u64 \t%rd11, %rd173;','cvta.to.global.u64 \t%rd12, %rd174;','mul.wide.u32 \t%rd194, %r241, 4;','add.s64 \t%rd195, %rd12, %rd194;','ld.global.nc.u32 \t%r2, [%rd195];','add.s64 \t%rd196, %rd11, %rd194;','ld.global.nc.u32 \t%r3, [%rd196];'],
      'child_identity_and_arity':['ld.param.u64 \t%rd179, [up_action_star_param_8];','cvta.to.global.u64 \t%rd7, %rd179;','mov.b32 \t%r807, 0;','$L__BB9_3:','add.s32 \t%r243, %r807, %r2;','mul.wide.u32 \t%rd197, %r243, 4;','add.s64 \t%rd198, %rd7, %rd197;','ld.global.nc.u32 \t%r244, [%rd198];','cvt.u64.u32 \t%rd20, %r244;','mul.wide.u32 \t%rd200, %r244, 4;','add.s64 \t%rd201, %rd199, %rd200;','ld.global.nc.u32 \t%r7, [%rd201];'],
      'uniform_child_skip_and_loop':['setp.lt.s32 \t%p3, %r7, 1;','@%p3 bra \t$L__BB9_178;','$L__BB9_178:','add.s32 \t%r807, %r807, 1;','setp.ne.s32 \t%p122, %r807, %r3;','@%p122 bra \t$L__BB9_3;'],
      'child_234_generic_dispatch':['setp.eq.s32 \t%p4, %r7, 4;','setp.eq.s32 \t%p5, %r7, 3;','setp.ne.s32 \t%p6, %r7, 2;'],
      'parent_234_generic_dispatch':['setp.eq.s32 \t%p123, %r3, 4;','setp.eq.s32 \t%p124, %r3, 3;','setp.ne.s32 \t%p125, %r3, 2;','shl.b64 \t%rd1561, %rd17, 2;','add.s64 \t%rd1562, %rd10, %rd1561;','ld.global.nc.u32 \t%r614, [%rd1562];']}
    for label,lines in witnesses.items():
        assert all(line in text for line in lines),label
    a,b=text.split('bar.sync \t0;',1)
    assert all(line in a for key,lines in witnesses.items()if key!='parent_234_generic_dispatch'for line in lines)
    assert all(line in b for line in witnesses['parent_234_generic_dispatch'])
    assert not re.search(r'%(?:rd20|r244|r807|r7)\b',b),'parent consumes child loop node/arity state'
    return witnesses
def parameter_layout(blob):
    assert blob[:6]==b'\x7fELF\x02\x01';shoff=struct.unpack_from('<Q',blob,40)[0];size,n,strindex=struct.unpack_from('<HHH',blob,58)
    assert size==64
    headers=[struct.unpack_from('<IIQQQQIIQQ',blob,shoff+i*size)for i in range(n)]
    table=headers[strindex];names=blob[table[4]:table[4]+table[5]]
    sections={names[h[0]:].split(b'\0')[0].decode():h for h in headers}
    info=sections['.nv.info.up_action_star'];data=blob[info[4]:info[4]+info[5]];at=0;params={};cbank=None;param_bytes=None;records=[]
    while at<len(data):
        fmt,attribute,value=struct.unpack_from('<BBH',data,at);payload=data[at+4:at+4+value]if fmt==4 else b''
        assert fmt in[1,2,3,4]and len(payload)==(value if fmt==4 else 0)
        if fmt==4 and attribute==0x17:
            assert value==12;ordinal,offset=struct.unpack_from('<HH',payload,4);flags=struct.unpack_from('<I',payload,8)[0]
            assert ordinal not in params;params[ordinal]={'offset':offset,'bytes':(flags>>18)&0x3fff,'record_absolute_offset':info[4]+at}
        elif fmt==4 and attribute==0x0a:
            assert value==8;symbol,base,length=struct.unpack('<IHH',payload);cbank={'symbol':symbol,'base':base,'bytes':length}
        elif fmt==3 and attribute==0x19:param_bytes=value
        records.append({'format':fmt,'attribute':attribute,'value':value});at+=4+(value if fmt==4 else 0)
    assert at==len(data)and set(params)==set(range(20))and cbank is not None
    widths=[8,4,4,4]+[8]*14+[4,4];offsets=[];offset=0
    for width in widths:offset=(offset+width-1)//width*width;offsets.append(offset);offset+=width
    assert param_bytes==cbank['bytes']==offset==144
    assert [params[i]['offset']for i in range(20)]==offsets and [params[i]['bytes']for i in range(20)]==widths
    symtab=sections['.symtab'];sym=struct.unpack_from('<IBBHQQ',blob,symtab[4]+cbank['symbol']*symtab[9]);section_name=names[headers[sym[3]][0]:].split(b'\0')[0].decode()
    assert section_name=='.nv.constant0.up_action_star'
    return {'params':params,'bank':cbank,'actual_constant_section':section_name,'total_parameter_bytes':param_bytes,'attribute_records':records}
def native_control(text,layout):
    ops=[(int(m[1],16),m[2])for m in re.finditer(r'/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*',text)]
    assert ops and len({p for p,v in ops})==len(ops)
    barriers=[(p,v)for p,v in ops if v.startswith('BAR.SYNC')]
    assert len(barriers)==1 and barriers[0][1]=='BAR.SYNC.DEFER_BLOCKING 0x0'
    pc=barriers[0][0];early=[(p,v)for p,v in ops if p<pc and 'EXIT'in v]
    assert early==[(0x50,'@P0 EXIT')]
    bypc=dict(ops);bank=layout['bank']['base'];count=bank+layout['params'][2]['offset']
    assert bypc[0x10]=='S2UR UR4, SR_CTAID.X'and bypc[0x30]==f'LDC R0, c[0x0][0x{count:x}]'
    assert bypc[0x40]=='ISETP.LE.U32.AND P0, PT, R0, UR4, PT'
    assert any('STG.'in v for p,v in ops if p<pc)and any('STG.'in v for p,v in ops if p>pc)
    calls=[v for p,v in ops if 'CALL.'in v]
    assert calls and all('__cuda_sm20_rcp_rn_f32_slowpath'in v or'__cuda_sm3x_div_rn_noftz_f32_slowpath'in v for v in calls)
    indirect=[(p,v)for p,v in ops if re.sub(r'^@!?P\d+\s+','',v).startswith('BRX')]
    assert len(indirect)==1 and indirect[0][0]>pc
    return {'native_instruction_sites':len(ops),'barrier_PC':hex(pc),'barrier':barriers[0][1],'only_pre_barrier_EXIT':early,'uniform_exit_sources':['SR_CTAID.X','actual_param_2_count'],
        'captured_actual_count_constant_address':hex(count),'application_helper_calls':0,'CUDA_ordinary_division_slowpath_call_sites':len(calls),
        'indirect_parent_dispatch_PC':hex(indirect[0][0]),'global_stores_in_both_regions':True}
ptx={arch:(R/('star-'+arch+'.ptx.txt')).read_text(encoding='utf-8')for arch in['compute_120','compute_75']}
graphs={arch:ptx_graph(text)for arch,text in ptx.items()};bindings=actual120_bindings(ptx['compute_120'])
binary=(H/'execution/module-0.cubin').read_bytes();layout=parameter_layout(binary);sass=(H/'execution/up_action_star.sass.txt').read_text(encoding='utf-8');native=native_control(sass,layout)
negative=[]
def reject(label,function):
    try:function()
    except(AssertionError,AttributeError,KeyError,IndexError):negative.append(label)
    else:raise AssertionError('accepted corrupt '+label)
reject('missing_CTA_barrier',lambda:ptx_graph(ptx['compute_120'].replace('bar.sync \t0;','',1)))
needle='@%p1 bra \t$L__BB9_359;'
assert needle in ptx['compute_120']
reject('valid_thread_early_return',lambda:ptx_graph(ptx['compute_120'].replace(needle,needle+'\n\tret;',1)))
reject('wrong_child_ID_table_base',lambda:actual120_bindings(ptx['compute_120'].replace('add.s64 \t%rd198, %rd7, %rd197;','add.s64 \t%rd198, %rd12, %rd197;',1)))
reject('parent_uses_child_arity',lambda:actual120_bindings(ptx['compute_120'].replace('setp.eq.s32 \t%p123, %r3, 4;','setp.eq.s32 \t%p123, %r7, 4;',1)))
reject('native_wrong_early_exit_predicate',lambda:native_control(sass.replace('@P0 EXIT','@P1 EXIT',1),layout))
reject('native_wrong_barrier_ID',lambda:native_control(sass.replace('BAR.SYNC.DEFER_BLOCKING 0x0','BAR.SYNC.DEFER_BLOCKING 0x1',1),layout))
corrupt=bytearray(binary);struct.pack_into('<H',corrupt,layout['params'][2]['record_absolute_offset']+4+6,16)
reject('captured_parameter_offset_corruption',lambda:parameter_layout(corrupt))
assert len(negative)==7
h.save(H/'control-report.json',{'id':'E127-native-control','at':h.now(),'status':'pass_scoped_two_phase_control_and_captured_parameter_contract',
    'protocol_sha256':sys.argv[1],'PTX_complete_control_graphs':graphs,'actual120_root_child_loop_and_parent_bindings':bindings,
    'captured_native_parameter_layout':layout,'native_control_witnesses':native,'negative_corruption_controls_rejected':negative,
    'scope':'BothwholePTXentryCFGschecked:validCTAfiniteexitspasssinglebarrier,onlyinvalidblockuniformexitcanbypass,no parent-to-childedge. Exactcompiled120root/childIDs/arity/looplatch/parentconsumersandactualCUBIN20paramoffsets/widthsreplayed. ActualSASScountguarduniformonlyprebarrierEXIT/onebarrier/child+parentstores,forceinlineapplicationhelpers;onlyoriginalCUDAdivisionmathslowpathcalls.',
    'limits':'NotfullSASSCFG/FPoperandequivalence,norC++pointervalidity/GPUmemoryrace/numerical/capacity/material/speedproof. ParentindirectSASSdispatchoccurspostbarrier; completePTXCFG/sourceinverseprovidesstructuredcontrolproof. FiniteD313memoryownershipplusactualhosteligibilitymustholdbeforeappkernels. Allrawdirect/engine/canonicalandadoptiongatesremain.',
    'new_compilers_native_GPU_CFR_solver_or_speed_samples':0,'candidate_adopted':False,'all_new_bulk_X_S_readonly_no_T':True})
print(json.dumps({'status':'pass','architectures':list(graphs),'negative':negative,'native_barrier_PC':native['barrier_PC'],'actual_parameter_bytes':layout['total_parameter_bytes']}),flush=True)
