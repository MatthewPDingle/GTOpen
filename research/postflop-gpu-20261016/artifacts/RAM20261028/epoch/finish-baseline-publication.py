import sys,json,statistics,shutil,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import common as h
assert len(sys.argv)==2;h.pin(h.EPOCH/'baseline-protocol.json',sys.argv[1]);P=h.read(h.EPOCH/'baseline-protocol.json')
for p,digest in P['input_sha256'].items():h.pin(p,digest)
h.custody();O=h.ROOT/'runs/RAM20261028-execution';D=h.ROOT/'comparisons/RAM20261028-baseline'
report=h.read(D/'report.json');frozen_report_sha=h.sha(D/'report.json')
assert report['protocol_sha256']==sys.argv[1]
assert h.read(O/'assessment.exit.json')['returncode']==1
scored=[x['id']for x in P['sequence']if x['scored']];fixtures=report['fixtures'];aggregate=report['aggregate_ms']
for x in P['sequence']:
 ident=x['id'];receipt=h.read(O/(ident+'.exit.json'));assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
 if not x['unit']:assert h.exact(ident)==h.read(h.EPOCH/'exact-anchor.json')
for i,f in enumerate(fixtures):
 values=[h.read(h.ROOT/'runs'/ident/'report.json')['results'][i]['full_cycle_ms']for ident in scored]
 assert values==f['raw_full_cycle_ms']and statistics.median(values)==f['median_full_cycle_ms']
assert sum(f['median_full_cycle_ms']for f in fixtures)==aggregate
h.save(D/'publication-repair.json',{'at':h.now(),'original_assessment_exit_sha256':h.sha(O/'assessment.exit.json'),'original_error':'Hardware metadata was already published at the same evidence path; create-new assertion stopped publication after the final baseline report was written.','repair':'Reader/publication only: verify identical existing evidence bytes and reuse them. All seven native processes and the five scored measurements are retained; no native rerun, exclusion, extension, threshold or report alteration.','retained_report_sha256':frozen_report_sha,'new_native_processes':0,'all_seven_native_exit_codes_zero':True})
source=(h.EPOCH/'assess-baseline.py').read_text(encoding='utf-8')
body=source[source.index('pub=[]'):]
needle="assert not dst.exists();shutil.copyfile(p,dst)"
assert body.count(needle)==1
body=body.replace(needle,"\n if dst.exists():assert dst.read_bytes()==p.read_bytes()\n else:shutil.copyfile(p,dst)")
exec(compile(body,str(h.EPOCH/'assess-baseline.py')+'#publication-replay','exec'))
h.pin(D/'report.json',frozen_report_sha)
