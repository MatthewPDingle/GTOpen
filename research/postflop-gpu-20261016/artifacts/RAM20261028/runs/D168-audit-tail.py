excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms','runtime_nvrtc_jit_included'}
logs={};actual_workers={};unique_CPU=set();unique_GPU=set();science=checkpoint=0
for row in P['sequence']:
    ident=row['id'];workers=row['workers'];text=(H/'execution'/(ident+'.stdout.log')).read_text(encoding='utf-8')
    results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
    stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_STAGE ' in x]
    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
    req(len(results)==3 and all(x['runtime_nvrtc_jit_included'] is False for x in results),'honestprebuilt diagnostictelemetry')
    req([[{k:v for k,v in x.items() if k not in excluded} for x in results],conv]==[[{k:v for k,v in x.items() if k not in excluded} for x in anchor[0]],anchor[1]],'alloriginal fullscience/stop/quality/config/state/checkpointfields')
    science+=len(results);checkpoint+=len(conv)
    pools=[json.loads(x.split('D168_POOL ',1)[1]) for x in text.splitlines() if x.startswith('D168_POOL ')]
    req(pools==[{'actual':workers,'requested':workers,'observation_after_entire_suite_and_lifecycle':True}],'actualpool matchesrequestedafterallwork');actual_workers[ident]=workers
    req(text.index('D168_POOL ')>text.rindex('D156_CONTROL ') and text.index('D168_POOL ')>text.rindex('AUTORESEARCH_RESULT '),'poolqueryafterallsuite/results/lifecycle')
    req(len([x for x in text.splitlines() if x=='D166_BIND baseline'])==6,'all6sealedE080bindings')
    req('test result: ok. 1 passed; 0 failed; 0 ignored;' in text,'terminalnativepass')
    controls=[json.loads(x.split('D156_CONTROL ',1)[1]) for x in text.splitlines() if x.startswith('D156_CONTROL ')]
    req([x['fixture_id'] for x in controls]==['rainbow','two-tone','river'],'fixedfixtureorder');logs[ident]=controls
    resource=h.read(H/'execution'/(ident+'.resource.json'));req(resource['reported_peak_working_set_bytes']<=P['limits']['process_reported_peak_max_bytes'] and resource['reported_peak_commit_bytes']<=P['limits']['process_reported_peak_max_bytes'],'reportedprocesscaps');req(resource['minimum_observed_available_RAM_bytes']>=P['limits']['available_RAM_during_bytes'],'availableRAMguard')
    inv=h.read(H/'execution'/(ident+'.invocation.json'));req(inv['output_env']['RAYON_NUM_THREADS']==str(workers),'actualchildenvironment')
cpu=gpu=query=save=evs=0
for ident in ['workers8','workers32']:
    for b,c in zip(logs['reference16'],logs[ident]):
        name=b['fixture_id'];req(name==c['fixture_id'] and b['all_GPU_and_CPU_objects_dropped'] and c['all_GPU_and_CPU_objects_dropped'],'sameterminalfixtures')
        req(b['stages']==c['stages'] and [x['stage'] for x in b['stages']]==P['lifecycle_stages'],'allfutureEV/iteration/devicegeometry/graph/hoststate descriptors exact')
        for bs,cs in zip(b['stages'],c['stages']):
            stage=bs['stage'];bo=H/'reference16-output';co=H/(ident+'-output')
            if bs['ev_bits'] is not None:req(math.isfinite(struct.unpack('<d',struct.pack('<Q',bs['ev_bits']))[0]),'finitefutureEV');evs+=1
            a,z=bo/f'{name}-{stage}.cpu.bin',co/f'{name}-{stage}.cpu.bin';pair(a,z);cpu_frame(a,bs['iteration']);cpu_frame(z,cs['iteration']);cpu+=1;unique_CPU.update([str(a),str(z)])
            a,z=bo/f'{name}-{stage}.gpu.bin',co/f'{name}-{stage}.gpu.bin';pair(a,z);gpu_frame(a,bs['info']);gpu_frame(z,cs['info']);gpu+=1;unique_GPU.update([str(a),str(z)])
            print('D168 raw reader',ident,name,stage,'exact',flush=True)
        for stage in ['locked','resumed']:pair(H/'reference16-output'/f'{name}-{stage}.query.json',H/(ident+'-output')/f'{name}-{stage}.query.json');query+=1
        pair(H/'reference16-output'/f'{name}.save',H/(ident+'-output')/f'{name}.save');save+=1
req(science==9 and checkpoint==69 and len(unique_CPU)==len(unique_GPU)==36,'allunique scientificrecords andcompleteframes')
req(cpu==gpu==24 and query==12 and save==6 and evs==18,'allpredeclared referencecomparisons')
raw_bytes=sum(p.stat().st_size for d in H.glob('*-output') for p in d.iterdir() if p.is_file());req(raw_bytes<=P['limits']['raw_reservation_bytes'],'rawreservation');req(len(hashes)==99,'whole99retainedfilescompared')
h.custody();D=ROOT/'comparisons/D168-worker-raw-control';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D168','at':h.now(),'status':'pass_actual_worker_counts_and_full_canonical_raw_state','protocol_sha256':h.sha(H/'protocol.json'),'actual_workers':actual_workers,'unique_full_records_exact':science,'unique_checkpoints_exact':checkpoint,'unique_CPU_frames':len(unique_CPU),'unique_GPU69field_frames':len(unique_GPU),'CPU_pairs_vs16':cpu,'GPU_pairs_vs16':gpu,'query_pairs_vs16':query,'save_pairs_vs16':save,'future_EV_pairs_vs16':evs,'pair_bytes_compared':pair_bytes,'represented_words_including_replayed_reference':represented_words,'reader_checks':checks,'raw_output_bytes':raw_bytes,'whole_compared_file_sha256':hashes,'actual_pool_observed_only_after_all_work':True,'all_cpu_q_scales_and_entire_device_buffers_CFVs_exact':True,'all_owned_children_terminal':True,'source_main_live_protected_PTX_custody_pass':True,'performance_qualification_samples':0,'configuration_accepted':False,'scope':'FiniteacceptedE080canonicalDCFR/compressed/iso/lifecyclematrix8/16/32workers. Queryactualpoolafterentiresuite/lifecycle/destructors;no poolpreinitializationorclockchange. AllCPUq/scalesandall66devicebuffers/entirephysicalCFV/hoststate/query/save/futureEVbytes exactvs16. Originalscience/stops/checkpoints exact. TimesprebuiltPTX+heavyobserversdiagnostic/unscored. Timingwithrealruntimecompile,freshconfirmation,broadnonpostflop/material/capacity/holdout/adoptionstillrequired.'})
print(json.dumps({'status':'pass_config_raw_controls','workers':actual_workers,'records':science,'checkpoints':checkpoint,'pair_bytes':pair_bytes,'checks':checks}),flush=True)
