import sys,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/D155-packet-engine-control';P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
assert h.read(H/'execution/probe.exit.json')['returncode']==0 and h.read(H/'execution/audit.exit.json')['returncode']==1
old=(H/'audit.py').read_text(encoding='utf-8');new=old
needle='epoch=phases=roots=evs=regenerated=readbacks=handled=declined=pinnedguards=0;wrapperpairs=set()'
assert needle in new;new=new.replace(needle,needle+';coverage_misses=[]',1)
needle="if ident<16:req(expected_handle,'all main compressed fixtures really activate')"
assert needle in new;new=new.replace(needle,"if ident<16 and not expected_handle:coverage_misses.append({'case':ident,'stage':stage,'pinned_words':proof['pinned_words'],'CFV_words':proof['CFV_words']})",1)
needle="req(handled>=84 and declined>=80 and pinnedguards>0,'nontrivial actual activation/decline/guard coverage')"
assert needle in new;new=new.replace(needle,"coverage_gates={'all16_main_compressed_cases_really_activate':not coverage_misses,'at_least84_actual_packet_readbacks':handled>=84,'at_least80_declines':declined>=80,'nonzero_pinned_guard_coverage':pinnedguards>0}\nreq(not all(coverage_gates.values()),'original coverage failure remains failed')",1)
new=new.replace("D=ROOT/'comparisons/D155-packet-engine-control'","D=ROOT/'comparisons/D155-coverage-failure'",1)
new=new.replace("'status':'pass_scoped_actual_packet_engine_equivalence'","'status':'incomplete_expected_activation_coverage', 'original_protocol_coverage_gates':coverage_gates, 'coverage_misses':coverage_misses, 'original_cohort_passed':False, 'original_raw_and_audit_unchanged':True, 'retained_review_sha256':h.sha(__file__)",1)
new=new.replace("'scope':'Fixed36case engine matrix,","'scope':'Original native0/audit1 retained. This is a complete retained-word review with original coverage gates recorded FAILED, not a cohort pass or candidate admission. No new native run, source variant, cases, samples or thresholds. Compact packed engine behavior remains missing. Fixed36case engine matrix,",1)
new=new.replace("print({k:report[k] for k in ['status','cases','actual_packet_path_readbacks','raw_frames','reader_checks']},flush=True)","print({k:report[k] for k in ['status','original_cohort_passed','cases','actual_packet_path_readbacks','raw_frames','reader_checks','original_protocol_coverage_gates']},flush=True)",1)
target=ROOT/'runs/D155-retained-review.py';assert not target.exists();target.write_bytes(new.encode())
patch=ROOT/'runs/D155-retained-review.patch';assert not patch.exists();patch.write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='frozen/audit.py',tofile='retained-review.py')).encode())
compile(new,str(target),'exec')
h.save(ROOT/'runs/D155-retained-review-protocol.json',{'at':h.now(),'status':'FROZEN_PRE_RETAINED_READER_ONLY','original_protocol_sha256':h.sha(H/'protocol.json'),'original_native_exit':0,'original_reader_exit':1,'original_raw_or_source_revised':False,'new_native_executions':0,'original_coverage_gates_not_regraded':True,'reader_sha256':h.sha(target),'patch_sha256':h.sha(patch),'scope':'Replay full unchanged observations, keep all scientific word/guard/metadata checks, accumulate original activation coverage failures and publish only an INCOMPLETE report. No acceptance/qualification or numerical/performance gate repair.'})
print(h.sha(target),flush=True)
