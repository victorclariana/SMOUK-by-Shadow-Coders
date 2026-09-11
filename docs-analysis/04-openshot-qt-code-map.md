# FASE 5 — Análisis detallado de openshot-qt

> Mapa de código de la interfaz. Para cada componente se indica: ruta, clase
> principal, responsabilidad, dependencias, señales/slots, comunicación con el
> motor, riesgo de modificación y posibilidad de personalización sin tocar C++.

---

## 1. Punto de entrada e inicialización

- **Ruta:** `src/launch.py` (función `main()`); `src/__init__.py`.
- **Clase de aplicación:** `OpenShotApp(QApplication)` en `src/classes/app.py:73`.
- **Responsabilidad:** configurar Qt, cargar `openshot` (bindings), crear
  `SettingStore`, `ProjectDataStore`, `UpdateManager`, `ThemeManager`, y lanzar
  `MainWindow` mediante `gui()`.
- **Métodos clave:** `__init__`, `gui()`, `show_environment()`,
  `check_libopenshot_version()`, `cleanup()`.
- **Señales:** `aboutToQuit` (conecta `cleanup`).
- **Comunicación con motor:** `import openshot`; fija
  `openshot.Settings.Instance().PATH_OPENSHOT_INSTALL`.
- **Riesgo:** ALTO (controla todo el arranque y las referencias globales).
- **Personalización sin C++:** SÍ (es Python), pero con cuidado por ser el núcleo.

---

## 2. Ventana principal

- **Ruta:** `src/windows/main_window.py`; UI: `src/windows/ui/main-window.ui`.
- **Clase:** `MainWindow(updates.UpdateWatcher, QMainWindow)` (línea 102).
- **Responsabilidad:** orquestar paneles, docks, menús, barras de herramientas,
  transporte, timeline, visor, gestión de proyecto y acciones globales.
- **Señales emitidas** (líneas 108-120): `previewFrameSignal`,
  `refreshFrameSignal`, `refreshFilesSignal`, `refreshTransitionsSignal`,
  `refreshEffectsSignal`, `LoadFileSignal`, `PlaySignal`, `PauseSignal`,
  `StopSignal`, `SeekSignal`, `SpeedSignal`, etc.
- **Métodos clave:** `save_project()` (`main_window.py:574`), `open_project()`
  (`main_window.py:675`), `updateStatusChanged()` (`main_window.py:3792`).
- **Dependencias:** casi todo `src/classes/` y `src/windows/` (models, views,
  preview_thread, video_widget).
- **Comunicación con motor:** indirecta a través de `TimelineSync` y
  `PreviewParent` (no toca C++ directamente salvo vía `import openshot`).
- **Riesgo:** ALTO (concentra la lógica de UI).
- **Personalización sin C++:** SÍ (layout, estilos, organización de paneles).

---

## 3. Timeline visual

- **Ruta:** `src/windows/views/timeline.py` (clase `TimelineView`), backend en
  `src/windows/views/timeline_backend/`.
- **Backend de renderizado:** `timeline_backend/qwidget/` con `TimelineWidget`
  (`__init__.py:38`), `TimelineWidgetBase` (`base.py:138`), `TimelineEvents`
  (`base.py:75`), `TimelineThumbnailManager` (`thumbnails.py:85`),
  `TimelineStateMachine` (`state.py:91`), `TimelineTheme` (`theme.py:91`).
- **Responsabilidad:** representación visual de pistas/clips, interacción
  (drag & drop, recorte, zoom, snap), miniaturas, playhead.
- **Comunicación con motor:** vía `TimelineSync` (los cambios del diccionario
  del proyecto se traducen a `openshot.Timeline`).
- **Riesgo:** ALTO (pieza central de la edición visual).
- **Personalización sin C++:** SÍ en estilo (`TimelineTheme`, `styles.py`,
  temas `cosmic`/`humanity`); la lógica de interacción es delicada.

---

## 4. Visor / controles de transporte

- **Visor:** `src/windows/video_widget.py` → `VideoWidget(QWidget,
  updates.UpdateInterface)` (línea 57).
- **Reproducción:** `src/windows/preview_thread.py` → `PreviewParent(QObject,
  UpdateInterface)` (hilo UI) y `PlayerWorker` (hilo de trabajo).
- **Señales:** `regionAnnotationChanged`, `regionRectChanged`,
  `scopeRegionCancelled` (VideoWidget).
- **Comunicación con motor:** `openshot.QtPlayer` entrega frames al widget;
  `PreviewParent` mueve el playhead y gestiona seek/play/pause.
- **Riesgo:** ALTO (sincronización audio/vídeo, hilos).
- **Personalización sin C++:** MEDIA (restyle del widget; no el motor).

---

## 5. Panel de archivos del proyecto

- **Modelo:** `src/windows/models/files_model.py` → `FilesModel(QObject,
  updates.UpdateInterface)` (línea 209), señal `ModelRefreshed`.
- **Vistas:** `src/windows/views/files_treeview.py` (`FilesTreeView`),
  `src/windows/views/files_listview.py` (`FilesListView`),
  `src/windows/views/files_thumbnail_overlay.py`.
- **Responsabilidad:** listar medios importados, miniaturas, búsqueda,
  drag & drop hacia la timeline.
- **Comunicación con motor:** a través del proyecto (`files`); los `reader` se
  crean al importar (vía `openshot.FFmpegReader`/`QtImageReader`).
- **Riesgo:** BAJO-MEDIO. **Personalización sin C++:** SÍ.

---

## 6. Panel de propiedades

- **Modelo:** `src/windows/models/properties_model.py` → `PropertiesModel(
  updates.UpdateInterface)` (línea 69).
- **Vista:** `src/windows/views/properties_tableview.py` →
  `PropertiesTableView`, `SelectionLabel`.
- **Responsabilidad:** editar atributos del clip/transición/efecto
  seleccionado y keyframes.
- **Comunicación con motor:** edita el diccionario del proyecto; `TimelineSync`
  lo propaga al motor.
- **Riesgo:** MEDIO. **Personalización sin C++:** SÍ.

---

## 7. Efectos y transiciones

- **Modelos:** `src/windows/models/effects_model.py` (`EffectsModel`),
  `src/windows/models/transition_model.py` (`TransitionsModel`).
- **Vistas:** `src/windows/views/effects_treeview.py`, `effects_listview.py`,
  `transitions_treeview.py`, `transitions_listview.py`.
- **Definiciones:** `src/effects/`, `src/transitions/common/`,
  `src/transitions/extra/`.
- **Comunicación con motor:** los efectos reales se aplican en C++
  (`libopenshot/src/effects/`); la UI gestiona la configuración JSON.
- **Riesgo:** MEDIO. **Personalización sin C++:** SÍ (los efectos nuevos
  requieren C++).

---

## 8. Exportación

- **Diálogo:** `src/windows/export.py` → `Export(QDialog)` (línea 65); UI en
  `src/windows/ui/export.ui`.
- **Exportadores EDL/XML:** `src/classes/exporters/edl.py`, `final_cut_pro.py`.
- **Recursos:** `src/resources/export-*.xml`, `src/profiles/`, `src/presets/`.
- **Comunicación con motor:** crea `openshot.FFmpegWriter` y escribe frames.
- **Riesgo:** ALTO. **Personalización sin C++:** MEDIA (presets, perfiles, UI).

---

## 9. Preferencias

- **Diálogo:** `src/windows/preferences.py` → `Preferences(QDialog)` (línea 53);
  UI en `src/windows/ui/preferences.ui`.
- **Almacén:** `src/classes/settings.py` → `SettingStore` (JSON en
  `~/.openshot_qt/openshot.settings`).
- **Riesgo:** BAJO-MEDIO. **Personalización sin C++:** SÍ.

---

## 10. Menús, barras de herramientas, acciones, docks y layout

- **UI declarativa:** `src/windows/ui/*.ui` (18 archivos), cargados con
  `uic`/`QUiLoader` desde `qt_api`.
- **Menús personalizados:** `src/windows/views/menu.py`.
- **Docks:** `src/windows/audio_recording.py` (`AudioRecordingDockContent`),
  `src/windows/scope_panel.py` (`WaveformDockContent`, `HistogramDockContent`,
  `VectorscopeDockContent`, `AudioMeterWidget`).
- **Atajos/acciones:** `QAction`/`QShortcut` en `MainWindow`; `src/classes/tabstops.py`.
- **Riesgo:** BAJO-MEDIO (reorganizar paneles es seguro si se conservan señales).

---

## 11. Temas, hojas de estilo e iconos

- **Temas:** `src/themes/base.py` (`BaseTheme`, `MessageBoxStyleFilter`),
  `src/themes/manager.py` (`ThemeManager`), `src/themes/cosmic/`,
  `src/themes/humanity/` (hojas de estilo `.css`, iconos, estilos de timeline).
- **Iconos:** `images/` y `src/images/`; recurso `images/openshot.qrc`.
- **Riesgo:** BAJO (zona idónea para personalización visual).

---

## 12. Gestión del proyecto, undo/redo y drag & drop

- **Modelo:** `src/classes/project_data.py` → `ProjectDataStore`.
- **Persistencia:** `src/classes/json_data.py` → `JsonDataStore`.
- **Undo/redo:** historial en clave `history` + `UpdateManager`
  (`src/classes/updates.py`).
- **Drag & drop:** implementado en vistas (files/timeline) y `MainWindow`.
- **Riesgo:** ALTO (modelo de datos + serialización).

---

## 13. Comunicación con libopenshot (resumen)

- `src/classes/timeline.py` → `TimelineSync` (crea y sincroniza
  `openshot.Timeline`).
- `src/windows/preview_thread.py` → `PreviewParent`/`PlayerWorker`
  (reproducción con `openshot.QtPlayer`).
- `src/classes/logger_libopenshot.py` → captura logs del motor (hilo).
- `src/classes/thumbnail.py` → miniaturas usando readers del motor.

---

## 14. Workers y threads

- `PreviewParent`/`PlayerWorker` (reproducción).
- `LoggerLibOpenShot(Thread)` (logging).
- `_GenerationWorker`/`GenerationQueueManager` (`src/classes/generation_queue.py`).
- `GenerationService`, `_ComfyAvailabilityWorker` (`src/classes/generation_service.py`).
- `httpThumbnailServerThread` (`src/classes/thumbnail.py`).

---

## 15. Tests de interfaz

- **Ruta:** `src/tests/` (42 `test_*.py`).
- **Fixture Qt:** `qt_test_app.py`.
- **Framework:** `unittest` (CI corre `python3 -m unittest discover -s src/tests`)
  y `pytest` en algunos casos.
- **Cobertura:** modelos, ventanas, timeline, exportación, diálogos, utilidades.

---

## 16. Código específico de Windows (openshot-qt)

- `src/launch.py:50-58` — DLL de Qt en `PATH`.
- `installer/windows-installer.iss`, `isportable.iss`, `package_msix.ps1`,
  `openshot-msix-template.xml`, `launch-win.bat`, `qt.conf`, `windows.manifest`.

---

## 17. Tabla resumen de riesgo de personalización

| Componente | Archivos principales | Riesgo | ¿Toca C++? |
|---|---|---|---|
| Temas/estilos/iconos | `src/themes/`, `images/`, `*.css`, `*.qrc` | BAJO | No |
| Preferencias | `windows/preferences.py`, `classes/settings.py` | BAJO-MEDIO | No |
| Paneles/docks/menús | `windows/ui/*.ui`, `views/menu.py`, `scope_panel.py` | MEDIO | No |
| Modelos/vistas de listas | `windows/models/*.py`, `windows/views/*.py` | MEDIO | No |
| Exportación | `windows/export.py`, `classes/exporters/` | ALTO | Parcial |
| Timeline visual | `views/timeline.py`, `views/timeline_backend/` | ALTO | No (pero lógica delicada) |
| Visor/reproducción | `video_widget.py`, `preview_thread.py` | ALTO | No (motor ya en C++) |
| Proyecto/serialización | `classes/project_data.py`, `json_data.py` | ALTO | No |
| Comunicación con motor | `classes/timeline.py`, `preview_thread.py` | ALTO | Parcial (SWIG) |

