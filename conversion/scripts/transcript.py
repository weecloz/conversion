"""Lecture des transcriptions « [mm:ss] Nom: texte » (ou « 00:03 Nom: texte »)."""
from __future__ import annotations

import re
from dataclasses import dataclass

LINE = re.compile(r"^\[?(\d{1,3}):(\d{2})(?::(\d{2}))?\]?\s*([^:\[\]]+?)\s*:\s*(.*)$")


@dataclass
class Line:
    t: str | None
    seconds: int | None
    speaker: str
    text: str


def parse(text: str) -> list[Line]:
    """Une réplique par ligne horodatée. Une ligne qui suit sans horodatage (réplique sur plusieurs
    lignes) est ajoutée à la réplique précédente ; une ligne vide termine la réplique."""
    out: list[Line] = []
    continuation = False
    for raw in text.splitlines():
        s = raw.strip()
        m = LINE.match(s)
        if m:
            a, b, c, speaker, body = m.groups()
            if c is None:  # [mm:ss]
                secs, t = int(a) * 60 + int(b), f"{a}:{b}"
            else:  # [h:mm:ss]
                secs, t = int(a) * 3600 + int(b) * 60 + int(c), f"{a}:{b}:{c}"
            out.append(Line(t, secs, speaker.strip(), body.strip()))
            continuation = True
        elif not s:
            continuation = False
        elif continuation and out:
            out[-1].text = (out[-1].text + " " + s).strip()
    return out
