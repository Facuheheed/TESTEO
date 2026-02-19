# DotCut Studio (MVP)

Primera iteración de un editor de vídeo automatizado enfocado en **recorte inteligente de silencios** y flujo de exportación reproducible.

## Qué incluye esta versión

- Detección de silencios con FFmpeg (`silencedetect`).
- Generación de segmentos hablados con padding configurable.
- Render final concatenado automáticamente.
- Export opcional de metadatos JSON para inspección.
- Pruebas unitarias para la lógica crítica de segmentación.

## Requisitos

- Python 3.11+
- FFmpeg instalado y disponible en `PATH`

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

> Si `pip install -e .[dev]` falla por red/proxy, puedes ejecutar igualmente el proyecto en modo local con `PYTHONPATH=src`.

## Uso rápido

```bash
dotcut input.mp4 output.mp4 \
  --noise-threshold -32dB \
  --min-silence 0.45 \
  --padding 0.18 \
  --min-keep 0.20 \
  --report report.json
```

Esto:
1. detecta silencios,
2. construye segmentos no silenciosos,
3. concatena los segmentos en `output.mp4`.

---

## ¿Cómo lo pruebo? (paso a paso)

### 1) Verifica que FFmpeg existe

```bash
ffmpeg -version
ffprobe -version
```

### 2) Ejecuta los tests unitarios

```bash
PYTHONPATH=src python -m pytest
```

Deberías ver algo como `4 passed`.

### 3) Genera un video de prueba con silencios (sin descargar nada)

```bash
ffmpeg -hide_banner -y \
  -f lavfi -i color=c=black:s=1280x720:d=8 \
  -f lavfi -i "sine=frequency=1000:duration=2" \
  -f lavfi -i "anullsrc=r=48000:cl=stereo:d=2" \
  -f lavfi -i "sine=frequency=700:duration=2" \
  -f lavfi -i "anullsrc=r=48000:cl=stereo:d=2" \
  -filter_complex "[1:a][2:a][3:a][4:a]concat=n=4:v=0:a=1[a]" \
  -map 0:v -map "[a]" -shortest sample_input.mp4
```

Este archivo tiene tono + silencio + tono + silencio, ideal para validar recorte automático.

### 4) Corre DotCut sobre ese video

```bash
PYTHONPATH=src python -m dotcut.cli sample_input.mp4 sample_output.mp4 \
  --noise-threshold -35dB \
  --min-silence 0.30 \
  --padding 0.10 \
  --min-keep 0.15 \
  --report sample_report.json
```

### 5) Comprueba que realmente recortó

```bash
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 sample_input.mp4
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 sample_output.mp4
cat sample_report.json
```

Si todo está bien:
- `sample_output.mp4` debería durar menos que `sample_input.mp4`.
- `sample_report.json` mostrará los silencios detectados y segmentos conservados.

## Notas

- Es un MVP de base para seguir creciendo hacia una app completa (timeline, subtítulos, presets, cola de renders, etc.).
- Si no se detectan silencios, se mantiene el vídeo original completo.
