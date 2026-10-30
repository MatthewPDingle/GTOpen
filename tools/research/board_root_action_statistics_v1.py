"""All-class descriptive moments for paired, root-only action values."""
import math
from itertools import combinations
from board_root_action_decomposition_v1 import ACTIONS, NAMES, require

PAIRS = tuple(combinations(range(4), 2))
WIDTH = 21  # 12 action outcomes, six paired BB contrasts, three mixed outcomes


class Moments:
    def __init__(self):
        self.n = 0
        self.mean = [0.] * WIDTH
        self.m2 = [0.] * WIDTH

    def add(self, values):
        require(len(values) == WIDTH and all(math.isfinite(v) for v in values), 'Finite paired outcomes required')
        self.n += 1
        for k,x in enumerate(values):
            delta=x-self.mean[k]
            self.mean[k] += delta/self.n
            self.m2[k] += delta*(x-self.mean[k])

    def finish(self):
        se = [math.sqrt(max(0.,v)/(self.n-1)/self.n) if self.n > 1 else None for v in self.m2]
        means = self.mean if self.n else [None]*WIDTH
        return dict(evaluation_count=self.n, action_means=[means[k:k+3] for k in range(0,12,3)],
            action_standard_errors=[se[k:k+3] for k in range(0,12,3)],
            paired_BB_differences=[dict(action_a=ACTIONS[a], action_b=ACTIONS[b],
                mean_a_minus_b=means[12+k],standard_error=se[12+k]) for k,(a,b) in enumerate(PAIRS)],
            original_mixture_means=means[18:21], original_mixture_standard_errors=se[18:21])


class Summary:
    def __init__(self, expected_batches):
        self.expected = list(expected_batches)
        require(len(self.expected) == len(set(self.expected)) and self.expected, 'Unique ordered batches required')
        self.seen = []
        self.classes = [[Moments() for _ in range(169)] for _ in NAMES]
        self.overall = [Moments() for _ in NAMES]
        self.policies = [[None]*169 for _ in NAMES]

    def add(self, name, document):
        require(len(self.seen) < len(self.expected) and name == self.expected[len(self.seen)],
            'Duplicate, missing or reordered batch')
        require(tuple(p['name'] for p in document['profiles']) == NAMES, 'Unexpected profile order')
        reference_classes = None
        for p,profile in enumerate(document['profiles']):
            require(len(profile['deals']) == 32, 'Complete 32-deal batches required')
            current_classes=[]
            for i,row in enumerate(profile['deals']):
                c=row['native_class_index']; probs=row['root_probabilities']; q=row['action_values']
                require(row['deal_index'] == i and type(c) is int and 0 <= c < 169, 'Invalid deal identity')
                require(len(probs) == 4 and all(math.isfinite(v) and 0 <= v <= 1 for v in probs)
                    and abs(math.fsum(probs)-1) < 1e-12, 'Invalid root probabilities')
                require(len(q) == 4 and all(len(x) == 3 for x in q), 'All action outcomes required')
                old=self.policies[p][c]
                if old is None: self.policies[p][c]=list(probs)
                else: require(max(abs(a-b) for a,b in zip(old,probs)) < 1e-12, 'Root class policy changed')
                values=[x for action in q for x in action]
                values += [q[a][0]-q[b][0] for a,b in PAIRS]
                values += [math.fsum(probs[a]*q[a][k] for a in range(4)) for k in range(3)]
                self.classes[p][c].add(values);self.overall[p].add(values);current_classes.append(c)
            if reference_classes is None: reference_classes=current_classes
            else: require(current_classes == reference_classes, 'Profiles do not share physical deals')
        self.seen.append(name)

    def finish(self):
        require(self.seen == self.expected, 'Incomplete sample cannot produce final summary')
        return dict(format=1, action_order=ACTIONS, columns=['BB_bb_per_entry','BTN_bb_per_entry','expected_rake_bb'],
            deals=32*len(self.seen), batches=len(self.seen), all_classes_included=True,
            fresh_deals=0, exploratory=True, accuracy_qualified=False, bounds_best_response_above=False,
            uncertainty='Paired descriptive standard errors on reused evaluation deals; no registered discovery claims.',
            training_support='Per-observation own-reach support was not retained; evaluation counts are not training coverage.',
            profiles=[dict(name=name,overall=self.overall[p].finish(),classes=[
                dict(native_class_index=c,root_probabilities=self.policies[p][c],**self.classes[p][c].finish())
                for c in range(169)]) for p,name in enumerate(NAMES)])
