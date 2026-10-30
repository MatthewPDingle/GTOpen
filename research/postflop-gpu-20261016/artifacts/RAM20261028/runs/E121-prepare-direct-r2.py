"""Freeze both complete terminal corpora with explicit per-arm metadata encoding."""
import ast
import copy
import json
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h

def once(text, old, new):
    assert text.count(old) == 1, old[:160]
    return text.replace(old, new, 1)

def save_reuse(path, value):
    if path.exists():
        assert h.read(path) == value
    else:
        h.save(path, value)

def write_reuse(path, data):
    if path.exists():
        assert path.read_bytes() == data
    else:
        path.write_bytes(data)

h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
assert not (ROOT / 'epoch-sequence.lock').exists()
assert shutil.disk_usage(ROOT).free >= 96 * 1024**3
S = ROOT / 'runs/E121-source'
R = ROOT / 'runs/E121-resource'
assert all(h.read(R / 'report.json')['gates'].values())
assert h.read(ROOT / 'runs/D297-hand-word-native/report.json')['status'] == 'pass_scoped_two_terminal_native_hand_word_operand_and_removed_load_witness'

F = ROOT / 'runs/D298-hand-word-fold'
F.mkdir(exist_ok=True)
A = ROOT / 'runs/D291-static-fold-control'
old_fold = h.read(A / 'corpus.json')
fold = copy.deepcopy(old_fold)
assert len(fold['cases']) == 360 and len(fold['full_scenarios']) == 34
for scenario_index in [15, 32]:
    scenario = copy.deepcopy(old_fold['full_scenarios'][scenario_index])
    assert scenario['nh_o'] == scenario['nh_p'] == 1326
    new_index = len(fold['full_scenarios'])
    scenario['id'] += '-descriptor-boundaries'
    patterns = [(0, 1, 0), (50, 51, 1325), (0, 51, 0xffffffff)]
    for i in range(scenario['nh_p']):
        scenario['pc1'][i], scenario['pc2'][i], scenario['same_p'][i] = patterns[i % 3]
    fold['full_scenarios'].append(scenario)
    for case in old_fold['cases']:
        if case['scenario_index'] == scenario_index:
            new_case = copy.deepcopy(case)
            new_case.update(id=len(fold['cases']), scenario_index=new_index)
            fold['cases'].append(new_case)
assert fold['cases'][:360] == old_fold['cases']
assert fold['full_scenarios'][:34] == old_fold['full_scenarios']
assert len(fold['cases']) == 380 and len(fold['full_scenarios']) == 36
fold.update(id='E121-full-fold-private-hand-word', case_count=380, kernel_launches_if_executed=760)
save_reuse(F / 'corpus.json', fold)

probe = (A / 'probe.rs').read_text().replace('D291', 'D298')
probe = once(probe, 'type Out=BufWriter<File>;', 'include!("host-encode.rs");\ntype Out=BufWriter<File>;')
probe = once(probe, 'assert_eq!(cases.len(),360);', 'assert_eq!(cases.len(),380);')
probe = once(probe,
    'let dsame=stream.clone_htod(&same).unwrap();let dslots=',
    'let dslots=')
probe = once(probe,
    '  for (label,f) in [("baseline",&bf),("candidate",&cf)]{\n   let mut dv=',
    '''  let mut packed_same = same.clone();
  let packed = terminal_hand_words(&pc1[..nhp as usize], &pc2[..nhp as usize], &same[..nhp as usize]);
  packed_same[..nhp as usize].copy_from_slice(&packed);
  for (label,f) in [("baseline",&bf),("candidate",&cf)]{
   let same_words = if label == "candidate" { &packed_same } else { &same };
   let dsame = stream.clone_htod(same_words).unwrap();
   let mut expected_immutable = immutable.clone();
   expected_immutable[12] = same_words.clone();
   let mut dv=''')
probe = once(probe,
    'assert_eq!(post,immutable,"immutable case{index}/{label}");',
    '''assert_eq!(post,expected_immutable,"immutable case{index}/{label}");
   if label == "candidate" {
    for i in 0..nhp as usize {
     let word = post[12][i];
     assert!(word < 0x800000);
     assert_eq!(word & 63, pc1[i]);
     assert_eq!((word >> 6) & 63, pc2[i]);
     assert_eq!(if word >> 12 == 2047 {u32::MAX} else {word >> 12}, same[i]);
    }
   }''')
write_reuse((F / 'probe.rs'), probe.encode())

audit = (A / 'audit-r2.py').read_text().replace('D291', 'D298')
audit = once(audit,
    '    req(bi.data == ci.data, "all actual immutable device bytes equal between arms")',
    '    # Every per-arm physical input is checked below, including the complete encoded same vector.')
audit = once(audit,
    '            req(all(a == b for a, b in zip(imm, post)), "all actual immutable device inputs unchanged")',
    '''            if family == "up-fold" and out is cand:
                packed = list(imm[12])
                for hand in range(scenario["nh_p"]):
                    c1, c2, same = imm[8][hand], imm[9][hand], imm[12][hand]
                    req(c1 < 52 and c2 < 52 and (same == 0xffffffff or same < scenario["nh_o"]), "descriptor source domain")
                    packed[hand] = c1 | (c2 << 6) | ((2047 if same == 0xffffffff else same) << 12)
                for field, (original, actual) in enumerate(zip(imm, post)):
                    if field == 12:
                        equal(actual, packed, "every physical packed word including unchanged empty/padding guard")
                        for hand in range(scenario["nh_p"]):
                            word = actual[hand]
                            req(word < 0x800000 and word & 63 == imm[8][hand] and (word >> 6) & 63 == imm[9][hand], "actual packed cards decode original")
                            req((0xffffffff if word >> 12 == 2047 else word >> 12) == imm[12][hand], "actual packed same index decodes original")
                    else:
                        req(original == actual, "every other actual immutable input byte unchanged")
            else:
                req(all(a == b for a, b in zip(imm, post)), "all actual immutable device inputs unchanged")''')
audit = audit.replace('"pass_scoped_full_raw_equivalence"', '"pass_scoped_encoded_input_full_raw_equivalence"')
audit = audit.replace('"full_raw_files_equal": True,', '"full_output_files_equal": True, "every_physical_input_checked_against_declared_encoding": True, "changed_input_field": "candidate same_p valid hand prefix only; all other words exact",')
ast.parse(audit)
write_reuse((F / 'audit.py'), audit.encode())

executor = (ROOT / 'runs/D291-execute-static-fold.py').read_text()
executor = executor.replace('D291-static-fold-control', 'D298-hand-word-fold').replace('D291', 'D298')
executor = executor.replace('len(rows)==361', 'len(rows)==381').replace("['cases']==360", "['cases']==380").replace("['kernel_launches']==720", "['kernel_launches']==760")
ast.parse(executor)
fold_executor = ROOT / 'runs/D298-execute-hand-word-fold.py'
write_reuse(fold_executor, executor.encode())

B = ROOT / 'runs/E120-kernel-control'
G = ROOT / 'runs/E121-show-control'
G.mkdir(exist_ok=True)
old_show = h.read(B / 'corpus.json')
show = copy.deepcopy(old_show)
assert len(show['cases']) == 2636 and len(show['geometries']) == 244
added = []
for geometry in old_show['geometries'][:36]:
    if geometry['target_m'] != 1081:
        continue
    template = next(case for case in old_show['cases'] if case['geometry'] == geometry['id'] and case['profile'] == 'seeded_ordinary' and case['count'] == 2)
    nh = geometry['nh_o']
    ob = geometry['arrays']['o_off'][1]
    mo = geometry['arrays']['o_cnt'][1]
    listed = sorted(geometry['arrays']['o_idx'][ob:ob + mo])
    indices = sorted({0, nh - 1, listed[0], listed[-1], min(listed, key=lambda value: abs(value - 511)), min(listed, key=lambda value: abs(value - 1023))})
    rows = sorted({geometry['arrays']['rsrc_o'][node] for node in [2, 5]})
    for index in indices:
        for weight in [1, 0x3f800000]:
            case = copy.deepcopy(template)
            case.update(id=geometry['id'] + '-hand-word-single-' + str(index) + '-' + hex(weight),
                        profile='stress_hand_word_single_reach', payout_test=True, hand_word_test=True)
            for row in rows:
                case['reach_o_bits'][row * nh:(row + 1) * nh] = [0] * nh
                case['reach_o_bits'][row * nh + index] = weight
            show['cases'].append(case)
            added.append({'case': case['id'], 'geometry': geometry['id'], 'opponent_index': index, 'weight_bits': weight, 'source_rows': rows})
assert show['cases'][:2636] == old_show['cases'] and show['geometries'] == old_show['geometries']
assert added and len({case['id'] for case in show['cases']}) == len(show['cases'])
show.update(id='E121-full-showdown-private-hand-word', hand_word_added_case_provenance=added)
save_reuse(G / 'corpus.json', show)
geometries = {row['id']: row for row in show['geometries']}
case_count = len(show['cases'])
pairs = case_count * 5
launches = pairs * 2
active_words = 5 * sum(2 * geometries[case['geometry']]['nh_p'] if case['count'] else 0 for case in show['cases'])
guards = 5 * sum(2 * (len(geometries[case['geometry']]['output_initial']) - (2 * geometries[case['geometry']]['nh_p'] if case['count'] else 0)) for case in show['cases'])

probe = (B / 'probe.rs').read_text().replace('E120', 'E121')
probe = once(probe, 'mod cards { pub type Card=u8; }', 'include!("host-encode.rs");\nmod cards { pub type Card=u8; }')
probe = once(probe, 'width:u32,active:&[bool])->Result<', 'width:u32,active:&[bool],encoded:bool)->Result<')
probe = once(probe,
    ' let (same,d_same)=upload_u32(s,a,"same_p")?;let (c1,d_c1)=upload_u32(s,a,"pc1")?;let (c2,d_c2)=upload_u32(s,a,"pc2")?;let (slots,d_slots)=upload_u32(s,a,"cfv_slot")?;',
    ''' let (c1,d_c1)=upload_u32(s,a,"pc1")?;let (c2,d_c2)=upload_u32(s,a,"pc2")?;
 let original_same = words(&a["same_p"]);
 let mut same = original_same.clone();
 if encoded {
  let count = n(g,"nh_p");
  let packed = terminal_hand_words(&c1[..count], &c2[..count], &original_same[..count]);
  same[..count].copy_from_slice(&packed);
 }
 let d_same = s.clone_htod(&same)?;
 let (slots,d_slots)=upload_u32(s,a,"cfv_slot")?;''')
probe = once(probe, 'run_variant(&s,&bf,g,c,width,&active)?', 'run_variant(&s,&bf,g,c,width,&active,false)?')
probe = once(probe, 'run_variant(&s,&cf,g,c,width,&active)?', 'run_variant(&s,&cf,g,c,width,&active,true)?')
for old, new in [('cs.len(),2636', 'cs.len(),' + str(case_count)),
                 ('"comparison_pairs":13180', '"comparison_pairs":' + str(pairs)),
                 ('launches,26360', 'launches,' + str(launches)),
                 ('active_words,7645180', 'active_words,' + str(active_words)),
                 ('guard_checks,63032880', 'guard_checks,' + str(guards)),
                 ('input_checks,553560', 'input_checks,' + str(pairs * 42))]:
    expected = 2 if old == '"comparison_pairs":13180' else 1
    assert probe.count(old) == expected, old
    probe = probe.replace(old, new)
write_reuse((G / 'probe.rs'), probe.encode())
shutil.copyfile(B / 'accepted-evaluator.rs', G / 'accepted-evaluator.rs')

audit = (B / 'audit.py').read_text().replace('E120', 'E121')
audit = once(audit,
    "     actual=snapshot['actual_device_words'];req(actual==expected,'complete actual '+label+' '+short+' image matches explicit expected bits');word_count+=len(actual)",
    '''     actual=snapshot['actual_device_words']
     if label=='candidate' and short=='same':
      packed=list(expected)
      for hand in range(g['nh_p']):
       one=g['arrays']['pc1'][hand];two=g['arrays']['pc2'][hand];index=expected[hand]
       req(one<52 and two<52 and(index==0xffffffff or index<g['nh_o']),'original hand descriptor domain')
       packed[hand]=one|(two<<6)|((2047 if index==0xffffffff else index)<<12)
      req(actual==packed,'every physical encoded same word, no omissions')
      for hand in range(g['nh_p']):
       word=actual[hand]
       req(word<0x800000 and word&63==g['arrays']['pc1'][hand] and(word>>6)&63==g['arrays']['pc2'][hand],'actual packed cards decode original')
       req((0xffffffff if word>>12==2047 else word>>12)==expected[hand],'actual packed index decodes original')
     else:req(actual==expected,'complete actual '+label+' '+short+' image matches explicit expected bits')
     word_count+=len(actual)''')
audit = once(audit,
    "   req(all(x['actual_device_words']==y['actual_device_words']for x,y in zip(bs,cs)),'all21 actual metadata buffers byte-identical')",
    "   req(all(x['actual_device_words']==y['actual_device_words'] for x,y in zip(bs,cs) if x['buffer']!='same'),'all20 unchanged input buffers byte-identical; every encoded same word separately checked and decoded')")
audit = audit.replace('12140', str(pairs)).replace('13180', str(pairs)).replace('26360', str(launches))
audit = audit.replace('pass_scoped_full_sparse_card_raw_equivalence', 'pass_scoped_encoded_hand_word_full_raw_equivalence')
audit = audit.replace("'all21_input_buffers_identical':True", "'all21_input_buffers_fully_checked':True,'all20_unchanged_buffers_identical':True,'encoded_same_all_words_checked_and_decoded':True")
audit = audit.replace('all21metadata inputs byte-identical', 'all20unchangedmetadata inputs byte-identical andeveryencoded same wordfullychecked/decoded')
ast.parse(audit)
write_reuse((G / 'audit.py'), audit.encode())
execute = (B / 'execute.py').read_text().replace('E120', 'E121').replace('13183', str(pairs + 3)).replace('13180', str(pairs)).replace('26360', str(launches))
ast.parse(execute)
write_reuse((G / 'execute.py'), execute.encode())

for folder in [F, G]:
    shutil.copyfile(S / 'host-encode.rs', folder / 'host-encode.rs')
    for arm in ['baseline', 'candidate']:
        shutil.copyfile(S / (arm + '.cu'), folder / (arm + '.cu'))
        source = R / ('baseline-compute_120.ptx' if arm == 'baseline' else 'execution/candidate-compute_120.ptx')
        h.pin(source, h.read(R / 'report.json')['PTX_sha256'][arm + '-compute_120'])
        shutil.copyfile(source, folder / (arm + '.ptx'))

common_files = [Path(__file__), R / 'protocol.json', R / 'report.json', R / 'host-encode-report.json',
                ROOT / 'runs/D296-hand-word-PTX/report.json', ROOT / 'runs/D297-hand-word-native/report.json',
                ROOT / 'runs/E121-source/manifest.json', ROOT / 'epoch/common.py']
dependencies = [path for path in (ROOT / 'reference/accepted-e080-deps').iterdir() if path.is_file()]

fold_parent = h.read(A / 'protocol.json')
fold_protocol = {key: copy.deepcopy(value) for key, value in fold_parent.items() if key != 'input_sha256'}
def remap(value):
    if isinstance(value, str):
        return value.replace('D291-static-fold-control', 'D298-hand-word-fold').replace('D291', 'D298')
    if isinstance(value, list):
        return [remap(row) for row in value]
    if isinstance(value, dict):
        return {remap(key): remap(row) for key, row in value.items()}
    return value
fold_protocol = remap(fold_protocol)
fold_protocol.update(id='D298', at=h.now(), status='FROZEN_PRE_COMPILER_AND_FIRST_APPLICATION_KERNEL', cases=380, kernel_launches=760)
fold_protocol['audit_command'][1] = str(F / 'audit.py')
fold_protocol['failure'] = 'Any genuine output/input/guard/encoding/ABI/numerical failure closes the one fixed E121 form. All original360cases plus20descriptor-boundarycases retained. No source/sentinel/mask/width/architecture/helper/flags/quality/sample rescue. Entire encoded same prefix independently decoded; no blanket input exemption. New controls remain unscored.'
fold_protocol['physical_input_mapping'] = 'Candidate same_p valid hand prefix only: low6card1/next6card2/upper11matchingindex/2047sentinel. Every physical word checked; empty/dummy/padding words unchanged. Other13 actual immutable buffers byte-exact. Whole outputs and guards literal equal.'
files = common_files + dependencies + [fold_executor, A / 'protocol.json', A / 'corpus.json', A / 'probe.rs', A / 'audit-r2.py'] + list(F.iterdir())
h.save(F / 'preparation.json', {'at': h.now(), 'input_sha256': {p.name: h.sha(p) for p in F.iterdir() if p.is_file()}, 'scope': fold_protocol['physical_input_mapping']})
files.append(F / 'preparation.json')
fold_protocol['input_sha256'] = {str(path): h.sha(path) for path in files}
h.save(F / 'protocol.json', fold_protocol)

parent = h.read(B / 'protocol.json')
files = common_files + dependencies + [B / name for name in ['protocol.json', 'corpus.json', 'probe.rs', 'audit.py', 'execute.py']] + list(G.iterdir())
h.save(G / 'protocol.json', {
    'id': 'E121-show-control', 'at': h.now(), 'status': 'FROZEN_PRE_COMPILER_AND_FIRST_APPLICATION_KERNEL',
    'rustc_command': [value.replace(str(B), str(G)) for value in parent['rustc_command']],
    'input_sha256': {str(path): h.sha(path) for path in files}, 'resource_report': str(R / 'report.json'),
    'native_mechanism_report': str(ROOT / 'runs/D297-hand-word-native/report.json'),
    'widths': [1, 32, 64, 128, 256], 'base_cases': case_count, 'geometries': 244,
    'original_cases_retained_exact': 2636, 'added_single_opponent_cases': len(added),
    'expected_pairs': pairs, 'expected_application_launches': launches,
    'expected_active_words': active_words, 'expected_guard_word_checks': guards,
    'sealed_PTX_sha256': {arm: h.sha(G / (arm + '.ptx')) for arm in ['baseline', 'candidate']},
    'scope': 'Entire original E1202636cases/244physical geometries/rankoracle/anti-vacuity/2roundingwitnesses retained. Added full-range single-opponent reaches at physical extrema/511/1023 boundaries, unit/subnormal weights, bothplayers/boards. Only candidate same_p prefix encoded; all21physicalinputbuffers fullychecked, allencodedwords decodedtooriginal3fields, other20literalidentical. Fullphysicaloutputs/guards bitwiseequal. No omittedfield/padding/NaN/roundingtolerance. Any genuine failure closes fixedE121form without source/sentinel/mask/width/architecture/helper/flags/quality/sample rescue. No NVRTC rerun/sourceactivation/solver/speed.',
    'admission_free_bytes': shutil.disk_usage(ROOT).free, 'raw_output_cap_bytes': 8 * 1024**3,
    'peak_reservation_bytes': 32 * 1024**3, 'minimum_free_bytes': 64 * 1024**3,
    'candidate_adopted': False, 'performance_measurement': False
})

wrapper = ROOT / 'runs/E121-run-direct.py'
assert not wrapper.exists()
code = '''import sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==3;F=ROOT/'runs/D298-hand-word-fold';G=ROOT/'runs/E121-show-control';h.pin(F/'protocol.json',sys.argv[1]);h.pin(G/'protocol.json',sys.argv[2]);h.custody();O=ROOT/'runs/E121-direct-execution';O.mkdir(exist_ok=False)
h.child([sys.executable,str(ROOT/'runs/D298-execute-hand-word-fold.py'),sys.argv[1]],O,'fold',1200);h.custody()
h.child([sys.executable,str(G/'execute.py'),sys.argv[2]],O,'show',1200);h.custody()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());h.child([sys.executable,str(G/'audit.py')],O,'show-reader',1200);h.custody()
q=ROOT/'comparisons/E121-kernel-control-root-check/report.json';r=h.read(q);assert r['status']=='pass_scoped_encoded_hand_word_full_raw_equivalence'
dst=h.ar.DASHBOARD/'evidence'/q.parent.name/q.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(q,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+q.parent.name+'/'+q.name,timeout=20)as z:assert z.read()==q.read_bytes()
h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'fold_protocol_sha256':sys.argv[1],'show_protocol_sha256':sys.argv[2],'fold_report_sha256':h.sha(ROOT/'comparisons/D298-hand-word-fold/report.json'),'show_report_sha256':h.sha(q),'application_results_not_timing_samples':True,'candidate_adopted':False});h.custody();print('Both full direct terminal matrices passed.',flush=True)
'''
ast.parse(code)
wrapper.write_bytes(code.encode())
# The wrapper is an execution owner; pin it separately before either native process.
run_plan = ROOT / 'runs/E121-direct-plan'
run_plan.mkdir(exist_ok=False)
h.save(run_plan / 'protocol.json', {'at': h.now(), 'status': 'FROZEN_PRE_DIRECT_OWNER',
    'input_sha256': {str(path): h.sha(path) for path in [wrapper, F / 'protocol.json', G / 'protocol.json']},
    'fold_protocol_sha256': h.sha(F / 'protocol.json'), 'show_protocol_sha256': h.sha(G / 'protocol.json'),
    'scope': 'Exactly one foldcompiler/process/fullreader, one showcompiler/process/fullreader, serialGPUlock. Full original cohorts and prospective extra cases. Close fixed E121 on genuine failure; no completed native repeat for mechanical reader repair.'})
for path in [F / 'protocol.json', G / 'protocol.json', run_plan / 'protocol.json']:
    key = path.parent.name + '/' + path.name
    destination = h.ar.DASHBOARD / 'evidence' / key
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists()
    shutil.copyfile(path, destination)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
        assert response.read() == path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    experiment = next(row for row in status['experiments'] if row['id'] == 'E121')
    experiment.update(stage='Frozen complete direct fold/show GPU controls', reason=f'380 foldpairs/760launches and {pairs} showdownpairs/{launches}launches; every actual encoded word decoded, all other inputs/wholeoutputs/guards exact. No numerical or speed result yet.')
    experiment['evidence'] += [{'label': label, 'url': 'evidence/' + path.parent.name + '/protocol.json'} for label, path in [('Fold matrix and mapping', F / 'protocol.json'), ('Showdown matrix and mapping', G / 'protocol.json')]]
    status.update(updated_at=h.now(), stage=experiment['stage'], activity=experiment['reason'])
    h.ar.atomic_json(h.ar.STATUS, status)
h.custody()
print(json.dumps({'fold_protocol_sha256': h.sha(F / 'protocol.json'), 'show_protocol_sha256': h.sha(G / 'protocol.json'), 'owner_plan_sha256': h.sha(run_plan / 'protocol.json'), 'show_cases': case_count, 'show_pairs': pairs, 'show_added_cases': len(added)}), flush=True)
