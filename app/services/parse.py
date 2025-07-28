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
    soup = BeautifulSoup(html, "html.parser")
    sections = []
    section_id = 0
    # 1. Extract all <section> and <div> with class/id as atomic sections
    atomic_blocks = []
    for tag in ["section", "div"]:
        for el in soup.find_all(tag):
            if el.get("class") or el.get("id"):
                text = el.get_text(" ", strip=True)
                imgs = [img.get("src") for img in el.find_all("img") if img.get("src")]
                classes = el.get("class", [])
                el_id = el.get("id")
                atomic_blocks.append((el, SectionData(
                    section_id=section_id,
                    heading=None,
                    text=text,
                    img_urls=imgs,
                    classes=classes,
                    id=el_id
                )))
                section_id += 1
    # Remove atomic blocks from soup to avoid double-counting
    for el, _ in atomic_blocks:
        el.decompose()
    sections.extend([sd for _, sd in atomic_blocks])
    # 2. Heading-based splitting on remaining content
    current = {
        "heading": None,
        "text": [],
        "img_urls": []
    }
    def flush():
        nonlocal section_id
        if current["text"] or current["heading"] or current["img_urls"]:
            sections.append(SectionData(
                section_id=section_id,
                heading=current["heading"],
                text=" ".join(current["text"]).strip(),
                img_urls=current["img_urls"],
                classes=[],
                id=None
            ))
            section_id += 1
            current["heading"] = None
            current["text"] = []
            current["img_urls"] = []
    for el in soup.body.descendants if soup.body else []:
        if el.name in ["h1", "h2", "h3"]:
            flush()
            current["heading"] = el.get_text(strip=True)
        elif el.name == "img":
            src = el.get("src")
            if src:
                current["img_urls"].append(src)
        elif el.string and el.string.strip():
            current["text"].append(el.string.strip())
    flush()
    return sections

async def persist_analysis_input(job_id: int, sections: List[SectionData], db: AsyncSession):
    # Persist JSON to Job.analysis_input
    data = [asdict(s) for s in sections]
    json_str = json.dumps(data)
    job = await db.get(Job, job_id)
    job.analysis_input = json_str
    await db.commit() 