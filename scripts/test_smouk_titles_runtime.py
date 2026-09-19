"""Qt regression checks; optional read-only FFmpeg/Tesseract checks on real media.

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
        self.assertEqual(regions['presenter_left'], (96, 421, 432, 486))
        self.assertEqual(regions['presenter_right'], (528, 421, 825, 486))
        self.assertEqual(regions['pretitle'], (240, 383, 691, 426))
        self.assertEqual(regions['story_headline'], (0, 421, 864, 502))
        self.assertEqual(regions['persistent_headline'], (28, 475, 576, 518))
        for left, top, right, bottom in regions.values():
            self.assertLess(right, 900)  # Leave the TN bug and clock untouched.
            self.assertTrue(0 <= left < right <= 960)
            self.assertTrue(0 <= top < bottom <= 540)

    def test_chyron_graphic_gate_requires_the_expected_template_style(self):
        import cv2
        import numpy
        orange = numpy.full((48, 180, 3), (0, 128, 255), dtype=numpy.uint8)
        black = numpy.zeros((48, 180, 3), dtype=numpy.uint8)
        cv2.putText(black, 'TITOL', (8, 33), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (255, 255, 255), 2)
        self.assertTrue(self.dock._chyron_graphic_present(
            'story_headline', orange, cv2, numpy))
        self.assertFalse(self.dock._chyron_graphic_present(
            'story_headline', black, cv2, numpy))
        self.assertTrue(self.dock._chyron_graphic_present(
            'pretitle', black, cv2, numpy))
        self.assertFalse(self.dock._chyron_graphic_present(
            'location', orange, cv2, numpy))

    def test_clock_phase_uses_repeated_native_second_transitions(self):
        scores = [(frame, 0.0) for frame in range(1, 80)]
        for first in (8, 33, 58):
            for frame in range(first, first + 6):
                scores[frame - 1] = (frame, 10.0)
        self.assertEqual(self.dock._clock_phase_from_differences(scores), 6)
        self.assertEqual(self.dock._clock_phase_from_differences([(1, 2.0)]), 0)

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
        self.dock._on_title_clock_ocr_completed({'error': 'Tesseract timeout'})
        self.assertIn('Tesseract timeout', self.dock.title_folder_results.text())
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
        with patch.object(v, 'available_ocr_language', return_value='cat'), \
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
