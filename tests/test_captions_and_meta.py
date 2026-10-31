from gta6clipper import captions, metadata
from gta6clipper.config import DEFAULTS
from gta6clipper.sources import Source, channel_allowed
from gta6clipper.transcribe import Word


def test_chunks_and_ass_are_clip_relative():
    words = [Word(100.0, 100.3, "no"), Word(100.3, 100.6, "way"), Word(100.6, 101.0, "bro"),
             Word(103.0, 103.5, "{run}")]
    ass = captions.build_ass(words, 99.0, 110.0, 1080, 1920, title="GTA 6: test")
    assert "PlayResY: 1920" in ass
    assert "0:00:01.00" in ass and "NO WAY BRO" in ass
    assert "(RUN)" in ass and "{run}" not in ass  # braces would be parsed as ASS tags
    assert "Title,,0,0,0,,GTA 6: TEST" in ass


def test_permission_matching():
    info = {"channel": "Big Streamer", "channel_id": "UC123", "uploader_id": "@bigstreamer",
            "channel_url": "https://www.youtube.com/@bigstreamer"}
    assert channel_allowed(info, ["@BigStreamer"])
    assert channel_allowed(info, ["UC123"])
    assert channel_allowed(info, ["https://youtube.com/@bigstreamer/"])
    assert channel_allowed(info, ["big streamer"])
    assert not channel_allowed(info, ["someone else"])
    assert not channel_allowed(info, [])


def test_post_text_credits_creators_but_not_self(tmp_path):
    own = Source(path=tmp_path, title="my run", own=True)
    other = Source(path=tmp_path, title="vod", own=False, url="https://x.test/v", channel="Big Streamer")
    assert "Clipped from" not in metadata.short_post(DEFAULTS, "t", own)
    assert "Clipped from Big Streamer - https://x.test/v" in metadata.short_post(DEFAULTS, "t", other)
    text = metadata.longform_post(DEFAULTS, own, [(0, "Moment 1"), (75, "No Way")])
    assert "0:00 Moment 1" in text and "1:15 No Way" in text
