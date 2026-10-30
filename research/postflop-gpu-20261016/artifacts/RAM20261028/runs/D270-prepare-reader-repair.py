"""Additive read-only repair; preserve completed native cases and original forecast."""
import ast, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
H=ROOT/'runs/D270-actual-metadata-CPU';P=h.read(H/'protocol.json')
assert not(ROOT/'gpu-run.lock').exists()and not(H/'root-report.json').exists()
for label,code in [('compile',0),('native',0),('reader',1)]:assert h.read(H/'execution'/(label+'.exit.json'))['returncode']==code
stderr=(H/'execution/reader.stderr.log').read_text(encoding='utf-8');assert 'assert seen==expected' in stderr
old=ROOT/'runs/D270-root-replay.py';text=old.read_text(encoding='utf-8')
def replace(before,after):
    global text
    assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after)
replace('assert len(sys.argv)==2','assert len(sys.argv)==3')
replace("for path,digest in P['input_sha256'].items():h.pin(path,digest)","""for path,digest in P['input_sha256'].items():h.pin(path,digest)
h.pin(H/'reader-repair-protocol.json',sys.argv[2]);R=h.read(H/'reader-repair-protocol.json')
for path,digest in R['input_sha256'].items():h.pin(path,digest)""")
replace("    na=io.vec(raw['node_na'],'I');players=io.vec(raw['node_player'],'I');data=io.vec(raw['node_data_off'],'Q')", "    na=io.vec(raw['node_na'],'I');players=io.vec(raw['node_player'],'I');data=io.vec(raw['node_data_off'],'Q');chance=io.vec(raw['node_cdiv'],'I')")
replace("    expected={i for i in range(nn)if na[i]>0 and players[i]==player}if a[16]else set()", "    expected={i for i in range(nn)if na[i]>0 and chance[i]==0 and players[i]==player}if a[16]else set()")
replace("rows=[];negative=[];checks=plan_bytes=projection_words=arena_bytes=guards=0", "rows=[];negative=[];checks=plan_bytes=projection_words=arena_bytes=guards=0;derived_selected_cases=0;eligibility=[]")
replace("    assert len(original_locks)==nn\n    for arm in P['arms']:", """    assert len(original_locks)==nn
    # Independent original-data oracle: chance nodes have positive cdiv, even
    # though their patched child count is52. Action allocation is in CPU node
    # reservation order (tree.rs); reproduce only its exact integer offsets.
    old_na=io.vec(original['node_na'],'I');old_player=io.vec(original['node_player'],'I')
    old_cdiv=io.vec(original['node_cdiv'],'I');old_data=io.vec(original['node_data_off'],'Q')
    nh=struct.unpack('<QQQ',original['nh']);ae=struct.unpack('<QQQ',original['arena_elements']);assert nh[0]==ae[0]==2
    physical=[0,0];offset_mismatch=[False,False];action_counts=[0,0];chance_counts=0
    for node in range(nn):
        if old_cdiv[node]!=0:
            assert old_na[node]==52;chance_counts+=1
        elif old_na[node]>0:
            player=old_player[node];assert player in[0,1];action_counts[player]+=1
            offset_mismatch[player]|=old_data[node]!=physical[player]
            physical[player]+=old_na[node]*nh[player+1]
    compact_expected=[ae[p+1]!=physical[p]or offset_mismatch[p]for p in range(2)]
    assert max(8*nn,4*len(original_children))<=4*max(ae[1:])
    selected_expected=all(compact_expected);derived_selected_cases+=selected_expected
    eligibility.append({'id':case['id'],'CPU_action_counts':action_counts,'chance_nodes':chance_counts,'original_CPU_arena_elements':physical,'plan_arena_elements':list(ae[1:]),'offset_mismatch':offset_mismatch,'independently_derived_compact':compact_expected,'independently_derived_selected':selected_expected})
    for arm in P['arms']:""")
replace("        ordered=arm!='selected'or marker['capable']", "        assert marker['compact']==compact_expected and marker['capable']==selected_expected and marker['scratch_elements']==max(ae[1:])\n        ordered=arm!='selected'or selected_expected")
replace("assert len(rows)==18 and sum(r['ordered']for r in rows)==16 and len(negative)==50", """assert len(rows)==18
expected_ordered=2*len(P['fixtures'])+derived_selected_cases;expected_fallback=len(P['fixtures'])-derived_selected_cases
assert sum(r['ordered']for r in rows)==expected_ordered and sum(not r['ordered']for r in rows)==expected_fallback
assert len(negative)==3*expected_ordered+expected_fallback""")
replace("h.save(H/'root-report.json',", "h.save(H/'root-report-r2.json',")
replace("'status':'pass_full_actual_production_CPU_metadata_replay_only'", "'status':'pass_full_actual_production_CPU_metadata_replay_corrected_reader_only','reader_repair_protocol_sha256':sys.argv[2],'original_16ordered_2fallback_forecast_not_met':True,'original_protocol_literal_forecast_pass_claimed':False,'independent_original_input_eligibility':eligibility,'ordered_cases':expected_ordered,'fallback_cases':expected_fallback,'source_case_or_predicate_changes':0")
replace("'ordered':16,'fallbacks':2,'negative_fixtures':50", "'ordered':expected_ordered,'fallbacks':expected_fallback,'negative_fixtures':len(negative)")
ast.parse(text)
dest=ROOT/'runs/D270-root-replay-r2.py'
with dest.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
runner=ROOT/'runs/D270-execute-reader-repair.py';ast.parse(runner.read_text(encoding='utf-8'))
paths=[Path(__file__),old,dest,runner,H/'protocol.json',H/'fixtures.json',H/'execution/build-manifest.json',H/'execution/compile.exit.json',H/'execution/native.exit.json',H/'execution/native.stdout.log',H/'execution/reader.exit.json',H/'execution/reader.stderr.log',H/'execution/reader.stdout.log',H/'execution/restoration.json',h.REPO/'crates/solver/src/tree.rs',h.REPO/'crates/solver/src/gpu/plan.rs',ROOT/'runs/E115-source-v2/manifest.json']
h.save(H/'reader-repair-protocol.json',{'id':'D270-reader-repair','at':h.now(),'status':'FROZEN_PRE_ADDITIVE_READ_ONLY_REPLAY','original_protocol_sha256':h.sha(H/'protocol.json'),'input_sha256':{str(p):h.sha(p)for p in paths},
 'error_evidence':'Original reader classifies all node_na>0 as action nodes; actual source tree.rs patches chance child count52. Original plan.rs sets positive node_cdiv only for chance, so exclude positive cdiv for action oracle. Full native18 cases/record lookups passed, and first three whole plan/projection comparisons passed before reader failed at first real compact arena.',
 'forecast_correction':'Original16 ordered/2 river fallback forecast is false. Original plan.rs retains full action arenas when compact savings<5%; therefore rainbow and explicit-chance flops also have full layouts. Do not change E115 fixed both-compact predicate or inputs. Independently derive CPU action physical offsets from original node reservation order, kind via original cdiv, and original arena_elements/node_data_off. Require actual native capability and every compact flag to match that oracle for every case. Ordered/fallback totals and negative fixture counts are derived from all six immutable original plans, not selected from timing outcomes. Original forecast unmet is explicitly retained, not called an original-protocol pass.',
 'unchanged_gates':'Same18 completed native cases, no compiler/native/CUDA/solver/candidate/source/fixture/predicate/science/output changes or repetitions. All53 before/after fields, all23 arrays/every word, maps/physical values/full record/capacity/canary/48 boundary checks remain mandatory. Every ordered case has same3 negative fixtures, every actual identity fallback rejects nonidentity mapping. No numerical/resource/performance gate relaxed; all original GPU/full-cycle/1%/strictfixture/fresh16/material/holdout/cumulative/app gates remain.',
 'scope':'One repaired Python root reader only under serialization. Existing large outputs immutable; no repeat of any completed native case. Passing only establishes corrected full CPU replay, never GPU numerical/performance/adoption.'})
print(h.sha(H/'reader-repair-protocol.json'),flush=True)
