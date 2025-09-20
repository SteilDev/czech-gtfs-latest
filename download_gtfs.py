#!/usr/bin/env python3
import requests
import json
import os

JSON_URL = "https://raw.githubusercontent.com/public-transport/transitous/refs/heads/main/feeds/cz.json"
OUTPUT_FILE = "cz_mapping.json"

def download_file(url, filename):
    """Download file from url to filename"""
    print(f"Downloading {filename} from {url}")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

def main():
    if os.path.exists("cz.json"):
        print("Loading local cz.json ...")
        with open("cz.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print(f"Fetching {JSON_URL} ...")
        response = requests.get(JSON_URL)
        response.raise_for_status()
        data = response.json()

    sources = data.get("sources", [])

    http_feeds = [s for s in sources if s.get("type") == "http" and "url" in s]
    http_feeds_sorted = sorted(http_feeds, key=lambda s: f"cz_{s['name']}.zip")

    mapping = {}

    for idx, src in enumerate(http_feeds_sorted):
        name = src["name"]
        filename = f"cz_{name}.zip"
        prefix = idx
        url = src["url"]

        rt_feeds = [
            s["url"]
            for s in sources
            if s.get("type") == "url" and s.get("spec") == "gtfs-rt" and s.get("name") == name
        ]

        mapping[filename] = {
            "prefix": prefix,
            "download_url": url,
            "gtfs_rt": rt_feeds if rt_feeds else None
        }

        if not os.path.exists(filename):
            download_file(url, filename)
        else:
            print(f"Skipping {filename}, already exists")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"\nDownloaded {len(http_feeds_sorted)} GTFS feeds")
    print(f"Mapping saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
