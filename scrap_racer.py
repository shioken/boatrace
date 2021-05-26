#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import os.path
import urllib.parse
import urllib.request

target_url = "https://www.boatrace.jp/owpc/pc/extra/data/download.html"

r = requests.get(target_url)
soup = BeautifulSoup(r.text, "html.parser")

links = soup.find_all("a")
lzhs = []
for link in links:
    href = link.get('href')
    root, ext = os.path.splitext(href)
    if ext.lower() == '.lzh':
        lzhs.append(href)

for lzh in lzhs:
    url = urllib.parse.urljoin(target_url, lzh)
    basename = os.path.basename(lzh)
    print(url, basename)
    urllib.request.urlretrieve(url, f"lzh/{basename}")

print("done")
