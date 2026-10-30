"""Derive prospective current-base stages; no source variant or outcome selection."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
q=old.read(ROOT/'runs/E062-resource/report.json');assert all(q['gates'].values()) and q['kernel_launches']==0
sources={};outputs={}
for stem in ['prepare-raw','freeze-build','freeze-primary','run-and-assess']:
 a=ROOT/'runs'/('E061-'+stem+'.py');b=ROOT/'runs'/('E062-'+stem+'.py');assert not b.exists()
 code=a.read_text(encoding='utf-8').replace('E061','E062').replace('e061','e062').replace('E050','E057').replace('V061','V062')
 if stem=='prepare-raw':
  needle="assert r['gates']['all9_sm75_fallback_entries_exact'] and r['gates']['async_copies_emitted']";assert code.count(needle)==1
  code=code.replace(needle,"assert r['gates']['other8_sm75_entries_exact'] and r['gates']['sm75_show_changed']\nassert all(r['gates'][v+'_'+a+'_legacy_ptx_exact'] for v in ['baseline','candidate'] for a in ['compute_120','compute_75'])")
  code=code.replace('asynchronous staging','prefix address mapping').replace('9sm75fallback entries exact,2async copies/wait emitted','other8sm75entries exact, all4original PTX artifacts exact')
  needle="P.update(cases=364,kernel_launches=728,";assert code.count(needle)==1
  code=code.replace(needle,"P['retained_corpus_protocol_sha256']=P.pop('protocol_sha256')\n"+needle)
 if stem=='freeze-build':
  needle="'session_id':37260";assert code.count(needle)==1
  code=code.replace(needle,"'native_child_receipt_sha256':old.sha(K/'execution/probe.exit.json')")
 if stem=='freeze-primary':
  code=code.replace('B189','B192').replace('B190','B193').replace('B191','B194')
  code=code.replace('Exact original E057four-byte asynchronous staging form transferred only within up_show onto accepted E051.','Exact original E057prefix-index mapping helper and accesses, byte-identical complete CUDA source on accepted E051.')
 ast.parse(code);b.write_text(code,encoding='utf-8',newline='\n');sources[str(a)]=old.sha(a);outputs[str(b)]=old.sha(b)
old.save(ROOT/'runs/E062-resource/derived-stage-manifest.json',{'at':old.now(),'template_sha256':sources,'generated_sha256':outputs,'changes':'Candidate/source-form identities; exact current prefix/PTX gate; retained corpus provenance labeling; actual raw child receipt rather than inherited handle; prospective B192..194/V062identities. No source/metric/guard/quality/sampling changes.','native_numerical_or_speed_outcomes_before_derivation':0,'source_variant':False})
old.custody();print(json.dumps({'derived_scripts':list(outputs),'first_numerical_runs':0,'candidate':'E062'}),flush=True)
