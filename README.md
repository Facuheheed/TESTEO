# DotCut Studio (MVP+)

Base de editor de vídeo automatizado orientado a flujo **IA + edición + export**.

## Qué incluye esta versión

- Recorte inteligente de silencios con FFmpeg (`silencedetect`).
- Construcción de segmentos útiles con padding y control de micro-cortes.
- Render final concatenado automáticamente.
- Export de reporte JSON con silencios/segmentos.
- **Extracción dinámica de onda de audio** para timeline (JSON normalizado).
- Pruebas unitarias de segmentación y waveform.

## Dirección de producto (alineado a tu visión)

- Editor web moderno (UI cuidada, timeline detallado, interacción natural).
- Pipeline híbrido:
  - ingestión media,
  - análisis audio (silencios + waveform),
  - transcripción/traducción,
  - edición asistida por IA,
  - export en cola.
- API pensada para agentes (automatización por lenguaje natural sobre herramientas del editor).

## CLI actual

```bash
PYTHONPATH=src python -m dotcut.cli INPUT.mp4 OUTPUT.mp4 \
  --noise-threshold -32dB \
  --min-silence 0.45 \
  --padding 0.18 \
  --min-keep 0.20 \
  --report report.json
```

### Extraer solo waveform (sin render)

```bash
PYTHONPATH=src python -m dotcut.cli INPUT.mp4 \
  --only-waveform \
  --waveform-json waveform.json \
  --waveform-points 1600 \
  --waveform-sample-rate 12000
```

El `waveform.json` contiene `[{t, amp}]` para dibujar onda en timeline estable a cualquier zoom.

---

## ¿Cómo lo pruebo?

### 1) Tests unitarios

```bash
PYTHONPATH=src python -m pytest
```

### 2) Ayuda de CLI

```bash
PYTHONPATH=src python -m dotcut.cli --help
```

### 3) Smoke test de waveform (requiere ffmpeg instalado)

```bash
PYTHONPATH=src python -m dotcut.cli sample.mp4 \
  --only-waveform \
  --waveform-json sample_waveform.json
```

## Requisitos

- Python 3.11+
- FFmpeg y FFprobe en `PATH`

## Próximos pasos recomendados

1. Endpoint backend `/media/{id}/waveform` para precomputar y cachear onda.
2. Cache multi-resolución (ej: 400 / 1600 / 6400 puntos) para zoom fluido.
3. Subtítulos automáticos + corte por transcripción.
4. Cola de renders/export y auditoría por job.
