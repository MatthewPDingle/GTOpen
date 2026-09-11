"""Pass04 queue adapter for reviewed pass03 session deployment helpers.

Source preparation only. Parent must first verify qualification evidence. All
native/ownership/launch/rollback operations remain in the existing helpers.
"""
from pathlib import Path
import json
import sys

PASS = Path(__file__).resolve().parents[2]
ROOT = PASS.parents[3]
PREVIOUS = ROOT / 'research/autoresearch/passes/03-preflop-20260910/proposals/final-deployment'
sys.path.insert(0, str(PREVIOUS))
import session_guard as guard
import cutover

old_queues_clear = guard.queues_clear


def queues_clear():
    # Retain the old pass guard, then add this pass and its production builder.
    old_queues_clear()
    active = json.loads((PASS / 'active.json').read_text(encoding='utf-8'))
    guard.require(active.get('running') is False, 'pass04 queue is not explicitly stopped')
    labs = [ROOT / 'target/autoresearch/preflop-interactive-20260911',
            ROOT / 'target/autoresearch/preflop-interactive-production-20260911']
    # During restore, the new production EXE can legitimately own the live port.
    live_pid = guard.owner(56708)['pid']
    controllers = ('qualify_production.py', 'run_baseline_api.py', 'qualify_preview_api.py',
                   'run_large_warmstart.py', 'run_large128_queue.py', 'run_small128_queue.py',
                   'guarded_run.py')
    for process in guard.psutil.process_iter(['pid', 'exe', 'cmdline']):
        try:
            if process.pid == live_pid:
                continue
            executable = process.info['exe']
            if executable:
                guard.require(not any(Path(executable).resolve().is_relative_to(p.resolve()) for p in labs),
                              'pass04 research/test executable remains active')
            arguments = process.info['cmdline'] or []
            guard.require(not any(Path(arg).name in controllers for arg in arguments),
                          'pass04 qualification controller remains active')
        except (guard.psutil.NoSuchProcess, guard.psutil.AccessDenied):
            continue


def main():
    guard.require(len(sys.argv) > 1, 'use smoke, check-live, cutover or restore')
    guard.require('--execute' in sys.argv and '--queues-complete' in sys.argv,
                  'explicit --execute --queues-complete required after qualification review')
    guard.queues_clear = queues_clear
    if sys.argv[1] == 'cutover':
        sys.argv.pop(1)
        sys.argv.remove('--queues-complete')
        cutover.main()
    else:
        guard.main()


if __name__ == '__main__':
    main()
