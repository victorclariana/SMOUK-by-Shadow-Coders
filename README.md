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

La causa documentada del crash nativo de la frontera BSC–ParlaBE está en
[la memoria forense permanente](docs/SMOUK-TRANSCRIPTION-FORENSIC-MEMORY.md).

## Estado actual

Estamos en una fase inicial de desarrollo. La investigación técnica y el plan
por fases están en [docs-analysis](docs-analysis/README.md). El dock
`Verticalization` ya integra corte de planos, reencuadre asistido, exportación
vertical y la primera automatización de subtítulos en catalán.

## Versiones y cambios

Usamos versiones `0.0.x` durante esta etapa inicial. Cada cambio funcional o
de interfaz de SMOUK incrementa `x` y debe añadirse a este historial.

### 0.0.109

- Añade el estado textual de cada fase bajo la barra de subtitulado sin
  modificar la barra ni tocar la interfaz durante la inferencia BSC.
- Recupera el ajuste de dos líneas de 26 caracteres después de la revisión
  ParlaBE y fija la tipografía SVG, usando compresión horizontal para mantener
  el texto dentro de la guía 9:16.
- Resalta con amarillo únicamente los caracteres insertados o sustituidos por
  ParlaBE en la ventana de revisión.

### 0.0.110

- Recupera exactamente el flujo seguro de revisión de 0.0.108 y limita este
  parche a la presentación visual: subtítulos de hasta dos líneas, tipografía
  estable dentro de la guía 9:16, blanco al 100% y borde negro de 2.9 px.

### 0.0.111

- Ajusta automáticamente solo las líneas de subtítulo excepcionalmente largas
  para que ningún SVG pueda salir de los márgenes de la guía 9:16 cuando el
  renderizador de Windows no respeta `textLength`.

### 0.0.112

- Descarta únicamente los microsegmentos terminales de Whisper con marcas de
  tiempo colapsadas y palabras repetidas, como el falso texto “Arada, Ada i
  Ada”, sin alterar palabras válidas del resto de la transcripción.

### 0.0.113

- Fija una única medida, color blanco y borde negro para toda la tipografía de
  subtítulos. Las líneas excepcionales se comprimen solo horizontalmente para
  respetar la guía 9:16, sin reducir la altura tipográfica de esa pantalla.

### 0.0.114

- Elimina toda compresión horizontal, `textLength` y escalado de subtítulos.
  La fuente mantiene tamaño, proporciones, blanco y borde fijos; las frases
  largas se redistribuyen por palabras y puntuación en más líneas para caber.

### 0.0.115

- Impone una o dos líneas como máximo, redistribuye el texto corregido entre
  sus intervalos temporales antes de crear los clips y fija el borde negro en
  1.9 px, sin deformar la tipografía.

### 0.0.116

- Redistribuye cualquier texto corregido que exceda dos líneas en intervalos
  temporales interpolados dentro del mismo tramo de voz. El renderizador solo
  recibe líneas seguras de una o dos filas dentro de la guía 9:16.

### 0.0.117

- Fija la medida tipográfica del perfil 9:16 en 40.5 px, reduce cada fila a
  22 caracteres útiles y redistribuye los intervalos en grupos de 44
  caracteres para conservar dos líneas sin compresión ni desbordamiento.

### 0.0.118

- Elimina la creación de intervalos interpolados cortos después de la revisión.
  Se conservan los tiempos originales y cualquier pantalla inferior a 1
  segundo se fusiona con una pantalla vecina para mantener legibilidad.

### 0.0.119

- Fija la tipografía de subtítulos en 42 px y el borde negro en 2.2 px.
  Redistribuye las palabras con un máximo de 21 caracteres por fila y 42 por
  pantalla para compensar el espacio adicional sin deformar la fuente.

### 0.0.120

- Corrige el límite posterior a la revisión manual: cada pantalla se reparte
  con un máximo efectivo de 40 caracteres para garantizar dos filas de 21 o
  menos y respetar siempre el rectángulo 9:16.

### 0.0.121

- Fusiona cualquier solapamiento temporal detectado después de la revisión en
  un único clip, impidiendo que dos subtítulos se dibujen simultáneamente.

### 0.0.122

- Reparte las frases corregidas con una partición con capacidad: cada cue se
  limita a 40 caracteres y solo se aceptan cortes que permiten que todos los
  cues restantes respeten también el límite de dos filas.

### 0.0.123

- Valida cada fila después de la partición, no solo el total de caracteres.
  Una fila de más de 21 caracteres mueve palabras al siguiente cue temporal y
  queda bloqueada antes de generar el SVG.

### 0.0.124

- Añade el apartado MASK al dock Verticalization. Permite cargar una máscara
  PSD transparente centrada en la guía 9:16, ajustar su posición X/Y, mostrarla
  u ocultarla en una pista propia entre el vídeo y los overlays, y conservar
  todos esos valores en la configuración de OpenShot.

### 0.0.125

- Convierte MASK en una salida de pista reversible tipo ojo: conserva el PSD y
  su posición al ocultarlo, permite volver a activarlo y aplica el estado al
  visor y al render mediante `Track.enabled`.
- Declara las claves de ruta, posición y visibilidad en la configuración oficial
  para que se guarden realmente entre sesiones. El engranaje abre ahora
  `SETTINGS VERTICALIZATION`, preparado para la configuración general del dock.

### 0.0.126

- Integra el engranaje de Verticalization en el `HiddenTitleBar` que OpenShot
  reconstruye realmente, de modo que permanece visible junto al título del dock
  al cambiar de tema, acoplarlo o tabularlo.

### 0.0.127

- Hace que el ojo de MASK afecte inmediatamente al visor y al render mediante
  una curva de alpha reversible en el clip, además de conservar el estado
  `Track.enabled` en el proyecto.

### 0.0.128

- Separa la creación de la pista de la salida de la máscara: `SHOW MASK TRACK`
  crea la pista desde el PSD guardado cuando falta, y el ojo solo controla su
  visibilidad en visor y render.

### 0.0.108

- Elimina la actualización de widget inmediatamente posterior a BSC, que era
  el único efecto Qt entre la transcripción válida y el crash nativo.
- Desglosa la preparación de ParlaBE en trazas persistentes para identificar
  de forma exacta cualquier fallo posterior sin perder el estado del proceso.

### 0.0.107

- Corrige el cierre nativo de Qt que ocurría tras completar BSC y antes de la
  revisión: la salida del proceso, ParlaBE y el diálogo ahora cruzan límites
  separados del bucle de eventos.
- Sustituye el diálogo bloqueante `exec_()` por un diálogo modal asíncrono y
  conserva trazas de cada transición en `openshot-qt.log`.

### 0.0.104

- Añade una revisión intermedia de la transcripción catalana: ParlaBE corrige
  frases antes de crear los clips del Timeline, muestra los cambios resaltados
  en amarillo y permite editarlos manualmente. Los timecodes originales se
  conservan y el botón Aceptar reutiliza el reparto de subtítulos existente.

### 0.0.105

- Recorta los cues finales de Whisper al OUT exacto del Timeline antes de la
  validación, evitando que una cola fraccional fuera de rango bloquee la
  transcripción y la ventana de revisión.

### 0.0.106

- Añade estado visible durante la carga y revisión de ParlaBE para distinguir
  la corrección Python de un cuelgue y mostrar el avance por frase.

### 0.0.103

- Amplía el contorno negro de los subtítulos verticales a 2,9 píxeles.

### 0.0.102

- Ajusta los subtítulos verticales a la banda útil inferior del formato 9:16,
  aumenta la tipografía y aplica un borde negro grueso inspirado en la
  referencia de emisión.

### 0.0.101

- Se rehízo el flujo local de subtítulos: extracción estricta del IN–OUT del
  Timeline, reconocimiento BSC con contexto controlado, reparación de marcas
  temporales imposibles y validación antes de crear clips.
- Los subtítulos se agrupan en dos líneas, respetan los finales de frase y
  evitan dejar una sola palabra aislada entre pantallas.
- Se guardan la transcripción bruta, el resultado final y un informe de
  validación temporal antes de insertar nada en OpenShot.

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

### 0.0.26

- La disposición guardada de la interfaz se restaura realmente después de que
  Windows muestre la ventana. El checkpoint inicial ya no puede sobrescribir
  antes de tiempo la posición y tamaño de timeline, visor y docks.
- El perfil predeterminado para proyectos nuevos es `FHD PAL 1080i 25 fps`.
  Las instalaciones existentes reciben este valor una vez y después conservan
  cualquier perfil predeterminado que el usuario elija manualmente.
- Los vídeos HD anamórficos de 1440×1080 con SAR 4:3 o DAR 16:9 se reconocen al
  importar. Se normalizan como 16:9 y se expanden automáticamente para llenar
  el lienzo horizontal; también se actualizan los clips existentes que aún
  utilicen `Best Fit`.

### 0.0.27

- Se corrige definitivamente la regresión de corte introducida en 0.0.25. El
  límite detectado por FFmpeg vuelve a ser una única frontera compartida: el
  clip izquierdo termina en ella y el derecho usa esa misma posición como
  inicio de fuente. Así, la conversión inclusiva de libopenshot deja dos
  fotogramas consecutivos, sin repetir el anterior y sin abrir un hueco.
- Se añade una prueba de regresión a 25 fps que reproduce el corte de `34,28 s`
  y verifica tanto la continuidad del timeline como la continuidad de los
  fotogramas de fuente.
- La restauración de la interfaz se ejecuta estrictamente después de que Windows
  aplique el estado normal, maximizado o de pantalla completa. Se elimina la
  carrera que consumía prematuramente la restauración desde `showEvent` y se
  registra en el log si Qt aceptó el estado guardado.
- El preset vertical elegido queda registrado como una preferencia válida; ya
  no se descarta al cerrar por faltar su clave en la configuración base.

### 0.0.28

- Se añade `Transcribe timeline in Catalan` a la sección `Subtitles` del dock.
  Un solo clic transcribe cada fuente con audio presente en la timeline y
  aplica el resultado a todos sus planos como efectos `Caption` editables.
- La transcripción es local mediante OpenVINO en CPU/GPU Intel con el modelo
  multilingüe `whisper-large-v3-turbo-int4-ov`. En el primer uso se confirma la
  instalación y descarga del modelo; después funciona sin red.
- El proceso muestra progreso, genera copias JSON y SRT reproducibles dentro de
  `.smouk-transcriptions` y conserva cualquier efecto Caption creado a mano.
  Al repetirlo solo actualiza los efectos identificados como transcripción de
  SMOUK.
- El runtime Python y los modelos se aíslan en carpetas ignoradas por Git para
  no alterar el Python/Qt con el que se ejecuta OpenShot.

### 0.0.29

- Se acelera la transcripción catalana en CPU. El worker deja dos hilos libres
  para mantener fluida la interfaz y utiliza hasta diez hilos; en el equipo de
  desarrollo pasa de los cuatro hilos predeterminados de CTranslate2 a diez.
- La decodificación cambia de `beam_size=5` a `beam_size=1`. Se conserva el
  modelo BSC catalán, la cuantización INT8, el detector de voz y los timestamps
  por palabra, evitando calcular cinco hipótesis completas para cada fragmento.
- La selección automática de hilos tiene pruebas para equipos de 2, 8, 14 y 32
  procesadores lógicos y admite parámetros manuales para futuras comparativas.

### 0.0.30

- Los subtítulos automáticos adoptan un estilo vertical basado en la referencia:
  Arial blanca, borde negro, fondo transparente, centrados en la parte baja y
  limitados al 86 % de la anchura interior de la guía.
- El efecto `Caption` se dibuja después del reencuadre del clip. En el visor sus
  coordenadas se calculan dentro del rectángulo 9:16 o 4:5; durante la
  exportación se convierten a coordenadas y tamaño reales del lienzo vertical
  de 1080 píxeles. El texto ya no pertenece al espacio horizontal 16:9.
- Al abrir un proyecto, mostrar el dock o cambiar de preset se migran también
  los efectos de transcripción existentes. Los captions manuales no se tocan.
- La segmentación reduce cada pantalla a 60 caracteres y unas 30 posiciones por
  línea, evitando dejar preposiciones catalanas al final. La frase de referencia
  queda como `i la crida feta` / `pel president d'Omnium`.

### 0.0.31

- La transcripción usa un perfil equilibrado de precisión: tres hipótesis por
  segmento en lugar de una, conserva el texto anterior como contexto y reduce
  el umbral del detector de voz con 500 ms de margen. Esto recupera palabras de
  menor volumen y mejora la continuidad sin volver al coste de cinco hipótesis.
- Se mantienen los diez hilos de CPU de 0.0.29, por lo que el aumento de calidad
  sigue siendo considerablemente más rápido que la primera implementación.
- El borde negro de los subtítulos se reduce de 2,25 a 0,5 unidades en el render
  vertical. En el visor se escala en la misma proporción respecto a la guía,
  dejando que domine el relleno blanco como en la referencia proporcionada.

### 0.0.32

- Los subtítulos creados por la transcripción usan Arial en negrita para
  separarse mejor del fondo sin recuperar el borde negro grueso.
- `libopenshot` interpreta el sufijo ` Bold` del nombre de fuente como peso
  tipográfico real. Se conserva el contorno fino de 0,5 unidades establecido
  en 0.0.31 tanto en el visor como en la exportación vertical.

### 0.0.33

- Cada bloque de subtítulos generado muestra como máximo dos líneas dentro del
  encuadre vertical. El agrupador cierra el bloque antes de que una línea larga
  provoque un tercer renglón automático en `Caption`.
- El mismo límite se aplica cuando Whisper solo devuelve segmentos y no
  timestamps por palabra: SMOUK estima los tiempos internos, vuelve a agrupar
  el texto y conserva todas las palabras.

### 0.0.34

- Los efectos de subtítulos reciben WebVTT sin índices SRT, evitando que el
  número de un cue se cuele en pantalla a partir de ciertas transcripciones.
- La tipografía sube de 35 a 37 puntos en el lienzo final. Las contracciones
  con apóstrofo (por ejemplo, `d'odi` y `d'acollida`) se mantienen como una
  sola palabra al unir tokens, repartir líneas y separar pantallas.
- Los cues duran al menos un segundo cuando es posible unirlos sin exceder las
  dos líneas; así no aparecen textos fugaces de unos pocos fotogramas.
- El progreso distingue el reconocimiento de voz del formateo y guardado. Si
  Whisper tarda en decodificar un segmento largo, el dock informa de esa fase y
  del último porcentaje del audio procesado, sin quedarse falsamente en 98 %.

### 0.0.35

- Cada cue se crea como un clip SVG transparente e independiente en una nueva
  pista `SMOUK Subtitles` situada sobre las pistas actuales. Los clips siguen
  los tiempos de origen incluso cuando el vídeo ya está cortado; se pueden
  mover y recortar en el Timeline, y sus títulos SVG se pueden editar desde los
  medios del proyecto. Al volver a transcribir, se sustituyen los clips SMOUK
  previos y se retiran los antiguos efectos Caption automáticos.
- Los títulos usan Arial Black, peso 900 y dos puntos más que la tipografía
  anterior, centrados dentro de la guía vertical y con contorno fino.
- Se elimina una cola final muy concreta de repetición de partículas
  (`el, el, i/y`) que el modelo puede inventar después de cerrar una frase; no
  se recortan finales normales sin ese patrón.

### 0.0.36

- El análisis de reencuadre desentrelaza los fotogramas de forma temporal con
  FFmpeg `bwdif` antes de enviarlos a YuNet, YOLO y MediaPipe. Solo cambia la
  copia usada por los detectores: la fuente del proyecto, los cortes y la
  frecuencia de imagen se conservan.
- El log indica cuántos fotogramas analizó cada clip y en cuántos encontró un
  sujeto, para distinguir una detección vacía de un fallo real de FFmpeg.

### 0.0.37

- El dock Verticalization incorpora `Browse PNG logo`: valida que el archivo
  tenga canal Alpha y lo añade como clip de imagen nativo en la pista superior
  `SMOUK Logo`.
- El logo cubre la duración actual del proyecto y conserva los controles
  estándar de OpenShot para moverlo y cambiar su escala desde el visor; al
  volver a elegir un PNG se reemplaza solo el clip generado anterior.

### 0.0.38

- El apartado `Logo` del dock incluye un deslizador `Logo opacity` de 0 a 100 %
  para ajustar directamente la transparencia del clip seleccionado.
- La opacidad se guarda en la propiedad Alpha del clip como keyframes constantes
  y se sincroniza al cambiar de clip o mover el cabezal.

### 0.0.39

- Se protege la sincronización del control de opacidad durante el arranque para
  que la restauración del estado de selección no use el deslizador antes de que
  el dock haya terminado de construirlo.

### 0.0.40

- Las señales de selección y posición se conectan después de construir todo el
  dock Verticalization, evitando callbacks prematuros durante el arranque.

### 0.0.41

- La opacidad del logo se aplica al clip seleccionado sin conexiones automáticas
  durante el arranque. Esto evita cierres nativos de Qt al restaurar la ventana.

### 0.0.42

- El dock Verticalization permite seleccionar una carpeta de análisis de títulos
  y valida los ficheros `CLEAN.MP4`, `DATA.JSON` y `PROGRAMA.MP4`.
- Se validan los cortes del JSON a 25 fps, se comprueba la información básica de
  los dos vídeos y se marca la posible presencia de un reloj visual para la
  futura calibración OCR, sin modificar todavía el proyecto.

### 0.0.43

- Las secciones del dock Verticalization se abren contraídas. Esto evita el
  recálculo continuo de un panel muy alto al arrastrar su barra de desplazamiento
  en esta instalación de Qt para Windows.

### 0.0.44

- Se restablecen abiertas por defecto todas las secciones de Verticalization.
- El estado de los docks ya no se serializa durante cada `resizeEvent`: abrir,
  cerrar o desplazar las secciones no puede llamar a `Qt.saveState()` mientras
  Qt está recalculando el área desplazable, evitando el cierre nativo en
  `Qt5Core.dll`.

### 0.0.45

- Los proyectos nuevos de SMOUK empiezan con dos pistas. También se corrige la
  plantilla local antigua de cinco pistas cuando se crea un proyecto en blanco;
  los proyectos `.osp` existentes conservan sus propias pistas.
- En la primera apertura tras esta versión, el Timeline se ajusta a la altura
  de su barra, regla y dos pistas, calculada según el tema activo. El espacio
  liberado queda disponible para el visor, Project Files y los docks, y el
  tamaño que el usuario elija después se conserva normalmente.

### 0.0.46

- La sección `Titles` del dock Verticalization muestra junto al selector los
  tres nombres obligatorios de la carpeta: `CLEAN.MP4`, `DATA.JSON` y
  `PROGRAMA.MP4`.
- En el tema predeterminado Cosmic, las filas de pista, clips y transiciones
  del Timeline duplican su altura de 48 a 96 píxeles. El ajuste compacto se
  recalcula una vez para reservar barra, regla y las dos pistas altas.

### 0.0.47

- La validación de la carpeta de títulos recorre los primeros tres minutos de
  `CLEAN.MP4` y `PROGRAMA.MP4` en muestras de un segundo a 25 fps, en lugar de
  mirar únicamente el primer fotograma. Busca el patrón gráfico del reloj y
  muestra por separado el primer instante candidato y las muestras analizadas
  de cada vídeo. La lectura de los dígitos se incorporará en la fase OCR.

### 0.0.48

- El rastreo del reloj usa FFmpeg para extraer las muestras, evitando el fallo
  de lectura de OpenCV que podía devolver cero fotogramas para los MP4 de
  emisión. El detector reconoce la combinación visual de números blancos y
  paneles naranja saturados del reloj de referencia.
- El resultado informa del diagnóstico del lector cuando no se ha podido
  obtener una muestra, en vez de presentarlo como un reloj no encontrado.

### 0.0.49

- Se corrige el falso positivo de reloj en el Clean Feed: además de los
  números blancos, el patrón debe ocupar al menos el 30 % de la imagen con los
  paneles naranja característicos. Las comprobaciones con el material de
  referencia midieron un 3,1 % en el falso positivo inicial y un 61,7 % en el
  reloj real.
- El apartado `Titles` muestra una barra de 360 muestras y un texto de estado:
  analiza primero `CLEAN.MP4` y después `PROGRAMA.MP4`, actualizándose mientras
  FFmpeg entrega cada fotograma de la exploración de tres minutos.

### 0.0.50

- Se endurece la firma del reloj frente a las caretas del programa. Además de
  los dígitos y del naranja, exige que el naranja ocupe al menos el 50 % de la
  imagen y que exista un panel naranja continuo de al menos el 18 %. En los
  fotogramas validados, la careta tenía 15,4 % y 5,9 %; el reloj real, 61,7 %
  y 28,0 % respectivamente.

### 0.0.51

- El detector deja de decidir por un umbral de color. Extrae automáticamente
  de `CLEAN.MP4` una plantilla de referencia en una ventana centrada en
  01:23 y compara cada muestra mediante color, forma, área, relación de
  aspecto y `cv2.matchTemplate`.
- La puntuación compuesta pondera color (25 %), forma (15 %), plantilla
  (45 %) y área (15 %). Solo acepta el reloj cuando supera los mínimos de
  puntuación y plantilla durante tres muestras consecutivas, descartando las
  caretas de aspecto parecido.

### 0.0.52

- Al seleccionar una carpeta vÃ¡lida con `CLEAN.MP4`, `DATA.JSON` y
  `PROGRAMA.MP4`, el dock ejecuta el flujo completo sin ventanas de resultado:
  valida los cortes, detecta los dos relojes, hace OCR de su banda de dÃ­gitos,
  sincroniza los dos orÃ­genes y coloca el intervalo de `CLEAN.MP4` en Track 2.
- Incorpora el modelo local catalÃ¡n de Tesseract para leer los timecodes y
  rastrea las regiones de localizaciÃ³n y rÃ³tulo inferior de `PROGRAMA.MP4`.
  Las detecciones consecutivas se agrupan y se crean como SVG transparentes y
  editables en la pista superior `CHYRONS`, con texto, plantilla, coordenadas,
  referencia, confianza y timecodes conservados como metadatos del clip.
- El progreso y los posibles problemas se muestran en el dock Titles y en la
  barra de estado, sin interrumpir el flujo con diÃ¡logos emergentes.

### 0.0.53

- Corrige el bloqueo aparente tras aceptar una carpeta de tÃ­tulos: la
  extracciÃ³n FFmpeg y el OCR de los dos relojes se ejecutan ahora en un hilo
  de trabajo, manteniendo reactiva la interfaz.
- El dock Titles conserva una traza visible de las Ãºltimas fases (fotograma
  de CLEAN, fotograma de PROGRAMA, sincronizaciÃ³n, importaciÃ³n y OCR de
  rÃ³tulos) y cada una se registra tambiÃ©n en `openshot-qt.log`.

### 0.0.54

- Corrige el cierre al comenzar el OCR: `MainWindow.statusBar` es un widget
  `QStatusBar`, y el código anterior lo llamaba como una función. La excepción
  se producía al mostrar el primer mensaje, antes de iniciar el trabajador OCR.
- Protege las entradas y respuestas del proceso de títulos: los errores quedan
  en el dock y en el log, y se vuelve a habilitar la selección de carpeta.
  Los mensajes incluyen fase, hora y segundos de espera sin borrar el motivo
  del fallo. Se impiden ejecuciones simultáneas y el cierre durante el análisis.
- También ejecuta el análisis de rótulos en segundo plano; mantiene la escritura
  de clips en el hilo de Qt. Elimina código inalcanzable y un uso de traducción
  sin definir que ocultaba fallos como si el resultado fuese cero rótulos.
- Incluye el modelo inglés de Tesseract para los dígitos del reloj y conserva
  el modelo catalán para texto. El detector entrega al OCR las tres muestras
  exactas que validó, en lugar de volver a buscar un keyframe distinto.
- Validación: siete pruebas con widgets y señales reales de Qt, lectura de ambos
  vídeos y OCR de ocho segundos de PROGRAMA con la interfaz reactiva. Con el
  material de prueba se han leído `14:28:23` en CLEAN y `14:29:00` en PROGRAMA;
  la sincronización calcula cortes relativos sin tocar el Timeline hasta que
  ambos relojes y el intervalo han pasado sus comprobaciones.

### 0.0.58

- Se corrigió el bloqueo al usar **Guardar como**: el proyecto y sus recursos
  se guardan en el hilo de la interfaz de Qt, que es el único seguro para
  OpenShot y libopenshot.
- El autoguardado de proyectos ya guardados usa el mismo camino seguro, por lo
  que no inicia una segunda escritura concurrente mientras se está moviendo o
  registrando un recurso.
- El cursor de espera de **Guardar como** se libera siempre al terminar el
  guardado, incluso si OpenShot informa de un error.

### 0.0.59

- El guardado de SMOUK deja de crear, copiar, mover, comprimir o borrar árboles
  de recursos. Escribe únicamente el fichero `.osp` JSON y conserva las rutas
  de los vídeos y SVG generados, evitando la actividad masiva que activaba la
  protección corporativa contra cifrado no autorizado.
- Las carpetas de recursos se crearán solamente cuando una función las necesite,
  nunca como efecto lateral de **Guardar** o **Guardar como**.
- El lanzador también puede usar `python3.14.exe`, el ejecutable versionado del
  paquete oficial firmado de MSYS2, si la protección elimina los alias
  `python.exe` o `python3.exe`.

### 0.0.61

- Sincroniza los vídeos CLEAN y PROGRAMA hasta el fotograma: mide la fase de
  las transiciones nativas del reloj, además de leer sus dígitos. En el bloque
  de prueba ambos relojes tienen una fase de seis fotogramas, que se aplica al
  corte y a los chyrons en lugar de redondear el reloj al segundo completo.
- El OCR de títulos limita la banda inferior al gráfico real. Tras reconocer
  un texto en catalán, contrasta sólo su recorte cercano a 25 fps mediante
  `matchTemplate`, conservando los fotogramas de entrada y salida sin hacer
  OCR fotograma a fotograma en todo el programa.
- Verificado con `ILLA DEMANA GENEROSITAT EN L'ACOLLIDA`: la entrada y salida
  de PROGRAMA se traducen a `00:00:05,18` y `00:00:17,21` en CHYRONS.

### 0.0.62

- El OCR de chyrons adopta el mapa editorial de TNM: analiza por separado
  DIRECTE/localización, identificaciones de presentadores, nombre y cargo,
  firma, pretítulo, titular principal y rótulo persistente. Las capas que
  coinciden en pantalla se conservan como clips editables independientes.
- Excluye la imagen central, el logotipo TN, el reloj y la banda de
  transcripción. Las validaciones de color y forma distinguen DIRECTE de una
  localización ordinaria y una identificación de nombre/cargo de una firma,
  reduciendo títulos duplicados antes de ejecutar OCR en catalán.
- El Dock informa ahora durante el refinado de entrada/salida de cada rótulo y
  durante la creación de los SVG editables, además del análisis OCR.

### 0.0.63

- **New Project**, el inicio normal y la apertura de proyectos dejan de borrar
  recursivamente las carpetas de miniaturas, títulos y proxies. Ahora sólo se
  comprueba que existan; no se borra, mueve, copia ni comprime un árbol de
  archivos desde esos flujos.
- La recuperación automática no carga proyectos de backup que contengan
  chyrons SMOUK y tampoco los mueve. Un nuevo proyecto registra sólo la
  intención de no recuperar el backup anterior si el programa se interrumpe
  antes del siguiente autosave.
- Se desactiva la recuperación basada en ZIP. El guardado normal sigue siendo
  un único JSON `.osp`, sin migración masiva de assets.

### 0.0.64

- Separa el pretítulo del titular principal en sus bandas reales: el OCR ya no
  mezcla la pastilla negra superior con la barra naranja o el titular de
  sumario.
- Las zonas de firma, nombre/cargo y presentadores rechazan líneas en
  mayúsculas y una barra naranja que cruza de lado a lado. Con ello un titular
  principal no se vuelve a importar como un segundo crédito o presentador.
- Recupera el modo OCR de bloque que usaba la versión previa para los rótulos
  TNM; mejora la lectura de titulares como `ILLA DEMANA GENEROSITAT EN
  L'ACOLLIDA`.

### 0.0.65

- Un pretítulo sólo se acepta si su banda oscura es una pastilla compacta. La
  barra completa del titular, combinada con letras presentes en la imagen,
  queda excluida antes de OCR. En el caso del Barça a `00:01:19,13` se rechaza
  el falso `l BE MmLE…` y se conserva únicamente el titular real.
- Los rótulos editables se distribuyen en cuatro pistas: `CHYRONS · Titulares`,
  `CHYRONS · Pretítulos`, `CHYRONS · Personas` y `CHYRONS · Localización`.
  Así, los elementos simultáneos se ven y revisan por separado.

### 0.0.66

- La detección de las cartelas de presentador usa exclusivamente el naranja
  saturado de su gráfica. Ya no toma como parte del rótulo la ropa amarilla o
  la imagen que se mueve detrás, por lo que espera dos muestras de la cartela
  ya completa antes de ejecutar OCR en catalán. Esto recupera las
  identificaciones de Anna Garnatxe Masmitjà y Xavi Coral Trullàs de
  `PROGRAMA.MP4` alrededor de `03:36`.
- Una cartela grande de presentador no se duplica como `Nombre y cargo`: esa
  plantilla queda reservada para el rótulo de entrevistado, con su acento
  naranja pequeño.
- Cada plantilla editorial tiene ahora su propia pista de revisión: titular,
  titular persistente, pretítulo, presentador izquierdo, presentador derecho,
  nombre y cargo, firma, directo y localización. Las capas simultáneas ya no
  quedan superpuestas en una sola pista.

### 0.0.67

- Las dos cartelas de presentadores se leen con el modo OCR que corresponde a
  su geometría: línea única a la izquierda y línea escasa a la derecha. En el
  plano de `03:36` se generan `Anna Garnatxe Masmitjà` y `Xavi Coral Trullàs`;
  se elimina el fragmento decorativo previo y la raya final que puede devolver
  el OCR de la cartela derecha.
- Seleccionar un SVG de chyron en la Timeline ya no lo envía al control de
  reencuadre de vídeo. El deslizador vuelve a cero y no evalúa keyframes de un
  overlay, evitando el bloqueo observado al seleccionar el título de Anna.

### 0.0.68

- El reconocimiento de los relojes y de los rótulos TNM se realiza ahora con
  **PP-OCRv5 Latin**, el modelo neuronal local de PaddleOCR que incluye
  alfabetos latinos y catalán. Se elimina del código de análisis cualquier
  llamada, comprobación de idioma o archivo temporal del motor anterior.
- SMOUK conserva el detector visual, las zonas editoriales TNM, las exclusiones
  de logo/reloj/subtítulos y el refinado a 25 fps. PP-OCRv5 sólo recibe el
  recorte de una gráfica ya estable y devuelve texto y confianza, por lo que
  no analiza todos los fotogramas ni genera PNG temporales por lectura.
- El modelo se ejecuta en un entorno Python 3.12 aislado en
  `.third_party/paddleocr`, mientras la aplicación mantiene su Python 3.14.
  La instalación verificada usa `PaddlePaddle 3.3.1` y `PaddleOCR 3.7.0` desde
  PyPI: los 69 wheels se comprobaron contra sus SHA-256 publicados antes de
  instalarse sin red. El modelo `latin_PP-OCRv5_mobile_rec` procede del
  repositorio oficial de Paddle y sus hashes locales quedan en la caché para
  detectar cualquier modificación posterior.

### 0.0.69

- Se añaden al desplegable `Vertical output profile` los perfiles
  `608 x 1080 (9:16)`, a 25 y a 30 fps. El renderizador usa el lienzo exacto
  de 608×1080 y una guía con esa misma proporción, de modo que una fuente HD
  de 1920×1080 puede encuadrarse a su altura nativa sin ampliación vertical.
- `608 x 1080 (9:16) - 25 fps` pasa a ser el valor inicial de SMOUK. Las
  instalaciones existentes se actualizan una única vez al abrir el dock;
  después, cualquier selección del editor se conserva como preferencia.

### 0.0.70

- Se corrige el localizador de FFmpeg de la validación de carpeta de títulos.
  Un error interno al crear la plantilla visual de CLEAN.MP4 se interpretaba
  como si el reloj no existiera y detenía la cadena antes de PP-OCRv5. Ahora
  el error se informa como tal y la detección vuelve a crear la referencia
  cerca de 01:23 para rastrear ambos feeds y continuar al OCR de chyrons.
- Se añade una prueba de regresión para el localizador de FFmpeg. La validación
  de solo lectura en `MATERIAL PER TRACTAR` detecta los relojes de CLEAN y
  PROGRAMA y entra en el análisis de las zonas de títulos.

### 0.0.71

- Se corrige el protocolo local de PP-OCRv5 en Windows: sus respuestas se
  codifican ahora como JSON ASCII escapado antes de cruzar el pipe UTF-8 de
  SMOUK. Así se conservan `ç`, `à`, `í`, `ñ` y el resto de caracteres
  catalanes en los SVG editables, en vez de guardarse como `�`.
- El área del titular TNM se extiende del 90% al 93% del ancho: el límite
  anterior podía truncar el último glifo de titulares largos, como
  `ACOLLIDA`. El reloj continúa excluido por estar debajo de esa banda.
- Los titulares, pretítulos y cintillos persistentes solo se aceptan cuando
  contienen su combinación gráfica de banda naranja y texto blanco y superan
  una confianza mínima real de PP-OCRv5. Las transiciones vacías, subtítulos
  de imagen y lecturas corruptas ya no se convierten en chyrons editables.
  El refinado de entrada/salida conserva la confianza original y no puede
  inflarla artificialmente.

### 0.0.72

- Se corrige la geometría de los titulares grandes TNM: su zona comenzaba en
  el 82% de la altura y entregaba al OCR letras recortadas. Ahora cubre la
  banda gris/naranja completa, por lo que detecta los titulares de sumario y
  noticia como `ALERTA PER LES PLUGES` y `ELS JAVIS, CAMÍ DELS OSCARS`.
- PP-OCRv5 conserva su modelo local pero recibe las palabras separadas de las
  bandas editoriales fijas. Para las barras naranjas, aísla primero esa barra
  y evita mezclar el pretítulo o el logotipo TN; para los cintillos grises,
  segmenta las palabras blancas. Esto también reconstruye a la vez el
  pretítulo `CONSELL DE SEGURETAT EUROPEU` y el titular de noticia.
- La agrupación visual permite la variación normal de las animaciones de
  entrada en titulares, pretítulos y cintillos persistentes, manteniendo dos
  muestras estables y los filtros gráficos. Los nombres y otras etiquetas
  compactas conservan el umbral estricto anterior.

### 0.0.73

- Los cintillos persistentes TNM se reconstruyen como un único clip editable
  aunque los subtítulos de emisión o un cambio de plano oculten temporalmente
  su zona inferior izquierda. La unión exige el mismo texto y no cruza un
  cambio a otro tema editorial.
- Se limpia el artefacto OCR de nombres `àas` al final de un apellido, que
  corregía incorrectamente `Xavi Coral Trullàs` como `Trullàas`. La lectura
  correcta de `Anna Garnatxe Masmitjà` se conserva.

### 0.0.74

- Los titulares grandes de noticia se reconstruyen dentro del área central
  activa 9:16 que marca la guía blanca, incluso mientras el proyecto se edita
  en 16:9. Se aplica un margen interior y recorte de seguridad para que ningún
  carácter se pierda al exportar en vertical.
- Los titulares se dividen por palabras en varias líneas y se centran en el
  tercio inferior de ese área. Esta primera adaptación afecta solo a la pista
  `CHYRONS · Titular`; los demás tipos de rótulo mantienen su posición actual
  para revisarlos por separado.

### 0.0.75

- Todos los tipos de rótulo reconstruidos —localización, directo, nombres,
  cargos, firmas, pretítulos y cintillos persistentes— se componen dentro del
  área activa central 9:16, con el mismo margen y recorte seguro que los
  titulares grandes.
- Cuando coinciden en el tiempo, SMOUK los distribuye en carriles verticales
  separados. Conserva una jerarquía editorial: localización arriba,
  identificaciones en el centro, pretítulos y cintillos debajo, y el titular
  principal en el tercio inferior.

### 0.0.76

- Se separó el flujo de Source Video, que valida e importa el corte de
  `CLEAN.MP4`, del análisis posterior de chyrons en `PROGRAMA.MP4` dentro de
  la sección Titles.
- Se ordenó el dock Verticalization: el selector de carpeta y el corte de
  `CLEAN.MP4` están en **Source Video**; la detección de chyrons de
  `PROGRAMA.MP4` tiene su propio botón en **Titles**. Ambos pasos comparten la
  sincronización horaria, pero el segundo no abre otro selector ni vuelve a
  cortar o importar CLEAN.
- El selector Source Video exige `CLEAN.MP4`, `DATA.JSON` y `PROGRAMA.MP4`,
  obtiene el `in/out` de DATA y calibra solo el reloj de CLEAN para importar
  el clip en Track 2. Titles calibra después solo PROGRAMA y crea los chyrons
  encima de ese clip.
- Los controles manuales `Horizontal framing (selected clip)`, su deslizador
  y `Keyframes` se trasladaron a **Automatic Reframing**. La guía 9:16 se
  muestra marcada por defecto junto al perfil de salida.

### 0.0.77

- Se corrigió el temporizador de progreso compartido por Source Video y
  Titles. El análisis del reloj de `CLEAN.MP4` conserva ahora sus propias
  trazas y estado, y ya no puede generar un error de Titles ni iniciar el
  análisis de chyrons.

### 0.0.78

- Los PNG de logo verticales se insertan ahora con su tamaño nativo y gravedad
  centrada. Un fichero de 608×1080 queda dentro del rectángulo blanco 9:16 de
  un proyecto HD 1920×1080, con posición y tamaño aún editables desde el visor.

### 0.0.79

- Se reservaron bandas verticales para que la transcripción quede centrada en
  la zona de subtítulos de la guía. Localización, identificaciones, pretítulos
  y titulares se distribuyen en sus franjas propias y ya no se superponen con
  los subtítulos al coincidir en el tiempo.

### 0.0.60

- Se corrigió el cursor de espera que quedaba activo tras importar CLEAN.MP4
  durante el análisis de títulos. La inserción individual termina ahora la
  transacción de Timeline y restablece el cursor; se aplica el mismo ajuste a
  la inserción individual del logotipo.

### 0.0.57

- Protege New, Open y Save frente a backups generados por las versiones de OCR

### 0.0.100

Les marques de paraula correctes de BSC ja no es redistribueixen si només una
marca és defectuosa. SMOUK limita únicament aquella paraula impossible i
preserva la sincronització ja correcta abans i després.

### 0.0.99

La transcripció es refactoritza sobre el model català BSC, que conserva les
marques de paraula. Abans de transcriure, SMOUK extreu estrictament l'àudio
entre l'IN i l'OUT del clip del Timeline. El resultat brut de Whisper es desa
com `*.whisper-raw.json` abans de crear cap clip de subtítol, per separar de
forma verificable un error de reconeixement d'un error de col·locació.

### 0.0.98

La transcripció OpenVINO manté el català com a idioma de treball i ja no
activa per defecte la recuperació en castellà, que podia convertir la cua
curta d'un vídeo en text espuri. Quan l'últim fragment és més curt que el
context de Whisper, es torna a llegir amb una finestra de 30 segons i només
s'afegeix al Timeline la part nova. Això evita la pèrdua de transcripció als
canvis de fragment, inclòs el punt 00:01:29 del projecte de prova.

El perfil OpenVINO utilitza fragments de 10 segons en aquest maquinari per
reduir les caigudes de Whisper després de canvis de pla i descarta sortides
curtes o repetitives que no són veu utilitzable.

Per a un projecte bilingüe, la recuperació anterior es pot activar
explícitament amb `SMOUK_ALLOW_SPANISH_FALLBACK=1`.

### 0.0.97

Mantiene el catalán como idioma principal y reintenta en castellano solo los
fragmentos cuya salida catalana es vacía o el token espurio `I`. Esto cubre
insertos bilingües sin perder la transcripción de voz catalana.

### 0.0.96

Limita los bloques de Whisper OpenVINO a 30 segundos, que es el contexto de
audio del modelo. Los bloques de 60 segundos solo reconocían correctamente la
primera mitad y producían tokens repetidos en la segunda mitad.

### 0.0.95

Los clips de subtítulos editables guardan ahora su duración real. Antes
conservaban los 3600 segundos predeterminados del recurso SVG y se solapaban
durante todo el Timeline, ocultando o adelantando visualmente otros cues.

### 0.0.94

La transcripción usa el intervalo real de cada clip del Timeline (`IN`, `OUT`
y posición), en lugar de procesar el archivo fuente completo. Los tiempos del
audio recortado se vuelven a expresar en el tiempo de origen para mantener la
sincronización y evitar subtítulos de partes que no están en pantalla.

### 0.0.93

Durante la inferencia GPU la barra de transcripción usa el indicador continuo
propio de Qt. Evita actualizaciones de widgets tras cada fragmento, que hacían
fallar Qt5Core en la instalación MSYS2, y deja claro que el proceso sigue activo.

### 0.0.92

Muestra el progreso de la transcripción en el dock, actualizándolo de forma
limitada desde el temporizador seguro del hilo de Qt para evitar bloqueos por
señales de alta frecuencia durante la inferencia en GPU.

### 0.0.91

Usa las marcas de segmento nativas de Whisper (`return_timestamps`) al crear los subtítulos. Cada fragmento conserva ahora sus límites temporales reales y deja de repartir todo el texto uniformemente por la ventana de audio, evitando la deriva de sincronía.

### 0.0.90

Evita actualizar widgets Qt mientras el trabajador OpenVINO entrega resultados. Los estados, progreso y texto parcial quedan registrados en `openshot-qt.log` y la interfaz se actualiza al terminar, evitando el cierre nativo de `Qt5Core.dll` que ocurría justo después de la primera inferencia.

### 0.0.89

Añade trazas de diagnóstico en cada frontera del transcriptor OpenVINO (Python, modelo, dispositivo, audio, fragmentos e inferencia) y registra el PID y código de salida en `openshot-qt.log`. La GPU vuelve a ser el dispositivo predeterminado; se puede forzar CPU con `SMOUK_OPENVINO_DEVICE=CPU`.

### 0.0.88

La transcripción usa CPU por defecto para no compartir la GPU Intel integrada entre OpenVINO y la previsualización Qt de OpenShot, una combinación que provocaba el cierre nativo `Qt5Core.dll`/`0xc0000602`. Se mantiene la opción explícita `SMOUK_OPENVINO_DEVICE=GPU` para equipos que la hayan validado.

### 0.0.87

- Sustituye la transcripción remota por `OpenVINO/whisper-large-v3-turbo-int4-ov`, un modelo multilingüe local cuantizado a INT4. Usa la GPU Intel mediante OpenVINO cuando está disponible y procesa el audio en bloques de 60 segundos, sin credenciales ni tráfico de audio fuera del equipo.
- El runtime y el modelo se instalan en carpetas aisladas de SMOUK desde fuentes oficiales, manteniendo el contrato JSON/SRT/VTT y el progreso del dock.
- Usa tiempos estimados dentro de cada bloque cuando el modelo no entrega marcas de palabra, conserva subtítulos catalanes en dos líneas y limpia los WAV intermedios tolerando permisos administrados de Windows.

### 0.0.86

- Excluye `localhost`, `127.0.0.1` y `::1` del proxy corporativo al iniciar
  SMOUK. El servidor interno de miniaturas ya no se envía erróneamente al proxy,
  evitando su bucle de fallos y el cierre de Qt durante la carga del Timeline.

  que crearon cientos de chyrons falsos. Si `backup.osp` contiene más de 40
  assets SMOUK, se conserva en `recovery/smouk-quarantine` y se inicia un
  proyecto vacío, evitando cargar cientos de lectores SVG en la Timeline.

### 0.0.56

- El OCR de rótulos ahora ignora la imagen central y analiza solamente la banda
  superior izquierda de localización/fecha (2–56% × 6–31%) y la banda inferior
  editorial (4–96% × 73–94%).
- Se inspecciona visualmente cada segundo, exige dos muestras estables y llama
  a Tesseract en catalán una sola vez por cada imagen nueva de rótulo estable.
  Esto reduce radicalmente el número de OCR sin perder los títulos cortos.
- El lanzador de Windows usa `python3.exe` de MSYS2 si el alias `python.exe`
  ha sido retirado por el antivirus.

### 0.0.55

- Corrige el análisis que creó cientos de títulos inválidos. La imagen de vídeo
  cambiaba en cada segundo y se interpretaba erróneamente como un rótulo nuevo.
  Ahora el OCR analiza una muestra cada cinco segundos y un texto debe ser
  consistente durante al menos dos muestras antes de convertirse en chyron.
- El análisis se realiza completamente en memoria: no guarda recortes de cada
  candidato. Solo se generan SVG cuando un título ha pasado la validación y el
  bloque limita el resultado a 40 chyrons; si se supera, no se escribe ninguno.
- Tesseract reutiliza un único archivo temporal en `%LOCALAPPDATA%\\SMOUK\\ocr`
  en vez de crear y borrar un PNG por cada lectura. Esto reduce drásticamente
  la actividad de disco que provocó la alerta de protección del equipo.

## Desarrollo local

Para iniciar la versión de desarrollo en Windows:

```bat
scripts\run_smouk.bat
```

El detalle de compilación está en
[docs-analysis/08-windows-build-analysis.md](docs-analysis/08-windows-build-analysis.md).
Los parches que permiten reproducir las modificaciones sobre repositorios
limpios de OpenShot están en [patches](patches/README.md).
