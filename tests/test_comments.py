from autopilot import comments


class Call:
    def __init__(self, result=None, boom=None, log=None, name=""):
        self.result, self.boom, self.log, self.name = result, boom, log, name

    def execute(self):
        if self.boom:
            raise self.boom
        return self.result


class Fake:
    """Just enough of the YouTube client: videos().list, commentThreads().insert/list, channels().list."""

    def __init__(self, public=(), threads=(), boom_on=()):
        self.public, self.threads, self.boom_on, self.inserted = set(public), list(threads), set(boom_on), []

    def videos(self):
        outer = self

        class V:
            def list(self, part, id):
                ids = id.split(",")
                if part == "status":
                    return Call({"items": [{"id": i, "status": {"privacyStatus": "public" if i in outer.public else "private"}} for i in ids]})
                return Call({"items": [{"id": i, "snippet": {"title": f"Title {i}"}} for i in ids]})
        return V()

    def commentThreads(self):
        outer = self

        class C:
            def insert(self, part, body):
                vid = body["snippet"]["videoId"]
                if vid in outer.boom_on:
                    return Call(boom=RuntimeError("commentsDisabled"))
                outer.inserted.append((vid, body["snippet"]["topLevelComment"]["snippet"]["textOriginal"]))
                return Call({"id": f"c-{vid}"})

            def list(self, **kw):
                return Call({"items": outer.threads})
        return C()

    def channels(self):
        class Ch:
            def list(self, part, mine):
                return Call({"items": [{"id": "CHAN"}]})
        return Ch()


def thread(i, at, author="viewer", by="UCviewer"):
    return {"id": f"t{i}", "snippet": {"videoId": "v1", "topLevelComment": {"snippet": {
        "videoId": "v1", "authorDisplayName": author, "authorChannelId": {"value": by}, "textOriginal": f"hello {i}", "publishedAt": at}}}}


def test_first_comments_go_only_on_public_videos_once_and_failures_are_counted():
    maps = {"a": {"comment": "Which part surprised you?"}, "b": {"comment": "Where have you seen this?"}, "c": {"title": "no question"}, "d": {"comment": "x?"}}
    ledger = comments.empty_ledger()
    yt = Fake(public={"a", "d"}, boom_on={"d"})
    assert comments.post_first_comments(yt, maps, ledger, log=lambda m: None) == 1
    assert yt.inserted == [("a", "Which part surprised you?")] and ledger["posted"]["a"]["comment_id"] == "c-a" and ledger["failed"] == {"d": 1}
    assert comments.post_first_comments(yt, maps, ledger, log=lambda m: None) == 0           # a is done, b still private, d retried and failed
    assert ledger["failed"]["d"] == 2 and len(yt.inserted) == 1
    yt.public.add("b")
    comments.post_first_comments(yt, maps, ledger, log=lambda m: None)
    assert [v for v, _ in yt.inserted] == ["a", "b"]
    for _ in range(3):
        comments.post_first_comments(yt, maps, ledger, log=lambda m: None)
    assert ledger["failed"]["d"] == comments.MAX_TRIES                                       # gives up after three tries


def test_viewer_comments_are_announced_once_our_own_are_skipped_and_the_first_look_is_quiet():
    sent = []
    ledger = comments.empty_ledger()
    yt = Fake(threads=[thread(1, "2026-11-02T10:00:00Z"), thread(2, "2026-11-02T11:00:00Z", author="us", by="CHAN")])
    comments.run_profile(yt, "en", "Brightwork Science", {}, ledger, sent.append, log=lambda m: None)
    assert sent == [] and ledger["seen_at"]["en"] == "2026-11-02T10:00:00Z"                  # first look: starting point only
    yt.threads = [thread(3, "2026-11-02T12:00:00Z", author="Sam"), thread(1, "2026-11-02T10:00:00Z")]
    comments.run_profile(yt, "en", "Brightwork Science", {}, ledger, sent.append, log=lambda m: None)
    assert len(sent) == 1 and "Sam: hello 3" in sent[0] and "Title v1" in sent[0] and "lc=t3" in sent[0]
    comments.run_profile(yt, "en", "Brightwork Science", {}, ledger, sent.append, log=lambda m: None)
    assert len(sent) == 1                                                                    # nothing new, nothing sent
