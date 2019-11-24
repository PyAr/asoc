#!/usr/bin/fades

import csv
import os

import requests  # fades

BASE_URL = "https://asocmembers.blob.core.windows.net/asoc-members/pictures/"
DUMP_DIR = 'pictures'

# check dump dir
if not os.path.exists(DUMP_DIR):
    os.mkdir(DUMP_DIR)

with open("dump-carnets.csv", 'rt', encoding='utf8') as fh:
    reader = csv.DictReader(fh)
    for item in reader:
        picture = os.path.basename(item['picture'])
        if not picture or picture == 'False' or picture == 'None':
            print("Skipping (no picture)", item)
            continue

        dump_path = os.path.join(DUMP_DIR, picture)
        if os.path.exists(dump_path):
            print("Skipping (already downloaded)", repr(picture))
            continue

        print("Downloading", repr(picture))
        url = BASE_URL + picture
        resp = requests.get(url)

        with open(dump_path, 'wb') as fh:
            for chunk in resp.iter_content(chunk_size=4096):
                fh.write(chunk)
        print("    ok", resp.headers['Content-Length'])
