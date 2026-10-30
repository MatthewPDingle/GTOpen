"""E030 host-only adaptation of frozen D036 full scenarios; no native calls."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,value):
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
    old_path=HERE/'original-d036-corpus.json'
    assert sha(old_path)=='265f74834e8d0b3506abb0b7229308f732ca8405387958fb0ae79528c9a2a217'
    old=json.loads(old_path.read_text());scenarios=[];pairs=[]
    totals={'comparison_pairs':0,'kernel_launches':0,'active_words_per_arm':0,'required_finite_words_per_arm':0,'output_words_per_arm':0,'output_guard_checks_both_arms':0,'input_buffer_checks_both_arms':0,'input_word_checks_both_arms':0}
    for s in old['full_scenarios']:
        s=dict(s);off=s['card_off'];idx=s['card_idx']
        assert len(off)==53 and off[0]==0 and off[-1]==len(idx)==2*s['nh_o']
        assert all(a<=b for a,b in zip(off,off[1:]))
        for c in range(52):assert idx[off[c]:off[c+1]]==[i for i,h in enumerate(s['opponent_hands']) if c in h]
        tasks=sorted(range(52),key=lambda c:(-(off[c+1]-off[c]),c))
        assert sorted(tasks)==list(range(52))
        s['candidate_card_off']=off+tasks
        assert s['candidate_card_off'][:53]==off and len(s['candidate_card_off'])==105
        assert {k:v for k,v in s.items() if k!='candidate_card_off'}==old['full_scenarios'][len(scenarios)]
        scenarios.append(s)
        base_words=sum([len(s['nodes']),3*len(s['node_meta']),len(s['rsrc0']),len(s['rsrc1']),len(s['reach0_bits']),len(s['reach1_bits']),max(1,len(s['pc1'])),max(1,len(s['pc2'])),53,max(1,len(idx)),max(1,len(s['same_p'])),len(s['cfv_slot'])])
        for block in [128,16,32,64,256]:
            for p in [0,1]:
                for count in ([s['count'],0] if s['id']=='n0-own1' else [s['count']]):
                    nodes=s['nodes'][s['start']:s['start']+count]
                    active=count*s['nh_p'];required=sum(s['nh_p'] for n in nodes if s['node_meta'][n]['required'])
                    pairs.append({'scenario':s['id'],'block':block,'p':p,'count':count,'active_words':active,'required_words':required,'guard_words_per_arm':s['cfv_words']-active,'input_words_both_arms':2*base_words+52})
                    totals['comparison_pairs']+=1;totals['kernel_launches']+=2;totals['active_words_per_arm']+=active;totals['required_finite_words_per_arm']+=required;totals['output_words_per_arm']+=s['cfv_words'];totals['output_guard_checks_both_arms']+=2*(s['cfv_words']-active);totals['input_buffer_checks_both_arms']+=28;totals['input_word_checks_both_arms']+=2*base_words+52
    assert totals=={'comparison_pairs':180,'kernel_launches':360,'active_words_per_arm':1771280,'required_finite_words_per_arm':1644760,'output_words_per_arm':4756170,'output_guard_checks_both_arms':5969780,'input_buffer_checks_both_arms':5040,'input_word_checks_both_arms':15887460}
    corpus={k:v for k,v in old.items() if k not in ['raw_cases','full_scenarios']}
    corpus.update(schema=2,source='D036 full scenarios byte-value preserved; candidate_card_off adds only52 task IDs; raw-total microkernel corpus omitted',full_scenarios=scenarios)
    write('corpus.json',corpus)
    write('corpus-summary.json',{'original_corpus_sha256':sha(old_path),'corpus_sha256':sha(HERE/'corpus.json'),'original_full_scenarios_preserved':17,'original_raw_microkernel_cases_executed':0,'totals':totals,'fixed_pair_order':pairs,'card_order':'descending list length, ascending card ID ties','baseline_offset_words':53,'candidate_offset_words':105,'production_block':128,'supplementary_blocks':[16,32,64,256],'compiler_native_gpu_executions':0})
    print(json.dumps({'corpus_sha256':sha(HERE/'corpus.json'),'totals':totals}))
if __name__=='__main__':main()
