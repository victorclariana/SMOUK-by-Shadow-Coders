# FASE 7 — Análisis detallado de libopenshot-audio

> Mapa de código de la biblioteca de audio. Se distingue claramente el código
> desarrollado por OpenShot del código de JUCE (terceros) y del generado.

---

## 1. Visión general

- **Target CMake:** `add_library(openshot-audio SHARED ${JUCE_SOURCES})`
  (`CMakeLists.txt:167`); alias `OpenShot::Audio` (`CMakeLists.txt:298`).
- **Versión/SO:** `PROJECT_VERSION_FULL "1.0.0"`, `PROJECT_SO_VERSION 10`
  (`CMakeLists.txt:43-44`).
- **Estándar C++:** C++17 (`CMakeLists.txt:46-49`).
- **CMake mínimo:** 3.1...3.20 (`CMakeLists.txt:27`).
- **Licencia:** GPL-3.0-or-later (`CMakeLists.txt:13-24`).
- **Proyecto Projucer:** `OpenShotLibrary.jucer` (projectType `dll`, nombre
  `OpenShotAudio`).

---

## 2. Procedencia del código

| Procedencia | Archivos | Descripción |
|---|---|---|
| **OpenShot** | `src/Main.cpp`, `src/hex_version.cpp`, `CMakeLists.txt`, `include/*.in`, `cmake/*`, `OpenShotLibrary.jucer` | demo de prueba de sonido y sistema de compilación. |
| **JUCE (terceros vendored)** | `JuceLibraryCode/modules/` (7 módulos), `JuceLibraryCode/include_juce_*.cpp/.mm` | motor de audio (dispositivos, buffers, DSP, formatos). |
| **Generado (Projucer/CMake)** | `JuceLibraryCode/AppConfig.h`, `JuceHeader.h`, `include/*.h` (a partir de `*.in`) | cabeceras de configuración. |

- Los 7 módulos JUCE: `juce_audio_basics`, `juce_audio_devices`,
  `juce_audio_formats`, `juce_core`, `juce_data_structures`, `juce_dsp`,
  `juce_events` (`OpenShotAudio.h.in:18-24`).

---

## 3. API pública

- `include/OpenShotAudio.h.in` — cabecera principal; incluye `AppConfig.h` y los
  7 módulos JUCE; define `ProjectInfo` (nombre/versión).
- `include/JuceHeader.h.in` y `JuceHeader.h` — cabecera agregadora de JUCE.
- `include/AppConfig.h.in`/`AppConfig.h` — configuración de JUCE.
- El consumidor (`libopenshot`) incluye `OpenShotAudio.h`
  (`libopenshot/src/AudioDevices.h:18`, `src/Qt/AudioPlaybackThread.h:24`).

---

## 4. Inicialización y dispositivos

- `src/Main.cpp` es un **demo**: inicializa `juce::AudioDeviceManager`,
  lista los dispositivos disponibles y reproduce 5 tonos de prueba.
- Subclase `TestAudioDeviceManager : public juce::AudioDeviceManager`
  (`Main.cpp:44`) que registra los tipos de dispositivo:
  - Windows: **WASAPI** (shared/exclusive/sharedLowLatency), **DirectSound**,
    **ASIO** (`Main.cpp:56-60`).
  - macOS: **CoreAudio** (`Main.cpp:61`), **iOSAudio** (`Main.cpp:62`).
  - Linux: **ALSA**, **JACK** (`Main.cpp:64-65`).
  - Otros: **Bela**, **Oboe** (Android), **OpenSLES**, **Android**
    (`Main.cpp:63-68`).
- Evidencia adicional: `libopenshot/README.md:24` enumera ASIO, WASAPI,
  DirectSound, CoreAudio, iPhone Audio, ALSA, JACK y Android.
- `OpenShotLibrary.jucer:42` fija `JUCE_ASIO="1"` (ASIO habilitado).

---

## 5. Reproducción, mezcla, remuestreo y buffers

Estas operaciones viven principalmente en **JUCE** (módulos `juce_audio_basics`,
`juce_audio_devices`, `juce_dsp`):

- **Buffers:** `juce::AudioBuffer<float>` (`juce_audio_basics/buffers/`).
- **Mezcla:** `juce::MixerAudioSource` / combinación de buffers.
- **Remuestreo:** `juce::ResamplingAudioSource` (`juce_audio_basics`).
- **Dispositivos:** `juce::AudioDeviceManager`, `juce::AudioIODeviceType`
  (`juce_audio_devices/audio_io/`).

La lógica de nivel superior (cuándo leer, qué mezclar) la implementa
`libopenshot` en `src/AudioReaderSource.*`, `AudioBufferSource.*`,
`AudioResampler.*`, `AudioDevices.*` y `src/Qt/AudioPlaybackThread.*`.

---

## 6. Integración con libopenshot

- `libopenshot/src/CMakeLists.txt:238-242`:
  ```cmake
  if(NOT TARGET OpenShot::Audio)
    find_package(OpenShotAudio 1.0.0 REQUIRED)
  endif()
  target_link_libraries(openshot PUBLIC OpenShot::Audio)
  ```
- `libopenshot-audio` instala/exporta el target `OpenShot::Audio` y
  `OpenShotAudioConfig.cmake` (`CMakeLists.txt:341-377`), con
  `COMPATIBILITY AnyNewerVersion`.
- `libopenshot-audio/INSTALL.md:127` documenta `-DOpenShotAudio_ROOT=...`.

---

## 7. Sistema de compilación y código generado

- `CMakeLists.txt` compila los `JUCE_SOURCES` (agregadores `include_juce_*.cpp`
  + `.mm` para macOS/iOS) y `src/`.
- `cmake/Config.cmake.in` genera `OpenShotAudioConfig.cmake`.
- `cmake/Modules/` — módulos auxiliares de CMake.
- `hex_version.cpp` — genera el número de versión hexadecimal para `JuceHeader.h`
  (usado en CMake < 3.13).

---

## 8. Pruebas

- **No hay suite de tests unitarios propia** en este repositorio (solo
  `src/Main.cpp` como demo reproducible y `doc/openshot-audio-demo.1` como
  página de manual).
- La validación principal es el target de demo `openshot-audio-test-sound`
  (ver `libopenshot/INSTALL.md:223`).

---

## 9. Licencias y código de terceros

- `COPYING` (GPL v3, 33 KB) — licencia de libopenshot-audio.
- El código JUCE vendored tiene su propia licencia (JUCE es GPL/comercial; la
  combinación con GPL-3.0 de OpenShot es coherente).
- `.reuse`/SPDX no está presente aquí (a diferencia de `libopenshot`); la
  atribución está en cabeceras de archivo.

---

## 10. Nota de discrepancia menor

- `OpenShotLibrary.jucer:3` declara `version="0.2.1"` y `JuceHeader.h:46`
  `versionString = "0.2.1"` — esto es la **versión del proyecto Projucer/JUCE**,
  no la versión del componente (`1.0.0` en `CMakeLists.txt:43`). No es un
  conflicto de versión del producto.

---

## 11. Riesgos al modificar libopenshot-audio

- **ALTO:** cualquier cambio en la API pública (`OpenShotAudio.h`, target
  `OpenShot::Audio`) afecta a `libopenshot` y, en cadena, a `openshot-qt`.
- **MEDIO:** actualizar los módulos JUCE (vendored) puede romper la ABI y los
  backends nativos.
- **BAJO:** el `Main.cpp` de demo es independiente del producto.
