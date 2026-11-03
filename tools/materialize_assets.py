"""Recover approved source bytes; never render or alter artwork."""
from pathlib import Path
import io,tarfile,hashlib,json,csv,shutil
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'original-assets/manifest.json').read_text())
parts=sorted((ROOT/'original-assets').glob('FOX_TRIBE_original_assets.tar.xz.part-*'))
data=b''.join(p.read_bytes() for p in parts)
assert hashlib.sha256(data).hexdigest()==manifest['archive_sha256'], 'Original archive hash mismatch'
extracted={}
with tarfile.open(fileobj=io.BytesIO(data),mode='r:xz') as t:
 for m in t:
  if m.isdir():continue
  name=m.name.removeprefix('./')
  assert m.isfile() and name in manifest['files'], 'Unexpected archive member: '+name
  b=t.extractfile(m).read()
  assert hashlib.sha256(b).hexdigest()==manifest['files'][name], 'Source file mismatch: '+name
  assert name not in extracted, 'Duplicate archive member'
  extracted[name]=b
assert set(extracted)==set(manifest['files']), 'Missing original source files'
dest=ROOT/'app/src/main/res/drawable-nodpi';dest.mkdir(parents=True,exist_ok=True)
for icon in manifest['icons']:
 (dest/(icon['resource']+'.png')).write_bytes(extracted[icon['source']])
assert len(manifest['icons'])==110
print('PASS: all approved original source files verified; 110 original PNGs materialized byte-for-byte')
