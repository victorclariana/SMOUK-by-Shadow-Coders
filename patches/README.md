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
| `0020-SMOUK-0.0.19-yolo-onnx-object-reframing.patch` | **openshot-qt** | Bundles YOLO11n ONNX and uses OpenCV DNN object detections as an automatic reframing fallback. |
| `0021-SMOUK-0.0.20-fix-yolo-dock-reference.patch` | **openshot-qt** | Fixes the YOLO loader's reference to the Verticalization dock class. |
| `0022-SMOUK-0.0.21-source-fps-accurate-shot-slicing.patch` | **openshot-qt** | Keeps FFmpeg shot cuts on each source video's native frame boundaries instead of rounding them to project FPS. |
| `0023-SMOUK-0.0.22-persist-ui-layout-checkpoints.patch` | **openshot-qt** | Persists the window geometry and dock layout on close and via debounced, periodic checkpoints to survive native crashes. |
| `0024-SMOUK-0.0.23-conservative-auto-reframing.patch` | **openshot-qt** | Makes automatic reframing prefer a fixed median crop and only create slow linear keyframes for a clear sustained one-way pan. |
| `0025-SMOUK-0.0.24-clamp-vertical-crop-bounds.patch` | **openshot-qt** | Clamps timeline reframing and the final crop-render coordinates to prevent black edge strips. |
| `0026-SMOUK-0.0.25-exclude-first-frame-of-next-shot.patch` | **openshot-qt** | Treats FFmpeg's detected frame as the right-shot start and excludes it from OpenShot's inclusive left clip end. |
| `0027-SMOUK-0.0.26-restore-layout-PAL-default-and-anamorph.patch` | **openshot-qt** | Restores the saved dock layout after window mapping, defaults new projects to FHD PAL 1080i 25 fps, and expands detected 1440x1080 anamorphic media to 16:9. |
| `0028-SMOUK-0.0.27-frame-exact-cuts-and-final-layout-resto.patch` | **openshot-qt** | Uses one shared source/timeline boundary for frame-contiguous shot cuts, restores docks only after the final native window state, and persists the selected vertical preset. |
| `0029-SMOUK-0.0.28-catalan-transcription.patch` | **openshot-qt** | Adds one-click offline Catalan transcription with progress and applies tagged, editable Caption effects to every matching timeline clip. |
| `0030-SMOUK-0.0.29-faster-catalan-transcription.patch` | **openshot-qt** | Bumps SMOUK to 0.0.29 and tests the adaptive CPU-thread policy used by the faster Catalan transcription worker. |
| `0031-SMOUK-0.0.30-vertical-caption-layout.patch` | **openshot-qt** | Places generated captions after clip transforms, constrains their preview to the active vertical guide, and converts their typography to the final 1080px export canvas. |
| `0032-SMOUK-0.0.31-balanced-transcription-and-thin-caption.patch` | **openshot-qt** | Uses the balanced three-hypothesis Catalan transcription profile and reduces generated Caption outlines to a thin vertical-safe stroke. |
| `0033-SMOUK-0.0.32-bold-generated-captions.patch` | **openshot-qt** | Selects Arial Bold for captions created by the Verticalization transcription workflow and bumps SMOUK to 0.0.32. |
| `0034-SMOUK-0.0.32-bold-caption-font.patch` | **libopenshot** | Interprets a ` Bold` font suffix as a real Qt bold weight while preserving the requested font family and thin outline. |
| `0035-SMOUK-0.0.33-two-line-subtitle-cues.patch` | **openshot-qt** | Bumps SMOUK to 0.0.33 for the companion transcription-worker change that limits generated subtitle cues to two safe-width lines. |
| `0036-SMOUK-0.0.34-fix-caption-cues-and-progress.patch` | **openshot-qt** | Removes SRT cue indices from rendered captions, increases font size by two points, and reports recognition/finalization progress. |
| `0037-SMOUK-0.0.35-subtitle-timeline-clips.patch` | **openshot-qt** | Creates independent editable subtitle title clips on a track above the video, uses a heavy Arial Black face, and bumps SMOUK to 0.0.35. |
| `0038-SMOUK-0.0.36-deinterlace-reframing-analysis.patch` | **openshot-qt** | Deinterlaces analysis-only frames with FFmpeg `bwdif` so the reframer can detect subjects in interlaced media, and logs per-clip sample/detection counts. |
| `0039-SMOUK-0.0.37-transparent-logo-overlay.patch` | **openshot-qt** | Adds transparent PNG browsing, validation, and a full-duration editable logo clip on the dedicated top `SMOUK Logo` track. |
| `0040-SMOUK-0.0.38-logo-opacity-control.patch` | **openshot-qt** | Adds a 0–100% opacity slider in the Logo dock and persists Alpha keyframes for the selected logo clip. |
| `0041-SMOUK-0.0.39-logo-opacity-startup-guard.patch` | **openshot-qt** | Guards the logo opacity synchronization callback during dock construction and startup state restoration. |
| `0042-SMOUK-0.0.40-delay-logo-sync-connections.patch` | **openshot-qt** | Connects timeline selection synchronization only after the Verticalization dock controls are fully constructed. |
| `0043-SMOUK-0.0.41-safe-logo-opacity-startup.patch` | **openshot-qt** | Removes startup-time logo opacity synchronization while retaining direct Alpha editing for the selected logo clip. |
| `0044-SMOUK-0.0.42-title-analysis-folder-validation.patch` | **openshot-qt** | Adds the first title-analysis workflow step: validates `CLEAN.MP4`, `DATA.JSON` and `PROGRAMA.MP4`, converts JSON cuts to 25-fps frames, and probes for a visual clock without changing the project. |
| `0045-SMOUK-0.0.43-stable-verticalization-dock.patch` | **openshot-qt** | Starts Verticalization sections collapsed to avoid an unstable tall-dock relayout while scrolling on the current Windows Qt build. |
| `0046-SMOUK-0.0.44-safe-dock-relayout.patch` | **openshot-qt** | Restores all Verticalization sections open by default and prevents Qt dock-state serialization during content-driven resize events, avoiding the `Qt5Core.dll` fail-fast crash. |
| `0047-SMOUK-0.0.45-two-track-compact-timeline.patch` | **openshot-qt** | Starts new SMOUK projects with two tracks and migrates the default Timeline to the theme-aware height needed for its toolbar, ruler, and two tracks. |
| `0048-SMOUK-0.0.46-title-folder-legend-tall-tracks.patch` | **openshot-qt** | Displays the required title-analysis filenames in the dock and doubles the default Cosmic Timeline row height, recalibrating the compact two-track layout. |
| `0049-SMOUK-0.0.47-three-minute-clock-scan.patch` | **openshot-qt** | Scans the first three minutes of both CLEAN.MP4 and PROGRAMA.MP4 at one 25-fps-aligned sample per second, reporting clock candidates for each feed. |
| `0050-SMOUK-0.0.48-ffmpeg-clock-reference-detector.patch` | **openshot-qt** | Uses FFmpeg to extract broadcast MP4 samples and detects the reference clock through its white numerals and saturated orange panels. |
| `0051-SMOUK-0.0.49-clock-progress-and-false-positive-fix.patch` | **openshot-qt** | Adds live two-video clock-scan progress in the Titles dock and requires a large orange clock-panel footprint to reject false positives. |
| `0052-SMOUK-0.0.50-clock-colour-shape-signature.patch` | **openshot-qt** | Uses the reference clock's total orange coverage and largest contiguous orange panel to reject programme-ident false positives. |
| `0053-SMOUK-0.0.51-reference-template-clock-matching.patch` | **openshot-qt** | Extracts the CLEAN clock reference near 01:23 and combines colour, geometry, area, aspect, OpenCV template matching, and temporal persistence for final clock detection. |
| `0054-SMOUK-0.0.52-automatic-ocr-title-import.patch` | **openshot-qt** | Runs clock OCR and feed synchronisation after selecting a valid folder, imports the calculated CLEAN interval in Track 2, and reconstructs stable title-region OCR results as editable SVG clips in `CHYRONS`. |
| `0055-SMOUK-0.0.53-asynchronous-clock-ocr-trace.patch` | **openshot-qt** | Moves FFmpeg and Tesseract clock OCR off the Qt UI thread and adds a visible per-stage Titles trace plus log diagnostics. |
| `0056-SMOUK-0.0.54-title-statusbar-crash-fix.patch` | **openshot-qt** | Fixes the reproduced non-callable QStatusBar crash before OCR startup, guards Qt callbacks, preserves error diagnostics, moves chyron analysis off the UI thread, and reads the accepted clock frames with local English digit OCR. |
| `0057-SMOUK-0.0.55-safe-chyron-candidates.patch` | **openshot-qt** | Prevents per-frame false chyron creation through throttled, persistent text candidates, a hard title limit, and one reusable OCR cache image instead of per-frame temporary files. |
| `0058-SMOUK-0.0.56-hot-zone-catalan-chyron-ocr.patch` | **openshot-qt** | Restricts title OCR to TNM's upper-left and lower title bands, uses stable visual masks to OCR each title once in Catalan, and bumps SMOUK to 0.0.56. |
| `0059-SMOUK-0.0.57-isolate-unstable-chyron-backups.patch` | **openshot-qt** | Preserves and isolates recovery backups containing an unsafe number of legacy generated chyrons so New, Open, and Save start from a stable project. |
| `0060-SMOUK-0.0.58-save-project-on-qt-thread.patch` | **openshot-qt** | Keeps Save As and autosave on the Qt thread because OpenShot project assets are not safe to migrate from detached Python threads, and balances the save cursor. |
| `0061-SMOUK-0.0.59-corporate-safe-project-save.patch` | **openshot-qt** | Makes SMOUK save only its plain JSON project file, without ZIP recovery archives or bulk temporary-asset migration that endpoint protection can classify as unauthorised encryption. |
| `0062-SMOUK-0.0.60-release-title-import-wait-cursor.patch` | **openshot-qt** | Completes the Timeline refresh transaction after individual CLEAN and logo insertion so the global wait cursor cannot remain active after title analysis. |
| `0063-SMOUK-0.0.61-frame-accurate-title-sync.patch` | **openshot-qt** | Calibrates the native clock phase in CLEAN and PROGRAMA, restricts lower-third OCR to the actual graphic, and refines each confirmed chyron's entry and exit with 25-fps template matching. |
| `0064-SMOUK-0.0.62-manual-title-zones.patch` | **openshot-qt** | Applies TNM's manual title zones, excludes picture/logo/clock/subtitle areas, separates simultaneous title templates with graphic gates, and reports title-boundary refinement and editable-clip creation. |
| `0065-SMOUK-0.0.63-nondestructive-project-lifecycle.patch` | **openshot-qt** | Removes recursive runtime cleanup and ZIP recovery from startup/New/Open flows, skips automatic recovery of generated-title backups without relocating them, and records an explicit New Project safely. |
| `0066-SMOUK-0.0.64-title-template-overlap-and-ocr-fix.patch` | **openshot-qt** | Separates TNM pretitle/headline bands, restores block OCR for title strips, and rejects all-caps/full-width-banner results from person and byline templates to prevent duplicate chyrons. |
| `0067-SMOUK-0.0.65-pretitle-validation-and-review-tracks.patch` | **openshot-qt** | Rejects full-width headline bands masquerading as compact pretitles and places headline, pretitle, people, and location chyrons on separate Timeline review tracks. |
| `0068-SMOUK-0.0.66-settled-identity-ocr-and-template-tracks.patch` | **openshot-qt** | Uses the saturated TNM graphic to OCR settled presenter labels without moving picture content, prevents presenter/name-cargo duplicates, and assigns every chyron template its own review track. |
| `0069-SMOUK-0.0.67-safe-chyron-selection-and-presenter-ocr.patch` | **openshot-qt** | Keeps SVG chyron selections out of the video reframe path and uses tailored OCR modes to read both TNM presenter labels reliably. |
| `0070-SMOUK-0.0.68-ppocrv5-title-recognition.patch` | **openshot-qt** | Replaces the prior title and clock recognizer with the isolated local PP-OCRv5 Latin model, preserving TNM visual gates and 25-fps boundaries while sending crops over an in-memory helper protocol. |
| `0071-SMOUK-0.0.69-608x1080-native-height-output.patch` | **openshot-qt** | Adds 608×1080 nominal 9:16 profiles at 25/30 fps, makes 25 fps the default dock selection, and uses the exact 608:1080 canvas ratio in preview and export. |
| `0072-SMOUK-0.0.70-fix-clock-reference-ffmpeg-resolver.patch` | **openshot-qt** | Restores the FFmpeg resolver used by visual-clock reference extraction, reports a resolver error rather than a false absent-clock result, and adds a regression test. |
| `0073-SMOUK-0.0.71-unicode-safe-quality-chyron-ocr.patch` | **openshot-qt** | Preserves Catalan Unicode through the local PP-OCRv5 pipe, prevents final-glyph clipping in the TNM headline zone, and accepts only settled, confident title graphics. |
| `0074-SMOUK-0.0.72-segmented-tnm-title-bands.patch` | **openshot-qt** | Segments the fixed TNM headline and pretitle bands into individual words before PP-OCRv5 recognition, includes the full large-title geometry, and tolerates their settled entrance animation. |
| `0075-SMOUK-0.0.73-persistent-title-continuity.patch` | **openshot-qt** | Bridges brief OCR blind spots in a same-topic persistent TNM label and removes the `àas` presenter-name artifact. |
| `0076-SMOUK-0.0.74-vertical-safe-multiline-headlines.patch` | **openshot-qt** | Places large TNM story headlines inside the centred 9:16 active guide, wraps them by words over multiple lines, and clips their SVG output to that safe area. |
| `0077-SMOUK-0.0.75-vertical-safe-chyron-layout.patch` | **openshot-qt** | Composes every editable chyron inside the 9:16 active guide and assigns distinct vertical lanes to concurrent editorial graphics. |
| `0078-SMOUK-0.0.76-split-source-and-title-workflows.patch` | **openshot-qt** | Separates CLEAN source validation/import from PROGRAM chyron detection, reorganizes the dock controls, and keeps the 9:16 guide enabled by default. |
| `0079-SMOUK-0.0.77-source-progress-heartbeat.patch` | **openshot-qt** | Keeps Source Video and Titles progress clocks independent, preventing Source clock analysis from emitting a Titles error. |
| `0080-SMOUK-0.0.78-centred-vertical-logo.patch` | **openshot-qt** | Centres proportional vertical PNG logo clips in the active 9:16 guide rather than the left edge of the 16:9 edit canvas. |
| `0081-SMOUK-0.0.79-title-subtitle-safe-bands.patch` | **openshot-qt** | Assigns separate vertical guide bands to subtitles, locations, identities, pretitles, and headlines to prevent on-screen overlap. |
| `0088-SMOUK-0.0.86-local-proxy-bypass.patch` | **scripts / openshot-qt** | Bypasses corporate proxies for OpenShot's loopback thumbnail server, preventing repeated proxy failures and native Qt instability. |
| `0089-SMOUK-0.0.87-openvino-turbo-transcription.patch` | **openshot-qt / scripts** | Replaces remote transcription with the local OpenVINO Whisper Large-v3 Turbo INT4 worker, Intel GPU selection, 60-second chunks, and the existing JSON/SRT/VTT subtitle contract. |
| `0090-SMOUK-0.0.88-openvino-cpu-isolation.patch` | **openshot-qt / scripts** | Keeps OpenVINO inference on CPU by default so the Qt preview and Intel graphics stack are isolated. |
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
