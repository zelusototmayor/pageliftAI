import os
import openai
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import json
import re
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
2. Write an improved, polished summary of the section (aim for 150-300 characters for better quality).
3. Focus on business value and clear messaging while preserving key information.

Respond in JSON as a list of objects with fields: section_id, category, short_copy.

Sections:
{sections_json}
"""

def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 characters per token"""
    return len(text) // 4

def clean_text_content(text: str) -> str:
    """Remove HTML noise and optimize content for AI analysis"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common noise patterns
    noise_patterns = [
        r'\bcookie\b.*?policy\b.*?(?:\.|$)',  # Cookie notices
        r'\bterms\b.*?service\b.*?(?:\.|$)',  # Terms of service
        r'\bprivacy\b.*?policy\b.*?(?:\.|$)',  # Privacy policy
        r'\b(?:follow|like|share)\s+(?:us\s+)?on\s+(?:facebook|twitter|instagram|linkedin)\b.*?(?:\.|$)',  # Social media
        r'\b\d{4}\s+(?:all\s+)?rights?\s+reserved\b.*?(?:\.|$)',  # Copyright
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Limit very long text blocks to avoid token explosion
    if len(text) > 1000:
        sentences = text.split('. ')
        # Keep first few sentences that contain key business info
        key_sentences = []
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            if any(keyword in sentence.lower() for keyword in ['service', 'business', 'company', 'we', 'our', 'about', 'contact', 'phone', 'email']):
                key_sentences.append(sentence)
        
        if key_sentences:
            text = '. '.join(key_sentences) + '.'
        else:
            text = '. '.join(sentences[:5]) + '.'  # Fallback to first 5 sentences
    
    return text.strip()

def prioritize_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort sections by business importance"""
    def get_priority(section):
        text = (section.get('text') or '').lower()
        heading = (section.get('heading') or '').lower()
        classes = ' '.join(section.get('classes') or []).lower()
        
        # Hero/main content (highest priority)
        if any(keyword in (text + heading + classes) for keyword in ['hero', 'banner', 'main', 'welcome', 'home']):
            return 1
        
        # Services (very high priority)
        if any(keyword in (text + heading + classes) for keyword in ['service', 'offer', 'solution', 'product']):
            return 2
        
        # About (high priority)
        if any(keyword in (text + heading + classes) for keyword in ['about', 'company', 'business', 'who we are', 'our story']):
            return 3
        
        # Contact (high priority)
        if any(keyword in (text + heading + classes) for keyword in ['contact', 'phone', 'email', 'address', 'location', 'get in touch']):
            return 4
        
        # Gallery/testimonials (medium priority)
        if any(keyword in (text + heading + classes) for keyword in ['gallery', 'portfolio', 'testimonial', 'review', 'client']):
            return 5
        
        # Everything else (lower priority)
        return 6
    
    return sorted(sections, key=get_priority)

def chunk_sections(sections: List[Dict[str, Any]], max_tokens: int = 4000) -> List[List[Dict[str, Any]]]:
    """Split sections into chunks that fit within token limits"""
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for section in sections:
        # Clean and estimate tokens for this section
        cleaned_text = clean_text_content(section.get('text', ''))
        section_data = {
            "section_id": section["section_id"], 
            "heading": section.get("heading"), 
            "text": cleaned_text
        }
        section_tokens = estimate_tokens(json.dumps(section_data))
        
        # If adding this section would exceed limit, start new chunk
        if current_tokens + section_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [section_data]
            current_tokens = section_tokens
        else:
            current_chunk.append(section_data)
            current_tokens += section_tokens
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def analyze_sections(sections: List[Dict[str, Any]]) -> List[SectionAnalysis]:
    # Prioritize sections by business importance
    prioritized_sections = prioritize_sections(sections)
    
    # Split into manageable chunks
    chunks = chunk_sections(prioritized_sections, max_tokens=4000)
    
    print(f"Processing {len(sections)} sections in {len(chunks)} chunks")
    
    all_results = []
    client = openai.OpenAI()
    
    # Process each chunk separately
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)} with {len(chunk)} sections")
        
        sections_json = json.dumps(chunk, ensure_ascii=False)
        prompt = PROMPT_TEMPLATE.format(sections_json=sections_json)
        
        # Estimate total prompt tokens
        prompt_tokens = estimate_tokens(prompt)
        print(f"Chunk {i+1} estimated tokens: {prompt_tokens}")
        
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,  # Increased for better quality responses
                temperature=0.2,
            )
            
            # Parse this chunk's response
            chunk_results = parse_openai_response(response.choices[0].message.content, chunk)
            all_results.extend(chunk_results)
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            # Create fallback results for this chunk
            for section in chunk:
                all_results.append({
                    "section_id": section["section_id"],
                    "category": "other",
                    "short_copy": section.get("text", "")[:200] if section.get("text") else "Content section"
                })
    
    # Combine results from all chunks
    
    result = all_results
    
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
    
    print(f"Successfully analyzed {len(analyses)} sections")
    return analyses

def parse_openai_response(content: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse OpenAI response and extract JSON results"""
    import ast
    
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
            return result
        except Exception as e:
            print(f"JSON parsing error: {e}")
            try:
                result = ast.literal_eval(result_json)
                return result
            except Exception as e2:
                print(f"AST parsing error: {e2}")
    
    # If parsing failed, create fallback response
    print(f"No JSON array found in response, creating fallback")
    fallback_results = []
    for section in sections:
        fallback_results.append({
            "section_id": section["section_id"],
            "category": "other",
            "short_copy": section.get("text", "")[:200] if section.get("text") else "Content section"
        })
    return fallback_results

async def persist_analysis_output(job_id: int, analyses: List[SectionAnalysis], db: AsyncSession):
    # Persist JSON to Job.analysis_output
    data = [asdict(a) for a in analyses]
    json_str = json.dumps(data)
    job = await db.get(Job, job_id)
    job.analysis_output = json_str
    await db.commit() 