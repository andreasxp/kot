from contextlib import contextmanager


@contextmanager
def atleave(*fn):
    """Use during `with` statement to call something at the end regardless of exceptions.

    Example:
    ```
    resource = Resource()
    with atleave(lambda: release(resource)):
        # Work on resource
    ```
    """
    try:
        yield None
    finally:
        for f in fn:
            f()
