"""One place for web requests, so a half-sent answer cannot crash a run.

`urllib.request.urlopen(...).read()` can raise http.client.IncompleteRead, RemoteDisconnected or BadStatusLine when a server drops the
connection. Those are NOT OSErrors, so none of our "network trouble, try the next source" handlers caught them: on 11 Nov 2026 one
IncompleteRead(0 bytes read) from a model API failed the whole Plotline run. `urlopen` here reads the whole answer inside the try and turns
those errors into ConnectionError (an OSError), which every existing handler already understands."""
import http.client
import io
import urllib.request


class Response(io.BytesIO):
    """The whole answer, already read: works with json.load(...), .read(), and `with ... as r`. Carries the status and headers."""

    def __init__(self, body: bytes, status: int | None, headers) -> None:
        super().__init__(body)
        self.status, self.headers = status, headers

    def getcode(self) -> int | None:
        return self.status


def urlopen(req, timeout: float = 30) -> Response:
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        try:
            body = r.read()
        finally:
            close = getattr(r, "close", None)
            if close:
                close()
    except http.client.HTTPException as exc:
        raise ConnectionError(f"{type(exc).__name__}: {exc}") from exc
    return Response(body, getattr(r, "status", None), getattr(r, "headers", None))
