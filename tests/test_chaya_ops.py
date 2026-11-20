from datetime import datetime, timezone

from chaya import ops

IST = ops.IST


def at(y, m, d, h, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=IST).astimezone(timezone.utc)


def test_first_slot_is_today_when_far_enough_ahead():
    assert ops.next_slot(ops.empty_state(), at(2026, 11, 20, 10)) == "2026-11-20T12:30:00Z"      # 18:00 IST


def test_slot_moves_to_tomorrow_when_too_close():
    assert ops.next_slot(ops.empty_state(), at(2026, 11, 20, 16)) == "2026-11-21T12:30:00Z"


def test_slots_are_one_a_day_after_the_last_taken():
    st = ops.empty_state()
    st["items"]["a"] = {"status": "approved", "publish_at": "2026-11-23T12:30:00Z"}
    st["items"]["b"] = {"status": "held", "publish_at": "2027-01-01T12:30:00Z"}      # held ones do not count
    assert ops.next_slot(st, at(2026, 11, 20, 9)) == "2026-11-24T12:30:00Z"


def test_pick_next_skips_done_and_waits_when_three_are_waiting():
    q = [{"content": "x", "id": "a"}, {"content": "x", "id": "b"}]
    st = ops.empty_state()
    st["items"]["a"] = {"status": "uploaded"}
    assert ops.pick_next(q, st)["id"] == "b"
    for i in "123":
        st["items"][i] = {"status": "awaiting"}
    assert ops.pick_next(q, st) is None


def test_green_schedules_red_holds_and_other_chats_are_ignored():
    st = ops.empty_state()
    st["items"]["a"] = {"status": "awaiting"}
    st["items"]["b"] = {"status": "awaiting"}
    now = at(2026, 11, 20, 9)
    assert ops.apply_press(st, {"chat_id": "9", "data": "chaya|ok|a", "text": ""}, "1", now) is None
    assert ops.apply_press(st, {"chat_id": "1", "data": "chaya|ok|a", "text": ""}, "1", now) == ("approve", "a")
    assert st["items"]["a"]["status"] == "approved" and st["items"]["a"]["publish_at"] == "2026-11-20T12:30:00Z"
    assert ops.apply_press(st, {"chat_id": "1", "data": "chaya|ok|a", "text": ""}, "1", now)[0] == "again"
    assert ops.apply_press(st, {"chat_id": "1", "data": "chaya|no|b", "text": ""}, "1", now) == ("hold", "b")
    assert ops.apply_press(st, {"chat_id": "1", "data": "", "text": "make the text bigger"}, "1", now) == ("note", "b")
    assert st["items"]["b"]["note"] == "make the text bigger"
