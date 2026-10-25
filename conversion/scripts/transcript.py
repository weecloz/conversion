import re
from dataclasses import dataclass

LINE = re.compile(r"^\[(\d{1,3}):(\d{2})(?::(\d{2}))?\]\s*([^:\[\]]+?)\s*:\s*(.*)$")


@dataclass
class Line:
    t: str | None
    seconds: int | None
    speaker: str
    text: str


def parse(text: str) -> list[Line]:
    out: list[Line] = []
    for raw in text.splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        a, b, c, speaker, body = m.groups()
        if c is None:  # [mm:ss]
            secs, t = int(a) * 60 + int(b), f"{a}:{b}"
        else:  # [h:mm:ss]
            secs, t = int(a) * 3600 + int(b) * 60 + int(c), f"{a}:{b}:{c}"
        out.append(Line(t, secs, speaker.strip(), body.strip()))
    return out
