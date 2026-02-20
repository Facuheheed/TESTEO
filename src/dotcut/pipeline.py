from __future__ import annotations

from dataclasses import dataclass

from dotcut.silence import Segment


@dataclass(frozen=True)
class PipelineProfile:
    """Configura qué análisis se desean en una corrida."""

    include_silence_cut: bool = True
    include_waveform: bool = True
    include_transcription: bool = False
    include_translation: bool = False
    include_scene_candidates: bool = False


@dataclass(frozen=True)
class ClipCandidate:
    """Candidato de clip sugerido para edición asistida."""

    start: float
    end: float
    reason: str


def segment_to_candidate(segment: Segment, *, min_duration: float = 1.5) -> ClipCandidate | None:
    """Convierte un segmento útil en candidato de clip si supera una duración mínima."""
    if segment.duration < min_duration:
        return None
    return ClipCandidate(
        start=segment.start,
        end=segment.end,
        reason="speech_segment",
    )


def build_candidates_from_segments(segments: list[Segment], *, min_duration: float = 1.5) -> list[ClipCandidate]:
    out: list[ClipCandidate] = []
    for seg in segments:
        candidate = segment_to_candidate(seg, min_duration=min_duration)
        if candidate is not None:
            out.append(candidate)
    return out


def build_analysis_summary(profile: PipelineProfile) -> dict[str, bool]:
    """Estado declarativo de módulos para uso por UI/API de agentes."""
    return {
        "silence_cut": profile.include_silence_cut,
        "waveform": profile.include_waveform,
        "transcription": profile.include_transcription,
        "translation": profile.include_translation,
        "scene_candidates": profile.include_scene_candidates,
    }
