import copy
import unittest
from migrate_action_sizes import migrate_profile

def policy(size=None, multiple=None):
    result={'call':[.2]*169,'raise':[.3]*169,'jam':[.05]*169,'raise_size':'max'}
    if size is not None:result['raise_sizes']=size
    if multiple is not None:result['raise_multiples']=multiple
    return result

def dataset(p):
    return {'site':'test','min_players':3,'max_players':6,'ante':False,'empirical_opening':True,
            'small_blind_bb':.5,'contextual_reraise':'old-version','scope':'old note','response_notes':{},
            'rows':[{'players':6,'role':0,'open_raise':20,'open_limp':5,'iso_raise':30,'limp_behind':10,
                     'opening':policy([[2.5,1]]),'responses':{'raise':0,'squeeze':0}}],
            'response_policies':[copy.deepcopy(p)]}

def profile():
    p=policy()
    return {'name':'My player','buckets':[policy([[2.5,1]]),copy.deepcopy(p),copy.deepcopy(p),copy.deepcopy(p),copy.deepcopy(p)],
            'vs_raise_bands':[[2.5,copy.deepcopy(p)],[5,copy.deepcopy(p)]],
            'limp_defense':copy.deepcopy(p),'postflop':{'cbet_flop':62,'raise_vs_bet':9},
            'locks':{'private-test':'unchanged'},
            'response':{'adaptive_from':.25,'contextual_reraise':'active-old-version',
                        'cold_reraise':copy.deepcopy(p),'limp_unopened':copy.deepcopy(p),
                        'limp_contexts':[{'limpers':1,'free_check':False,'policy':copy.deepcopy(p)},
                                         {'limpers':1,'free_check':True,'policy':copy.deepcopy(p)}],
                        'source_stats':{'vpip':32.3,'raise_size':'max','dataset':dataset(p)}}}

def generated(old):
    new=copy.deepcopy(old)
    new['name']='Generated other name';new['response']['adaptive_from']=.7
    new['postflop']={'cbet_flop':99};new['locks']={}
    from migrate_action_sizes import _policy_map
    for path,p in _policy_map(new).items():
        if path != 'buckets/0':p['raise_multiples']=[[3,1]]
        p['raise_size']='min'
    d=new['response']['source_stats']['dataset'];d['scope']='new measured sizing'
    d['contextual_reraise']='unwanted-new-version';d['response_notes']={'sizes':'observed'}
    d['response_policies'][0]['raise_multiples']=[[3,1]]
    return new

class MigrationTests(unittest.TestCase):
    def test_pure_migration_preserves_every_non_size_field(self):
        old=profile();new=generated(old);snapshots=copy.deepcopy((old,new))
        result,summary=migrate_profile(old,new)
        self.assertEqual((old,new),snapshots)
        self.assertEqual(len(summary['updated']),11)
        self.assertEqual(summary['skipped'],[])
        self.assertTrue(summary['dataset_updated'])
        self.assertEqual(result['name'],old['name']);self.assertEqual(result['postflop'],old['postflop'])
        self.assertEqual(result['locks'],old['locks'])
        self.assertEqual(result['response']['adaptive_from'],.25)
        self.assertEqual(result['response']['contextual_reraise'],'active-old-version')
        self.assertEqual(result['response']['source_stats']['dataset']['contextual_reraise'],'old-version')
        self.assertEqual(result['buckets'][2]['raise_size'],'max')
        result['buckets'][2]['call'][0]=0
        self.assertEqual(old['buckets'][2]['call'][0],.2)
    def test_painted_hand_skipped_and_source_retained(self):
        old=profile();new=generated(old);old['buckets'][2]['raise'][42]=.1
        result,summary=migrate_profile(old,new)
        self.assertEqual(result['buckets'][2],old['buckets'][2])
        self.assertEqual(summary['skipped'][0]['path'],'buckets/2')
        self.assertFalse(summary['dataset_updated'])
        self.assertEqual(result['response']['source_stats']['dataset'],old['response']['source_stats']['dataset'])
    def test_manual_nonempty_mix_never_overwritten(self):
        old=profile();old['buckets'][2]['raise_multiples']=[[4,1]];new=generated(old)
        result,summary=migrate_profile(old,new)
        self.assertEqual(result['buckets'][2]['raise_multiples'],[[4,1]])
        self.assertIn('custom',summary['skipped'][0]['reason'])
    def test_verified_opening_can_change_but_manual_opening_cannot(self):
        old=profile();new=copy.deepcopy(old);new['buckets'][0]['raise_sizes']=[[3,1]]
        result,summary=migrate_profile(old,new)
        self.assertEqual(result['buckets'][0]['raise_sizes'],[[3,1]])
        old['buckets'][0]['raise_sizes']=[[7,1]]
        result,summary=migrate_profile(old,new)
        self.assertEqual(result['buckets'][0]['raise_sizes'],[[7,1]])
        self.assertTrue(summary['skipped'])
    def test_dataset_hand_change_or_entry_rate_blocks_replacement(self):
        for kind in ['hand','rate']:
            old=profile();new=generated(old);d=new['response']['source_stats']['dataset']
            if kind=='hand':d['response_policies'][0]['call'][0]=.1
            else:d['rows'][0]['open_raise']=21
            result,summary=migrate_profile(old,new)
            self.assertFalse(summary['dataset_updated'])
            self.assertEqual(result['response']['source_stats']['dataset'],old['response']['source_stats']['dataset'])
    def test_semantic_dataset_reindexing_allowed(self):
        old=profile();new=generated(old);d=new['response']['source_stats']['dataset']
        d['response_policies'].append(copy.deepcopy(d['response_policies'][0]));d['rows'][0]['responses']['squeeze']=1
        result,summary=migrate_profile(old,new)
        self.assertTrue(summary['dataset_updated'])
        self.assertEqual(result['response']['source_stats']['dataset']['rows'][0]['responses']['squeeze'],1)
    def test_band_and_limp_context_matching_uses_identity_not_order(self):
        old=profile();new=generated(old)
        new['vs_raise_bands'].reverse();new['response']['limp_contexts'].reverse()
        new['vs_raise_bands'][0][1]['raise_multiples']=[[5,1]]
        new['response']['limp_contexts'][0]['policy']['raise_multiples']=[[6,1]]
        result,_=migrate_profile(old,new)
        self.assertEqual(result['vs_raise_bands'][0][1]['raise_multiples'],[[3,1]])
        self.assertEqual(result['vs_raise_bands'][1][1]['raise_multiples'],[[5,1]])
        self.assertEqual(result['response']['limp_contexts'][0]['policy']['raise_multiples'],[[3,1]])
        self.assertEqual(result['response']['limp_contexts'][1]['policy']['raise_multiples'],[[6,1]])
    def test_explicit_jam_and_unknown_policies_retained(self):
        old=profile();old['buckets'][2]['raise_size']='jam';old['future_policy']=policy([[7,1]])
        result,summary=migrate_profile(old,generated(old))
        self.assertEqual(result['buckets'][2],old['buckets'][2]);self.assertEqual(result['future_policy'],old['future_policy'])
        self.assertTrue(any('jam' in item['reason'] for item in summary['skipped']))
    def test_idempotence_and_malformed_units_fail_closed(self):
        old=profile();new=generated(old);result,_=migrate_profile(old,new)
        twice,summary=migrate_profile(result,new)
        self.assertEqual(twice,result);self.assertFalse(summary['updated'])
        new['buckets'][1]['raise_sizes']=[[2,1]]
        with self.assertRaisesRegex(ValueError,'mutually exclusive'):migrate_profile(old,new)
    def test_contextual_opt_out_and_source_custom_mix_preserved(self):
        old=profile();del old['response']['source_stats']['dataset']['contextual_reraise'];new=generated(old)
        result,summary=migrate_profile(old,new)
        self.assertNotIn('contextual_reraise',result['response']['source_stats']['dataset'])
        old['response']['source_stats']['dataset']['response_policies'][0]['raise_multiples']=[[8,1]]
        result,summary=migrate_profile(old,new)
        self.assertFalse(summary['dataset_updated'])

if __name__=='__main__':unittest.main()
