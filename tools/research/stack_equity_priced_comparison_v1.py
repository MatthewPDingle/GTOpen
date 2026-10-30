"""Matched baseline/equity-pricing learning; no standalone scientific launch.

One batch object feeds both arms. Training is float32; selection and final
inference widen the saved float32 weights to float64 for BOTH approaches.
Only the existing uniform-opponent terminal river reference is supported.
"""
import copy
import hashlib
from pathlib import Path
import time
import numpy as np
import torch
import stack_equity_priced_model_v1 as equity_model
from stack_board_relative_model_v1 import fresh as baseline_fresh, rng_hash
from stack_price_learning_fit_v1 import scores, probabilities
from stack_board_relative_readback_v1 import dense_scores
from stack_board_balanced_metrics_v1 import summarize_context, evaluation_summary

ARMS = ('direct_value', 'equity_priced')
CHECKPOINTS = (0, 1024, 4096, 8192)
STEPS, BATCH_SIZE = 8192, 4096


class Dataset:
    def __init__(self, boards, contexts, *, terminal_call_confirmed, device='cuda'):
        if terminal_call_confirmed is not True or not boards or not contexts:
            raise ValueError('Qualified terminal boards and contexts required')
        self.board_count, self.contexts = len(boards), contexts
        self.device = torch.device(device)
        for board in boards:
            if np.asarray(board['features']).shape != (1081, 387):
                raise ValueError('Every board must retain all 1081 holdings and 387 inputs')
            counts = np.asarray(board['counts'])
            if (counts.shape != (1081, 3) or counts.dtype.kind not in 'iu'
                    or np.any(counts < 0) or np.any(counts.sum(1) != 990)):
                raise ValueError('Complete nonnegative integer win/tie/loss counts required')
        self.card_np = np.concatenate([b['features'] for b in boards]).astype(np.float32)
        counts = np.concatenate([b['counts'] for b in boards])
        self.equity_np = (counts[:, 0] + counts[:, 1] / 2) / 990
        self.category_np = np.argmax(self.card_np[:, 269:278], axis=1)
        self.economics_np = np.concatenate([p['economics'] for p in contexts])
        equity_model.validate_economics(self.economics_np, terminal_call_confirmed=True)
        public = np.concatenate([p['features'] for p in contexts]).astype(np.float32)
        self.lengths = np.asarray([len(p['rows']) for p in contexts], dtype=np.int64)
        if (np.any(self.lengths <= 0) or public.shape != (sum(self.lengths), 387)
                or len(self.economics_np) != len(public)):
            raise ValueError('Complete state rows required')
        for context in contexts:
            if not np.all(np.asarray(context['economics'])[:, 0] == context['stack']):
                raise ValueError('Context starting stack mismatch')
        if not np.isfinite(self.card_np).all() or not np.isfinite(public).all():
            raise ValueError('Nonfinite features')
        if np.any(public[:, equity_model.CARD_COLUMNS]):
            raise ValueError('Public context must not enter the uniform-equity head')
        self.offsets = np.r_[0, np.cumsum(self.lengths)[:-1]]
        self.cards = torch.as_tensor(self.card_np, device=device)
        self.public = torch.as_tensor(public, device=device)
        self.equity = torch.as_tensor(self.equity_np, device=device)
        self.economics = torch.as_tensor(self.economics_np, device=device)
        self.lengths_gpu = torch.as_tensor(self.lengths, device=device)
        self.offsets_gpu = torch.as_tensor(self.offsets, device=device)

    def assemble(self, states, cards):
        x = (self.cards[cards] + self.public[states]).contiguous()
        e = self.economics[states]
        target = ((self.equity[cards] * e[:, 1] - e[:, 2]) / e[:, 0]).to(torch.float32)
        return dict(x=x, actors=e[:, 3].to(torch.long), target=target,
                    economics=e, states=states, cards=cards)

    def sample(self, n, generator):
        # Same draw order/distribution as the established reference Dataset.
        context = torch.randint(len(self.contexts), (n,), device=self.device, generator=generator)
        u = torch.rand(n, device=self.device, generator=generator, dtype=torch.float64)
        states = self.offsets_gpu[context] + torch.floor(u * self.lengths_gpu[context]).to(torch.long)
        cards = torch.randint(len(self.card_np), (n,), device=self.device, generator=generator)
        return self.assemble(states, cards)


def fresh(seed, arm, device='cpu'):
    if arm == ARMS[0]:
        return baseline_fresh(seed, 387, device)
    if arm == ARMS[1]:
        return equity_model.fresh(seed, scope=equity_model.SCOPE, device=device)
    raise ValueError('Unregistered model arm')


def predict(model, arm, batch):
    dtype = next(model.parameters()).dtype
    x = batch['x'].to(dtype=dtype)
    if arm == ARMS[0]:
        return scores(model, x, batch['actors'])[:, :2]
    if arm == ARMS[1]:
        return model.normalized_values(x, batch['economics'], terminal_call_confirmed=True)
    raise ValueError('Unregistered model arm')


def value_loss(raw, target):
    return (raw[:, 0].square() + (raw[:, 1] - target).square()).mean() / 2


def arrays(model, arm):
    if arm == ARMS[0]:
        return {f'p{a}.{k}': v.detach().cpu().numpy().copy()
                for a, m in enumerate(model) for k, v in m.state_dict().items()}
    if arm == ARMS[1]:
        return {k: v.detach().cpu().numpy().copy() for k, v in model.state_dict().items()}
    raise ValueError('Unregistered model arm')


def save(path, model, arm):
    path = Path(path)
    with path.open('xb') as stream:
        np.savez_compressed(stream, **arrays(model, arm))
    return dict(file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def load(reference, seed, arm, device='cpu'):
    path = Path(reference['file'])
    if hashlib.sha256(path.read_bytes()).hexdigest() != reference['sha256']:
        raise ValueError('Changed checkpoint')
    model = fresh(seed, arm, device)
    expected = arrays(model, arm)
    with np.load(path, allow_pickle=False) as stored:
        if set(stored.files) != set(expected):
            raise ValueError('Wrong checkpoint keys')
        values = {}
        for key, template in expected.items():
            value = stored[key]
            if value.shape != template.shape or value.dtype != template.dtype or not np.isfinite(value).all():
                raise ValueError('Wrong checkpoint array: ' + key)
            if key == 'card_columns' and not np.array_equal(value, template):
                raise ValueError('Changed card feature contract')
            values[key] = torch.as_tensor(value.copy(), device=device)
    if arm == ARMS[0]:
        for a, m in enumerate(model):
            m.load_state_dict({k: values[f'p{a}.{k}'] for k in m.state_dict()}, strict=True)
    else:
        model.load_state_dict(values, strict=True)
    return model


def numpy_scores(weights, arm, features, economics):
    """Independent widened-weight CPU arithmetic for both model types."""
    x, e = np.asarray(features, dtype=np.float64), np.asarray(economics, dtype=np.float64)
    if x.shape != (len(e), 387) or not np.isfinite(x).all():
        raise ValueError('Complete finite feature rows required')
    equity_model.validate_economics(e, terminal_call_confirmed=True)
    if arm == ARMS[0]:
        wide = {k: np.asarray(v, dtype=np.float64) for k, v in weights.items()}
        output = np.empty((len(x), 2), dtype=np.float64)
        for a in (0, 1):
            selected = e[:, 3] == a
            if selected.any():
                output[selected] = dense_scores(wide, x[selected], a, 387)[:, :2]
        return output
    if arm == ARMS[1]:
        q = equity_model.numpy_equity(weights, x)
        priced = equity_model.price_estimate(q, e, scope=equity_model.SCOPE,
                                            terminal_call_confirmed=True)
        return np.column_stack((priced['fold_value_bb'], priced['normalized_call_value']))
    raise ValueError('Unregistered model arm')


def evaluate(model, arm, data, guard, *, detail):
    """Widen a copy; fitting parameters and optimizer state remain float32."""
    inference = copy.deepcopy(model).to(dtype=torch.float64).eval()
    records, nc = [], len(data.card_np)
    try:
        with torch.no_grad():
            for ci, context in enumerate(data.contexts):
                guard()
                offset, ns = int(data.offsets[ci]), int(data.lengths[ci])
                raw = np.empty((ns * nc, 2), dtype=np.float64)
                for lo in range(0, len(raw), 8192):
                    guard()
                    ix = torch.arange(lo, min(lo + 8192, len(raw)), device=data.device)
                    batch = data.assemble(offset + ix // nc, ix % nc)
                    raw[lo:lo + len(ix)] = predict(inference, arm, batch).cpu().numpy()
                # With fold score exactly zero, the inherited conversion is
                # exactly greedy call for positive call value, fold on ties.
                records.append(summarize_context(probabilities(raw), raw[:, 0], raw[:, 1],
                    data.equity_np, data.economics_np[offset:offset + ns], data.category_np,
                    float(context['stack']), data.board_count, detail=detail, guard=guard))
        return evaluation_summary(records)
    finally:
        del inference


def select(checkpoints):
    if not checkpoints:
        raise ValueError('No checkpoints')
    for c in checkpoints:
        score = c['validation']['context_balanced_mean_regret_stack_fraction']
        if not np.isfinite(score) or score < 0:
            raise ValueError('Invalid selection loss')
    return min(checkpoints, key=lambda c: (c['validation']['context_balanced_mean_regret_stack_fraction'], c['step']))


def fit_pair(seed, train, validation, store, guard, progress):
    """Single shared draw per update, separate unchanged Adam optimizers."""
    started = time.monotonic()
    models = {arm: fresh(seed, arm, train.device) for arm in ARMS}
    optimizers = {arm: torch.optim.Adam(m.parameters(), lr=.001, foreach=False) for arm, m in models.items()}
    generator = torch.Generator(device=train.device).manual_seed(seed + 100000)
    checkpoints = {arm: [] for arm in ARMS}
    batch_probes = []
    for step in range(STEPS + 1):
        if step in CHECKPOINTS:
            for arm, model in models.items():
                guard()
                metrics = evaluate(model, arm, validation, guard, detail=False)
                weights = save(Path(store) / f'{arm}-step-{step}.npz', model, arm)
                checkpoints[arm].append(dict(step=step, weights=weights, validation=metrics,
                                            batch_rng_sha256=rng_hash(generator)))
                progress('validation', seed=seed, arm=arm, step=step,
                         mean_normalized_regret=metrics['context_balanced_mean_regret_stack_fraction'])
        if step == STEPS:
            break
        if step % 64 == 0:
            guard()
        batch = train.sample(BATCH_SIZE, generator)
        if step % 1024 == 0:
            digest = hashlib.sha256()
            for key in ('states', 'cards', 'x', 'actors', 'target', 'economics'):
                digest.update(batch[key].detach().cpu().contiguous().numpy().tobytes())
            batch_probes.append(dict(step=step, shared_batch_sha256=digest.hexdigest()))
        # Both models receive the same objects; model forward never mutates them.
        for arm, model in models.items():
            model.train()
            optimizers[arm].zero_grad(set_to_none=True)
            loss = value_loss(predict(model, arm, batch), batch['target'])
            loss.backward()
            optimizers[arm].step()
            if step % 1024 == 0:
                measured = float(loss.detach())
                if not np.isfinite(measured):
                    raise ValueError('Nonfinite training loss')
                progress('fitting', seed=seed, arm=arm, step=step, last_normalized_loss=measured)
    for model in models.values():
        if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
            raise ValueError('Nonfinite trained model')
    return dict(seed=seed, steps=STEPS, batch_size=BATCH_SIZE, learning_rate=.001,
                paired_seconds=time.monotonic() - started, shared_batch_probes=batch_probes,
                shared_batch_objects=True, checkpoint_steps=list(CHECKPOINTS),
                fits=[dict(seed=seed, arm=arm, checkpoints=checkpoints[arm],
                           selected=select(checkpoints[arm])) for arm in ARMS],
                training_dtype='float32', evaluation_dtype='widened-float64')
