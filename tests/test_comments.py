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


def test_drafts_are_empty_for_questions_criticism_spam_and_bad_wording():
    gen = lambda k, d: (lambda p: {"kind": k, "draft": d})
    assert comments.make_draft("great video", "T", "C", gen("praise", "Thank you, glad it helped. Which part did you like most?")) == {
        "kind": "praise", "draft": "Thank you, glad it helped. Which part did you like most?"}
    for kind in ("question", "criticism", "spam"):
        assert comments.make_draft("x", "T", "C", gen(kind, "A draft"))["draft"] == ""
    for bad in ("See https://example.com", "Thanks 😀", "x" * 400, ""):
        assert comments.make_draft("x", "T", "C", gen("praise", bad))["draft"] == ""
    assert comments.make_draft("x", "T", "C", lambda p: (_ for _ in ()).throw(ValueError("down"))) == {"kind": "other", "draft": ""}


def test_commands_are_parsed_strictly():
    p = comments.parse_command
    assert p("ok 3") == ("post", "3", None) and p("Yes #12") == ("post", "12", None) and p("ok all") == ("post", "all", None)
    assert p("skip 4") == ("skip", "4", None)
    assert p("3: Thanks, glad it helped") == ("custom", "3", "Thanks, glad it helped")
    assert p("hello") is None and p("ok") is None and p("skip all") == ("skip", "all", None)


class ReplyClient:
    def __init__(self):
        self.posted = []

    def comments(self):
        outer = self

        class C:
            def insert(self, part, body):
                outer.posted.append((body["snippet"]["parentId"], body["snippet"]["textOriginal"]))
                return Call({"id": f"r{len(outer.posted)}"})
        return C()


def pending_ledger():
    led = comments.empty_ledger()
    now = "2026-11-02T10:00:00+00:00"
    led["pending"] = {"1": {"profile": "en", "thread": "t1", "video": "v", "author": "a", "text": "nice", "draft": "Thank you!", "kind": "praise", "at": now, "status": "waiting"},
                      "2": {"profile": "en", "thread": "t2", "video": "v", "author": "b", "text": "why?", "draft": "", "kind": "question", "at": now, "status": "waiting"}}
    return led


def test_replies_are_posted_only_after_the_owner_approves_and_only_once():
    led, yt, sent = pending_ledger(), ReplyClient(), []
    ups = [{"update_id": 10, "chat_id": "999", "text": "ok 1"},                 # a stranger: ignored
           {"update_id": 11, "chat_id": "42", "text": "ok 2"},                  # no draft: asks for own words
           {"update_id": 12, "chat_id": "42", "text": "ok 1"},
           {"update_id": 13, "chat_id": "42", "text": "ok 1"},                  # already posted
           {"update_id": 14, "chat_id": "42", "text": "2: Good question, it is because of friction."}]
    n = comments.process_approvals(ups, led, {"en": yt}, "42", sent.append, log=lambda m: None)
    assert n == 2 and yt.posted == [("t1", "Thank you!"), ("t2", "Good question, it is because of friction.")]
    assert led["pending"]["1"]["status"] == "posted" and led["tg_offset"] == 15
    assert any("no draft" in m for m in sent) and any("nothing waiting" in m for m in sent)


def test_skip_ok_all_and_failures_leave_things_safe():
    led, yt, sent = pending_ledger(), ReplyClient(), []
    comments.process_approvals([{"update_id": 1, "chat_id": "42", "text": "skip 2"}, {"update_id": 2, "chat_id": "42", "text": "ok all"}], led, {"en": yt}, "42", sent.append,
                               log=lambda m: None)
    assert yt.posted == [("t1", "Thank you!")] and led["pending"]["2"]["status"] == "skipped"

    class Broken(ReplyClient):
        def comments(self):
            class C:
                def insert(self, part, body):
                    return Call(boom=RuntimeError("quota"))
            return C()
    led2 = pending_ledger()
    comments.process_approvals([{"update_id": 3, "chat_id": "42", "text": "ok 1"}], led2, {"en": Broken()}, "42", sent.append, log=lambda m: None)
    assert led2["pending"]["1"]["status"] == "waiting" and "could not post" in sent[-1]


def test_new_comments_get_numbered_drafts_and_old_pending_ones_expire():
    sent = []
    ledger = comments.empty_ledger()
    ledger["seen_at"]["en"] = "2026-11-02T09:00:00Z"
    yt = Fake(threads=[thread(5, "2026-11-02T12:00:00Z", author="Sam")])
    comments.run_profile(yt, "en", "Brightwork Science", {}, ledger, sent.append, log=lambda m: None, gen=lambda p: {"kind": "praise", "draft": "Thanks, Sam."})
    assert ledger["pending"]["1"]["draft"] == "Thanks, Sam." and ledger["next_id"] == 2
    assert "#1 New comment" in sent[0] and "ok 1" in sent[0] and "Draft reply (praise): Thanks, Sam." in sent[0]
    ledger["pending"]["1"]["at"] = "2026-10-01T00:00:00+00:00"
    comments.expire_pending(ledger)
    assert ledger["pending"] == {}
