class TransientError(RuntimeError):
    """An outage or quota wall that is not the job's fault. The job stays pending and is retried
    on a later run without counting against its attempt limit."""


class RestartJob(RuntimeError):
    """A stage's input files are gone (e.g. a new CI runner after an interrupted run). Rewind the job
    to the start and regenerate; this is not a failure and does not count as an attempt."""
