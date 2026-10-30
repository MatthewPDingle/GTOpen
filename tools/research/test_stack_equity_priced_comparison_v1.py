"""Synthetic integration controls; no historical or fresh poker labels."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import torch
import stack_equity_priced_comparison_v1 as compare
from stack_board_balanced_metrics_v1 import reference_context, compare_evaluations, evaluation_summary


def fixture(device='cpu'):
    rng = np.random.default_rng(9297500)
    boards = []
    for _ in range(2):
        x = np.zeros((1081, 387), dtype=np.float32)
        x[:, compare.equity_model.CARD_COLUMNS] = rng.uniform(0, 1, (1081, 191))
        x[:, 269:278] = 0
        x[np.arange(1081), 269 + np.arange(1081) % 9] = 1
        wins = rng.integers(0, 991, 1081)
        ties = rng.integers(0, 991, 1081) % (991 - wins)
        boards.append(dict(features=x, counts=np.column_stack((wins, ties, 990 - wins - ties))))
    contexts = []
    for stack, n in ((20, 2), (100, 3)):
        net = np.linspace(.8, 1.9, n) * stack
        cost = net * np.linspace(.15, .45, n)
        e = np.column_stack((np.full(n, stack), net, cost, np.arange(n) % 2, cost / net))
        x = np.zeros((n, 387), dtype=np.float32)
        x[:, 133] = np.linspace(.1, .7, n)
        x[:, 302] = np.linspace(.9, .2, n)
        contexts.append(dict(stack=stack, rows=list(range(n)), features=x, economics=e))
    return boards, contexts, compare.Dataset(boards, contexts, terminal_call_confirmed=True, device=device)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        cls.boards, cls.contexts, cls.data = fixture()

    def test_complete_shared_draw_matches_legacy_distribution(self):
        data = self.data
        a, b = (torch.Generator().manual_seed(818) for _ in range(2))
        for n in (1, 31, 4096):
            batch = data.sample(n, a)
            context = torch.randint(len(data.contexts), (n,), generator=b)
            u = torch.rand(n, generator=b, dtype=torch.float64)
            states = data.offsets_gpu[context] + torch.floor(u * data.lengths_gpu[context]).long()
            cards = torch.randint(len(data.card_np), (n,), generator=b)
            self.assertTrue(torch.equal(batch['states'], states))
            self.assertTrue(torch.equal(batch['cards'], cards))
            self.assertTrue(torch.equal(a.get_state(), b.get_state()))
            e = data.economics[states]
            target = ((data.equity[cards] * e[:, 1] - e[:, 2]) / e[:, 0]).float()
            self.assertTrue(torch.equal(batch['target'], target))
            self.assertTrue(torch.equal(batch['x'], data.cards[cards] + data.public[states]))

    def test_reject_leakage_and_corrupt_data(self):
        for mutate in (
            lambda b, c: c[0]['features'].__setitem__((0, 0), 1),
            lambda b, c: b[0]['counts'].__setitem__((0, 0), 991),
            lambda b, c: c[0]['economics'].__setitem__((0, 3), 2),
            lambda b, c: c[0].__setitem__('stack', 40),
        ):
            b, c = copy.deepcopy((self.boards, self.contexts))
            mutate(b, c)
            with self.assertRaises(ValueError):
                compare.Dataset(b, c, terminal_call_confirmed=True, device='cpu')
        with self.assertRaises(ValueError):
            compare.Dataset(self.boards, self.contexts, terminal_call_confirmed=False, device='cpu')

    def test_checkpoint_roundtrip_and_reject_alterations(self):
        batch = self.data.sample(31, torch.Generator().manual_seed(17))
        with tempfile.TemporaryDirectory() as td:
            for arm in compare.ARMS:
                model = compare.fresh(123, arm)
                saved = compare.save(Path(td) / (arm + '.npz'), model, arm)
                loaded = compare.load(saved, 123, arm)
                self.assertTrue(torch.equal(compare.predict(model, arm, batch), compare.predict(loaded, arm, batch)))
                Path(saved['file']).write_bytes(b'changed')
                with self.assertRaises(ValueError):
                    compare.load(saved, 123, arm)

    def test_independent_float64_predictions_and_no_mutation(self):
        batch = self.data.sample(257, torch.Generator().manual_seed(89))
        original = {k: v.clone() for k, v in batch.items()}
        for arm in compare.ARMS:
            model = compare.fresh(987, arm)
            # Exercise non-neutral head and relative branch with synthetic weights.
            with torch.no_grad():
                for p in model.parameters():
                    p.add_(.013)
            weights = compare.arrays(model, arm)
            expected = compare.numpy_scores(weights, arm, batch['x'].numpy(), batch['economics'].numpy())
            actual = compare.predict(copy.deepcopy(model).double(), arm, batch).detach().numpy()
            np.testing.assert_allclose(actual, expected, rtol=0, atol=2e-12)
            for key in batch:
                self.assertTrue(torch.equal(batch[key], original[key]))

    def test_detailed_metrics_independently_reconstructed(self):
        data = self.data
        for arm in compare.ARMS:
            model = compare.fresh(123, arm)
            weights = compare.arrays(model, arm)
            gpu_path = compare.evaluate(model, arm, data, lambda: None, detail=True)
            contexts = []
            for context in data.contexts:
                def rows():
                    for state, public in zip(context['economics'], context['features']):
                        features = data.card_np + public.astype(np.float32)
                        economics = np.broadcast_to(state, (len(features), 5))
                        yield compare.numpy_scores(weights, arm, features, economics)
                contexts.append(reference_context(rows(), data.equity_np, context['economics'],
                    data.category_np, context['stack'], data.board_count, detail=True))
            proof = compare_evaluations(gpu_path, evaluation_summary(contexts))
            self.assertTrue(proof['passed'], proof)
            self.assertTrue(all(p.dtype == torch.float32 for p in model.parameters()))

    def test_tie_selection_and_invalid_losses(self):
        rows = [dict(step=s, validation=dict(context_balanced_mean_regret_stack_fraction=v))
                for s, v in ((8192, .1), (0, .2), (1024, .1), (4096, .1))]
        self.assertEqual(compare.select(rows)['step'], 1024)
        for value in (float('nan'), -1):
            with self.assertRaises(ValueError):
                compare.select([dict(step=0, validation=dict(context_balanced_mean_regret_stack_fraction=value))])

    def test_synthetic_paired_fit_and_float32_restore(self):
        with tempfile.TemporaryDirectory() as td, patch.object(compare, 'STEPS', 2), \
                patch.object(compare, 'CHECKPOINTS', (0, 2)), patch.object(compare, 'BATCH_SIZE', 31):
            result = compare.fit_pair(852, self.data, self.data, td, lambda: None, lambda *a, **kw: None)
            self.assertTrue(result['shared_batch_objects'])
            fits = result['fits']
            self.assertEqual([c['batch_rng_sha256'] for c in fits[0]['checkpoints']],
                             [c['batch_rng_sha256'] for c in fits[1]['checkpoints']])
            for fit in fits:
                before = compare.load(fit['checkpoints'][0]['weights'], 852, fit['arm'])
                after = compare.load(fit['checkpoints'][1]['weights'], 852, fit['arm'])
                self.assertTrue(any(not torch.equal(a, b) for a, b in zip(before.parameters(), after.parameters())))
                self.assertTrue(all(p.dtype == torch.float32 for p in after.parameters()))


if __name__ == '__main__':
    unittest.main()
