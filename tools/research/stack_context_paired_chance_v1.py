"""Separate matched chance inputs from each arm's necessarily distinct state.

The whole plan must first validate against its own arm's frozen parent. Only
then compare the board draw and registered draw configuration across arms.
This is a proposed comparator correction; it does not edit any old registration,
failure, checkpoint or matching record, or resume scientific work.
"""
import hashlib
import json
from board_root_accumulator_v1 import BoardRootRegrets

FIELDS = {'format', 'method', 'generation', 'parent_state_sha256', 'config_sha256', 'boards'}


def chance_identity(plan, *, parent_state, expected_config):
    if not isinstance(plan, dict) or set(plan) != FIELDS:
        raise ValueError('Complete known board-plan contract required')
    state = BoardRootRegrets.restore(parent_state, expected_config=expected_config)
    if plan != state.plan():
        raise ValueError('Board plan is not the exact registered draw from its own parent state')
    chance = {key:value for key,value in plan.items() if key != 'parent_state_sha256'}
    identity = hashlib.sha256((json.dumps(chance, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()).hexdigest()
    return dict(chance_sha256=identity, parent_state_sha256=plan['parent_state_sha256'],
                generation=plan['generation'], boards=plan['boards'], config_sha256=plan['config_sha256'])


def matched_board_chance(left, right, *, left_parent, right_parent, expected_config):
    a = chance_identity(left, parent_state=left_parent, expected_config=expected_config)
    b = chance_identity(right, parent_state=right_parent, expected_config=expected_config)
    if a['chance_sha256'] != b['chance_sha256']:
        raise ValueError('Different registered chance inputs between matched arms')
    return dict(matched=True, chance_sha256=a['chance_sha256'], generation=a['generation'],
        boards=a['boards'], config_sha256=a['config_sha256'],
        left_parent_state_sha256=a['parent_state_sha256'], right_parent_state_sha256=b['parent_state_sha256'],
        parents_are_identical=a['parent_state_sha256'] == b['parent_state_sha256'],
        each_parent_validated=True)
