# FASE 1 — Verificación de repositorios y versiones

> Documento generado únicamente con comandos Git de lectura.
> No se modificó ningún archivo de los repositorios oficiales.

---

## 1. Resumen ejecutivo

Los tres componentes del proyecto OpenShot están clonados desde sus repositorios
oficiales de GitHub y se encuentran **todos en la rama `develop`** (rama de
desarrollo), con el árbol de trabajo limpio y sincronizados con `origin/develop`.

Ninguno de los tres repositorios está en una etiqueta exacta: están ligeramente
**por delante** de sus respectivas etiquetas de lanzamiento más recientes.

| Componente | Rama | Etiqueta más cercana | Commits sobre la etiqueta | Commit actual | Estado |
|---|---|---|---|---|---|
| openshot-qt | develop | `v4.0.0` | 23 | `4cabe0231` | limpio |
| libopenshot | develop | `v1.0.0` | 16 | `772e6794` | limpio |
| libopenshot-audio | develop | `v1.0.0` | 1 | `2819b3b` | limpio |

---

## 2. openshot-qt

- **Nombre:** openshot-qt (aplicación de escritorio / interfaz de usuario).
- **Ruta local:** `D:\SMOUK by Shadow Coders\openshot-qt`
- **URL remota (origin):**
  - fetch: `https://github.com/OpenShot/openshot-qt.git`
  - push: `https://github.com/OpenShot/openshot-qt.git`
- **Rama activa:** `develop`
- **Commit actual:** `4cabe02317f0cd4f1d2ce33555ceee940251ac3a`
  - Asunto: `Merge pull request #6117 from OpenShot/banner-translations`
  - Autor: Jonathan Thomas
  - Fecha: 2026-09-09 14:32:16 -0500
- **Etiqueta asociada (describe):** `v4.0.0-23-g4cabe0231`
  - Es decir, 23 commits por delante de la etiqueta `v4.0.0`.
- **Estado del working tree:** limpio (`nothing to commit, working tree clean`),
  sincronizado con `origin/develop`.
- **Submódulos declarados:** ninguno (el comando `git submodule status` no
  devuelve ninguna entrada).
- **Submódulos inicializados/ausentes:** no aplica (no hay submódulos).
- **Posible versión del componente:** 4.0.0 (desarrollo posterior a `v4.0.0`).
- **Estable o desarrollo:** rama de **desarrollo**.

### Evidencia

- Rama: `git branch --show-current` → `develop`.
- Remoto: `git remote -v` → `https://github.com/OpenShot/openshot-qt.git`.
- Descripción: `git describe --tags --always` → `v4.0.0-23-g4cabe0231`.
- Commit: `git log -1 --oneline` → `4cabe0231 ... Merge pull request #6117 ...`.
- Limpieza: `git status` → `nothing to commit, working tree clean`.
- Sin submódulos: `git submodule status` → salida vacía.

---

## 3. libopenshot

- **Nombre:** libopenshot (motor de edición de vídeo, C++).
- **Ruta local:** `D:\SMOUK by Shadow Coders\libopenshot`
- **URL remota (origin):**
  - fetch: `https://github.com/OpenShot/libopenshot.git`
  - push: `https://github.com/OpenShot/libopenshot.git`
- **Rama activa:** `develop`
- **Commit actual:** `772e6794353bebea50ff54337339237cfff3cbd4`
  - Asunto: `Merge pull request #1095 from OpenShot/ffmpeg-prefix-mac`
  - Autor: Jonathan Thomas
  - Fecha: 2026-09-09 21:11:09 -0500
- **Etiqueta asociada (describe):** `v1.0.0-16-g772e6794`
  - Es decir, 16 commits por delante de la etiqueta `v1.0.0`.
- **Estado del working tree:** limpio (`nothing to commit, working tree clean`),
  sincronizado con `origin/develop`.
- **Submódulos declarados:** 1
  - Ruta: `external/godot-cpp`
  - URL: `https://github.com/godotengine/godot-cpp`
- **Submódulos inicializados/ausentes:**
  - El submódulo `external/godot-cpp` está **declarado pero NO inicializado**.
  - Evidencia: `git submodule status` devuelve:
    `-b0e3b1e4b78a606f48d162898afb5eeda533d2a9 external/godot-cpp`
  - El prefijo `-` indica que el submódulo no está clonado/inicializado en el
    árbol de trabajo.
  - Evidencia adicional: `libopenshot\.gitmodules` contiene únicamente la entrada
    `[submodule "external/godot-cpp"]`.
- **Posible versión del componente:** 1.0.0 (desarrollo posterior a `v1.0.0`).
- **Estable o desarrollo:** rama de **desarrollo**.

### Evidencia

- Rama: `git branch --show-current` → `develop`.
- Remoto: `git remote -v` → `https://github.com/OpenShot/libopenshot.git`.
- Descripción: `git describe --tags --always` → `v1.0.0-16-g772e6794`.
- Commit: `git log -1 --oneline` → `772e6794 ... Merge pull request #1095 ...`.
- Limpieza: `git status` → `nothing to commit, working tree clean`.
- Submódulo declarado: `libopenshot\.gitmodules` → entrada `external/godot-cpp`.
- Submódulo no inicializado: `git submodule status` → `-b0e3b1e4... external/godot-cpp`.

---

## 4. libopenshot-audio

- **Nombre:** libopenshot-audio (motor de audio, C++, basado en JUCE).
- **Ruta local:** `D:\SMOUK by Shadow Coders\libopenshot-audio`
- **URL remota (origin):**
  - fetch: `https://github.com/OpenShot/libopenshot-audio.git`
  - push: `https://github.com/OpenShot/libopenshot-audio.git`
- **Rama activa:** `develop`
- **Commit actual:** `2819b3bf8518d1844713513804df5bfc927aaa86`
  - Asunto: `Merge pull request #170 from OpenShot/release-20260725`
  - Autor: Jonathan Thomas
  - Fecha: 2026-08-30 21:37:30 -0500
- **Etiqueta asociada (describe):** `v1.0.0-1-g2819b3b`
  - Es decir, 1 commit por delante de la etiqueta `v1.0.0`.
- **Estado del working tree:** limpio (`nothing to commit, working tree clean`),
  sincronizado con `origin/develop`.
- **Submódulos declarados:** ninguno (`git submodule status` devuelve salida vacía).
- **Submódulos inicializados/ausentes:** no aplica.
- **Posible versión del componente:** 1.0.0 (desarrollo posterior a `v1.0.0`).
- **Estable o desarrollo:** rama de **desarrollo**.

### Evidencia

- Rama: `git branch --show-current` → `develop`.
- Remoto: `git remote -v` → `https://github.com/OpenShot/libopenshot-audio.git`.
- Descripción: `git describe --tags --always` → `v1.0.0-1-g2819b3b`.
- Commit: `git log -1 --oneline` → `2819b3b ... Merge pull request #170 ...`.
- Limpieza: `git status` → `nothing to commit, working tree clean`.
- Sin submódulos: `git submodule status` → salida vacía.

---

## 5. Correspondencia entre los tres componentes

- Los tres repositorios están en la **misma rama de desarrollo** (`develop`) y
  sincronizados con sus respectivos `origin/develop`.
- Las etiquetas de lanzamiento más recientes de cada repositorio son:
  - `openshot-qt`: `v4.0.0`
  - `libopenshot`: `v1.0.0`
  - `libopenshot-audio`: `v1.0.0`
- Esta combinación (`openshot-qt 4.0.0` + `libopenshot 1.0.0` +
  `libopenshot-audio 1.0.0`) es consistente con la línea de lanzamiento
  principal de OpenShot: la interfaz `openshot-qt` ha mantenido su esquema de
  versionado propio (3.x → 4.0.0), mientras que las dos bibliotecas nativas
  adoptaron `1.0.0` en esta generación.
- Los tres repositorios se comprobaron en el mismo punto temporal (commits del
  2026-08-30 a 2026-09-09), lo que sugiere una instantánea de desarrollo
  coherente en el tiempo.

### Compatibilidad

- **Conclusión:** los tres componentes son **mutuamente compatibles** en el
  sentido de que pertenecen a la misma generación de desarrollo y están
  sincronizados temporalmente.
- **Salvedad:** la compatibilidad exacta de ABI/API entre `openshot-qt` y
  `libopenshot`/`libopenshot-audio` **no se puede afirmar solo con Git** y se
  verificará en fases posteriores (Fases 4–7) leyendo el código de los bindings
  Python y las comprobaciones de versión en tiempo de ejecución.
- No se modificó ninguna rama ni etiqueta, tal y como exige la regla principal.

---

## 6. Observaciones y riesgos detectados en esta fase

1. **Submódulo `external/godot-cpp` no inicializado en `libopenshot`.**
   - Está declarado en `.gitmodules` pero no clonado.
   - Implicación: cualquier compilación que dependa de ese submódulo fallará o
     lo omitirá hasta que se inicialice (`git submodule update --init`), acción
     que **no se realizará en esta fase**.
   - Se investigará en fases posteriores qué funcionalidad de `libopenshot`
     depende de `godot-cpp`.
2. **Todos los repositorios están en `develop`**, no en una etiqueta de release.
   - Es esperable en un entorno de trabajo activo, pero implica que el código
     analizado puede diferir del último instalador estable publicado.

---

## 7. Comandos Git ejecutados (todos de lectura)

Para cada repositorio:

```text
git status
git remote -v
git branch --show-current
git describe --tags --always
git log -1 --oneline
git log -1 --format='%H%n%ad%n%an%n%s' --date=iso
git submodule status
git tag --sort=-creatordate
```

Además, para `libopenshot`:

```text
git config -f .gitmodules --list
```

No se ejecutó ningún comando que modificara ramas, etiquetas, commits, remotos,
submódulos, dependencias o el sistema operativo.
