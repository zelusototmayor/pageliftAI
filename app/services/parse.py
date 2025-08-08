from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List, Optional
import json
from app.models import Job
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass
class SectionData:
    section_id: int
    heading: Optional[str]
    text: str
    img_urls: List[str]
    classes: List[str]
    id: Optional[str]


def parse_html_sections(html: str) -> List[SectionData]:
    """
    Semantic HTML parsing that creates meaningful content sections
    instead of fragmenting into every div/section element
    """
    soup = BeautifulSoup(html, "html.parser")
    sections = []
    section_id = 0
    
    # Helper function to determine if content is substantial enough
    def is_meaningful_content(text: str, min_words: int = 5) -> bool:
        """Check if text content is substantial enough to be a section"""
        if not text or len(text.strip()) < 20:  # Too short
            return False
        word_count = len(text.split())
        return word_count >= min_words
    
    def extract_heading(element):
        """Extract the most prominent heading from an element"""
        for heading_tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            heading = element.find(heading_tag)
            if heading:
                return heading.get_text(strip=True)
        return None
    
    def get_semantic_containers():
        """Find semantic containers that likely contain meaningful sections"""
        containers = []
        
        # 1. First priority: Semantic HTML5 elements
        for tag in ["main", "article", "section"]:
            for el in soup.find_all(tag):
                text = el.get_text(" ", strip=True)
                if is_meaningful_content(text):
                    containers.append(el)
        
        # 2. Second priority: Divs with meaningful classes/content
        meaningful_classes = [
            "content", "main", "container", "section", "block", "article",
            "hero", "about", "services", "contact", "gallery", "testimonials",
            "intro", "description", "feature", "highlight"
        ]
        
        for div in soup.find_all("div"):
            classes = div.get("class", [])
            div_id = div.get("id", "")
            text = div.get_text(" ", strip=True)
            
            # Check if this div has meaningful content and semantic indicators
            has_semantic_class = any(cls.lower() in " ".join(classes + [div_id]).lower() 
                                   for cls in meaningful_classes)
            
            if has_semantic_class and is_meaningful_content(text, min_words=10):
                # Avoid nested containers (choose the most outer meaningful one)
                if not any(div in container.descendants for container in containers):
                    containers.append(div)
        
        return containers
    
    # Extract meaningful sections from semantic containers
    processed_elements = set()
    
    for container in get_semantic_containers():
        if container in processed_elements:
            continue
            
        text = container.get_text(" ", strip=True)
        if not is_meaningful_content(text, min_words=8):
            continue
            
        # Extract images
        imgs = []
        for img in container.find_all("img"):
            src = img.get("src")
            if src and src not in imgs:
                imgs.append(src)
        
        # Get heading
        heading = extract_heading(container)
        
        # Get classes and id for context
        classes = container.get("class", [])
        element_id = container.get("id")
        
        sections.append(SectionData(
            section_id=section_id,
            heading=heading,
            text=text,
            img_urls=imgs,
            classes=classes,
            id=element_id
        ))
        section_id += 1
        
        # Mark this container and its descendants as processed
        processed_elements.add(container)
        for descendant in container.descendants:
            processed_elements.add(descendant)
    
    # Fallback: If we found very few sections, use heading-based extraction
    if len(sections) < 3:
        # Reset and try heading-based approach
        sections = []
        section_id = 0
        
        current_section = {
            "heading": None,
            "text_parts": [],
            "img_urls": []
        }
        
        def flush_section():
            nonlocal section_id
            text = " ".join(current_section["text_parts"]).strip()
            if is_meaningful_content(text) or current_section["heading"] or current_section["img_urls"]:
                sections.append(SectionData(
                    section_id=section_id,
                    heading=current_section["heading"],
                    text=text,
                    img_urls=current_section["img_urls"],
                    classes=[],
                    id=None
                ))
                section_id += 1
                current_section["heading"] = None
                current_section["text_parts"] = []
                current_section["img_urls"] = []
        
        # Walk through all elements looking for content
        for element in soup.body.descendants if soup.body else []:
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                flush_section()
                current_section["heading"] = element.get_text(strip=True)
            elif element.name == "img":
                src = element.get("src")
                if src and src not in current_section["img_urls"]:
                    current_section["img_urls"].append(src)
            elif element.string and element.string.strip():
                # Only add meaningful text content
                text = element.string.strip()
                if len(text) > 3:  # Ignore very short strings
                    current_section["text_parts"].append(text)
        
        flush_section()
    
    # Final cleanup: Remove duplicate or very similar sections
    cleaned_sections = []
    seen_texts = set()
    
    for section in sections:
        # Create a signature of the section
        text_signature = section.text[:100].lower().strip() if section.text else ""
        
        # Skip if we've seen very similar content
        if text_signature and text_signature not in seen_texts:
            seen_texts.add(text_signature)
            cleaned_sections.append(section)
        elif section.heading and len(section.img_urls) > 0:
            # Keep sections with images even if text is similar
            cleaned_sections.append(section)
    
    # Reassign section IDs
    for i, section in enumerate(cleaned_sections):
        section.section_id = i
    
    return cleaned_sections

async def persist_analysis_input(job_id: int, sections: List[SectionData], db: AsyncSession):
    # Persist JSON to Job.analysis_input
    data = [asdict(s) for s in sections]
    json_str = json.dumps(data)
    job = await db.get(Job, job_id)
    job.analysis_input = json_str
    await db.commit() 