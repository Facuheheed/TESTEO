import struct

from dotcut.waveform import bucket_peaks, build_wave_points, decode_f32le_mono, normalize_samples


def test_decode_f32le_mono() -> None:
    raw = struct.pack("<4f", 0.0, -0.5, 0.25, 1.0)
    out = decode_f32le_mono(raw)
    assert out == [0.0, -0.5, 0.25, 1.0]


def test_normalize_samples_abs_range_0_1() -> None:
    normalized = normalize_samples([0.0, -2.0, 1.0, 2.0])
    assert normalized == [0.0, 1.0, 0.5, 1.0]


def test_bucket_peaks_returns_fixed_size() -> None:
    peaks = bucket_peaks([0.1, 0.9, 0.3, 0.6, 0.2], bucket_count=3)
    assert len(peaks) == 3
    assert peaks[0] >= 0 and peaks[0] <= 1


def test_build_wave_points_time_distribution() -> None:
    points = build_wave_points([0.2, 0.8, 0.4], duration=6.0)
    assert [round(p.t, 2) for p in points] == [0.0, 2.0, 4.0]
    assert [p.amp for p in points] == [0.2, 0.8, 0.4]
