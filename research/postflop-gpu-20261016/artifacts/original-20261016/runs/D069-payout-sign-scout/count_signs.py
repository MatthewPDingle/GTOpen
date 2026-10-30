"""File-only sign-bit grouping of frozen D067 plans and historical D066 row flags."""
from pathlib import Path
import hashlib,json,struct
B=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths={
 'preparation':(B/'runs/D069-root-decisions/preparation.json','9f458c46ed104ced45f2bf2dfbfd14c4c23f177e3300e57bb4d5b86a7705a6d2'),
 'mapping_catalog':(B/'runs/D067-execution/mapping-artifacts.json','72ce0a7e59999f8872b12d78df775d08bb772808f5b4916890e9cdf46e4c7476'),
 'census_catalog':(B/'runs/D066-execution/census-artifacts.json','38b1e9c7fcc5780b9cbef76fd48ce5bed508f3fe317b84549b6e9e78b08e56cc'),
 'planned_report':(B/'comparisons/D067-planned-show-incidence/report.json','bc2abc4281d230d3e8348758bd12795c3ec5a8bf00d6a2c0ac074ba57f831c94'),
 'planned_audit':(B/'comparisons/D067-independent-review/report.json','1ecbdcd95211088d000e6ebbee566a1c3a0ab96c1e6e6ef6f69839950cc22cce'),
 'census_audit':(B/'comparisons/D066-independent-review/report.json','b6c9a39790578335bee453727d32bdb7cc4f5e1bae3c194d1e3f91b4a8db1e18')}
refs={}
records={}
for name,(path,h) in paths.items():
 assert sha(path)==h,(name,path)
 refs[str(path)]=h;records[name]=json.loads(path.read_text())
assert records['planned_audit']['independent_terminal_audit_pass'] is True
assert records['census_audit']['independent_terminal_audit_pass'] is True
mc=records['mapping_catalog'];cc=records['census_catalog'];prior=records['planned_report']
assert prior['status']=='pass' and prior['mapping_validation_pass'] is True and prior['historical_flag_join_pass'] is True
rows=[]
def read_pinned(directory,name,pins):
 path=Path(directory)/name;data=path.read_bytes();pin=pins[name]
 assert len(data)==pin['bytes'] and sha(path)==pin['sha256'],path
 refs[str(path)]=pin['sha256'];return data
for f in prior['fixtures']:
 name=f['fixture_id']+'-planned-show-mapping.u32le'
 data=read_pinned(mc['mapping_directory'],name,mc['files'])
 assert len(data)%36==0 and len(data)//36==f['show_ctas_per_traverser']
 for snap in f['historical_snapshots']:
  for a in sorted(snap['arrays'],key=lambda x:x['traverser']):
   p=a['traverser'];q=a['opponent'];assert q==1-p
   flags=read_pinned(cc['census_directory'],a['historical_rowflag_file'],cc['files'])
   assert a['historical_rowflag_file']==f['fixture_id']+'-iteration'+str(snap['historical_iteration'])+'-reach'+str(q)+'.rowflags'
   assert len(flags)==a['physical_rows']==f['reach_blocks'][q] and all(x<=7 for x in flags)
   counts={format(i,'03b'):0 for i in range(8)};zero_total=0;nonfinite=0;total=0
   for row in struct.iter_unpack('<9I',data):
    total+=1;assert row[3]<f['num_slots'] and row[1+q]<len(flags)
    if flags[row[1+q]]!=0:continue
    zero_total+=1
    if any((x&0x7f800000)==0x7f800000 for x in row[4:7]):nonfinite+=1;continue
    pattern=''.join('1' if x&0x80000000 else '0' for x in row[4:7])
    counts[pattern]+=1
   eligible=sum(counts.values());old=a['planned_show_counts']
   assert total==old['show_ctas'] and zero_total==old['all_positive_zero']
   assert eligible==old['all_positive_zero_and_finite_payouts'] and zero_total==eligible+nonfinite
   rows.append({'fixture_id':f['fixture_id'],'historical_iteration':snap['historical_iteration'],'traverser':p,'opponent':q,'planned_show_ctas':total,'all_positive_zero_row_planned_ctas':zero_total,'eligible_zero_row_and_three_finite_payouts':eligible,'all_three_payout_sign_bits_negative':counts['111'],'other_finite_sign_patterns':eligible-counts['111'],'eligible_sign_patterns_win_lose_tie':counts,'zero_row_with_nonfinite_payout':nonfinite,'matches_D067_eligible_count':True,'mapping_file':name,'rowflag_file':a['historical_rowflag_file']})
assert len(rows)==12 and len({r['rowflag_file'] for r in rows})==12
out={'id':'D069-payout-sign-scout','status':'FROZEN_EXISTING_FILE_SIGN_PATTERN_COUNTS','scope':'Source-planned CTA metadata joined to six historical pre-evaluation reach snapshots; twelve fixture/snapshot/traverser counts. No GPU expression evaluated.','pattern_key':'Three bits in win,lose,tie order;1 means negative IEEE754 f32 sign bit, including negative zero. Finiteness separately excludes exponent255.','eligibility':'Entire logical opponent row flag0 (all raw bits positive-zero) and each of the three retained planned f32 payout words finite. Each planned CTA counted once per retained snapshot/traverser.','rows':rows,'all_twelve_rows_match_prior_eligible_totals':True,'limits':['These are sign-pattern counts, not newly evaluated zero-mass expression result bits.','Maps are accepted-source host reconstructions; D066 did not retain a device download of showdown metadata or raw reach float payload.','Sampled planned counts are not lifetime frequency, device work fraction, timing or a complete-cycle speed estimate.','Repeated snapshots are separate records and must not be interpreted as a dynamic total or independent timing samples.','E036 remains rejected with its fixed gates and samples unchanged; no new candidate or shortcut correctness is established here.'],'reference_sha256':refs,'new_plan_solver_or_census':False,'compiler_native_gpu_executed':False,'production_modified':False,'performance_measurement':False,'candidate_accepted':False}
with (D/'report.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps([{'fixture':r['fixture_id'],'iteration':r['historical_iteration'],'p':r['traverser'],'eligible':r['eligible_zero_row_and_three_finite_payouts'],'all_negative':r['all_three_payout_sign_bits_negative'],'other':r['other_finite_sign_patterns'],'nonzero_patterns':{k:v for k,v in r['eligible_sign_patterns_win_lose_tie'].items() if v}} for r in rows],indent=2))
