import numpy as np

from gta6clipper import highlights as hl
from gta6clipper.media import loudness_curve
from gta6clipper.transcribe import Word


def test_loud_bursts_are_found(gameplay):
    loud = loudness_curve(gameplay, 0.5)
    assert abs(loud.size * 0.5 - 180) < 2
    score = hl.score_timeline(loud, 0.5)
    found = hl.find_highlights(score, 0.5, 180, count=2, length=30, min_gap=45)
    peaks = sorted(h.peak for h in found)
    assert 58 <= peaks[0] <= 64 and 138 <= peaks[1] <= 143


def test_window_keeps_inside_video():
    assert hl.window_around(5, 30, 100) == (0.0, 30.0)
    assert hl.window_around(98, 30, 100) == (70.0, 100.0)
    assert hl.window_around(50, 30, 20) == (0.0, 20.0)


def test_peaks_respect_min_gap():
    score = np.zeros(400, dtype=np.float32)
    score[100], score[105], score[300] = 5, 4.9, 3
    peaks = hl.pick_peaks(score, 0.5, 2, min_gap=10)
    assert peaks == [100, 300]


def test_keyword_hits_and_heatmap_boost():
    words = [Word(1, 1.3, "Oh"), Word(1.3, 1.5, "my"), Word(1.5, 1.9, "God!"), Word(50, 50.4, "bro")]
    hits = hl.keyword_hits(words, ["oh my god", "bro", "heist"])
    assert [p for _, p in hits] == ["oh my god", "bro"]
    flat = np.full(200, -30, dtype=np.float32)
    heat = hl.heatmap_curve([{"start_time": 70, "end_time": 75, "value": 1.0}], 200, 0.5)
    peak = hl.pick_peaks(hl.score_timeline(flat, 0.5, heat), 0.5, 1, 10)[0]
    assert 70 <= peak * 0.5 < 75


def test_snap_to_speech_avoids_cutting_words():
    words = [Word(9.8, 10.4, "insane"), Word(39.7, 40.5, "heist")]
    start, end = hl.snap_to_speech(10.0, 40.0, words)
    assert start < 9.8 and end > 40.5
