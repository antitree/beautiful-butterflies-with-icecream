import os
import re
from flask import Flask, render_template, send_from_directory, abort
from charset_normalizer import from_bytes
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

LOG_ROOT = Path(os.environ.get('LOG_ROOT', 'logs')).resolve()
FILE_RE = re.compile(r"^[0-9]{8}\.out$")


def read_file_validated(path: Path) -> str:
    """Return text from path or hex representation if not valid text."""
    data = path.read_bytes()
    if not data:
        return ""
    try:
        best = from_bytes(data).best()
        if best and best.encoding:
            return best.str()
    except Exception:
        pass
    return ' '.join(f'{b:02x}' for b in data)


def find_log_dirs():
    log_dirs = {}
    for path in LOG_ROOT.rglob('*'):
        if path.is_file() and FILE_RE.match(path.name):
            rel_dir = path.parent.relative_to(LOG_ROOT)
            log_dirs.setdefault(rel_dir.as_posix(), []).append(path)
    for files in log_dirs.values():
        files.sort()
    return log_dirs


def collect_logs(dir_key):
    directory = LOG_ROOT / dir_key
    if not directory.exists():
        return None
    files = sorted([p for p in directory.glob('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].out')])
    return files


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
    files = collect_logs(dir_key)
    if files is None:
        abort(404)
    contents = []
    for f in files:
        contents.append(f"--- {f.name} ---\n")
        contents.append(read_file_validated(f))
        contents.append('\n')
    return render_template('logs.html', dir_key=dir_key, log="".join(contents))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
