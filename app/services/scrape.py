import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import boto3
import os
import re
import logging
from requests.exceptions import HTTPError
from .brand_extraction import extract_brand_identity

# Set up logging
logger = logging.getLogger(__name__)
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
    section_id: Optional[int] = None
    heading: Optional[str] = None
    img_urls: List[str] = None
    strategy: Optional[str] = None
    priority: Optional[int] = None
    
    def __post_init__(self):
        if self.forms is None:
            self.forms = []
        if self.ctas is None:
            self.ctas = []
        if self.business_data is None:
            self.business_data = {}
        if self.img_urls is None:
            self.img_urls = []

@dataclass
class PageScrape:
    url: str
    html: str
    assets: List[str]
    sections: List[Section]
    brand_identity: Optional[Dict[str, Any]] = None  # Brand identity data
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


def extract_text_content(element):
    """Extract clean text content from an element, preserving structure"""
    if not element:
        return ""
    
    # Remove script and style elements
    for script in element(["script", "style", "meta", "link"]):
        script.decompose()
    
    # Get text and clean it up
    text = element.get_text()
    # Clean up whitespace but preserve line breaks
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_heading_hierarchy(soup):
    """Extract all headings with their hierarchy"""
    headings = []
    for level in range(1, 7):  # h1 to h6
        for heading in soup.find_all(f"h{level}"):
            headings.append({
                'level': level,
                'text': heading.get_text().strip(),
                'element': heading
            })
    return headings

def find_content_containers(soup):
    """Find all potential content containers using multiple strategies"""
    containers = []
    
    # Strategy 1: Semantic HTML5 elements
    for tag in ["section", "article", "header", "footer", "main", "aside", "nav"]:
        for el in soup.find_all(tag):
            containers.append({
                'element': el,
                'strategy': 'semantic',
                'tag': tag,
                'priority': 1
            })
    
    # Strategy 2: Divs with meaningful class names or IDs
    semantic_keywords = [
        'hero', 'banner', 'intro', 'about', 'services', 'products', 'gallery', 
        'portfolio', 'testimonials', 'reviews', 'contact', 'footer', 'header',
        'content', 'main', 'primary', 'secondary', 'sidebar', 'widget',
        'section', 'block', 'container', 'wrapper', 'area', 'zone'
    ]
    
    for div in soup.find_all(['div', 'section', 'article']):
        classes = ' '.join(div.get("class", [])).lower()
        div_id = (div.get("id") or "").lower()
        
        # Check if classes or ID contain semantic keywords
        if any(keyword in classes or keyword in div_id for keyword in semantic_keywords):
            containers.append({
                'element': div,
                'strategy': 'semantic_classes',
                'tag': div.name,
                'priority': 2
            })
    
    # Strategy 3: Content-rich containers (substantial text content)
    for div in soup.find_all(['div', 'section', 'article', 'p']):
        text_content = extract_text_content(div)
        word_count = len(text_content.split())
        
        # If container has significant text content (20+ words)
        if word_count >= 20:
            containers.append({
                'element': div,
                'strategy': 'content_rich',
                'tag': div.name,
                'priority': 3,
                'word_count': word_count
            })
    
    # Strategy 4: Containers with images
    for container in soup.find_all(['div', 'section', 'article']):
        images = container.find_all('img')
        if images:
            containers.append({
                'element': container,
                'strategy': 'image_container',
                'tag': container.name,
                'priority': 4,
                'image_count': len(images)
            })
    
    return containers

def deduplicate_containers(containers):
    """Remove duplicate containers, keeping the most specific ones"""
    seen_elements = set()
    unique_containers = []
    
    # Sort by priority (lower number = higher priority)
    containers.sort(key=lambda x: x['priority'])
    
    for container in containers:
        element = container['element']
        element_html = str(element)
        
        # Skip if we've already seen this exact element
        if element_html in seen_elements:
            continue
            
        # Skip if this element is contained within another element we've already added
        is_duplicate = False
        for existing in unique_containers:
            existing_element = existing['element']
            # Check if current element is inside existing element
            if element in existing_element.descendants:
                is_duplicate = True
                break
            # Check if existing element is inside current element (replace existing with current)
            elif existing_element in element.descendants:
                unique_containers.remove(existing)
                break
        
        if not is_duplicate:
            seen_elements.add(element_html)
            unique_containers.append(container)
    
    return unique_containers

def extract_images_from_element(element, base_url):
    """Extract all images from an element"""
    images = []
    for img in element.find_all('img'):
        src = img.get('src')
        alt = img.get('alt', '')
        if src:
            # Convert relative URLs to absolute
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                from urllib.parse import urljoin
                src = urljoin(base_url, src)
            elif not src.startswith(('http://', 'https://')):
                from urllib.parse import urljoin
                src = urljoin(base_url, src)
            images.append(src)
    return images

def extract_phone_numbers(text):
    """Extract phone numbers using various international patterns"""
    phone_patterns = [
        # Portuguese phone numbers
        r'(\+351\s?)?(\d{3}\s?\d{3}\s?\d{3})',
        r'(\+351\s?)?(91\d{7}|92\d{7}|93\d{7}|96\d{7})',
        
        # General international patterns
        r'\+?[\d\s\-\(\)]{10,15}',
        r'\(\d{3}\)\s?\d{3}[\-\s]?\d{4}',
        r'\d{3}[\-\.\s]?\d{3}[\-\.\s]?\d{4}',
        
        # UK patterns
        r'\+44\s?\d{10,11}',
        r'0\d{10}',
        
        # US patterns
        r'\+1\s?\d{10}',
        r'\d{3}[\-\.\s]?\d{4}',
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                phone = ''.join(match).strip()
            else:
                phone = match.strip()
            
            # Clean up the phone number
            phone = re.sub(r'[^\d\+]', '', phone)
            
            # Validate length (7-15 digits)
            if 7 <= len(re.sub(r'[^\d]', '', phone)) <= 15:
                phones.append(phone)
    
    return list(set(phones))  # Remove duplicates

def extract_email_addresses(text):
    """Extract email addresses"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    # Filter out obvious noise
    valid_emails = []
    for email in emails:
        # Skip emails with too many dots or suspicious patterns
        if email.count('.') <= 3 and not any(noise in email.lower() for noise in ['example', 'test', 'placeholder']):
            valid_emails.append(email.lower())
    
    return list(set(valid_emails))

def extract_business_hours(text):
    """Extract business hours information"""
    hours_patterns = [
        # Portuguese patterns
        r'(segunda|terça|quarta|quinta|sexta|sábado|domingo).{0,20}(\d{1,2}[h:]?\d{0,2}).{0,10}(\d{1,2}[h:]?\d{0,2})',
        r'(seg|ter|qua|qui|sex|sáb|dom).{0,20}(\d{1,2}[h:]?\d{0,2}).{0,10}(\d{1,2}[h:]?\d{0,2})',
        
        # English patterns
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday).{0,20}(\d{1,2}[:\.]?\d{0,2}\s?[ap]m?).{0,10}(\d{1,2}[:\.]?\d{0,2}\s?[ap]m?)',
        r'(mon|tue|wed|thu|fri|sat|sun).{0,20}(\d{1,2}[:\.]?\d{0,2}\s?[ap]m?).{0,10}(\d{1,2}[:\.]?\d{0,2}\s?[ap]m?)',
        
        # General time patterns
        r'(\d{1,2}[h:]\d{2}).{0,5}(\d{1,2}[h:]\d{2})',
        r'(\d{1,2}[:\.]?\d{0,2}\s?[ap]m).{0,10}(\d{1,2}[:\.]?\d{0,2}\s?[ap]m)',
    ]
    
    hours_info = []
    for pattern in hours_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            hours_info.append(' '.join(match))
    
    return hours_info

def extract_addresses(text):
    """Extract address information"""
    address_patterns = [
        # Portuguese address patterns
        r'(rua|avenida|av\.|r\.|travessa|praça|largo)\s+[A-Za-zÀ-ÿ\s\d\-,\.]+\d{4}[\-\s]?\d{3}',
        r'\d{4}[\-\s]?\d{3}\s+[A-Za-zÀ-ÿ\s]+',
        
        # General address patterns
        r'\d+\s+[A-Za-z\s]+\b(street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|place|pl)\b',
        r'\b\d{1,5}\s+[A-Za-z\s]+,\s*[A-Za-z\s]+,?\s*\d{5}',
    ]
    
    addresses = []
    for pattern in address_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        addresses.extend(matches)
    
    return addresses

def extract_social_media_links(soup):
    """Extract social media profile links"""
    social_patterns = {
        'facebook': r'(?:https?://)?(?:www\.)?facebook\.com/[A-Za-z0-9._-]+',
        'instagram': r'(?:https?://)?(?:www\.)?instagram\.com/[A-Za-z0-9._-]+',
        'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/[A-Za-z0-9._-]+',
        'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|company)/[A-Za-z0-9._-]+',
        'youtube': r'(?:https?://)?(?:www\.)?youtube\.com/(?:c|channel|user)/[A-Za-z0-9._-]+',
    }
    
    social_links = {}
    page_text = soup.get_text()
    
    # Check links in href attributes
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        for platform, pattern in social_patterns.items():
            if re.search(pattern, href, re.IGNORECASE):
                social_links[platform] = href
                break
    
    # Check in text content as backup
    for platform, pattern in social_patterns.items():
        if platform not in social_links:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                social_links[platform] = match.group(0)
    
    return social_links

def extract_ctas_and_forms(element):
    """Extract call-to-action buttons and forms"""
    ctas = []
    forms = []
    
    # Extract CTAs (buttons, links with action words)
    cta_keywords = [
        'contact', 'call', 'phone', 'email', 'quote', 'book', 'schedule', 'order',
        'buy', 'purchase', 'get', 'request', 'learn more', 'find out', 'discover',
        'contactar', 'ligar', 'telefone', 'email', 'orçamento', 'marcar', 'agendar',
        'pedir', 'solicitar', 'saber mais', 'descobrir'
    ]
    
    for button in element.find_all(['button', 'a', 'input']):
        text = button.get_text().strip().lower()
        button_type = button.get('type', '')
        href = button.get('href', '')
        
        # Check if this looks like a CTA
        if any(keyword in text for keyword in cta_keywords) or button_type == 'submit':
            ctas.append({
                'text': button.get_text().strip(),
                'type': button.name,
                'href': href,
                'action': button_type
            })
    
    # Extract forms
    for form in element.find_all('form'):
        form_data = {
            'action': form.get('action', ''),
            'method': form.get('method', 'get'),
            'fields': []
        }
        
        for input_field in form.find_all(['input', 'textarea', 'select']):
            field_info = {
                'type': input_field.get('type', input_field.name),
                'name': input_field.get('name', ''),
                'placeholder': input_field.get('placeholder', ''),
                'required': input_field.has_attr('required')
            }
            form_data['fields'].append(field_info)
        
        forms.append(form_data)
    
    return ctas, forms

def extract_business_data(soup, text_content):
    """Extract comprehensive business-critical data"""
    business_data = {}
    
    # Extract contact information
    business_data['phones'] = extract_phone_numbers(text_content)
    business_data['emails'] = extract_email_addresses(text_content)
    business_data['addresses'] = extract_addresses(text_content)
    business_data['business_hours'] = extract_business_hours(text_content)
    
    # Extract social media
    business_data['social_media'] = extract_social_media_links(soup)
    
    # Extract CTAs and forms from the whole page
    ctas, forms = extract_ctas_and_forms(soup)
    business_data['ctas'] = ctas
    business_data['forms'] = forms
    
    # Extract services/products keywords
    service_keywords = [
        'service', 'services', 'serviço', 'serviços', 'product', 'products', 'produto', 'produtos',
        'solution', 'solutions', 'solução', 'soluções', 'offer', 'oferece', 'specialist', 'especialista'
    ]
    
    services = []
    for keyword in service_keywords:
        # Find sentences containing service keywords
        sentences = re.split(r'[.!?]', text_content)
        for sentence in sentences:
            if keyword.lower() in sentence.lower() and len(sentence.strip()) > 10:
                services.append(sentence.strip())
    
    business_data['services'] = services[:5]  # Limit to top 5 service mentions
    
    # Log business data extraction results
    logger.info(f"Business data extracted: {len(business_data['phones'])} phones, {len(business_data['emails'])} emails, {len(business_data['addresses'])} addresses")
    logger.info(f"Forms and CTAs: {len(business_data['forms'])} forms, {len(business_data['ctas'])} CTAs")
    
    return business_data

def extract_sections(html: str, base_url: str = "") -> List[Section]:
    """Enhanced section extraction with comprehensive content capture"""
    soup = BeautifulSoup(html, "html.parser")
    
    logger.info(f"Starting enhanced section extraction for URL: {base_url}")
    
    # Remove noise elements
    for noise in soup(["script", "style", "meta", "link", "noscript"]):
        noise.decompose()
    
    # Extract business-critical data from the entire page first
    page_text = soup.get_text()
    global_business_data = extract_business_data(soup, page_text)
    logger.info(f"Global business data extracted: {len(global_business_data.get('phones', []))} phones, {len(global_business_data.get('emails', []))} emails")
    
    # Find all potential content containers
    containers = find_content_containers(soup)
    logger.info(f"Found {len(containers)} potential content containers")
    
    # Log container strategies
    strategy_counts = {}
    for container in containers:
        strategy = container['strategy']
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    logger.info(f"Container strategies: {strategy_counts}")
    
    # Deduplicate containers
    unique_containers = deduplicate_containers(containers)
    logger.info(f"After deduplication: {len(unique_containers)} unique containers")
    
    sections = []
    section_id = 0
    
    for container_info in unique_containers:
        element = container_info['element']
        
        # Extract text content
        text_content = extract_text_content(element)
        word_count = len(text_content.split())
        
        # Skip containers with minimal content (less than 10 words)
        if word_count < 10:
            logger.debug(f"Skipping container with {word_count} words (strategy: {container_info['strategy']})")
            continue
        
        # Extract images
        images = extract_images_from_element(element, base_url)
        
        # Find heading within this section
        heading = ""
        for h_level in range(1, 7):
            h_element = element.find(f'h{h_level}')
            if h_element:
                heading = h_element.get_text().strip()
                break
        
        # Extract section-specific business data
        section_business_data = extract_business_data(element, text_content)
        
        # Extract section-specific CTAs and forms
        section_ctas, section_forms = extract_ctas_and_forms(element)
        
        # Log section details
        logger.info(f"Section {section_id}: {word_count} words, {len(images)} images, heading: '{heading[:50]}...', strategy: {container_info['strategy']}")
        logger.info(f"  Section business data: {len(section_business_data.get('phones', []))} phones, {len(section_ctas)} CTAs, {len(section_forms)} forms")
        
        # Create section
        section = Section(
            html=str(element),
            tag=container_info['tag'],
            classes=element.get("class", []),
            id=element.get("id"),
            text=text_content
        )
        
        # Add additional data
        section.section_id = section_id
        section.heading = heading
        section.img_urls = images
        section.strategy = container_info['strategy']
        section.priority = container_info['priority']
        section.business_data = section_business_data
        section.ctas = section_ctas
        section.forms = section_forms
        
        sections.append(section)
        section_id += 1
    
    # If we didn't find enough content, fallback to broader extraction
    if len(sections) < 3:
        logger.warning(f"Only found {len(sections)} sections, using fallback extraction")
        # Extract from major containers even if they don't meet our criteria
        for tag in ['body', 'main', 'div']:
            for element in soup.find_all(tag):
                text_content = extract_text_content(element)
                word_count = len(text_content.split())
                if word_count >= 5:  # Even less restrictive
                    logger.info(f"Fallback section: {word_count} words from {tag} element")
                    section = Section(
                        html=str(element),
                        tag=tag,
                        classes=element.get("class", []),
                        id=element.get("id"),
                        text=text_content
                    )
                    section.section_id = len(sections)
                    section.heading = ""
                    section.img_urls = extract_images_from_element(element, base_url)
                    section.strategy = 'fallback'
                    section.priority = 10
                    sections.append(section)
                    
                    if len(sections) >= 10:  # Don't go overboard
                        break
    
    logger.info(f"Extraction complete: {len(sections)} total sections extracted")
    
    # Log final section summary
    total_words = sum(len(section.text.split()) for section in sections if section.text)
    total_images = sum(len(section.img_urls) for section in sections)
    logger.info(f"Content summary: {total_words} total words, {total_images} total images")
    
    # Attach global business data to sections for later use
    for section in sections:
        if not section.business_data:
            section.business_data = {}
        # Merge global business data with section data
        for key, value in global_business_data.items():
            if key not in section.business_data or not section.business_data[key]:
                section.business_data[key] = value
    
    return sections


def extract_sections_with_brand(html: str, base_url: str = "") -> tuple:
    """Enhanced extraction that includes both sections and brand identity"""
    logger.info(f"Starting comprehensive extraction (sections + brand) for: {base_url}")
    
    # Extract sections using existing function
    sections = extract_sections(html, base_url)
    
    # Extract brand identity
    try:
        brand_identity = extract_brand_identity(base_url, html)
        
        # Convert dataclass to dict for easier handling
        brand_dict = {
            'colors': {
                'primary': brand_identity.colors.primary,
                'secondary': brand_identity.colors.secondary,
                'accent': brand_identity.colors.accent,
                'background': brand_identity.colors.background,
                'text_primary': brand_identity.colors.text_primary,
                'text_secondary': brand_identity.colors.text_secondary,
                'success': brand_identity.colors.success,
                'error': brand_identity.colors.error,
            },
            'typography': {
                'primary_font': brand_identity.typography.primary_font,
                'secondary_font': brand_identity.typography.secondary_font,
                'heading_font': brand_identity.typography.heading_font,
                'font_sizes': brand_identity.typography.font_sizes,
                'font_weights': brand_identity.typography.font_weights,
                'line_heights': brand_identity.typography.line_heights,
            },
            'style': {
                'border_radius': brand_identity.style.border_radius,
                'shadow_style': brand_identity.style.shadow_style,
                'spacing_scale': brand_identity.style.spacing_scale,
                'button_styles': brand_identity.style.button_styles,
                'card_styles': brand_identity.style.card_styles,
                'layout_patterns': brand_identity.style.layout_patterns,
            },
            'brand': {
                'industry': brand_identity.industry,
                'tone': brand_identity.tone,
                'layout_preference': brand_identity.layout_preference,
                'image_style': brand_identity.image_style,
            }
        }
        
        logger.info(f"Brand extraction completed: {brand_identity.industry} industry, {brand_identity.tone} tone")
        logger.info(f"Primary color: {brand_identity.colors.primary}, Font: {brand_identity.typography.primary_font}")
        
    except Exception as e:
        logger.error(f"Brand extraction failed: {e}")
        # Return default brand identity
        brand_dict = {
            'colors': {
                'primary': '#3B82F6',
                'secondary': '#64748B', 
                'accent': '#F59E0B',
                'background': '#FFFFFF',
                'text_primary': '#111827',
                'text_secondary': '#6B7280',
                'success': '#10B981',
                'error': '#EF4444',
            },
            'typography': {
                'primary_font': 'Inter, system-ui, sans-serif',
                'secondary_font': 'Inter, system-ui, sans-serif',
                'heading_font': 'Inter, system-ui, sans-serif',
                'font_sizes': None,
                'font_weights': None,
                'line_heights': None,
            },
            'style': {
                'border_radius': '0.5rem',
                'shadow_style': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                'spacing_scale': None,
                'button_styles': None,
                'card_styles': None,
                'layout_patterns': ['flex', 'grid'],
            },
            'brand': {
                'industry': 'business',
                'tone': 'professional',
                'layout_preference': 'modern',
                'image_style': 'photography',
            }
        }
    
    return sections, brand_dict


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
        sections = extract_sections(html, page_url)
        pages.append(PageScrape(
            url=page_url,
            html=html,
            assets=list(assets),
            sections=sections
        ))
    return MultiPageScrapeResult(pages=pages) 