"""Render real Tk widgets and invoke owner flow with synthetic data only.

Run with a graphical display: `xvfb-run -a python scripts/gui_smoke.py`.
A pass on Linux/Xvfb is NOT evidence of native Windows/NTFS/Defender QA.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def smoke() -> dict:
    import tkinter as tk
    from tkinter import ttk, filedialog
    from factoryax.gui import launch
    from factoryax.delivery import verify_candidate

    with tempfile.TemporaryDirectory(prefix='factoryax-gui-synthetic-') as tmp:
        work = Path(tmp)
        subprocess.run([sys.executable, str(BASE / 'examples/make_reconcile_synthetic.py'),
                        str(work / 'inputs')], check=True, capture_output=True)
        spec = work / 'inputs' / 'approved.json'
        original = {p: _sha(p) for p in (work / 'inputs' / 'input').iterdir() if p.is_file()}
        dest = work / 'GUI-검수-1'
        observed = {'windows': 0, 'clicks': 0}

        def examine(root: tk.Tk) -> None:
            observed['windows'] += 1
            try:
                assert 'Factory AX' in root.title()
                root.update_idletasks()
                assert root.winfo_width() >= 540
                assert root.winfo_height() >= 380
                widgets = []

                def visit(node):
                    for widget in node.winfo_children():
                        widgets.append(widget)
                        visit(widget)
                visit(root)
                inputs = [widget for widget in widgets if isinstance(widget, ttk.Entry)]
                buttons = [widget for widget in widgets
                           if isinstance(widget, ttk.Button) and widget.cget('text') == '읽기 전용 검수 실행']
                results = [widget for widget in widgets if isinstance(widget, tk.Text)]
                assert len(inputs) == 2 and len(buttons) == 1 and len(results) == 1
                parent_buttons = [w for w in widgets if isinstance(w, ttk.Button)
                                  and w.cget('text') == '상위 폴더 선택']
                assert len(parent_buttons) == 1
                # Directory dialog cancellation must not choose the filesystem root.
                with patch.object(filedialog, 'askdirectory', return_value=''):
                    parent_buttons[0].invoke()
                assert inputs[1].get() == ''
                inputs[0].insert(0, str(spec))
                inputs[1].insert(0, str(dest))
                buttons[0].invoke()
                observed['clicks'] += 1
                assert '검수: OK' in results[0].get('1.0', 'end')
                assert verify_candidate(dest)['status'] == 'OK'
                # Double-click should be fail-closed: no overwrite or delete.
                before = _sha(dest / 'result.json')
                buttons[0].invoke()
                observed['clicks'] += 1
                assert 'BLOCKED: OUTPUT_EXISTS_NO_OVERWRITE' in results[0].get('1.0', 'end')
                assert '검수: OK' not in results[0].get('1.0', 'end')
                assert _sha(dest / 'result.json') == before
            finally:
                root.destroy()

        with patch.object(tk.Tk, 'mainloop', examine):
            launch()
        assert observed == {'windows': 1, 'clicks': 2}
        assert all(_sha(path) == sha for path, sha in original.items())
    return {'status': 'GUI_SYNTHETIC_PASS', 'platform': sys.platform,
            'tk_real_widgets': 1, 'button_invocations': 2, 'inputs_unchanged': True,
            'native_windows_verified': False, 'release': 'HOLD'}


if __name__ == '__main__':
    try:
        print(json.dumps(smoke(), ensure_ascii=False, sort_keys=True))
    except Exception as exc:
        print(json.dumps({'status': 'GUI_SYNTHETIC_FAIL', 'type': type(exc).__name__,
                          'reason': str(exc), 'release': 'HOLD'}))
        raise
