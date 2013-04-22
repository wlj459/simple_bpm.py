"""
bpm.engine.kernel.states
========================

Built-in task states.
"""

CREATED = 'CREATED'
PENDING = 'PENDING'
READY = 'READY'
RUNNING = 'RUNNING'
BLOCKED = 'BLOCKED'
SUSPENDED = 'SUSPENDED'
SUCCESS = 'SUCCESS'
FAILURE = 'FAILURE'
REVOKED = 'REVOKED'

TRANSITION = {
    CREATED:    frozenset([PENDING, REVOKED]),
    PENDING:    frozenset([READY, REVOKED]),
    READY:      frozenset([RUNNING, REVOKED, SUSPENDED]),
    RUNNING:    frozenset([BLOCKED, SUCCESS, FAILURE, REVOKED, SUSPENDED]),
    BLOCKED:    frozenset([READY, REVOKED, SUSPENDED]),
    SUSPENDED:  frozenset([READY, REVOKED]),
    SUCCESS:    frozenset([]),
    FAILURE:    frozenset([]),
    REVOKED:    frozenset([]),
}


def can_transit(from_state, to_state):
    if from_state in TRANSITION:
        if to_state in TRANSITION[from_state]:
            return True
