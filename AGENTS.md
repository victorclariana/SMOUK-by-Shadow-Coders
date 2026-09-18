# Instrucciones permanentes de SMOUK

Para cada cambio funcional o corrección realizada en este proyecto:

1. Incrementar la versión de SMOUK en `openshot-qt/src/windows/main_window.py`.
2. Actualizar `README.md` y `patches/README.md` con la nueva versión y el parche reproducible cuando corresponda.
3. Registrar los cambios en Git y subirlos a GitHub, rama `main`, usando el remoto `origin`.
4. Ejecutar `scripts/run_smouk.bat` al terminar para que el usuario pueda ver los cambios en el programa.
5. Ejecutar las comprobaciones adecuadas antes de informar de que el cambio está terminado.

No guardar ni modificar proyectos multimedia del usuario durante la validación salvo que lo solicite expresamente.

## Descargas y seguridad

Antes de descargar, reinstalar o actualizar cualquier dependencia, herramienta o modelo externo:

1. Usar la fuente oficial del proyecto o un canal de distribución mantenido por su editor.
2. Verificar la firma criptográfica, el checksum publicado o ambos cuando estén disponibles.
3. Revisar los avisos de seguridad y los informes públicos recientes del repositorio oficial antes de incorporarlo.
4. No continuar si la procedencia o la verificación no son satisfactorias; informar del bloqueo y de la evidencia disponible.
