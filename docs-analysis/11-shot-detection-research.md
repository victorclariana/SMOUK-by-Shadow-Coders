# FASE 11 — Investigación: detección de cambios de plano

> Comparación de alternativas para detectar cortes y transiciones, con evidencia
> de licencia, mantenimiento e integración.

---

## 1. Alternativas comparadas

| Criterio | PySceneDetect | FFmpeg (filtro `select`/`scdet`) | OpenCV (histograma propio) |
|---|---|---|---|
| **Licencia** | BSD-3-Clause | GPL/LGPL (FFmpeg) | Apache-2.0 (OpenCV) |
| **Lenguaje** | Python + OpenCV | C (binario) | C++/Python |
| **Mantenimiento** | Activo (v0.7.1, jul-2026, 5.2k★) | Activo (parte de FFmpeg) | Activo |
| **Detectores** | ContentDetector (cortes), AdaptiveDetector (movimiento rápido, 2 pasadas), ThresholdDetector (fundidos) | `select='gt(scene,0.4)'`, `scdet` | comparación de histogramas (correlación/chi²) manual |
| **Precisión** | frame-accurate; benchmark público | buena, configurable | depende del umbral manual |
| **Transiciones/fundidos** | ThresholdDetector | parcial | manual |
| **API Python** | sí (`detect`, `SceneManager`, `open_video`) | solo subproceso | sí (cv2) |
| **Dependencias** | numpy, OpenCV (av?); ffmpeg/mkvmerge solo para *split* | binario ffmpeg | numpy, OpenCV |
| **Windows** | sí (builds MSI/zip) | sí | sí |
| **Integración con OpenShot** | proceso Python en worker (o biblioteca) | subproceso ffmpeg | en proceso (cv2) |

### 1.1 PySceneDetect (recomendado)

- **Uso como biblioteca:** `from scenedetect import detect, ContentDetector`;
  `detect("video.mp4", ContentDetector())` → lista de escenas con timecodes y
  números de frame. También `SceneManager` + `add_detector` + `detect_scenes`.
- **Uso como proceso separado:** CLI `scenedetect -i video.mp4 detect-content
  list-scenes`. Útil para desacoplar (aislar fallos/dependencias).
- **Determinación:** puede usarse **como biblioteca integrada** (más cómodo para
  exponer progreso y cancelar) y, opcionalmente, **como subproceso** para
  entornos empaquetados. Recomendación: biblioteca integrada dentro de un worker
  (QThread), con la dependencia como opcional.
- **Detectores a usar:** `ContentDetector` (cortes directos) + `AdaptiveDetector`
  (si hay mucho movimiento) y `ThresholdDetector` (fundidos). Configuración de
  sensibilidad por umbral (`threshold`).

### 1.2 FFmpeg

- Filtro `select='gt(scene,0.4)'` o el filtro `scdet` (`scdet:threshold=...`).
- Ya está disponible en OpenShot (FFmpeg es dependencia del motor). No requiere
  nuevas dependencias Python, pero la integración es por subproceso y la
  detección de transiciones es más limitada.

### 1.3 OpenCV (histograma propio)

- Comparar histogramas entre frames consecutivos (correlación, chi-cuadrado,
  Bhattacharyya) con umbral. Total control pero más código propio y calibración.
- Recomendado solo como fallback o para refinamiento.

---

## 2. Compatibilidad con OpenShot (cortes en la timeline)

- Los cortes deben insertarse como **clips separados** en la timeline. Las APIs
  de corte ya existen en OpenShot (`windows/cutting.py`, `views/timeline.py addClip`).
- **Sin pérdida de frames:** al partir, usar números de frame exactos devueltos
  por PySceneDetect (`scene.start.frame_num`, `scene.end.frame_num`) y ajustar
  el inicio/fin del clip (`start`/`end` en JSON del clip).
- **Sincronización de audio:** mantener el audio como pista continua o como clips
  con el mismo corte (OpenShot ya gestiona audio por clip).
- **Frame rate variable:** normalizar a un frame rate de trabajo (el proyecto
  fija `fps`), documentando el mapeo de timecode→frame.
- **Persistencia:** la lista de planos se guarda en la clave `smouk` del
  proyecto; las miniaturas en caché.
- **Corrección:** permitir activar/desactivar cortes, unir y dividir; cada cambio
  es una acción de `UpdateManager` (undo/redo).

---

## 3. Recomendación

- **Adoptar PySceneDetect** (BSD-3-Clause, compatible con GPLv3 de la app) como
  motor de detección, integrado como biblioteca opcional en un worker.
- **Mantener FFmpeg** como alternativa/fallback sin dependencias nuevas.
- **Descartar** implementar detección por histogramas desde cero salvo como
  utilidad auxiliar.
