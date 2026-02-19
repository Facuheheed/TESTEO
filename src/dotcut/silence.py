from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

START_RE = re.compile(r"silence_start:\s*([\d.]+)")
END_RE = re.compile(r"silence_end:\s*([\d.]+)")


@dataclass(frozen=True)
class SilenceRange:
    start: float
    end: float


@dataclass(frozen=True)
class Segment:
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


def parse_silence_events(stderr_text: str) -> list[SilenceRange]:
    """Parsea stderr de FFmpeg con silencedetect en rangos de silencio."""
    starts: list[float] = []
    silences: list[SilenceRange] = []

    for line in stderr_text.splitlines():
        start_match = START_RE.search(line)
        if start_match:
            starts.append(float(start_match.group(1)))
            continue

        end_match = END_RE.search(line)
        if end_match and starts:
            start = starts.pop(0)
            end = float(end_match.group(1))
            if end > start:
                silences.append(SilenceRange(start=start, end=end))

    return silences


def build_keep_segments(
    silences: Iterable[SilenceRange],
    media_duration: float,
    *,
    padding: float,
    min_keep: float,
) -> list[Segment]:
    """Construye segmentos a conservar (no silenciosos) con padding."""
    safe_duration = max(0.0, media_duration)
    if safe_duration == 0:
        return []

    sorted_silences = sorted(silences, key=lambda x: x.start)
    keep: list[Segment] = []
    cursor = 0.0

    for silence in sorted_silences:
        silent_start = max(0.0, silence.start - padding)
        silent_end = min(safe_duration, silence.end + padding)

        if silent_start > cursor:
            seg = Segment(start=cursor, end=silent_start)
            if seg.duration >= min_keep:
                keep.append(seg)

        cursor = max(cursor, silent_end)

    if cursor < safe_duration:
        tail = Segment(start=cursor, end=safe_duration)
        if tail.duration >= min_keep:
            keep.append(tail)

    if not keep:
        return [Segment(0.0, safe_duration)]

    return keep


def merge_adjacent(segments: Iterable[Segment], *, join_gap_below: float = 0.08) -> list[Segment]:
    """Une segmentos casi contiguos para evitar micro-cortes molestos."""
    ordered = sorted(segments, key=lambda s: s.start)
    if not ordered:
        return []

    merged: list[Segment] = [ordered[0]]
    for seg in ordered[1:]:
        last = merged[-1]
        gap = seg.start - last.end
        if gap <= join_gap_below:
            merged[-1] = Segment(last.start, max(last.end, seg.end))
        else:
            merged.append(seg)

    return merged
