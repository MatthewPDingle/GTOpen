"""File-only root check of compiled E045 integer controls and unchanged production scope."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
ROOT=old.ROOT;P=old.read(HERE/'protocol.json');C=old.read(ROOT/'runs/E045-control-execution/complete.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
M=old.read(P['source_manifest']);D=Path(P['source_manifest']).parent;checks=0
def req(v,m):
 global checks
 assert v,m;checks+=1
base=(D/'base-arena.rs').read_text(encoding='utf-8');production=(D/'production-arena.rs').read_text(encoding='utf-8');candidate=(D/'candidate-arena.rs').read_text(encoding='utf-8')
req((D/'production-arena.rs').read_bytes()==(ROOT/'runs/E045-design/production-arena.rs').read_bytes(),'test repair left production exact')
original=base[base.index('    fn can_upload_zeros('):base.index('    pub(super) fn upload(')]
req(original.replace('fn can_upload_zeros(','fn e045_original_can_upload_zeros(') in candidate,'accepted predicate copied exactly')
expected=original.replace('q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0','zero_proof_i16_bits(q.as_slice()) == 0').replace('q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0','zero_proof_u16_bits(q.as_slice()) == 0')
req(expected==production[production.index('    fn can_upload_zeros('):production.index('    pub(super) fn upload(')],'all original non-reduction guards exact')
req(production[production.index('    pub(super) fn upload('):]==base[base.index('    pub(super) fn upload('):],'upload/readback/tests suffix unchanged')
req('unsafe' not in production[production.index('// Integer OR is exact'):production.index('impl ArenaLayout {')],'no unsafe parallel helper')
r=old.read(ROOT/'runs/V045-unit/report.json');rawpath=ROOT/'runs/V045-unit/stdout.log';old.pin(rawpath,r['stdout_sha256']);raw=rawpath.read_text(encoding='utf-8')
req(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('86','0','4','0','0')],'complete ordinary inventory')
integer=[json.loads(x.split('E045_INTEGER_OR_CONTROL ',1)[1]) for x in raw.splitlines() if 'E045_INTEGER_OR_CONTROL ' in x]
predicate=[json.loads(x.split('E045_FULL_PREDICATE_CONTROL ',1)[1]) for x in raw.splitlines() if 'E045_FULL_PREDICATE_CONTROL ' in x]
req(len(integer)==len(predicate)==1,'one marker per fixed control');q=integer[0];chunk=1<<20
req(q['lengths']==[0,1,7,127,128,129,chunk-1,chunk,chunk+1,2*chunk-1,2*chunk,2*chunk+1,3*chunk+17],'fixed length inventory')
req(q['threads']==[1,2,16],'pool inventory')
count=0
for n in q['lengths']:
 positions=sorted(set(p for p in [0,max(0,n-1),chunk-1,chunk,2*chunk-1,2*chunk] if p<n))
 count+=2*(2+16*len(positions))*3
req(count==3516==q['checks']==C['integer_or_checks'],'recomputed raw integer case count')
req(9*2*2*2*8==576==predicate[0]['cases']==C['full_predicate_cases'],'recomputed predicate count')
req(q['inputs_unchanged'] and q['raw_integer_or_exact'] and predicate[0]['inputs_unchanged'] and predicate[0]['accepted_original_exact'],'successful native assertions')
req(r['returncode']==0 and r['status']=='measured' and r['provenance']['source_sha256']==old.BASE,'native success/accepted checkout')
bm=old.read(ROOT/'binaries/E045-solver.manifest.json');old.pin(ROOT/'binaries/E045-solver.exe',bm['binary_sha256'])
req(bm['source_sha256']==old.BASE|{n:x['candidate_sha256'] for n,x in M['owned'].items()},'compiled source exact')
req(r['binary_sha256']==bm['binary_sha256'] and r['binary_build_manifest']['data']==bm,'native binary/build manifest exact')
T=old.read(ROOT/'runs/E045-final-build-r2/terminal.json');req(T['returncode']==0 and T['complete_sha256']==old.sha(ROOT/'runs/E045-final-build-r2/complete.json'),'all compilers terminal')
old.custody()
OUT=ROOT/'comparisons/E045-integer-control-root';OUT.mkdir()
report={'id':'E045-integer-control-root','at':old.now(),'status':'pass_scoped_parallel_zero_proof_root','checks':checks,'root_cross_check_only':True,'ordinary_passed':86,'integer_or_checks':3516,'full_predicate_cases':576,'raw_stdout_sha256':old.sha(rawpath),'control_complete_sha256':old.sha(ROOT/'runs/E045-control-execution/complete.json'),'source_manifest_sha256':old.sha(Path(P['source_manifest'])),'production_sha256':old.sha(D/'production-arena.rs'),'accepted162_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Root source/receipt/raw-marker and corpus arithmetic check, not an external independent audit. Integer source/corpus exactness is scoped; no timing, CPU-resource or GPU-path universal claim.'}
old.save(OUT/'report.json',report);print(json.dumps({'checks':checks,'report_sha256':old.sha(OUT/'report.json')}))
