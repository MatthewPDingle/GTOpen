"""Independent complete raw replay for the fixed E121 five-width showdown matrix."""
from pathlib import Path
import bisect,collections,json,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'epoch'));import common as old
P=old.read(H/'protocol.json');C=old.read(H/'execution/complete.json');corpus=old.read(H/'corpus.json');checks=0
for p,h in P['input_sha256'].items():old.pin(p,h)
old.pin(H/'execution/raw-results.jsonl',C['raw_sha256'])
def req(v,label):
 global checks
 assert v,label;checks+=1
fields=[('nodes','nodes'),('win','node_twin'),('lose','node_tlose'),('tie','node_ttie'),('river','node_river_slot'),('rsrc','rsrc_o'),('reach',None),('po','p_off'),('pc','p_cnt'),('pi','p_idx'),('pl','p_lower'),('pu','p_upper'),('oo','o_off'),('oc','o_cnt'),('oi','o_idx'),('co','o_card_off'),('cp','o_card_pos'),('same','same_p'),('c1','pc1'),('c2','pc2'),('slots','cfv_slot')]
geometries={g['id']:g for g in corpus['geometries']};total=collections.Counter();raw=H/'execution/raw-results.jsonl'
with raw.open(encoding='utf-8')as f:
 for width in P['widths']:
  for case in corpus['cases']:
   line=f.readline();req(bool(line),'full raw record present');d=json.loads(line);row=d['record'];g=geometries[case['geometry']]
   req(row['stage']=='full_show_exact'and row['case_id']==case['id']and row['threads']==width and row['geometry']==g['id'],'fixed complete case/width order')
   req(all(row[k]==g[k]for k in ['m_p','m_o','nh_p','nh_o']),'actual geometry')
   req(row['profile']==case['profile']and row['count']==case['count'],'actual profile/count')
   before=d['baseline_output_bits'];after=d['candidate_output_bits'];initial=g['output_initial'];req(before==after,'entire physical CFV outputs bitwise equal')
   req(len(before)==len(after)==len(initial),'complete output geometry')
   active=[False]*len(initial)
   if case['count']:
    for node in [2,5]:
     start=g['arrays']['cfv_slot'][node]*g['nh_max'];active[start:start+g['nh_p']]=[True]*g['nh_p']
   req(active==[bool(case['count'])and x for x in g['output_active']],'actual output ownership matches independent spans')
   for output in [before,after]:req(all(isinstance(x,int)and 0<=x<2**32 for x in output),'every output is a complete32bit image');req(all(x==seed for x,seed,owned in zip(output,initial,active)if not owned),'every nonowned/guard word exact')
   ac=sum(active);guards=2*(len(initial)-ac);words=[x for x,owned in zip(before,active)if owned]
   req(row['active_words']==ac and row['guard_word_checks']==guards,'active/guard inventory')
   req(all(x!=0x4b123456 for x in words),'active anti-stale guard overwritten')
   for label in ['baseline','candidate']:
    snapshots=d[label+'_actual_device_inputs'];req([x['buffer']for x in snapshots]==[x[0]for x in fields],'all21 actual device inputs present in order')
    word_count=0
    for snapshot,(short,key)in zip(snapshots,fields):
     expected=case['reach_o_bits']if key is None else g['arrays'][key]
     actual=snapshot['actual_device_words']
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
     word_count+=len(actual)
    total['device_input_word_checks']+=word_count;total['device_input_buffer_checks']+=21
   bs=d['baseline_actual_device_inputs'];cs=d['candidate_actual_device_inputs']
   req(all(x['actual_device_words']==y['actual_device_words'] for x,y in zip(bs,cs) if x['buffer']!='same'),'all20 unchanged input buffers byte-identical; every encoded same word separately checked and decoded')
   total['active_words_compared']+=ac;total['output_guard_word_checks']+=guards;total['full_output_words_both_arms']+=len(before)+len(after);total['comparison_pairs']+=1
   if not case.get('payout_test',False) and width==128 and case['count']and g['board_text']=='AsKsQsJsTs'and g['target_m']==257 and case['profile']=='sparse_rounding_witness':
    i=g['rounding_witness_own_index'];slot=g['arrays']['cfv_slot'][5];req(before[slot*g['nh_max']+i]==0xbe800000,'original128thread sparse rounding witness');total['rounding_witness_checks']+=1
 req(f.read()=='','no missing/extra raw records')
summary=C['summary']
for k in ['comparison_pairs','active_words_compared','output_guard_word_checks','device_input_buffer_checks','device_input_word_checks','rounding_witness_checks']:req(total[k]==summary[k],'root/native full '+k+' inventory')
req(total['comparison_pairs']==13300 and summary['kernel_launches']==26600 and summary['tested_block_widths']==P['widths'],'all predefined launches and widths')
req(summary['all_output_bits_exact']and summary['all_inputs_unchanged']and summary['performance_measurement']is False,'native summary scope')
old.custody();O=R/'comparisons/E121-kernel-control-root-check';assert not O.exists();O.mkdir()
report={'id':'E121-kernel-control','at':old.now(),'status':'pass_scoped_encoded_hand_word_full_raw_equivalence','checks':checks,'root_cross_check_only':True,'inventory':dict(total),'kernel_launches':26600,'tested_block_widths':P['widths'],'whole_physical_outputs_bitwise_equal':True,'all_actual_inputs_match_exact_expected':True,'all21_input_buffers_fully_checked':True,'all20_unchanged_buffers_identical':True,'encoded_same_all_words_checked_and_decoded':True,'raw_sha256':C['raw_sha256'],'raw_bytes':C['raw_bytes'],'protocol_sha256':old.sha(H/'protocol.json'),'source_main_live_PTX_custody_pass':True,'performance_measured':False,'candidate_accepted':False,'limits':'Finite declared13300pair corpus and root decoder, not universal NaN/illegal-address proof or external independent review. Same physical output geometry; all20unchangedmetadata inputs byte-identical andeveryencoded same wordfullychecked/decoded and every complete input image checked against the original explicit expected bits. Full solver/state/save/resume/material/speed qualification remains.'};old.save(O/'report.json',report);print(json.dumps({'status':report['status'],'checks':checks,'inventory':dict(total)}),flush=True)
