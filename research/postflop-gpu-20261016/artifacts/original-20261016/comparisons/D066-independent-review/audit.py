"""Independent post-terminal, file-only D066 audit. No package imports or native work."""
from pathlib import Path
import collections,hashlib,json,re,struct,subprocess,datetime
B=Path(r'S:\GTOpen-research\postflop-gpu-20261016'); H=B/'runs/D066-fold-zero-census'; O=Path(__file__).parent; R=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
pins={};checks=[]
def ck(v,n):
 if not v: raise AssertionError(n)
 checks.append(n)
def sha(p):
 p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p)]=h;return h
def load(p,h=None):
 a=sha(p)
 if h:ck(a==h,'pin '+str(p))
 return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pinmap(m,base=H):
 for p,h in m.items():ck(sha(Path(p) if Path(p).is_absolute() else base/p)==h,'pin '+p)
def fnv(data):
 v=0xcbf29ce484222325
 for b in data:v=((v^b)*1099511628211)&((1<<64)-1)
 return f'{v:016x}'
def records(text,prefix):return [json.loads(x.split(prefix,1)[1]) for x in text.splitlines() if prefix in x]
def tally(rows,flags,p):
 c=collections.Counter(fold_ctas=0,all_positive_zero=0,any_negative_zero=0,any_finite_nonzero=0,any_nonfinite=0,finite_selected_amount=0,all_positive_zero_and_finite_amount=0)
 for row in rows:
  f=flags[row[2-p]];finite=(row[3+p]&0x7f800000)!=0x7f800000
  c.update(fold_ctas=1,all_positive_zero=int(f==0),any_negative_zero=int(bool(f&1)),any_finite_nonzero=int(bool(f&2)),any_nonfinite=int(bool(f&4)),finite_selected_amount=int(finite),all_positive_zero_and_finite_amount=int(f==0 and finite))
 return dict(c)
def write(n,j):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(j if isinstance(j,str) else json.dumps(j,indent=2,allow_nan=False)+'\n')
seal=load(H/'scripts-manifest.json','f7bf21efd733c81061fed48b2627e643bb19173cedd05fe9f931cb4bf84834fa')
for k in ['script_sha256','reference_sha256']:pinmap(seal[k])
source=load(H/'source/source-manifest.json','0df9774c514a3ad3260b96ee219e6154ac8f402307912dd6130f84e8111e2748');pinmap(source['artifact_sha256'],H/'source')
p=load(H/'protocol.json');schema=load(H/'source/output-schema.json');anchors=load(H/'design/anchors.json')
auth=load(H/'authorization.json','88e00cbf8d42f9aa2fcc5e68d4ba8db423b2d7b33319d726d8088e0607d6fc64');pinmap(auth['evidence_sha256'])
ck(auth['candidate']=='D066' and all(auth[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'root authorization scope')
for v in auth['prerequisites'].values():ck(sha(v['path'])==v['sha256'],'root review prerequisite')
accepted=load(B/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256'];expected=accepted|source['candidate_sha256'];ck(len(accepted)==162 and len(expected)==163,'162 accepted /163 diagnostic maps')
activation=load(B/'runs/D066-source/activation.json');ck(activation['source_before']['source_sha256']==accepted and activation['source_after']['source_sha256']==expected and activation['authorization_sha256']==sha(H/'authorization.json'),'exact two-file activation')
manifest=load(B/'binaries/D066-solver.manifest.json');ck(manifest['source_sha256']==expected==load(B/'runs/D066-build/source-before.json')['source_sha256'],'complete frozen build source map')
ck(manifest['candidate']=='D066' and manifest['source_matches_prebuild'] and manifest['test_only_append_verified'],'test-only build source custody')
ck(manifest['probe_authorization_sha256']==sha(H/'authorization.json') and manifest['probe_evidence_sha256']==auth['evidence_sha256'] and manifest['primary_protocol_sha256']==sha(H/'protocol.json') and manifest['build_script_sha256']==sha(H/'build.py'),'build authorization/script/protocol pins')
for n,v in manifest['source_copies'].items():ck(sha(v['path'])==v['sha256']==source['candidate_sha256'][n],'archived source '+n)
ck(set(manifest['source_copies'])==set(source['candidate_sha256']),'all two candidate files archived')
for k,hk in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:ck(sha(manifest[k])==manifest[hk],'build artifact '+k)
ck(manifest['patch_sha256']==sha(H/'source/candidate.patch'),'complete helper patch archived')
bexit=load(B/'runs/D066-build/exit.json');benv=load(B/'runs/D066-build/build-environment.json')
ck(bexit['returncode']==0 and bexit['error'] is None and bexit['cleanup'] is None,'terminal build0')
ck(bexit['command']==['cargo','test','--release','--locked','--offline','-p','solver','--features','gpu','--lib','--no-run','--message-format=json'],'fixed compile-only command')
ck(benv['target_previously_absent'] and benv['compiler_override_absence']=={} and benv['RAYON_NUM_THREADS']=='16','fresh build and compiler overrides absent')
cargo=[json.loads(x) for x in Path(manifest['build_log']).read_text().splitlines() if x.strip()]
ck(cargo[-1]=={'reason':'build-finished','success':True},'Cargo terminal success')
ck(not any(x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error' for x in cargo),'no compiler diagnostic error')
arts=[x for x in cargo if x.get('reason')=='compiler-artifact']
for x in arts:
 for f in x.get('filenames',[])+([x['executable']] if x.get('executable') else []):ck(Path(f).resolve().is_relative_to(Path(p['build_target_root']).resolve()),'fresh artifact path '+f)
units=[x for x in arts if x.get('executable') and x['target']['name']=='solver' and x['profile']['test']]
ck(len(units)==1 and units[0]==manifest['cargo_artifact'] and units[0]['fresh'] is False and set(units[0]['features'])=={'gpu'},'one fresh gpu-only solver test artifact')
ck(Path(units[0]['manifest_path']).resolve()==(R/'crates/solver/Cargo.toml').resolve() and Path(units[0]['target']['src_path']).resolve()==(R/'crates/solver/src/lib.rs').resolve(),'solver Cargo/source path')
binary=Path(p['binary']);ck(sha(binary)=='5262304b3c8c23e9a6bcdd680f1eda63abfd51bdf6a8999411cb9f68edaa4cf0'==manifest['binary_sha256']==sha(units[0]['executable']),'frozen fresh executable identity')
blob=binary.read_bytes();cuda=(R/'crates/solver/src/gpu/kernels.cu').read_bytes();ck(cuda in blob and b'D066_FOLD_ZERO_CENSUS' in blob,'accepted CUDA and diagnostic marker embedded');del blob
native=load(B/'runs/D066R1/report.json');raw_path=B/'runs/D066R1/stdout.log';ck(sha(raw_path)==native['stdout_sha256'],'native rawlog pin');raw=raw_path.read_text(encoding='utf-8')
inv=load(B/'runs/D066-execution/invocation.json');ex=load(B/'runs/D066-execution/exit.json');complete=load(B/'runs/D066-execution/complete.json')
ck(ex['returncode']==native['returncode']==0 and ex['error'] is None and ex['cleanup'] is None and complete['native_test_pass'],'single native terminal0')
ck(native['id']==inv['actual_run']==complete['actual_run']=='D066R1' and native['kind']=='diagnostic' and native['fixture'] is None and native['status']=='measured' and native['test_pass_count']==1,'fixed single run identity')
ck(native['command']==[str(binary),p['test_filter'],'--nocapture','--test-threads=1','--ignored'],'only exact ignored diagnostic test')
ck(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')],'exact1/0/0/0/88 inventory')
ck(not any(x in raw for x in ['D066_SOLVER_CLEANUP_ERROR','D066 invalid diagnostic','panicked at','test result: FAILED']),'no native cleanup/panic failure')
ck(native['binary_sha256']==inv['binary_sha256']==manifest['binary_sha256'],'build/run executable identity')
ck(native['binary_build_manifest']['data']==manifest and native['binary_build_manifest']['sha256']==inv['build_manifest_sha256']==sha(B/'binaries/D066-solver.manifest.json'),'embedded manifest exact')
ck(native['provenance']['source_sha256']==inv['source_sha256']==expected,'actual run source163 custody')
ck(inv['authorization_sha256']==sha(H/'authorization.json') and inv['protocol_sha256']==sha(H/'protocol.json') and inv['script_sha256']==sha(H/'run.py'),'actual runner frozen inputs')
ck(activation['at']<=bexit['at']<=inv['at']<=native['process_started_at']<=native['finished_at']<=ex['at'],'build before native chronology')
expected_env={'D066_CENSUS_DIR':p['census_directory'],'POSTFLOP_AUTORESEARCH_FIXTURE':None,'POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE':None,'POSTFLOP_AUTORESEARCH_PROFILE':'0','POSTFLOP_AUTORESEARCH_STORAGE':'compressed','RAYON_NUM_THREADS':'16'}
ck(inv['run_env']==expected_env,'exact runtime environment')
for k in ['RAYON_NUM_THREADS','POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE']:ck(native['environment'][k]==expected_env[k],'native env '+k)
for n in ['stdout.log','stderr.log']:sha(B/'runs/D066-execution'/n)
ck(not (B/'runs/D066-execution/stderr.log').read_text().strip(),'wrapper stderr empty')
for key in ['live_status_before','live_status_at_launch']:
 v=native[key];ck(not v['/api/status']['gpu'] and not v['/api/preflop/status']['gpu'] and not v['/api/reports/status']['running'],'recorded live idle '+key)
rec=records(raw,p['marker']);ck([{'stage':x['stage'],**({'fixture_id':x['fixture_id']} if 'fixture_id' in x else {}),**({'iteration':x['iteration']} if 'iteration' in x else {})} for x in rec]==schema['expected_stage_order'] and len(rec)==39,'all39 fixed markers/order')
ck(not records(raw,'AUTORESEARCH_RESULT '),'no benchmark result or timing cohort')
census=Path(p['census_directory']);catalog=load(B/'runs/D066-execution/census-artifacts.json',complete['census_artifacts_sha256'])
ck(set(catalog['files'])==set(schema['expected_files'])=={x.name for x in census.iterdir()} and len(catalog['files'])==15,'exact15 compact files')
for n,v in catalog['files'].items():
 f=census/n;ck(f.is_file() and not f.is_symlink() and f.resolve().parent==census.resolve() and f.stat().st_size==v['bytes'] and sha(f)==v['sha256'],'compact SHA/size '+n)
assessment=load(B/'comparisons/D066-fold-zero-census/report.json','240336229464e41c57267bc3b4ae72ff4618ce668bb7c70ba07b079a04b59642')
ck(assessment['status']=='pass' and assessment['exactness_pass'] and assessment['census_validation_pass'],'terminal assessment passes')
observations=[];total_words=0
for a in anchors:
 fid=a['fixture_id'];r=[x for x in rec if x.get('fixture_id')==fid];g=next(x for x in r if x['stage']=='geometry');ad=next(x for x in r if x['stage']=='admission');ass=next(x for x in assessment['fixtures'] if x['fixture_id']==fid)
 ck(g['nodes']==a['nodes'] and g['nh']==a['nh'] and g['uploaded_metadata_exact_both_arms'] and not g['physical_reach_has_padding'],'native verified logical geometry '+fid)
 ck(all(type(x)is int and x>0 for x in g['nh']+g['reach_blocks']),'positive geometry '+fid)
 spans=g['fold_spans'];cursor=0
 for i,x in enumerate(spans):ck(x['level']==i and x['start']==cursor and type(x['count'])is int and x['count']>=0,'contiguous span '+fid+str(i));cursor+=x['count']
 ck(cursor==g['fold_ctas_per_traverser'],'actual flattened fold coverage '+fid)
 m=g['mapping'];data=(census/m['file']).read_bytes();ck(m['file']==fid+'-fold-mapping.u32le' and len(data)==m['bytes']==cursor*20 and fnv(data)==m['fnv1a64'],'mapping codec/FNV '+fid)
 rows=list(struct.iter_unpack('<IIIII',data));ck(all(n<g['nodes'] and s0<g['reach_blocks'][0] and s1<g['reach_blocks'][1] for n,s0,s1,_,_ in rows),'mapping bounds '+fid)
 ck(ad['dual_device_required_with_reserve']==2*ad['device_per_arm_payload_bytes']+2*(1<<30)<=ad['device_free_bytes']<=ad['device_total_bytes'],'two-arm GPU admission '+fid)
 ck(ad['cpu_arena_bytes_per_arm']==sum(v['bytes'] for v in a['state_fingerprint']['arenas']) and ad['pinned_bytes_per_arm']==4*max(ad['device_arena_elements']),'separate CPU/pinned lengths '+fid)
 geom=20*cursor+8*len(spans)+max(g['reach_blocks']);required=2*ad['cpu_arena_bytes_per_arm']+2*ad['pinned_bytes_per_arm']+(8<<20)+geom+(8<<30)
 ck(ad['compact_geometry_and_rowclass_bytes']==geom and ad['host_additional_required']==required<=ad['host_free_after_spot_and_plan'] and ad['host_free_before_spot']>=16*(1<<30),'host admission arithmetic '+fid)
 ck([{'iteration':x['iteration'],'exploit_bits':x['exploit_bits']} for x in r if x['stage']=='checkpoint']==a['convergence'],'all immutable convergence bits '+fid)
 ck(all(x['ordinary_and_observed_exact'] and x['immutable_original_and_E020_anchor_exact'] for x in r if x['stage']=='checkpoint'),'native both-arm anchors '+fid)
 final=next(x for x in r if x['stage']=='final_anchor_exact');ck(final['state_fingerprint']==a['state_fingerprint'] and final['complete_cpu_q_and_scale_bits_exact'] and final['cleanup_complete'],'full final CPU-state/native cleanup '+fid)
 for snap in [x for x in r if x['stage']=='snapshot']:
  it=snap['iteration'];ck(snap['before_exploitability'] and snap['paired_reach_bits_exact'] and not snap['raw_float_payload_retained'] and not snap['performance_measurement'] and snap['chunk_floats']==1048576 and snap['peak_float_snapshot_bytes']==8388608,'fixed pre-eval snapshot '+fid+str(it))
  ck([(x['opponent'],x['traverser']) for x in snap['arrays']]==[(0,1),(1,0)],'both traversers '+fid+str(it))
  for arr in snap['arrays']:
   q=arr['opponent'];player=1-q;nh=g['nh'][q];nr=g['reach_blocks'][q];total_words+=nh*nr
   ck(arr['entries']==nh*nr and arr['logical_nh']==nh and arr['physical_rows']==nr and arr['paired_bits_exact'],'full logical-row coverage '+fid+str((it,q)))
   rc=arr['rowclass'];flags=(census/rc['file']).read_bytes();ck(rc['file']==f'{fid}-iteration{it}-reach{q}.rowflags' and len(flags)==rc['bytes']==nr and fnv(flags)==rc['fnv1a64'] and all(v<8 for v in flags),'rowflag exact codec '+rc['file'])
   hist=collections.Counter(flags);wc=arr['whole_reach_word_categories'];ck(set(wc)=={'positive_zero','negative_zero','finite_nonzero','nonfinite'} and all(type(x)is int and x>=0 for x in wc.values()) and sum(wc.values())==nh*nr,'disjoint whole-buffer word totals')
   ck(wc['positive_zero']>=hist[0]*nh,'positivezero word/row bound')
   for bit,name in [(1,'negative_zero'),(2,'finite_nonzero'),(4,'nonfinite')]:
    k=sum(v for flag,v in hist.items() if flag&bit);ck(k<=wc[name]<=k*nh,'independent row/word bounds '+name)
   counted=tally(rows,flags,player);ck(counted==arr['fold_counts'],'independently recomputed aggregate '+rc['file'])
   level_counts=[dict(x,counts=tally(rows[x['start']:x['start']+x['count']],flags,player)) for x in spans];ck(level_counts==arr['levels'],'independently recomputed every level '+rc['file'])
   ck(all(sum(v['counts'][k] for v in level_counts)==counted[k] for k in counted),'levels sum to aggregate '+rc['file'])
   reported=next(x for ss in ass['snapshots'] if ss['iteration']==it for x in ss['arrays'] if x['opponent']==q)
   ck(reported['fold_counts']==counted and reported['physical_row_flag_histogram']=={str(k):hist.get(k,0) for k in range(8)} and reported['whole_reach_word_categories']==wc,'assessor independent result agreement '+rc['file'])
   observations.append({'fixture_id':fid,'iteration':it,'traverser':player,'opponent':q,'fold_ctas':cursor,'all_positive_zero':counted['all_positive_zero'],'finite_amount_eligible':counted['all_positive_zero_and_finite_amount'],'fraction':counted['all_positive_zero']/cursor,'counts':counted,'physical_row_flags':dict(sorted(hist.items()))})
ck(total_words==assessment['native_paired_reach_words_compared'],'reported native raw word comparison coverage')
ck(rec[-1]=={'stage':'complete','fixtures':3,'snapshots':6,'reach_array_snapshots':12,'checkpoints':23,'final_full_state_checks':3,'mapping_files':3,'rowclass_files':12,'performance_measurement':False,'candidate_accepted':False},'terminal complete exact')
for k,v in [('marker_count',39),('compact_file_count',15),('checkpoint_count',23),('snapshot_count',6),('final_full_state_checks',3)]:ck(assessment[k]==v,'assessment count '+k)
ck(all(assessment[k] is False for k in ['performance_measurement','candidate_accepted','deployment_changed','extension_allowed']),'no performance/adoption/extension')
cleanup=load(B/'runs/D066-cleanup/report.json')
ck(cleanup['status']=='restored' and cleanup['all162_accepted_entries_exact'] and cleanup['temporary_helper_removed_after_preservation'],'root exact restoration')
ck(cleanup['source_before']['source_sha256']==expected and cleanup['source_after']['source_sha256']==accepted,'custody before and after restoration')
ck(cleanup['assessment_sha256']==sha(B/'comparisons/D066-fold-zero-census/report.json') and cleanup['build_exit_sha256']==sha(B/'runs/D066-build/exit.json') and cleanup['execution_exit_sha256']==sha(B/'runs/D066-execution/exit.json'),'cleanup terminal outcome pins')
for n,v in cleanup['preserved_candidate_sources'].items():ck(sha(v['path'])==v['sha256']==source['candidate_sha256'][n],'cleanup candidate preservation '+n)
ck(set(cleanup['preserved_candidate_sources'])==set(source['candidate_sha256']),'both candidate copies preserved')
pinmap(accepted,R);ck(not (R/'crates/solver/src/gpu/fold_zero_census.rs').exists(),'temporary helper absent')
ck(cleanup['preexisting_target_artifacts']==p['preexisting_target_artifacts'],'two exact preexisting PTX pins')
for n,v in p['preexisting_target_artifacts'].items():ck(sha(R/n)==v['sha256'] and (R/n).stat().st_size==v['bytes'],'PTX preserved '+n)
live=Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe');ck(sha(live)==cleanup['live_exe_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','exact live desktop binary unchanged')
main_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r'X:\Dev\GTOpen',text=True).strip();ck(main_head=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
ck(cleanup['live_before']==cleanup['live_after'] and cleanup['compiler_and_native_terminal'] and cleanup['no_extra_samples'],'root cleanup/idle/noextra evidence')
ck(ex['at']<=cleanup['at'],'restoration after terminal native')
write('report.json',{'id':'D066','verdict':'PASS_SCOPED_CENSUS_AUDIT','independent_terminal_audit_pass':True,'exactness_pass':True,'incidence_recomputation_pass':True,'custody_and_cleanup_pass':True,'observations':observations,'marker_count':39,'compact_file_count':15,'checkpoint_count':23,'final_full_state_checks':3,'native_paired_reach_words_compared':total_words,'test_summary':dict(passed=1,failed=0,ignored=0,measured=0,filtered_out=88),'binary_sha256':manifest['binary_sha256'],'assessment_sha256':pins[str(B/'comparisons/D066-fold-zero-census/report.json')],'cleanup_sha256':pins[str(B/'runs/D066-cleanup/report.json')],'limits':['File-level mapping/rowflag incidence and selected payout finiteness were independently recomputed. Raw reach floats and complete CPU q/scales were not retained; paired bitwise and full-store equality are supported by pinned native checks and anchors, not FNV alone.','All positive-zero inputs do not imply positive-zero outputs or safe omitted stores. Finite payout eligibility is separate.','These six snapshots establish neither all-iteration frequency nor kernel cost, dynamic work shares, speedup or complete-cycle headroom. No optimization accepted.'],'checks':checks,'input_sha256':pins,'reviewer_compiler_native_gpu_execution':False,'performance_measurement':False,'candidate_accepted':False,'deployment_changed':False,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
summary='D066 terminal audit passes: one native invocation,39markers,15compact files,23immutable checkpoints and3final full states. All per-level and aggregate counts independently recomputed. Current162 E020 sources, both generated PTX files and exact live desktop executable remain unchanged after restoration.\n\n|Fixture|Iteration|Traverser|All +0 CTAs|Total CTAs|Incidence|\n|---|---:|---:|---:|---:|---:|\n'
for x in sorted(observations,key=lambda x:(['rainbow','two-tone','river'].index(x['fixture_id']),x['iteration'],x['traverser'])):summary+=f"|{x['fixture_id']}|{x['iteration']}|{x['traverser']}|{x['all_positive_zero']}|{x['fold_ctas']}|{x['fraction']*100:.6f}%|\n"
summary+='\nEvery selected payout was finite. No negative-zero or nonfinite row flags were observed in these retained snapshots. Incidence is not a timing share, predicted saving or fast-path correctness proof. Raw floats/full CPU stores were checked by pinned native code but not retained for replay.\n'
write('summary.md',summary)
write('manifest.json',{'id':'D066-independent-review','verdict':'PASS_SCOPED_CENSUS_AUDIT','artifact_sha256':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in ['audit.py','preparation.md','report.json','summary.md']}})
print(json.dumps({'checks':len(checks),'pins':len(pins),'native_paired_reach_words_compared':total_words,'report_sha256':sha(O/'report.json'),'manifest_sha256':sha(O/'manifest.json')}))
