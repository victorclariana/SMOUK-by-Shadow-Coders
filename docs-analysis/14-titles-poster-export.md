# FASE 14 — Títulos, logotipo, portada y exportación vertical

> Estrategias de títulos, capa de logo, captura de portada y exportación.

---

## 1. Títulos identificativos: comparativa de estrategias

### ESTRATEGIA A — SVG editable (RECOMENDADA)

- **Evidencia:** OpenShot ya usa títulos SVG: `src/titles/*.svg` (49 plantillas)
  y `src/windows/title_editor.py` (`load_svg_template`, `save_and_reload`).
  El motor renderiza SVG vía `QtImageReader`/`QtSvg`/resvg.
- **Cómo:** generar dinámicamente un SVG transparente con formas + texto desde
  Python; un único clip SVG por título; regenerar el SVG al cambiar los datos.
- **Ventajas:** totalmente editable (texto, formas, colores, tipografía, márgenes,
  posición, duración, entrada/salida); compatible con el editor de títulos;
  reutiliza el pipeline existente; sin códec alpha.
- **Inconvenientes:** renderizado SVG por frame (coste CPU); animaciones complejas
  limitadas (usar keyframes de OpenShot).

### ESTRATEGIA B — MOV con canal alpha

- **Cómo:** importar un vídeo MOV pre-renderizado con alpha (p. ej. ProRes 4444,
  PNG/Qt Animation) en pista superior.
- **Ventajas:** animaciones complejas ya renderizadas; rendimiento de
  decodificación.
- **Inconvenientes:** el texto **no es editable** tras renderizar; códecs alpha
  limitados y soporte variable en FFmpeg/libopenshot en Windows; tamaño de archivo
  grande; plantillas menos reutilizables; fiabilidad de transparencia dudosa.
- **Códecs alpha en FFmpeg:** ProRes 4444 (compatible), VP9/WebM (alpha parcial),
  Qt Animation/PNG (secuencia). La transparencia al exportar puede no conservarse
  con H.264 (sin alpha), lo que obliga a compositar antes.

### Recomendación

**Adoptar Estrategia A (SVG editable)** como principal, por integración, edición
posterior y fiabilidad en Windows. La Estrategia B solo como alternativa para
animaciones complejas puntuales, aceptando que el texto no será editable.

---

## 2. Logotipo de compañía (capa superior)

- Reutilizar **clip de imagen PNG** en pista superior (transparencia ya soportada:
  `Frame`/`Clip` usan `QImage` RGBA; `apply_background` en `Clip.cpp`).
- Propiedades a fijar: `location_x`/`location_y` (esquina), `scale_x`/`scale_y`,
  `gravity` (p. ej. `GRAVITY_BOTTOM_RIGHT`), duración, activar/desactivar.
- Configurable en preferencias (`smouk-logo-*`); vista previa inmediata.

---

## 3. Portada PNG (PosterExportService)

- **Obtener el frame compuesto por el motor:** `timeline.GetFrame(n)` devuelve el
  `openshot::Frame` ya compuesto (todas las capas). Desde Python:
  `frame = timeline.GetFrame(frame_number)`.
- **Extraer imagen:** `frame.GetImage()` devuelve `QImage` (`Frame.cpp:132`);
  guardar con `QImage::save("portada.png")` (PNG con alpha si procede).
  Alternativa: `ImageWriter` (ImageMagick), pero `QImage::save` es más simple.
- **Frame exacto:** usar el frame del playhead (1-based) del proyecto.
- **Tamaño:** el del perfil vertical (1080×1920). Verificar `frame.GetWidth()/
  GetHeight()` y pixel aspect ratio.
- **Color:** `QImage` en RGBA; convertir si es necesario.
- **Directorios y nombre:** configurable en preferencias; evitar sobreescritura.

---

## 4. Exportación vertical

### 4.1 Perfiles y presets existentes (verificado)

- **Perfiles** en `src/profiles/definitions/*.json` (360, ATSC, BD, DVD, NTSC,
  PAL, VGA...). No hay un perfil 1080×1920 por defecto → **crear uno**.
- **Presets verticales ya existen:** `src/presets/tiktok.xml`,
  `instagram_reels.xml`, `youtube_shorts.xml`, `snapchat.xml` — presets 9:16
  sociales. También `format_mp4_x264*.xml` (H.264) y variantes HW
  (`*_hw.xml`, `*_nv.xml`, `*_qsv.xml`, `*_vtab.xml`, `*_dx.xml`).

### 4.2 Estrategia

- **No crear exportador nuevo:** ampliar/configurar el sistema existente.
- **Crear un perfil** `Vertical_1080x1920` (o usar presets existentes) y un
  **preset SMOUK** (`smouk_vertical.xml`) basado en `format_mp4_x264.xml` con
  1080×1920, H.264 + AAC, bitrate/CRF configurables.
- **Aceleración HW opcional:** variantes HW ya existentes (QSV/NVENC/D3D11).
- **Verificación post-export:** resolución, fps, audio, duración, presencia de
  capas (títulos/logo/subtítulos), y prevención de sobreescritura (nombre
  derivado del proyecto + timestamp).
- **Cancelación/progreso/logs:** patrón de worker + progreso ya usado por la
  exportación actual (`export.py`).

---

## 5. Resumen de archivos implicados

- Títulos: reutilizar `src/titles/`, `title_editor.py`, `QtImageReader` (SVG).
- Logo: clip PNG + keyframes de Clip (sin código C++ nuevo).
- Portada: `timeline.GetFrame` + `frame.GetImage` + `QImage::save`.
- Exportación: crear perfil + preset vertical; reutilizar `export.py` y
  `FFmpegWriter`.
