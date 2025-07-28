import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional
import boto3
import os
from requests.exceptions import HTTPError
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

@dataclass
class Section:
    html: str
    tag: str
    classes: List[str]
    id: Optional[str]

@dataclass
class PageScrape:
    url: str
    html: str
    assets: List[str]
    sections: List[Section]

@dataclass
class MultiPageScrapeResult:
    pages: List[PageScrape]


def extract_sections(html: str) -> List[Section]:
    soup = BeautifulSoup(html, "html.parser")
    sections = []
    # Look for semantic section containers
    for tag in ["section", "header", "footer", "main"]:
        for el in soup.find_all(tag):
            sections.append(Section(
                html=str(el),
                tag=tag,
                classes=el.get("class", []),
                id=el.get("id")
            ))
    # Fallback: top-level divs with semantic class names
    for div in soup.find_all("div", recursive=False):
        classes = div.get("class", [])
        if any(c in ["hero", "about", "services", "gallery", "contact"] for c in classes):
            sections.append(Section(
                html=str(div),
                tag="div",
                classes=classes,
                id=div.get("id")
            ))
    return sections


def _parse(html_str):
    return BeautifulSoup(html_str, "html.parser")


def scrape_site(url: str, max_pages: int = 5) -> MultiPageScrapeResult:
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket = os.getenv("MINIO_BUCKET", "pagelift-assets")
    
    # Fix endpoint URL construction
    if not minio_endpoint.startswith(('http://', 'https://')):
        minio_endpoint = f"http://{minio_endpoint}"
    
    s3 = boto3.client(
        "s3",
        endpoint_url=minio_endpoint,
        aws_access_key_id=minio_access_key,
        aws_secret_access_key=minio_secret_key,
        region_name="us-east-1",
    )
    visited = set()
    to_visit = [url]
    pages = []
    domain = urlparse(url).netloc
    while to_visit and len(pages) < max_pages:
        page_url = to_visit.pop(0)
        if page_url in visited:
            continue
        visited.add(page_url)
        try:
            resp = requests.get(page_url, timeout=30)
            try:
                resp.raise_for_status()
            except HTTPError as e:
                if resp.status_code == 403:
                    # Retry with User-Agent
                    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                    resp = requests.get(page_url, timeout=30, headers=headers)
                    resp.raise_for_status()
                else:
                    raise
            html = resp.text
        except HTTPError as e:
            # Playwright fallback
            if PLAYWRIGHT_AVAILABLE:
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page.goto(page_url, timeout=30000)
                    html = page.content()
                    browser.close()
            else:
                raise
        # Parse HTML synchronously
        soup = _parse(html)
        # Find assets
        assets = set()
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                assets.add(urljoin(page_url, src))
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href")
            if href:
                assets.add(urljoin(page_url, href))
        # Find nav links (same domain)
        nav_links = set()
        for nav in soup.find_all("nav"):
            for a in nav.find_all("a", href=True):
                link = urljoin(page_url, a["href"])
                if urlparse(link).netloc == domain and link not in visited:
                    nav_links.add(link)
        if not nav_links:
            for a in soup.find_all("a", href=True, recursive=False):
                link = urljoin(page_url, a["href"])
                if urlparse(link).netloc == domain and link not in visited:
                    nav_links.add(link)
        # Add new nav links to to_visit
        for link in nav_links:
            if link not in visited and link not in to_visit and len(pages) + len(to_visit) < max_pages:
                to_visit.append(link)
        # Save HTML to MinIO
        parsed = urlparse(page_url)
        key = f"S3_ORIGINAL/{parsed.netloc}{parsed.path if parsed.path else ''}.html"
        key = key.replace("//", "/")
        s3.put_object(Bucket=minio_bucket, Key=key, Body=html.encode("utf-8"))
        # Extract sections
        sections = extract_sections(html)
        pages.append(PageScrape(
            url=page_url,
            html=html,
            assets=list(assets),
            sections=sections
        ))
    return MultiPageScrapeResult(pages=pages) 