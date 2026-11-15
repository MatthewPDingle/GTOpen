"""Tests for train.py's play floor: the loss weight of hands a range barely plays.

    python -m unittest tools/leafnet/test_train.py

Needs torch (CPU is enough) and is skipped without it. No GPU, no solve-cli:
the snapshots are fabricated arrays in a temporary folder, and the one
training test fits a 16-wide net for 1,500 steps, twice.
"""

import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import torch
except ImportError:      # the other test files need no torch; this one cannot run without it
    torch = None

if torch is not None:
    import harness  # noqa: E402
    import train  # noqa: E402
    from prepare import REAL_GENERATOR  # noqa: E402

NC = 169
N_IN = 2 * NC * 2 + 10      # range oop/ip, balanced oop/ip, 10 meta


class Snapshot:
    """The few things train.py reads from the harness's data object, over fabricated arrays."""

    def __init__(self, folder, rng, w, generator, split=None, train_index=None, resid=None, meta=None):
        n = len(rng)
        split = np.zeros(n, np.int8) if split is None else np.asarray(split, np.int8)
        x = np.zeros((n, N_IN), np.float32)
        x[:, :2 * NC] = rng.reshape(n, -1)
        x[:, -10:] = np.random.default_rng(0).normal(size=(n, 10)) if meta is None else meta
        np.save(os.path.join(folder, "x.npy"), x)
        np.save(os.path.join(folder, "w.npy"), w.reshape(n, 2, NC).astype(np.float32))
        np.save(os.path.join(folder, "split.npy"), split)
        np.save(os.path.join(folder, "generator.npy"), np.asarray(generator, np.int16))
        tr = np.nonzero(split == harness.SPLITS["train"])[0]
        if train_index is not None:
            self.train_index = np.asarray(train_index)
            tr = tr[self.train_index]
        self.dir, self.device, self.n_train = folder, "cpu", len(tr)
        self.n_in, self.n_out = N_IN, 2 * NC
        mu, sd = x[tr].mean(axis=0), x[tr].std(axis=0)                 # inputs normalized as the harness does
        self.x_train = torch.from_numpy((x[tr] - mu) / np.where(sd < 1e-3, 1.0, sd)).half()
        self.w_train = torch.from_numpy(w.reshape(n, -1)[tr].astype(np.float32)).half()
        resid = np.zeros((n, 2 * NC), np.float32) if resid is None else resid
        self.r_train = torch.from_numpy(resid[tr]).half()

    def val_loss(self, model):
        self.checks = getattr(self, "checks", 0) + 1       # always a little better: the last state is the one kept
        return 1.0 / self.checks


def leaves(n, seed=0, tokens=8):
    """n leaves: per player 40 classes in the range (weights 0.05 to 1, the largest 1), `tokens` classes at
    0.001 just outside it, the rest at 0; loss weights as the snapshot stores them (share of the range x 169,
    every class taken as 4 combos)."""
    r_ = np.random.default_rng(seed)
    rng = np.zeros((n, 2, NC), np.float32)
    for i in range(n):
        for p in range(2):
            order = r_.permutation(NC)
            rng[i, p, order[:40]] = np.round(r_.uniform(0.05, 1.0, 40), 3)
            rng[i, p, order[0]] = 1.0
            rng[i, p, order[40:40 + tokens]] = 0.001
    w = rng / rng.sum(axis=2, keepdims=True) * NC
    return rng, w


def with_floor(rng, w, floor):
    """Loss weights (n, 338) under a floor, the slow way: every class with a weight counts as if at
    max(weight, floor), then each player's weights are scaled back to the total they had."""
    n = len(rng)
    r, w = rng.reshape(n, 2, NC).astype(np.float64), w.reshape(n, 2, NC).astype(np.float64)
    out = np.zeros_like(w)
    for i in range(n):
        for p in range(2):
            lifted = np.where(r[i, p] > 0, w[i, p] * np.maximum(r[i, p], floor) / np.maximum(r[i, p], 1e-12), 0.0)
            out[i, p] = lifted * w[i, p].sum() / lifted.sum()
    return out.reshape(n, -1)


@unittest.skipIf(torch is None, "torch is not installed")
class PlayFloorWeights(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def snapshot(self, n=12, real=(3, 4, 7), **kw):
        rng, w = leaves(n)
        gen = np.ones(n, np.int16)
        gen[list(real)] = REAL_GENERATOR
        return Snapshot(self.tmp.name, rng, w, gen, **kw), rng.reshape(n, -1), w.reshape(n, -1)

    def test_the_factor_lifts_a_weight_to_the_floor_and_no_further(self):
        f = train.play_floor_factor(np.array([0.0, 0.001, 0.25, 0.5, 1.0]), 0.5)
        np.testing.assert_allclose(f, [1.0, 500.0, 2.0, 1.0, 1.0])
        np.testing.assert_allclose(train.play_floor_factor(np.array([0.0, 0.001, 1.0]), 1.0), [1.0, 1000.0, 1.0])

    def test_off_by_default_and_the_losses_keep_the_snapshots_weights(self):
        data, _, _ = self.snapshot()
        self.assertEqual(train.CONFIG["play_floor"], 0.0)
        self.assertIsNone(train.play_floor(dict(train.CONFIG), data))
        self.assertIsNone(train.play_floor({}, data))

    def test_real_rows_count_every_solved_hand_as_if_at_the_floor(self):
        data, rng, w = self.snapshot()
        wl, fac = train.play_floor(dict(train.CONFIG, play_floor=1.0), data)
        self.assertEqual((wl.dtype, tuple(wl.shape)), (data.w_train.dtype, (12, 2 * NC)))
        wl, fac = wl.float().numpy(), fac.numpy()
        real = np.zeros(12, bool)
        real[[3, 4, 7]] = True
        # pool rows: untouched
        np.testing.assert_array_equal(fac[~real], 1.0)
        np.testing.assert_array_equal(wl[~real], data.w_train.float().numpy()[~real])
        # real rows at floor 1: every class with a weight counts the same (all classes have 4 combos here),
        # token classes included; the rest stay at 0; each player's total is what it was
        np.testing.assert_allclose(wl[real], with_floor(rng[real], w[real], 1.0), rtol=2e-3)
        for row in wl[real].reshape(3, 2, NC):
            for player in row:
                self.assertEqual(len(np.unique(np.round(player[player > 0], 2))), 1)
                self.assertEqual(int((player > 0).sum()), 48)
        np.testing.assert_allclose(wl[real].reshape(3, 2, NC).sum(axis=2), w[real].reshape(3, 2, NC).sum(axis=2), rtol=1e-3)
        # a token class is lifted 1,000 times as much as the range's most-played class
        top, tok = rng[real] == 1.0, rng[real] == np.float32(0.001)
        self.assertEqual(int(tok.sum()), 3 * 2 * 8)
        np.testing.assert_allclose(fac[real][tok].reshape(3, 2, 8) / fac[real][top].reshape(3, 2, -1)[:, :, :1], 1000.0, rtol=1e-4)
        # a lower floor lifts only what lies under it
        wl25, _ = train.play_floor(dict(train.CONFIG, play_floor=0.25), data)
        np.testing.assert_allclose(wl25.float().numpy()[real], with_floor(rng[real], w[real], 0.25), rtol=2e-3)
        self.assertGreater(np.abs(with_floor(rng[real], w[real], 0.25) - with_floor(rng[real], w[real], 1.0)).max(), 0.5)

    def test_all_rows(self):
        data, rng, w = self.snapshot()
        wl, fac = train.play_floor(dict(train.CONFIG, play_floor=1.0, play_floor_rows="all"), data)
        self.assertTrue((fac.numpy() != 1.0).any(axis=1).all())
        np.testing.assert_allclose(wl.float().numpy(), with_floor(rng, w, 1.0), rtol=2e-3)

    def test_a_token_weight_survives_where_half_precision_would_lose_it(self):
        # a class at 0.001 in a range of 300 classes' worth of weight: the snapshot's float32 weight is kept exactly
        rng, w = leaves(4)
        w = w * 1e-3                                   # weights too small for float16 to hold well
        data = Snapshot(self.tmp.name, rng, w, np.full(4, REAL_GENERATOR, np.int16))
        wl, _ = train.play_floor(dict(train.CONFIG, play_floor=1.0), data)
        tok = rng.reshape(4, -1) == np.float32(0.001)
        want = with_floor(rng, w, 1.0)
        self.assertLess(w.reshape(4, -1)[tok].max(), 1e-5)
        np.testing.assert_allclose(wl.float().numpy()[tok], want[tok], rtol=2e-3)
        self.assertGreater(want[tok].min(), 1e-3)

    def test_no_real_rows_means_no_change(self):
        data, _, _ = self.snapshot(real=())
        self.assertIsNone(train.play_floor(dict(train.CONFIG, play_floor=1.0), data))

    def test_rows_follow_the_training_split_and_a_data_fraction(self):
        split = np.array([0, 1, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0])
        data, rng, w = self.snapshot(split=split, train_index=[6, 0, 3, 2])
        tr = np.nonzero(split == 0)[0][[6, 0, 3, 2]]                              # snapshot rows in x_train's order
        wl, fac = train.play_floor(dict(train.CONFIG, play_floor=1.0), data)
        real = np.isin(tr, [3, 4, 7])
        self.assertTrue(real.any() and not real.all())
        np.testing.assert_array_equal(fac.numpy()[~real], 1.0)
        np.testing.assert_allclose(wl.float().numpy()[real], with_floor(rng[tr][real], w[tr][real], 1.0), rtol=2e-3)
        np.testing.assert_array_equal(wl.float().numpy()[~real], data.w_train.float().numpy()[~real])

    def test_values_that_could_be_a_mistake_are_refused(self):
        data, _, _ = self.snapshot()
        with self.assertRaises(ValueError):
            train.play_floor(dict(train.CONFIG, play_floor=2.0), data)
        with self.assertRaises(ValueError):
            train.play_floor(dict(train.CONFIG, play_floor=1.0, play_floor_rows="pool"), data)

    def test_one_run_computes_it_once(self):
        data, _, _ = self.snapshot()
        cfg = dict(train.CONFIG, play_floor=1.0)
        self.assertIs(train.play_floor(cfg, data)[0], train.play_floor(cfg, data)[0])
        self.assertIsNot(train.play_floor(dict(cfg, play_floor=0.5), data)[0], train.play_floor(cfg, data)[0])

    def test_the_flop_average_weights_get_the_same_factor(self):
        data, rng, w = self.snapshot()
        _, fac = train.play_floor(dict(train.CONFIG, play_floor=1.0), data)
        wbar = torch.from_numpy((rng * 0.7).astype(np.float32)).half()           # proportional to the range, as wbar is
        out = train.floored(wbar, fac, chunk=5)
        self.assertEqual(out.dtype, wbar.dtype)
        real = np.zeros(12, bool)
        real[[3, 4, 7]] = True
        np.testing.assert_array_equal(out.numpy()[~real], wbar.numpy()[~real])
        # the same lift and the same scaling back as the loss weights (w is proportional to the range here too)
        np.testing.assert_allclose(out.float().numpy()[real], with_floor(rng[real], rng[real] * 0.7, 1.0), rtol=0.05)

    def test_teachers_with_a_floor_have_their_own_cache_names(self):
        base = train.teacher_tag(dict(train.CONFIG))
        self.assertEqual(base, train.teacher_tag(dict(train.CONFIG, play_floor=0.0)))
        real = train.teacher_tag(dict(train.CONFIG, play_floor=1.0))
        every = train.teacher_tag(dict(train.CONFIG, play_floor=1.0, play_floor_rows="all"))
        half = train.teacher_tag(dict(train.CONFIG, play_floor=0.5))
        self.assertEqual(len({base, real, every, half}), 4)
        self.assertTrue(real.startswith(base))


class Budget:
    def done(self, step):
        return False


def two_spots(n, seed=0):
    """n leaves of two spots, told apart by the last input. Spot 0 plays classes 0-49 and has token weights on
    50-57; spot 1 plays 50-99 and has them on 0-7: every token class is a played class of the other spot, as
    in real solves. A token hand is worth 5% of the pot more than the net's starting point, a played hand
    nothing on average, with flop luck of 5% of the pot around it."""
    r_ = np.random.default_rng(seed)
    spot = r_.integers(0, 2, n)
    rng = np.zeros((n, 2, NC), np.float32)
    for i in range(n):
        lo = 50 * spot[i]
        rng[i, :, lo:lo + 50] = np.round(r_.uniform(0.05, 1.0, (2, 50)), 3)
        rng[i, :, lo] = 1.0
        rng[i, :, 50 - lo:58 - lo] = 0.001
    w = rng / rng.sum(axis=2, keepdims=True) * NC
    flat = rng.reshape(n, -1)
    mean = np.where(flat == np.float32(0.001), 0.05, 0.0).astype(np.float32)
    resid = mean + np.where(flat >= 0.05, r_.normal(0, 0.05, flat.shape), 0.0).astype(np.float32)
    return spot, rng, w, mean, resid


@unittest.skipIf(torch is None, "torch is not installed")
class PlayFloorTraining(unittest.TestCase):
    def test_the_net_learns_the_hands_outside_the_range_only_with_the_floor(self):
        """Without the floor a token hand's loss weight is a thousandth of a played hand's, and the same class
        is a played hand in the other spot: the net leaves the token hands where they started. With the
        floor it learns them, and the played hands are no worse."""
        n = 512
        spot, rng, w, mean, resid = two_spots(n)
        flat = rng.reshape(n, -1)
        tok, played = flat == np.float32(0.001), flat >= 0.05
        cfg = dict(train.CONFIG, teacher=False, hidden=16, depth=1, batch=64, max_steps=1500, eval_every=100,
                   lr=1e-3, weight_decay=0.0)
        errs = {}
        for floor in (0.0, 1.0):
            with tempfile.TemporaryDirectory() as tmp:
                data = Snapshot(tmp, rng, w, np.full(n, REAL_GENERATOR, np.int16), resid=resid,
                                meta=np.repeat(spot[:, None], 10, axis=1))
                harness.seed_everything(0)
                model = train.run(dict(cfg, play_floor=floor), data, Budget(), torch.Generator().manual_seed(0))
                with torch.no_grad():
                    pred = model(data.x_train.float()).numpy()
            errs[floor] = (float(np.abs(pred - mean)[tok].mean()), float(np.abs(pred - mean)[played].mean()))
        self.assertGreater(errs[0.0][0], 0.04, errs)       # no better than where it started (0.05)
        self.assertLess(errs[1.0][0], 0.02, errs)
        self.assertLess(errs[1.0][1], errs[0.0][1] + 0.005, errs)


if __name__ == "__main__":
    unittest.main()
