"""Collect factual product/version metadata from public WRDS vendor pages.

Run: uv run --no-project --with beautifulsoup4 python scripts/collect_product_docs.py
     --output research/product-docs-NEW-DATE.json
No login, credentials, or research data are used.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

DIRECTORY = "https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/"
SITEMAP = "https://wrds-www.wharton.upenn.edu/sitemap.xml"


def fetch(url):
    request = Request(url, headers={"User-Agent": "WRDS-skill-documentation-research/1.0"})
    with urlopen(request, timeout=45) as response:
        raw = response.read()
        resolved = response.url
    return BeautifulSoup(raw, "html.parser"), raw, resolved


def collect(url):
    try:
        soup, raw, resolved = fetch(url)
        heading = soup.find("h1")
        vendor = heading.get_text(" ", strip=True) if heading else url.rstrip("/").split("/")[-1]
        products = []
        for column in soup.select(".product-detail-column"):
            fields = {}
            for label in column.find_all("h4"):
                sibling = label.find_next_sibling()
                if sibling is not None:
                    fields[label.get_text(" ", strip=True).rstrip(":")] = sibling.get_text(" ", strip=True)
            schema = fields.get("Product Code/Schema")
            if not schema:
                continue
            dictionary = column.find("a", href=lambda h: h and "/data-dictionary/" in h)
            products.append({
                "schema": schema,
                "title": fields.get("Title"),
                "update_frequency": fields.get("Update Frequency"),
                "last_updated": fields.get("Data Last Updated"),
                "identifiers": fields.get("Identifiers"),
                "regions": fields.get("Regions"),
                "dictionary_url": urljoin(url, dictionary["href"]) if dictionary else None,
            })
        return {"url": url, "resolved_url": resolved, "vendor": vendor,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(raw).hexdigest(), "products": products}
    except Exception as error:
        return {"url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "error": f"{type(error).__name__}: {error}", "products": []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", help="Restrict to explicit public vendor URLs for a prototype.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.url:
        urls = args.url
    else:
        soup, _, _ = fetch(DIRECTORY)
        urls = {urljoin(DIRECTORY, a["href"]) for a in soup.find_all("a", href=True)
                       if "/pages/about/data-vendors/" in a["href"]
                       and urljoin(DIRECTORY, a["href"]).rstrip("/") != DIRECTORY.rstrip("/")}
        with urlopen(SITEMAP, timeout=45) as response:
            sitemap = ET.fromstring(response.read())
        urls.update(node.text for node in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                    if node.text and node.text.startswith(DIRECTORY) and node.text != DIRECTORY)
        urls = sorted(urls)
    with ThreadPoolExecutor(max_workers=3) as pool:
        pages = list(pool.map(collect, urls))
    report = {"directory": DIRECTORY, "sitemap": SITEMAP, "collected_at": datetime.now(timezone.utc).isoformat(),
              "method": "Public vendor page product cards; facts only. Listing is not subscription or table access evidence.",
              "pages": pages}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"pages": len(pages), "products": sum(len(p["products"]) for p in pages),
                      "errors": [{"url": p["url"], "error": p["error"]} for p in pages if "error" in p],
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
