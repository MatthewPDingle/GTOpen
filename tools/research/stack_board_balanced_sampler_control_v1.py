"""Independent CPU qualification for the visible-card sampler, no learning.

Default CLI is fixtures only, with synthetic exclusion groups and tiny splits;
it never selects the 1,344 study boards.  Full qualification is an explicit
``--qualify --seed INT --exclusions FILE`` action after source review.  FILE must
be a JSON list of canonical five-card groups.  A successful full run optionally
writes the selected records with ``--boards-output NEW_FILE`` and the report
with ``--output NEW_FILE``.  Existing paths are never overwritten.  Reports bind
the exclusion file, normalized union, code/helper hashes, interpreter, and exact
board sequence.  This control cannot prove completeness of the historical union.

Independent work: enumerate all 4**5 suit assignments for each recursively
generated legal rank partition, rejecting duplicate physical cards; reconstruct
cells and canonical groups without the sampler's helpers; enumerate 120 card
orders and 24 suit permutations for each cell representative; check exact quotas,
replay, changed seeds, mutual separation, historical exclusion, and bad inputs.
No random-frequency goodness-of-fit test or inference about poker accuracy.
"""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

os.environ.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
import stack_board_balanced_sampler_v1 as sampler
import stack_price_reference_v1 as reference

MAXIMUM_SECONDS = 60
MAXIMUM_OUTPUT_BYTES = 2 * 1024 * 1024
FIXTURE_SEED = 9297109
FIXTURE_SIZES = (("fit_random", 3), ("fit_structured", 13),
                 ("validation", 3), ("test", 3), ("stress", 13))


def _require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def _json_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def independent_cell(board):
    if (not isinstance(board, (list, tuple)) or len(board) != 5
            or any(type(card) is not int or card < 0 or card > 51 for card in board)
            or len(set(board)) != 5):
        raise ValueError("Invalid board")
    ranks = [sum(card // 4 == rank for card in board) for rank in range(13)]
    multiplicities = sorted((n for n in ranks if n), reverse=True)
    suit_maximum = max(sum(card % 4 == suit for card in board) for suit in range(4))
    return "-".join(str(n) for n in multiplicities) + "|s" + str(suit_maximum)


def independent_group(board):
    independent_cell(board)
    images = []
    for renaming in permutations((0, 1, 2, 3)):
        images.append(tuple(sorted(4 * (card // 4) + renaming[card % 4] for card in board)))
    return min(images)


def _partitions(total=5, largest=4):
    if total == 0:
        yield ()
    else:
        for first in range(min(total, largest), 0, -1):
            for rest in _partitions(total - first, first):
                yield (first,) + rest


def _independent_catalog():
    counts = Counter()
    representatives = {}
    physical_counts = {}
    for shape in sorted(_partitions()):
        slots = [rank for rank, count in enumerate(shape) for _ in range(count)]
        repeated_slots = math.prod(math.factorial(n) for n in shape)
        patterns = Counter()
        for suits in product(range(4), repeat=5):
            board = [4 * rank + suit for rank, suit in zip(slots, suits)]
            if len(set(board)) != 5:
                continue
            cell = independent_cell(board)
            patterns[cell] += 1
            representatives.setdefault(cell, board)
        rank_assignments = math.perm(13, len(shape)) // math.prod(
            math.factorial(n) for n in Counter(shape).values())
        for cell, count in patterns.items():
            _require(count % repeated_slots == 0, "Suit-slot symmetry count")
            counts[cell] = count // repeated_slots
            physical_counts[cell] = rank_assignments * counts[cell]
    cells = sorted(counts, key=lambda cell: (tuple(map(int, cell.split("|")[0].split("-"))),
                                           int(cell.split("|s")[1])))
    return cells, counts, representatives, physical_counts


def verify_records(records, exclusions, sizes):
    _require(isinstance(records, list), "Record list required")
    _require(len(records) == sum(count for _, count in sizes), "Total split size")
    cells, _, _, _ = _independent_catalog()
    excluded = {tuple(group) for group in exclusions}
    used = set()
    offset = 0
    cell_counts = {}
    for split, count in sizes:
        rows = records[offset:offset + count]
        offset += count
        observed = Counter()
        for index, row in enumerate(rows):
            _require(set(row) == {"split", "index", "board", "canonical_group", "cell"}, "Record fields")
            _require(row["split"] == split and type(row["index"]) is int and row["index"] == index,
                     "Split order and unique contiguous indices")
            cell = independent_cell(row["board"])
            group = independent_group(row["board"])
            _require(row["cell"] == cell, "Independent visible cell")
            _require(isinstance(row["canonical_group"], list)
                     and all(type(card) is int for card in row["canonical_group"])
                     and tuple(row["canonical_group"]) == group, "Independent canonical group")
            _require(group not in excluded and group not in used, "Historical and cross-split suit separation")
            used.add(group)
            observed[cell] += 1
        if split in ("fit_structured", "stress"):
            expected = {cell: count // len(cells) + (i < count % len(cells))
                        for i, cell in enumerate(cells)}
            _require(all(observed[cell] == n for cell, n in expected.items()), "Independent exact cell quotas")
        cell_counts[split] = dict(sorted(observed.items()))
    return cell_counts


def fixture_checks(deadline):
    cells, counts, representatives, physical_counts = _independent_catalog()
    _require(len(cells) == 13 and cells == sampler.feasible_cells(), "Exact feasible cells and order")
    _require(sum(physical_counts.values()) == math.comb(52, 5), "All physical boards counted once")
    _require(sum(counts.values()) == 1644, "Exact complete suit-template count")
    for cell, multiplicities, templates in sampler._catalog():
        _require(len(templates) == len(set(templates)) == counts[cell], "Complete nonduplicated suit templates")
        for template in templates:
            _require(tuple(map(len, template)) == multiplicities, "Template multiplicities")
            _require(all(tuple(sorted(set(suits))) == suits and all(0 <= s < 4 for s in suits)
                         for suits in template), "Legal ordered suit subsets")
            board = [4 * rank + suit for rank, suits in enumerate(template) for suit in suits]
            _require(independent_cell(board) == cell, "Every template is in its claimed cell")
    for count in (0, 1, 12, 13, 14, 64, 512):
        expected = {cell: count // 13 + (i < count % 13) for i, cell in enumerate(cells)}
        _require(sampler.allocation(count) == expected, "Frozen deterministic remainder")
    invariance_checks = 0
    for cell, board in representatives.items():
        group = independent_group(board)
        for ordered in permutations(board):
            _require(sampler.board_cell(ordered) == cell and sampler.board_group(ordered) == group,
                     "Card-order invariance")
            invariance_checks += 1
        for suit_map in permutations(range(4)):
            renamed = [4 * (card // 4) + suit_map[card % 4] for card in board]
            _require(sampler.board_cell(renamed) == cell and sampler.board_group(renamed) == group,
                     "Suit-renaming invariance")
            invariance_checks += 1
        _require(time.monotonic() < deadline, "Fixture time limit")
    fixture_exclusions = {independent_group(board) for board in representatives.values()}
    frozen_exclusions = sorted(fixture_exclusions)
    kwargs = dict(max_candidates=1000, max_bucket_candidates=200)
    first = sampler._select(FIXTURE_SEED, fixture_exclusions, FIXTURE_SIZES, **kwargs)
    _require(first == sampler._select(FIXTURE_SEED, list(reversed(frozen_exclusions)), FIXTURE_SIZES, **kwargs),
             "Exact fixture seeded replay and exclusion-order invariance")
    other_seed = sampler._select(FIXTURE_SEED + 1, fixture_exclusions, FIXTURE_SIZES, **kwargs)
    _require(first != other_seed, "Seed sensitivity")
    _require(first == sampler.select_boards(FIXTURE_SEED, fixture_exclusions, counts=dict(FIXTURE_SIZES)),
             "Public reduced-count control API")
    _require(sampler.select_boards(FIXTURE_SEED, [], counts={name: 0 for name, _ in FIXTURE_SIZES}) == [],
             "Zero counts yield no boards")
    _require(sorted(fixture_exclusions) == frozen_exclusions, "Caller exclusion set was not mutated")
    verify_records(first, fixture_exclusions, FIXTURE_SIZES)
    verify_records(other_seed, fixture_exclusions, FIXTURE_SIZES)
    # Force an actual rejection of a previously accepted group on the same stream.
    extended = fixture_exclusions | {tuple(first[0]["canonical_group"])}
    rejected_replay = sampler._select(FIXTURE_SEED, extended, FIXTURE_SIZES, **kwargs)
    verify_records(rejected_replay, extended, FIXTURE_SIZES)
    _require(first[0] != rejected_replay[0], "Excluded candidate was redrawn")
    rejected = 0
    invalid_boards = (None, [], [0, 1, 2, 3], [0, 1, 2, 3, 3], [0, 1, 2, 3, 52],
                      [0, 1, 2, 3, -1], [0, 1, 2, 3, True], [0, 1, 2, 3, 4.0], "01234")
    for bad in invalid_boards:
        try:
            sampler.board_cell(bad)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("Invalid board accepted")
    for bad in (None, True, -1, 2**64, 1.0, "1"):
        try:
            sampler._select(bad, [], FIXTURE_SIZES, **kwargs)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("Invalid seed accepted")
    for bad in (None, "[]", {}, [[0, 1, 2, 3, 3]], [[4, 3, 2, 1, 0]], [[0, 1, 2, 3, True]]):
        try:
            sampler._select(FIXTURE_SEED, bad, FIXTURE_SIZES, **kwargs)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("Invalid exclusion collection accepted")
    for bad in (-1, True, 1.0, 1_000_001):
        try:
            sampler.allocation(bad)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("Invalid allocation accepted")
    for bad in ({}, {name: -1 for name, _ in FIXTURE_SIZES},
                {name: True for name, _ in FIXTURE_SIZES},
                {name: maximum + 1 for name, maximum in sampler.SPLIT_SIZES}):
        try:
            sampler.select_boards(FIXTURE_SEED, [], counts=bad)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("Invalid control counts accepted")
    try:
        sampler._select(FIXTURE_SEED, [], FIXTURE_SIZES, max_candidates=1, max_bucket_candidates=1)
    except sampler.SelectionExhausted:
        rejected += 1
    else:
        raise AssertionError("Global exhaustion was not preserved")
    # Reject the first deterministic candidate with only one permitted draw.
    try:
        sampler._select(FIXTURE_SEED, extended, FIXTURE_SIZES, max_candidates=100,
                        max_bucket_candidates=1)
    except sampler.SelectionExhausted:
        rejected += 1
    else:
        raise AssertionError("Bucket exhaustion was not preserved")
    _require(time.monotonic() < deadline, "Fixture time limit")
    retained = [dict(case=case, **row) for case, rows in
                (("primary", first), ("other_seed", other_seed), ("excluded_redraw", rejected_replay))
                for row in rows]
    retained_groups = sorted({tuple(row["canonical_group"]) for row in retained})
    return dict(feasible_cells=cells, suit_template_counts=dict(counts),
                physical_board_counts=physical_counts, total_physical_boards=sum(physical_counts.values()),
                card_order_and_suit_invariance_checks=invariance_checks, negative_controls_rejected=rejected,
                fixture_records=len(first), fixture_record_sha256=_json_hash(first),
                fixture_seed=FIXTURE_SEED, retained_fixture_records=retained,
                retained_fixture_canonical_groups=retained_groups,
                retained_fixture_group_count=len(retained_groups),
                exact_replay=True, exclusion_order_invariant=True, study_boards_selected=False)


def qualify(seed, exclusions, deadline):
    """Explicit complete board-selection qualification after source review."""
    first = sampler.select_boards(seed, exclusions)
    _require(time.monotonic() < deadline, "Full-selection time limit")
    _require(first == sampler.select_boards(seed, list(reversed(exclusions))),
             "Full exact seeded replay and exclusion-order invariance")
    _require(time.monotonic() < deadline, "Replay time limit")
    counts = verify_records(first, exclusions, sampler.SPLIT_SIZES)
    _require(time.monotonic() < deadline, "Full independent verification time limit")
    return first, dict(study_boards_selected=True, records=len(first),
                       record_sha256=_json_hash(first), cell_counts=counts,
                       exact_replay=True, mutually_suit_disjoint=True,
                       historical_exclusion_verified=True,
                       historical_union_completeness_verified=False)


def _write_new(path, value):
    serialized = json.dumps(value, sort_keys=True, indent=2) + "\n"
    if len(serialized.encode("utf-8")) > MAXIMUM_OUTPUT_BYTES:
        raise ValueError("Output exceeds the 2 MiB evidence cap")
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualify", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--exclusions", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--boards-output", type=Path)
    args = parser.parse_args()
    if args.qualify != (args.seed is not None and args.exclusions is not None):
        parser.error("Full qualification requires --qualify, --seed, and --exclusions together")
    if not args.qualify and (args.seed is not None or args.exclusions is not None or args.boards_output is not None):
        parser.error("Fixture-only mode does not accept study seed, exclusions, or boards output")
    targets = [path.resolve() for path in (args.output, args.boards_output) if path is not None]
    if len(targets) != len(set(targets)) or any(path.exists() for path in targets):
        parser.error("Output paths must be distinct new files")
    start = time.monotonic()
    deadline = start + MAXIMUM_SECONDS
    sources = [Path(__file__).resolve(), Path(sampler.__file__).resolve(), Path(reference.__file__).resolve()]
    hashes = {str(path): _file_hash(path) for path in sources}
    report = dict(method=sampler.METHOD, passed=False, mode="qualification" if args.qualify else "fixtures",
                  source_sha256=hashes, python=sys.version, implementation=platform.python_implementation(),
                  maximum_seconds=MAXIMUM_SECONDS, maximum_output_bytes=MAXIMUM_OUTPUT_BYTES,
                  new_equity_labels=0, training=False, cuda=False,
                  production_modified=False)
    boards = None
    try:
        report["fixtures"] = fixture_checks(deadline)
        if args.qualify:
            exclusion_hash = _file_hash(args.exclusions)
            exclusions = json.loads(args.exclusions.read_text(encoding="utf-8"))
            if not isinstance(exclusions, list):
                raise ValueError("Exclusion file must contain a JSON list of canonical groups")
            canonical = sampler._validated_exclusions(exclusions)
            retained_control_groups = {tuple(group) for group in report["fixtures"]["retained_fixture_canonical_groups"]}
            _require(retained_control_groups <= canonical,
                     "Historical exclusions must include the retained control groups from fixture mode")
            report.update(seed=args.seed, exclusion_path=str(args.exclusions.resolve()),
                          exclusion_file_sha256=exclusion_hash,
                          exclusion_union_sha256=_json_hash(sorted(canonical)), excluded_groups=len(canonical))
            boards, report["qualification"] = qualify(args.seed, sorted(canonical), deadline)
            _require(_file_hash(args.exclusions) == exclusion_hash, "Exclusion file changed during control")
        _require(all(_file_hash(path) == digest for path, digest in hashes.items()), "Source changed during control")
        _require(time.monotonic() < deadline, "Overall control time limit")
        if boards is not None and args.boards_output is not None:
            combined_bytes = len((json.dumps(boards, sort_keys=True, indent=2) + "\n").encode("utf-8"))
            combined_bytes += len((json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8"))
            _require(combined_bytes + 4096 <= MAXIMUM_OUTPUT_BYTES, "Combined evidence output cap")
            _write_new(args.boards_output, boards)
            report["boards_path"] = str(args.boards_output.resolve())
            report["boards_file_sha256"] = _file_hash(args.boards_output)
        report["passed"] = True
    except Exception as exc:
        report["error"] = dict(type=type(exc).__name__, message=str(exc))
    report["seconds"] = time.monotonic() - start
    if args.output is not None:
        _write_new(args.output, report)
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
