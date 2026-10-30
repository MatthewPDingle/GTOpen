"""Freeze one observer-only full Spot data/phase measurement corpus."""
import ast,json,re,sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
scout=ROOT/'runs/D273-spot-construction-scout/report.json';s=h.read(scout);assert not s['literal_parallel_tree_river_hits_for_review']and not s['source_candidate_created']
H=ROOT/'runs/D274-spot-observation';H.mkdir(exist_ok=False)
game=h.REPO/'crates/solver/src/game.rs';original=game.read_bytes();text=original.decode('utf-8');assert '\r'not in text
a=text.index('    fn new_impl(');b=text.index('    /// Indices into suit_perms',a);method=text[a:b];profiled=method;edits=[]
def edit(before,after):
    global profiled
    assert profiled.count(before)==1,(before,profiled.count(before));at=profiled.index(before);profiled=profiled[:at]+after+profiled[at+len(before):];edits.append((at,before,after))
edit('    fn new_impl(', '    fn d274_profiled_new_impl(')
edit('    ) -> Result<Spot, String> {\n', '    ) -> Result<Spot, String> {\n        let d274_total=std::time::Instant::now();\n')
needle='        let tree = TreeBuilder::build_with_options('
edit(needle,'        let d274_tree=std::time::Instant::now();\n        D274_MARKS.with(|m|{let mut x=m.get();x.tree_started=true;m.set(x);});\n'+needle)
needle='        let river = build_river_table(&board, board_mask, &hands);'
edit(needle,'        D274_MARKS.with(|m|{let mut x=m.get();x.tree_ns=d274_tree.elapsed().as_nanos()as u64;m.set(x);});\n        let d274_river=std::time::Instant::now();\n        D274_MARKS.with(|m|{let mut x=m.get();x.river_started=true;m.set(x);});\n'+needle+'\n        D274_MARKS.with(|m|{let mut x=m.get();x.river_ns=d274_river.elapsed().as_nanos()as u64;m.set(x);});')
needle='        // Suit symmetry group:'
edit(needle,'        let d274_symmetry=std::time::Instant::now();\n        D274_MARKS.with(|m|{let mut x=m.get();x.symmetry_started=true;m.set(x);});\n'+needle)
edit('        Ok(Spot {','        let d274_result=Ok(Spot {')
needle='            hand_perm,\n        })'
edit(needle,'            hand_perm,\n        });\n        D274_MARKS.with(|m|{let mut x=m.get();x.symmetry_ns=d274_symmetry.elapsed().as_nanos()as u64;x.total_ns=d274_total.elapsed().as_nanos()as u64;m.set(x);});\n        d274_result')
back=profiled
for at,before,after in reversed(edits):assert back[at:at+len(after)]==after;back=back[:at]+before+back[at+len(after):]
assert back==method
template=ROOT/'runs/D274-observer.template.rs';adapter=template.read_text(encoding='utf-8');assert adapter.count('@PROFILED_METHOD@')==adapter.count('@FIXTURES@')==1
old=h.read(ROOT/'runs/D194-parent-chance-census/protocol.json');fixtures=[x['fixture']for x in old['raw_inputs']if x['fixture']['use_iso']];assert len(fixtures)==3
h.save(H/'fixtures.json',fixtures)
adapter=adapter.replace('@PROFILED_METHOD@',profiled).replace('@FIXTURES@',str(H/'fixtures.json'))
with(H/'observed-game.rs').open('xb')as f:f.write(original+adapter.encode())
(H/'baseline-game.rs').write_bytes(original)
spot_fields=re.findall(r'(?m)^    pub (\w+):',text[text.index('pub struct Spot {'):text.index('impl Spot {')]);assert spot_fields==['config','board','board_mask','tree','hands','weights','same_combo','river','suit_perms','hand_perm']
fields=['config_json','board','board_mask','tree_config_json','tree_root_street','tree_nodes','tree_children','tree_actions','tree_data_size','hands','weights','same_combo','river_root_street','river_entries','suit_perms','hand_perm','data_vector_capacities']
h.save(H/'schema.json',{'magic':'D274-SPOT-v1 +4nullbytes','field_order':fields,'Vec':'u64 length then every typed value','Array':'u64 fixed length then every value','Node':'<4B2I7Q,68bytes:kind/player/street/na,children/actions start,data offset,put arraylen=2/2f64bits,3payoff f64bits','HandInfo':'<BBIQ,14bytes:cards/weight f32bits/mask','Action':'u64 vectorlength;variant u8 fold0/check1/call2/bet3/raise4;last3 thenf64bits','River':'u64 entrycount;u8Option0/1;Some:arraylen2 and2vectors of u32strength/u16handindex pairs','Capacities':'board/tree.nodes/tree.children/tree.actions/river.entries/suit_perms;eachp hands/weights/same_combo/hand_perm outer andall inner capacities;then everySome river sorted vector capacities','actual_Spot_fields_covered':spot_fields,'No_raw_struct_padding_reads':True})
h.save(H/'source-review.json',{'at':h.now(),'actual_game_source_sha256':h.sha(game),'observer_file_sha256':h.sha(H/'observed-game.rs'),'original_entire_production_prefix_byte_exact':(H/'observed-game.rs').read_bytes()[:len(original)]==original,'appended_profiled_method_inverse_byte_exact':True,'method_edits':[{'position':i,'old':x,'new':y}for i,x,y in edits],'all17serializedfields_cover_entire_originalSpot_tree_andriver':True,'control':'Original Spot::new unchanged,only appended cfg(test) clone/timers/serializer/observer. One exact CPU observer test per fresh process, no other unit test executed. Both outputs native-compared andwritten in full outside clocks. Data-vector capacities included. No GPU/CFR/sourcecandidate or performance qualification.'})
runner=ROOT/'runs/D274-execute-observation.py';reader=ROOT/'runs/D274-root-observation.py'
for p in[Path(__file__),runner,reader]:ast.parse(p.read_text(encoding='utf-8'))
paths=[Path(__file__),runner,reader,template,scout,ROOT/'runs/D274-spot-observation-design-draft.json',ROOT/'runs/D194-parent-chance-census/protocol.json',ROOT/'comparisons/E115-three-pair-comparison/report.json',ROOT/'epoch/common.py',H/'fixtures.json',H/'schema.json',H/'source-review.json',H/'baseline-game.rs',H/'observed-game.rs',h.REPO/'crates/solver/src/tree.rs']
P={'id':'D274','at':h.now(),'status':'FROZEN_PRE_CPU_OBSERVER_COMPILER_AND_FIXED_FRESH_PROCESSES','input_sha256':{str(p):h.sha(p)for p in paths},'accepted_source_sha256':h.custody(),'owned_path':'crates/solver/src/game.rs','observed_path':str(H/'observed-game.rs'),'observed_sha256':h.sha(H/'observed-game.rs'),'baseline_path':str(H/'baseline-game.rs'),'baseline_sha256':h.sha(game),'target':str(ROOT/'build-d274-spot-observer'),'sequence':[{'id':'P1','order':'BO'},{'id':'P2','order':'OB'},{'id':'P3','order':'BO'}],'fixtures':fixtures,'schema_path':str(H/'schema.json'),'required_free_bytes':66*1024**3,'raw_reservation_bytes':8*1024**3,'required_available_RAM_bytes':32*1024**3,'worker_count':16,'error_cases':['budget0','budget1','budget100','bad_stack','bad_bet','bad_board','empty_range','impossible_ranges'],'expected_full_Spot_pairs':9,'expected_error_pairs':24,'planning_effort_constant_ms':100.521554,
 'scope':'One fresh offline/locked release CPU-only librarytest compiler withoriginalgame prefix andseparate cfgtest profiledclone.3fresh exacttest processes BO/OB/BO,eachoriginal3canonical Spot pairs/all17fields/nativeeveryvalue+fullrawoutsideclocks,8originalstrict validation/budget errors withno river/symmetry. Full arrays/config/typedfloatbits/sortedriver strength/hand/suit/children/actions/data offsets/data-vector capacity comparisons. No GPU features/API/context/kernel/Solver/CFR iterations or GPU/fullsolve/speed samples. Original production source restored before native;RAYON16/defaultaffinity. Callingcurrent_num_threads initializes globalpool beforeclocks,so freshprocess isnot coldpool orfullsolve latency.',
 'interpretation':'Fresh CPU observer only. Stage/envelope/wall clocks arefinite instrumented observations,codegen/cold/warm/cache/pool effects remain. Sum min(per-fixture medianTree,medianRiver) is an idealized overlap arithmetic planning proxy,not removabletime upperbound ormeasured parallel gain.100.521554ms isonly1%of freshB360-36210052.1554ms as an effort constant,no historical/current timing sample pooling. No source or optimization admission fromtimers alone. HistoricalD044/D110/D183 timing excluded.',
 'failure':'Every source reversal/native/raw/shape/bit/capacity/error/endpoint mandatory. Preserve observer/reader failures additively,no completed native case rerun. No extra/process/sample/order/quality/fixture/timing rescue. Prospective source muststill resolve realmax_nodes/error priority/speculative CPU work/join/panic/worker/FPU/peak costs andalloriginalcomplete1%/strictfixture/fresh16/broad/material/holdout/fresh-original/cumulative/app gates.'}
h.save(H/'protocol.json',P)
for name in['protocol.json','source-review.json','schema.json']:
    p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D274','title':'Fresh CPU Spot construction observations','kind':'diagnostic','status':'staged','accepted':False,'stage':'Original/profiler full Spot outputs andfixed3CPUprocesses frozen','reason':'Measure current serial tree/river effort without implementing overlap. Full Spot/tree/river/capacity/error comparisons mandatory; all GPU/full-cycle gates remain. No speed/candidate admission.','evidence':[{'label':n,'url':'evidence/'+H.name+'/'+n}for n in['protocol.json','source-review.json','schema.json']]});s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='D274',stage='Spot construction: fresh CPU observations',activity='Frozen3fresh CPU-only processes,all original3Spot configs/full output data/validation behavior. No GPU prototype or new performance samples. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
