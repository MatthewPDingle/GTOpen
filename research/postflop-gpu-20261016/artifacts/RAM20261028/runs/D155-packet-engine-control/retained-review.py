import sys,struct,itertools,math
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
O=H/'output';M=h.read(O/'metadata.json')
checks=words=frames=logicalwords=physicalwords=0
def req(v,s):
    global checks
    assert v,s;checks+=1
def eq(a,b):return a.shape==b.shape and bool(np.array_equal(a,b))
def frame(path,magic):
    global words,frames
    data=path.read_bytes();req(data[:16]==magic,'magic');at=16;fields={}
    while at<len(data):
        kind,n=struct.unpack_from('<II',data,at);at+=8;name=data[at:at+n].decode();at+=n
        count=struct.unpack_from('<Q',data,at)[0];at+=8;req(name not in fields,'unique field')
        if kind==0:
            req(struct.unpack_from('<I',data,at)[0]==0,'all positivezero run');at+=4;v=np.zeros(count,dtype='<u4')
        else:
            req(kind in [1,2],'kind');v=np.frombuffer(data,dtype='<u4',count=count,offset=at);at+=count*4
            if kind==1:
                actual=np.frombuffer(data,dtype='<u4',count=count,offset=at);at+=count*4;req(eq(actual,v),'all actual CPU-reference words')
        fields[name]=v;words+=count
    req(at==len(data),'full frame');frames+=1;return fields
inventory=set(h.read(H/'source-review.json')['device_field_inventory'])|{'iteration','algorithm','hands','CFV_logical'}
def gpu(path,info):
    global physicalwords,logicalwords
    f=frame(path,b'D155-GPU-RAW1\0\0\0');req(set(f)==inventory and len(f)==70,'all70 actual fields')
    phys,logical=f['d_cfv'],f['CFV_logical'];rows,stride,nh=info['rows'],info['stride'],info['logical_hands']
    req(len(phys)==info['physical_words']==rows*stride and len(logical)==rows*nh and 0<nh<=stride,'full geometry')
    req(eq(phys.reshape(rows,stride)[:,:nh].reshape(-1),logical),'every physical/logical mapping')
    req(int(f['hands'][info['logical_player']])==nh and int(f['algorithm'][0])==expected_algo,'actual intended player/algorithm')
    req(requested_iso or not info['actual_iso_active'],'actual intended noiso')
    logicalwords+=len(logical);physicalwords+=len(phys);return f
pattern=np.array([0x7fc01234,0x7f801234,0x7f800000,0xff800000,0xdeadc0de,0xffffffff,0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x4b123456,0x00800000,0x7f7fffff,0xff7fffff],dtype='<u4')
expected=list(itertools.product(['Compressed','F32'],['Dcfr','CfrPlus'],[False,True],[False,True],[False,True]))
expected += [('Compressed',algo,False,iso,False) for board in ['Ks7s2d','Ks7s2dQhTc'] for algo,iso in [('Dcfr',False),('CfrPlus',True)]]
ordinary=['train-first','train-capture','train-replay','strategy-sync','eval-eager','eval-capture','eval-replay','full-sync','train-after-sync','locked-train','locked-eval-eager','locked-eval-capture','unlocked-train','unlocked-eval','before-save','resumed-train','resumed-eval-eager','resumed-eval-capture','resumed-eval-replay','resumed-full-sync']
retained={'strategy-sync','full-sync','before-save','resumed-full-sync'}
epoch=phases=roots=evs=regenerated=readbacks=handled=declined=pinnedguards=0;wrapperpairs=set();coverage_misses=[]
req(len(M['cases'])==36 and not M['performance_measurement'] and M['packing_implementation_created'],'fixed matrix')
for ident,(row,dims) in enumerate(zip(M['cases'],expected)):
    req(row['case']==ident and row['resume_fixture_flags_explicitly_restored'] and row['default_public_fallbacks_silent'],'case order/resume/default assertions')
    req((row['storage'],row['algorithm'],row['reverse_ranges'],row['isomorphism'],row['warm_CPU_start'])==dims,'matrix dimensions')
    req(row['extra_board']==(None if ident<32 else ['Ks7s2d','Ks7s2dQhTc'][(ident-32)//2]),'extra boards')
    expected_algo=0 if dims[1]=='Dcfr' else 1;requested_iso=dims[3]
    continuation=dims[1]=='CfrPlus' and not dims[3]
    stages=ordinary+([f'continuation-{i}-p{p}' for i,p in enumerate([0,1,0,1])] if continuation else [])
    req([x['stage'] for x in row['phases']]==[x['stage'] for x in row['clobbers']]==stages,'all ordered phases/clobbers')
    req(len(row['exploit_bits'])==9 and all(math.isfinite(struct.unpack('<d',struct.pack('<Q',v))[0]) for v in row['exploit_bits']),'all finite exact EV records');evs+=9
    req(len(row['continuation_root_bits'])==len(stages)-20,'all root records')
    for values in row['continuation_root_bits']:req(all(math.isfinite(struct.unpack('<f',struct.pack('<I',v))[0]) for v in values),'finite root words');roots+=1
    for phase,witness in zip(row['phases'],row['clobbers']):
        stage,proof=phase['stage'],witness['proof'];epoch+=1
        req(proof['epoch']==epoch and proof['rotation']==epoch%16 and proof['pattern']==pattern.tolist(),'fixed seed')
        before=gpu(O/f'clobber-{ident:02}-{stage}-before.gpu.bin',proof['info']);after=gpu(O/f'clobber-{ident:02}-{stage}-after.gpu.bin',proof['info'])
        req(eq(after['d_cfv'],np.resize(np.roll(pattern,-epoch%16),len(after['d_cfv']))),'all physical clobber words')
        req(int(np.count_nonzero(before['d_cfv']!=after['d_cfv']))==proof['changed_words']>0,'all changed counts')
        for name in inventory-{'d_cfv','CFV_logical'}:req(eq(before[name],after[name]),'all other fields unchanged by seed')
        del before,after
        bi,ci=phase['baseline_info'],phase['candidate_info'];normalized=dict(ci);normalized['wrapper_bytes']=bi['wrapper_bytes'];normalized['packet_module_loaded']=bi['packet_module_loaded']
        req(bi==normalized,'geometry/graphs exact apart from declared host wrapper/module');wrapperpairs.add((bi['wrapper_bytes'],ci['wrapper_bytes']))
        b=gpu(O/f'baseline-{ident:02}-{stage}.gpu.bin',bi);c=gpu(O/f'candidate-{ident:02}-{stage}.gpu.bin',ci)
        regen=stage not in retained;req(phase['CFV_regenerated']==regen,'declared regeneration')
        for name in inventory-{'d_cfv'}:
            if name=='CFV_logical' and not regen:continue
            req(eq(b[name],c[name]),'all phase learning/reach/immutable/logical words exact')
        regenerated+=regen;phases+=1;del b,c
    rb_stages=['strategy-sync','full-sync','prelock-full','before-save','resumed-full-sync']+(['continuation-final'] if continuation else [])
    req([x['stage'] for x in row['readbacks']]==rb_stages,'every forced readback')
    for item in row['readbacks']:
        stage,proof=item['stage'],item['proof'];readbacks+=1
        expected_handle=dims[0]=='Compressed' and min(proof['CFV_words'],proof['pinned_words'])>=65544
        req(proof['forced_packed_path']==proof['expected_from_fixture_format_and_current_capacity']==expected_handle,'actual forced activation')
        req(proof['production_min_source_bytes']==16777216 and proof['internal_control_min_source_bytes']==0 and proof['packet_prefix_words']==65544,'fixed production rule and control-only size override')
        if ident<16 and not expected_handle:coverage_misses.append({'case':ident,'stage':stage,'pinned_words':proof['pinned_words'],'CFV_words':proof['CFV_words']})
        before=np.fromfile(O/f'pinned-{ident:02}-{stage}-before.u32',dtype='<u4');after=np.fromfile(O/f'pinned-{ident:02}-{stage}-after.u32',dtype='<u4')
        req(len(before)==len(after)==proof['pinned_words'] and bool(np.all(before==0x5a5a5a5a)),'all pinned initial words')
        if expected_handle:
            req(bool(np.all(after[65544:]==0x5a5a5a5a)) and proof['pinned_tail_guard_words']==len(after)-65544,'every pinned tail guard')
            req(proof['module_loaded_after'],'actual module retained for handled path');handled+=1;pinnedguards+=len(after)-65544
        else:
            req(not proof['module_loaded_before'] and not proof['module_loaded_after'],'all fallback paths retain zero optional module');declined+=1
        b=gpu(O/f'pinned-{ident:02}-{stage}-before.gpu.bin',proof['GPU_info']);c=gpu(O/f'pinned-{ident:02}-{stage}-after.gpu.bin',proof['GPU_info'])
        for name in inventory-{'d_cfv','CFV_logical'}:req(eq(b[name],c[name]),'all65 actual arrays exact before/after readback')
        if not expected_handle:req(eq(b['d_cfv'],c['d_cfv']),'declined original readback leaves physical scratch unchanged')
        del b,c,before,after
    print('D155 retained reader case',ident,'complete',flush=True)
pairs=constructors=cpu=0
for p in sorted(O.glob('baseline-*')):
    if p.name.endswith('.gpu.bin'):continue
    q=O/p.name.replace('baseline-','candidate-',1);req(p.read_bytes()==q.read_bytes(),'every whole CPU/query/save/constructor file');pairs+=1
    if p.name.endswith('-constructor.bin'):
        a=frame(p,b'D155-FRAME-v1\0\0\0');b=frame(q,b'D155-FRAME-v1\0\0\0');req(len(a)==len(b)==66 and set(a)==set(b) and all(eq(a[k],b[k]) for k in a),'all66 actual constructor fields');constructors+=1
    elif p.name.endswith('.cpu.bin'):
        a=frame(p,b'D155-STATE-v1\0\0\0');b=frame(q,b'D155-STATE-v1\0\0\0');req(set(a)==set(b) and all(eq(a[k],b[k]) for k in a),'all CPU q/scale/publication state words');cpu+=1
req(epoch==phases==752 and regenerated==608 and roots==32 and evs==324 and constructors==36 and readbacks==188,'whole fixed control inventory')
coverage_gates={'all16_main_compressed_cases_really_activate':not coverage_misses,'at_least84_actual_packet_readbacks':handled>=84,'at_least80_declines':declined>=80,'nonzero_pinned_guard_coverage':pinnedguards>0}
req(not all(coverage_gates.values()),'original coverage failure remains failed')
h.custody();D=ROOT/'comparisons/D155-coverage-failure';D.mkdir(exist_ok=False)
report={'id':'D155','at':h.now(),'status':'incomplete_expected_activation_coverage', 'original_protocol_coverage_gates':coverage_gates, 'coverage_misses':coverage_misses, 'original_cohort_passed':False, 'original_raw_and_audit_unchanged':True, 'retained_review_sha256':h.sha(__file__),'protocol_sha256':h.sha(H/'protocol.json'),'binary_sha256':h.sha(H/'probe.exe'),'cases':36,'phase_pairs':phases,'CFV_clobbers':epoch,'regenerated_logical_CFV_pairs':regenerated,'constructor_pairs':constructors,'exploitability_pairs':evs,'continuation_root_pairs':roots,'forced_readbacks':readbacks,'actual_packet_path_readbacks':handled,'original_declines_in_forced_controls':declined,'ordinary_public_decline_calls':72,'all65_arrays_exact_across_each_forced_readback':True,'all_CPU_q_scale_query_save_resume_files_exact':True,'all66_constructor_images_match_CPU_references':True,'CPU_query_save_constructor_file_pairs':pairs,'CPU_frame_pairs':cpu,'raw_frames':frames,'represented_raw_words':words,'logical_CFV_words_checked':logicalwords,'physical_CFV_words_retained':physicalwords,'actual_pinned_tail_guard_words_checked':pinnedguards,'reader_checks':checks,'actual_baseline_candidate_wrapper_bytes':sorted(wrapperpairs),'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_measurement':False,'candidate_accepted':False,'scope':'Original native0/audit1 retained. This is a complete retained-word review with original coverage gates recorded FAILED, not a cohort pass or candidate admission. No new native run, source variant, cases, samples or thresholds. Compact packed engine behavior remains missing. Fixed36case engine matrix, broader asymmetric turn ranges ensure actual checked capacity for forcing the same packed implementation below16MiB. Production admission remains frozen. Full persistent device/CPU/query/save/resume/EV/root words exact, physical scratch retained with logical equality only after regeneration; every pinned tail word and actual direct source immutability checked. No large primary/holdout, physical peak/capacity, runtime error injection, actual paged wrapper or complete-cycle timing qualification.'}
h.save(D/'report.json',report);print({k:report[k] for k in ['status','original_cohort_passed','cases','actual_packet_path_readbacks','raw_frames','reader_checks','original_protocol_coverage_gates']},flush=True)
