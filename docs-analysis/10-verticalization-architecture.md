# FASE 10 — Diseño del Dock "Verticalization" y arquitectura modular

> Diseño funcional y técnico (sin implementar) del nuevo dock y de la
> arquitectura de servicios para SMOUK. Las referencias al código de OpenShot
> están verificadas en el árbol local.

---

## 1. Cómo se crean los docks en openshot-qt (verificado)

- `src/windows/main_window.py` importa `QDockWidget` (`línea 52`) y usa:
  - `self.addDockWidget(Qt.RightDockWidgetArea, self.dockAudioRecording)` (`línea 1568`).
  - `self.addDockWidget(target_area, props_dock)` (`línea 1611`).
  - `self.getDocks()` → `self.findChildren(QDockWidget)` (`línea 3120`).
  - `self.removeDocks()` (`línea 3122`).
  - `dock.toggleViewAction().isChecked()` para visibilidad (`línea 1659`).
  - `_add_dock_visibility_actions(...)` (`línea 1661`).
- Los docks de contenido se implementan como **QWidget**, no `QDockWidget`:
  - `src/windows/scope_panel.py` → `WaveformDockContent`, `HistogramDockContent`,
    `VectorscopeDockContent`, `AudioMeterWidget`.
  - `src/windows/audio_recording.py` → `AudioRecordingDockContent`
    (`RECORDING_DOCK_MIN_WIDTH = 320`).
- La **barra de título personalizada** está en `src/classes/title_bar.py`
  (`HiddenTitleBar`).
- El **orden de tabulación** de docks se gestiona en `src/classes/tabstops.py`.
- Las **preferencias persistentes** de un dock usan `_settings()`/`_get()`/`_set()`
  de `scope_panel.py:67-89`, que llama a `get_app().get_settings()`
  (`SettingStore`, `src/classes/settings.py`).
- La **traducción** se hace con `get_app()._tr`/`_()`; `scope_panel.py:62`
  define `N_()` para cadenas diferidas.

### Conclusión

El Dock `Verticalization` debe implementarse como **QWidget de contenido**
(`VerticalizationDockContent`) y ser envuelto en `QDockWidget` por `MainWindow`,
siguiendo el patrón de `AudioRecordingDockContent`/`WaveformDockContent`.

---

## 2. Diseño del Dock "Verticalization"

| Elemento | Ubicación prevista |
|---|---|
| `VerticalizationDockContent(QWidget)` | `src/windows/verticalization.py` |
| Registro en `MainWindow` | `src/windows/main_window.py` (`addDockWidget`, acción de menú) |
| `VERTICALIZATION_DOCK_MIN_WIDTH` | mismo archivo del dock |

### Secciones del dock

1. SOURCE VIDEO · 2. SHOT DETECTION · 3. AUTOMATIC REFRAMING · 4. TITLES ·
5. SUBTITLES · 6. LOGO · 7. POSTER · 8. EXPORT.

### Interacción con el sistema

- **MainWindow:** se conecta a señales existentes (`SeekSignal`, `PlaySignal`,
  `PauseSignal`, `refreshFrameSignal`, `previewFrameSignal`).
- **ProjectDataStore:** no muta el proyecto directamente; produce acciones vía
  `UpdateManager`/`UpdateInterface` (para undo/redo y propagación al motor).
- **Timeline:** cortes/clips vía APIs existentes (`views/timeline.py:5576 addClip`).
- **Visor:** overlay 9:16 dibujado en el widget del visor (no exportado).

---

## 3. Arquitectura modular propuesta (validada contra OpenShot)

| Servicio propuesto | ¿Duplica algo? | Integración |
|---|---|---|
| `VerticalizationDock` | No | `MainWindow` + docks |
| `SourceVideoController` | Parcial (`FilesModel`, `query.File`) | `openshot.FFmpegReader` |
| `ShotDetectionService` | No | PySceneDetect/OpenCV en worker |
| `SceneReviewModel` | No | modelo Qt + `ProjectDataStore` |
| `ReframeAnalysisService` | No | detección de sujetos |
| `SubjectDetectionService` | Parcial (`CVObjectDetection`) | OpenCV/MediaPipe/YOLO |
| `TrackingService` | Parcial (`CVTracker`, sort_filter) | ByteTrack/BoT-SORT |
| `ReframePathGenerator` | No | escribe keyframes `location_x`, `scale_x/y` |
| `OpenShotTimelineAdapter` | **SÍ** (`TimelineSync`, `query.py`) | envolver `TimelineSync` |
| `TitleTemplateService` | Parcial (`title_editor.py`) | SVG de `src/titles/` |
| `SubtitleTranscriptionService` | No | faster-whisper/WhisperX |
| `SubtitleSegmentationService` | No | algoritmo de segmentación |
| `SubtitleImportExportService` | No | SRT ↔ Caption effect |
| `LogoOverlayService` | Parcial (clip imagen) | clip PNG en pista superior |
| `PosterExportService` | No | `Timeline::GetFrame` + `QImage::save` |
| `VerticalExportService` | **SÍ** (`export.py`, presets) | ampliar presets verticales |
| `VerticalPreviewOverlay` | No | overlay en visor |
| `SettingsService` | **SÍ** (`SettingStore`) | ampliar claves |
| `JobManager` | Parcial (`generation_queue.py`) | worker + progreso + cancelación |
| `AnalysisCache` | No | caché en `info.CACHE_PATH` |

### Reglas de diseño

- **Desacoplados (interfaces):** servicios de IA tras una interfaz para poder
  sustituirse y para que la instalación básica funcione sin ellos.
- **Integrados:** `OpenShotTimelineAdapter`, `VerticalExportService`,
  `SettingsService` reutilizan clases existentes.
- **Con tests:** `ReframePathGenerator`, `SubtitleSegmentationService`,
  `OpenShotTimelineAdapter`, `SourceVideoController`, `PosterExportService`.

---

## 4. Modelo de datos propuesto (sin cambiar `.osp`)

Principio: **no modificar el formato `.osp`**; guardar los metadatos de análisis
como una clave nueva **opcional y autodescriptiva** dentro del JSON del proyecto
(p. ej. `smouk` o `verticalization`), de modo que OpenShot estándar la ignore.

| Dato | Dónde se guarda | Regenerable | Se invalida si cambia el vídeo |
|---|---|---|---|
| Vídeo fuente (ruta) | `.osp` (clave `files` existente) | no | — |
| Huella del archivo (hash) | metadatos `smouk` | sí (se recalcula) | es el detonante |
| Detección de planos (timecodes) | metadatos `smouk` | sí | sí |
| Miniaturas de planos | caché (`info.THUMBNAIL_PATH`) | sí | sí |
| Detecciones/tracks/confianza | metadatos `smouk` | sí | sí |
| Sujeto seleccionado | metadatos `smouk` | no (manual) | sí |
| Trayectoria de recorte | keyframes del clip (`location_x`, `scale_x/y`) | sí | sí |
| Correcciones manuales | keyframes + flags en `smouk` | no | solo si se desea |
| Títulos | clips SVG/títulos existentes | sí | no |
| Subtítulos | Caption effect (VTT) | sí | sí |
| Estilos | preferencias globales | no | no |
| Logo | clip imagen + preferencias | no | no |
| Config exportación | presets + preferencias | no | no |
| Rutas | preferencias | no | no |
| Modelo usado + versión + params | metadatos `smouk` | no | sí |
| Estado del proceso / errores | metadatos `smouk` (o caché) | sí | — |
| Caché de análisis | `info.CACHE_PATH`/`PREVIEW_CACHE_PATH` | sí | sí |

- **Preferencias globales:** en `SettingStore` (archivo `openshot.settings`).
- **Por proyecto:** dentro de `.osp` (clave nueva) y archivos auxiliares
  (miniaturas, caché, SRT intermedio) en directorios configurables.
- **Invalidación:** clave única derivada de hash + resolución + fps del vídeo
  fuente; cualquier cambio de vídeo regenera el análisis.

---

## 5. Flujo completo propuesto (clasificado)

| # | Paso | Auto | Confirma | Editable | Cancela | GPU | CPU | Worker |
|---|---|---|---|---|---|---|---|---|
| 1-2 | Abrir SMOUK / dock | — | — | — | — | — | — | — |
| 3-4 | Seleccionar e importar MP4 | ✔ | valida 16:9 | sí | — | — | ✔ | — |
| 5 | Configurar salida vertical | ✔ | — | sí | — | — | — | — |
| 6-7 | Detectar/revisar planos | ✔ | revisar cortes | sí | ✔ | no | ✔ | ✔ |
| 8 | Crear clips editables | ✔ | — | sí | ✔ | — | ✔ | ✔ |
| 9-10 | Analizar planos (sujetos) | ✔ | — | sí | ✔ | opcional | ✔ | ✔ |
| 11 | Generar reencuadre | ✔ | — | sí | ✔ | no | ✔ | ✔ |
| 12 | Crear posiciones/keyframes | ✔ | — | sí | — | — | ✔ | — |
| 13-14 | Revisar/corregir encuadres | — | — | ✔ (manual) | — | — | ✔ | — |
| 15 | Añadir títulos | semiauto | — | ✔ | — | — | ✔ | — |
| 16 | Añadir logotipo | ✔ | — | ✔ | — | — | ✔ | — |
| 17-18 | Transcribir/revisar | ✔ | revisar texto | ✔ | ✔ | opcional | ✔ | ✔ |
| 19-21 | Segmentar/aplicar subtítulos | ✔ | — | ✔ | ✔ | — | ✔ | — |
| 22 | Seleccionar frame | — | — | ✔ | — | — | ✔ | — |
| 23 | Exportar portada PNG | ✔ | — | — | ✔ | no | ✔ | ✔ |
| 24 | Validar | ✔ | — | — | ✔ | — | ✔ | ✔ |
| 25 | Exportar MP4 vertical | ✔ | — | — | ✔ | opcional | ✔ | ✔ |
| 26 | Verificar archivos | ✔ | — | — | — | — | ✔ | — |
| 27 | Abrir directorios | ✔ | — | — | — | — | — | — |

- **GPU:** útil para Whisper grande, YOLO, SAM2, MediaPipe; **CPU** es fallback.
- **Repetibles:** toda detección/transcripción/reencuadre debe poder relanzarse.
- **Invalidables:** todo lo derivado del vídeo fuente se invalida al cambiar éste.

---

## 6. Directorios configurables (ampliación de preferencias)

`SettingStore` (`src/classes/settings.py`) ya persiste preferencias en
`openshot.settings` y soporta claves nuevas. Se añadirán claves `smouk-*`:

| Clave | Finalidad | Defecto |
|---|---|---|
| `smouk-input-dir` | directorio de entrada | último usado |
| `smouk-export-dir` | vídeos exportados | `~/Videos` |
| `smouk-poster-dir` | portadas PNG | subdirectorio del proyecto |
| `smouk-srt-dir` | SRT | subdirectorio del proyecto |
| `smouk-models-dir` | modelos IA | `~/.openshot_qt/models` |
| `smouk-cache-dir` | caché | `info.CACHE_PATH` |
| `smouk-temp-dir` | temporales | `tempfile` |
| `smouk-logs-dir` | logs | `info.USER_PATH` |

Validación de rutas: usar `os.path.normpath`, soportar rutas UNC Windows
(`\\server\share`) y espacios; comprobar permisos de escritura antes de usar
(patrón ya presente en `OpenShotApp.gui()` al probar permisos de `info.USER_PATH`,
`src/classes/app.py:238-259`). Crear directorios con `os.makedirs(exist_ok=True)`.
Limpiar temporales al cerrar (análogo a `cleanup()` de `app.py:341`).

---

## 7. Rendimiento y procesamiento

- **Evitar analizar todos los frames:** muestrear (p. ej. 1 de cada N) para
  detección de sujetos; usar detección de planos que ya es incremental.
- **Proxies:** `src/classes/proxy_service.py` y `info.PROXY_PATH` ya existen;
  reutilizarlos para vídeos largos.
- **Workers:** patrón de `preview_thread.py` (QThread + worker) y de
  `generation_queue.py` (cola con un solo worker, progreso y cancelación).
- **RAM:** liberar frames (`std::shared_ptr<Frame>`), limitar caché.
- **VRAM:** cargar modelos según disponibilidad (CPU si no hay GPU).
- **Lotes:** permitir procesar varios vídeos en cola (`JobManager`).

---

## 8. Clases y archivos que deberán modificarse/crearse (resumen)

- **Crear:** `src/windows/verticalization.py` (dock + widgets), modelos/servicios
  bajo `src/windows/models/` o `src/classes/` (p. ej. `verticalization/`).
- **Modificar (mínimo):** `src/windows/main_window.py` (registrar dock y acción
  de menú), `src/classes/settings.py`/`src/settings/_default.settings`
  (claves `smouk-*`), `src/presets/` (preset vertical), `src/profiles/`
  (perfil 1080×1920 si no existe).
- **No modificar** `libopenshot` ni `libopenshot-audio` salvo necesidad real.

