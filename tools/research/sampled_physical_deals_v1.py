"""Resumable physical deal sampling with explicit panel or full-deck chance law.

The entry cutoff reproduces the frozen context convention; it is not a new
training-time support reduction. Folded players' private cards remain omitted.
"""
import copy
import hashlib
import itertools
import json

import numpy as np

from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES, COUNTS


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class PhysicalDeals:
    def __init__(self, context_source, *, mode, seed, manifest_source=None):
        if mode not in ('panel', 'full_deck'):
            raise ValueError('Explicit panel or full_deck mode required')
        if (mode == 'panel') != (manifest_source is not None):
            raise ValueError('Panel mode requires a manifest; full deck must not have one')
        if type(seed) is not int or seed < 0:
            raise ValueError('Explicit nonnegative seed required')
        context = json.loads(context_source)
        masses = np.asarray(context['incoming_class_mass'], dtype=np.float64)
        if masses.shape != (2,169) or not np.isfinite(masses).all() or np.any(masses < 0) or np.any(masses.sum(1) <= 0):
            raise ValueError('Two nonempty finite nonnegative entry ranges required')
        self.weights = masses[:,CLASSES]/COUNTS[CLASSES]
        self.weights /= self.weights.max(1)[:,None]
        self.weights[self.weights < 1e-5] = 0
        self.mode, self.context_sha256 = mode, digest(context_source)
        self.manifest_sha256 = digest(manifest_source) if manifest_source is not None else None
        self.rng = np.random.Generator(np.random.PCG64(seed))
        self.draws = 0
        self.permutations = list(itertools.permutations(range(4)))
        self.live, self.first, self.masses, self.boards = [], [], [], []
        rows = json.loads(manifest_source)['boards'] if mode == 'panel' else [dict(board='',weight=1.)]
        if not rows:
            raise ValueError('Empty board panel')
        nominal = []
        for row in rows:
            board, weight = row['board'], row['weight']
            if not np.isfinite(weight) or weight <= 0 or len(board) != (6 if mode == 'panel' else 0):
                raise ValueError('Invalid board or board weight')
            try:
                cards = [4*'23456789TJQKA'.index(board[i])+'cdhs'.index(board[i+1]) for i in range(0,len(board),2)]
            except ValueError as error:
                raise ValueError('Invalid board card') from error
            if len(set(cards)) != len(cards):
                raise ValueError('Duplicate board card')
            mask = sum(1<<c for c in cards)
            live = self.weights*((MASKS & np.uint64(mask)) == 0)
            counts = np.bincount(PAIRS.ravel(), weights=np.repeat(live[1],2), minlength=52)
            available = np.maximum(live[1].sum()-counts[PAIRS[:,0]]-counts[PAIRS[:,1]]+live[1],0)
            marginal = live[0]*available
            mass = float(marginal.sum())
            if not np.isfinite(mass) or mass <= 0:
                raise ValueError('No compatible private pair mass')
            self.live.append(live); self.first.append(marginal/mass)
            self.masses.append(mass); self.boards.append(cards); nominal.append(float(weight))
        self.board_probability = np.asarray(nominal)*self.masses
        if not np.isfinite(self.board_probability).all() or not np.isfinite(self.board_probability.sum()):
            raise ValueError('Board probability normalization overflow')
        self.board_probability /= self.board_probability.sum()

    def sample(self, count):
        if type(count) is not int or not 0 <= count <= 65536:
            raise ValueError('Bounded nonnegative deal count required')
        deals = []; board_ids = []
        for _ in range(count):
            b = int(self.rng.choice(len(self.boards),p=self.board_probability)) if self.mode == 'panel' else 0
            i = int(self.rng.choice(len(PAIRS),p=self.first[b]))
            second = self.live[b][1]*((MASKS & MASKS[i]) == 0)
            second /= second.sum()
            j = int(self.rng.choice(len(PAIRS),p=second))
            private = [int(c) for c in PAIRS[i]]+[int(c) for c in PAIRS[j]]
            if self.mode == 'panel':
                permutation = self.permutations[int(self.rng.integers(24))]
                physical = [4*(c//4)+permutation[c%4] for c in private+self.boards[b]]
                remaining = [c for c in range(52) if c not in physical]
                physical.extend(int(c) for c in self.rng.choice(remaining,size=2,replace=False))
            else:
                # Compatible physical private pairs first, then five shared public
                # cards uniformly without replacement. No fixed flop panel.
                physical = private
                remaining = [c for c in range(52) if c not in physical]
                physical.extend(int(c) for c in self.rng.choice(remaining,size=5,replace=False))
            physical[:2] = sorted(physical[:2]); physical[2:4] = sorted(physical[2:4])
            physical[4:7] = sorted(physical[4:7])
            assert len(set(physical)) == 9
            deals.append(physical); board_ids.append(b if self.mode == 'panel' else None)
        self.draws += count
        return dict(deals=deals, panel_board_indices=board_ids)

    def checkpoint(self):
        return dict(format=1,mode=self.mode,context_sha256=self.context_sha256,
                    manifest_sha256=self.manifest_sha256,numpy_version=np.__version__,
                    draws=self.draws,rng=copy.deepcopy(self.rng.bit_generator.state))

    @classmethod
    def restore(cls, checkpoint, context_source, manifest_source=None):
        if checkpoint['format'] != 1 or checkpoint['numpy_version'] != np.__version__:
            raise ValueError('Unsupported checkpoint or different NumPy runtime')
        result = cls(context_source,mode=checkpoint['mode'],seed=0,manifest_source=manifest_source)
        if (result.context_sha256 != checkpoint['context_sha256']
                or result.manifest_sha256 != checkpoint['manifest_sha256']):
            raise ValueError('Changed sampling context or panel')
        if type(checkpoint['draws']) is not int or checkpoint['draws'] < 0:
            raise ValueError('Invalid deal counter')
        result.rng.bit_generator.state = copy.deepcopy(checkpoint['rng'])
        result.draws = checkpoint['draws']
        return result
