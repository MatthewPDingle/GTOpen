"""File-only terminal audit; no imports or execution of candidate scripts/native code."""
from pathlib import Path
import datetime, hashlib, json, re, struct
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
P=ROOT/'runs/E030-fold-card-order-exact'
OUT=Path(__file__).resolve().parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
pins={};checks=0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    pins[str(p)]=sha(p)
    return json.loads(p.read_text(encoding='utf-8'))
def ck(v,why):
    global checks
    checks+=1
    assert v,why
def pin(p,h):ck(sha(p)==h,str(p));pins[str(p)]=h
def fnv(data):
    h=0xcbf29ce484222325
    for v in data:h=((h^v)*0x100000001b3)&0xffffffffffffffff
    return f'{h:016x}'
def wordhash(v):return fnv(struct.pack('<'+str(len(v))+'I',*v))
def finite(v):return v&0x7f800000!=0x7f800000
def nonfinite(v):return {'count':sum(not finite(w) for w in v),'first_16':[{'index':i,'bits':f'{w:08x}'} for i,w in enumerate(v) if not finite(w)][:16]}
def entry(ptx,name):
    start=re.search(r'\.visible\s+\.entry\s+'+re.escape(name)+r'\(',ptx).start()
    i=ptx.index('{',start);depth=1;j=i+1
    while depth:
        depth+=(ptx[j]=='{')-(ptx[j]=='}');j+=1
    return ptx[start:j]
m=read(P/'prepared-manifest.json');ck(pins[str(P/'prepared-manifest.json')]=='cb0cd4ca8b23c2b35781be5d41e320ccad9914f9b9b1ef92766fcee3bc3bacf9','prepared seal')
for n,h in m['artifact_sha256'].items():pin(P/n,h)
for group in ['references','dependency_rlibs']:
    for v in m[group].values():pin(Path(v['path']),v['sha256'])
for n,h in m['protected_checkout_sha256'].items():pin(REPO/n,h)
proto=read(P/'protocol.json');corpus=read(P/'corpus.json');summary=read(P/'corpus-summary.json');report=read(P/'report.json');ex=read(P/'execution-manifest.json')
started=read(P/'execution-started.json');pre=read(P/'preflight.json');launch=read(P/'launch-preflight.json')
commands=[read(P/(n+'.command.json')) for n in ['rustc','probe']]
ck(commands==report['commands'],'actual commands equal report')
ck(all(c['returncode']==0 and c['cleanup'] is None and c['timeout_seconds']==600 for c in commands),'terminal zero commands')
ck(commands[0]['args']==ex['compile_command'],'rustc exact recorded argv')
ck(commands[1]['args']==[str(P/'probe.exe')],'only direct native argv')
end=datetime.datetime.fromisoformat(commands[0]['started_at'])+datetime.timedelta(seconds=commands[0]['elapsed_seconds'])
ck(end<=datetime.datetime.fromisoformat(commands[1]['started_at']),'serial compile before native')
ck(ex['prepared_manifest_sha256']==started['prepared_manifest_sha256']==pins[str(P/'prepared-manifest.json')],'execution bindings')
ck(ex['input_sha256_before']==report['input_sha256_after']==m['artifact_sha256'],'input pre/post maps')
ck(pre['free_bytes']>=pre['minimum_free_reserve_bytes']+pre['output_reservation_bytes'],'admission reserve')
for state in [pre['live_status'],launch]:
    ck(state['/api/status']['state']=='idle' and state['/api/preflop/status']['state'] not in ['solving','running'] and state['/api/reports/status']['running'] is False,'recorded live idle')
for n,h in ex['nvrtc_dll_sha256'].items():pin(Path(ex['nvrtc_directory'])/n,h)
pin(Path(ex['rustc_executable']),ex['rustc_executable_sha256'])
pin(P/'probe.exe',report['binary_sha256']);pin(P/'raw-results.jsonl',report['raw_results_sha256'])
binary=(P/'probe.exe').read_bytes()
for n in ['baseline.cu','candidate.cu','corpus.json']:ck((P/n).read_bytes() in binary,'embedded '+n)
ck(not (P/'failure.json').exists(),'no failure artifact')
for n in ['rustc.stdout.log','rustc.stderr.log','probe.stdout.log','probe.stderr.log','baseline.ptx','candidate.ptx','baseline-up_fold.ptx','candidate-up_fold.ptx']:
    pins[str(P/n)]=sha(P/n)
ck((P/'probe.stderr.log').stat().st_size==0 and (P/'rustc.stderr.log').stat().st_size==0,'empty stderr logs')
lines=(P/'probe.stdout.log').read_text(encoding='utf-8').splitlines();ck(all(l.startswith('E030_DIRECT_EXACT ') for l in lines),'only expected stdout marker')
rows=[json.loads(l[len('E030_DIRECT_EXACT '):]) for l in lines]
ck([r['stage'] for r in rows]==proto['expected_stages'] and len(rows)==183,'fixed183 markers')
ck(rows==report['records'] and rows[-1]==report['complete'],'raw/report records exact')
hc,device=rows[:2];ck(hc['expected_bit_injection_rejected'] and hc['guard_injection_rejected'] and hc['metadata_validated'],'harness self checks')
ck(hc['corpus_fnv1a64']==fnv((P/'corpus.json').read_bytes()),'embedded corpus identity')
ck(device['device']=='NVIDIA GeForce RTX 5090' and device['architecture']=='compute_120' and device['production_block']==128 and device['tested_blocks']==[128,16,32,64,256],'actual device/shapes')
for res in device['resources']:
    sv=m['source_variants'][res['variant']]
    ck(res['source_fnv1a64']==sv['fnv1a64'] and res['source_bytes']==sv['bytes'],'actual CUDA identity')
    ck(res['max_threads_per_block']>=256 and res['static_shared_bytes']+1326*4<=device['max_shared_bytes_per_block_default'],'capacity only')
scenarios={s['id']:s for s in corpus['full_scenarios']};cases=[];input_hashes={}
def padded(v):return v or [corpus['guard_bits']]
for sc in corpus['full_scenarios']:
    off=sc['card_off'];packed=sc['candidate_card_off'];order=sorted(range(52),key=lambda c:(-(off[c+1]-off[c]),c))
    ck(len(off)==53 and len(packed)==105 and packed[:53]==off and packed[53:]==order,'complete metadata permutation')
    for c in range(52):ck(sc['card_idx'][off[c]:off[c+1]]==[i for i,h in enumerate(sc['opponent_hands']) if c in h],'original hand order')
    for variant in ['baseline','candidate']:
        values={'nodes':sc['nodes'],'owner':[v['owner'] for v in sc['node_meta']],'twin':[v['twin_bits'] for v in sc['node_meta']],'tlose':[v['tlose_bits'] for v in sc['node_meta']], 'rsrc0':sc['rsrc0'],'rsrc1':sc['rsrc1'],'reach0':sc['reach0_bits'],'reach1':sc['reach1_bits'],'pc1':padded(sc['pc1']),'pc2':padded(sc['pc2']),'card_off':off if variant=='baseline' else packed,'card_idx':padded(sc['card_idx']),'same_p':padded(sc['same_p']),'cfv_slot':sc['cfv_slot']}
        input_hashes[sc['id'],variant]=[(k,len(v),wordhash(v)) for k,v in values.items()]
    for block in [128,16,32,64,256]:
        for player in [0,1]:
            for count in ([sc['count'],0] if sc['id']=='n0-own1' else [sc['count']]):cases.append((sc['id'],block,player,count))
ck(len(cases)==180,'fixed180 pairs')
totals=dict(comparison_pairs=180,kernel_launches=360,active_words_per_arm=0,required_finite_words_per_arm=0,required_nonzero_words=0,output_guard_checks_both_arms=0,input_buffer_checks_both_arms=0,input_word_checks_both_arms=0)
output_words=0;overflow_nonfinite=0
with (P/'raw-results.jsonl').open(encoding='utf-8') as raw:
    for pos,(sid,block,player,count) in enumerate(cases):
        sc=scenarios[sid];a=json.loads(next(raw));b=json.loads(next(raw));row=rows[pos+2]
        expected_id={'scenario':sid,'block':block,'p':player,'count':count}
        for value in [a,b,row]:ck(all(value[k]==v for k,v in expected_id.items()),'same fixed pair order')
        ck(a['variant']=='baseline' and b['variant']=='candidate' and a['scope']==b['scope']=='full_up_fold','two actual full kernels')
        av,bv=a['output_bits'],b['output_bits'];ck(len(av)==len(bv)==sc['cfv_words'] and av==bv,'all complete output bits exact')
        active={}
        for node in sc['nodes'][sc['start']:sc['start']+count]:
            for hand in range(sc['nh_p']):
                at=sc['cfv_slot'][node]*sc['nh_max']+hand
                assert at not in active and 0<=at<sc['cfv_words'];active[at]=sc['node_meta'][node]['required']
        ck(all(type(v) is int and 0<=v<=0xffffffff for v in av),'raw u32 output domain')
        ck(all(v==corpus['guard_bits'] for i,v in enumerate(av) if i not in active),'all output guards')
        req=[av[i] for i,r in active.items() if r];overflow=[av[i] for i,r in sorted(active.items()) if not r]
        ck(all(finite(v) for v in req),'finite-domain output contract')
        changed=sum(v!=corpus['guard_bits'] for v in req);nz=sum(v!=corpus['guard_bits'] and v&0x7fffffff!=0 for v in req)
        ck(not req or changed>0,'nonvacuous finite output')
        ck(row['required_words']==len(req) and row['active_words']==len(active) and row['required_changed_words']==changed and row['required_nonzero_words_excluding_stale_guard']==nz,'exact row counts')
        ck(row['optional_bit_mismatches']==0 and row['optional_baseline_nonfinite']==row['optional_candidate_nonfinite']==nonfinite(overflow),'overflow bits/stats exact')
        ck(row['baseline_hash']==wordhash(av) and row['candidate_hash']==wordhash(bv),'actual output record hashes')
        ck(row['guard_words_checked_per_variant']==sc['cfv_words']-len(active) and row['all_input_buffers_bitwise_immutable'] is True and row['device_input_buffer_checks']==28,'guard/input markers')
        pairwords=0
        for image in [a,b]:
            expected=input_hashes[sid,image['variant']];observed=image['input_readbacks'];ck(len(observed)==14,'all14 readbacks')
            for rec,(name,n,h) in zip(observed,expected):
                ck(rec['name']==name and rec['words']==n and rec['expected_fnv1a64']==rec['actual_fnv1a64']==h,'actual device input hash/count');pairwords+=n
        exp=summary['fixed_pair_order'][pos]
        ck(all(exp[k]==v for k,v in expected_id.items()) and exp['input_words_both_arms']==pairwords and exp['active_words']==len(active) and exp['required_words']==len(req) and exp['guard_words_per_arm']==sc['cfv_words']-len(active),'fixed corpus counts')
        totals['active_words_per_arm']+=len(active);totals['required_finite_words_per_arm']+=len(req);totals['required_nonzero_words']+=nz;totals['output_guard_checks_both_arms']+=2*(sc['cfv_words']-len(active));totals['input_buffer_checks_both_arms']+=28;totals['input_word_checks_both_arms']+=pairwords
        output_words+=len(av);overflow_nonfinite+=sum(not finite(v) for v in overflow)
    ck(next(raw,None) is None,'exactly360 raw images, no extras')
ck(totals==rows[-1]['totals'] and totals['required_nonzero_words']>0,'independent complete totals')
for k,v in summary['totals'].items():ck((output_words if k=='output_words_per_arm' else totals[k])==v,'frozen expected total '+k)
ck(overflow_nonfinite==report['nonfinite_overflow_words_per_arm'],'all overflow retained')
ptx={v:(P/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate']}
names=['copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action','copy_span','up_action_eval']
for v in ptx:ck(re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx[v])==names,'nine actual entries')
abi={n:entry(ptx['baseline'],n).split('{',1)[0]==entry(ptx['candidate'],n).split('{',1)[0] for n in names};unchanged={n:entry(ptx['baseline'],n)==entry(ptx['candidate'],n) for n in names if n!='up_fold'}
ck(all(abi.values()) and abi==report['all_entry_abi_exact'],'all9 ABI exact');ck(all(unchanged.values()) and unchanged==report['other_eight_entry_ptx_exact'],'other8 PTX exact')
for v in ptx:ck((P/(v+'-up_fold.ptx')).read_text(encoding='utf-8')==entry(ptx[v],'up_fold')+'\n','exact retained fold PTX')
ck(report['status']=='completed_exact_complete_up_fold_comparison' and report['comparison_pairs']==180 and report['kernel_launches']==360,'terminal report')
for k in ['performance_measurement','candidate_accepted','deployment_changed']:ck(report[k] is False,'scope '+k)
ck(report['prepared_manifest_sha256']==pins[str(P/'prepared-manifest.json')] and report['protocol_sha256']==m['protocol_sha256'],'terminal bindings')
for v in ['baseline','candidate']:ck(report[v+'_cuda_sha256']==m['source_variants'][v]['sha256'],'terminal source '+v)
validation={'id':'E030-direct','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_EXACT_COMPLETE_UP_FOLD_COMPARISON','exactness_pass':True,'numerical_validation':'executed','prepared_manifest_sha256':pins[str(P/'prepared-manifest.json')],'source_manifest_sha256':m['source_manifest_sha256'],'protocol_sha256':m['protocol_sha256'],'baseline_cuda_sha256':m['source_variants']['baseline']['sha256'],'candidate_cuda_sha256':m['source_variants']['candidate']['sha256'],'production_threads':128,'block_shapes':[128,16,32,64,256],'each_pair_same_block_shape':True,'comparison_pairs':180,'kernel_launches':360,'recomputed_totals':totals,'output_words_per_arm':output_words,'overflow_nonfinite_words_per_arm':overflow_nonfinite,'other_eight_ptx_entries_exact':unchanged,'all_nine_ptx_abis_exact':abi,'checks_passed':checks,'actual_resource_metadata':device['resources'],'file_only_audit':True,'reviewer_native_compiler_gpu_executions':0,'candidate_accepted':False,'performance_measurement':False,'deployment_changed':False,'limits':['Fixed actual full-kernel finite-input corpus only; overflow-derived observed bits all retained and exact, no NaN-input generalization.','Supplemental shapes compare each same shape; no cross-shape equality or speed assertion.','Input readbacks were directly byte-compared by the reviewed Rust harness; retained per-buffer hashes/counts independently match frozen host words.','Host constructor/accounting, full solver lifecycle and complete-cycle performance remain separate qualification gates.'],'input_sha256':pins}
with (OUT/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(validation,f,indent=2);f.write('\n')
print(json.dumps({'verdict':validation['verdict'],'checks':checks,'totals':totals,'overflow_nonfinite_words_per_arm':overflow_nonfinite,'validation_sha256':sha(OUT/'validation.json')},indent=2))
