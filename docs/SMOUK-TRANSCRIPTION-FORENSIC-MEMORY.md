# Memoria forense permanente de subtitulado

## Fallo Qt5Core tras BSC (SMOUK 0.0.107–0.0.108)

El proceso BSC terminaba correctamente: el audio del IN–OUT se extraía, los
timecodes se validaban y el JSON bruto se guardaba. El crash sucedía al entrar
en la preparación de la revisión ParlaBE, antes de lanzar el proceso ParlaBE y
antes de crear la ventana.

Windows registró repetidamente `python.exe` (`C:\msys64\mingw64\bin\python.exe`)
con módulo fallido `Qt5Core.dll` 5.15.19 y excepción `0xc0000602`. No era una
excepción Python ni un error del modelo BSC. El detonante reproducible era una
mutación de un widget Qt (`transcription_results.setText`) en la frontera que
seguía a la inferencia nativa. El uso de `QDialog.exec_()` en esa misma ruta
añadía además un bucle de eventos anidado inseguro.

La regla permanente es: después de la inferencia BSC no se deben modificar
widgets desde el drenaje del proceso ni desde la primera transición de salida;
se debe esperar a que el lector y el proceso terminen, cruzar un límite del
bucle Qt y usar `QDialog.open()` con señales. Los estados visibles deben ser
coarse y programados en fases seguras; el detalle completo se conserva en
`openshot-qt.log`.

## Regla permanente de tipografía

La tipografía de subtítulos conserva siempre la misma medida vertical, relleno
blanco al 100% y borde negro de 2.9 px. Una línea excepcionalmente larga puede
comprimirse solo en horizontal para respetar la guía 9:16; nunca se reduce la
medida de la fuente de una pantalla respecto de otra.

La distribución debe resolver el espacio mediante saltos de palabra y
puntuación dentro de una o dos filas. Si una corrección manual hace crecer la
frase, sus palabras se reparten entre los intervalos temporales disponibles
antes de crear los clips. Nunca se debe deformar horizontalmente la fuente.

Cuando el texto corregido no cabe en dos filas, se divide en nuevos intervalos
temporales interpolados dentro del intervalo original, conservando el orden y
la sincronía de la voz. El SVG nunca recibe una tercera fila ni una fuente
comprimida.

Para el perfil 9:16 la medida fija de referencia es 40.5 px, con un máximo de
22 caracteres por fila y 44 por pantalla. Esta medida no se reduce para
acomodar frases: se crean más pantallas sincronizadas cuando es necesario.
