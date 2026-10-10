#!/usr/bin/env python3
"""Compile the canonical, self-contained elsarticle manuscript to PDF."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    compiler = shutil.which('pdflatex')
    if compiler is None:
        raise SystemExit('PDF export requires pdflatex and a TeX distribution containing elsarticle and its supporting packages.')
    temporary_root = ROOT / 'tmp'
    temporary_root.mkdir(exist_ok=True)
    destination = ROOT / 'output/pdf/controlling-incompatible-magic.pdf'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='latex-build-', dir=temporary_root) as temporary:
        build = Path(temporary)
        log = ''
        for _ in range(3):
            result = subprocess.run(
                [compiler, '-interaction=nonstopmode', '-halt-on-error',
                 '-file-line-error', '-no-shell-escape',
                 f'-output-directory={build}', str(ROOT / 'paper.tex')],
                cwd=ROOT, capture_output=True, text=True,
            )
            if result.returncode:
                raise SystemExit(result.stdout[-6000:] + result.stderr[-1000:])
            log = (build / 'paper.log').read_text(errors='replace')
        unresolved = re.search(r'(?:Citation|Reference) .+ undefined|There were undefined (?:references|citations)', log)
        if unresolved:
            raise SystemExit('Unresolved LaTeX references: ' + unresolved.group(0))
        overfull = re.findall(r'Overfull \\[hv]box[^\n]*', log)
        if overfull:
            raise SystemExit('Layout overflow requires repair:\n' + '\n'.join(overfull))
        shutil.copy2(build / 'paper.pdf', destination)
    print(destination)


if __name__ == '__main__':
    main()
