# FASE 6 — Análisis detallado de libopenshot

> Mapa de código del motor C++. Se indica ruta, clases, responsabilidad, flujo
> de datos, dependencias, API expuesta, uso desde Python y riesgo al modificar.

---

## 1. Visión general

- **Target CMake:** `add_library(openshot SHARED)` (`src/CMakeLists.txt:187`).
- **Versión/SO:** `PROJECT_VERSION_FULL "1.0.0"`, `PROJECT_SO_VERSION 31`
  (`CMakeLists.txt:27-28`).
- **Dependencias obligatorias clave:** FFmpeg, Qt5/Qt6, `OpenShotAudio 1.0.0`,
  JSON (jsoncpp), OpenMP, ZeroMQ (ver `src/CMakeLists.txt`).
- **Licencia:** LGPL-3.0-or-later (`CMakeLists.txt:9`, `README.md`).

---

## 2. Núcleo: Timeline, Clip, Frame, FrameMapper

| Clase | Archivo | Herencia | Responsabilidad |
|---|---|---|---|
| `Timeline` | `src/Timeline.h/.cpp` | `TimelineBase`, `ReaderBase` | agregar clips/frames, composición multi-capa, `GetFrame(n)`, `SetJson`/`Json`. |
| `TimelineBase` | `src/TimelineBase.h/.cpp` | — | interfaz genérica de timeline. |
| `Clip` | `src/Clip.h/.cpp` | `ClipBase`, `ReaderBase` | representa un clip en pista; `CreateReader`, `GetFrame`. |
| `ClipBase` | `src/ClipBase.h/.cpp` | — | base de clips/efectos (keyframes, propiedades). |
| `Frame` | `src/Frame.h/.cpp` | — | pixel + audio de un instante; `GetImage`/`AddImage`/`AddAudio`/`Display`. |
| `FrameMapper` | `src/FrameMapper.h/.cpp` | `ReaderBase` | mapea frames de un reader a un rango/velocidad (time-mapping). |
| `FrameScope` | `src/FrameScope.h/.cpp` | — | muestreo por región (formas de onda/histogramas/vectorescopio). |

### Flujo de datos de un frame

```
Timeline::GetFrame(n)
  └─> Clip::GetFrame(n) → FrameMapper → ReaderBase (FFmpegReader/QtImageReader)
  └─> aplicar efectos (EffectBase) y transiciones
  └─> composición de capas
  └─> Cache (CacheMemory/CacheDisk)
```

---

## 3. Readers y Writers

| Clase | Archivo | Herencia | Uso |
|---|---|---|---|
| `ReaderBase` | `src/ReaderBase.h/.cpp` | — | base de lectores (Open/Close/GetFrame/GetFrameCount). |
| `FFmpegReader` | `src/FFmpegReader.h/.cpp` | `ReaderBase` | decodificar vídeo/audio/imágenes vía FFmpeg. |
| `WriterBase` | `src/WriterBase.h/.cpp` | — | base de escritores (Open/WriteFrame/Close). |
| `FFmpegWriter` | `src/FFmpegWriter.h/.cpp` | `WriterBase` | codificar flujo de salida vía FFmpeg. |
| `ImageReader`/`ImageWriter` | `src/ImageReader.*`, `ImageWriter.*` | — | imágenes (ImageMagick). |
| `QtImageReader`/`QtTextReader`/`QtHtmlReader` | `src/Qt*.cpp/.h` | `ReaderBase` | imágenes/SVG/texto/HTML vía Qt. |
| `ChunkReader`/`ChunkWriter` | `src/ChunkReader.*`, `ChunkWriter.*` | — | lectura/escritura por fragmentos. |
| `DummyReader` | `src/DummyReader.*` | `ReaderBase` | fuente sin contenido (pruebas/relleno). |
| `CameraCaptureReader`/`ScreenCaptureReader`/`WaylandScreenCaptureReader` | `src/*CaptureReader.*` | `ReaderBase` | captura de cámara/pantalla. |

---

## 4. Caché

- `CacheBase` (`src/CacheBase.h/.cpp`) — base común.
- `CacheMemory` (`src/CacheMemory.*`) — caché en RAM.
- `CacheDisk` (`src/CacheDisk.*`) — caché en disco.
- `VideoCacheThread` (`src/Qt/VideoCacheThread.*`) — hilo de precarga de frames.

---

## 5. Keyframes y animación

- `Keyframe` (clase, en `src/KeyFrame.h/.cpp`) — keyframe (frame#, valor,
  interpolación).
- `AnimatedCurve` / `AnimatedCurveNode` (`src/AnimatedCurve.*`) — curva
  interpolada (Bézier, lineal, constante).
- `Point` (`src/Point.*`), `Coordinate` (`src/Coordinate.*`),
  `Fraction` (`src/Fraction.*`) — tipos geométricos/matemáticos.
- `Color` (`src/Color.*`) — color animable en el tiempo.

---

## 6. Efectos

- Base: `EffectBase : public ClipBase` (`src/EffectBase.h:56`);
  `EffectInfo` (`src/EffectInfo.h/.cpp`) lista los efectos; `Effects.h`
  enumera IDs.
- **Efectos de vídeo** (`src/effects/`): Blur, Brightness, ChromaKey, ColorGrade,
  ColorMap, ColorShift, Crop (+CropHelpers), Deinterlace, DenoiseImage,
  Displace, FilmGrain, Glow, Hue, LensFlare, Mask, Negate, ObjectDetection,
  ObjectMask, Outline, Pixelate, Saturation, Shadow, Sharpen, Shift,
  SphericalProjection, Stabilizer, Timer, Tracker, Wave, AnalogTape, Bars,
  BeatSync, Caption, AudioVisualization.
- **Efectos de audio** (`src/audio_effects/`): Compressor, Delay, Distortion,
  Echo, Expander, Noise, ParametricEQ, Robotization, STFT, Whisperization.

---

## 7. Audio

- `AudioDevices` (`src/AudioDevices.*`) — consulta de dispositivos (usa
  `OpenShotAudio.h`).
- `AudioResampler` (`src/AudioResampler.*`) — remuestreo.
- `AudioReaderSource` / `AudioBufferSource` — fuentes de audio para JUCE.
- `AudioRecorder` (`src/AudioRecorder.*`) — grabación.
- `AudioWaveformer` (`src/AudioWaveformer.*`) — forma de onda.
- `AudioLocation.h` / `ChannelLayouts.h` — metadatos de canales.

---

## 8. Reproducción (capa Qt)

- `PlayerBase` (`src/PlayerBase.h/.cpp`) — base del reproductor.
- `RendererBase` (`src/RendererBase.h/.cpp`) — base del renderizador.
- `QtPlayer` (`src/QtPlayer.h/.cpp`) — reproductor Qt; `SetQWidget(uintptr_t)`
  para enlazar el widget de la UI (`QtPlayer.h:92`).
- Hilos Qt: `AudioPlaybackThread`, `VideoPlaybackThread`, `VideoCacheThread`.
- `VideoRenderer`, `VideoRenderWidget`, `PlayerPrivate`, `PlayerDemo`.

---

## 9. Serialización JSON

- `Json.h`/`Json.cpp` — lectura/escritura JSON con `jsoncpp` (vendored en
  `thirdparty/jsoncpp/`).
- Las clases del motor implementan `SetJson(...)`/`Json()`/`JsonValue()`.

---

## 10. Excepciones, logging, threading, memoria

- **Excepciones:** `src/Exceptions.h`.
- **Logging:** `ZmqLogger` (`src/ZmqLogger.*`) vía ZeroMQ; `CrashHandler`.
- **Threading:** `ProcessingController.h`, hilos Qt (`src/Qt/`), `std::mutex`
  en clases (p. ej. `Clip.h:91`).
- **Memoria:** `MemoryTrim.*` y cachés.

---

## 11. Aceleración por hardware

- `USE_HW_ACCEL` (`CMakeLists.txt:76`) y `HAVE_HW_ACCEL`
  (`src/CMakeLists.txt:473-475`).
- Detección en `FFmpegReader.cpp` (decodificación) y `FFmpegWriter.cpp`
  (codificación): NVDEC/NVENC, QSV, VA-API, D3D9/D3D11, VTB.
- Benchmark Vulkan opcional (`ENABLE_VULKAN_BENCHMARK`).

---

## 12. Visión por computador y Protobuf

- OpenCV (`ENABLE_OPENCV`): `CVObjectDetection`, `CVObjectMask`,
  `CVStabilization`, `CVTracker`, `TrackedObjectBase`, `TrackedObjectBBox`.
- Algoritmos SORT/Kalman en `src/sort_filter/`.
- ONNX vía `cv::dnn::readNetFromONNX` (`CVObjectDetection.cpp:230`).
- Protobuf: `objdetectdata.proto`, `stabilizedata.proto`, `trackerdata.proto`.

---

## 13. Bindings Python (SWIG)

- **Archivo SWIG:** `bindings/python/openshot.i` → módulo `openshot`.
- Genera `openshot.py` + `_openshot` (extensión nativa).
- Expone clases C++ (`Timeline`, `Clip`, `Frame`, `FFmpegReader`,
  `FFmpegWriter`, efectos, etc.) y `juce::AudioBuffer<float>`.
- Uso típico desde Python (`openshot-qt/src/classes/timeline.py`):
  `openshot.Timeline(w, h, openshot.Fraction(num, den), sr, ch, layout)`.

---

## 14. Tests

- `tests/` — ~65 archivos `*.cpp` con **Catch2** (`catch2v2.h.in`,
  `catch2v3.h.in`, `catch_main.cpp`).
- Cubren prácticamente cada clase (Timeline, Clip, Frame, effects, readers, etc.).

---

## 15. Código específico de Windows (libopenshot)

- `CMakeLists.txt:106-108` define la propiedad `WIN32`.
- `src/CMakeLists.txt:676-687` copia `libopenshot-audio.dll` al directorio de
  tests (Windows).
- Drivers de audio JUCE: WASAPI, DirectSound, ASIO (`README.md:24`).
- Build con MinGW/MSYS2 (`doc/INSTALL-WINDOWS.md`); MSVC no soportado
  (`INSTALL.md:170`).

---

## 16. Riesgos al modificar libopenshot

- **ALTO:** Timeline/Clip/Frame (núcleo), FFmpegReader/Writer (codificación),
  cachés, serialización, bindings SWIG (cualquier cambio de API afecta a
  `openshot-qt`), audio (sincronización).
- **MEDIO:** efectos concretos (autocontenidos), `Profiles`, utilidades.
- Cualquier cambio en `openshot.i` requiere regenerar bindings y recompilar.

