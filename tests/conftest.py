import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def gameplay(tmp_path_factory) -> Path:
    """3-minute fake 'gameplay': quiet hum with loud bursts at 60s and 140s."""
    out = tmp_path_factory.mktemp("media") / "session.mp4"
    audio = (
        "aevalsrc='0.02*sin(2*PI*220*t)"
        "+if(between(t,60,63),0.9*sin(2*PI*90*t)*random(0),0)"
        "+if(between(t,140,142),0.9*sin(2*PI*120*t)*random(1),0)':s=48000:d=180"
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1280x720:r=30:d=180",
         "-f", "lavfi", "-i", audio, "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac",
         "-shortest", str(out)],
        check=True,
    )
    return out
