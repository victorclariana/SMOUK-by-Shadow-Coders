# FASE 12 — Investigación: reencuadre automático (16:9 → 9:16)

> Evaluación de tecnologías para detectar el sujeto de interés y generar
> trayectorias de recorte editables en OpenShot.

---

## 1. Propiedades de Clip que permiten reencuadrar (verificado en C++)

En `libopenshot/src/Clip.h` y `Clip.cpp` existen, como **Keyframes**:

- `location_x` (`Clip.cpp:95`), `location_y` (`Clip.cpp:96`) — desplazamiento.
- `scale_x` (`Clip.cpp:91`), `scale_y` (`Clip.cpp:92`) — escala (1.0 por defecto).
- `gravity` (`GravityType`, `Clip.h:185`), `scale` (`ScaleType`, `Clip.h:186`),
  `anchor` (`AnchorType`, `Clip.h:187`).
- Serialización JSON: `location_x`, `location_y`, `scale_x`, `scale_y`,
  `gravity`, `scale` (`Clip.cpp:838, 987-989`) y lectura en `SetJsonValue`
  (`Clip.cpp:1099-1106`).
- `get_transform()` (`Clip.h:155`) aplica los keyframes de transformación.

**Conclusión clave:** el reencuadre se implementa **íntegramente** con
`location_x` + `scale_x`/`scale_y` como keyframes (más `gravity`/`anchor`), sin
modificar `libopenshot`. Para un recorte 9:16 de un 16:9:
- `scale_x = scale_y = altura_9:16 / altura_16:9` (escala uniforme).
- `location_x` animado para seguir al sujeto.

Existe el efecto `Crop` (`src/effects/Crop.*`) como alternativa, pero **escala +
posición** conserva resolución fuente al exportar vertical.

---

## 2. Tecnologías evaluadas

| Tecnología | Licencia | Mantenimiento | Comercial | Offline | Nota |
|---|---|---|---|---|---|
| MediaPipe (Face/BlazePose) | Apache-2.0 | Activo | sí | sí (envía métricas) | Python OK |
| Ultralytics YOLO (11/26) | **AGPL-3.0**/Enterprise | Activo | requiere Enterprise | sí | ONNX, CPU/GPU |
| InsightFace | código MIT; **modelos no comerciales** | Activo | **modelos no** | sí | Python OK |
| OpenCV DNN (YuNet/ONNX) | Apache-2.0 | Activo | sí | sí | ya en OpenShot |
| ByteTrack / BoT-SORT | MIT | Activo | sí | sí | sobre YOLO/OpenCV |
| UNISAL (saliencia) | MIT (código) | Bajo | sí | sí | PyTorch |
| SAM / SAM 2 | Apache-2.0 (código) | Activo | sí | sí | PyTorch/ONNX |
| AutoFlip (google/autoflip) | — | **repo 404** | — | — | descartado |
| PyAutoFlip | variable | poco mantenido | — | — | estudiar |
| OpenCV (KCF/MOSSE/CSRT) | Apache-2.0 | Activo | sí | sí | ya en OpenShot (`CVTracker`) |

### 2.1 Notas críticas

- **AutoFlip está descatalogado** (URL 404); no adoptar como dependencia.
- **Ultralytics AGPL-3.0:** integrar en app distribuida puede obligar a abrir el
  código o pagar Enterprise. Alternativa: modelos YOLO **exportados a ONNX**
  cargados con OpenCV DNN (evita el paquete), pero **los pesos YOLO tienen su
  propia licencia** (los de Ultralytics AGPL/comerciales).
- **InsightFace:** modelos del zoo **no comerciales**; requiere revisión legal.
- **MediaPipe:** Apache-2.0, sólido para caras/personas; envía métricas (se puede
  desactivar).
- **OpenShot ya trae OpenCV** (`CVObjectDetection`, `CVTracker` MOSSE/CSRT,
  `sort_filter` SORT+Kalman): reutilizar antes que añadir frameworks.

---

## 3. Pipeline de reencuadre propuesto

```
frame(s) → SubjectDetection (caras/personas/objetos + saliencia)
         → Tracking (ByteTrack/Kalman)
         → Selección del centro de interés (confianza + saliencia)
         → ReframePathGenerator (suavizado, sparse keyframes)
         → OpenShotTimelineAdapter (escribe location_x/scale_x/y en Clip)
```

- **Detección base:** OpenCV DNN (YuNet) o MediaPipe (BlazeFace/BlazePose);
  fallback a saliencia si no hay sujeto.
- **Seguimiento:** reutilizar `CVTracker`/`sort_filter` (Kalman + Hungarian) o
  ByteTrack; evita jitter.
- **Suavizado:** límite de velocidad horizontal + ventana deslizante; keyframes
  sólo en puntos de cambio.
- **Fallback:** centrar recorte o mantener último encuadre.
- **Confianza:** mostrar `conf` y permitir elegir/bloquear sujeto manualmente.

---

## 4. Overlay 9:16 en el visor (diseño, sin implementar)

- **Widget real:** `libopenshot/src/Qt/VideoRenderWidget` (`paintEvent`,
  `centeredViewport`). En Python, `VideoWidget` (`src/windows/video_widget.py`).
- **Overlay:** dibujar en `paintEvent` un rectángulo 9:16 **no exportado**.
  Geometría calculada respecto al viewport centrado (letterboxing) y al
  `devicePixelRatio`, sin píxeles fijos.
- **Geometría:** altura = altura visible del frame; anchura = altura × (9/16);
  centrado horizontal inicial; top/bottom coinciden con el frame.
- **Interacción:** arrastrar horizontalmente; distinguir interior/exterior
  (oscurecer exterior); guías de centro/tercios opcionales.
- **Conversión widget↔vídeo:** mapear posición del rectángulo a `location_x`
  normalizado considerando letterboxing y escala.
- **Sincronización:** señales `SeekSignal`/`previewFrameSignal` + clip seleccionado
  para leer/escribir keyframes.
- **Archivos a modificar:** `src/windows/video_widget.py` (o subclase/overlay),
  `src/windows/preview_thread.py`, servicio `VerticalPreviewOverlay`. **No**
  tocar `VideoRenderWidget.cpp` salvo necesidad de rendimiento.

---

## 5. Recomendación (resumen)

- **Adoptar:** OpenCV DNN (YuNet/ONNX) y/o MediaPipe; reutilizar `CVTracker`/
  `sort_filter`.
- **Estudiar:** ByteTrack/BoT-SORT, UNISAL, SAM 2 (solo si hace falta segmentación).
- **Descartar:** AutoFlip (desaparecido), InsightFace (modelos no comerciales),
  Ultralytics directo (AGPL) salvo Enterprise o ONNX con pesos de licencia clara.
