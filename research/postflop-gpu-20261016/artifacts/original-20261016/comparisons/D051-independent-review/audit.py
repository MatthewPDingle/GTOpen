"""Independent D051 terminal audit; reads evidence only, never imports/runs probe code."""
import bisect, datetime, hashlib, itertools, json, re, struct, traceback
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
R=ROOT/'runs/D051-show-physical256-exact'
OUT=Path(__file__).parent
inputs={}; checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def ok(name,value):
 if not value:raise AssertionError(name)
 checks.append(name)
def pin(p,h=None):
 p=Path(p);actual=sha(p)
 if h is not None:ok('pin:'+str(p),actual==h)
 inputs[str(p)]=actual
 return actual
def fnv(b):
 h=0xcbf29ce484222325
 for v in b:h=((h^v)*0x100000001b3)&0xffffffffffffffff
 return f'{h:016x}'
def words_hash(v):return fnv(struct.pack('<'+'I'*len(v),*v))
def entry(s,n):
 m=re.search(r'\.visible\s+\.entry\s+'+re.escape(n)+r'\(',s);ok('entry exists:'+n,m is not None)
 start=s.index('{',m.start());end=start+1;level=1
 while level:
  if s[end]=='{':level+=1
  elif s[end]=='}':level-=1
  end+=1
 return s[m.start():end]
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def audit():
 prepared_hash=pin(R/'prepared-manifest.json','99ee2d3fb6e718177e1d576c9af88dc801a24396073998e04954b2ac080961d2')
 pin(ROOT/'comparisons/D051-source-script-review/report.json','c07388eb7c398680c9faa11d0a033a579f2ad0bda60dc2ef3a2d111d581ae42c')
 prep=j(R/'prepared-manifest.json');report=j(R/'report.json');protocol=j(R/'protocol.json')
 for n,h in prep['artifact_sha256'].items():pin(R/n,h)
 for info in prep['references'].values():pin(info['path'],info['sha256'])
 for info in prep['dependency_rlibs'].values():pin(info['path'],info['sha256'])
 protected=prep['protected_checkout_sha256'];ok('162 source entries',len(protected)==162)
 accepted=j(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
 ok('protected map is accepted E020',protected==accepted)
 for n,h in protected.items():pin(REPO/n,h)
 for n in ['report.json','execution-started.json','execution-manifest.json','preflight.json','launch-preflight.json','rustc.command.json','probe.command.json','rustc.stdout.log','rustc.stderr.log','probe.stdout.log','probe.stderr.log','raw-results.jsonl','baseline.ptx','candidate.ptx','baseline-up_show.ptx','candidate-up_show.ptx','probe.exe','root-execution-review.json']:pin(R/n)
 earlier=ROOT/'comparisons/D051-corpus-source-review/draft-pin-refusal.json'
 if earlier.exists():pin(earlier)
 ex=j(R/'execution-manifest.json');start=j(R/'execution-started.json');rootreview=j(R/'root-execution-review.json')
 ok('frozen inputs before/after',ex['input_sha256_before']==report['input_sha256_after']==prep['artifact_sha256'])
 ok('manifest binding',all(x['prepared_manifest_sha256']==prepared_hash for x in [report,ex,start,rootreview]))
 for n,h in ex['nvrtc_dll_sha256'].items():pin(Path(ex['nvrtc_directory'])/n,h)
 pin(ex['rustc_executable'],ex['rustc_executable_sha256'])
 binary=(R/'probe.exe').read_bytes()
 ok('binary hash',sha(R/'probe.exe')==report['binary_sha256'])
 ok('raw hash',sha(R/'raw-results.jsonl')==report['raw_results_sha256'])
 ok('embedded sealed CUDA and corpus',all((R/n).read_bytes() in binary for n in ('baseline.cu','candidate.cu','corpus.json')))
 ok('accepted evaluator exact',(R/'accepted-evaluator.rs').read_bytes()==(REPO/'crates/solver/src/evaluator.rs').read_bytes())
 code=(R/'probe.rs').read_text(encoding='utf-8')
 ok('rank precheck precedes context',code.index('for g in gs{validate_geometry(g)?;}')<code.index('let ctx=CudaContext::new(0)?'))
 ok('actual accepted rank assertion','assert_eq!(strengths[i],r,"frozen independent rank differs from accepted evaluate7")' in code)
 rust=j(R/'rustc.command.json');native=j(R/'probe.command.json')
 ok('two terminal commands',report['commands']==[rust,native] and rust['returncode']==native['returncode']==0 and rust['cleanup'] is None and native['cleanup'] is None)
 ok('exact compile command',rust['args']==ex['compile_command'] and rust['args'][0:3]==['rustc','probe.rs','--edition=2021'])
 ok('only original native invocation',native['args']==[str(R/'probe.exe')] and native['cwd']==rust['cwd']==str(R))
 ok('chronology',dt(prep['at'])<=dt(rootreview['at'])<=dt(start['at'])<=dt(rust['started_at']) and dt(rust['started_at'])+datetime.timedelta(seconds=rust['elapsed_seconds'])<=dt(native['started_at']))
 ok('timeouts unchanged',native['timeout_seconds']==rust['timeout_seconds']==600)
 ok('no native stderr',(R/'probe.stderr.log').stat().st_size==0)
 ok('no failure artifact',not(R/'failure.json').exists())
 pre=j(R/'preflight.json');launch=j(R/'launch-preflight.json')
 ok('reserve admission',pre['free_bytes']>=pre['minimum_free_reserve_bytes']+pre['output_reservation_bytes'])
 for tag,live in [('pre',pre['live_status']),('launch',launch)]:
  ok(tag+' idle solve',live['/api/status']['state']!='running' and live['/api/preflop/status']['state']!='running' and live['/api/reports/status']['running'] is False)
 rows=[json.loads(line[len('D051_EXACT '):]) for line in (R/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('D051_EXACT ')]
 raw=[json.loads(line) for line in (R/'raw-results.jsonl').read_text(encoding='utf-8').splitlines()]
 ok('151 ordered markers',[r['stage'] for r in rows]==['corpus_validated','device']+['full_show_exact']*148+['complete'])
 ok('raw/report matches markers',rows==report['records'] and len(raw)==148)
 ok('rank precheck marker',rows[0]=={'accepted_rank_oracle':True,'comparison_pairs':148,'geometries':36,'host_injections_are_gpu_cases':False,'host_verifier_injections_rejected':2,'stage':'corpus_validated'})
 device=rows[1]
 ok('device and width identity',device['device']=='NVIDIA GeForce RTX 5090' and device['architecture']=='compute_120' and (device['baseline_physical_threads'],device['candidate_physical_threads'],device['logical_scan_threads'])==(128,256,128))
 ok('production compile options',device['compile_options']=='arch only, all other production defaults')
 for v in ['baseline','candidate']:
  b=(R/(v+'.cu')).read_bytes();sv=prep['source_variants'][v]
  ok(v+' source bits',sha(R/(v+'.cu'))==sv['sha256']==report[v+'_cuda_sha256'] and len(b)==sv['bytes'] and fnv(b)==sv['fnv1a64']==device[v+'_source_fnv1a64'])
 ptx={v:(R/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate']}
 names=re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx['baseline'])
 ok('same9 entry identities',len(names)==9 and names==re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx['candidate']))
 for v in ptx:
  old=Path(prep['references']['D050_'+v+'_ptx']['path']).read_text(encoding='utf-8')
  for n in names:ok(v+' D050 PTX:'+n,entry(ptx[v],n)==entry(old,n))
  ok(v+' saved up_show',entry(ptx[v],'up_show')+'\n'==(R/(v+'-up_show.ptx')).read_text(encoding='utf-8'))
  ok(v+' no FTZ','.ftz' not in entry(ptx[v],'up_show'))
 for n in names:
  if n!='up_show':ok('unchanged entry:'+n,entry(ptx['baseline'],n)==entry(ptx['candidate'],n))
 ok('show ABI exact',entry(ptx['baseline'],'up_show').split('{',1)[0]==entry(ptx['candidate'],'up_show').split('{',1)[0])
 corpus=j(R/'corpus.json');gs={g['id']:g for g in corpus['geometries']};cases=corpus['cases']
 boards=['Ks7h2dQhTc','AsKsQsJsTs'];counts=[0,1,127,128,129,255,256,257,1081];profiles=['all_zero','sparse_rounding_witness','seeded_ordinary','subnormal_mixed_scales']
 ids=[f'{b}-m{m}-p{p}-{f}' for b,m,p,f in itertools.product(boards,counts,[0,1],profiles)]+[f'{b}-m257-p{p}-seeded_ordinary-count0' for b,p in itertools.product(boards,[0,1])]
 ok('fixed corpus/order',len(gs)==36 and [c['id'] for c in cases]==ids and [r['case_id'] for r in rows[2:-1]]==ids)
 for g in gs.values():
  a=g['arrays'];hp=g['hands_p'];ho=g['hands_o'];board=set(g['board'])
  sp=sorted((s,i) for i,s in enumerate(g['strengths_p']) if s!=0xffffffff);so=sorted((s,i) for i,s in enumerate(g['strengths_o']) if s!=0xffffffff)
  ok('orientation:'+g['id'],(len(sp),len(so))==((257,g['target_m']) if g['player']==0 else(g['target_m'],257)))
  ok('legal roots:'+g['id'],all(len(h)==len(set(h))==2 and all(0<=c<52 for c in h) and not(set(h)&set(g['board'][:3])) for h in hp+ho) and len({tuple(h) for h in hp})==len(hp) and len({tuple(h) for h in ho})==len(ho))
  ok('rank sentinel maps:'+g['id'],all((s==0xffffffff)==bool(set(h)&board) for hs,ss in [(hp,g['strengths_p']),(ho,g['strengths_o'])] for h,s in zip(hs,ss)))
  strengths=[s for s,i in so]
  ok('sorted indices:'+g['id'],a['p_idx'][5:5+len(sp)]==[i for s,i in sp] and a['o_idx'][7:7+len(so)]==[i for s,i in so])
  ok('bounds:'+g['id'],a['p_lower'][5:5+len(sp)]==[bisect.bisect_left(strengths,s) for s,i in sp] and a['p_upper'][5:5+len(sp)]==[bisect.bisect_right(strengths,s) for s,i in sp])
  ok('card position lists:'+g['id'],all(a['o_card_pos'][a['o_card_off'][53+c]:a['o_card_off'][54+c]]==[k for k,(s,i) in enumerate(so) if c in ho[i]] for c in range(52)))
  ok('same hand mapping:'+g['id'],a['same_p'][:len(hp)]==[ho.index(h) if h in ho else 0xffffffff for h in hp])
  ok('row mask:'+g['id'],all(bool(mask)==any(a['cfv_slot'][n]*g['nh_max']<=i<a['cfv_slot'][n]*g['nh_max']+g['nh_p'] for n in [2,5]) for i,mask in enumerate(g['output_active'])))
  ok('capacity:'+g['id'],g['dynamic_shared_bytes']==4*g['nh_o']+16*g['m_o'] and g['dynamic_shared_bytes']+1040<=device['max_shared_bytes_per_block_default'] and device['max_threads_per_block']>=256)
 totals={k:0 for k in ['active_words','guard_word_checks','device_input_buffer_checks','device_input_word_checks','active_overwritten_words','nonzero_active_words']};witnesses=[];nonfinite=0;zero_cases=0
 for case,row,full in zip(cases,rows[2:-1],raw):
  cid=case['id'];g=gs[case['geometry']];a=g['arrays'];count=case['count'];before=full['baseline_output_bits'];after=full['candidate_output_bits'];initial=g['output_initial']
  active=[bool(count and b) for b in g['output_active']];sel=[v for v,b in zip(before,active) if b];ac=sum(active)
  ok('raw record:'+cid,full['record']==row)
  ok('exact complete output:'+cid,len(before)==len(after)==len(initial) and before==after and all(type(v)==int and 0<=v<=0xffffffff for v in before))
  ok('guards:'+cid,all(v==initial[i] for i,v in enumerate(before) if not active[i]))
  ok('input finite bits:'+cid,all(v&0x7f800000!=0x7f800000 for v in case['reach_o_bits']))
  expected={'active_words':ac,'guard_word_checks':2*(len(before)-ac),'device_input_buffer_checks':42,'device_input_word_checks':2*(sum(len(v) for v in a.values())+len(case['reach_o_bits'])),'active_overwritten_words':sum(v!=corpus['guard'] for v in sel),'nonzero_active_words':sum((v&0x7fffffff)!=0 and v!=corpus['guard'] for v in sel)}
  ok('metadata:'+cid,row['count']==count and row['geometry']==g['id'] and row['profile']==case['profile'] and row['board']==g['board_text'] and all(row[k]==g[k] for k in ['m_p','m_o','nh_p','nh_o','dynamic_shared_bytes','target_m','player']))
  ok('recomputed counts:'+cid,all(row[k]==v for k,v in expected.items()) and expected['active_overwritten_words']==ac and row['all_output_bits_exact'] is True and row['input_bits_unchanged'] is True)
  ok('output FNV:'+cid,row['baseline_output_fnv1a64']==row['candidate_output_fnv1a64']==words_hash(before))
  nf=[{'index':i,'bits':v} for i,v in enumerate(sel) if v&0x7f800000==0x7f800000];nonfinite+=len(nf)
  ok('nonfinite:'+cid,row['nonfinite_active']=={'count':len(nf),'words':nf})
  if case['profile']=='all_zero' or g['m_p']==0 or g['m_o']==0:ok('zero active:'+cid,all(v==0 for v in sel))
  if count:
   ok('blocked own +0:'+cid,all(before[a['cfv_slot'][n]*g['nh_max']+i]==0 for n in [2,5] for i,s in enumerate(g['strengths_p']) if s==0xffffffff))
   if g['target_m']>=127 and case['profile']!='all_zero':ok('nonzero anti vacuity:'+cid,expected['nonzero_active_words']>0)
  else:zero_cases+=1;ok('count0 unchanged:'+cid,before==initial and after==initial)
  if count and g['board_text']=='AsKsQsJsTs' and g['target_m']==257 and case['profile']=='sparse_rounding_witness':
   i=g['rounding_witness_own_index'];oi=a['o_idx'][7:11]
   ok('witness input/compatibility:'+cid,all(not(set(g['hands_p'][i])&set(g['hands_o'][o])) for o in oi) and all([case['reach_o_bits'][slot*g['nh_o']+o] for o in oi]==[0x3f800000,0x33800000,0x33800000,0x33800000] for slot in [2,4]))
   ok('witness exact payoff:'+cid,before[a['cfv_slot'][5]*g['nh_max']+i]==0xbe800000);witnesses.append(cid)
  for k,v in expected.items():totals[k]+=v
 comp=rows[-1]
 expected_totals={'active_words':78896,'guard_word_checks':525400,'device_input_buffer_checks':6216,'device_input_word_checks':1246720,'active_overwritten_words':78896,'nonzero_active_words':36786}
 ok('totals',totals==expected_totals and nonfinite==0 and zero_cases==4 and len(witnesses)==2)
 mapped={'active_words':'active_words_compared','guard_word_checks':'output_guard_word_checks'}
 ok('terminal complete matches recomputation',comp==report['complete'] and all(comp[mapped.get(k,k)]==v for k,v in totals.items()) and comp['rounding_witness_checks']==2 and comp['comparison_pairs']==148 and comp['kernel_launches']==296 and comp['nonfinite_active_words']==0)
 ok('terminal scoped pass',report['verdict']=='PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON' and report['exactness_pass'] is True and report['numerical_validation']=='executed' and report['solver_executions']==0 and report['performance_measurement'] is False and report['candidate_accepted'] is False)
 result={'id':'D051','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON','exactness_pass':True,'numerical_validation':'executed','baseline_cuda_sha256':prep['source_variants']['baseline']['sha256'],'candidate_cuda_sha256':prep['source_variants']['candidate']['sha256'],'baseline_physical_threads':128,'candidate_physical_threads':256,'logical_scan_threads':128,'comparison_pairs':148,'kernel_launches':296,'performance_measurement':False,'candidate_accepted':False,'solver_executions':0,'deployment_changed':False,'prepared_manifest_sha256':prepared_hash,'source_script_review_sha256':sha(ROOT/'comparisons/D051-source-script-review/report.json'),'raw_report_sha256':sha(R/'report.json'),'raw_results_sha256':sha(R/'raw-results.jsonl'),'binary_sha256':sha(R/'probe.exe'),'corpus_sha256':sha(R/'corpus.json'),'stdout_markers':151,'raw_records':148,'totals':totals,'nonfinite_active_words':nonfinite,'witness_cases':witnesses,'count0_cases':zero_cases,'all162_checkout_sources_exact':True,'all18_PTX_entries_match_D050':True,'other8_entries_identical':True,'check_count':len(checks),'input_count':len(inputs),'inputs_sha256':inputs,
 'limits':['Fixed finite-input full-up_show corpus only; no NaN/Inf-input or general NaN-payload guarantee.','Orientations reverse own257/opponentm into ownm/opponent257; not a full count-by-player crossing.','Input immutability is established by pinned native assertions and terminal records; raw output arrays are independently rechecked here.','Direct-kernel numerical prerequisite only. Full-solver accuracy, complete-cycle performance, broad/wide/cumulative qualification remain required.'],
 'reviewer_execution':{'file_audit_only':True,'compiler':0,'native':0,'gpu':0,'checkout_edits':0,'status_edits':0}}
 with (OUT/'validation.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:result[k] for k in ['verdict','check_count','input_count','totals','binary_sha256']},indent=2))
try:audit()
except BaseException as error:
 with (OUT/'reviewer-failure.json').open('x',encoding='utf-8') as f:json.dump({'error':repr(error),'traceback':traceback.format_exc(),'passed_checks':len(checks),'execution':'file-only reviewer; no native/compiler/GPU'},f,indent=2)
 raise
