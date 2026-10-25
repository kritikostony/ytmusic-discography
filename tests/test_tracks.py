from ytmusic_discography.tracks import ATV, OMV, find_audio, plan, titles_match


class FakeYT:
    def __init__(self, results):
        self.results = results
        self.queries = []

    def search(self, query, filter=None, limit=None):
        self.queries.append((query, filter))
        return self.results


def noop():
    pass


def test_titles_match():
    assert titles_match("Eipes", "Eipes")
    assert titles_match("Oneiro Tha 'Nai Ksana (Kounia) (00s Version)", "Oneiro Tha 'Nai Ksana (Kounia)")
    assert not titles_match("Eipes Kati", "Eipe")
    assert not titles_match("Eipes", "")


def test_find_audio_requires_atv_title_and_duration():
    track = {"title": "Katamata", "duration_seconds": 281}
    yt = FakeYT([
        {"videoId": "live", "videoType": ATV, "title": "Katamata", "duration_seconds": 237},
        {"videoId": "omv", "videoType": OMV, "title": "Katamata", "duration_seconds": 281},
        {"videoId": "other", "videoType": ATV, "title": "Allo", "duration_seconds": 281},
        {"videoId": "ok", "videoType": ATV, "title": "Katamata", "duration_seconds": 282},
    ])
    assert find_audio(yt, "Thodoris Ferris", track, noop)["videoId"] == "ok"
    assert yt.queries == [("Thodoris Ferris Katamata", "songs")]


def test_plan_statuses():
    album = {"tracks": [
        {"trackNumber": 1, "title": "A", "videoId": "a", "videoType": ATV, "duration_seconds": 100},
        {"trackNumber": 2, "title": "B", "videoId": "b", "videoType": OMV, "duration_seconds": 200},
        {"trackNumber": 3, "title": "C", "videoId": "c", "videoType": OMV, "duration_seconds": 300},
        {"trackNumber": 4, "title": "D", "videoId": None, "isAvailable": False},
    ]}
    yt = FakeYT([{"videoId": "b-audio", "videoType": ATV, "title": "B", "duration_seconds": 200}])
    p = plan(yt, album, "X", noop)
    assert [(t.status, t.video_id) for t in p] == [
        ("audio", "a"), ("replaced", "b-audio"), ("skipped", None), ("skipped", None)]
