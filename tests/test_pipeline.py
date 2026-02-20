from dotcut.pipeline import PipelineProfile, build_analysis_summary, build_candidates_from_segments
from dotcut.silence import Segment


def test_build_candidates_from_segments_filters_by_duration() -> None:
    segments = [
        Segment(0.0, 0.8),
        Segment(1.0, 3.0),
        Segment(3.2, 5.4),
    ]
    candidates = build_candidates_from_segments(segments, min_duration=1.5)
    assert len(candidates) == 2
    assert [(c.start, c.end) for c in candidates] == [(1.0, 3.0), (3.2, 5.4)]


def test_build_analysis_summary_maps_profile_flags() -> None:
    profile = PipelineProfile(
        include_silence_cut=True,
        include_waveform=True,
        include_transcription=True,
        include_translation=True,
        include_scene_candidates=True,
    )
    summary = build_analysis_summary(profile)
    assert summary == {
        "silence_cut": True,
        "waveform": True,
        "transcription": True,
        "translation": True,
        "scene_candidates": True,
    }
