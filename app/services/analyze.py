import os
import openai
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import json
from app.models import Job
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings

@dataclass
class SectionAnalysis:
    section_id: int
    category: str
    short_copy: str
    original_text: str
    heading: str = None
    img_urls: List[str] = None
    classes: List[str] = None
    id: str = None

OPENAI_MODEL = settings.OPENAI_MODEL

PROMPT_TEMPLATE = """
You are an expert web content classifier and copywriter. For each section below, do the following:
1. Classify the section as one of: hero, about, services, gallery, contact, other.
2. Write a short, polished summary of the section (max 120 characters).

Respond in JSON as a list of objects with fields: section_id, category, short_copy.

Sections:
{sections_json}
"""

def analyze_sections(sections: List[Dict[str, Any]]) -> List[SectionAnalysis]:
    # Prepare prompt
    sections_json = json.dumps([
        {"section_id": s["section_id"], "heading": s.get("heading"), "text": s["text"]} for s in sections
    ], ensure_ascii=False)
    prompt = PROMPT_TEMPLATE.format(sections_json=sections_json)
    
    # Call OpenAI with new client
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2,
    )
    
    # Parse response
    import re
    import ast
    # Try to extract JSON from response
    content = response.choices[0].message.content
    
    # Debug: log the response content
    print(f"OpenAI Response: {content}")
    
    # Extract JSON from markdown code blocks or find JSON array
    json_match = re.search(r'```json\s*(\[.*?\])\s*```', content, re.DOTALL)
    if not json_match:
        json_match = re.search(r'(\[.*?\])', content, re.DOTALL)
    
    if json_match:
        result_json = json_match.group(1)
        try:
            result = json.loads(result_json)
        except Exception as e:
            print(f"JSON parsing error: {e}")
            try:
                result = ast.literal_eval(result_json)
            except Exception as e2:
                print(f"AST parsing error: {e2}")
                result = []
    else:
        # If no JSON array found, try to create a fallback response
        print(f"No JSON array found in response: {content}")
        result = []
    
    # If parsing failed, create fallback analysis
    if not result:
        print("Creating fallback analysis")
        for s in sections:
            result.append({
                "section_id": s["section_id"],
                "category": "other",
                "short_copy": s.get("text", "")[:120] if s.get("text") else "Content section"
            })
    
    # Map back to SectionAnalysis, include original fields
    by_id = {s["section_id"]: s for s in sections}
    analyses = []
    for item in result:
        sid = item["section_id"]
        orig = by_id.get(sid, {})
        analyses.append(SectionAnalysis(
            section_id=sid,
            category=item.get("category", "other"),
            short_copy=item.get("short_copy", ""),
            original_text=orig.get("text", ""),
            heading=orig.get("heading"),
            img_urls=orig.get("img_urls", []),
            classes=orig.get("classes", []),
            id=orig.get("id"),
        ))
    return analyses

async def persist_analysis_output(job_id: int, analyses: List[SectionAnalysis], db: AsyncSession):
    # Persist JSON to Job.analysis_output
    data = [asdict(a) for a in analyses]
    json_str = json.dumps(data)
    job = await db.get(Job, job_id)
    job.analysis_output = json_str
    await db.commit() 