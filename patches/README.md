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
| `0008-SMOUK-0.0.7-sensitive-shot-detection-and-slicing.patch` | **openshot-qt** | Lowers FFmpeg cut sensitivity and slices the matching selected timeline clip with Keep Both Sides. |
| `0009-SMOUK-0.0.8-one-click-timeline-shot-slicing.patch` | **openshot-qt** | Replaces manual source selection with one-click detection and Keep Both Sides slicing for all timeline videos. |
| `0010-SMOUK-0.0.9-live-reframing-slider.patch` | **openshot-qt** | Synchronizes per-clip reframing, updates it live while dragging, and enlarges the slider handle. |
| `0011-SMOUK-0.0.10-apply-vertical-render-profile.patch` | **openshot-qt** | Applies the complete SMOUK profile to the temporary render timeline before cropping. |
| `0012-SMOUK-0.0.11-fix-crop-and-audio.patch` | **openshot-qt** | Resolves imported media metadata before applying crop and selects an MP4-compatible audio codec for SMOUK exports. |
| `0013-SMOUK-0.0.12-remember-export-folder.patch` | **openshot-qt** | Keeps the most recently used export folder when opening the SMOUK export dialog. |
| `0002-SMOUK-0.0.13-FFmpeg-audio-sample-format.patch` | **libopenshot** | Uses FFmpeg's supported-config API to select the audio encoder sample format on FFmpeg 7+. |
| `0015-SMOUK-0.0.14-enable-guide-with-dock.patch` | **openshot-qt** | Enables the vertical framing guide when the Verticalization dock is shown. |
| `0016-SMOUK-0.0.15-hide-guide-with-dock.patch` | **openshot-qt** | Hides the vertical framing guide when the Verticalization dock is closed. |
| `0017-SMOUK-0.0.16-yunet-auto-reframe.patch` | **openshot-qt** | Adds offline YuNet face detection and CSRT tracking to generate editable framing keyframes. |
| `0018-SMOUK-0.0.17-fix-yunet-tracker-box.patch` | **openshot-qt** | Converts YuNet boxes for OpenCV 5 CSRT tracking and preserves detection-only fallback. |
| `0019-SMOUK-0.0.18-mediapipe-fallback-and-timeline-badge.patch` | **openshot-qt** | Adds MediaPipe face/pose fallback for automatic reframing and an `AI` badge on reframed timeline clips. |
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
