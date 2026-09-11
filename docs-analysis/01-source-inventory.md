# FASE 2 — Inventario completo del código fuente

> Inventario de la estructura de cada repositorio. Se excluyeron de los
> recuentos volumétricos: `.git`, `build`, `dist`, `__pycache__`,
> `.pytest_cache`, `.mypy_cache`, entornos virtuales, binarios, objetos
> compilados, cachés, logs y paquetes de distribución.
>
> El código de terceros **sí** se identifica (no se ignora).

---

## 1. openshot-qt (aplicación / interfaz)

**Ruta:** `D:\SMOUK by Shadow Coders\openshot-qt`

### 1.1 Directorios principales (nivel raíz)

| Directorio | Contenido / función |
|---|---|
| `src/` | Código fuente principal de la aplicación (Python + recursos). |
| `doc/` | Documentación de usuario y desarrollador en Sphinx (`*.rst`). |
| `images/` | Iconos, cursores, logotipos y `openshot.qrc`. |
| `installer/` | Empaquetado e instaladores (Inno Setup `.iss`, MSIX, scripts). |
| `xdg/` | Archivos de integración de escritorio Linux (`.desktop`, etc.). |
| `.github/` | Plantillas de issues y workflows de CI. |

### 1.2 Archivos de entrada

- `src/launch.py` — punto de entrada de la aplicación.
- `src/__init__.py` — paquete raíz `openshot_qt`.
- `src/qt_api.py` — capa de abstracción de Qt (selección de PySide6/PyQt5).
- `setup.py` — empaquetado Python (punto de instalación).
- `freeze.py` — script de congelado/empaquetado (PyInstaller).
- `MANIFEST.in` — contenido del paquete sdist.

### 1.3 Código fuente Python (`src/`)

| Subdirectorio | Función |
|---|---|
| `src/classes/` | Lógica de negocio: app, timeline, project_data, settings, logger, etc. |
| `src/windows/` | Ventanas y diálogos (`main_window.py`, `export.py`, `preferences.py`, etc.). |
| `src/windows/models/` | Modelos Qt (files_model, properties_model, effects_model, ...). |
| `src/windows/views/` | Vistas Qt (files_treeview, timeline, properties_tableview, ...). |
| `src/windows/views/timeline_backend/` | Backend de renderizado de la timeline (geometry, paint, qwidget). |
| `src/settings/` | Plantillas por defecto (`_default.project`, `_default.settings`). |
| `src/tests/` | Tests de interfaz (pytest; 42 archivos `test_*.py`). |
| `src/effects/` | Definiciones de efectos (iconos + datos). |
| `src/transitions/` | Definiciones de transiciones (`common/`, `extra/`). |
| `src/titles/` | Plantillas de títulos. |
| `src/profiles/` | Perfiles de exportación (`definitions/`, `legacy/`). |
| `src/presets/` | Presets de exportación. |
| `src/blender/` | Plantillas y scripts de Blender (títulos 3D). |
| `src/colors/` | Presets de etalonaje por categorías. |
| `src/emojis/` | Emojis y datos (`color/svg`, `data`). |
| `src/comfyui/` | Integración con ComfyUI (generación por IA). |
| `src/language/` | Traducciones (`*.qm`, `*.po`, `*.pot`, `*.qrc`). |
| `src/themes/` | Temas (`cosmic/`, `humanity/`). |
| `src/resources/` | Datos estáticos JSON (contributors, modelos de IA, plantillas). |
| `src/images/` | Recursos de imagen (`cache/`, `fonts/`). |

### 1.4 Clases/lógica clave en `src/classes/`

Archivos representativos: `app.py`, `timeline.py`, `project_data.py`,
`settings.py`, `logger.py`, `logger_libopenshot.py`, `version.py`, `info.py`,
`query.py`, `json_data.py`, `waveform.py`, `thumbnail.py`, `conversion.py`,
`clip_utils.py`, `keyframe_scaler.py`, `proxy_service.py`, `metrics.py`,
`sentry.py`, `updates.py`, `comfy_client.py`, `generation_service.py`, etc.

### 1.5 Recursos gráficos y estilos

- `images/openshot.qrc` — recurso Qt principal (iconos, logotipos, cursores).
- `images/actions/`, `images/Humanity/` — iconos de acciones.
- `src/images/` — SVG de miniaturas, cursores, fondos, máscaras.
- `src/themes/cosmic/`, `src/themes/humanity/` — temas con hojas de estilo
  (2 archivos `.css`) e iconos.
- Cursores y SVG de aceleración por hardware (`hw-accel-*.svg`).

### 1.6 Traducciones

- `src/language/` — 107 archivos `.qm` compilados (un idioma por archivo).
- `src/language/OpenShot/` — 4 plantillas `.pot` (OpenShot, blender, emojis, transitions).
- Archivos `.po` (675) — fuentes de traducción por idioma.
- `src/language/openshot_lang.qrc` y `openshot_lang.py` — carga de traducciones.
- `src/language/generate_translations.py`, `show_translations.py`,
  `test_translations.py`, `neutralize_resource_import.py`, `Makefile`.

### 1.7 Tests

- `src/tests/` — 42 archivos `test_*.py` + `qt_test_app.py` (fixture Qt).
- Framework: pytest (con fixtures Qt).
- Cubren: modelos, ventanas, timeline, exportación, diálogos, etc.

### 1.8 Documentación

- `doc/` — Sphinx (`conf.py`, `index.rst`, +26 archivos `.rst`).
- `README.md`, `CONTRIBUTING.md`, `AUTHORS.md`, `COPYING` (GPL v3).

### 1.9 Instaladores / empaquetado

- `installer/` — `windows-installer.iss`, `isportable.iss` (Inno Setup),
  `package_msix.ps1`, `openshot-msix-template.xml`, `launch-win.bat`,
  `launch-linux.sh`, `launch-mac`, `build-mac-dmg.sh`, `deploy.py`,
  `build_server.py`, `analyze_bundle.py`, `qt.conf`, `windows.manifest`,
  `Info.plist`, `openshot.entitlements`, etc.
- Raíz: `freeze.py` (PyInstaller), `setup.py`, `MANIFEST.in`.

### 1.10 Workflows CI

- `.github/workflows/ci.yml`, `sphinx.yml`, `translations.yml`,
  `label-merge-conflicts.yml`.
- `.github/dependabot.yml`, `.github/stale.yml`.
- `.gitlab-ci.yml` (CI de GitLab, 15 KB).

### 1.11 Recuento de archivos por extensión (excl. ignorados)

| Extensión | Cantidad | Nota |
|---|---|---|
| `.png` | 3675 | iconos/recursos gráficos |
| `.svg` | 1516 | iconos vectoriales |
| `.po` | 675 | fuentes de traducción |
| `.jpg` | 525 | recursos gráficos |
| `.py` | 251 | código fuente y scripts |
| `.qm` | 107 | traducciones compiladas |
| `.xml` | 87 | plantillas / datos |
| `.cube` | 50 | LUT de etalonaje |
| `.json` | 47 | datos/configuración |
| `.ui` | 18 | diseños Qt Designer |
| `.rst` | 26 | documentación Sphinx |
| `.qrc` | 2 | recursos Qt |

---

## 2. libopenshot (motor de edición de vídeo)

**Ruta:** `D:\SMOUK by Shadow Coders\libopenshot`

### 2.1 Directorios principales

| Directorio | Función |
|---|---|
| `src/` | Núcleo C++ del motor (timeline, clips, frames, readers/writers, efectos). |
| `src/effects/` | Efectos de vídeo (C++). |
| `src/audio_effects/` | Efectos de audio (C++). |
| `src/Qt/` | Capa Qt (reproducción, caché, render). |
| `src/sort_filter/` | Algoritmos de seguimiento (SORT + Kalman). |
| `bindings/` | Bindings SWIG: `python/`, `java/`, `ruby/`, `godot/`. |
| `tests/` | Tests unitarios (Catch2). |
| `examples/` | Ejemplos y recursos multimedia de prueba. |
| `thirdparty/jsoncpp` | Código de terceros incluido (JSON para C++). |
| `external/godot-cpp` | Submódulo (Godot C++), declarado pero **no inicializado**. |
| `cmake/Modules` | Módulos CMake. |
| `doc/` | Documentación de instalación por plataforma. |
| `LICENSES/` | Textos de licencias SPDX. |
| `.reuse/` | Configuración REUSE (`dep5`). |

### 2.2 Archivos de entrada / raíz

- `CMakeLists.txt` (11.8 KB) — sistema de compilación principal.
- `version.sh` — versión del componente.
- `README.md`, `INSTALL.md`, `COPYING`, `AUTHORS`.
- `.gitmodules` — declara `external/godot-cpp`.
- `.gitlab-ci.yml` — CI.

### 2.3 Núcleo C++ en `src/`

Clases/subsistemas clave (archivos `.h`/`.cpp`):

- Timeline: `Timeline.*`, `TimelineBase.*`, `Clip.*`, `ClipBase.*`.
- Frames: `Frame.*`, `FrameMapper.*`, `FrameScope.*`.
- Lectura/escritura: `FFmpegReader.*`, `FFmpegWriter.*`, `ReaderBase.*`,
  `WriterBase.*`, `ImageReader.*`, `ImageWriter.*`, `TextReader.*`,
  `ChunkReader.*`, `ChunkWriter.*`, `DummyReader.*`.
- Lectores de dispositivo: `CameraCaptureReader.*`, `ScreenCaptureReader.*`,
  `WaylandScreenCaptureReader.*`.
- Lectores Qt: `QtImageReader.*`, `QtTextReader.*`, `QtHtmlReader.*`,
  `QtPlayer.*`.
- Reproducción: `PlayerBase.*`, `RendererBase.*`.
- Caché: `CacheBase.*`, `CacheDisk.*`, `CacheMemory.*`.
- Audio: `AudioReaderSource.*`, `AudioBufferSource.*`, `AudioResampler.*`,
  `AudioDevices.*`, `AudioRecorder.*`, `AudioWaveformer.*`, `AudioLocation.h`.
- Keyframes/animation: `KeyFrame.*`, `AnimatedCurve.*`, `Point.*`,
  `Coordinate.*`, `Fraction.*`, `Color.*`.
- Efectos base: `EffectBase.*`, `EffectInfo.*`, `Effects.h`.
- Detección/seguimiento CV: `CVObjectDetection.*`, `CVObjectMask.*`,
  `CVStabilization.*`, `CVTracker.*`, `TrackedObjectBase.*`,
  `TrackedObjectBBox.*`.
- Utilidades: `Json.*`, `Settings.*`, `Profiles.*`, `Exceptions.h`,
  `Enums.h`, `OpenShot.h`, `OpenShotVersion.*`, `CrashHandler.*`,
  `ZmqLogger.*`, `MemoryTrim.*`, `ClipProcessingJobs.*`, `ChannelLayouts.h`.
- Utilidades de terceros integradas: `MagickUtilities.*` (ImageMagick),
  `OpenCVUtilities.h`, `OpenMPUtilities.h`, `QtUtilities.h`,
  `FFmpegUtilities.h`, `WaylandBufferUtilities.h`.
- Protobuf: `objdetectdata.proto`, `stabilizedata.proto`, `trackerdata.proto`.

### 2.4 Efectos de vídeo (`src/effects/`)

Blur, Brightness, ChromaKey, ColorGrade, ColorMap, ColorShift, Crop,
Deinterlace, DenoiseImage, Displace, FilmGrain, Glow, Hue, LensFlare, Mask,
Negate, ObjectDetection, ObjectMask, Outline, Pixelate, Saturation, Shadow,
Sharpen, Shift, SphericalProjection, Stabilizer, Timer, Tracker, Wave,
AnalogTape, Bars, BeatSync, Caption, AudioVisualization, CropHelpers.

### 2.5 Efectos de audio (`src/audio_effects/`)

Compressor, Delay, Distortion, Echo, Expander, Noise, ParametricEQ,
Robotization, STFT, Whisperization.

### 2.6 Capa Qt (`src/Qt/`)

`AudioPlaybackThread`, `VideoPlaybackThread`, `VideoCacheThread`,
`PlayerPrivate`, `PlayerDemo`, `VideoRenderer`, `VideoRenderWidget`.

### 2.7 Bindings (SWIG)

- `bindings/python/openshot.i` + `CMakeLists.txt`.
- `bindings/java/openshot.i` + `CMakeLists.txt`.
- `bindings/ruby/openshot.i` + `CMakeLists.txt`.
- `bindings/godot/` — bindings Godot (`.gdextension`, `osg_timeline.*`,
  `register_types.*`).

### 2.8 Tests

- `tests/` — ~65 archivos `*.cpp` de tests unitarios.
- Framework: Catch2 (`catch2v2.h.in`, `catch2v3.h.in`, `catch_main.cpp`).

### 2.9 Ejemplos

- `examples/` — `Example.cpp`, `Example.py`, `Example.rb`, `ExampleHtml.*`,
  `Example_opencv.cpp`, `VulkanBenchmark.cpp`, subdirectorios `qt-demo/`,
  `vulkan/`, y recursos multimedia de prueba (`.mp4`, `.wav`, `.png`, LUTs).

### 2.10 Código de terceros

- `thirdparty/jsoncpp/` — biblioteca JSON en C++ (incluida/vendored).
- `external/godot-cpp/` — submódulo Godot (declarado, NO inicializado).

### 2.11 Recuento de archivos por extensión (excl. ignorados)

| Extensión | Cantidad |
|---|---|
| `.cpp` | 184 |
| `.h` | 128 |
| `.png` | 19 |
| `.txt` | 14 |
| `.md` | 6 |
| `.cmake` | 6 |
| `.py` | 3 |
| `.i` (SWIG) | 3 |
| `.proto` | 3 |

---

## 3. libopenshot-audio (motor de audio)

**Ruta:** `D:\SMOUK by Shadow Coders\libopenshot-audio`

### 3.1 Directorios principales

| Directorio | Función |
|---|---|
| `src/` | Código fuente propio (`.cpp`). |
| `include/` | Cabeceras generadas por CMake (`*.h.in`). |
| `JuceLibraryCode/` | Código JUCE (vendored): módulos + agregadores de compilación. |
| `cmake/Modules` | Módulos CMake. |
| `cmake/Config.cmake.in` | Plantilla de configuración CMake. |
| `doc/` | Documentación (página de manual, logotipo). |

### 3.2 Archivos de entrada / raíz

- `CMakeLists.txt` (17 KB) — sistema de compilación principal.
- `OpenShotLibrary.jucer` — proyecto Projucer/JUCE.
- `version.sh` — versión del componente.
- `README.md`, `INSTALL.md`, `COPYING`, `AUTHORS`.
- `.gitlab-ci.yml`, `.cproject`, `.project` (Eclipse), `.gitignore`, `.bzrignore`.

### 3.3 Código fuente propio (`src/`)

- `Main.cpp` — punto de entrada / demo de audio.
- `hex_version.cpp` — versión.
- `CMakeLists.txt`.

### 3.4 Cabeceras generadas (`include/`)

- `AppConfig.h.in`, `JuceHeader.h.in`, `OpenShotAudio.h.in` — plantillas
  procesadas por CMake para generar las cabeceras de la API pública.

### 3.5 Código JUCE (`JuceLibraryCode/`)

- `JuceHeader.h`, `AppConfig.h` — cabeceras de configuración JUCE.
- `include_juce_*.cpp` / `include_juce_*.mm` — agregadores de compilación por
  módulo (7 módulos).
- `modules/` — módulos JUCE vendored:
  `juce_audio_basics`, `juce_audio_devices`, `juce_audio_formats`,
  `juce_core`, `juce_data_structures`, `juce_dsp`, `juce_events`.
- `ReadMe.txt` — notas del código generado por Projucer.

### 3.6 Distinción de procedencia del código

- **OpenShot:** `src/Main.cpp`, `src/hex_version.cpp`, `CMakeLists.txt`,
  `include/*.in`, `cmake/*`.
- **JUCE (terceros vendored):** todo `JuceLibraryCode/` (módulos y agregadores).
- **Generado:** `JuceLibraryCode/AppConfig.h`, `JuceHeader.h` y los `include_juce_*`
  son regenerados por Projucer/CMake a partir de `OpenShotLibrary.jucer`.

### 3.7 Recuento de archivos por extensión (excl. ignorados)

| Extensión | Cantidad | Nota |
|---|---|---|
| `.h` | 493 | mayormente JUCE |
| `.cpp` | 327 | JUCE + propio |
| `.c` | 55 | JUCE |
| `.mm` | 24 | Objective-C++ (macOS/iOS) |
| `.java` | 6 | JUCE (Android) |
| `.in` | 4 | plantillas CMake |
| `.jucer` | 1 | proyecto Projucer |

---

## 4. Observaciones generales del inventario

1. **openshot-qt** es íntegramente Python + Qt (no contiene C++ propio); toda la
   lógica multimedia vive en `libopenshot` vía bindings SWIG.
2. **libopenshot** concentra el motor C++ y sus efectos; incluye `jsoncpp`
   (vendored) y declara un submódulo `godot-cpp` (no inicializado) para un
   binding experimental de Godot.
3. **libopenshot-audio** es un envoltorio fino sobre **JUCE** (vendored): el
   grueso del audio (dispositivos, drivers, buffers) proviene de JUCE.
4. Los tres repositorios comparten CI (`ci.yml` en GitHub, `.gitlab-ci.yml`) y
   usan CMake como sistema de compilación nativo.
5. La documentación de instalación específica por plataforma está en
   `libopenshot/doc/INSTALL-WINDOWS.md` (se analiza en la Fase 9).

---

## 5. FASE 0 — Validación técnica de Verticalization

### 5.1 Alcance inicial del MVP

La primera versión validará únicamente:

1. Dock Qt denominado `Verticalization`.
2. Proyecto vertical 9:16.
3. Overlay visual 9:16 sobre el visor 16:9.
4. Detección de cambios de plano.
5. Detección de caras y propuesta de encuadre.
6. Corrección manual plano a plano.
7. Importación de subtítulos SRT.
8. Logo fijo.
9. Captura PNG de la composición.
10. Exportación vertical básica.

La transcripción mediante IA, el seguimiento avanzado y la detección semántica se reservarán para fases posteriores.

### 5.2 Puntos de integración identificados

| Necesidad | Área prevista |
|---|---|
| Dock y controles | `openshot-qt/src/windows/` |
| Modelo de planos | `openshot-qt/src/windows/models/` o `src/classes/` |
| Visor y overlay | vistas de reproducción existentes |
| Persistencia | `src/classes/project_data.py` |
| Captura de fotograma | APIs existentes de reproducción/render |
| Títulos y logo | timeline, títulos y clips de imagen existentes |
| SRT | modelos y utilidades de subtítulos existentes |
| Detección multimedia | Python inicialmente; `libopenshot` solo si fuese necesario |
| Procesamiento pesado | tareas en segundo plano de la aplicación |
| Pruebas | `openshot-qt/src/tests/` |

### 5.3 Decisiones técnicas iniciales

- El dock se implementará inicialmente en Python usando la abstracción Qt existente.
- El análisis será no destructivo y sus resultados se guardarán como metadatos del proyecto.
- Cada plano conservará inicio, fin, miniatura y parámetros de encuadre.
- La propuesta automática nunca sustituirá un ajuste manual confirmado.
- El rectángulo 9:16 será un overlay del visor, no un efecto aplicado al vídeo original.
- La captura PNG se generará desde la composición renderizada, no mediante una captura de pantalla del widget.
- El análisis deberá poder cancelarse y ejecutarse en segundo plano.
- Las dependencias de IA serán opcionales para no bloquear la instalación básica.

### 5.4 Dependencias a evaluar

| Función | Primera opción | Alternativa |
|---|---|---|
| Cambios de plano | PySceneDetect | análisis propio con OpenCV |
| Detección facial | MediaPipe u OpenCV YuNet | RetinaFace |
| Saliencia | OpenCV | modelo ONNX ligero |
| Subtítulos posteriores | faster-whisper | whisper.cpp |
| Edición SRT | utilidad propia compatible con SRT | pysubs2 |

Antes de incorporarlas se debe verificar:

- Licencia compatible con GPLv3.
- Compatibilidad con las versiones soportadas de Python y Qt.
- Tamaño de los modelos.
- Funcionamiento sin conexión.
- Uso opcional de GPU.
- Compatibilidad con Windows, Linux y macOS.
- Posibilidad de distribuir o descargar los modelos legalmente.

### 5.5 Riesgos técnicos

- La detección facial puede fallar con perfiles, oclusiones o baja resolución.
- Un plano con varias personas puede requerir seguimiento y keyframes.
- La composición final puede necesitar cambios en `libopenshot` si las APIs actuales no permiten aplicar crops animados eficientemente.
- Los análisis largos no deben bloquear la interfaz.
- Los modelos de IA pueden aumentar considerablemente el tamaño del instalador.
- Las licencias de modelos y dependencias deben revisarse por separado de las licencias del código.

### 5.6 Criterios de aceptación de la fase 0

La fase 0 se considerará completada cuando exista:

- Diseño aprobado del dock.
- Mapa de integración con archivos concretos.
- Decisión sobre el formato de metadatos de los planos.
- Lista de dependencias permitidas y descartadas.
- Estrategia de ejecución local y uso opcional de GPU.
- Matriz de plataformas soportadas.
- Plan de pruebas para vídeos con cortes, caras, varias personas y ausencia de caras.
- Confirmación de que no es necesario modificar `libopenshot` para el primer prototipo.

### 5.7 Resultado de la fase

No se modifica todavía ningún archivo de código. El siguiente paso será realizar una inspección específica de las ventanas, modelos, visor, timeline, persistencia y pruebas existentes de `openshot-qt`, para elaborar el mapa exacto de archivos que participarán en el prototipo.

### 5.8 Estado de ejecución

**Estado: PARCIAL — pendiente de inspección del código fuente.**

Con el inventario disponible se han validado:

- La separación arquitectónica entre `openshot-qt`, `libopenshot` y `libopenshot-audio`.
- La conveniencia de implementar el primer prototipo en Python y Qt.
- La posibilidad de reutilizar timeline, títulos, clips de imagen, renderizado y bindings existentes.
- La necesidad de ejecutar el análisis multimedia en segundo plano.
- La conveniencia de mantener las dependencias de IA como opcionales.
- Los riesgos principales de licencias, rendimiento, modelos y compatibilidad multiplataforma.

No se pueden confirmar todavía:

- El archivo y la clase concretos donde registrar el dock.
- El visor exacto que debe recibir el overlay 9:16.
- La API disponible para capturar un fotograma compuesto.
- El formato correcto de persistencia del proyecto.
- La integración exacta con títulos, subtítulos y clips de imagen.
- La disponibilidad de keyframes o crops suficientes para el primer prototipo.
- Si será necesario modificar `libopenshot`.
- La lista definitiva de dependencias y versiones compatibles.
- La ejecución real de pruebas sobre vídeos de referencia.

### 5.9 Requisito para cerrar la fase 0

Para completar la fase 0 se necesita proporcionar el repositorio `openshot-qt` o, como mínimo, estos archivos y directorios:

- `src/windows/main_window.py`.
- Archivos del visor y reproducción.
- Archivos de timeline.
- `src/classes/project_data.py`.
- Clases de títulos, clips e imágenes.
- Configuración de dependencias y versiones de Python/Qt.
- Pruebas relacionadas con ventanas, timeline y renderizado.

Hasta disponer de esos archivos, la fase 0 queda correctamente planificada, pero no validada técnicamente al completo.

