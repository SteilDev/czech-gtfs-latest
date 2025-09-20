#!/usr/bin/env python3
import argparse
import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://api.transitous.org/gtfs/"

def main():
    parser = argparse.ArgumentParser(description="Download GTFS files from Transitous API with optional prefix filter.")
    parser.add_argument("--prefix", type=str, required=True, help="Prefix to filter files (e.g., 'X' downloads 'X_*').")
    args = parser.parse_args()

    # Get directory listing (HTML)
    response = requests.get(BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract all links ending in .zip
    files = [a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".zip")]

    # Filter files based on prefix
    prefix = args.prefix
    if prefix:
        files = [f for f in files if f.startswith(f"{prefix}_")]

    if not files:
        print(f"No files found with prefix '{prefix}_'")
        return

    print(f"Found {len(files)} files. Downloading...")

    for filename in files:
        url = BASE_URL + filename
        print(f"Downloading {filename} ...")
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print("Download completed.")

if __name__ == "__main__":
    main()

