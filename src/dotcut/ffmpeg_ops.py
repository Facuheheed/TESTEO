from __future__ import annotations

from dataclasses import dataclass
import json
import subprocess
import tempfile
from pathlib import Path

from dotcut.silence import Segment


@dataclass(frozen=True)
class ProbeResult:
    duration: float


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=True)


def probe_duration(input_file: Path) -> ProbeResult:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(input_file),
    ]
    out = run_checked(cmd)
    data = json.loads(out.stdout)
    duration = float(data["format"]["duration"])
    return ProbeResult(duration=duration)


def detect_silence(input_file: Path, *, noise_threshold: str, min_silence: float) -> str:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(input_file),
        "-af",
        f"silencedetect=noise={noise_threshold}:d={min_silence}",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return f"{proc.stdout}\n{proc.stderr}"


def concat_segments(input_file: Path, output_file: Path, segments: list[Segment]) -> None:
    with tempfile.TemporaryDirectory(prefix="dotcut-") as tmp:
        tmp_path = Path(tmp)
        chunk_paths: list[Path] = []

        for idx, seg in enumerate(segments, start=1):
            chunk_path = tmp_path / f"chunk_{idx:04d}.mp4"
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-ss",
                f"{seg.start:.3f}",
                "-to",
                f"{seg.end:.3f}",
                "-i",
                str(input_file),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "20",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(chunk_path),
            ]
            run_checked(cmd)
            chunk_paths.append(chunk_path)

        list_file = tmp_path / "concat.txt"
        lines = [f"file '{p.as_posix()}'" for p in chunk_paths]
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        cmd_concat = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(output_file),
        ]
        run_checked(cmd_concat)
