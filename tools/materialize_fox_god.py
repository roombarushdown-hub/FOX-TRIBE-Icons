"""Restore exact approved FOX TRIBE Fox God artwork. Never regenerate or recolor."""
from pathlib import Path
import base64, csv, hashlib, io, json, struct, zipfile
ROOT = Path(__file__).resolve().parents[1]
parts = sorted((ROOT / "fox-god-assets/encoded").glob("shard-*.b64"))
assert [p.name for p in parts] == [f"shard-{i:03d}.b64" for i in range(41)], "Incomplete encoded artwork"
raw64 = "".join(p.read_text().strip().replace("\n", "").replace("\r", "") for p in parts)
data = base64.b64decode(raw64, validate=True)
assert len(data) == 31435826, "Source archive length mismatch"
assert hashlib.sha256(data).hexdigest() == "eb502cd9fbce378beb385e87a155a451adaaf8602393e8b9688712c606203d5a", "Source archive hash mismatch"
with zipfile.ZipFile(io.BytesIO(data)) as archive:
    assert archive.testzip() is None, "Bad source ZIP"
    manifest = json.loads(archive.read("QA_MANIFEST.json"))
    inventory = list(csv.DictReader((ROOT / "APP_INVENTORY.csv").open()))
    assert len(manifest) == len(inventory) == 110, "Not 110 icons"
    expected = {f"icons/{entry['file']}" for entry in manifest} | {"QA_MANIFEST.json"}
    assert set(archive.namelist()) == expected, "Unexpected or missing ZIP members"
    target = ROOT / "app/src/main/res/drawable-nodpi"
    target.mkdir(parents=True, exist_ok=True)
    for item, app in zip(manifest, inventory):
        assert int(app["number"]) == item["number"] and app["app_name"] == item["name"], "App order/name mismatch"
        assert item["file"] == app["resource_name"].removeprefix("fox_") + ".png", "Resource name mismatch"
        b = archive.read("icons/" + item["file"])
        assert hashlib.sha256(b).hexdigest() == item["sha256"], "Icon checksum mismatch"
        assert b[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", b[16:24]) == (512, 512), "PNG dimensions mismatch"
        (target / (app["resource_name"] + ".png")).write_bytes(b)
    assert len(list(target.glob("*.png"))) == 110, "Unexpected drawable PNG count"
    (ROOT / "fox-god-assets/QA_MANIFEST.json").write_bytes(archive.read("QA_MANIFEST.json"))
print("PASS: 110 byte-exact approved Fox God images restored")
