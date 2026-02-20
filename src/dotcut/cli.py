from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotcut.ffmpeg_ops import concat_segments, detect_silence, extract_waveform, probe_duration
from dotcut.pipeline import PipelineProfile, build_analysis_summary, build_candidates_from_segments
from dotcut.silence import build_keep_segments, merge_adjacent, parse_silence_events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dotcut",
        description="Recorta silencios automáticamente y exporta un vídeo continuo.",
    )
    parser.add_argument("input", type=Path, help="Archivo de entrada")
    parser.add_argument("output", type=Path, nargs="?", help="Archivo de salida (opcional con --only-waveform)")
    parser.add_argument("--noise-threshold", default="-32dB", help="Umbral de ruido para silencedetect")
    parser.add_argument("--min-silence", type=float, default=0.45, help="Duración mínima (s) para considerar silencio")
    parser.add_argument("--padding", type=float, default=0.18, help="Padding (s) alrededor de silencios")
    parser.add_argument("--min-keep", type=float, default=0.20, help="Duración mínima de segmento a mantener")
    parser.add_argument("--join-gap", type=float, default=0.08, help="Une segmentos con huecos menores a este valor")
    parser.add_argument("--report", type=Path, help="Ruta opcional para escribir reporte JSON")
    parser.add_argument("--waveform-json", type=Path, help="Exporta forma de onda normalizada para timeline")
    parser.add_argument("--waveform-points", type=int, default=1200, help="Cantidad de puntos de onda a generar")
    parser.add_argument("--waveform-sample-rate", type=int, default=12000, help="Sample rate para extraer onda")
    parser.add_argument("--only-waveform", action="store_true", help="Solo genera waveform JSON y no renderiza video")
    parser.add_argument("--analysis-json", type=Path, help="Escribe un resumen de pipeline y candidatos de clips")
    parser.add_argument("--enable-transcription", action="store_true", help="Marca transcripción como fase activa")
    parser.add_argument("--enable-translation", action="store_true", help="Marca traducción como fase activa")
    parser.add_argument("--enable-scene-candidates", action="store_true", help="Marca análisis de escenas como fase activa")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_file: Path = args.input

    if not input_file.exists():
        raise SystemExit(f"No existe el archivo de entrada: {input_file}")

    probe = probe_duration(input_file)

    waveform_data: list[dict[str, float]] = []
    if args.waveform_json:
        waveform_data = extract_waveform(
            input_file,
            sample_rate=max(1000, args.waveform_sample_rate),
            points=max(50, args.waveform_points),
            duration=probe.duration,
        )
        args.waveform_json.write_text(
            json.dumps(
                {
                    "input": str(input_file),
                    "duration": probe.duration,
                    "points": len(waveform_data),
                    "waveform": waveform_data,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    if args.only_waveform:
        print("✅ Waveform generada.")
        if args.waveform_json:
            print(f"🟣 JSON: {args.waveform_json}")
        return

    if not args.output:
        raise SystemExit("Debes indicar output para render, o usar --only-waveform")

    output_file: Path = args.output
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

    profile = PipelineProfile(
        include_silence_cut=True,
        include_waveform=bool(args.waveform_json),
        include_transcription=args.enable_transcription,
        include_translation=args.enable_translation,
        include_scene_candidates=args.enable_scene_candidates,
    )
    candidates = build_candidates_from_segments(keep, min_duration=1.5)

    if args.analysis_json:
        args.analysis_json.write_text(
            json.dumps(
                {
                    "input": str(input_file),
                    "duration": probe.duration,
                    "profile": build_analysis_summary(profile),
                    "candidates": [
                        {"start": c.start, "end": c.end, "reason": c.reason} for c in candidates
                    ],
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    if args.report:
        report = {
            "input": str(input_file),
            "output": str(output_file),
            "duration": probe.duration,
            "silences": [{"start": s.start, "end": s.end} for s in silences],
            "segments": [{"start": s.start, "end": s.end, "duration": s.duration} for s in keep],
            "waveform_json": str(args.waveform_json) if args.waveform_json else None,
            "analysis_json": str(args.analysis_json) if args.analysis_json else None,
        }
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    total_before = probe.duration
    total_after = sum(seg.duration for seg in keep)
    reduction = max(0.0, total_before - total_after)
    print(f"✅ Export generado: {output_file}")
    print(f"⏱️ Duración original: {total_before:.2f}s")
    print(f"✂️ Duración final: {total_after:.2f}s")
    print(f"📉 Tiempo recortado: {reduction:.2f}s")
    if args.waveform_json:
        print(f"🟣 Waveform JSON: {args.waveform_json}")
    if args.analysis_json:
        print(f"🧠 Analysis JSON: {args.analysis_json}")


if __name__ == "__main__":
    main()
