"""Native fixed-teacher labels on an explicitly supplied conditional chance plan.

No teacher selection, sampling, fitting or scientific admission. All future
policies are inferred before forcing history. Inputs use visible-only queries.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import numpy as np
import stack_context_teacher_conditioning_v1 as condition
from stack_context_teacher_path_v1 import Binding, encoded


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    if not isinstance(value, bytes):value = encoded(value)
    with Path(path).open('xb') as stream:
        stream.write(value);stream.flush();os.fsync(stream.fileno())


def checked_values(native, names, count, context):
    if (native.get('format') != 2 or native.get('terminal_estimator') != 'conditional-preflop-allin-v1'
            or native.get('postflop_outcomes') != 'sampled-board'
            or native.get('fixed_policy_evaluation_only') is not True
            or native.get('bounds_best_response_above') is not False
            or [r['name'] for r in native['profiles']] != names):
        raise ValueError('Changed native fixed-profile payoff contract')
    for field in ('maximum_forward_cashflow_error', 'maximum_conservation_error'):
        value = native[field]
        if type(value) not in (int, float) or not np.isfinite(value) or not 0 <= value < 1e-10:
            raise ValueError('Native cashflow check failed')
    result = {};stack = context['config']['stack'];dead = context['dead_money']
    for profile in native['profiles']:
        if len(profile['deals']) != count:raise ValueError('Incomplete native physical-deal values')
        values = []
        for i, row in enumerate(profile['deals']):
            v = np.asarray(row['values'], dtype=np.float64)
            if (row['deal_index'] != i or v.shape != (2,) or not np.isfinite(v).all()
                    or np.any(v < -stack-1e-9) or np.any(v > stack+dead+1e-9)
                    or not np.isfinite(row['expected_rake']) or row['expected_rake'] < -1e-12
                    or abs(row['terminal_mass']-1) > 1e-12
                    or abs(float(v.sum())+row['expected_rake']-dead) > 1e-10):
                raise ValueError('Native terminal value, order, mass or ledger bound changed')
            values.append(v)
        result[profile['name']] = np.asarray(values)
    return result


def shared_intervention(frozen, deals, hi, action):
    """Merge identical public-history interventions without changing future rows."""
    rows = frozen.binding.queries['observations'];forced = {};targets = set()
    for deal in deals:
        index, path = frozen.binding.trace(deal, hi);targets.add(index)
        for i, a, _ in path:
            if i in forced and forced[i] != a:raise ValueError('Conflicting shared past-action intervention')
            forced[i] = a
    if len(targets) != 1 or targets.intersection(forced):
        raise ValueError('Conditional target differs across hidden hands or occurs in its past')
    index = next(iter(targets));n = rows[index]['n'];changed = frozen.p.copy()
    for i, a in forced.items():changed[i] = 0.;changed[i, a] = 1.
    if action is not None:
        if type(action) is not int or not 0 <= action < n:raise ValueError('Illegal target intervention')
        changed[index] = 0.;changed[index, action] = 1.
    changed.flags.writeable = False
    return changed, index, sorted(forced)


def evaluate_plan(*, history, posterior, plan, start_state, teacher, teacher_manifest,
                  cache, query_executable, evaluation_executable, folder, guard):
    """Return paired conditional Q/advantages, preserving every native artifact.

    The caller owns the scientific teacher/source/budget admission. A manifest
    must describe the immutable bank; the adapter records it, not selects it.
    Zero own-entry/history support is refused by this support-only interface.
    """
    condition.audit_plan(posterior, plan, start_state)
    condition.validate_posterior(posterior)
    if plan['draw_count'] < 1 or not posterior['teacher_state_supported']:
        raise ValueError('Nonempty supported conditional information state required')
    if not isinstance(teacher_manifest, dict) or not teacher_manifest:
        raise ValueError('Explicit immutable teacher manifest required')
    if not hasattr(teacher, 'average'):raise ValueError('Original fixed teacher inference required')
    folder = Path(folder)
    if folder.exists():raise ValueError('Preserve existing native-plan attempt; no replacement or retry')
    guard()
    # Reconstruct the original history probabilities from the same teacher;
    # do not compute reach under any forced policy.
    hp, _ = teacher.average(history['queries'], guard=guard)
    bound_history = Binding(history['queries']);history_frozen = bound_history.freeze(hp)
    if encoded(condition.posterior(history, history_frozen)) != encoded(posterior):
        raise ValueError('Conditional plan uses a different original teacher/history')
    folder.mkdir()
    teacher_identity = hashlib.sha256(encoded(teacher_manifest)).hexdigest()
    target = posterior['target'];context_source = posterior['context_source'];context = json.loads(context_source)
    save(folder/'teacher-manifest.json', teacher_manifest)
    save(folder/'conditional-history.json', history)
    save(folder/'posterior.json', posterior);save(folder/'chance-start.json', start_state)
    save(folder/'chance-plan.json', plan)
    save(folder/'context.json', context_source.encode())
    batch = dict(format=2, batch_id='fixed-teacher-native-plan-v1/'+plan['posterior_sha256'],
                 seed=0, query_limit=1000000, deals=plan['deals'])
    # seed here is inert native metadata; the chance stream is authenticated
    # through the complete explicit plan and its local RNG checkpoints.
    save(folder/'batch.json', batch)
    def invoke(label, arguments):
        guard()
        done = subprocess.run(list(map(str, arguments)), capture_output=True, text=True,
            timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
        save(folder/(label+'-process.json'), dict(code=done.returncode, stdout=done.stdout, stderr=done.stderr))
        if done.returncode:raise ValueError(label+' native failure: '+done.stderr[-2000:])
        guard()
    invoke('queries', [query_executable, 'queries', folder/'context.json', folder/'batch.json', '-', folder/'queries.json'])
    query = json.loads((folder/'queries.json').read_bytes())
    if query['context_source'] != context_source or query['batch_source'].encode() != (folder/'batch.json').read_bytes():
        raise ValueError('Changed native query context or physical plan')
    binding = Binding(query)
    original, _ = teacher.average(query, guard=guard);frozen = binding.freeze(original)
    overlap_error = 0.;overlap = 0
    for i, row in enumerate(query['observations']):
        key = (row['hi'], row['lo'])
        if key in bound_history.lookup:
            overlap += 1;overlap_error = max(overlap_error, float(np.max(abs(frozen.p[i]-hp[bound_history.lookup[key]]))))
    if not overlap or overlap_error > 1e-10:raise ValueError('Original history/future teacher inference mismatch')
    conditional = cache.batch(batch);cache.check_batch(conditional)
    save(folder/'conditional-batch.json', conditional)
    profiles = [];future_checks = [];indices = [];changed_rows = set()
    def append(name, probability):
        rows = [dict(hi=r['hi'], lo=r['lo'], actor=r['actor'], n=r['n'], probabilities=p.tolist())
                for r, p in zip(query['observations'], probability)]
        profiles.append(dict(name=name, policies=rows))
    past_only, index, past = shared_intervention(frozen, plan['deals'], target['hi'], None)
    if query['observations'][index]['lo'] != target['lo'] or query['observations'][index]['actor'] != target['actor']:
        raise ValueError('Original visible target changed')
    sigma_error = float(np.max(abs(frozen.p[index, :target['n']]-posterior['original_sigma'])))
    if sigma_error > 1e-10:raise ValueError('Original target mixture changed')
    # The mix control uses exactly the original posterior target strategy.
    mixed = past_only.copy();mixed[index] = 0.;mixed[index, :target['n']] = posterior['original_sigma']
    append('original-target-mix', mixed)
    changed_rows.update(past);changed_rows.add(index)
    unchanged = np.array([i for i in range(len(query['observations'])) if i not in changed_rows])
    for a in range(target['n']):
        probability, actual_index, actual_past = shared_intervention(frozen, plan['deals'], target['hi'], a)
        if actual_index != index or actual_past != past:raise ValueError('Action-specific conditional history changed')
        if len(unchanged) and not np.array_equal(probability[unchanged], frozen.p[unchanged]):
            raise ValueError('Future teacher policies changed under intervention')
        future_checks.append(len(unchanged));append('action'+str(a), probability)
    save(folder/'profiles.json', dict(format=1, context_source=context_source,
        batch_source=(folder/'conditional-batch.json').read_bytes().decode(), profiles=profiles))
    invoke('evaluation', [evaluation_executable, folder/'context.json', folder/'conditional-batch.json',
                          folder/'profiles.json', folder/'native.json'])
    native = json.loads((folder/'native.json').read_bytes())
    values = checked_values(native, [p['name'] for p in profiles], plan['draw_count'], context)
    q = np.stack([values['action'+str(a)][:, target['actor']] for a in range(target['n'])], axis=1)
    expected_mix = np.asarray(values['original-target-mix'][:, target['actor']])
    mixture_error = float(np.max(abs(q @ np.asarray(posterior['original_sigma'])-expected_mix)))
    if mixture_error > 1e-10:raise ValueError('Native same-teacher Q/baseline mixture failed')
    reduced = condition.sampled_advantage(posterior, plan, q, start_state=start_state)
    receipt = dict(complete=True, teacher_manifest_sha256=teacher_identity,
        history_frozen_teacher_sha256=history_frozen.identity, future_frozen_teacher_sha256=frozen.identity,
        posterior_sha256=posterior['sha256'], draw_count=plan['draw_count'], target=target,
        queries=len(query['observations']), native_calls=2, forced_past_rows=past,
        unchanged_future_rows_per_action=future_checks, native_original_history_overlap_rows=overlap,
        maximum_original_history_policy_error=overlap_error, original_sigma_error=sigma_error,
        mixture_error=mixture_error, per_draw_action_values=q.tolist(),
        action_values=reduced['action_values'].tolist(), value=reduced['value'],
        normalized_advantage=reduced['advantage'].tolist(),
        arithmetic_mean_retain_draw_multiplicity=True, posterior_applied_once=True,
        query_inputs_visible_only=True, original_teacher_inferred_before_interventions=True,
        terminal_estimator='conditional-preflop-allin-v1', postflop_outcomes='sampled-board',
        executable_sha256={str(p):sha(p) for p in (query_executable, evaluation_executable)},
        allin_cache_sha256=cache.sha256, scientific_admission_by_adapter=False,
        artifacts={str(p.relative_to(folder)):sha(p) for p in folder.iterdir() if p.is_file()})
    save(folder/'result.json', receipt)
    return receipt
