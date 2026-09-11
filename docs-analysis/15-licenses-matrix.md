# FASE 15 — Matriz de licencias

> Revisión de licencias (código, modelos, pesos, datos). **No es asesoramiento
> jurídico.** Se indican los elementos que requieren revisión legal antes de
> distribuir SMOUK.

---

## 1. Licencias de OpenShot (base del proyecto)

| Componente | Licencia | Nota |
|---|---|---|
| openshot-qt | GPL-3.0-or-later | `src/classes/info.py:36` `GPL_VERSION = "3"` |
| libopenshot | LGPL-3.0-or-later | `CMakeLists.txt:9`, `README.md` |
| libopenshot-audio | GPL-3.0-or-later | `CMakeLists.txt:13-24` |
| JUCE (vendored) | GPL/comercial (dual) | coherente con GPL-3.0 |
| jsoncpp (vendored) | MIT/Public Domain | `thirdparty/jsoncpp/` |

---

## 2. Dependencias candidatas

| Dependencia | Licencia código | Modelo/pesos | Comercial | Riesgo |
|---|---|---|---|---|
| PySceneDetect | BSD-3-Clause | — | sí | bajo |
| OpenCV | Apache-2.0 | — | sí | bajo |
| FFmpeg | GPL/LGPL (según build) | — | depende de códecs | medio (códecs GPL) |
| MediaPipe | Apache-2.0 | — | sí | bajo (envía métricas) |
| Ultralytics | AGPL-3.0 / Enterprise | pesos AGPL/comercial | requiere Enterprise | **alto** |
| InsightFace | código MIT | **modelos no comerciales** | no (modelos) | **alto** |
| ByteTrack | MIT | — | sí | bajo |
| BoT-SORT | MIT | — | sí | bajo |
| UNISAL | MIT (código) | pesos propios | verificar | medio |
| SAM / SAM 2 | Apache-2.0 (código) | pesos Apache | sí | bajo-medio |
| faster-whisper | MIT | — | sí | bajo |
| openai/whisper | MIT | pesos MIT | sí | bajo |
| WhisperX | BSD-2-Clause | — | sí | bajo |
| pyannote | MIT (código) | **modelos CC-BY-4.0 (no comercial)** | no | **alto** (si diarización) |
| ffmpeg-python | Apache-2.0 | — | sí | bajo |

---

## 3. Modelos Whisper catalán

| Modelo | Licencia modelo/pesos | Comercial |
|---|---|---|
| projecte-aina/whisper-large-v3-ca-3catparla | Apache-2.0 | sí |
| BSC-LT/whisper-bsc-large-v3-cat | Apache-2.0 | sí |
| openai/whisper-large-v3 | MIT (pesos) | sí |

---

## 4. Distinciones importantes

- **Licencia del código ≠ licencia de los pesos ≠ licencia de los datos.**
- **AGPL (Ultralytics):** obliga a publicar el código fuente si se distribuye
  la obra; uso comercial interno puede requerir licencia Enterprise.
- **Modelos no comerciales (InsightFace, pyannote):** no pueden redistribuirse ni
  usarse comercialmente sin licencia adicional.
- **Códecs FFmpeg:** builds con libx264/otros pueden implicar términos GPL;
  verificar la build concreta distribuida.
- **Atribución:** varias licencias (Apache, CC-BY, BSD) exigen avisos de
  atribución.

---

## 5. Elementos que requieren revisión legal antes de distribuir SMOUK

1. Ultralytics (si se usa) — decisión AGPL vs Enterprise.
2. InsightFace — modelos no comerciales.
3. pyannote — modelos CC-BY-4.0 (no comercial) si se añade diarización.
4. Pesos YOLO concretos (fuente y licencia).
5. Build de FFmpeg distribuida (códecs y términos).
6. Modelos de Hugging Face descargados (verificar licencia de pesos y datos de
   entrenamiento de cada uno).
7. Política de redistribución de los modelos descargados en el instalador de SMOUK.

**Estrategia recomendada:** priorizar componentes **MIT/BSD/Apache-2.0** y
modelos con pesos **Apache-2.0/MIT**, evitar AGPL (Ultralytics) y modelos no
comerciales en la distribución, y mantener las dependencias de IA **opcionales**
para no acoplar SMOUK a términos restrictivos.
