"""Tests for the "near zero" input layout: leafnet_io, near_zero.py, the harness's export and train.py.

    python -m unittest tools/leafnet/test_near_zero.py

The file-format tests need numpy only. The others need torch (CPU is enough) and are skipped without it. No
GPU, no solve-cli: the snapshots are fabricated arrays in a temporary folder, and the one training test fits
a linear net for 1,000 steps, twice.
"""

import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "datagen"))

import leafnet_io  # noqa: E402
from leafnet_io import NC, NEAR_ZERO_TAU, N_INPUTS, N_INPUTS_NEAR_ZERO  # noqa: E402

try:
    import torch
except ImportError:
    torch = None

if torch is not None:
    import harness  # noqa: E402
    import near_zero  # noqa: E402
    import train  # noqa: E402
    from prepare import REAL_GENERATOR  # noqa: E402
    from test_train import Budget, Snapshot, leaves  # noqa: E402


def random_net(n_in, hidden=5, seed=0):
    r = np.random.default_rng(seed)
    weights = [r.normal(0, 0.1, (n_in, hidden)).astype(np.float32), r.normal(0, 0.1, (hidden, 2 * NC)).astype(np.float32)]
    biases = [r.normal(0, 0.1, hidden).astype(np.float32), r.normal(0, 0.1, 2 * NC).astype(np.float32)]
    return weights, biases, r.normal(0, 0.1, n_in).astype(np.float32), r.uniform(0.5, 2, n_in).astype(np.float32)


def inputs(n, seed=0):
    """First-layout inputs with ranges that have hands at 0, at a token weight and at real weights."""
    rng, _ = leaves(n, seed) if torch is not None else (np.random.default_rng(seed).uniform(0, 1, (n, 2, NC)), None)
    x = np.random.default_rng(seed + 1).normal(0, 1, (n, N_INPUTS)).astype(np.float32)
    x[:, :2 * NC] = np.asarray(rng, np.float32).reshape(n, -1)
    return x


class Layout(unittest.TestCase):
    def test_the_extra_inputs_mark_a_hand_the_range_does_not_hold(self):
        x = np.zeros((1, N_INPUTS), np.float32)
        x[0, :6] = [0.0, 0.001, 0.02, 0.1, 1.0, 1.5]        # 1.5 cannot happen (the largest weight is 1): held to 1
        x[0, 2 * NC:] = 7.0                                  # the other inputs play no part
        e = leafnet_io.near_zero(x)
        self.assertEqual(e.shape, (1, 2 * NC))
        self.assertEqual(e[0, 0], 1.0)
        np.testing.assert_allclose(e[0, 1:5], np.exp(-np.array([0.001, 0.02, 0.1, 1.0]) / NEAR_ZERO_TAU), rtol=1e-6)
        self.assertGreater(e[0, 1], 0.95)
        self.assertLess(e[0, 3], 0.01)
        self.assertEqual(e[0, 5], e[0, 4])
        np.testing.assert_array_equal(e[0, 6:], 1.0)
        wide = leafnet_io.inputs_for(x, N_INPUTS_NEAR_ZERO)
        self.assertEqual(wide.shape, (1, N_INPUTS_NEAR_ZERO))
        np.testing.assert_array_equal(wide[:, :N_INPUTS], x)
        np.testing.assert_array_equal(wide[:, N_INPUTS:], e)
        self.assertIs(leafnet_io.inputs_for(x, N_INPUTS), x)
        self.assertIs(leafnet_io.inputs_for(wide, N_INPUTS_NEAR_ZERO), wide)
        with self.assertRaises(ValueError):
            leafnet_io.inputs_for(x, N_INPUTS + 1)

    def test_a_net_file_of_the_wider_layout_runs_on_the_first_layouts_inputs(self):
        x = inputs(7)
        with tempfile.TemporaryDirectory() as tmp:
            for n_in in (N_INPUTS, N_INPUTS_NEAR_ZERO):
                W, b, mu, sd = random_net(n_in)
                path = os.path.join(tmp, f"net{n_in}.bin")
                leafnet_io.write(path, W, b, mu, sd)
                header, members = leafnet_io.read_members(path)
                self.assertEqual(header["sizes"][0], n_in)
                self.assertEqual("near zero" in header["features"], n_in == N_INPUTS_NEAR_ZERO)
                h = np.maximum(((leafnet_io.inputs_for(x, n_in) - mu) / sd) @ W[0] + b[0], 0) @ W[1] + b[1]
                np.testing.assert_allclose(leafnet_io.forward_members(members, x), h, atol=1e-6)
            # one of each in an ensemble: each member builds the inputs it was trained with
            a, c = random_net(N_INPUTS, seed=1), random_net(N_INPUTS_NEAR_ZERO, seed=2)
            path = os.path.join(tmp, "ens.bin")
            leafnet_io.write_ensemble(path, [a, c])
            header, members = leafnet_io.read_members(path)
            self.assertEqual([m[0] for m in header["ensemble"]], [N_INPUTS, N_INPUTS_NEAR_ZERO])
            want = (leafnet_io.forward(*a, x) + leafnet_io.forward(*c, x)) / 2
            np.testing.assert_allclose(leafnet_io.forward_members(members, x), want, atol=1e-6)


def snapshot(tmp, n=64, seed=0, **kw):
    rng, w = leaves(n, seed)
    return Snapshot(tmp, rng, w, np.full(n, REAL_GENERATOR, np.int16), **kw), rng.reshape(n, -1)


@unittest.skipIf(torch is None, "torch is not installed")
class Module(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_the_module_builds_the_files_inputs_from_normalized_ones(self):
        data, rng = snapshot(self.tmp.name)
        x = np.load(os.path.join(self.tmp.name, "x.npy"))
        xn = torch.from_numpy((x - data.mu) / data.sd)
        head = near_zero.NearZero(data.mu, data.sd)
        raw = leafnet_io.near_zero(x)
        np.testing.assert_allclose(head.raw(xn).numpy(), raw, atol=2e-5)
        out = head(xn).numpy()                                # before fit(): the extra inputs as they are
        np.testing.assert_array_equal(out[:, :N_INPUTS], xn.numpy())
        np.testing.assert_allclose(out[:, N_INPUTS:], raw, atol=2e-5)
        head.fit(data.x_train)                                # the harness's training rows are float16
        mu, sd = raw.mean(axis=0), raw.std(axis=0)
        np.testing.assert_allclose(head.extra_mu.numpy(), mu, atol=2e-2)
        np.testing.assert_allclose(head.extra_sd.numpy(), np.where(sd < 1e-3, 1.0, sd), atol=2e-2)
        self.assertTrue((head.extra_sd.numpy() > 0).all())
        with self.assertRaises(ValueError):
            head(torch.zeros(2, N_INPUTS_NEAR_ZERO))

    def test_the_exported_file_gives_the_models_numbers(self):
        """What the harness writes for a model with a NearZero is a plain net of the wider layout: the numpy
        forward pass (and so the Rust loader, which builds the same inputs) on the inputs as they are on
        disk gives what the torch model gives on the harness's normalized inputs."""
        data, _ = snapshot(self.tmp.name)
        x = np.load(os.path.join(self.tmp.name, "x.npy"))
        cfg = dict(train.CONFIG, hidden=8, depth=2, near_zero=True)
        torch.manual_seed(0)
        model = train.build(cfg, data.n_in, data.n_out, data)
        head, rest = near_zero.split(model)
        self.assertIsInstance(head, near_zero.NearZero)
        Ws, bs = harness.to_mlp(model)
        self.assertEqual([Ws[0].shape[0]] + [W.shape[1] for W in Ws], [N_INPUTS_NEAR_ZERO, 8, 8, 2 * NC])
        mu, sd = near_zero.file_norm(head, data.mu, data.sd)
        self.assertEqual((len(mu), len(sd)), (N_INPUTS_NEAR_ZERO, N_INPUTS_NEAR_ZERO))
        path = os.path.join(self.tmp.name, "leaf_net.bin")
        leafnet_io.write(path, Ws, bs, mu, sd)
        _, members = leafnet_io.read_members(path)
        mine = harness.predict(model, (x - data.mu) / data.sd).reshape(len(x), -1)
        np.testing.assert_allclose(leafnet_io.forward_members(members, x), mine, atol=1e-4)
        # without the setting the model and the file are what they always were
        plain = train.build(dict(cfg, near_zero=False), data.n_in, data.n_out, data)
        self.assertIsNone(near_zero.split(plain)[0])
        self.assertEqual(harness.to_mlp(plain)[0][0].shape[0], N_INPUTS)
        self.assertIs(near_zero.file_norm(None, data.mu, data.sd)[0], data.mu)
        self.assertFalse(train.CONFIG["near_zero"])
        # the kept width is over the size limit with the wider first layer: refused before any training
        with self.assertRaises(ValueError):
            train.build(dict(train.CONFIG, near_zero=True), data.n_in, data.n_out, data)
        train.build(dict(train.CONFIG, near_zero=True, hidden=1218), data.n_in, data.n_out, data)

    def test_the_module_may_only_come_first(self):
        data, _ = snapshot(self.tmp.name)
        head = near_zero.NearZero(data.mu, data.sd)
        late = torch.nn.Sequential(torch.nn.Linear(N_INPUTS, N_INPUTS), head, torch.nn.Linear(N_INPUTS_NEAR_ZERO, 2 * NC))
        with self.assertRaises(ValueError):
            harness.to_mlp(late)


def weight_decides(n, seed):
    """n leaves where a hand's value depends on its own weight alone: a hand at a token weight is worth 5% of
    the pot more than the net's starting point, a played hand nothing on average (with flop luck of 2% of the
    pot around it). Which classes are played and which sit just outside changes from leaf to leaf, and nothing
    else tells the leaves apart."""
    rng, w = leaves(n, seed)
    flat = rng.reshape(n, -1)
    r_ = np.random.default_rng(seed + 100)
    mean = np.where(flat == np.float32(0.001), 0.05, 0.0).astype(np.float32)
    resid = mean + np.where(flat >= 0.05, r_.normal(0, 0.02, flat.shape), 0.0).astype(np.float32)
    return rng, w, flat, mean, resid


@unittest.skipIf(torch is None, "torch is not installed")
class Training(unittest.TestCase):
    def test_only_a_net_with_the_extra_inputs_can_price_outside_hands_without_moving_played_ones(self):
        """With every solved hand counted (play floor 1), a net that sees weights on a linear scale has to
        trade the hands outside the range against the thinly played ones. With the extra inputs it gets both
        right, on leaves it was not trained on."""
        n = 12000
        rng, w, _, _, resid = weight_decides(n, 0)
        _, _, flat2, mean2, _ = weight_decides(400, 1)
        x2 = np.zeros((400, N_INPUTS), np.float32)
        x2[:, :2 * NC] = flat2
        tok, played = flat2 == np.float32(0.001), flat2 >= 0.05
        cfg = dict(train.CONFIG, teacher=False, depth=0, batch=256, max_steps=1000, eval_every=100, lr=3e-3,
                   weight_decay=0.0, play_floor=1.0, last_layer_scale=0.01)
        errs = {}
        for wide in (False, True):
            with tempfile.TemporaryDirectory() as tmp:
                data = Snapshot(tmp, rng, w, np.full(n, REAL_GENERATOR, np.int16), resid=resid, meta=np.zeros((n, 10)))
                harness.seed_everything(0)
                model = train.run(dict(cfg, near_zero=wide), data, Budget(), torch.Generator().manual_seed(0))
                pred = harness.predict(model, (x2 - data.mu) / data.sd).reshape(400, -1)
            err = np.abs(pred - mean2)
            errs[wide] = (float(err[tok].mean()), float(err[played].mean()))
        self.assertGreater(errs[False][0], 0.02, errs)
        self.assertLess(errs[True][0], 0.01, errs)
        self.assertLess(errs[True][1], 0.01, errs)
        self.assertLess(errs[True][1], errs[False][1], errs)


if __name__ == "__main__":
    unittest.main()
