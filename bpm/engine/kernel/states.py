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

ALL_STATES = frozenset([CREATED, PENDING, READY, RUNNING,
                        BLOCKED, SUSPENDED, SUCCESS, FAILURE, REVOKED])
ARCHIVED_STATES = frozenset([SUCCESS, FAILURE, REVOKED])


class ConstantDict(dict):
    """ConstantDict is a subclass of :class:`dict`, implementing __setitem__
    method to avoid item assignment::

    >>> d = ConstantDict({'key': 'value'})
    >>> d['key'] = 'value'
    Traceback (most recent call last):
        ...
    TypeError: 'ConstantDict' object does not support item assignment
    """

    def __setitem__(self, key, value):
        raise TypeError("'%s' object does not support item assignment"
                        % self.__class__.__name__)


_PRECEDENCE = ConstantDict({
    CREATED: 1,
    PENDING: 2,
    READY: 10,
    RUNNING: 11,
    BLOCKED: 12,
    SUSPENDED: 19,
    SUCCESS: 99,
    FAILURE: 99,
    REVOKED: 89,
})


def precedence(state):
    """Get the precedence for state::

    >>> precedence(PENDING)
    2

    >>> precedence('UNKNOWN')
    0
    """
    if state in _PRECEDENCE:
        return _PRECEDENCE[state]
    else:
        return 0


class State(str):
    """State is a subclass of :class:`str`, implementing comparison
    methods adhering to state precedence rules::

        >>> State(PENDING) < State(SUCCESS)
        True

        >>> State(FAILURE) < State(REVOKED)
        False

        >>> State(SUCCESS) <= State(FAILURE)
        True
    """

    def __gt__(self, other):
        return precedence(self) > precedence(other)

    def __ge__(self, other):
        return precedence(self) >= precedence(other)

    def __lt__(self, other):
        return precedence(self) < precedence(other)

    def __le__(self, other):
        return precedence(self) <= precedence(other)


_TRANSITION = ConstantDict({
    CREATED: frozenset([PENDING, REVOKED]),
    PENDING: frozenset([READY, REVOKED]),
    READY: frozenset([RUNNING, REVOKED, SUSPENDED]),
    RUNNING: frozenset([BLOCKED, SUCCESS, FAILURE]),
    BLOCKED: frozenset([READY, REVOKED]),
    SUSPENDED: frozenset([READY, REVOKED]),
    SUCCESS: frozenset([]),
    FAILURE: frozenset([]),
    REVOKED: frozenset([]),
})


def can_transit(from_state, to_state):
    """Test if :param:`from_state` can transit to :param:`to_state`::

    >>> can_transit(CREATED, PENDING)
    True

    >>> can_transit(CREATED, READY)
    False
    """
    if from_state in _TRANSITION:
        if to_state in _TRANSITION[from_state]:
            return True
    return False