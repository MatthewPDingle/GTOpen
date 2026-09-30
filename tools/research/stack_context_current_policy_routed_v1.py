"""Candidate: preserve current-policy semantics while routing preflop overlays.

This separate implementation is not wired into the registered study. Card,
public-context, history and network calculations are inherited unchanged.
"""
import numpy as np
from stack_context_current_policy_v1 import CurrentPolicy as OriginalPolicy
from sampled_physical_bank_v1 import histories


class CurrentPolicy(OriginalPolicy):
    def prepare(self, queries, *, require_history=True):
        if type(require_history) is not bool or queries['context_source'] != self.context_source:
            raise ValueError('Explicit history mode and matching native context required')
        obs = queries['observations']
        if require_history:
            if any('own_history' not in row for row in obs):
                raise ValueError('Native queries must retain actual own-history links')
            own = histories(obs)
        else:
            if any('own_history' in row for row in obs):
                raise ValueError('Score-only rows must not supply unchecked history links')
            if any(row['phase'] == 0 for row in obs):
                raise ValueError('Only fixed-board postflop rows may omit own-history links')
            own = None
        x, actor, arity, keys = self._features(obs)
        legal = np.arange(4)[None, :] < arity[:, None]
        table = legal.astype(np.float64)/arity[:, None]
        mask = np.zeros(len(obs), dtype=bool)
        if self.tables:
            # The original table contract rejects one-action rows even though
            # no preflop table can match postflop. Keep that rejection here.
            # _features already checks canonical keys/phase/actor/legal menus;
            # the freshly constructed postflop table rows are valid uniforms.
            if np.any(~np.isin(arity, (2, 3, 4))):
                raise ValueError('Invalid input actor or legal action probabilities')
            ids = np.flatnonzero([row['phase'] == 0 for row in obs])
            if len(ids):
                subset = [obs[i] for i in ids]
                routed = table[ids]
                for overlay in self.tables:
                    routed, matched = overlay.apply(subset, routed)
                    mask[ids[np.asarray(matched, dtype=int)]] = True
                table[ids] = routed
        return dict(features=x, actors=actor, arity=arity, legal=legal, keys=keys,
                    own_history=own, table=table, mask=mask,
                    context_sha256=self.context_sha256, owner=self)
