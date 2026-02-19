from dotcut.silence import SilenceRange, build_keep_segments, merge_adjacent, parse_silence_events


def test_parse_silence_events_pairs_start_end() -> None:
    log = """
[silencedetect @ 0x1] silence_start: 1.20
[silencedetect @ 0x1] silence_end: 2.00 | silence_duration: 0.80
[silencedetect @ 0x1] silence_start: 3.50
[silencedetect @ 0x1] silence_end: 4.10 | silence_duration: 0.60
"""
    silences = parse_silence_events(log)
    assert silences == [SilenceRange(1.2, 2.0), SilenceRange(3.5, 4.1)]


def test_build_keep_segments_applies_padding_and_min_keep() -> None:
    silences = [SilenceRange(1.0, 2.0), SilenceRange(4.0, 4.4)]
    segments = build_keep_segments(silences, 6.0, padding=0.1, min_keep=0.2)
    assert [(round(s.start, 2), round(s.end, 2)) for s in segments] == [
        (0.0, 0.9),
        (2.1, 3.9),
        (4.5, 6.0),
    ]


def test_build_keep_segments_fallback_to_full_duration() -> None:
    silences = [SilenceRange(0.0, 4.0)]
    segments = build_keep_segments(silences, 4.0, padding=0.0, min_keep=10.0)
    assert len(segments) == 1
    assert segments[0].start == 0.0
    assert segments[0].end == 4.0


def test_merge_adjacent_joins_small_gaps() -> None:
    segments = build_keep_segments([], 5.0, padding=0.0, min_keep=0.0)
    merged = merge_adjacent(segments, join_gap_below=0.1)
    assert len(merged) == 1
    assert merged[0].start == 0.0
    assert merged[0].end == 5.0
