# SMOUK patches

This directory contains the modifications SMOUK makes to the upstream OpenShot
repositories. Each patch can be applied with `git am` inside a clean clone of the
corresponding repository.

| Patch | Target repository | Purpose |
|---|---|---|
| `0001-Add-SMOUK-Verticalization-dock-and-top-level-SMOUK-m.patch` | **openshot-qt** | Adds the `Verticalization` dock (`src/windows/verticalization.py`) and registers it in `MainWindow`. |
| `0002-Brand-SMOUK-window-title-and-move-Verticalization-dock.patch` | **openshot-qt** | Sets the window title to `SMOUK by Shadow Coders 0.0.1` and exposes `Verticalization` through `View` → `Docks`. |
| `0003-SMOUK-0.0.2-vertical-project-and-viewer-guide.patch` | **openshot-qt** | Adds the built-in 9:16 vertical project button and the toggleable 9:16 guide overlay in the viewer (`video_widget.py`). |
| `0004-SMOUK-0.0.3-clip-reframing-controls.patch` | **openshot-qt** | Adds per-clip horizontal reframing, optional keyframes, and 4:5/9:16 output-profile selection. |
| `0005-SMOUK-0.0.4-vertical-crop-renderer.patch` | **openshot-qt** | Adds the isolated vertical crop renderer used by SMOUK exports. |
| `0006-SMOUK-0.0.5-explicit-vertical-export-action.patch` | **openshot-qt** | Adds the Verticalization export button and passes its selected preset explicitly to the SMOUK renderer. |
| `0007-SMOUK-0.0.6-ffmpeg-shot-detection.patch` | **openshot-qt** | Adds initial FFmpeg scene-cut detection for an externally selected video. |
| `0001-FFmpeg-9-compatibility-guard-AVCodec-capability-fiel.patch` | **libopenshot** | Guards the `AVCodec` capability fields (`supported_samplerates`, `ch_layouts`, `sample_fmts`, `pix_fmts`) that were removed in FFmpeg 7+, so `FFmpegWriter.cpp` builds against FFmpeg 9. |

## Apply

```sh
# openshot-qt
cd openshot-qt
git am /path/to/patches/0001-Add-SMOUK-*.patch

# libopenshot
cd libopenshot
git am /path/to/patches/0001-FFmpeg-9-*.patch
```
