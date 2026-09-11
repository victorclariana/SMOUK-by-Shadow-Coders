# Análisis del código fuente — OpenShot / SMOUK by Shadow Coders

> Índice maestro del análisis de la primera fase del proyecto. Documenta el
> estado real de los repositorios, la arquitectura verificada y los límites de
> personalización de la interfaz, **sin haber modificado el código fuente**.

---

## Objetivo del análisis

Analizar completamente el código fuente oficial de OpenShot (descargado en el
workspace) antes de modificar su interfaz, verificando (no asumiendo) la
arquitectura, los lenguajes, las tecnologías, las dependencias y el proceso de
compilación en Windows.

## Repositorios analizados

| Repositorio | Rama | Commit | Etiqueta más cercana |
|---|---|---|---|
| openshot-qt | develop | `4cabe0231` | `v4.0.0` (+23 commits) |
| libopenshot | develop | `772e6794` | `v1.0.0` (+16 commits) |
| libopenshot-audio | develop | `2819b3b` | `v1.0.0` (+1 commit) |

- Los tres están en la rama de **desarrollo** (`develop`), con árbol de trabajo
  **limpio** y sincronizados con `origin/develop`.

## Resumen de arquitectura

- `openshot-qt` (Python + PyQt5/PyQt6/PySide6) es la **interfaz**.
- `libopenshot` (C++17) es el **motor** de edición/reproducción/exportación.
- `libopenshot-audio` (C++17 + JUCE) es el **motor de audio**.
- La UI se comunica con el motor mediante **bindings SWIG** (`import openshot`).
- El proyecto se representa como **JSON** (`.osp`) en `ProjectDataStore` y se
  sincroniza con el motor a través de `TimelineSync` + `UpdateManager`.

## Lenguajes principales

Python, C++ (C++17), C, Objective-C++, Java (JUCE/Android), Ruby (binding),
Shell, PowerShell/Batch.

## Estado del análisis

**Fases completadas (1–11):**

| Documento | Contenido |
|---|---|
| [00-repositories-and-versions.md](00-repositories-and-versions.md) | Verificación Git de los repositorios. |
| [01-source-inventory.md](01-source-inventory.md) | Inventario completo de archivos. |
| [02-languages-and-technologies.md](02-languages-and-technologies.md) | Lenguajes y tecnologías verificados. |
| [03-architecture-overview.md](03-architecture-overview.md) | Arquitectura + diagramas Mermaid. |
| [04-openshot-qt-code-map.md](04-openshot-qt-code-map.md) | Mapa de código de la UI. |
| [05-libopenshot-code-map.md](05-libopenshot-code-map.md) | Mapa de código del motor. |
| [06-libopenshot-audio-code-map.md](06-libopenshot-audio-code-map.md) | Mapa de código del audio. |
| [07-dependencies.md](07-dependencies.md) | Inventario de dependencias. |
| [08-windows-build-analysis.md](08-windows-build-analysis.md) | Compilación Windows (sin compilar). |
| [09-ui-customization-boundaries.md](09-ui-customization-boundaries.md) | Límites de personalización de UI. |

## Fase Verticalization (investigación y diseño — sin implementar)

| Documento | Contenido |
|---|---|
| [10-verticalization-architecture.md](10-verticalization-architecture.md) | Dock `Verticalization`, arquitectura modular, modelo de datos, flujo, directorios, rendimiento. |
| [11-shot-detection-research.md](11-shot-detection-research.md) | Detección de planos (PySceneDetect vs FFmpeg vs OpenCV). |
| [12-reframing-research.md](12-reframing-research.md) | Reencuadre 9:16, tecnologías de sujeto/seguimiento, overlay en visor. |
| [13-catalan-subtitles-research.md](13-catalan-subtitles-research.md) | Subtítulos en catalán (Whisper), efecto `Caption`, segmentación. |
| [14-titles-poster-export.md](14-titles-poster-export.md) | Títulos (SVG vs MOV alpha), logo, portada PNG, exportación vertical. |
| [15-licenses-matrix.md](15-licenses-matrix.md) | Matriz de licencias (código, modelos, pesos). |


## Elementos no verificados

- Versión mínima exacta de **Python** (solo «3.0+» en `README.md`).
- Versión mínima exacta de **FFmpeg** (no fijada en archivos).
- Versión exacta de **Qt** usada en producción (solo «Qt5 o Qt6»).
- Versión exacta de **ZeroMQ / OpenCV / babl**.
- Compatibilidad ABI/API exacta entre `openshot-qt` y `libopenshot` más allá
  del chequeo de versión (`MINIMUM_LIBOPENSHOT_VERSION = "1.0.0"`).

## Riesgos principales

1. **Todos los repositorios en `develop`** (no en una etiqueta estable).
2. **Submódulo `external/godot-cpp` no inicializado** en `libopenshot`
   (no afecta a la compilación estándar).
3. **Documentación Windows parcialmente desactualizada** (usa UnitTest++,
   Python 3.3, MSYS 1.0; el CI actual usa Catch2 y MSYS2/MinGW64).
4. **MSVC no soportado** (solo MinGW/MSYS2 en Windows).
5. **Coherencia Qt5/Qt6** entre el motor y el binding Python de la UI.

## Próxima fase recomendada

1. Definir el alcance de la **nueva interfaz (SMOUK)** sobre la capa de
   personalización de **bajo y medio riesgo** (temas, iconos, layout, docks,
   menús) descrita en `09-ui-customization-boundaries.md`.
2. Antes de programar, fijar la combinación exacta de versiones (Qt, Python,
   FFmpeg) y validar un build Windows reproducible basado en el
   `.gitlab-ci.yml` (MSYS2/MinGW64).
3. No tocar `libopenshot` ni `libopenshot-audio` salvo que se requiera una
   funcionalidad nueva de motor.
