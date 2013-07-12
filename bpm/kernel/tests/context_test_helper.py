def apply_context(test, contextmanager):
    contextmanager.__enter__()
    test.addCleanup(lambda: contextmanager.__exit__(None, None, None))