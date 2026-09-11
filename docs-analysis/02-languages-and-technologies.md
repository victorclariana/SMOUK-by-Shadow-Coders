# FASE 3 — Lenguajes y tecnologías

> Determinación de lenguajes y tecnologías **realmente** presentes en el código,
> configuración y documentación. No se asumen versiones: se cita el archivo que
> las evidencia.

---

## 1. Lenguajes de programación

### 1.1 Python

- **Repositorio:** `openshot-qt` (principal), `libopenshot` (scripts de ejemplo
  y bindings generados).
- **Uso:** toda la interfaz y la lógica de aplicación; scripts de empaquetado;
  ejemplos de uso del motor; tests de interfaz.
- **Directorios:** `openshot-qt/src/` (251 `.py`), `openshot-qt/installer/`,
  `libopenshot/examples/` (`Example.py`, `OpenShot Wipe Tests.py`).
- **Archivos de entrada:** `openshot-qt/src/launch.py` (punto de entrada;
  `info.py` lo declara como `openshot_qt.launch:main`), `src/__init__.py`,
  `src/qt_api.py`.
- **Versión:** los documentos indican «Python 3.0+».
  - `openshot-qt/README.md` (línea 96): «OpenShot is programmed in Python
    (version 3+)».
  - `libopenshot/INSTALL.md` (línea 82): «Python 3 (libpython)».
  - **Rango concreto fijado:** no hay `python_requires` explícito en `setup.py`;
    se documenta «3+» (versión mínima no fijada de forma precisa).
- **Interviene en:** runtime (interfaz), testing (`src/tests/`), empaquetado
  (`setup.py`, `freeze.py`), build de bindings (vía SWIG).

### 1.2 C++

- **Repositorio:** `libopenshot` (principal), `libopenshot-audio` (propio + JUCE).
- **Uso:** motor de edición (timeline, clips, frames, readers/writers, efectos),
  motor de audio, bindings, tests.
- **Directorios:** `libopenshot/src/` (184 `.cpp`/128 `.h`),
  `src/effects/`, `src/audio_effects/`, `src/Qt/`, `src/sort_filter/`,
  `tests/`, `libopenshot-audio/src/`, `libopenshot-audio/JuceLibraryCode/`.
- **Estándar:** **C++17**.
  - `libopenshot/CMakeLists.txt` (líneas 101–104): `CMAKE_CXX_STANDARD 17`,
    `CMAKE_CXX_STANDARD_REQUIRED ON`, `CMAKE_CXX_EXTENSIONS OFF`.
  - `libopenshot-audio/CMakeLists.txt` (líneas 46–49): idem C++17.
- **Interviene en:** runtime (motor), build (compilación), testing (tests Catch2).

### 1.3 C

- **Repositorio:** `libopenshot-audio` (código JUCE).
- **Uso:** partes internas de JUCE (zlib, códecs FLAC/OGG, etc.).
- **Evidencia:** 55 archivos `.c` bajo `JuceLibraryCode/modules/`.

### 1.4 Objective-C++

- **Repositorio:** `libopenshot-audio` (JUCE).
- **Uso:** backends nativos macOS/iOS de JUCE.
- **Evidencia:** 24 archivos `.mm` (`include_juce_*.mm`) en `JuceLibraryCode/`.

### 1.5 Java

- **Repositorio:** `libopenshot-audio` (JUCE) y binding `libopenshot/bindings/java/`.
- **Uso:** JUCE para Android (6 `.java`); binding Java de libopenshot
  (`bindings/java/openshot.i` + `CMakeLists.txt`).

### 1.6 Ruby

- **Repositorio:** `libopenshot`.
- **Uso:** binding Ruby generado por SWIG.
- **Evidencia:** `libopenshot/bindings/ruby/openshot.i`, `examples/Example.rb`.

### 1.7 Shell script (sh/bash)

- **Repositorio:** los tres.
- **Uso:** scripts de empaquetado/CI.
- **Evidencia:** `openshot-qt/installer/build-mac-dmg.sh`, `launch-linux.sh`,
  `mangle-hw-libs.sh`; `libopenshot/version.sh`; `libopenshot-audio/version.sh`.

### 1.8 PowerShell / Batch (Windows)

- **Repositorio:** `openshot-qt`.
- **Uso:** empaquetado MSIX y lanzador Windows.
- **Evidencia:** `installer/package_msix.ps1`, `installer/launch-win.bat`.

---

## 2. Frameworks y bibliotecas de interfaz (Qt)

### 2.1 Bindings Python de Qt

- **Repositorio:** `openshot-qt`.
- **Soportados (según `src/qt_api.py`):** **PyQt6, PySide6 y PyQt5**.
  - `src/qt_api.py` (líneas 4–7): «Selects an available binding
    (PyQt6/PySide6/PyQt5) using the `OPENSHOT_QT_API` env var (`auto` default,
    otherwise one of `pyqt6|pyside6|pyqt5`)».
  - `openshot-qt/README.md` (línea 97): «PyQt / PySide binding for Qt5 or Qt6».
- **PySide2** no aparece. El conjunto soportado es {PyQt5, PyQt6, PySide6}.
- **CI de referencia:** `openshot-qt/.github/workflows/ci.yml` instala
  `python3-pyqt5` (PyQt5) para las pruebas.

### 2.2 Qt (C++)

- **Repositorio:** `libopenshot`.
- **Uso:** visualización de vídeo, composición de imágenes, efectos, utilidades.
- **Versiones:** **Qt5 y Qt6**, seleccionables con `-DUSE_QT6=AUTO|ON|OFF`.
  - `libopenshot/INSTALL.md` (línea 204): «`-DUSE_QT6=AUTO|ON|OFF`».
  - `libopenshot/src/CMakeLists.txt` (líneas 400–418): `find_package(Qt6 ... QUIET)`
    y luego `find_package(Qt${QT_VERSION_MAJOR} ...)`.
- **CI:** `libopenshot/.github/workflows/ci.yml` instala `qtbase5-dev` (Qt5).

### 2.3 Componentes Qt detectados

- `QtCore`, `QtGui`, `QtWidgets`, `QtSvg` (exports en `openshot-qt/src/qt_api.py`).
- En C++: `QtCore`, `QtGui`, `QtWidgets`, `QSvgRenderer`/`QtSvg`
  (`libopenshot/src/QtImageReader.cpp`).

---

## 3. Bibliotecas nativas del motor (libopenshot)

| Tecnología | Evidencia | Finalidad |
|---|---|---|
| **FFmpeg** | `src/CMakeLists.txt:435` `find_package(FFmpeg REQUIRED COMPONENTS avcodec avdevice avformat avutil swscale ...)` | decodificar/codificar vídeo, audio e imágenes. |
| **ImageMagick++** | opción `ENABLE_MAGICK` (`CMakeLists.txt:73`), `src/MagickUtilities.*` | decodificación/encoding de imágenes (opcional). |
| **OpenCV** | opción `ENABLE_OPENCV` (`CMakeLists.txt:74`), `src/CV*.cpp`, `OpenCVUtilities.h` | detección/seguimiento, máscaras, estabilización, ONNX (DNN). |
| **Protobuf 3** | `ENABLE_OPENCV` nota «requires Boost, Protobuf 3»; `src/*.proto` | serialización de datos de seguimiento/detección. |
| **Boost** | nota `ENABLE_OPENCV` «requires Boost, Protobuf 3» | soporte para algoritmos OpenCV. |
| **ZeroMQ (libzmq)** | `src/ZmqLogger.*`; CI `libzmq3-dev`; `INSTALL.md` | logging/depuración publicador/suscriptor. |
| **OpenMP** | `INSTALL.md` (`-fopenmp`), `src/OpenMPUtilities.h`; CI `libomp-dev` | paralelización multi-núcleo. |
| **babl** | `src/CMakeLists.txt:549` `babl_lib`; `ChromaKey.cpp` | conversión de espacios de color (Chroma Key). |
| **resvg** | `src/CMakeLists.txt:356` `Resvg::Resvg`; `QtImageReader.*` | rasterizado de SVG. |
| **JSON (jsoncpp)** | `thirdparty/jsoncpp/`, `src/Json.*`; opción `USE_SYSTEM_JSONCPP` | serialización JSON (proyectos `.osp`, config). |
| **Vulkan** | opción `ENABLE_VULKAN_BENCHMARK`; `examples/VulkanBenchmark.cpp` | benchmark experimental (opcional). |
| **Godot (godot-cpp)** | submódulo `external/godot-cpp`, `bindings/godot/*.gdextension` | binding experimental de Godot. |

### 3.1 FFmpeg — componentes y versiones

- Componentes: `avcodec avdevice avformat avutil swscale` (obligatorios),
  `swresample` (opcional) o `avresample` (fallback).
- Aceleración hardware: `src/CMakeLists.txt:473` habilita `HAVE_HW_ACCEL` si
  `FFmpeg_avcodec_VERSION > 57.106`.
- `src/FFmpegUtilities.h` usa `LIBAVCODEC_VERSION_INT >= AV_VERSION_INT(57, 107, 100)`
  para el macro `USE_HW_ACCEL` por defecto.

### 3.2 OpenCV y ONNX

- **ONNX Runtime NO se usa como dependencia independiente.** No hay
  `ONNXRuntime` ni `OrtSession` en el código.
- Los modelos ONNX se cargan mediante **OpenCV DNN**:
  `libopenshot/src/CVObjectDetection.cpp:230` → `cv::dnn::readNetFromONNX(modelPath)`.
- Requiere OpenCV ≥ 4.3.0 (`CVObjectDetection.cpp:226`).
- Modelos referenciados desde `openshot-qt/src/resources/` (YOLO, EfficientSAM,
  Cutie) y `src/windows/process_effect.py`.

---

## 4. Biblioteca de audio (libopenshot-audio)

| Tecnología | Evidencia | Finalidad |
|---|---|---|
| **JUCE** | `JuceLibraryCode/` (módulos `juce_audio_*`, `juce_core`, `juce_dsp`, `juce_events`), `OpenShotLibrary.jucer` | dispositivos, drivers, mezcla, buffers, DSP. |
| **C++17** | `CMakeLists.txt:46` | estándar de compilación. |

- **Drivers de audio** (según `libopenshot/README.md:24`): ASIO, WASAPI,
  DirectSound, CoreAudio, iPhone Audio, ALSA, JACK y Android.
- JUCE está **vendored** en `JuceLibraryCode/` (no hay `find_package(JUCE)`).

---

## 5. Herramientas de build, bindings y testing

| Tecnología | Evidencia | Uso |
|---|---|---|
| **CMake** | `libopenshot/CMakeLists.txt:11` (`3.10...3.20`), `libopenshot-audio/CMakeLists.txt:27` (`3.1...3.20`) | sistema de compilación. |
| **SWIG 4.0** | `libopenshot/bindings/java/CMakeLists.txt:12` `find_package(SWIG 4.0 REQUIRED)` | generación de bindings Python/Ruby/Java. |
| **Catch2** | `libopenshot/CMakeLists.txt:221` `find_package(Catch2)`; `tests/catch2v2.h.in`, `catch2v3.h.in`, `catch_main.cpp` | tests unitarios del motor. |
| **pytest** | `openshot-qt/src/tests/test_*.py` | tests de interfaz. |
| **Doxygen** | `libopenshot/CMakeLists.txt:160` `find_package(Doxygen)` | documentación API C++. |
| **Sphinx** | `openshot-qt/doc/conf.py`, `index.rst` | documentación de usuario. |

---

## 6. Empaquetado e instaladores

| Tecnología | Evidencia | Plataforma |
|---|---|---|
| **cx_Freeze** | `openshot-qt/freeze.py:62` (`from cx_Freeze import setup, Executable`); CI `cx_Freeze==7.0.0` | congelar app (Windows/macOS). |
| **Inno Setup** | `installer/windows-installer.iss`, `isportable.iss` | instalador Windows. |
| **MSIX** | `installer/package_msix.ps1`, `openshot-msix-template.xml` | paquete MSIX (Windows). |
| **DMG (macOS)** | `installer/build-mac-dmg.sh`, `dmg-background.*` | imagen de disco macOS. |
| **AppImage** | opción `APPIMAGE_BUILD` en `libopenshot/CMakeLists.txt:69` | paquete Linux. |

---

## 7. Otras dependencias Python (openshot-qt)

Según `openshot-qt/.github/workflows/ci.yml` (líneas 23–24):

- `setuptools`, `wheel`
- `sentry-sdk` (telemetría de errores; ver `src/classes/sentry.py`)
- `cx_Freeze==7.0.0`, `distro`, `defusedxml`, `requests`, `certifi`,
  `chardet`, `urllib3`
- `python3-zmq` (cliente ZeroMQ en Python)

---

## 8. Resumen de tecnologías no presentes

| Tecnología | Resultado |
|---|---|
| **PySide2** | No aparece (solo PyQt5/PyQt6/PySide6). |
| **PyQt4** | No aparece. |
| **ONNX Runtime** | No aparece (ONNX se consume vía OpenCV DNN). |
| **UnitTest++** | No aparece como dependencia activa; los tests usan Catch2. |
| **Electron/JS para UI** | No aplica (la UI es Python/Qt). |

---

## 9. Correspondencia lenguaje ↔ fase del ciclo de vida

| Lenguaje/Tecnología | Runtime | Build | Test | Empaquetado |
|---|---|---|---|---|
| Python (openshot-qt) | ✔ | — | ✔ (pytest) | ✔ (cx_Freeze/setuptools) |
| C++ (libopenshot) | ✔ | ✔ | ✔ (Catch2) | ✔ (CMake install) |
| C++ (libopenshot-audio) | ✔ | ✔ | — | ✔ (CMake install) |
| C/ObjC++/Java (JUCE) | ✔ | ✔ | — | — |
| CMake | — | ✔ | ✔ (CTest) | ✔ |
| SWIG | — | ✔ (bindings) | — | — |
| Inno Setup / MSIX / DMG | — | — | — | ✔ |


