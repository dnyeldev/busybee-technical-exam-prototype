import copy
import json

from gta6clipper.config import DEFAULTS
from gta6clipper.media import probe
from gta6clipper.pipeline import Pipeline
from gta6clipper.transcribe import Word


class FakeTranscriber:
    def words(self, media, start=0.0, end=None):
        return [Word(start + 4, start + 4.4, "no"), Word(start + 4.4, start + 4.8, "way")]


def test_end_to_end(gameplay, tmp_path):
    cfg = copy.deepcopy(DEFAULTS)
    cfg["output_dir"] = str(tmp_path / "clips")
    cfg["shorts"]["count"] = 2
    cfg["longform"]["count"] = 3
    cfg["longform"]["clip_seconds"] = 20
    cfg["render"]["loudnorm"] = False
    pipe = Pipeline(cfg, log=lambda *_: None)
    pipe._transcriber = FakeTranscriber()

    out = pipe.run(str(gameplay))

    summary = json.loads((out / "summary.json").read_text())
    assert len(summary["shorts"]) == 2
    for short in summary["shorts"]:
        info = probe(out / short["file"])
        assert (info["width"], info["height"]) == (1080, 1920)
        assert 25 <= info["duration"] <= 35
        assert (out / short["file"].replace(".mp4", ".txt")).exists()
    comp = probe(out / "compilation.mp4")
    assert (comp["width"], comp["height"]) == (1920, 1080)
    assert 55 <= comp["duration"] <= 65
    assert "Chapters:" in (out / "compilation.txt").read_text()
    assert not (out / "longform_parts").exists()
