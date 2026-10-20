class TransientError(RuntimeError):
    """An outage or quota wall that is not the job's fault. The job stays pending and is retried
    on a later run without counting against its attempt limit."""
