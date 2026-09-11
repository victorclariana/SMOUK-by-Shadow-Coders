# FASE 9 — Compilación y ejecución en Windows

> Análisis de cómo debería compilarse/ejecutarse esta versión en Windows, **sin
> compilar ni instalar nada**. Se comparan documentación, CMake, CI y scripts.

---

## 1. Requisitos comprobados

| Requisito | Evidencia | Comentario |
|---|---|---|
| CMake ≥3.10 (libopenshot) | `libopenshot/CMakeLists.txt:11` | obligatorio |
| CMake ≥3.1 (libopenshot-audio) | `libopenshot-audio/CMakeLists.txt:27` | obligatorio |
| C++17 | `libopenshot/CMakeLists.txt:102` | obligatorio |
| Compilador MinGW (GCC) / MSYS2 | `libopenshot/doc/INSTALL-WINDOWS.md:26-27` | **MSVC no soportado** (`INSTALL.md:170`) |
| SWIG ≥4.0 | `bindings/java/CMakeLists.txt:12` | para bindings |
| Python 3 | `libopenshot/INSTALL.md:82` | para bindings + UI |
| Qt5 o Qt6 | `libopenshot/INSTALL.md:204` (`USE_QT6`) | obligatorio |
| FFmpeg (avcodec/avdevice/avformat/avutil/swscale) | `src/CMakeLists.txt:435` | obligatorio |
| libopenshot-audio 1.0.0 | `src/CMakeLists.txt:240` | obligatorio |
| ZeroMQ (libzmq) | `INSTALL.md:57`; CI | obligatorio (logging) |
| OpenCV / Protobuf / Boost | `CMakeLists.txt:74` (opcional) | para IA/CV |
| babl | `src/CMakeLists.txt:549` (opcional) | color |
| resvg | `src/CMakeLists.txt:356` (opcional) | SVG |

## 2. Requisitos no verificados

- **Versión exacta de FFmpeg** — no fijada en los archivos analizados.
- **Versión exacta de Qt** (solo se sabe Qt5/Qt6).
- **Versión exacta de Python** (solo «3.0+» en `README.md`).
- **Versión exacta de ZeroMQ / OpenCV / babl** — no fijadas.
- **Windows SDK / DirectX SDK** — la doc menciona `DXSDK_DIR`, pero el CI
  actual no lo usa explícitamente (JUCE puede prescindir de ello en MinGW64).

## 3. Orden esperado de compilación

1. **libopenshot-audio** (primero, porque libopenshot lo consume):
   ```text
   cmake -B build -S . -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=...
   cmake --build build
   cmake --install build
   ```
2. **libopenshot** (depende de libopenshot-audio):
   ```text
   cmake -B build -S . -G "MinGW Makefiles" -DCMAKE_INSTALL_PREFIX=... \
     -DOpenShotAudio_ROOT=[libopenshot-audio/build] \
     -DPYTHON_INCLUDE_DIR=... -DPYTHON_LIBRARY=... -DUSE_QT6=ON|OFF
   cmake --build build
   cmake --build build --target test   (opcional)
   cmake --install build
   ```
3. **openshot-qt** (no requiere compilación; usa los bindings instalados):
   ```text
   PYTHONPATH=[libopenshot]/build/bindings/python python src/launch.py
   ```

Evidencia: `libopenshot/doc/INSTALL-WINDOWS.md:319-368`,
`libopenshot/README.md:119-130`.

## 4. Dependencias necesarias

Ver `docs-analysis/07-dependencies.md`. Para Windows, la instalación se realiza
preferentemente vía **MSYS2/MinGW64** (`pacman`), como hace el CI
(`libopenshot-audio/.github/workflows/ci.yml:12-21` instala
`mingw-w64-x86_64-gcc`, `-pkgconf`, `-make`).

## 5. Herramientas necesarias

CMake, MinGW (gcc/g++/mingw32-make), MSYS2, SWIG, Python 3, Doxygen (docs,
opcional), y las bibliotecas nativas (FFmpeg, Qt, ZeroMQ, etc.).

## 6. Posibles incompatibilidades

1. **MSVC:** la documentación y `INSTALL.md:170` indican que MSVC **no está
   soportado**; se debe usar MinGW/MSYS2.
2. **Qt5 vs Qt6:** `libopenshot` y el binding Python de la UI deben coincidir
   en la versión mayor de Qt.
3. **Python:** el binding SWIG se compila contra una versión concreta de
   Python; el runtime debe usar la misma.
4. **Submódulo `godot-cpp` no inicializado** (`libopenshot/.gitmodules`): no
   afecta a la compilación estándar, pero fallará si se intenta el binding Godot.
5. **Documentación desactualizada** (ver §10).

## 7. Propuesta de compilación (para una fase posterior)

- Usar un entorno **MSYS2 MinGW64** con las dependencias instaladas por
  `pacman`, replicando el `libopenshot/.gitlab-ci.yml` (jobs Windows x64/x86).
- Generar bindings Python con `-DPYTHON_MODULE_PATH=python` y SWIG ≥4.0.
- Instalar `libopenshot-audio` y `libopenshot` en un prefijo común y exponer
  los bindings a `openshot-qt` mediante `PYTHONPATH`.
- Empaquetar la UI con `cx_Freeze` (`freeze.py`) e Inno Setup/MSIX
  (`installer/`).

## 8. Comandos propuestos (NO ejecutados)

```text
# libopenshot-audio
cmake -B build -S . -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=C:/openshot/install
cmake --build build --parallel
cmake --install build

# libopenshot
cmake -B build -S . -G "MinGW Makefiles" \
  -DCMAKE_INSTALL_PREFIX=C:/openshot/install \
  -DOpenShotAudio_ROOT=C:/openshot/libopenshot-audio/build \
  -DUSE_QT6=ON \
  -DPYTHON_INCLUDE_DIR=<python/include> -DPYTHON_LIBRARY=<libpython.a>
cmake --build build --parallel
cmake --install build

# openshot-qt (sin compilar)
set PYTHONPATH=C:/openshot/libopenshot/build/bindings/python
python src/launch.py
```

## 9. Archivos utilizados como evidencia

- `libopenshot/doc/INSTALL-WINDOWS.md` — guía de compilación Windows.
- `libopenshot/INSTALL.md` — dependencias y flags.
- `libopenshot/CMakeLists.txt`, `libopenshot/src/CMakeLists.txt` — flags y targets.
- `libopenshot-audio/CMakeLists.txt` — target de audio.
- `libopenshot/.github/workflows/ci.yml` — CI Linux (dependencias).
- `libopenshot-audio/.github/workflows/ci.yml` — CI con MSYS2 (Windows).
- `libopenshot/.gitlab-ci.yml` — CI Windows x64/x86 (MinGW).
- `openshot-qt/.github/workflows/ci.yml` — CI UI.
- `openshot-qt/freeze.py`, `installer/` — empaquetado.

---

## 10. Discrepancias detectadas (documentación vs. CI/scripts actuales)

1. **Framework de tests:** `INSTALL-WINDOWS.md:68` menciona **UnitTest++**, pero
   el código y el CI actuales usan **Catch2** (`tests/`, `ci.yml:89-97`).
2. **Versiones antiguas en la doc:** `INSTALL-WINDOWS.md` referencia Python 3.3,
   CMake 2.8, MSYS 1.0, swigwin-2.0.4, Windows 7/8, OpenCV 4.3.0; el CI actual
   usa MSYS2/MinGW64, Windows 2022, Catch2 2.13.8, resvg v0.19.0.
3. **OpenCV en CI:** se instala vía paquete (`libopencv-dev`) en Linux; en
   Windows la doc lo compila desde fuente (`INSTALL-WINDOWS.md:253-272`).
4. **`UNIT_TEST_DIR`/`DL_DIR`/`SNDFILE_DIR`/`DXSDK_DIR`:** variables de entorno
   de la doc antigua; no aparecen en los scripts de CI actuales.

**Conclusión:** `doc/INSTALL-WINDOWS.md` está parcialmente desactualizada; la
referencia fiable para esta versión concreta es el **`.gitlab-ci.yml`** (jobs
Windows x64/x86) y los **workflows de GitHub Actions**, que reflejan el estado
actual del código (Catch2, MSYS2/MinGW64, C++17).

