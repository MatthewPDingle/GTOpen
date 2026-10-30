"""Freeze unchanged 1% qualification for the one E063 source form."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
build=ROOT/'runs/E063-final-build/complete.json';B=old.read(build);assert B['all_compilers_terminal'] and B['native_executions']==0
for p,h in B['evidence_sha256'].items():old.pin(p,h)
control=ROOT/'comparisons/E063-kernel-control-root-check/report.json';C=old.read(control);assert C['status']=='pass_scoped_show_raw_equivalence' and C['cases']==364 and C['all_full_outputs_inputs_guards_exact'] and C['packed_boundary_representation_independently_validated']
H=ROOT/'runs/E063-primary-plan';assert not H.exists();H.mkdir();prior=ROOT/'runs/E062-primary-plan'
for n in ['native.py','assess.py','root-check.py']:
 code=(prior/n).read_text(encoding='utf-8').replace('E062','E063');ast.parse(code);(H/n).write_text(code,encoding='utf-8',newline='\n')
manager=(ROOT/'runs/E062-run-and-assess.py').read_text(encoding='utf-8').replace('E062','E063');ast.parse(manager);mp=ROOT/'runs/E063-run-and-assess.py';assert not mp.exists();mp.write_text(manager,encoding='utf-8',newline='\n')
P=old.read(prior/'protocol.json');baseline=ROOT/'runs/accepted-E051/baseline.json';binary=ROOT/'binaries/E051-postflop_autoresearch.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE
owned=old.read(ROOT/'runs/E063-source/manifest.json')['candidate_owned_sha256']
pairs=[{'baseline':'B195','candidate':'E063R1'},{'baseline':'B196','candidate':'E063R2'},{'baseline':'B197','candidate':'E063R3'}]
P.update(id='E063-primary',at=old.now(),status='FROZEN_BEFORE_FIRST_SPEED_OBSERVATION',baseline={'path':str(baseline),'sha256':old.sha(baseline)},baseline_binary={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)},candidate_owned_sha256=owned,build_protocol_sha256=old.sha(ROOT/'runs/E063-build-plan/build-protocol.json'),gpu_control_report={'path':str(control),'sha256':old.sha(control)},control_ids=['V063-unit'],ordinary_unit_id='V063-unit',measurement_order=['B195','E063R1','E063R2','B196','B197','E063R3'],pairs=pairs,source_scope='One-time CPU per-card lower/upper cutoff counts packed into spare bits of the same two GPU boundary words; three ordered GPU correction loops. Public plan values and persistent GPU buffer lengths/ABI/launches/quality unchanged. Count all extra host preparation/cloning and CUDA initialization in complete-cycle timing. D102integer proof/current resources and full364raw GPU pairs passed. No loop/packing/width/placement/schedule variants or rescue samples.',material_costs_pending='Temporary cloned host metadata is an actual cost: max4,998,544bytes in D102cases, conservative legal flop bound20,340,096bytes. Must verify peak/lifetime/headroom and behavior before any adoption; resource screen does not discharge material-cost qualification.')
P.pop('source_ancestry',None)
paths=[*H.glob('*.py'),mp,Path(__file__),baseline,binary,manifest,build,control,ROOT/'runs/E063-build-plan/build-protocol.json',ROOT/'runs/E063-resource/report.json',ROOT/'runs/E063-resource/compiled-mechanism.json',ROOT/'runs/E063-source/source-review.json',ROOT/'runs/E063-source/manifest.json',ROOT/'runs/E063-kernel-control/execution/terminal.json',ROOT/'runs/D102-card-cutoffs-r3/report.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for stem in ['E063-solver','E063-postflop_autoresearch']:
 exe=ROOT/'binaries'/(stem+'.exe');cm=exe.with_suffix('.manifest.json');data=old.read(cm);old.pin(exe,data['binary_sha256']);assert data['source_sha256']==old.BASE|owned;paths.extend([exe,cm])
status=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(e['id']==identity for e in status['experiments'])
P['input_sha256']={str(p):old.sha(p) for p in paths};old.save(H/'protocol.json',P)
published={}
for p in H.iterdir():
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'all_compilers_terminal':True,'new_timing_observations':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E063');e.update(stage='Ordinary units then fixed three-pair complete-cycle screen',reason='Fresh feature/primary builds terminal; accepted E051restored. Run V063-unit then B195/E063R1,E063R2/B196,B197/E063R3. Added CPU preprocessing and temporary clones included in full timing; same1%/strict fixture rules. Further fresh16/broad/material/holdout/cumulative required before adoption.');e['evidence'].append({'label':'First complete-cycle speed protocol','url':'evidence/'+H.name+'/protocol.json'});st.update(updated_at=old.now(),state='running',active_experiment='E063',stage='E063 first complete-cycle speed screen',activity='84ordinary GPU tests then3fixed pairs. Same accuracy/stops/storage/fixtures, all samples retained, accepted E051source remains restored.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'pairs':pairs,'minimum_gain_pct':P['policy']['minimum_complete_cycle_gain_pct'],'all_builds_terminal':True}),flush=True)
