import importlib.util, sys, tempfile, unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ig=load('ig_analyze','tools/ignition/analyze.py')
fit=load('ig_fit','tools/ignition/fit.py')
positions=load('ig_positions','tools/ignition/positions.py')
smoothing=load('ig_smoothing','tools/ignition/smoothing.py')
sizes=load('ig_sizes','tools/ignition/sizes.py')
contextual=load('ig_contextual','tools/ignition/contextual_reraise.py')

def hand(actions,total='0.25'):
    return '''Ignition Hand #1 TBL#1 HOLDEM No Limit - 2025-08-20 00:00:00
Seat 1: Small Blind ($10 in chips)
Seat 2: Big Blind ($10 in chips)
Seat 3: Dealer [ME] ($10 in chips)
Dealer [ME] : Set dealer [3]
Small Blind : Small Blind $0.05
Big Blind : Big blind $0.10
*** HOLE CARDS ***
Small Blind : Card dealt to a spot [As Ks]
Big Blind : Card dealt to a spot [2c 3d]
Dealer [ME] : Card dealt to a spot [Qh Qd]
'''+actions+'\n*** SUMMARY ***\nTotal Pot($'+total+')\n'

class Tests(unittest.TestCase):
    def test_source_selection_keeps_stakes_and_zone_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            names=['HH1 - RING - $0.05-$0.10 - HOLDEM.txt',
                'HH2 - ZONE - $0.05-$0.10 - HOLDEM.txt',
                'HH3 - RING - $0.02-$0.05 - HOLDEM.txt',
                'HH4 - ZONE - $0.02-$0.05 - HOLDEM.txt',
                'HH5 - RING - $0.10-$0.25 - HOLDEM.txt','notes.txt']
            for name in names:(Path(tmp)/name).write_text('')
            self.assertEqual([p.name for p in ig.source_paths(tmp)],names[:1])
            self.assertEqual([p.name for p in ig.source_paths(tmp,5)],names[2:3])
            self.assertEqual([p.name for p in ig.source_paths(tmp,5,True)],names[3:4])
            self.assertEqual([p.name for p in ig.source_paths(tmp,25)],names[4:5])
            self.assertEqual(ig.source_paths(tmp,25,True),[])

    def test_contextual_price_caps_short_stack_call(self):
        block=hand('Dealer [ME] : Raises $0.50 to $0.50\nSmall Blind : Raises $1.95 to $2\nBig Blind : All-in $0.90\nDealer [ME] : Folds','3.50').replace('Big Blind ($10 in chips)','Big Blind ($1 in chips)')
        canonical,_=ig.convert(block);_,cs=ig.cp.replay(canonical,10,variant='ignition')
        self.assertEqual(cs['Big Blind']['reraise_detail/3/BB/cold/3bet/0.257143/1.0000/9.0000|call'],1)

    def test_contextual_gradient_and_normalization(self):
        rows=np.array([[6,2,2,0,.3,2.5,97.5,168],[6,-2,0,1,.45,1,99,5],[4,0,1,0,.15,3,47,140]])
        x,names=contextual.features(rows,'hand_price');self.assertEqual(x.shape[1],len(names))
        p=np.array([[.01,.39,.6],[.95,.04,.01],[.3,.6,.1]]);y=np.array([[1.,2,3],[2,1,0],[0,2,1]])
        self.assertTrue(np.allclose(contextual.predict(x,p,np.zeros((x.shape[1],2))),p))
        v=np.random.default_rng(5).normal(0,.05,x.shape[1]*2)
        value,grad=contextual.objective(v,x,y,np.log(p),10)
        for j in [0,7,31,len(v)-1]:
            plus=v.copy();minus=v.copy();plus[j]+=1e-6;minus[j]-=1e-6
            numeric=(contextual.objective(plus,x,y,np.log(p),10)[0]-contextual.objective(minus,x,y,np.log(p),10)[0])/2e-6
            self.assertAlmostEqual(grad[j],numeric,places=5)
        w=contextual.fit(x,y,p,10);q=contextual.predict(x,p,w)
        self.assertTrue(np.isfinite(q).all());self.assertTrue((q>0).all());self.assertTrue(np.allclose(q.sum(1),1))

    def test_contextual_features_do_not_depend_on_outcomes(self):
        key='6/HJ/raised/3bet/0.300000/2.5000/97.5000/5'
        a=[dict(reraise_cells={key+'|fold':1})];b=[dict(reraise_cells={key+'|call':1})]
        ar,ay,_=contextual.observations(a);br,by,_=contextual.observations(b)
        self.assertTrue(np.array_equal(ar,br));self.assertFalse(np.array_equal(ay,by))
        self.assertTrue(np.array_equal(contextual.features(ar,'hand_price')[0],contextual.features(br,'hand_price')[0]))

    def test_reraise_audit_separates_cold_from_entered_and_depth(self):
        # BB first faces a 3-bet cold, raises, then faces a 5-bet after entering.
        block=hand('Dealer [ME] : Raises $0.25 to $0.25\nSmall Blind : Raises $0.85 to $0.90\nBig Blind : Raises $1.90 to $2\nDealer [ME] : Folds\nSmall Blind : Raises $3.10 to $4\nBig Blind : Calls $2','8.25')
        canonical,_=ig.convert(block);_,cs=ig.cp.replay(canonical,10,variant='ignition')
        bb=cs['Big Blind']
        self.assertEqual(bb['policy/3/BB/cold_reraise|raise'],1)
        self.assertEqual(bb['policy/3/BB/reraise|call'],1)
        self.assertEqual(bb['reraise_context/3/BB/cold/3bet/high|raise'],1)
        self.assertEqual(bb['reraise_context/3/BB/raised/4betplus/medium|call'],1)

    def test_open_size_projection_and_pooling(self):
        probs={2.:.4,2.6:.3,5.:.3}
        self.assertTrue(np.allclose(sizes.project(probs,[2,2.5,3,5]),[.4,.3,0,.3]))
        self.assertTrue(np.allclose(sizes.project(probs,[3]),[1.]))
        ss=[dict(counts={'opening_size/3/BTN|2.0000':8,'opening_size/3/SB|5.0000':2,
                         'opening_size/3/BTN|jam':1,'open_size|2.5':500})]
        rows,jams=sizes.counts(ss);self.assertEqual(jams,1)
        model,prior=sizes.fit(ss,2)
        self.assertAlmostEqual(sum(prior.values()),1)
        self.assertGreater(model[(3,0)][2.],model[(3,-1)][2.])
        self.assertTrue(all(set(p)=={2.,5.} for p in model.values()))

    def test_exact_first_in_size_excludes_isolation_raise(self):
        block=hand('Dealer [ME] : Raises $0.25 to $0.25\nSmall Blind : Folds\nBig Blind : Folds','0.40')
        canonical,_=ig.convert(block);_,cs=ig.cp.replay(canonical,10,variant='ignition')
        self.assertEqual(cs['Dealer [ME]']['opening_size/3/BTN|2.5000'],1)
        block=hand('Dealer [ME] : Calls $0.10\nSmall Blind : Raises $0.45 to $0.50\nBig Blind : Folds\nDealer [ME] : Folds','0.70')
        canonical,_=ig.convert(block);_,cs=ig.cp.replay(canonical,10,variant='ignition')
        self.assertFalse(any(k.startswith('opening_size/') for c in cs.values() for k in c))

    def test_hand_smoothing_does_not_inject_population_folds_into_aces(self):
        c=np.zeros((169,3));c[168,2]=10;c[154,2]=20;c[140,2]=20;c[0,2]=2
        c[12,0]=10000  # A2o must not become AA's prior.
        model=smoothing.fit({(6,-1,3):c},30,30,1)[(6,-1,3)]
        self.assertLess(model[168,0],.001)
        self.assertGreater(model[12,0],.99)
        self.assertTrue(np.allclose(model.sum(1),1))
        self.assertTrue(np.isfinite(model).all())
        self.assertGreater(model[168,0],0)  # No hard-coded never-fold premium rule.

    def test_free_check_smoothing_has_no_illegal_fold(self):
        c=np.zeros((169,3));c[168,2]=5;c[12,1]=20
        model=smoothing.fit({(6,-2,1):c},30,10,1,free=True)[(6,-2,1)]
        self.assertTrue((model[:,0]==0).all())
        self.assertTrue(np.allclose(model.sum(1),1))

    def test_position_transport_is_normalized_bounded_and_keeps_zero_distance(self):
        p=np.tile([.6,.1,.3],(169,1));slopes=np.array([[-.2,-.5],[-.1,-.4],[-.15,-.6]])
        q=positions.transport(p,slopes,2,1)
        self.assertTrue(np.allclose(positions.transport(p,slopes,0,1),p))
        self.assertTrue(np.allclose(q.sum(1),1))
        self.assertTrue((q[:,0]>p[:,0]).all())
        self.assertTrue(np.allclose(q,positions.transport(p,slopes,3,1)))
        self.assertFalse(np.allclose(q[0],q[13]))

    def test_hidden_table_filter_excludes_all_unavailable_positions(self):
        ss=[dict(id='test',cells={'4/CO/0|fold':2,'5/CO/0|call':3,'6/LJ/0|raise':7})]
        self.assertEqual(positions.subset(ss,4)[0]['cells'],{'4/CO/0|fold':2})
        self.assertEqual(len(ss[0]['cells']),3)

    def test_class_indices_match_rust_reference_labels(self):
        text=(ROOT/'crates/solver/src/preflop/reference.rs').read_text().split('pub const OPEN_SCORE:')[1].split('];')[0]
        import re
        labels=re.findall(r'// ([2-9TJQKA]{2}[so]?)',text)
        self.assertEqual(len(labels),169)
        for i,label in enumerate(labels):
            cards=(label[0]+'s',label[1]+('s' if label.endswith('s') else 'h'))
            self.assertEqual(ig.hand_index(cards),i,label)
        self.assertEqual(fit.COMBOS.sum(),1326)
        self.assertEqual(fit.COMBOS[ig.hand_index(('As','Ks'))],4)

    def test_allin_raise_and_partial_call_are_replayed(self):
        b=hand('''Dealer [ME] : All-in(raise) $10 to $10
Small Blind : Folds
Big Blind : All-in $9.90
*** FLOP *** [4s 5s 6s]
*** TURN *** [4s 5s 6s] [7s]
*** RIVER *** [4s 5s 6s 7s] [8s]''','20.05')
        canonical,cards=ig.convert(b);_,cs=ig.cp.replay(canonical,10,variant='ignition')
        self.assertEqual(cs['Dealer [ME]']['pre/open|raise'],1)
        self.assertEqual(cs['Big Blind']['pre/raise|call'],1)

    def test_unknown_cards_board_collisions_and_bad_delta_rejected(self):
        good=hand('Dealer [ME] : Raises $0.30 to $0.30\nSmall Blind : Folds\nBig Blind : Folds\nDealer [ME] : Return uncalled portion of bet $0.20','0.25')
        ig.cp.replay(ig.convert(good)[0],10,variant='ignition')
        for bad in [good.replace('[As Ks]','[As As]'),good.replace('Raises $0.30','Raises $0.20'),good.replace('*** SUMMARY ***','*** FLOP *** [As 4h 5h]\n*** SUMMARY ***')]:
            with self.assertRaises(ig.cp.Invalid):ig.convert(bad)

    def test_unseen_hand_borrows_training_only_and_probabilities_sum(self):
        sessions=[{'cells':{'6/BTN/168|raise':10,'6/BTN/1|fold':10}}]
        policies,hand,prior=fit.train(sessions,10,5)
        self.assertTrue(np.allclose(policies[(6,0)].sum(1),1))
        self.assertTrue(np.allclose(policies[(6,0)][50],hand[50]))
        self.assertEqual(fit.closest(policies,8,2),(6,0))

    def test_response_buckets_separate_prior_entry_and_cold_actions(self):
        b=hand('Dealer [ME] : Raises $0.30 to $0.30\nSmall Blind : Raises $0.95 to $1.00\nBig Blind : Folds\nDealer [ME] : Calls $0.70','2.10')
        _,cs=ig.cp.replay(ig.convert(b)[0],10,variant='ignition')
        self.assertEqual(cs['Small Blind']['policy/3/SB/raise_3.5|raise'],1)
        self.assertEqual(cs['Big Blind']['policy/3/BB/cold_reraise|fold'],1)
        self.assertEqual(cs['Dealer [ME]']['policy/3/BTN/reraise|call'],1)
        b=hand('Dealer [ME] : Raises $0.30 to $0.30\nSmall Blind : Calls $0.25\nBig Blind : Raises $1.10 to $1.20\nDealer [ME] : Folds\nSmall Blind : Folds\nBig Blind : Return uncalled portion of bet $0.90','0.90')
        _,cs=ig.cp.replay(ig.convert(b)[0],10,variant='ignition')
        self.assertEqual(cs['Big Blind']['policy/3/BB/squeeze|raise'],1)
        self.assertEqual(cs['Small Blind']['policy/3/SB/reraise|fold'],1)
        b=hand('Dealer [ME] : Calls $0.10\nSmall Blind : Raises $0.35 to $0.40\nBig Blind : Folds\nDealer [ME] : Folds\nSmall Blind : Return uncalled portion of bet $0.30','0.30')
        _,cs=ig.cp.replay(ig.convert(b)[0],10,variant='ignition')
        self.assertEqual(cs['Dealer [ME]']['policy/3/BTN/limp_defense|fold'],1)

    def test_response_collection_excludes_hero_and_keeps_folded_cards(self):
        import tempfile,json,contextlib,io
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'sample - $0.05-$0.10 - history.txt').write_text(hand('Dealer [ME] : Raises $0.30 to $0.30\nSmall Blind : Folds\nBig Blind : Folds\nDealer [ME] : Return uncalled portion of bet $0.20','0.25'))
            with contextlib.redirect_stdout(io.StringIO()):ig.run(root,root/'out')
            d=json.loads((root/'out/analysis.json').read_text());cells=d['sessions'][0]['policy_cells']
            self.assertFalse(any(k.startswith('open/') for k in cells))
            self.assertEqual(cells[f'raise/3/SB/{ig.hand_index(("As","Ks"))}|fold'],1)
            self.assertEqual(sum(v for k,v in cells.items() if k.startswith('raise/')),2)

    def test_limp_contexts_separate_completions_and_free_checks(self):
        for sb_action,count,total in [('Calls $0.05',2,'0.30'),('Folds',1,'0.25')]:
            b=hand('Dealer [ME] : Calls $0.10\nSmall Blind : '+sb_action+'\nBig Blind : Checks\n*** FLOP *** [4s 5s 6s]\n'+
                ('Small Blind : Checks\n' if count==2 else '')+'Big Blind : Checks\nDealer [ME] : Checks\n*** TURN *** [4s 5s 6s] [7s]\n'+
                ('Small Blind : Checks\n' if count==2 else '')+'Big Blind : Checks\nDealer [ME] : Checks\n*** RIVER *** [4s 5s 6s 7s] [8s]\n'+
                ('Small Blind : Checks\n' if count==2 else '')+'Big Blind : Checks\nDealer [ME] : Checks',total)
            _,cs=ig.cp.replay(ig.convert(b)[0],10,variant='ignition')
            self.assertEqual(cs['Small Blind']['limp/3/SB/complete/1|'+('call' if count==2 else 'fold')],1)
            self.assertEqual(cs['Big Blind'][f'limp/3/BB/free/{count}|call'],1)

if __name__=='__main__':unittest.main()
