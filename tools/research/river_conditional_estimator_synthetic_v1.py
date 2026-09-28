"""Exhaustive finite-game controls, not a native solver or poker-accuracy test."""
import argparse
from collections import defaultdict
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import time
import traceback
import uuid

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
NAME = 'river-conditional-estimator-synthetic-v1'
PLAN = OUT / 'BOARD-RIVER-ESTIMATOR-SYNTHETIC-PLAN.md'
REG = OUT / (NAME + '-registration.json')
RESULT = OUT / (NAME + '-result.json')
LIMIT = 180
TOL = 5e-10


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def publish(path, value):
    assert not path.exists()
    temporary = path.with_name('.partial-' + path.name + '-' + uuid.uuid4().hex)
    with temporary.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, separators=(',', ':'), allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.rename(temporary, path)


def verify(inputs):
    for path, expected in inputs.items():
        assert sha(path) == expected, path


def register():
    assert not REG.exists() and not RESULT.exists()
    accepted = OUT / 'board-river-deal-coverage-v1-evaluation.json'
    assert all(json.loads(accepted.read_text())['gates'].values())
    paths = [Path(__file__), PLAN, accepted,
             ROOT / 'crates/solver/examples/research_sampled/policy_walk_allin_v1.rs',
             ROOT / 'tools/research/weighted_physical_reservoir_v1.py',
             ROOT / 'tools/research/weighted_visible_objective_v1.py',
             ROOT / 'tools/research/sampled_physical_deals_v1.py',
             ROOT / 'tools/research/board_river_opponent_reach_math_v1.py']
    publish(REG, dict(inputs={str(p): sha(p) for p in paths}, maximum_seconds=LIMIT,
                     maximum_evidence_bytes=5_000_000, cpu_only=True,
                     native_or_production_modified=False, created_unix=time.time()))
    print(json.dumps(dict(registered=True, registration_sha256=sha(REG))), flush=True)


class Game:
    """Public stake-choice game with poker-like river decisions; not NLHE."""
    def __init__(self, rake):
        self.rake = rake
        self.nodes = {'root': (0, ('exit', 'L1', 'L2'))}
        self.leaves = {'exit': ('fold', 0, 1., False)}
        for lane, stake, bet in (('L1', 2., 3.), ('L2', 9., 11.)):
            self.nodes[lane] = (1, (lane + 'C', lane + 'B'))
            self.nodes[lane + 'B'] = (0, (lane + 'BF', lane + 'BC', lane + 'BR'))
            self.nodes[lane + 'BR'] = (1, (lane + 'BRF', lane + 'BRC'))
            self.leaves[lane + 'C'] = ('show', -1, stake, True)
            self.leaves[lane + 'BF'] = ('fold', 0, stake, True)
            self.leaves[lane + 'BC'] = ('show', -1, stake + bet, True)
            self.leaves[lane + 'BRF'] = ('fold', 1, stake + bet, True)
            self.leaves[lane + 'BRC'] = ('show', -1, stake + 3 * bet, True)
        self.prefix = {}; self.paths = []
        def walk(node, path):
            self.prefix[node] = path
            if node in self.leaves:
                self.paths.append((node, path)); return
            for a, child in enumerate(self.nodes[node][1]):
                walk(child, path + ((node, a),))
        walk('root', ())
        self.deals = list(itertools.permutations(range(8), 3))
        first = (1, 2, 1, 3, 2, 1, 3, 4); second = (4, 1, 3, 1, 2, 3, 1, 2)
        masses = [first[d[0]] * second[d[1]] / 6 for d in self.deals]
        total = math.fsum(masses); self.p = [m / total for m in masses]
        skew = [p * (1 + (d[0] + 3*d[1] + 2*d[2]) % 7) for d, p in zip(self.deals, self.p)]
        self.q = [v / math.fsum(skew) for v in skew]
        self.policy = {(d, n): self.sigma(d, n) for d in self.deals for n in self.nodes}
        self.values = {}; self.actions = {}; self.independent_max_error = 0.
        for d in self.deals:
            for actor in (0, 1):
                def recurse(node):
                    if node in self.leaves: return self.payoff(d, node, actor)
                    v = tuple(recurse(child) for child in self.nodes[node][1])
                    self.actions[d, actor, node] = v
                    value = math.fsum(x*y for x,y in zip(self.policy[d, node], v))
                    self.values[d, actor, node] = value
                    return value
                recurse('root')
                # Independent complete terminal-path sums, not recurse() reused.
                for n, (_, children) in self.nodes.items():
                    action = []
                    for a in range(len(children)):
                        terms = []
                        for terminal, path in self.paths:
                            if (n, a) not in path: continue
                            tail = path[path.index((n, a)) + 1:]
                            terms.append(math.prod(self.policy[d, k][j] for k,j in tail) * self.payoff(d, terminal, actor))
                        action.append(math.fsum(terms))
                    error = max(abs(x-y) for x,y in zip(action, self.actions[d, actor, n]))
                    self.independent_max_error = max(self.independent_max_error, error)
                    assert error < TOL
        self.conditionals = {}

    def sigma(self, d, node):
        actor = self.nodes[node][0]; rank = d[actor] // 2; board = d[2] // 2
        if node == 'root':
            enter = (.15, .5, .75, .9)[rank]
            return (1-enter, enter, 0.)  # Zero own reach is still counterfactually explored.
        if node in ('L1', 'L2'):
            bet = .95 if rank == board else (.001, .13, .57, .86)[rank]
            return (1-bet, bet)
        if node.endswith('BR'):
            fold = .02 if rank == board else (.8, .6, .4, .2)[rank]
            return (fold, 1-fold)
        return (.03, .27, .70) if rank == board else ((.87, .13, 0.), (.6, .35, .05), (.25, .60, .15), (.1, .6, .3))[rank]

    def payoff(self, d, terminal, actor):
        kind, folded, amount, river = self.leaves[terminal]
        rake = min(.08 * 2 * amount, 2.5) if self.rake and river else 0.
        if kind == 'fold': return -amount if actor == folded else amount-rake
        ranks = [((d[i]//2 == d[2]//2), d[i]//2) for i in (0, 1)]
        if ranks[0] == ranks[1]: return -rake/2
        winner = int(ranks[1] > ranks[0])
        return amount-rake if actor == winner else -amount

    def key(self, d, node):
        actor = self.nodes[node][0]
        return (node, d[actor], -1 if node == 'root' else d[2])

    def likelihood(self, d, node, actor, *, wrong=False, own=False):
        result = 1.
        for n, a in self.prefix[node]:
            if (self.nodes[n][0] == actor) != own: continue
            p = self.policy[d, n]
            if wrong:
                rotated = p[1:] + p[:1]
                p = tuple(.9*x + .1/len(p) for x in rotated)
            result *= p[a]
        return result

    def conditional(self, d, node, actor, flaw=None):
        key = (actor, self.key(d, node), flaw)
        if key in self.conditionals: return self.conditionals[key]
        weights = []; vectors = []
        for j, other in enumerate(self.deals):
            if self.key(other, node) != self.key(d, node): continue
            prior = self.q[j] if flaw == 'proposal_posterior' else self.p[j]
            history = 1. if flaw == 'omit_history' else self.likelihood(other, node, actor, wrong=flaw == 'wrong_policy')
            if flaw == 'own_reach': history *= self.likelihood(other, node, actor, own=True)
            weights.append(prior * history); vectors.append(self.actions[other, actor, node])
        mass = math.fsum(weights)
        # Only the intentionally wrong own-reach method may erase visited support.
        if mass == 0:
            assert flaw == 'own_reach'
            value = (0.,) * len(self.nodes[node][1])
        else:
            value = tuple(math.fsum(w*v[a] for w,v in zip(weights, vectors))/mass for a in range(len(vectors[0])))
        self.conditionals[key] = value
        return value

    def truth(self, actor):
        mass = defaultdict(float); numerators = {}; zero_own = set()
        for d, p in zip(self.deals, self.p):
            for node, (owner, _) in self.nodes.items():
                if owner != actor: continue
                key = self.key(d, node); w = p*self.likelihood(d, node, actor)
                v = self.actions[d, actor, node]; mean = self.values[d, actor, node]
                if key not in numerators: numerators[key] = [0.] * len(v)
                mass[key] += w
                for a, value in enumerate(v): numerators[key][a] += w*(value-mean)
                if w > 0 and self.likelihood(d, node, actor, own=True) == 0: zero_own.add(key)
        root = math.fsum(p*self.values[d, actor, 'root'] for d,p in zip(self.deals, self.p))
        return dict(mass=mass, numerators=numerators, root=root, zero_own=zero_own)


def walk(game, d, actor, node, mode, baseline='fixed', flaw=None):
    if node in game.leaves: return [(1., game.payoff(d, node, actor), ())]
    owner, children = game.nodes[node]; sigma = game.policy[d, node]
    if owner != actor:
        outcomes = []
        for a, child in enumerate(children):
            if sigma[a] == 0: continue
            for prob, value, records in walk(game, d, actor, child, mode, baseline, flaw):
                outcomes.append((sigma[a]*prob, value, records))
        return outcomes
    branches = [walk(game, d, actor, child, mode, baseline, flaw) for child in children]
    outcomes = []; key = game.key(d, node)
    for parts in itertools.product(*branches):
        probability = math.prod(p[0] for p in parts)
        records = sum((p[2] for p in parts), ())
        options = [(1., tuple(p[1] for p in parts))]
        if node != 'root' and mode != 'original':
            target = game.conditional(d, node, actor, flaw)
            options = [(1., target)]
            if mode in ('gated', 'uncorrected'):
                if baseline == 'oracle': b = target
                elif baseline == 'zero': b = (0.,) * len(target)
                else: b = tuple(-3 + 2*(d[actor]//2) + .4*(d[2]//2) + 5*a for a in range(len(target)))
                rho = .25 if node.startswith('L1') else .5
                options = [(1-rho, b), (rho, tuple(x+(y-x)/rho for x,y in zip(b, target)))]
                if mode == 'uncorrected': options = [(1., b)]
        for gate_probability, values in options:
            mean = math.fsum(p*v for p,v in zip(sigma, values))
            regret = tuple(v-mean for v in values)
            assert abs(math.fsum(p*r for p,r in zip(sigma, regret))) < TOL
            outcomes.append((probability*gate_probability, mean, records+((key, regret),)))
    return outcomes


def evaluate(game, actor, proposal, mode, baseline, flaw, deadline):
    distribution = game.p if proposal == 'matched' else game.q
    root_mean = root_second = 0.; mass = defaultdict(float); raw_visits = defaultdict(float)
    sums = {}; seconds = {}; traces = 0; normalization_error = 0.
    for d, p, q in zip(game.deals, game.p, distribution):
        assert time.monotonic() < deadline
        outcomes = walk(game, d, actor, 'root', mode, baseline, flaw)
        norm = abs(math.fsum(o[0] for o in outcomes)-1); normalization_error=max(normalization_error,norm)
        assert norm < TOL
        weight = p/q; effective = weight*weight if flaw == 'double_weight' else weight
        for prob, value, records in outcomes:
            traces += 1; chance = q*prob
            root_mean += chance*effective*value; root_second += chance*(effective*value)**2
            assert len({k for k,_ in records}) == len(records)
            for key, values in records:
                if key not in sums:
                    sums[key]=[0.]*len(values); seconds[key]=[0.]*len(values)
                mass[key] += chance*weight; raw_visits[key] += chance
                for a,v in enumerate(values):
                    sums[key][a] += chance*effective*v; seconds[key][a] += chance*(effective*v)**2
    truth=game.truth(actor); numerator_error=visit_error=0.; relative_error=0.
    for key, expected in truth['numerators'].items():
        got=sums.get(key,[0.]*len(expected))
        for a,(x,y) in enumerate(zip(got,expected)):
            numerator_error=max(numerator_error,abs(x-y)); relative_error=max(relative_error,abs(x-y)/max(1.,abs(y)))
        visit_error=max(visit_error,abs(mass[key]-truth['mass'][key]))
    root_error=abs(root_mean-truth['root']); relative_error=max(relative_error,root_error/max(1.,abs(truth['root'])))
    variance=math.fsum(max(0.,seconds[k][a]-sums[k][a]**2) for k in sums for a in range(len(sums[k])))
    zero_mass=math.fsum(truth['mass'][k] for k in truth['zero_own'])
    zero_signal=math.fsum(abs(x) for k in truth['zero_own'] for x in truth['numerators'][k])
    return dict(root_error=root_error, maximum_update_error=numerator_error, maximum_visit_mass_error=visit_error,
                maximum_scaled_error=relative_error, probability_error=normalization_error,
                root_mean=root_mean,root_variance=max(0.,root_second-root_mean**2), update_variance_sum=variance,
                supported_zero_own_keys=len(truth['zero_own']),zero_own_mass=zero_mass,zero_own_update_signal=zero_signal,
                traces=traces, infosets=len(sums), raw_visits=dict(raw_visits), weighted_visits=dict(mass))


def analyze():
    assert not RESULT.exists(); registration=json.loads(REG.read_text()); verify(registration['inputs'])
    began=time.monotonic(); deadline=began+LIMIT; rows=[]; negative=[]; reference_error=0.; zero_control=False
    for rake,actor in itertools.product((False,True),(0,1)):
        game=Game(rake); reference_error=max(reference_error,game.independent_max_error)
        tie_count=sum(d[0]//2 == d[1]//2 for d in game.deals); assert tie_count > 0
        assert len(game.deals)==336 and all(len(set(d))==3 for d in game.deals)
        assert abs(math.fsum(game.p)-1)<TOL and abs(math.fsum(game.q)-1)<TOL
        visible_policies={}
        for d in game.deals:
            for node in game.nodes:
                key=game.key(d,node)
                if key in visible_policies: assert visible_policies[key]==game.policy[d,node]
                visible_policies[key]=game.policy[d,node]
        assert len({game.key(d,'root') for d in game.deals})==8
        for who in (0,1):
            assert abs(game.payoff((0,1,2),'L1BC',who)-(-.4 if rake else 0.))<TOL
        assert game.payoff((6,0,4),'L2BRC',0)==(39.5 if rake else 42.)
        assert game.payoff((6,0,4),'L2BRC',1)==-42.
        assert game.payoff((6,0,4),'L1BF',0)==-2.
        assert abs(game.payoff((6,0,4),'L1BF',1)-(1.68 if rake else 2.))<TOL
        assert sum(game.payoff((6,0,4),'exit',who) for who in (0,1))==0.
        for proposal in ('matched','skewed'):
            reference=None
            for mode,baseline in (('original','fixed'),('conditional','fixed'),('gated','zero'),('gated','fixed'),('gated','oracle')):
                r=evaluate(game,actor,proposal,mode,baseline,None,deadline)
                assert r['maximum_scaled_error'] <= TOL and r['maximum_visit_mass_error'] <= TOL
                assert r['probability_error'] <= TOL
                if reference is None: reference=(r['raw_visits'],r['weighted_visits'])
                else:
                    for key,v in reference[0].items(): assert abs(v-r['raw_visits'][key]) <= TOL
                    for key,v in reference[1].items(): assert abs(v-r['weighted_visits'][key]) <= TOL
                if actor==0:
                    assert r['supported_zero_own_keys']>0 and r['zero_own_mass']>0 and r['zero_own_update_signal']>0
                    zero_control=True
                r.pop('raw_visits'); r.pop('weighted_visits')
                rows.append(dict(rake=rake,actor=actor,proposal=proposal,mode=mode,baseline=baseline,**r))
            for flaw in ('omit_history','proposal_posterior','double_weight','wrong_policy','own_reach','uncorrected_baseline'):
                mode='uncorrected' if flaw=='uncorrected_baseline' else 'conditional'
                r=evaluate(game,actor,proposal,mode,'fixed',flaw,deadline)
                negative.append(dict(rake=rake,actor=actor,proposal=proposal,flaw=flaw,
                                     root_error=r['root_error'],maximum_update_error=r['maximum_update_error']))
        print(json.dumps(dict(completed_fixture=dict(rake=rake,actor=actor),seconds=time.monotonic()-began)),flush=True)
    negative_checks={flaw:max(max(r['root_error'],r['maximum_update_error']) for r in negative if r['flaw']==flaw)>1e-6
                     for flaw in {r['flaw'] for r in negative}}
    assert all(negative_checks.values()) and zero_control
    # The oracle gated baseline must reproduce conditional replacement moments.
    for r in rows:
        if r['mode']=='gated' and r['baseline']=='oracle':
            ref=next(x for x in rows if x['mode']=='conditional' and all(x[k]==r[k] for k in ('rake','actor','proposal')))
            for metric in ('root_mean','root_variance','update_variance_sum'):
                assert abs(r[metric]-ref[metric]) <= TOL*max(1.,abs(ref[metric]))
    verify(registration['inputs']); assert time.monotonic()<deadline
    result=dict(passed=True,complete=True,registration_sha256=sha(REG),rows=rows,negative_controls=negative,
                negative_controls_detected=negative_checks,independent_terminal_path_maximum_error=reference_error,
                hand_calculated_tie_fold_cap_controls=True,visible_information_policy_consistency=True,
                seconds=time.monotonic()-began,full_deal_count=336,cpu_only=True,native_qualified=False,
                full_policy_or_preflop_accuracy_demonstrated=False)
    publish(RESULT,result);assert RESULT.stat().st_size+REG.stat().st_size<5_000_000
    print(json.dumps(dict(passed=True,rows=len(rows),negative_controls_detected=negative_checks,
                         seconds=result['seconds'],result=str(RESULT))),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('register','analyze'),required=True)
    args=parser.parse_args()
    try: register() if args.mode=='register' else analyze()
    except Exception as error:
        if args.mode=='analyze':
            publish(OUT/(NAME+'-failure-'+uuid.uuid4().hex+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
