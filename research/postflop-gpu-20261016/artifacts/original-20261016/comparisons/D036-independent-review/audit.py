import pathlib, hashlib, json, datetime, collections, struct, re, math
ROOT=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016')
P=ROOT/'runs/D036-fold-shuffle-probe-r3'; R2=ROOT/'runs/D036-fold-shuffle-probe-r2'
OUT=ROOT/'comparisons/D036-independent-review'; PRIOR=ROOT/'comparisons/D036-numeric-protocol-review'
REPO=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016')
checks=collections.Counter()
def ck(ok,label):
    if not ok: raise AssertionError(label)
    checks[label]+=1
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def fnv(data):
    h=0xcbf29ce484222325
    for b in data: h=((h^b)*0x100000001b3)&0xffffffffffffffff
    return f'{h:016x}'
def wh(words): return fnv(struct.pack('<%dI'%len(words),*words))
def finite(v): return v&0x7f800000 != 0x7f800000
def nf(words):
    vals=[{'index':i,'bits':f'{v:08x}'} for i,v in enumerate(words) if not finite(v)]
    return {'count':len(vals),'first_16':vals[:16]}
def bits(v):
    try: return struct.unpack('<I',struct.pack('<f',v))[0]
    except OverflowError: return 0xff800000 if v<0 else 0x7f800000
def flt(v): return struct.unpack('<f',struct.pack('<I',v))[0]
def add(a,b): return bits(flt(a)+flt(b))
def cpu(data,block):
    partial=[0]*block
    for lane in range(block):
        for v in data[lane::block]: partial[lane]=add(partial[lane],v)
    step=block//2
    while step:
        for lane in range(step): partial[lane]=add(partial[lane],partial[lane+step])
        step//=2
    return partial[0]
M=load(P/'prepared-manifest.json'); C=load(P/'corpus.json'); E=load(PRIOR/'runtime-expected-matrix.json'); R=load(P/'report.json'); X=load(P/'execution-manifest.json')
ck(sha(P/'prepared-manifest.json')=='b0fd45d3bceffb9fb5ba6de294dc3af3ede144a1707cd3ceacbd616e0e4d8279','sealed_r3_manifest')
ck(sha(PRIOR/'runtime-expected-matrix.json')=='68421e9a94be1e4184c554e1836b8b4243586631f7750aa56f5d2ab352b549b7','sealed_prospective_matrix')
for n,h in M['artifact_sha256'].items(): ck(sha(P/n)==h,'prepared_artifact_hash')
for d in M['dependency_rlibs'].values(): ck(sha(pathlib.Path(d['path']))==d['sha256'],'dependency_hash')
for n,h in M['protected_checkout_sha256'].items(): ck(sha(REPO/n)==h,'protected_accepted_source_hash')
ck(X['input_sha256_before']==R['input_sha256_after']==M['artifact_sha256'],'unchanged_before_after_inputs')
for d in [X,R,load(P/'execution-started.json')]: ck(d['prepared_manifest_sha256']==sha(P/'prepared-manifest.json'),'manifest_link')
ck(sha(P/'probe.exe')==R['binary_sha256'],'actual_binary_hash')
ck(sha(P/'raw-results.jsonl')==R['raw_results_sha256'],'raw_result_hash')
for n,h in X['nvrtc_dll_sha256'].items(): ck(sha(pathlib.Path(X['nvrtc_directory'])/n)==h,'nvrtc_dll_hash')
ck(not (P/'failure.json').exists(),'no_r3_failure_artifact')
for n in ['probe.stderr.log','rustc.stderr.log','rustc.stdout.log']: ck((P/n).stat().st_size==0,'empty_success_errorlogs')
cmds=[load(P/'rustc.command.json'),load(P/'probe.command.json')]
ck(cmds==R['commands'],'exact_command_records');ck(len(cmds)==2 and all(d['returncode']==0 for d in cmds),'one_compile_one_native_success')
ck(cmds[0]['args']==X['compile_command'],'frozen_compile_command')
ck(cmds[1]['args']==[str(P/'probe.exe')],'native_binary_path')
ck(all(d['timeout_seconds']==600 and d['cleanup'] is None for d in cmds),'no_timeout_or_child_cleanup')
start=[datetime.datetime.fromisoformat(d['started_at']) for d in cmds]
ck(start[1]>=start[0]+datetime.timedelta(seconds=cmds[0]['elapsed_seconds']),'build_precedes_probe')
failed=load(P/'failed-r2-evidence.json')
for n,d in failed['files'].items(): ck(sha(R2/n)==d['sha256'] and (R2/n).stat().st_size==d['bytes'],'r2_failure_artifact_preserved')
f=load(R2/'failure.json');ck(len(f['commands'])==1 and f['commands'][0]['returncode']==1 and f['commands'][0]['args'][0]=='rustc','r2_compile_only_failure')
ck(not (R2/'probe.exe').exists() and (R2/'rustc.stderr.log').read_text().count('error[E0277]')==62,'r2_no_native_case')
rows=[]
for line in (P/'probe.stdout.log').read_text().splitlines():
    ck(line.startswith('D036_PROBE '),'stdout_only_known_marker'); rows.append(json.loads(line[len('D036_PROBE '):]))
ck(rows==R['records'],'stdout_exact_report_records')
ck(dict(collections.Counter(r['stage'] for r in rows))==E['stage_counts'],'all_expected_stages')
expected_stages=['harness_checks']+['resource']*8+['raw_total_exact']*5+['full_fold_exact']*180+['complete']
ck([r['stage'] for r in rows]==expected_stages,'fixed_stage_order')
ck(rows[-1]==R['complete'],'complete_matches_terminal_stdout')
ck(rows[0]['expected_bit_injection_rejected'] and rows[0]['guard_injection_rejected'] and not rows[0]['counts_as_gpu_numerical_case'],'harness_rejects_bad_bit_and_guard')
ck(rows[0]['corpus_fnv1a64']==fnv((P/'corpus.json').read_bytes()),'runtime_corpus_identity')
resources=[r for r in rows if r['stage']=='resource']
for r,e in zip(resources,E['resource_rows']):
    for k,v in e.items(): ck(r[k]==v,'fixed_resource_matrix')
    ck((r['registers'],r['local_bytes_per_thread'],r['static_shared_bytes'],r['max_threads_per_block'],r['occupancy_blocks_per_sm_128'])==(39,0,1232,1024,12),'actual_resources')
    ck(r['device']=='NVIDIA GeForce RTX 5090' and r['architecture']=='compute_120','actual_device_architecture')
    ck(r['source_fnv1a64']==M['source_variants'][r['source_variant']]['fnv1a64'] and r['source_bytes']==M['source_variants'][r['source_variant']]['bytes'],'runtime_cuda_source_identity')
    ck(not r['performance_measurement'],'no_resource_timing_claim')
raw_markers={r['block']:r for r in rows if r['stage']=='raw_total_exact'}
full_markers=[r for r in rows if r['stage']=='full_fold_exact']
rawcounts=collections.Counter(); stats=collections.Counter(); nfstats=collections.Counter(); guard=C['guard_bits']
rawfile=(P/'raw-results.jsonl').open(encoding='utf-8')
def nxt(scope):
    line=next(rawfile); r=json.loads(line);ck(r['scope']==scope,'raw_row_order');rawcounts[scope]+=1;return r
for block in E['block_order']:
    outs=[]
    for variant in ['baseline','candidate']:
        d=nxt('raw_total');ck((d['block'],d['variant'])==(block,variant),'raw_block_variant_order'); a=d['output_bits'];ck(len(a)==676,'raw_output_length')
        for i,v in enumerate(a):
            if i not in range(2,674,3): ck(v==guard,'raw_guard_word');stats['raw_guard_word_checks']+=1
        outs.append(a)
    ck(outs[0]==outs[1],'raw_full_image_exact')
    mr=raw_markers[block]
    ck(wh(outs[0])==mr['baseline_hash']==mr['candidate_hash'],'raw_image_hash')
    ck(nf(outs[0])==mr['baseline_nonfinite']==mr['candidate_nonfinite'],'raw_nonfinite_summary')
    ck(mr['input_immutable'] and mr['guards_checked']==452 and mr['required_cases']==208 and mr['optional_cases']==16 and mr['optional_bit_mismatches']==0,'raw_marker_obligations')
    for i,case in enumerate(C['raw_cases']):
        d=nxt('raw_total_case');a=outs[0][2+3*i];b=outs[1][2+3*i]
        ck((d['id'],d['block'],d['required'])==(case['id'],block,case['required']),'raw_case_identity')
        ck(a==b==d['baseline_bits']==d['candidate_bits'],'mandatory_raw_case_exact')
        ck(d['baseline_finite']==d['candidate_finite']==finite(a),'raw_finiteness')
        stats['raw_pairs']+=1
        if case['required']:
            oracle=cpu(case['bits'],block)
            ck(finite(a) and a==oracle==d['cpu_same_tree_bits'],'independent_cpu_f32_raw_total');stats['finite_cpu_raw_pairs']+=1
        else:
            stats['mandatory_overflow_raw_pairs']+=1
            nfstats['raw_overflow_nonfinite']+=not finite(a)
            nfstats['raw_overflow_inf']+=((a&0x7fffffff)==0x7f800000)
            nfstats['raw_overflow_nan']+=((a&0x7fffffff)>0x7f800000)
scenarios={s['id']:s for s in C['full_scenarios']}; full_summary=[]
for e,mr in zip(E['full_rows'],full_markers):
    s=scenarios[e['scenario']];active={}; n=e['count']
    for node in s['nodes'][s['start']:s['start']+n]:
        for hand in range(s['nh_p']):
            pos=s['cfv_slot'][node]*s['nh_max']+hand;ck(pos not in active,'distinct_output_ownership');active[pos]=s['node_meta'][node]['required']
    ck(len(active)==e['all_active_words'] and sum(active.values())==e['required_finite_words'],'expected_full_active_matrix')
    outs=[]
    for variant in ['baseline','candidate']:
        d=nxt('full_up_fold')
        for k in ['scenario','p','block','count']: ck(d[k]==e[k],'fixed_full_order')
        ck(d['variant']==variant,'full_variant_order');a=d['output_bits'];ck(len(a)==e['output_words'],'full_output_length')
        guards=[v for i,v in enumerate(a) if i not in active];ck(len(guards)==e['guard_words_per_variant'] and all(v==guard for v in guards),'all_full_guard_words');stats['full_guard_word_checks']+=len(guards)
        outs.append(a)
    ck(outs[0]==outs[1],'mandatory_full_entire_image_exact')
    ck(wh(outs[0])==mr['baseline_hash']==mr['candidate_hash'],'full_image_hash')
    for k in ['scenario','p','block','count','nh_p','nh_o','dynamic_shared_bytes']: ck(mr[k]==e[k],'full_marker_configuration')
    required=[v for i,v in enumerate(outs[0]) if active.get(i) is True]; overflow=[v for i,v in enumerate(outs[0]) if active.get(i) is False]
    ck(all(finite(v) for v in required),'required_full_all_finite')
    changed=sum(v!=guard for v in required); nonzero=sum(v!=guard and (v&0x7fffffff)!=0 for v in required)
    ck(mr['required_words']==len(required)==e['required_finite_words'] and mr['required_changed_words']==changed and mr['required_nonzero_words_excluding_stale_guard']==nonzero,'full_antivacuity_counts')
    ck(not required or changed>0,'full_actual_active_writes')
    ck(mr['optional_baseline_nonfinite']==mr['optional_candidate_nonfinite']==nf(overflow),'full_overflow_nonfinite_summary')
    ck(mr['optional_bit_mismatches']==0 and mr['all_input_buffers_bitwise_immutable'] and mr['guard_words_checked_per_variant']==e['guard_words_per_variant'] and not mr['performance_measurement'],'full_marker_obligations')
    stats['full_pairs']+=1;stats['full_active_word_pairs']+=len(active);stats['finite_full_word_pairs']+=len(required);stats['mandatory_overflow_full_word_pairs']+=len(overflow);stats['finite_full_changed_words']+=changed;stats['finite_full_nonzero_words']+=nonzero
    stats['zero_count_pairs']+=n==0;stats['zero_own_hand_pairs']+=s['nh_p']==0
    nfstats['full_overflow_nonfinite']+=sum(not finite(v) for v in overflow);nfstats['full_overflow_inf']+=sum((v&0x7fffffff)==0x7f800000 for v in overflow);nfstats['full_overflow_nan']+=sum((v&0x7fffffff)>0x7f800000 for v in overflow)
    full_summary.append({**{k:e[k] for k in ['scenario','block','p','count']},'hash':mr['baseline_hash'],'all_active_words':len(active),'finite_changed_words':changed,'overflow_nonfinite':nf(overflow)['count']})
ck(rawfile.read()=='','raw_file_no_extra_rows');rawfile.close()
ck(dict(rawcounts)=={'raw_total':10,'raw_total_case':1120,'full_up_fold':360},'exact_raw_counts')
for k,v in {'raw_pairs':1120,'finite_cpu_raw_pairs':1040,'mandatory_overflow_raw_pairs':80,'full_pairs':180,'full_active_word_pairs':1771280,'finite_full_word_pairs':1644760,'mandatory_overflow_full_word_pairs':126520,'full_guard_word_checks':5969780,'raw_guard_word_checks':4520,'zero_count_pairs':10,'zero_own_hand_pairs':10}.items():ck(stats[k]==v,'recomputed_totals')
complete=R['complete']
ck(complete['required_nonzero_words']==stats['finite_full_nonzero_words'] and complete['required_full_output_words']==stats['finite_full_word_pairs'],'terminal_recomputed_counts')
ck(complete['kernel_launches']==370 and complete['raw_kernel_launches']==10 and complete['full_kernel_launches']==360,'launch_counts')
ck(complete['all_observed_gpu_bits_exact'] and complete['required_exact'] and complete['input_immutability'] and complete['output_guards'],'terminal_exact_obligations')
ck(not complete['candidate_accepted'] and not complete['performance_measurement'] and complete['solver_executions']==0 and not complete['nan_input_payload_guarantee'],'terminal_scope')
def entries(text):
    found={}
    for match in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',text):
        begin=text.index('{',match.end());depth=1;end=begin+1
        while depth:
            depth+=(text[end]=='{')-(text[end]=='}');end+=1
        found[match.group(1)]=text[match.start():end]
    return found
ptx={n:entries((P/(n+'.ptx')).read_text()) for n in ['baseline','candidate','raw-baseline','raw-candidate']}
ck(set(ptx['baseline'])==set(ptx['candidate']) and len(ptx['baseline'])==9,'same_nine_full_entrypoints')
for name in ptx['baseline']:
    if name!='up_fold':ck(ptx['baseline'][name]==ptx['candidate'][name] and R['other_entry_ptx_byte_equality'][name],'other_entry_ptx_exact')
for variant in ptx:
    name='raw_total' if variant.startswith('raw-') else 'up_fold';s=ptx[variant][name]
    ck(hashlib.sha256(s.encode()).hexdigest()==R['ptx'][variant]['entry_sha256'],'ptx_entry_hash')
    ck(s==(P/(variant+'-'+name+'.ptx')).read_text(),'saved_ptx_entry_exact')
ck(len(re.findall(r'\bshfl\.sync\.down\.b32\b',ptx['candidate']['up_fold']))==5,'five_static_shuffle_sites')
ck('shfl.sync.down.b32' not in ptx['baseline']['up_fold'],'baseline_no_static_shuffle')
files={str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in P.iterdir() if p.is_file()}
for name in ['frozen-protocol-validation.json','runtime-expected-matrix.json','r2-provenance-supplement.json','r3-provenance-supplement.json']:
    p=PRIOR/name;files[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size}
report={'id':'D036-independent-runtime-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS bounded standalone numerical and resource probe; eligible to propose a separately qualified solver candidate','review_actions':'CPU-only parsing/recomputation of preserved evidence; no build, GPU call, source or dashboard mutation','prepared_manifest_sha256':sha(P/'prepared-manifest.json'),'binary_sha256':sha(P/'probe.exe'),'raw_results_sha256':sha(P/'raw-results.jsonl'),'checks':dict(checks),'check_assertions':sum(checks.values()),'stats':dict(stats),'observed_overflow_outputs_per_baseline_candidate_pair':dict(nfstats),'resource_rows':resources,'all_eight_other_entrypoints_exact':True,'full_case_output_summaries':full_summary,'fixed_seed':C['seed_hex'],'fixed_blocks':C['blocks'],'all_planned_cases_retained':True,'r2_failed_compile':{'returncode':1,'e0277_count':62,'native_cases':0,'all_28_files_preserved':True},'r3_execution':{'compiler_seconds':cmds[0]['elapsed_seconds'],'probe_process_seconds':cmds[1]['elapsed_seconds'],'one_compile_one_native':True,'not_performance_evidence':True},'input_immutability_evidence':{'full_input_buffer_comparisons':360*14,'raw_input_buffer_comparisons':10*3,'basis':'Frozen successful native code compares every device input after each variant; markers confirm completion. Device input readback images are not separately persisted, so these are not independently recomputed from saved images.'},'limits':['Finite constructed corpus, not proof for all finite inputs or NaN/Inf input payloads','Mandatory finite-overflow output bits match, with nonfinite counts retained; no overflow exemptions','Independent CPU oracle covers finite-domain raw totals only; full compiled accepted kernel remains full-CFV oracle','No solver lifecycle, complete-cycle timing, candidate acceptance or speedup claim','Registers/static PTX/occupancy and whole probe duration are diagnostic metadata, not native solver speed'], 'input_artifacts':files}
with (OUT/'validation.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'verdict':report['verdict'],'checks':sum(checks.values()),'stats':dict(stats),'overflow':dict(nfstats),'validation_sha256':sha(OUT/'validation.json')},indent=2))
