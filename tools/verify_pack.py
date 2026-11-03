"""Fail closed on image, metadata, mapping, or packaged-resource changes."""
from pathlib import Path
import json,csv,hashlib,struct,xml.etree.ElementTree as ET,zipfile,sys
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'original-assets/manifest.json').read_text())
rows=list(csv.DictReader((R/'APP_INVENTORY.csv').open()))
assert len(rows)==110 and len({r['resource_name'] for r in rows})==110
assert {r['resource_name'] for r in rows}=={i['resource'] for i in m['icons']}
assert len(list((R/'app/src/main/res/drawable-nodpi').glob('*.png')))==110
for i in m['icons']:
 b=(R/'app/src/main/res/drawable-nodpi'/(i['resource']+'.png')).read_bytes()
 assert hashlib.sha256(b).hexdigest()==i['sha256'],i['resource']
 assert b[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',b[16:24])==(512,512)
resources={i['resource'] for i in m['icons']}
for name in ['appfilter.xml','drawable.xml','iconpack.xml']:
 assert (R/'app/src/main/assets'/name).read_bytes()==(R/'app/src/main/res/xml'/name).read_bytes()
filter=ET.parse(R/'app/src/main/assets/appfilter.xml').getroot()
seen={}
for e in filter:
 assert e.tag=='item' and e.get('drawable') in resources
 c=e.get('component');assert c not in seen,'Duplicate/conflicting component: '+str(c);seen[c]=e.get('drawable')
for name in ['drawable.xml','iconpack.xml']:
 actual=[e.get('drawable') for e in ET.parse(R/'app/src/main/assets'/name).getroot() if e.tag=='item']
 assert len(actual)==110 and set(actual)==resources
print('PASS: 110 unchanged original images; complete picker metadata; syntactically valid, conflict-free mappings')
if len(sys.argv)>1:
 apk=Path(sys.argv[1]);z=zipfile.ZipFile(apk);assert z.testzip() is None
 assert 'AndroidManifest.xml' in z.namelist() and 'classes.dex' in z.namelist()
 for i in m['icons']:
  candidates=[n for n in z.namelist() if n.startswith('res/') and n.rsplit('/',1)[-1]==i['resource']+'.png']
  assert len(candidates)==1,(i['resource'],candidates)
  assert hashlib.sha256(z.read(candidates[0])).hexdigest()==i['sha256'],'APK changed image: '+i['resource']
 for name in ['appfilter.xml','drawable.xml','iconpack.xml']:
  assert z.read('assets/'+name)==(R/'app/src/main/assets'/name).read_bytes()
 print('PASS: APK ZIP integrity, 110 byte-identical original images, and exact picker/mapping assets')
 print('APK SHA-256:',hashlib.sha256(apk.read_bytes()).hexdigest())
