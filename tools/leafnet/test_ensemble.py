"""Tests for ensemble net files and `harness.py ensemble` (no GPU, torch or solve-cli needed).

    python tools/leafnet/test_ensemble.py
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import types
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402
import leafnet_io  # noqa: E402

SNAP = "snap-test"
N, JOBS, NC, HIDDEN = 64, 16, 169, 6


def small_net(seed):
    """A random 686 -> 6 -> 338 net: seed copies differ the way trained seeds do."""
    r = np.random.default_rng(seed)
    Ws = [0.02 * r.standard_normal((686, HIDDEN)).astype(np.float32),
          0.05 * r.standard_normal((HIDDEN, 2 * NC)).astype(np.float32)]
    bs = [0.1 * r.standard_normal(HIDDEN).astype(np.float32), np.full(2 * NC, 0.03, np.float32)]
    return Ws, bs, np.zeros(686, np.float32), np.ones(686, np.float32)


class EnsembleTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.sdir = os.path.join(self.work, "snapshots", SNAP)
        with open(os.path.join(self.work, "CURRENT_SNAPSHOT"), "w") as f:
            f.write(SNAP + "\n")
        rng = np.random.default_rng(3)
        self.write_set(self.sdir, rng, split=True)
        self.write_set(os.path.join(self.sdir, "leaf", "check"), rng)
        with open(os.path.join(self.sdir, "manifest.json"), "w") as f:
            json.dump({"leaf_sets": [{"name": "check"}]}, f)
        with open(os.path.join(self.sdir, "inputs_val.jsonl"), "w") as f:
            f.write("".join(json.dumps({"index": i}) + "\n" for i in range(N)))
        y = np.load(os.path.join(self.sdir, "y.npy"))
        os.makedirs(os.path.join(self.sdir, "referee"))
        path = os.path.join(self.sdir, "referee", "val_cv.npy")
        np.save(path, (y - 0.01).astype(np.float32))
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        with open(os.path.join(self.sdir, "referee", "referee.json"), "w") as f:
            json.dump({"val_cv_sha256": sha}, f)
        self.runs = os.path.join(self.work, "runs", SNAP)
        os.makedirs(self.runs)
        _, self.sets = harness.scoring_sets(self.work, SNAP)
        # stands in for solve-cli: the numpy forward pass of whatever file it is given
        self.real_rust = harness.rust_residuals
        harness.rust_residuals = lambda cli, net, inputs, count=harness.PARITY_EXAMPLES: leafnet_io.forward_members(
            leafnet_io.read_members(net)[1], self.sets["val"].x[:count]).reshape(-1, 2, NC)
        self.names = [self.make_run(f"r{s}", s) for s in range(3)]
        st = harness.State(self.work, SNAP)
        st.s = {"best": "r0", "best_seeds": self.names, "history": ["r0"]}
        st.save()

    def tearDown(self):
        harness.rust_residuals = self.real_rust
        shutil.rmtree(self.work)

    def write_set(self, folder, rng, split=False):
        os.makedirs(folder)
        truth = rng.uniform(0.2, 0.8, (N, 2, NC))
        arrays = {"x": rng.standard_normal((N, 686)).astype(np.float32), "y": truth + 0.05 * rng.standard_normal((N, 2, NC)),
                  "mask": np.ones((N, 2, NC)), "reach": np.ones((N, 2, NC)), "w": np.ones((N, 2, NC)),
                  "jobs": np.repeat(np.arange(JOBS), N // JOBS), "pot_type": np.zeros(N, np.int64)}
        if split:
            arrays["split"] = np.full(N, harness.SPLITS["val"])
        for m in harness.MODELS:
            arrays[f"base_{m}"] = truth - 0.03
        for k, a in arrays.items():
            np.save(os.path.join(folder, k + ".npy"), a)

    def make_run(self, name, seed):
        d = os.path.join(self.runs, name)
        os.makedirs(d)
        net = os.path.join(d, "leaf_net.bin")
        leafnet_io.write(net, *small_net(seed))
        with open(os.path.join(d, "sums.json"), "w") as f:
            json.dump({k: harness.sums_to_json(v[0]) for k, v in harness.score_file(net, self.sets).items()}, f)
        return name

    def ensemble(self, runs=(), name=None):
        args = types.SimpleNamespace(work=self.work, snapshot=None, runs=list(runs), name=name, solve_cli="unused")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            harness.cmd_ensemble(args)
        return out.getvalue()

    def rows(self):
        with open(os.path.join(self.work, "results.tsv")) as f:
            lines = f.read().splitlines()
        return [dict(zip(lines[0].split("\t"), l.split("\t"))) for l in lines[1:]]

    def test_an_ensemble_file_is_the_mean_of_its_members(self):
        members = [small_net(s) for s in range(3)]
        path = os.path.join(self.work, "ens.bin")
        leafnet_io.write_ensemble(path, members, extra={"members": ["a", "b", "c"]})
        header, got = leafnet_io.read_members(path)
        self.assertEqual(header["ensemble"], [[686, HIDDEN, 2 * NC]] * 3)
        self.assertEqual(header["sizes"], [686, HIDDEN, 2 * NC])
        x = self.sets["val"].x
        want = np.mean([leafnet_io.forward(*m, x) for m in members], axis=0)
        np.testing.assert_allclose(leafnet_io.forward_members(got, x, batch=7), want, atol=1e-6)
        with self.assertRaises(ValueError):
            leafnet_io.read(path)                        # read() is for plain nets
        with self.assertRaises(ValueError):
            leafnet_io.write_ensemble(path, members[:1])
        # a plain net is one member, and a cut-off file is refused
        plain = os.path.join(self.runs, "r0", "leaf_net.bin")
        self.assertEqual(len(leafnet_io.read_members(plain)[1]), 1)
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(blob[:-8])
        with self.assertRaises(ValueError):
            leafnet_io.read_members(path)

    def test_the_command_averages_the_bests_seeds(self):
        self.assertIn("VERDICT: ensemble", self.ensemble())
        st = harness.State(self.work, SNAP)
        self.assertEqual(st.s["ensembles"], ["ens3-r0"])
        self.assertEqual((st.s["best"], st.s["history"]), ("r0", ["r0"]))      # never the best, never kept
        rdir = os.path.join(self.runs, "ens3-r0")
        header, members = leafnet_io.read_members(os.path.join(rdir, "leaf_net.bin"))
        self.assertEqual((len(members), header["members"], header["run"]), (3, self.names, "ens3-r0"))
        self.assertFalse(os.path.exists(os.path.join(rdir, "leaf_net.bin.tmp")))
        with open(os.path.join(rdir, "config.json")) as f:
            self.assertEqual(json.load(f)["ensemble"], self.names)
        # scored on every set, and no worse than its members' average on any of them
        ens, mean = st.group_sums(["ens3-r0"]), st.group_sums(self.names)
        self.assertEqual(sorted(ens), ["leaf:check", "val", "val_cv"])
        for k in ens:
            self.assertLess(harness.totals(ens[k])[0], harness.totals(mean[k])[0])
        row = self.rows()[-1]
        self.assertEqual((row["run"], row["verdict"], row["seed"]), ("ens3-r0", "ensemble", "ens"))
        self.assertEqual(int(row["macs"]), 3 * harness.macs([686, HIDDEN, 2 * NC]))
        self.assertGreater(float(row["gain_class"]), 0)
        self.assertTrue(row["val_cv_class"] and row["leaf_class"])
        # building the same ensemble again changes nothing; other members under that name are refused
        self.ensemble()
        self.assertEqual(harness.State(self.work, SNAP).s["ensembles"], ["ens3-r0"])
        with self.assertRaises(SystemExit):
            self.ensemble(["r0", "r1"], name="ens3-r0")
        self.assertIn("VERDICT: ensemble", self.ensemble(["r1", "r2"], name="pair"))
        self.assertEqual(harness.State(self.work, SNAP).s["ensembles"], ["ens3-r0", "pair"])

    def test_what_it_refuses(self):
        with self.assertRaises(SystemExit):
            self.ensemble(["r0"])                        # one net is not an ensemble
        with self.assertRaises(SystemExit):
            self.ensemble(["r0", "missing"])
        with self.assertRaises(SystemExit):
            self.ensemble(["r0", "r1"], name="../x")
        self.ensemble()
        with self.assertRaises(SystemExit):
            self.ensemble(["ens3-r0", "r1"])             # no ensembles of ensembles
        limit = harness.MAX_ENSEMBLE_MACS
        harness.MAX_ENSEMBLE_MACS = 2 * harness.macs([686, HIDDEN, 2 * NC])
        try:
            with self.assertRaises(SystemExit):
                self.ensemble(self.names, name="big")
        finally:
            harness.MAX_ENSEMBLE_MACS = limit
        # the keep rule compares single nets
        args = types.SimpleNamespace(work=self.work, snapshot=None, runs=["ens3-r0", "r1"], against=["r0"])
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            harness.cmd_confirm(args)

    def test_a_file_the_solver_reads_differently_is_rejected(self):
        numpy_forward = harness.rust_residuals
        harness.rust_residuals = lambda *a, **k: numpy_forward(*a, **k) + 0.01
        self.assertIn("VERDICT: rejected", self.ensemble())
        self.assertNotIn("ensembles", harness.State(self.work, SNAP).s)
        self.assertEqual(os.listdir(os.path.join(self.runs, "ens3-r0")), [])
        self.assertEqual(self.rows()[-1]["verdict"], "rejected")

    def test_rescore_reads_ensembles_too(self):
        self.ensemble()
        sp = os.path.join(self.runs, "ens3-r0", "sums.json")
        with open(sp) as f:
            d = json.load(f)
        want = d.pop("val_cv")
        with open(sp, "w") as f:
            json.dump(d, f)
        args = types.SimpleNamespace(work=self.work, snapshot=None, force=False)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            harness.cmd_rescore(args)
        with open(sp) as f:
            got = json.load(f)["val_cv"]
        for j in want:
            np.testing.assert_allclose(got[j], want[j], rtol=1e-9)


if __name__ == "__main__":
    unittest.main()
