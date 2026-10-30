import importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D281-zero-tie-scout';R=h.read(H/'report.json');h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
hits=R['literal_hits_for_manual_review'];assert len(hits)==11;literal='&& (__float_as_uint(tie) & 0x7f800000u) != 0x7f800000u) {';assert all(all(x['text']==literal for x in row['literal_hits'])for row in hits)
for row in hits:
    p=Path(row['identity']);h.pin(p,row['sha256']);text=p.read_text(encoding='utf-8');assert'int any_nonzero_bits = __syncthreads_or(reach_bits != 0);'in text and'if (!any_nonzero_bits)'in text
h.save(H/'hit-classification.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all11hits':'E036/E037positive-zero-reach shortcut variants/drafts. Matched line checks tie payoff finite, not zero tie payout, and onlyexecutesafterall-positive-zeroopponentrow predicate. Newproposalexplicitlyrequirespositivetotalandnonzerofiniteprefix, doesnotreuseentirerowskip/zerooutput logic.','closed_family_not_reopened':True,'source_candidate_created':False,'new_compilers_native_GPU_or_speed_samples':0})
old=ROOT/'comparisons/D272-metadata-canonical-v2/report.json';reference=h.read(old);spec=importlib.util.spec_from_file_location('d281_io',ROOT/'runs/D267b-model-io.py');io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io);schema_path=ROOT/'runs/D183-plan-phase-diagnostic/visibility-adapter/schema.json';schema=[n for n,t in h.read(schema_path)['fields']];extents={x['path']:x for x in reference['whole_original_CPU_plan_kind_map_extents']};results=[]
for fixture in['rainbow','two-tone','river']:
    p=ROOT/'runs/D272-metadata-canonical-v2/baseline-output'/(fixture+'-initial.map.plan.bin');pin=extents[str(p)];h.pin(p,pin['sha256']);assert p.stat().st_size==pin['bytes'];raw=io.plans(p,schema);show=io.vec(raw['show_nodes'],'I');ttie=io.vec(raw['node_ttie'],'I');win=io.vec(raw['node_twin'],'I');lose=io.vec(raw['node_tlose'],'I');slots=io.vec(raw['node_river_slot'],'i');counts=io.nested(raw['riv_cnt']);totals=[]
    for player in[0,1]:
        categories={'zero_tie_finite_payoffs_nonempty_supported_mo':0,'zero_tie_other_shape_or_nonfinite':0,'nonzero_or_nonfinite_tie':0}
        for node in show:
            assert 0<=slots[node]<len(counts[1-player]);mo=counts[1-player][slots[node]]
            if ttie[node]&0x7fffffff:categories['nonzero_or_nonfinite_tie']+=1
            elif(win[node]&0x7fffffff)<0x7f800000 and(lose[node]&0x7fffffff)<0x7f800000 and 0<mo<=1326:categories['zero_tie_finite_payoffs_nonempty_supported_mo']+=1
            else:categories['zero_tie_other_shape_or_nonfinite']+=1
        assert sum(categories.values())==len(show);totals.append({'player':player,'planned_show_CTAs':len(show),'categories':categories})
    results.append({'fixture':fixture,'whole_original_plan':pin,'full53field_endpoints_checked':True,'traversers':totals});print(fixture,totals,flush=True)
h.save(H/'static-payout-census.json',{'at':h.now(),'full_canonical_reference_sha256':h.sha(old),'schema_sha256':h.sha(schema_path),'IO_helper_sha256':h.sha(ROOT/'runs/D267b-model-io.py'),'all_original_planned_show_CTAs_both_traversers':results,'scope':'Read-only3wholeoriginal53fieldCPUplansalreadyfullcanonicalverified;actualnodepayoffbits/slots/opponentrivercounts. Counts onlystaticpayout/shapeeligibility, notruntimeboundedreach/positive-total/nonzero-prefix, iterationincidence, takenGPUbranches, removabletime/headroom orperformance. No new source/compiler/native/GPU/CFR/solve/speed samples.'});h.custody()
