"""Advance the unchanged E060 candidate after zero scalar output mismatches."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
SC=ROOT/'runs/E060-scalar-control';rp=old.read(SC/'protocol.json')
for n,h in rp['input_sha256'].items():old.pin(n,h)
assert old.read(SC/'execution/complete.json')['all_scalar_bits_exact']
q=old.read(SC/'execution/raw/report.json');assert q['cases']==2130758 and q['mismatches']==0 and q['shared_refinement_cases']==1252036 and q['native_fallback_cases']==685665
assert (SC/'execution/raw/inputs.bin').read_bytes()==(SC/'execution/raw/inputs-after.bin').read_bytes()
H=ROOT/'runs/E060-kernel-control';prior=ROOT/'runs/E055-kernel-control';RES=ROOT/'runs/E060-resource';assert not H.exists();H.mkdir()
for v in ['baseline','candidate']:(H/(v+'.ptx')).write_bytes((RES/'execution'/(v+'.ptx')).read_bytes())
(H/'discounts.rs').write_bytes((prior/'discounts.rs').read_bytes())
for n in ['probe.rs','execute.py','audit.py']:
 s=(prior/n).read_text(encoding='utf-8').replace('E055','E060')
 if n=='execute.py':
  assert s.count("=='pass_resource_feasibility_only'")==1
  s=s.replace("=='pass_resource_feasibility_only'","=='pass_resource_prerequisite'")
 if n.endswith('.py'):ast.parse(s)
 (H/n).write_text(s,encoding='utf-8',newline='\n')
corpus=old.read(prior/'corpus.json');corpus.update(id='E060-up-action-corpus',at=old.now());assert len(corpus['cases'])==819
old.save(H/'corpus.json',corpus)
old.save(H/'source-review.json',{'id':'E060-kernel-control-source-review','at':old.now(),'review_scope':'Root reused the retained complete819case ABI/address/output/guard decoder and exact production PTX, changed only candidate identity and resource-pass status string. No corpus/math/input mutation. Not external independent review.','candidate_source_sha256':old.sha(ROOT/'runs/E060-source/candidate.cu'),'resource_report_sha256':old.sha(RES/'report.json'),'scalar_report_sha256':old.sha(SC/'execution/raw/report.json'),'cases':819,'expected_launches':1638,'roles':['own unlocked','own locked','opponent'],'arities':[1,2,3,4,5,8,9,16,17],'controls':'Raw actual12immutable input vectors, mutable regret/strategy/CFV arrays, all guards/nonowned/child rows, distinct device address ranges, parent-child rows disjoint, DCFR/CFRplus production discount bits, NaN/infinities/signedzero/subnormals/overflow/handtails/countzero/block shapes. No timing score.','failure_rule':'Any mismatch stops E060 without source/math/guard/arity rescue; retain raw failed evidence.'})
P=old.read(prior/'protocol.json');P.update(id=H.name,at=old.now(),rustc_command=[x.replace(str(prior),str(H)) for x in old.read(prior/'protocol.json')['rustc_command']],resource_report=str(RES/'report.json'),raw_output=str(H/'evidence'))
inputs=[*H.iterdir(),ROOT/'runs/E060-source/manifest.json',RES/'report.json',SC/'protocol.json',SC/'execution/complete.json',SC/'execution/raw/report.json',Path(__file__),ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in inputs if p.is_file()};P['input_sha256'].update({p:h for p,h in old.read(prior/'protocol.json')['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']})
old.save(H/'protocol.json',P)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E060');e.update(stage='Whole action-kernel exactness matrix',reason='2,130,758scalar cases matched every result bit, including1,252,036shared-refinement and685,665native-fallback cases; unchanged inputs/guards. This is sampled evidence. Now testing819complete action-kernel geometries before timing.')
 d=next(e for e in st['experiments'] if e['id']=='D098');d.update(kind='diagnostic',status='measured',correctness='pass')
 st.update(updated_at=old.now(),stage='E060 complete action-kernel exactness',activity='Scalar exactness passed. Full raw kernel controls next; no solver run or new speed gain yet.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'cases':819,'scalar_cases_passed':q['cases']}),flush=True)
