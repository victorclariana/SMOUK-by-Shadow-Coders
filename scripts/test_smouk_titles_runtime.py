"""Qt regression checks; optional read-only FFmpeg/PP-OCRv5 checks on real media.

Run with the same MinGW Python as run_smouk.bat. No user project is loaded.
"""
import argparse
import ast
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DLL_HANDLES = [os.add_dll_directory(str(path)) for path in (
    Path(r"C:\msys64\mingw64\bin"), ROOT / "libopenshot/build/src",
    ROOT / "libopenshot-audio/build") if path.is_dir()]
sys.path[:0] = [str(ROOT / "openshot-qt/src"), str(ROOT / "libopenshot/build/bindings/python")]
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["OPENSHOT_QT_API"] = "pyqt5"
from qt_api import QtCore, QApplication, QWidget, QLabel, QPushButton, QProgressBar, QMainWindow, QStatusBar
from windows import verticalization as v
from classes import smouk_titles
from classes import smouk_ppocr

APP = QApplication.instance() or QApplication([])


class TestDock(v.VerticalizationDockContent):
    """Real title callbacks/widgets with project writes replaced by observations."""
    def __init__(self):
        QWidget.__init__(self)
        self.title_clock_progress = QProgressBar(self)
        self.title_clock_status = QLabel(self)
        self.title_folder_results = QLabel(self)
        self.btn_browse_title_folder = QPushButton(self)
        self._title_trace = []
        self._title_busy = False
        self._title_workers = []
        self._title_heartbeat = QtCore.QTimer(self)
        self._title_heartbeat.setInterval(100)
        self._title_heartbeat.timeout.connect(self._on_title_heartbeat)
        self.title_analysis_data = {}
        self.imports = []

    def _clear_generated_title_import(self):
        pass

    def _add_clean_feed_clip(self, *args):
        self.imports.append(args)

    def _subtitle_asset_directory(self):
        return str(ROOT / 'logs/title-runtime-test-assets')


def result_fixture():
    return {"files": {"clean": "CLEAN.mp4", "program": "PROGRAMA.mp4"},
            "clock_probes": {key: {"candidate": True, "seconds": 0} for key in ("clean", "program")},
            "timecodes": {"clip_in_frames": 100, "clip_out_frames": 150}}


def wait_for_workers(dock, seconds=240):
    deadline = time.monotonic() + seconds
    ticks = 0
    while (dock._title_workers or dock._title_busy) and time.monotonic() < deadline:
        APP.processEvents()
        time.sleep(.01)
        ticks += 1
    assert not dock._title_workers, 'Worker timeout'
    assert not dock._title_busy, 'Pipeline did not release busy state'
    return ticks


class TitleRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.window = QMainWindow()
        self.window.statusBar = QStatusBar(self.window)  # OpenShot stores a widget, not a method.
        self.window.setStatusBar(self.window.statusBar)
        self.window.refreshFilesSignal = SimpleNamespace(emit=lambda: None)
        self.window.refreshFrameSignal = SimpleNamespace(emit=lambda: None)
        self.context = SimpleNamespace(
            window=self.window, _tr=lambda value: value,
            project=SimpleNamespace(current_filepath=''))
        self.patch_app = patch.object(v, 'get_app', return_value=self.context)
        self.patch_app.start()
        self.dock = TestDock()

    def tearDown(self):
        self.patch_app.stop()
        self.dock.deleteLater()
        self.window.deleteLater()
        APP.processEvents()

    def test_progress_accepts_openshot_status_widget(self):
        self.dock._title_progress('CLEAN: reading clock', 0, 100)
        self.assertEqual(self.window.statusBar.currentMessage(), 'CLEAN: reading clock')
        self.assertIn('CLEAN: reading clock', self.dock.title_folder_results.text())

    def test_new_project_runtime_cleanup_cannot_delete_a_directory_tree(self):
        source = (ROOT / 'openshot-qt/src/windows/main_window.py').read_text(encoding='utf-8')
        module = ast.parse(source)
        main_window = next(node for node in module.body
                           if isinstance(node, ast.ClassDef) and node.name == 'MainWindow')
        cleanup = next(node for node in main_window.body
                       if isinstance(node, ast.FunctionDef) and node.name == 'clear_temporary_files')
        calls = {node.func.attr for node in ast.walk(cleanup)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        self.assertIn('makedirs', calls)
        self.assertNotIn('rmtree', calls)
        self.assertNotIn('unlink', calls)

    def test_recovery_paths_do_not_archive_or_relocate_project_data(self):
        source = (ROOT / 'openshot-qt/src/windows/main_window.py').read_text(encoding='utf-8')
        module = ast.parse(source)
        main_window = next(node for node in module.body
                           if isinstance(node, ast.ClassDef) and node.name == 'MainWindow')
        methods = {node.name: node for node in main_window.body if isinstance(node, ast.FunctionDef)}
        recovery_calls = {node.func.attr for node in ast.walk(methods['recover_backup'])
                          if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        archive_calls = {node.func.attr for node in ast.walk(methods['save_recovery'])
                         if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        self.assertNotIn('move', recovery_calls)
        self.assertNotIn('ZipFile', archive_calls)

    def test_chyron_hot_zones_exclude_the_central_picture(self):
        regions = self.dock._chyron_regions(960, 540)
        self.assertEqual(regions['live_location'], (28, 48, 297, 91))
        self.assertEqual(regions['presenter_left'], (96, 442, 432, 486))
        self.assertEqual(regions['presenter_right'], (528, 442, 825, 486))
        self.assertEqual(regions['pretitle'], (240, 399, 691, 453))
        self.assertEqual(regions['story_headline'], (0, 415, 892, 507))
        self.assertEqual(regions['persistent_headline'], (28, 475, 576, 518))
        for left, top, right, bottom in regions.values():
            self.assertLess(right, 900)  # Leave the TN bug and clock untouched.
            self.assertTrue(0 <= left < right <= 960)
            self.assertTrue(0 <= top < bottom <= 540)

    def test_text_bands_allow_settled_graphic_animation(self):
        self.assertEqual(self.dock._chyron_signature_threshold('story_headline'), .050)
        self.assertEqual(self.dock._chyron_signature_threshold('pretitle', changed=True), .080)
        self.assertEqual(self.dock._chyron_signature_threshold('presenter_left'), .012)

    def test_chyron_graphic_gate_requires_the_expected_template_style(self):
        import cv2
        import numpy
        orange = numpy.full((48, 180, 3), (0, 128, 255), dtype=numpy.uint8)
        cv2.putText(orange, 'TITOL', (8, 33), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (255, 255, 255), 2)
        black = numpy.zeros((48, 180, 3), dtype=numpy.uint8)
        cv2.putText(black, 'TITOL', (8, 33), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (255, 255, 255), 2)
        pretitle = numpy.full((48, 180, 3), (140, 140, 140), dtype=numpy.uint8)
        cv2.rectangle(pretitle, (38, 7), (142, 41), (35, 35, 35), -1)
        cv2.putText(pretitle, 'TITOL', (48, 32), cv2.FONT_HERSHEY_SIMPLEX,
                    .65, (255, 255, 255), 2)
        self.assertTrue(self.dock._chyron_graphic_present(
            'story_headline', orange, cv2, numpy))
        self.assertFalse(self.dock._chyron_graphic_present(
            'story_headline', black, cv2, numpy))
        self.assertTrue(self.dock._chyron_graphic_present(
            'pretitle', pretitle, cv2, numpy))
        self.assertFalse(self.dock._chyron_graphic_present(
            'pretitle', black, cv2, numpy))
        self.assertFalse(self.dock._chyron_graphic_present(
            'location', orange, cv2, numpy))

    def test_identity_filter_rejects_a_duplicate_all_caps_headline(self):
        self.assertEqual(
            self.dock._normalise_chyron_text('ILLA DEMANA GENEROSITAT EN L\'ACOLLIDA', 'credit'), '')
        self.assertEqual(
            self.dock._normalise_chyron_text('ILLA DEMANA GENEROSITAT EN L\'ACOLLIDA', 'presenter_left'), '')
        self.assertEqual(
            self.dock._normalise_chyron_text('Pilar Abril\nCorresponsal', 'name_cargo'),
            'Pilar Abril\nCorresponsal')

    def test_title_text_filter_rejects_subtitles_and_corrupt_characters(self):
        self.assertEqual(
            self.dock._normalise_chyron_text('i no els traficants de persones.', 'pretitle'), '')
        self.assertEqual(
            self.dock._normalise_chyron_text('EL BAR\ufffdA VOL SEGUIR L\u00cdDER', 'story_headline'), '')
        self.assertEqual(
            self.dock._normalise_chyron_text('CONSELL DE SEGURETAT EUROPEU**', 'persistent_headline'),
            'CONSELL DE SEGURETAT EUROPEU')

    def test_full_width_orange_banner_is_not_a_presenter_label(self):
        import cv2
        import numpy
        banner = numpy.full((48, 180, 3), (0, 128, 255), dtype=numpy.uint8)
        label = numpy.zeros((48, 180, 3), dtype=numpy.uint8)
        label[:, 32:138] = (0, 128, 255)
        self.assertTrue(self.dock._orange_spans_crop(cv2.inRange(
            cv2.cvtColor(banner, cv2.COLOR_BGR2HSV), (2, 115, 115), (28, 255, 255)), numpy))
        self.assertFalse(self.dock._orange_spans_crop(cv2.inRange(
            cv2.cvtColor(label, cv2.COLOR_BGR2HSV), (2, 115, 115), (28, 255, 255)), numpy))

    def test_title_templates_are_assigned_to_separate_review_tracks(self):
        self.assertEqual(self.dock._chyron_track_key('story_headline'), 'story_headline')
        self.assertEqual(self.dock._chyron_track_key('persistent_headline'), 'persistent_headline')
        self.assertEqual(self.dock._chyron_track_key('pretitle'), 'pretitle')
        self.assertEqual(self.dock._chyron_track_key('presenter_left'), 'presenter_left')
        self.assertEqual(self.dock._chyron_track_key('presenter_right'), 'presenter_right')
        self.assertEqual(self.dock._chyron_track_key('name_cargo'), 'name_cargo')
        self.assertEqual(self.dock._chyron_track_key('location'), 'location')

    def test_presenter_signature_ignores_yellow_picture_content(self):
        import cv2
        import numpy
        first = numpy.zeros((60, 180, 3), dtype=numpy.uint8)
        second = first.copy()
        # Stable saturated TNM orange label in both samples.
        cv2.rectangle(first, (42, 30), (150, 54), (0, 128, 255), -1)
        cv2.rectangle(second, (42, 30), (150, 54), (0, 128, 255), -1)
        # A moving yellow garment appears only in the second picture sample.
        cv2.rectangle(second, (0, 0), (90, 30), (0, 220, 240), -1)
        presenter_distance = self.dock._chyron_signature_distance(
            self.dock._chyron_signature(first, cv2, 'presenter_left'),
            self.dock._chyron_signature(second, cv2, 'presenter_left'), numpy)
        generic_distance = self.dock._chyron_signature_distance(
            self.dock._chyron_signature(first, cv2),
            self.dock._chyron_signature(second, cv2), numpy)
        self.assertLessEqual(presenter_distance, v.CHYRON_SIGNATURE_STABLE_DELTA)
        self.assertGreater(generic_distance, presenter_distance)

    def test_presenter_cleanup_keeps_both_names(self):
        self.assertEqual(
            self.dock._normalise_chyron_text('LE Xavi Coral Trullàs —', 'presenter_right'),
            'Xavi Coral Trullàs')

    def test_chyron_selection_does_not_evaluate_reframe_keyframes(self):
        class Slider:
            def __init__(self):
                self.value = None
            def blockSignals(self, _blocked):
                pass
            def setValue(self, value):
                self.value = value
        title = SimpleNamespace(data={'smouk_chyron_clip': True})
        self.dock._reframe_dragging = False
        self.dock.reframe_slider = Slider()
        with patch.object(self.dock, '_selected_clip', return_value=title), \
                patch.object(self.dock, '_clip_frame', side_effect=AssertionError):
            self.dock._sync_reframe_slider()
        self.assertEqual(self.dock.reframe_slider.value, 0)

    def test_clock_phase_uses_repeated_native_second_transitions(self):
        scores = [(frame, 0.0) for frame in range(1, 80)]
        for first in (8, 33, 58):
            for frame in range(first, first + 6):
                scores[frame - 1] = (frame, 10.0)
        self.assertEqual(self.dock._clock_phase_from_differences(scores), 6)
        self.assertEqual(self.dock._clock_phase_from_differences([(1, 2.0)]), 0)

    def test_clock_ffmpeg_resolver_is_available(self):
        """A resolver error must not masquerade as an absent visual clock."""
        with patch.object(smouk_titles.shutil, 'which', return_value=r'C:\\ffmpeg.exe'), \
                patch.object(smouk_titles.os.path, 'isfile', return_value=True):
            self.assertEqual(smouk_titles._ffmpeg_path(), r'C:\\ffmpeg.exe')

    def test_ppocr_protocol_preserves_catalan_characters(self):
        """The helper pipe must not depend on the Windows console code page."""
        class Capture:
            value = ''
            def write(self, text):
                self.value += text
            def flush(self):
                pass
        capture = Capture()
        with patch.object(smouk_ppocr.sys, '__stdout__', capture):
            smouk_ppocr._reply({'text': 'Barça, Masmitjà i Trullàs'})
        self.assertIn('\\u00e7', capture.value)
        self.assertIn('\\u00e0', capture.value)
        self.assertNotIn('ç', capture.value)

    def test_headline_word_mode_joins_the_fixed_tnm_text_band(self):
        import numpy

        band = numpy.full((60, 260, 3), (45, 45, 45), dtype=numpy.uint8)
        # Three separated bright word components in a TNM-style dark band.
        band[18:43, 20:64] = 255
        band[18:43, 88:144] = 255
        band[18:43, 170:238] = 255
        replies = iter([('ELS', .99), ('JAVIS,', .98), ('OSCARS', .97)])
        with patch.object(smouk_ppocr, '_recognize', side_effect=lambda *_args: next(replies)):
            text, confidence = smouk_ppocr._recognize_headline_words(object(), band)
        self.assertEqual(text, 'ELS JAVIS, OSCARS')
        self.assertEqual(confidence, .97)

    def test_button_signal_boolean_is_accepted(self):
        with patch.object(v.QFileDialog, 'getExistingDirectory', return_value=''):
            self.dock._on_browse_title_folder(False)
        self.assertFalse(self.dock._title_busy)

    def test_callback_error_is_visible_and_releases_ui(self):
        self.dock._title_pending_result = {}  # Deliberate malformed worker payload.
        self.dock._title_busy = True
        self.dock.btn_browse_title_folder.setEnabled(False)
        self.dock._on_title_clock_ocr_completed({})
        self.assertIn("Error en _on_title_clock_ocr_completed", self.dock.title_folder_results.text())
        self.assertFalse(self.dock._title_busy)
        self.assertTrue(self.dock.btn_browse_title_folder.isEnabled())

    def test_clock_failure_preserves_reason(self):
        self.dock._title_pending_result = result_fixture()
        self.dock._on_title_clock_ocr_completed({'error': 'PP-OCRv5 timeout'})
        self.assertIn('PP-OCRv5 timeout', self.dock.title_folder_results.text())
        self.assertFalse(self.dock.imports)

    def test_title_scan_error_is_not_reported_as_success(self):
        self.dock._on_title_chyrons_completed({'error': 'FFmpeg incomplete frame'})
        self.assertIn('FFmpeg incomplete frame', self.dock.title_folder_results.text())
        self.assertNotIn('Proceso terminado:', self.dock.title_folder_results.text())

    def test_clock_and_chyron_work_are_off_ui_thread(self):
        worker_threads = []
        def clock(*args):
            worker_threads.append(QtCore.QThread.currentThread() != APP.thread())
            time.sleep(.15)
            return {'frames': 0, 'text': '00:00:00'}
        def scan(*args, **kwargs):
            worker_threads.append(QtCore.QThread.currentThread() != APP.thread())
            time.sleep(.15)
            return []
        class FakePaddleSession:
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                pass
            def read(self, _image, _mode="line"):
                return {'text': '14:30:00', 'confidence': 1.0, 'reason': ''}
        with patch.object(v, 'ppocr_runtime_status', return_value={'available': True}), \
                patch.object(v, 'PaddleOcrSession', FakePaddleSession), \
                patch.object(self.dock, '_ocr_clock_at', side_effect=clock), \
                patch.object(self.dock, '_scan_chyrons', side_effect=scan), \
                patch.object(self.dock, '_place_chyrons', return_value=([], 0)):
            self.dock._run_title_reconstruction(result_fixture())
            self.assertFalse(self.dock.btn_browse_title_folder.isEnabled())
            ticks = wait_for_workers(self.dock)
        self.assertGreater(ticks, 10)
        self.assertEqual(worker_threads, [True, True, True])
        self.assertEqual(len(self.dock.imports), 1)
        self.assertIn('Proceso terminado', self.dock.title_folder_results.text())

    def test_media_bounds_prevent_import(self):
        result = result_fixture()
        result['files']['clean_info'] = {'duration': 2}
        self.dock._title_pending_result = result
        clock = {'frames': 0, 'text': '00:00:00'}
        self.dock._on_title_clock_ocr_completed({'clean': clock, 'program': clock})
        self.assertFalse(self.dock.imports)
        self.assertIn('fuera de CLEAN', self.dock.title_folder_results.text())

    def test_clean_feed_import_completes_timeline_refresh(self):
        """A single title-pipeline import must not retain the wait cursor."""
        calls = []

        class FakeFile:
            id = 'F1'
            data = {'id': 'F1', 'path': 'CLEAN.MP4'}

            @staticmethod
            def get(**_kwargs):
                return FakeFile()

            def absolute_path(self):
                return self.data['path']

        class FakeStoredClip:
            data = {}

            def save(self):
                pass

        class FakeClip:
            @staticmethod
            def get(**_kwargs):
                return FakeStoredClip()

        class FakeReader:
            def __init__(self, _path):
                pass

            def Json(self):
                return '{"id": "C1", "reader": {}}'

        self.context.project = SimpleNamespace(get=lambda _key: 1920)
        self.window.timeline = SimpleNamespace(
            addClip=lambda *args, **kwargs: calls.append(kwargs) or {'id': 'C1'})
        with patch.object(v, 'File', FakeFile), \
                patch.object(v, 'Clip', FakeClip), \
                patch.object(v.openshot, 'Clip', FakeReader):
            v.VerticalizationDockContent._add_clean_feed_clip(
                self.dock, 'CLEAN.MP4', 1, 2, 0)

        self.assertEqual(len(calls), 1)
        self.assertFalse(calls[0]['ignore_refresh'])


def real_media_check(folder):
    from classes.smouk_titles import validate_title_folder
    import cv2
    result = validate_title_folder(str(folder), clock_progress=lambda key, idx, n, total:
                                   print(key, n, '/', total, flush=True) if n % 60 == 0 else None)
    for key, probe in result['clock_probes'].items():
        frame = probe.get('clock_frame')
        if frame is not None:
            cv2.imwrite(str(ROOT / ('logs/accepted-clock-%s.png' % key)), frame)
    dock = TestDock()
    events = []
    worker = v.SmoukClockOcrWorker(dock, result['files'], result['clock_probes'])
    worker.stage.connect(lambda message: print(message, flush=True))
    worker.completed.connect(events.append)
    worker.start()
    ticks = 0
    while worker.isRunning() or not events:
        APP.processEvents()
        time.sleep(.01)
        ticks += 1
    print('REAL_CLOCK_RESULT', json.dumps(events, ensure_ascii=False), 'UI ticks:', ticks, flush=True)
    assert not events[0].get('error'), events
    worker.wait()
    # Exercise the throttled, in-memory OCR scan on real news footage.
    scan_events = []
    scan = v.SmoukChyronOcrWorker(dock, (result['files']['program'], 118, 30, 0, 0,
                                          str(ROOT / 'logs/title-runtime-test-assets/real')))
    scan.stage.connect(lambda message, value, maximum: print(message, flush=True))
    scan.completed.connect(scan_events.append)
    scan.start()
    while scan.isRunning() or not scan_events:
        APP.processEvents()
        time.sleep(.01)
        ticks += 1
    scan.wait()
    assert not scan_events[0].get('error'), scan_events
    assert len(scan_events[0]['events']) <= v.MAX_CHYRON_EVENTS
    print('REAL_CHYRON_RESULT', len(scan_events[0]['events']), 'events; UI ticks:', ticks, flush=True)
    (ROOT / 'logs/title-runtime-result.json').write_text(json.dumps(
        {'clocks': events, 'scan': scan_events,
         'validation': {'valid': result['valid'], 'timecodes': result['timecodes']}},
        ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--media-folder', type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TitleRuntimeTests)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    if not outcome.wasSuccessful():
        raise SystemExit(1)
    if args.media_folder:
        real_media_check(args.media_folder)
