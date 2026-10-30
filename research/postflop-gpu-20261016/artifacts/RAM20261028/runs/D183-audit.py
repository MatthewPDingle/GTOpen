import hashlib,json,statistics,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D183-plan-phase-diagnostic';P=h.read(H/'protocol.json');h.pin(H/'protocol.json',sys.argv[1]);h.custody()
for p,digest in P['input_sha256'].items():h.pin(p,digest)
schema=h.read(H/'schema.json');fields=[x[0] for x in schema['fields']];assert len(fields)==P['field_count'];fixtures=h.read(H/'fixtures.json');all_rows=[];identities={};pairs=0;compared=0;field_pairs=0
for seq in P['sequence']:
 receipt=h.read(H/'execution'/(seq['id']+'.exit.json'));assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
 log=H/'execution'/(seq['id']+'.stdout.log');raw=log.read_text();markers=[json.loads(x.split('D183_PLAN ',1)[1]) for x in raw.splitlines() if 'D183_PLAN ' in x];assert len(markers)==7 and markers[-1]['stage']=='complete' and markers[-1]['cases']==6 and markers[-1]['GPU_context_or_kernel_calls']==0
 for row,f in zip(markers[:-1],fixtures):
  assert row['stage']=='fixture' and row['id']==f['id'] and row['config']==f['config'] and row['use_iso']==f['use_iso'] and row['nodes']==f['expected_nodes'] and row['order']==seq['order'] and row['GPU_context_or_kernel_calls']==row['solver_runs']==0 and row['all_fields_retained']==P['field_count'];assert [x[0] for x in row['phase_ms']]==P['phase_labels'];assert all(x[1]>=0 for x in row['phase_ms']);assert sum(x[1] for x in row['phase_ms'])<=row['observed_plan_ms'];row['process']=seq['id'];all_rows.append(row)
  paths=[H/seq['id']/(f['id']+'-'+arm+'.plan.bin') for arm in ['baseline','observed']];sizes=[p.stat().st_size for p in paths];assert sizes[0]==sizes[1] and 0<sizes[0]<=P['max_raw_file_bytes'];hashes=[hashlib.sha256(),hashlib.sha256()]
  with paths[0].open('rb') as b,paths[1].open('rb') as c:
   def same(n):
    global compared
    a=b.read(n);d=c.read(n);assert len(a)==len(d)==n and a==d
    hashes[0].update(a);hashes[1].update(d);compared+=n;return a
   assert same(17)==b'D183_PLAN_RAW1\0\0\0'
   for name in fields:
    length,=struct.unpack('<I',same(4));assert 0<length<256;assert same(length).decode()==name;size,=struct.unpack('<Q',same(8));assert 0<size<=P['max_raw_file_bytes']
    while size:n=min(size,8*1024**2);same(n);size-=n
    field_pairs+=1
   assert not b.read(1) and not c.read(1)
  assert hashes[0].digest()==hashes[1].digest()
  for p,size,digest in zip(paths,sizes,hashes):identities[str(p)]={'bytes':size,'sha256':digest.hexdigest()}
  pairs+=1
assert pairs==18 and len(identities)==P['raw_files'] and field_pairs==18*len(fields)
rows=[]
for f in fixtures:
 rs=[x for x in all_rows if x['id']==f['id']];assert len(rs)==3;b=statistics.median(x['baseline_plan_ms'] for x in rs);o=statistics.median(x['observed_plan_ms'] for x in rs);phases={label:statistics.median(dict(x['phase_ms'])[label] for x in rs) for label in P['phase_labels']};rows.append({'id':f['id'],'fixture':f['fixture'],'use_iso':f['use_iso'],'baseline_plan_median_ms':b,'observed_plan_median_ms':o,'observer_outer_difference_pct':100*(o-b)/b if b else None,'phase_medians_ms':phases})
totals={label:sum(row['phase_medians_ms'][label] for row in rows if row['use_iso']) for label in P['phase_labels']};totals=dict(sorted(totals.items(),key=lambda x:x[1],reverse=True));D=ROOT/'comparisons/D183-plan-phase-diagnostic';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D183','at':h.now(),'status':'CPU_only_plan_phase_observation_complete','protocol_sha256':sys.argv[1],'full_plan_pairs_exact':pairs,'all_plan_fields':fields,'field_pairs_exact':field_pairs,'whole_pair_bytes_compared':compared,'all36_raw_file_sha256':identities,'rows':rows,'all18_observations':all_rows,'primary_iso_phase_median_sum_ms':totals,'primary_reference_plan_median_sum_ms':sum(x['baseline_plan_median_ms'] for x in rows if x['use_iso']),'GPU_context_or_kernel_or_solver_runs':0,'complete_cycle_headroom_or_speedup_established':False,'optimizer_admitted':False,'candidate_accepted':False,'scope':'Every byte of all original plan fields compared and hashed, including float bits, default/unreachable metadata, order/slots/spans. CPU-only14phase component clocks/paired observer differences are diagnostic; they exclude Spot/CPUarena construction, GPU, solves/readback/serialize/destruction and cannot prove integration speed/removable complete-cycle headroom. No exclusions/repeats/alternativefixture/source/flags. Any future candidate needs distinct history/source proof and every unchanged qualification gate.'})
print(json.dumps({'status':'pass_full_raw_cpu_plan','pairs':pairs,'field_pairs':field_pairs,'whole_pair_bytes':compared,'primary_phase_ms':totals,'observer_pct':{x['id']:x['observer_outer_difference_pct'] for x in rows}}),flush=True)
