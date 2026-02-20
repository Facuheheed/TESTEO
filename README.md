# DotCut Studio (MVP+)

Base de editor de vídeo automatizado orientado a flujo **IA + edición + export**.

## Estado de tus referencias (aplicación real)

Sí: **las apliqué parcialmente en esta base**. Quedó implementado lo que corresponde al núcleo de procesamiento en este repo, y dejé declarado lo que todavía pertenece a fases de producto/web.

| Referencia | Estado en este repo |
|---|---|
| Recorte automático de silencios | ✅ Implementado |
| Onda de audio dinámica para timeline | ✅ Implementado (JSON `[{t, amp}]`) |
| Sugerencia de candidatos de clip | ✅ Implementado (a partir de segmentos de voz) |
| Perfil de pipeline IA (transcripción/traducción/escenas) | ✅ Implementado como flags y contrato de análisis |
| Frontend Next.js + React + timeline visual | ⏳ No en este repo (pendiente fase web) |
| Backend Flask modular completo | ⏳ No en este repo (pendiente fase API/server) |

## Qué incluye esta versión

- Recorte inteligente de silencios con FFmpeg (`silencedetect`).
- Construcción de segmentos útiles con padding y control de micro-cortes.
- Render final concatenado automáticamente.
- Export de reporte JSON con silencios/segmentos.
- Extracción dinámica de onda de audio para timeline (JSON normalizado).
- Resumen de pipeline para automatización por agentes.
- Candidatos de clip derivados de segmentos de voz.

## CLI actual

```bash
PYTHONPATH=src python -m dotcut.cli INPUT.mp4 OUTPUT.mp4 \
  --noise-threshold -32dB \
  --min-silence 0.45 \
  --padding 0.18 \
  --min-keep 0.20 \
  --waveform-json waveform.json \
  --analysis-json analysis.json \
  --enable-transcription \
  --enable-translation \
  --enable-scene-candidates \
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

## ¿Cómo lo pruebo?

### 1) Tests unitarios

```bash
PYTHONPATH=src python -m pytest
```

### 2) Ayuda de CLI

```bash
PYTHONPATH=src python -m dotcut.cli --help
```

### 3) Smoke test completo (si tienes ffmpeg instalado)

```bash
PYTHONPATH=src python -m dotcut.cli sample.mp4 sample_out.mp4 \
  --waveform-json sample_waveform.json \
  --analysis-json sample_analysis.json \
  --enable-transcription \
  --enable-translation \
  --enable-scene-candidates \
  --report sample_report.json
```

## Requisitos

- Python 3.11+
- FFmpeg y FFprobe en `PATH`

## Próximos pasos recomendados

1. Montar backend Flask con endpoint `/media/{id}/analysis` y `/media/{id}/waveform`.
2. Cache multi-resolución de waveform (400 / 1600 / 6400 puntos) para zoom estable.
3. Integrar Whisper/traducción real detrás de los flags del pipeline.
4. Crear frontend Next.js timeline que consuma `waveform.json` + `analysis.json`.
