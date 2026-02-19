from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotcut.ffmpeg_ops import concat_segments, detect_silence, probe_duration
from dotcut.silence import build_keep_segments, merge_adjacent, parse_silence_events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dotcut",
        description="Recorta silencios automáticamente y exporta un vídeo continuo.",
    )
    parser.add_argument("input", type=Path, help="Archivo de entrada")
    parser.add_argument("output", type=Path, help="Archivo de salida")
    parser.add_argument("--noise-threshold", default="-32dB", help="Umbral de ruido para silencedetect")
    parser.add_argument("--min-silence", type=float, default=0.45, help="Duración mínima (s) para considerar silencio")
    parser.add_argument("--padding", type=float, default=0.18, help="Padding (s) alrededor de silencios")
    parser.add_argument("--min-keep", type=float, default=0.20, help="Duración mínima de segmento a mantener")
    parser.add_argument("--join-gap", type=float, default=0.08, help="Une segmentos con huecos menores a este valor")
    parser.add_argument("--report", type=Path, help="Ruta opcional para escribir reporte JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_file: Path = args.input
    output_file: Path = args.output

    if not input_file.exists():
        raise SystemExit(f"No existe el archivo de entrada: {input_file}")

    probe = probe_duration(input_file)
    ffmpeg_log = detect_silence(
        input_file,
        noise_threshold=args.noise_threshold,
        min_silence=args.min_silence,
    )

    silences = parse_silence_events(ffmpeg_log)
    keep = build_keep_segments(
        silences,
        probe.duration,
        padding=max(0.0, args.padding),
        min_keep=max(0.0, args.min_keep),
    )
    keep = merge_adjacent(keep, join_gap_below=max(0.0, args.join_gap))

    concat_segments(input_file, output_file, keep)

    if args.report:
        report = {
            "input": str(input_file),
            "output": str(output_file),
            "duration": probe.duration,
            "silences": [{"start": s.start, "end": s.end} for s in silences],
            "segments": [{"start": s.start, "end": s.end, "duration": s.duration} for s in keep],
        }
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    total_before = probe.duration
    total_after = sum(seg.duration for seg in keep)
    reduction = max(0.0, total_before - total_after)
    print(f"✅ Export generado: {output_file}")
    print(f"⏱️ Duración original: {total_before:.2f}s")
    print(f"✂️ Duración final: {total_after:.2f}s")
    print(f"📉 Tiempo recortado: {reduction:.2f}s")


if __name__ == "__main__":
    main()
