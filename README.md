# SMOUK by Shadow Coders

SMOUK es una adaptación de OpenShot para transformar de forma asistida vídeos
horizontales (16:9) en piezas verticales (9:16). Conserva el motor multimedia,
la línea de tiempo y el flujo de exportación de OpenShot, y añade un flujo de
trabajo especializado para verticalización.

## Objetivo final

El programa permitirá importar un vídeo horizontal y preparar una versión
vertical lista para publicar. El flujo final previsto incluye:

- detección y segmentación de cambios de plano;
- reencuadre automático de cada plano, priorizando rostros, personas y otras
  zonas de interés, con corrección manual;
- generación de subtítulos sincronizados en catalán y creación del SRT
  intermedio;
- capas configurables para títulos identificativos, branding y logotipo;
- una guía visual 9:16 sobre el visor para ajustar el encuadre;
- exportación del vídeo vertical y de un póster PNG de un fotograma elegido.

La interfaz se desarrolla en `openshot-qt` (Python/Qt). Los motores
`libopenshot` y `libopenshot-audio` siguen proporcionando edición,
reproducción, audio y renderizado.

## Estado actual

Estamos en una fase inicial de desarrollo. La investigación técnica y el plan
por fases están en [docs-analysis](docs-analysis/README.md). El dock
`Verticalization` ya existe como estructura visual; sus automatizaciones aún
no están conectadas.

## Versiones y cambios

Usamos versiones `0.0.x` durante esta etapa inicial. Cada cambio funcional o
de interfaz de SMOUK incrementa `x` y debe añadirse a este historial.

### 0.0.1

- Se creó la base del proyecto SMOUK sobre OpenShot, junto con el lanzador de
  desarrollo para Windows/MSYS2.
- Se documentó la arquitectura, las dependencias, los puntos de integración y
  la propuesta técnica de verticalización.
- Se añadió el esqueleto del dock `Verticalization`, con sus secciones de flujo
  previstas.
- Se añadió un parche de compatibilidad de `libopenshot` para FFmpeg 9.
- La cabecera de la aplicación muestra `SMOUK by Shadow Coders 0.0.1`,
  preservando el nombre de proyecto y el perfil entre corchetes.
- Se eliminó el menú superior `SMOUK`; el dock se abre desde
  `View` → `Docks` → `Verticalization`.

### 0.0.2

- Se añadió la guía visual de encuadre vertical sobre el visor, con zonas
  exteriores atenuadas y guías de tercios.
- La guía se dibuja únicamente en la interfaz y no forma parte del vídeo
  exportado.

### 0.0.3

- El proyecto continúa editándose en 16:9; ya no se cambia a vertical desde
  el dock.
- Se añadieron los perfiles de salida SMOUK disponibles: 1080×1350 (4:5) y
  1080×1920 (9:16), ambos a 25 o 30 fps.
- Se añadió un deslizador de encuadre horizontal para el clip seleccionado.
  Sin `Keyframes`, fija la posición en todo el plano; con `Keyframes`, la
  guarda en el fotograma actual.
- La guía del visor cambia automáticamente entre 4:5 y 9:16 según el perfil
  de salida seleccionado.

### 0.0.4

- Se añadió el renderizador vertical SMOUK al flujo de exportación.
- El renderizador crea una timeline temporal con el perfil seleccionado,
  convierte los clips 16:9 a relleno por recorte y transforma sus posiciones
  horizontales para que el resultado coincida con la guía blanca del visor.
- El proyecto de edición 16:9 no se modifica durante la exportación.

### 0.0.5

- Se añadió el botón `Export vertical video` dentro de la sección `Export` del
  dock `Verticalization`.
- Este botón envía el preset seleccionado directamente al renderizador SMOUK,
  evitando que la exportación normal vuelva a usar el lienzo 16:9.

### 0.0.6

- Se añadió una primera detección de cambios de plano con el filtro `scene` de
  FFmpeg, usando un umbral inicial de 0.30.
- El análisis permite elegir un archivo externo, muestra los timecodes de los
  cortes detectados y no importa ni modifica todavía la timeline.

### 0.0.7

- Se redujo el umbral inicial de detección FFmpeg de 0.30 a 0.20 para capturar
  cortes más sutiles, incluido el detectado alrededor de 00:19.8 en el vídeo
  de validación.
- Se añadió `Slice selected timeline clip (keep both sides)`, que inserta los
  cortes detectados en el clip seleccionado conservando ambos lados.

### 0.0.8

- La sección Shot Detection se simplificó a un único botón:
  `Detect and slice timeline videos`.
- Analiza todos los clips de vídeo de la timeline con FFmpeg y aplica los
  cortes automáticamente con `Keep Both Sides`, sin cargar archivos ni
  seleccionar clips manualmente.
- Añade una barra de progreso por clips procesados y un resumen final de
  cortes insertados o errores encontrados.

### 0.0.9

- El deslizador Horizontal framing se sincroniza con el plano seleccionado:
  vuelve al centro en planos sin ajuste y recupera su posición guardada en
  planos ya reencuadrados.
- El vídeo se desplaza en tiempo real mientras se arrastra el control.
- Se amplió el handle del deslizador para facilitar su agarre.

### 0.0.10

- Se corrigió el renderizador vertical para aplicar el perfil completo de
  salida (dimensiones, FPS y relación de aspecto) a la timeline temporal antes
  de aplicar el recorte de clips 16:9.

### 0.0.11

- Se corrigió la exportación vertical para localizar las dimensiones del medio
  en la tabla de archivos del proyecto cuando el clip solo contiene `file_id`.
  Así, los clips 16:9 reciben realmente `Scale Crop` y el resultado contiene
  el encuadre de la guía blanca, sin la imagen horizontal completa.
- El reconocimiento de clips 16:9 usa su relación de visualización, por lo que
  también se recortan correctamente fuentes anamórficas 1440×1080 marcadas
  como 16:9.
- La exportación iniciada desde el dock fuerza un códec de audio compatible
  con MP4 (AAC cuando está disponible), evitando que un códec heredado del
  preset bloquee la ventana de renderizado.

### 0.0.12

- El diálogo abierto desde `Export vertical video` conserva la última carpeta
  de exportación usada. Los ajustes guardados del proyecto ya no la sustituyen
  por una ruta antigua de la carpeta personal.

### 0.0.13

- Se corrigió el motor `libopenshot` para FFmpeg 7+: ahora consulta el formato
  de muestra soportado por el códec de audio. Esto permite abrir AAC con su
  formato `fltp` y exportar MP4 con audio.
- Mientras se reconstruye el motor en desarrollo, el diálogo SMOUK utiliza
  `libopus`, que sí acepta el formato de muestra actual y evita bloquear la
  exportación con audio.

### 0.0.14

- Al mostrarse el dock `Verticalization`, se activa por defecto `Show the
  9:16 guide in the viewer` para que el encuadre de exportación sea visible.

### 0.0.15

- Al ocultar o cerrar el dock `Verticalization`, se desactiva la guía 9:16 y
  desaparece del visor.

### 0.0.16

- Se añadió `Auto reframe timeline clips`: detecta la cara principal de cada
  plano con YuNet (OpenCV DNN), la sigue con CSRT y crea keyframes horizontales
  suavizados y editables. El análisis se ejecuta localmente y sin red.

### 0.0.17

- Se corrigió el seguimiento CSRT de OpenCV 5: YuNet entrega coordenadas
  flotantes y el tracker requiere píxeles enteros. Si el tracker no está
  disponible, el reencuadre sigue usando las detecciones de cara.

### 0.0.18

- Se añadió la segunda capa de reencuadre automático: MediaPipe Face y Pose se
  usan como respaldo de YuNet/CSRT cuando no hay una cara detectable. Prioriza
  el centro de la cara y, si no existe, el punto medio de los hombros o la
  nariz; todo se procesa localmente.
- Los planos reencuadrados automáticamente se identifican en la timeline con
  una insignia azul `AI`. Sus posiciones siguen siendo keyframes nativos y
  editables de `location_x`.
- MediaPipe se activa automáticamente cuando está instalado en un Python
  compatible; si no lo está, YuNet/CSRT continúa funcionando sin interrupción.

### 0.0.19

- Se añadió YOLO11n en formato ONNX, ejecutado localmente con OpenCV DNN y sin
  PyTorch. Cuando YuNet no detecta una cara, el reencuadre puede seguir una
  persona u objeto COCO relevante —vehículos, animales, deporte o pantallas—.
- El objeto se selecciona por confianza, prioridad semántica y tamaño visible;
  su centro se transforma en los mismos keyframes horizontales editables.

### 0.0.20

- Se corrigió el inicializador de YOLO: el nombre interno del dock impedía
  crear el detector y hacía fallar todos los clips antes del análisis.

### 0.0.21

- Los cortes detectados por FFmpeg se ajustan al FPS nativo de cada vídeo y no
  al FPS del proyecto SMOUK. Así, un vídeo de 25 fps en una timeline de 30 fps
  se corta en su límite real de fotograma, sin arrastrar un frame del plano
  siguiente al clip anterior.
- La timeline 16:9 y el preset vertical de exportación siguen siendo
  independientes: no se cambia el FPS creativo del proyecto al detectar o
  cortar planos.

### 0.0.22

- La disposición de la interfaz se guarda al cerrar y también como checkpoint
  durante el trabajo: tras mover o redimensionar la ventana o los docks, y al
  menos cada cinco segundos. Así se recuperan la posición y tamaño del visor,
  timeline y paneles tras un cierre inesperado.

### 0.0.23

- El reencuadre automático es ahora deliberadamente conservador. Para cada
  plano aplica como norma un encuadre fijo basado en la posición mediana del
  sujeto; solo crea dos keyframes lineales y lentos cuando detecta un paneo
  sostenido, amplio y casi unidireccional.
- Reduce el muestreo a dos veces por segundo, suaviza más la detección y
  conserva la cara ya adquirida en lugar de saltar a otra. Los cambios de lado
  u oscilaciones del detector quedan bloqueados en un encuadre estable.

### 0.0.24

- El encuadre horizontal queda limitado al recorrido físico posible del crop.
  Si se cambia el preset vertical, los keyframes existentes se ajustan al nuevo
  límite para impedir que entre una franja negra por cualquier lateral.
- El renderizador aplica el mismo límite en la geometría final de Crop como
  salvaguarda adicional, incluso para proyectos con keyframes antiguos.

### 0.0.25

- Se corrige un frame residual al separar planos. FFmpeg informa el primer
  frame del plano nuevo, mientras que OpenShot trata el final del clip
  izquierdo como inclusivo; el corte automático deja ahora ese final un frame
  nativo antes y mantiene el plano derecho en el timestamp detectado.

## Desarrollo local

Para iniciar la versión de desarrollo en Windows:

```bat
scripts\run_smouk.bat
```

El detalle de compilación está en
[docs-analysis/08-windows-build-analysis.md](docs-analysis/08-windows-build-analysis.md).
Los parches que permiten reproducir las modificaciones sobre repositorios
limpios de OpenShot están en [patches](patches/README.md).
