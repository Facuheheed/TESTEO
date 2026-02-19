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

## Notas

- Es un MVP de base para seguir creciendo hacia una app completa (timeline, subtítulos, presets, cola de renders, etc.).
- Si no se detectan silencios, se mantiene el vídeo original completo.
