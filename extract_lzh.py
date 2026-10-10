"""Extract downloaded official LZH archives into raw text files.

This is an extraction step, NOT yet a structured race CSV or an AI model.
Requires: pip install lhafile
"""
from pathlib import Path
import csv
import lhafile

root = Path('data')
out = Path('extracted')
out.mkdir(exist_ok=True)
manifest = []
archives = sorted(root.rglob('*.lzh'))
if not archives:
    raise SystemExit('No LZH archives found under data/. Run daily.py first.')
for archive in archives:
    relative = archive.relative_to(root)
    target_dir = out / relative.parent / archive.stem
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        lha = lhafile.Lhafile(str(archive))
            names = lha.namelist()
            if not names:
                raise ValueError('Archive is empty')
            for idx, name in enumerate(names):
                # Never trust archive paths: use a numbered, safe output filename.
                payload = lha.read(name)
                suffix = Path(name).suffix.lower()
                if suffix not in ('.txt', '.csv', '.dat'):
                    suffix = '.txt'
                dest = target_dir / f'{idx:03d}{suffix}'
                dest.write_bytes(payload)
                manifest.append([str(archive), name, str(dest), len(payload), 'OK'])
    except Exception as exc:
        manifest.append([str(archive), '', '', 0, f'ERROR: {exc}'])
        print('ERROR:', archive, exc)
with (out / 'manifest.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['archive', 'member', 'output', 'bytes', 'status'])
    writer.writerows(manifest)
print('Archives:', len(archives), 'Extracted files:', sum(r[-1] == 'OK' for r in manifest))
if any(r[-1] != 'OK' for r in manifest):
    raise SystemExit('Some archives could not be extracted. See manifest.csv.')
