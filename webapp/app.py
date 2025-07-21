import os
import re
from flask import Flask, render_template, send_from_directory, abort
from charset_normalizer import from_bytes
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

LOG_ROOT = Path(os.environ.get('LOG_ROOT', 'logs')).resolve()
FILE_RE = re.compile(r"^[0-9]{8}\.out$")


def hexdump(data: bytes) -> str:
    """Return a hexdump style string similar to `xxd -C`."""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_bytes = ' '.join(f"{b:02x}" for b in chunk)
        ascii_repr = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"{i:08x}  {hex_bytes:<47}  |{ascii_repr}|")
    return "\n".join(lines)


def read_file_validated(path: Path) -> str:
    """Return text from path or a hexdump if not valid text."""
    data = path.read_bytes()
    if not data:
        return ""
    try:
        best = from_bytes(data).best()
        if best and best.encoding:
            return best.str()
    except Exception:
        pass
    return hexdump(data)


def find_log_dirs():
    """Return mapping of normalized directory keys to lists of log Paths."""
    log_dirs = {}
    for path in LOG_ROOT.rglob('*'):
        if path.is_file() and FILE_RE.match(path.name):
            rel_dir = path.parent.relative_to(LOG_ROOT).as_posix()
            key = rel_dir.upper()
            log_dirs.setdefault(key, []).append(path)
    for files in log_dirs.values():
        files.sort()
    return log_dirs


def collect_logs(dir_key):
    """Collect all .out files for a normalized directory key."""
    key = dir_key.upper()
    matches = []
    for path in LOG_ROOT.rglob('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].out'):
        rel_dir = path.parent.relative_to(LOG_ROOT).as_posix().upper()
        if rel_dir == key:
            matches.append(path)
    if not matches:
        return None

    groups = {}
    for p in matches:
        groups.setdefault(p.name, []).append(p)

    for g in groups.values():
        g.sort()

    return {name: paths for name, paths in sorted(groups.items())}


@app.route('/')
def index():
    log_dirs = find_log_dirs()
    timeline = []
    for idx, (dir_key, files) in enumerate(log_dirs.items()):
        dataset = {
            'label': dir_key or '/',
            'data': []
        }
        for file in files:
            ts = file.stat().st_mtime
            dataset['data'].append({'x': int(ts * 1000), 'y': idx})
        timeline.append(dataset)
    return render_template('index.html', log_dirs=log_dirs, timeline=timeline)


@app.route('/logs/<path:dir_key>')
def view_logs(dir_key):
    grouped = collect_logs(dir_key)
    if grouped is None:
        abort(404)
    contents = []
    for name, paths in grouped.items():
        for idx, f in enumerate(paths, 1):
            header = f"--- {name}" if len(paths) == 1 else f"--- {name} #{idx} ({f.parent.name})"
            contents.append(f"{header}---\n")
            contents.append(read_file_validated(f))
            contents.append('\n')
    return render_template('logs.html', dir_key=dir_key.upper(), log="".join(contents))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
