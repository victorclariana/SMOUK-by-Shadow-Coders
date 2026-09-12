# FASE 13 — Investigación: subtítulos automáticos en catalán

> Evaluación de motores de transcripción y del soporte real de OpenShot para
> captions, más un algoritmo conceptual de segmentación por pantallas.

---

## 1. Soporte real de OpenShot para subtítulos (verificado)

- **Existe el efecto `Caption`** en C++: `libopenshot/src/effects/Caption.h/.cpp`,
  `class Caption : public EffectBase` (`Caption.h:38`).
- El constructor acepta **datos VTT/Subrip**: `Caption(std::string captions)`
  (`Caption.h:76-79`), y hay getter/setter `CaptionText()`.
- Propiedades de estilo completas: `color`, `stroke`, `background`,
  `background_alpha`, `background_corner`, `background_padding`, `stroke_width`,
  `font_size`, `font_alpha`, `line_spacing`, `left/top/right/bottom`, `fade_in`,
  `fade_out`, `font_name` (`Caption.h:55-71`).
- Registrado en `EffectInfo` (`EffectInfo.cpp:47,176`) como efecto "Caption".
- **Conclusión:** OpenShot **ya soporta subtítulos burn-in** mediante el efecto
  `Caption` que consume SRT/VTT directamente, con estilos y fondos. No hace falta
  escribir un renderizador nuevo: basta **generar SRT y aplicarlo como efecto
  Caption** (o, para edición por bloques, crear un clip/título por pantalla).

---

## 2. Motores de transcripción (catalán)

| Motor | Licencia | Backend | Timestamps por palabra | VAD | CPU | GPU | Offline |
|---|---|---|---|---|---|---|---|
| openai/whisper | MIT | PyTorch | sí | no | lento | ✔ | sí |
| faster-whisper | MIT | CTranslate2 | sí | sí | rápido (8-bit) | ✔ | sí |
| WhisperX | BSD-2 | faster-whisper + wav2vec2 | sí (alineación) | sí (pyannote/silero) | ✔ | ✔ (pide GPU) | sí |
| whisper.cpp | MIT | C++ (ggml) | parcial | sí | rápido | ✔ (opcional) | sí |

- **faster-whisper** es la opción recomendada como base: MIT, 4× más rápido que
  Whisper, cuantización 8-bit en CPU/GPU, timestamps por palabra y VAD, funciona
  offline, y hay apps Windows construidas sobre él.
- **WhisperX** aporta **alineación forzada** (wav2vec2) para timestamps de palabra
  más precisos, pero añade complejidad y `pyannote` (modelos CC-BY-4.0 con
  restricción de uso no comercial en algunos). Recomendado solo si se necesita
  alineación fina.
- **Diarización (pyannote):** no necesaria para SMOUK (subtítulos de un solo
  hablante); **descartar** salvo requisito futuro.

---

## 3. Modelos Whisper para catalán

| Modelo | Licencia | Base | WER 3CatParla (test) | WER Common Voice (acentos) | Punctuación |
|---|---|---|---|---|---|
| `projecte-aina/whisper-large-v3-ca-3catparla` | Apache-2.0 | large-v3 | 0.96 | ~8-12 | parcial |
| `BSC-LT/whisper-bsc-large-v3-cat` | Apache-2.0 | large-v3 | 4.80 | ~3-5 | parcial |
| `BSC-LT/faster-whisper-large-v3-ca-punctuated-3370h` | Apache-2.0 | large-v3 | — | — | sí |
| `openai/whisper-large-v3` (language=ca) | MIT | — | referencia | — | sí (multi-idioma) |

- **Mejor precisión catalán:** `BSC-LT/whisper-bsc-large-v3-cat` (~3.09 GB en
  F16, Apache-2.0). Los modelos especializados en catalán suelen **perder
  puntuación/mayúsculas**.
- **Estrategia adoptada en 0.0.28:** usar directamente el modelo CTranslate2
  `BSC-LT/faster-whisper-large-v3-ca-punctuated-3370h`, ajustado para catalán y
  con puntuación. Evita convertir el modelo y evita una segunda red neuronal
  dedicada únicamente a restaurar signos.
- **Conversión:** los modelos transformers deben convertirse a CTranslate2 para
  faster-whisper (`ct2-transformers-converter`), o usarse vía `transformers`.

---

## 4. Pipeline propuesto

```
audio → faster-whisper (modelo catalán) → JSON detallado (segmentos + palabras)
      → restauración de puntuación/mayúsculas
      → SubtitleSegmentationService (pantallas) → SRT
      → aplicar efecto Caption (VTT) o clips de texto en pista superior
      → exportar/importar SRT
```

- **SRT intermedio opcional** para importar/exportar y corregir.
- **Regenerable:** la transcripción puede relanzarse; el SRT corregido manualmente
  debe poder importarse sin perder ediciones.

---

## 5. Algoritmo conceptual de segmentación por pantallas

Valores **iniciales configurables** (no definitivos; calibrar con pruebas):

| Parámetro | Valor inicial propuesto |
|---|---|
| Máximo de líneas | 2 |
| Caracteres por línea (orientativo) | ~40-42 |
| Duración mínima | 1.0 s |
| Duración máxima | 6.0 s |
| Velocidad de lectura | ~15-17 caracteres/s (catalán) |
| Márgenes de seguridad | respetar pausas > 0.4 s y cambios de plano |

Reglas de segmentación:

1. Partir de timestamps por palabra y pausas de audio (VAD).
2. Agrupar palabras respetando **unidades sintácticas** y signos de puntuación
   (no cortar frases).
3. No exceder 2 líneas ni la duración máxima; no crear subtítulos < 1 s.
4. Insertar salto de línea en límites sintácticos o conjunciones.
5. Evitar solapamiento; dejar un pequeño margen entre bloques consecutivos.
6. Opcionalmente alinear a cambios de plano (no romper un subtítulo en un corte).

---

## 6. Recomendación

- **Adoptado:** `faster-whisper` (MIT) con el modelo catalán puntuado
  **BSC-LT/faster-whisper-large-v3-ca-punctuated-3370h** (Apache-2.0), ya
  convertido a CTranslate2 y ejecutado en un worker aislado con CPU INT8.
- **Perfil CPU desde 0.0.29:** hasta 10 hilos, reservando dos procesadores
  lógicos para la interfaz, y `beam_size=1`. Se mantienen VAD y timestamps por
  palabra; el objetivo es evitar el cuello de botella observado con los cuatro
  hilos predeterminados y cinco hipótesis por segmento.
- **WhisperX** solo si se requiere alineación fina; evitar pyannote (diarización).
- **Integrar** subtítulos con el efecto `Caption` (VTT) ya existente.
- **No** depender de servicios cloud; todo local tras descargar el modelo.
