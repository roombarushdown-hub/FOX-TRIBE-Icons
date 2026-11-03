"""Validate the Fox God icons in the source project and optional built APK."""
from pathlib import Path
import csv, hashlib, json, struct, sys, zipfile
import xml.etree.ElementTree as ET
R = Path(__file__).resolve().parents[1]
m = json.loads((R / "fox-god-assets/QA_MANIFEST.json").read_text())
rows = list(csv.DictReader((R / "APP_INVENTORY.csv").open()))
assert len(m) == len(rows) == 110
resources = []
for i, row in zip(m, rows):
    res = row["resource_name"]
    assert i["number"] == int(row["number"]) and i["name"] == row["app_name"]
    assert i["file"] == res.removeprefix("fox_") + ".png"
    png = (R / "app/src/main/res/drawable-nodpi" / (res + ".png")).read_bytes()
    assert hashlib.sha256(png).hexdigest() == i["sha256"], res
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", png[16:24]) == (512, 512)
    resources.append(res)
assert len(set(resources)) == 110
assert len(list((R / "app/src/main/res/drawable-nodpi").glob("*.png"))) == 110
for name in ("appfilter.xml", "drawable.xml", "iconpack.xml"):
    assert (R / "app/src/main/assets" / name).read_bytes() == (R / "app/src/main/res/xml" / name).read_bytes()
for name in ("drawable.xml", "iconpack.xml"):
    actual = [e.get("drawable") for e in ET.parse(R / "app/src/main/assets" / name).getroot() if e.tag == "item"]
    assert len(actual) == 110 and set(actual) == set(resources), name
mapping = ET.parse(R / "app/src/main/assets/appfilter.xml").getroot()
seen = set()
for item in mapping:
    assert item.tag == "item" and item.get("drawable") in resources
    component = item.get("component")
    assert component and component not in seen
    seen.add(component)
print("PASS: all 110 Fox God icons and launcher resource lists verified; no conflicting mapping entries")
if len(sys.argv) > 1:
    apk = Path(sys.argv[1])
    with zipfile.ZipFile(apk) as z:
        assert z.testzip() is None
        assert "AndroidManifest.xml" in z.namelist() and "classes.dex" in z.namelist()
        names = z.namelist()
        for i, row in zip(m, rows):
            res = row["resource_name"] + ".png"
            candidates = [n for n in names if n.startswith("res/") and n.rsplit("/", 1)[-1] == res]
            assert len(candidates) == 1, (res, candidates)
            assert hashlib.sha256(z.read(candidates[0])).hexdigest() == i["sha256"], res
        for name in ("appfilter.xml", "drawable.xml", "iconpack.xml"):
            assert z.read("assets/" + name) == (R / "app/src/main/assets" / name).read_bytes()
    print("PASS: APK contains exactly 110 byte-identical Fox God image resources and launcher metadata")
    print("APK SHA256:", hashlib.sha256(apk.read_bytes()).hexdigest())
