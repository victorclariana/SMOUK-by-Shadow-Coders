# FASE 8 — Inventario de dependencias

> Inventario real de dependencias, con el archivo que las declara. Cuando una
> versión no está fijada en los archivos analizados, se indica explícitamente.

---

## 1. Herramientas de compilación

| Dependencia | Repositorio | Finalidad | Archivo que la declara | Versión | Tipo |
|---|---|---|---|---|---|
| CMake | libopenshot | generar build | `CMakeLists.txt:11` (`3.10...3.20`) | ≥3.10 | Build |
| CMake | libopenshot-audio | idem | `CMakeLists.txt:27` (`3.1...3.20`) | ≥3.1 | Build |
| SWIG | libopenshot | generar bindings | `bindings/java/CMakeLists.txt:12` `find_package(SWIG 4.0 REQUIRED)` | ≥4.0 | Build |
| Compilador C/C++ | ambos | compilar | `libopenshot/INSTALL.md:166-170` (GCC/Clang; MSVC no soportado) | GCC/Clang | Build |
| MinGW/MSYS2 | ambos | build Windows | `libopenshot/doc/INSTALL-WINDOWS.md`; `libopenshot-audio/.github/workflows/ci.yml:12-21` | no fijada | Build |
| Doxygen | ambos | docs API | `libopenshot/CMakeLists.txt:160`; CI `doxygen` | no fijada | Build (docs) |
| Graphviz | libopenshot | diagramas Doxygen | CI `graphviz` | no fijada | Build (docs) |
| lcov | libopenshot | cobertura | CI `lcov` | no fijada | Build (tests) |
| cargo (Rust) | libopenshot | compilar resvg | CI `cargo` | no fijada | Build (resvg) |

- **C++17** es el estándar: `libopenshot/CMakeLists.txt:102`,
  `libopenshot-audio/CMakeLists.txt:46`.

---

## 2. Bibliotecas multimedia y nativas

| Dependencia | Repositorio | Finalidad | Archivo | Versión | Obligatoria |
|---|---|---|---|---|---|
| FFmpeg | libopenshot | decodificar/codificar | `src/CMakeLists.txt:435` (avcodec avdevice avformat avutil swscale; swresample/avresample) | no fijada | SÍ |
| libfdk-aac | libopenshot | códec AAC | CI `libfdk-aac-dev` | no fijada | opcional |
| Qt5/Qt6 | libopenshot | imágenes/composición/render | `INSTALL.md:204` `USE_QT6=AUTO\|ON\|OFF`; `src/CMakeLists.txt:400-418` | Qt5 o Qt6 | SÍ |
| ImageMagick++ | libopenshot | decodificar imágenes | `CMakeLists.txt:73` `ENABLE_MAGICK` | no fijada | opcional |
| OpenCV | libopenshot | detección/IA (DNN) | `CMakeLists.txt:74` `ENABLE_OPENCV` | ≥4.3 (ONNX) | opcional |
| Protobuf 3 | libopenshot | serialización CV | `CMakeLists.txt:74`; `src/*.proto`; CI `libprotobuf-dev` | 3 | opcional |
| Boost | libopenshot | soporte OpenCV | `CMakeLists.txt:74` | no fijada | opcional |
| ZeroMQ (libzmq) | libopenshot | logging pub/sub | `INSTALL.md:57`; `src/ZmqLogger.*`; CI `libzmq3-dev` | no fijada | SÍ |
| OpenMP (libomp) | libopenshot | paralelización | `INSTALL.md:63`; CI `libomp5 libomp-dev` | no fijada | opcional |
| babl | libopenshot | conversión de color | `src/CMakeLists.txt:549`; `ChromaKey.cpp` | no fijada | opcional |
| resvg | libopenshot | rasterizar SVG | `src/CMakeLists.txt:356`; CI `resvg v0.19.0` | v0.19.0 (CI) | opcional |
| Vulkan | libopenshot | benchmark | `examples/CMakeLists.txt:70` | no fijada | opcional |
| jsoncpp | libopenshot | JSON C++ | `thirdparty/jsoncpp/` (vendored) | vendored | SÍ |
| Catch2 | libopenshot | tests | `tests/`; CI `catch2_2.13.8` | 2.13.8 (CI) | tests |
| JUCE | libopenshot-audio | audio | `JuceLibraryCode/` (vendored) | vendored | SÍ |

---

## 3. Dependencias de audio (libopenshot-audio)

| Dependencia | Finalidad | Archivo | Versión |
|---|---|---|---|
| JUCE (7 módulos) | dispositivos/buffers/DSP | `JuceLibraryCode/modules/`, `OpenShotLibrary.jucer` | vendored |
| ALSA | backend Linux | `libopenshot-audio/.github/workflows/ci.yml:36` `libasound2-dev` | no fijada |
| WASAPI/DirectSound/ASIO | backends Windows | `src/Main.cpp:56-60`, `OpenShotLibrary.jucer:42` (`JUCE_ASIO=1`) | provistos por JUCE/OS |
| CoreAudio/iOSAudio | backends macOS | `src/Main.cpp:61-62` | provistos por OS |

---

## 4. Dependencias Python (openshot-qt)

| Dependencia | Finalidad | Archivo | Versión |
|---|---|---|---|
| Python 3 | runtime/app | `README.md:96` («3.0+») | 3.x (mínimo no fijado) |
| PyQt5 / PyQt6 / PySide6 | binding Qt | `src/qt_api.py:4-7`, `README.md:97` | no fijada |
| python3-zmq | cliente ZeroMQ | `.github/workflows/ci.yml:22` | no fijada |
| sentry-sdk | telemetría de errores | `ci.yml:23`; `src/classes/sentry.py` | no fijada |
| cx_Freeze | empaquetado | `ci.yml:24` (`cx_Freeze==7.0.0`); `freeze.py` | 7.0.0 |
| distro | detección de SO | `ci.yml:24` | no fijada |
| defusedxml | parseo XML seguro | `ci.yml:24` | no fijada |
| requests / certifi / chardet / urllib3 | HTTP | `ci.yml:24` | no fijadas |
| setuptools / wheel | empaquetado | `ci.yml:23` | no fijadas |
| Sphinx | documentación | `doc/conf.py` | no fijada |

---

## 5. Submódulos y código de terceros

| Dependencia | Repositorio | Finalidad | Archivo | Estado |
|---|---|---|---|---|
| godot-cpp | libopenshot | binding Godot | `.gitmodules`; `bindings/godot/` | declarado, **no inicializado** |
| jsoncpp | libopenshot | JSON C++ | `thirdparty/jsoncpp/` | vendored |
| JUCE | libopenshot-audio | audio | `JuceLibraryCode/` | vendored |

---

## 6. Observaciones de compatibilidad

- **Qt mayor:** `libopenshot` selecciona Qt6 si está disponible y CMake ≥3.16,
  si no Qt5 (`INSTALL.md:204`, `src/CMakeLists.txt:400-418`). La UI
  (`openshot-qt`) elige su binding Python independientemente
  (`OPENSHOT_QT_API`), pero el binding debe coincidir con la versión de Qt
  usada para compilar `libopenshot` (Qt5 vs Qt6).
- **Python:** el binding SWIG se compila contra una instalación de Python
  concreta (`PYTHON_INCLUDE_DIR`, `PYTHON_LIBRARY`); la versión de Python del
  runtime debe coincidir con la del binding.
- **FFmpeg:** no hay versión mínima fijada en los archivos; la aceleración HW
  requiere avcodec > 57.106 (`src/CMakeLists.txt:473`).
- **Riesgo:** el submódulo `godot-cpp` no inicializado no afecta a la
  compilación estándar (Godot es opcional/experimental), pero debe
  documentarse.

