from __future__ import annotations

from dataclasses import dataclass
import math
import struct
from typing import Iterable


@dataclass(frozen=True)
class WavePoint:
    """Punto de onda normalizado para dibujar en timeline."""

    t: float
    amp: float


def decode_f32le_mono(raw: bytes) -> list[float]:
    """Decodifica audio PCM float32 little-endian mono."""
    if len(raw) % 4 != 0:
        raw = raw[: len(raw) - (len(raw) % 4)]
    if not raw:
        return []
    count = len(raw) // 4
    return list(struct.unpack(f"<{count}f", raw))


def normalize_samples(samples: Iterable[float]) -> list[float]:
    """Normaliza amplitudes a rango 0..1 usando valor absoluto."""
    abs_samples = [abs(s) for s in samples if math.isfinite(s)]
    if not abs_samples:
        return []
    peak = max(abs_samples)
    if peak <= 0:
        return [0.0 for _ in abs_samples]
    return [min(1.0, s / peak) for s in abs_samples]


def bucket_peaks(normalized: list[float], *, bucket_count: int) -> list[float]:
    """Reduce una señal normalizada a picos por bucket para render eficiente."""
    if bucket_count <= 0:
        raise ValueError("bucket_count debe ser > 0")
    if not normalized:
        return [0.0] * bucket_count

    out: list[float] = []
    n = len(normalized)
    for idx in range(bucket_count):
        start = int((idx * n) / bucket_count)
        end = int(((idx + 1) * n) / bucket_count)
        chunk = normalized[start:end]
        out.append(max(chunk) if chunk else 0.0)
    return out


def build_wave_points(peaks: list[float], *, duration: float) -> list[WavePoint]:
    """Convierte picos en puntos (tiempo, amplitud) para timeline."""
    if duration <= 0 or not peaks:
        return []
    step = duration / len(peaks)
    return [WavePoint(t=idx * step, amp=amp) for idx, amp in enumerate(peaks)]
