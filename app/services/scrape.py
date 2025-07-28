import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import boto3
import os
import re
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
    text: Optional[str] = None
    forms: List[Dict[str, Any]] = None
    ctas: List[Dict[str, Any]] = None
    business_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.forms is None:
            self.forms = []
        if self.ctas is None:
            self.ctas = []
        if self.business_data is None:
            self.business_data = {}

@dataclass
class PageScrape:
    url: str
    html: str
    assets: List[str]
    sections: List[Section]
    business_info: Dict[str, Any] = None
    navigation: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.business_info is None:
            self.business_info = {}
        if self.navigation is None:
            self.navigation = {}

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
    return sections\n\ndef extract_business_data(soup: BeautifulSoup, page_url: str) -> Dict[str, Any]:\n    \"\"\"Extract business-critical information from the page\"\"\"\n    business_data = {\n        'phones': [],\n        'emails': [],\n        'addresses': [],\n        'hours': [],\n        'social_media': [],\n        'services': [],\n        'reviews': []\n    }\n    \n    # Get all text content for pattern matching\n    text_content = soup.get_text()\n    \n    # Extract phone numbers\n    phone_patterns = [\n        r'\\b(?:\\+?1[-.]?)?\\(?([0-9]{3})\\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\\b',\n        r'\\b([0-9]{3})[-.]([0-9]{3})[-.]?([0-9]{4})\\b',\n        r'\\(([0-9]{3})\\)\\s?([0-9]{3})[-.]([0-9]{4})\\b'\n    ]\n    \n    for pattern in phone_patterns:\n        matches = re.findall(pattern, text_content)\n        for match in matches:\n            if isinstance(match, tuple):\n                phone = ''.join(match)\n                if len(phone) == 10:\n                    formatted = f\"({phone[:3]}) {phone[3:6]}-{phone[6:]}\"\n                    if formatted not in business_data['phones']:\n                        business_data['phones'].append(formatted)\n    \n    # Extract email addresses\n    email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'\n    emails = re.findall(email_pattern, text_content)\n    business_data['emails'] = list(set(emails))\n    \n    # Extract addresses (look for common address patterns)\n    address_indicators = soup.find_all(text=re.compile(r'(?i)\\b(?:address|location|visit us|find us|directions)\\b'))\n    for indicator in address_indicators:\n        parent = indicator.parent\n        if parent:\n            addr_text = parent.get_text().strip()\n            # Look for patterns like \"123 Main St, City, State ZIP\"\n            addr_pattern = r'\\d+\\s+[A-Za-z\\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd).*?\\d{5}'\n            matches = re.findall(addr_pattern, addr_text)\n            business_data['addresses'].extend(matches)\n    \n    # Extract business hours\n    hours_indicators = soup.find_all(text=re.compile(r'(?i)\\b(?:hours|open|closed|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\\b'))\n    for indicator in hours_indicators:\n        parent = indicator.parent\n        if parent:\n            hours_text = parent.get_text().strip()\n            # Look for time patterns\n            time_pattern = r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)[\\s:]*\\d{1,2}(?::\\d{2})?\\s*(?:am|pm).*?\\d{1,2}(?::\\d{2})?\\s*(?:am|pm)'\n            matches = re.findall(time_pattern, hours_text, re.IGNORECASE)\n            business_data['hours'].extend(matches)\n    \n    # Extract social media links\n    social_patterns = {\n        'facebook': r'facebook\\.com/[\\w\\.-]+',\n        'twitter': r'twitter\\.com/[\\w\\.-]+',\n        'instagram': r'instagram\\.com/[\\w\\.-]+',\n        'linkedin': r'linkedin\\.com/[\\w\\.-/]+',\n        'youtube': r'youtube\\.com/[\\w\\.-/]+'\n    }\n    \n    for platform, pattern in social_patterns.items():\n        matches = re.findall(pattern, text_content, re.IGNORECASE)\n        for match in matches:\n            business_data['social_media'].append({\n                'platform': platform,\n                'url': f\"https://{match}\" if not match.startswith('http') else match\n            })\n    \n    # Extract services (look for service-related keywords)\n    service_keywords = ['service', 'repair', 'installation', 'maintenance', 'cleaning', 'plumbing', 'emergency']\n    service_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'li', 'div'], \n                                    text=re.compile(r'(?i)\\b(?:' + '|'.join(service_keywords) + r')\\b'))\n    \n    for element in service_elements:\n        service_text = element.get_text().strip()\n        if len(service_text) < 200 and service_text not in business_data['services']:\n            business_data['services'].append(service_text)\n    \n    return business_data\n\ndef extract_forms(soup: BeautifulSoup) -> List[Dict[str, Any]]:\n    \"\"\"Extract all forms from the page with their fields and actions\"\"\"\n    forms = []\n    \n    for form in soup.find_all('form'):\n        form_data = {\n            'action': form.get('action', ''),\n            'method': form.get('method', 'get').lower(),\n            'fields': [],\n            'html': str(form)\n        }\n        \n        # Extract form fields\n        for field in form.find_all(['input', 'textarea', 'select']):\n            field_data = {\n                'type': field.get('type', 'text'),\n                'name': field.get('name', ''),\n                'placeholder': field.get('placeholder', ''),\n                'required': field.has_attr('required'),\n                'label': ''\n            }\n            \n            # Try to find associated label\n            if field.get('id'):\n                label = soup.find('label', {'for': field.get('id')})\n                if label:\n                    field_data['label'] = label.get_text().strip()\n            \n            form_data['fields'].append(field_data)\n        \n        forms.append(form_data)\n    \n    return forms\n\ndef extract_ctas(soup: BeautifulSoup) -> List[Dict[str, Any]]:\n    \"\"\"Extract call-to-action buttons and links\"\"\"\n    ctas = []\n    \n    # Look for buttons with action-oriented text\n    cta_keywords = [\n        'call', 'contact', 'quote', 'schedule', 'book', 'get started', \n        'learn more', 'sign up', 'subscribe', 'download', 'buy now',\n        'order', 'purchase', 'request', 'apply', 'register', 'join'\n    ]\n    \n    # Check buttons\n    for button in soup.find_all(['button', 'a']):\n        button_text = button.get_text().strip().lower()\n        \n        # Check if button text contains CTA keywords\n        if any(keyword in button_text for keyword in cta_keywords):\n            cta_data = {\n                'text': button.get_text().strip(),\n                'type': button.name,\n                'href': button.get('href', ''),\n                'onclick': button.get('onclick', ''),\n                'classes': button.get('class', []),\n                'html': str(button)\n            }\n            ctas.append(cta_data)\n    \n    # Look for phone number links\n    for link in soup.find_all('a', href=re.compile(r'^tel:')):\n        cta_data = {\n            'text': link.get_text().strip(),\n            'type': 'phone',\n            'href': link.get('href'),\n            'classes': link.get('class', []),\n            'html': str(link)\n        }\n        ctas.append(cta_data)\n    \n    # Look for email links\n    for link in soup.find_all('a', href=re.compile(r'^mailto:')):\n        cta_data = {\n            'text': link.get_text().strip(),\n            'type': 'email',\n            'href': link.get('href'),\n            'classes': link.get('class', []),\n            'html': str(link)\n        }\n        ctas.append(cta_data)\n    \n    return ctas\n\ndef extract_navigation(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:\n    \"\"\"Extract navigation structure and internal links\"\"\"\n    navigation = {\n        'main_menu': [],\n        'footer_links': [],\n        'breadcrumbs': [],\n        'internal_links': []\n    }\n    \n    domain = urlparse(base_url).netloc\n    \n    # Extract main navigation\n    nav_elements = soup.find_all(['nav', 'div'], class_=re.compile(r'(?i)nav|menu'))\n    for nav in nav_elements:\n        for link in nav.find_all('a', href=True):\n            full_url = urljoin(base_url, link['href'])\n            if urlparse(full_url).netloc == domain:\n                navigation['main_menu'].append({\n                    'text': link.get_text().strip(),\n                    'url': full_url,\n                    'href': link['href']\n                })\n    \n    # Extract footer links\n    footer = soup.find('footer')\n    if footer:\n        for link in footer.find_all('a', href=True):\n            full_url = urljoin(base_url, link['href'])\n            if urlparse(full_url).netloc == domain:\n                navigation['footer_links'].append({\n                    'text': link.get_text().strip(),\n                    'url': full_url,\n                    'href': link['href']\n                })\n    \n    # Extract breadcrumbs\n    breadcrumb_selectors = ['[aria-label*=\"breadcrumb\"]', '.breadcrumb', '.breadcrumbs']\n    for selector in breadcrumb_selectors:\n        breadcrumb = soup.select_one(selector)\n        if breadcrumb:\n            for link in breadcrumb.find_all('a', href=True):\n                navigation['breadcrumbs'].append({\n                    'text': link.get_text().strip(),\n                    'url': urljoin(base_url, link['href'])\n                })\n            break\n    \n    return navigation


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