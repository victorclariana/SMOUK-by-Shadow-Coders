# FASE 10 — Límites de personalización de la interfaz

> Clasificación de áreas de la interfaz según el riesgo de modificarlas sin
> alterar el funcionamiento interno (motor C++/audio). Todo el análisis se basa
> en la estructura verificada en fases anteriores.

---

## 1. BAJO RIESGO (personalización visual pura)

Estas áreas pueden modificarse sin tocar el motor y sin riesgo funcional alto.

| Área | Archivos implicados | Clases | ¿Toca C++? |
|---|---|---|---|
| Colores / temas / hojas de estilo | `src/themes/`, `*.css`, `src/themes/base.py`, `manager.py` | `BaseTheme`, `ThemeManager`, `TimelineTheme` | No |
| Iconos / logotipos / cursores | `images/`, `src/images/`, `images/openshot.qrc` | — | No |
| Tipografías / márgenes / espaciados / tamaños | `*.ui`, `*.css`, `src/classes/style_tools.py` | — | No |
| Estilos de botones / organización visual | `src/windows/ui/*.ui`, hojas de estilo | — | No |

- **Dependencias:** solo recursos Qt (`.qrc`, `.css`, `.ui`).
- **Impacto esperado:** cosmético; no altera señales ni datos.
- **Riesgos:** romper referencias de recursos si se renombran/eliminan iconos.
- **Tests necesarios:** `src/tests/test_message_box_styling.py`,
  `test_qt_resource_imports.py`; inspección visual.
- **Rollback:** trivial (git revert de recursos).
- **Resolubles exclusivamente en `openshot-qt`:** SÍ.

---

## 2. RIESGO MEDIO (reorganización de UI sobre datos existentes)

| Área | Archivos implicados | Clases | ¿Toca C++? |
|---|---|---|---|
| Reorganización de paneles / docks | `src/windows/ui/main-window.ui`, `src/windows/scope_panel.py`, `audio_recording.py` | `MainWindow`, `*DockContent` | No |
| Menús / barras de herramientas | `src/windows/ui/*.ui`, `src/windows/views/menu.py` | `MainWindow` | No |
| Disposición del visor / controles | `src/windows/video_widget.py`, `*.ui` | `VideoWidget` | No |
| Nuevas vistas sobre datos existentes | `src/windows/views/*.py`, `src/windows/models/*.py` | `FilesModel`, `PropertiesModel`, etc. | No |
| Reorganización de diálogos | `src/windows/*.py` + `*.ui` | `Export`, `Preferences`, etc. | No |

- **Dependencias:** modelos Qt (`UpdateInterface`), señales de `MainWindow`.
- **Impacto esperado:** mejora de usabilidad; requiere conservar señales y
  slots para no romper la sincronización con el motor.
- **Riesgos:** perder conexiones señal/slot; duplicar IDs de `.ui`.
- **Tests necesarios:** `test_main_window.py`, `test_app_window_state.py`,
  `test_dialog_preview_resize.py`.
- **Rollback:** posible con git revert.
- **Resolubles exclusivamente en `openshot-qt`:** SÍ (sin tocar el motor).

---

## 3. ALTO RIESGO (núcleo de edición/reproducción)

Estas áreas son delicadas; su modificación puede afectar el motor o la
sincronización A/V.

| Área | Archivos implicados | Clases | ¿Toca C++? |
|---|---|---|---|
| Timeline visual | `src/windows/views/timeline.py`, `views/timeline_backend/` | `TimelineView`, `TimelineWidget`, `TimelineStateMachine` | No (pero lógica delicada) |
| Visor / reproducción | `src/windows/video_widget.py`, `preview_thread.py` | `VideoWidget`, `PreviewParent`, `PlayerWorker` | No (motor ya en C++) |
| Hilos / sincronización A/V | `preview_thread.py`, `libopenshot/src/Qt/` | `PlayerWorker`, `AudioPlaybackThread` | Parcial |
| Modelo de proyecto / serialización | `src/classes/project_data.py`, `json_data.py` | `ProjectDataStore`, `JsonDataStore` | No |
| Bindings | `libopenshot/bindings/python/openshot.i` | — | SÍ |
| Caché | `libopenshot/src/Cache*.cpp` | `CacheMemory`, `CacheDisk` | SÍ |
| Exportación | `src/windows/export.py`, `libopenshot/src/FFmpegWriter.cpp` | `Export`, `FFmpegWriter` | Parcial |
| Motor C++ | `libopenshot/src/` | `Timeline`, `Clip`, `Frame` | SÍ |
| Motor de audio | `libopenshot-audio/` (JUCE) | — | SÍ |

- **Dependencias:** motor C++ (`libopenshot`), FFmpeg, JUCE, bindings SWIG.
- **Impacto esperado:** funcional (edición, reproducción, exportación).
- **Riesgos:** corrupción de proyectos, desincronización A/V, rotura de ABI.
- **Tests necesarios:** tests C++ (Catch2) y tests Python (`test_timeline_helpers.py`,
  `test_video_widget_transform.py`, `test_project_data.py`, etc.).
- **Rollback:** posible, pero exige recompilar si se tocó C++.
- **Resolubles exclusivamente en `openshot-qt`:** NO (requieren `libopenshot`
  y/o `libopenshot-audio`).

---

## 4. Recomendaciones para la nueva interfaz (SMOUK)

1. **Empezar por la capa BAJA y MEDIA** (temas, iconos, layouts, docks, menús),
   que permiten cambiar radicalmente el aspecto sin tocar el motor.
2. **Conservar intactos:** `classes/timeline.py` (`TimelineSync`),
   `windows/preview_thread.py`, `classes/project_data.py`, `json_data.py` y
   todas las señales de `MainWindow`.
3. **No modificar** `libopenshot`/`libopenshot-audio` a menos que se quiera
   añadir una funcionalidad nueva de motor (requiere SWIG + recompilación).
4. **Para cambiar el estilo de la timeline**, usar `TimelineTheme`/`styles.py`
   y los temas `cosmic`/`humanity` antes que tocar la lógica de interacción.
5. **Mantener la compatibilidad del formato `.osp`** (JSON) para no romper la
   apertura de proyectos existentes.
