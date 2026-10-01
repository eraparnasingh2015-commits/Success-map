"""Download the Clean Investment Monitor (Rhodium Group & MIT CEEPR) US bulk data.

ClimateDeck serves the bulk zip through a Dash callback rather than a static URL,
so this script triggers the same callback the "Download full data (zip)" button uses.

Data licence: CC BY 4.0 - credit "Clean Investment Monitor, Rhodium Group & MIT CEEPR".
"""
import base64
import io
import json
import pathlib
import sys
import urllib.request
import zipfile

BASE = "https://climatedeck.rhg.com/clean-investment-us"
COMPONENT = "clean-investment-us-manufacturing-download-modal"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "cim"


def main():
    payload = {
        "output": f"{COMPONENT}-download-component.data",
        "outputs": {"id": f"{COMPONENT}-download-component", "property": "data"},
        "inputs": [
            {"id": f"{COMPONENT}-current-xls", "property": "n_clicks", "value": None},
            {"id": f"{COMPONENT}-full-zip", "property": "n_clicks", "value": 1},
        ],
        "changedPropIds": [f"{COMPONENT}-full-zip.n_clicks"],
        "state": [],
    }
    req = urllib.request.Request(
        f"{BASE}/_dash-update-component",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (research data fetch)"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.load(resp)["response"][f"{COMPONENT}-download-component"]["data"]

    archive = zipfile.ZipFile(io.BytesIO(base64.b64decode(data["content"])))
    OUT.mkdir(parents=True, exist_ok=True)
    for info in archive.infolist():
        if "__MACOSX" in info.filename or info.filename.endswith("/"):
            continue
        archive.extract(info, OUT)
    print(f"Saved {data['filename']} to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
