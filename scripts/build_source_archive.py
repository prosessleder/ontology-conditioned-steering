#!/usr/bin/env python3
"""Archive only tracked source files; never include credentials or run outputs."""
from pathlib import Path
import hashlib
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'publication/ontology-conditioned-steering-v0.1.0-source.zip'


def main():
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    paths=[p for p in paths if p and not p.startswith(('output/','publication/SHA256SUMS','publication/ontology-conditioned-steering-v0.1.0-source.zip'))]
    if not paths:
        raise SystemExit('Stage source files in Git before building archive.')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(paths):
            if name=='.env' or name.startswith(('.venv/','runs/','vectors/','data/generated/')) or '/.env' in name:
                raise SystemExit(f'Refusing sensitive or generated path: {name}')
            info=zipfile.ZipInfo('ontology-conditioned-steering/'+name,date_time=(2026,10,9,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,(ROOT/name).read_bytes())
    outputs=[ROOT/'output/pdf/controlling-incompatible-magic.pdf',OUT]
    (ROOT/'publication/SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in outputs))
    print(f'{OUT}: {len(paths)} source files')


if __name__=='__main__':
    main()
