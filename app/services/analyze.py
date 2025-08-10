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
    # Enhanced fields for template rendering
    business_data: Dict[str, Any] = None
    confidence: float = 0.5
    reasoning: str = ""
    is_hybrid: bool = False
    hybrid_categories: List[str] = None
    phone_number: str = "#"
    email: str = "#"
    
    def __post_init__(self):
        if self.img_urls is None:
            self.img_urls = []
        if self.classes is None:
            self.classes = []
        if self.business_data is None:
            self.business_data = {}
        if self.hybrid_categories is None:
            self.hybrid_categories = []

OPENAI_MODEL = settings.OPENAI_MODEL

PROMPT_TEMPLATE = """
You are an expert web content analyzer that understands the intent and purpose behind different website sections.

For each section, analyze its semantic intent and classify it based on what the content is trying to achieve:

**CLASSIFICATION RULES:**

**HERO** - Primary value proposition and main call to action
- Contains company/service name prominently
- Describes main offering or value proposition
- Has primary call-to-action (CTA)
- Usually the first/most prominent section
- Intent: "What do we do?" or "Why choose us?"

**ABOUT** - Company background, story, credentials, team
- Describes company history, mission, values
- Mentions experience, expertise, qualifications
- Contains "about us", "who we are", "our story" language
- Intent: "Who are we?" or "Why trust us?"

**SERVICES** - Specific offerings, products, solutions
- Lists specific services or products offered
- Describes what customer can buy/get
- Contains pricing, packages, or service details
- Intent: "What can you buy from us?"

**CONTACT** - How to reach the business
- Contains contact information (phone, email, address)
- Has contact forms or location details
- Business hours, directions, contact methods
- Intent: "How to reach us?"

**GALLERY** - Visual showcases, portfolios, testimonials
- Contains multiple images or visual content
- Showcases work examples, before/after, projects
- Customer testimonials or reviews
- Intent: "Proof of our work" or "What others say"

**OTHER** - Content that doesn't fit above categories
- General information, policies, blog content
- Navigation elements, footers with mixed content
- Use this only when content doesn't clearly fit other categories

**ANALYSIS APPROACH:**
1. Look for intent keywords and semantic patterns
2. Consider section position and context clues
3. Analyze business data (phones, CTAs, forms) to inform classification
4. When unsure between categories, choose the most specific one
5. Preserve all original content while improving clarity

Respond in JSON format:
```json
[
  {{
    "section_id": number,
    "category": "hero|about|services|contact|gallery|other",
    "confidence": number (0.0-1.0),
    "short_copy": "improved version of content (150-300 chars)",
    "reasoning": "brief explanation of classification decision"
  }}
]
```

Sections to analyze:
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
            "heading": section.get("heading") or "", 
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
    chunks = chunk_sections(prioritized_sections, max_tokens=3500)  # Reduced to account for larger prompt
    
    print(f"Processing {len(sections)} sections in {len(chunks)} chunks with enhanced semantic analysis")
    
    all_results = []
    client = openai.OpenAI()
    
    # Process each chunk separately
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)} with {len(chunk)} sections")
        
        # Enhance section data with business context for better classification
        enhanced_chunk = []
        for section in chunk:
            enhanced_section = {
                "section_id": section["section_id"],
                "heading": section.get("heading", ""),
                "text": section.get("text", ""),
                "business_data": section.get("business_data", {}),
                "ctas": len(section.get("ctas", [])),
                "forms": len(section.get("forms", [])),
                "images": len(section.get("img_urls", [])),
                "position": section["section_id"],  # Relative position can help classification
                "classes": section.get("classes", []),
                "tag": section.get("tag", "")
            }
            enhanced_chunk.append(enhanced_section)
        
        sections_json = json.dumps(enhanced_chunk, ensure_ascii=False, indent=2)
        prompt = PROMPT_TEMPLATE.format(sections_json=sections_json)
        
        # Estimate total prompt tokens
        prompt_tokens = estimate_tokens(prompt)
        print(f"Chunk {i+1} estimated tokens: {prompt_tokens}")
        
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,  # Increased for enhanced responses with confidence and reasoning
                temperature=0.1,  # Lower temperature for more consistent classification
            )
            
            # Parse this chunk's response with enhanced format
            chunk_results = parse_enhanced_openai_response(response.choices[0].message.content, chunk)
            all_results.extend(chunk_results)
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            # Create fallback results with smart defaults based on content analysis
            for section in chunk:
                fallback_category = determine_fallback_category(section)
                all_results.append({
                    "section_id": section["section_id"],
                    "category": fallback_category,
                    "confidence": 0.3,  # Low confidence for fallback
                    "short_copy": section.get("text", "")[:200] if section.get("text") else "Content section",
                    "reasoning": "Fallback classification due to AI processing error"
                })
    
    # Combine results from all chunks
    result = all_results
    
    # Map back to SectionAnalysis, include original fields
    by_id = {s["section_id"]: s for s in sections}
    analyses = []
    for item in result:
        sid = item["section_id"]
        orig = by_id.get(sid, {})
        
        # Extract business data from original section
        business_data = orig.get("business_data", {})
        phones = business_data.get("phones", [])
        emails = business_data.get("emails", [])
        
        # Create enhanced SectionAnalysis with all required fields
        analysis = SectionAnalysis(
            section_id=sid,
            category=item.get("category", "other"),
            short_copy=item.get("short_copy", ""),
            original_text=orig.get("text", ""),
            heading=orig.get("heading"),
            img_urls=orig.get("img_urls", []),
            classes=orig.get("classes", []),
            id=orig.get("id"),
            # Enhanced fields
            business_data=business_data,
            confidence=item.get("confidence", 0.5),
            reasoning=item.get("reasoning", ""),
            is_hybrid=item.get("is_hybrid", False),
            hybrid_categories=item.get("hybrid_categories", []),
            phone_number=phones[0] if phones else "#",
            email=emails[0] if emails else "#"
        )
        
        analyses.append(analysis)
    
    # Post-process to improve classifications using context
    analyses = apply_contextual_improvements(analyses)
    
    print(f"Successfully analyzed {len(analyses)} sections with semantic intent analysis")
    
    # Log classification results
    category_counts = {}
    confidence_sum = 0
    for analysis in analyses:
        category = analysis.category
        category_counts[category] = category_counts.get(category, 0) + 1
        confidence_sum += getattr(analysis, 'confidence', 0.5)
    
    avg_confidence = confidence_sum / len(analyses) if analyses else 0
    print(f"Classification results: {category_counts}")
    print(f"Average confidence: {avg_confidence:.2f}")
    
    return analyses

def determine_fallback_category(section: Dict[str, Any]) -> str:
    """Smart fallback classification with multi-language support"""
    text = str(section.get("text") or "").lower()
    heading = str(section.get("heading") or "").lower()
    business_data = section.get("business_data", {})
    combined_text = text + " " + heading
    
    # Multi-language keyword sets
    contact_keywords = {
        # English
        "contact", "phone", "email", "address", "location", "call", "reach", "get in touch",
        "telephone", "mobile", "fax", "office", "hours", "schedule", "appointment",
        # Portuguese  
        "contacto", "contato", "telefone", "email", "morada", "endereço", "localização",
        "ligar", "contactar", "horário", "horarios", "marcação", "agendamento",
        "escritório", "gabinete", "atendimento", "fale connosco", "fale conosco",
        # Spanish (bonus)
        "contacto", "teléfono", "correo", "dirección", "ubicación", "llamar",
        # French (bonus)
        "contact", "téléphone", "adresse", "emplacement", "appeler"
    }
    
    services_keywords = {
        # English
        "service", "services", "product", "products", "offer", "offers", "solution", "solutions",
        "specialist", "expert", "professional", "provide", "deliver", "install", "repair",
        "maintenance", "consulting", "support", "help", "assist",
        # Portuguese
        "serviço", "serviços", "produto", "produtos", "oferta", "ofertas", "solução", "soluções",
        "especialista", "perito", "profissional", "fornecemos", "entregamos", "instalar",
        "reparar", "reparação", "manutenção", "consultoria", "apoio", "ajuda", "assistir",
        "desentupimento", "desentupimentos", "canalização", "canalizações", "plombing"
    }
    
    about_keywords = {
        # English  
        "about", "company", "business", "organization", "team", "staff", "history", "story",
        "experience", "years", "established", "founded", "mission", "vision", "values",
        "who we are", "our team", "our story", "our company", "background",
        # Portuguese
        "sobre", "empresa", "negócio", "organização", "equipa", "equipe", "pessoal", 
        "história", "experiência", "anos", "fundada", "estabelecida", "missão", "visão",
        "valores", "quem somos", "nossa equipa", "nossa empresa", "nossa história"
    }
    
    hero_keywords = {
        # English
        "welcome", "leading", "best", "top", "quality", "trusted", "professional", "expert",
        "choose", "why", "premier", "excellence", "outstanding", "reliable", "experienced",
        # Portuguese  
        "bem-vindo", "bem-vindos", "líder", "melhor", "qualidade", "confiança", "profissional",
        "especialista", "escolher", "porquê", "excelência", "excepcional", "fiável", 
        "experiente", "confiável", "anos de experiência"
    }
    
    gallery_keywords = {
        # English
        "gallery", "portfolio", "work", "projects", "examples", "showcase", "testimonial", 
        "testimonials", "review", "reviews", "client", "clients", "customer", "customers",
        # Portuguese
        "galeria", "portfólio", "trabalho", "projetos", "projectos", "exemplos", "mostrar",
        "testemunho", "testemunhos", "avaliação", "avaliações", "cliente", "clientes"
    }
    
    def has_keywords(keyword_set, minimum_matches=1):
        """Check if text contains keywords from the set"""
        matches = sum(1 for keyword in keyword_set if keyword in combined_text)
        return matches >= minimum_matches
    
    # Priority-based classification
    
    # 1. Contact (highest priority - business critical)
    if (business_data.get("phones") or business_data.get("emails") or 
        has_keywords(contact_keywords, minimum_matches=1)):
        return "contact"
    
    # 2. Services (high priority - revenue generating)
    if has_keywords(services_keywords, minimum_matches=1):
        return "services"
    
    # 3. About (medium priority - trust building)
    if has_keywords(about_keywords, minimum_matches=1):
        return "about"
    
    # 4. Hero (check for first section with value proposition keywords)
    if (section.get("section_id", 0) == 0 or 
        (has_keywords(hero_keywords, minimum_matches=1) and len(text) > 50)):
        return "hero"
    
    # 5. Gallery (testimonials, work examples)
    if has_keywords(gallery_keywords, minimum_matches=1):
        return "gallery"
    
    # 6. Additional context-based rules
    
    # If section has images and descriptive text, likely gallery
    if len(section.get("img_urls", [])) > 1 and len(text) > 30:
        return "gallery"
    
    # If first section and has business data, likely hero
    if section.get("section_id", 0) == 0 and (business_data.get("ctas") or business_data.get("phones")):
        return "hero"
    
    # If section has long text without specific keywords, likely about
    if len(text) > 100 and not has_keywords(services_keywords):
        return "about"
    
    return "other"

def parse_enhanced_openai_response(content: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse enhanced OpenAI response with confidence and reasoning"""
    import ast
    import logging
    
    # Debug: log the response content  
    print(f"Enhanced OpenAI Response: {content[:500]}...")
    
    # Try multiple JSON extraction strategies
    json_patterns = [
        r'```json\s*(.*?)\s*```',  # Markdown JSON blocks
        r'```\s*(.*?)\s*```',      # Any markdown code blocks
        r'(\[(?:[^\[\]]|\[(?:[^\[\]]|\[[^\]]*\])*\])*\])',  # Nested array matching
        r'(\[.*?\])',              # Simple array matching
    ]
    
    result_json = None
    for pattern in json_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            result_json = match.group(1)
            break
    
    if result_json:
        # Clean up common JSON issues
        result_json = result_json.strip()
        
        # Fix common formatting issues
        result_json = re.sub(r',\s*}', '}', result_json)  # Remove trailing commas in objects
        result_json = re.sub(r',\s*]', ']', result_json)  # Remove trailing commas in arrays
        result_json = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', result_json)  # Remove control characters
        
        # Try multiple parsing approaches
        parsing_attempts = [
            ("Standard JSON", lambda x: json.loads(x)),
            ("AST evaluation", lambda x: ast.literal_eval(x)),
            ("Relaxed JSON", lambda x: json.loads(re.sub(r"'([^']*)':", r'"\1":', x))),  # Replace single quotes
        ]
        
        for approach_name, parse_func in parsing_attempts:
            try:
                result = parse_func(result_json)
                print(f"Successfully parsed with {approach_name}")
                
                # Validate and normalize the response format
                validated_results = []
                for item in result:
                    if isinstance(item, dict) and "section_id" in item:
                        # Normalize category names
                        category = str(item.get("category", "other")).lower().strip()
                        valid_categories = ["hero", "about", "services", "contact", "gallery", "other"]
                        if category not in valid_categories:
                            category = "other"
                        
                        # Ensure confidence is valid
                        confidence = item.get("confidence", 0.5)
                        try:
                            confidence = float(confidence)
                            confidence = max(0.0, min(1.0, confidence))  # Clamp between 0-1
                        except (ValueError, TypeError):
                            confidence = 0.5
                        
                        validated_item = {
                            "section_id": int(item.get("section_id", 0)),
                            "category": category,
                            "confidence": confidence,
                            "short_copy": str(item.get("short_copy", ""))[:300],  # Limit length
                            "reasoning": str(item.get("reasoning", ""))[:200]    # Limit length
                        }
                        validated_results.append(validated_item)
                
                # Ensure we have results for all sections
                section_ids_found = {item["section_id"] for item in validated_results}
                section_ids_expected = {section["section_id"] for section in sections}
                
                for section in sections:
                    if section["section_id"] not in section_ids_found:
                        # Add missing section with fallback categorization
                        fallback_category = determine_fallback_category(section)
                        validated_results.append({
                            "section_id": section["section_id"],
                            "category": fallback_category,
                            "confidence": 0.6,  # Medium confidence for smart fallback
                            "short_copy": str(section.get("text", ""))[:200],
                            "reasoning": "Added via fallback logic"
                        })
                
                return validated_results
                
            except Exception as e:
                print(f"{approach_name} parsing failed: {e}")
                continue
    
    # If all parsing failed, create comprehensive fallback response
    print(f"All parsing attempts failed, creating comprehensive fallback")
    fallback_results = []
    
    for section in sections:
        fallback_category = determine_fallback_category(section)
        
        # Boost confidence for clearly identifiable content
        confidence = 0.4  # Default fallback confidence
        text = str(section.get("text", "")).lower()
        heading = str(section.get("heading", "")).lower()
        
        # Increase confidence for clear matches
        if ("contact" in heading or "phone" in text or "email" in text or 
            section.get("business_data", {}).get("phones")):
            confidence = 0.8
        elif ("about" in heading or "company" in text or "who we are" in text):
            confidence = 0.7  
        elif ("service" in text or "offer" in text):
            confidence = 0.7
        elif section.get("section_id", 0) == 0:  # First section often hero
            confidence = 0.6
            
        fallback_results.append({
            "section_id": section["section_id"],
            "category": fallback_category,
            "confidence": confidence,
            "short_copy": str(section.get("text", ""))[:200] if section.get("text") else "Content section",
            "reasoning": f"Intelligent fallback categorization (confidence boosted)"
        })
    
    return fallback_results

def detect_hybrid_categories(analysis: SectionAnalysis) -> List[str]:
    """Detect if content could fit multiple categories"""
    potential_categories = []
    text = (analysis.original_text or "").lower()
    heading = (analysis.heading or "").lower()
    
    # Check for hero characteristics
    if (analysis.section_id == 0 or "company" in text or "business" in text or 
        len(getattr(analysis, 'ctas', [])) > 0):
        potential_categories.append("hero")
    
    # Check for about characteristics  
    if ("about" in heading or "company" in text or "experience" in text or
        "team" in text or "years" in text or "established" in text):
        potential_categories.append("about")
    
    # Check for services characteristics
    if ("service" in text or "offer" in text or "solution" in text or
        "specialist" in text or "professional" in text):
        potential_categories.append("services")
    
    # Check for contact characteristics
    if (getattr(analysis, 'business_data', {}).get('phones') or 
        getattr(analysis, 'business_data', {}).get('emails') or
        "contact" in text or "phone" in text):
        potential_categories.append("contact")
    
    # Check for gallery characteristics
    if len(analysis.img_urls) >= 2:
        potential_categories.append("gallery")
    
    return list(set(potential_categories))

def apply_confidence_adjustments(analyses: List[SectionAnalysis]) -> List[SectionAnalysis]:
    """Adjust confidence scores based on context and hybrid detection"""
    
    for analysis in analyses:
        original_confidence = getattr(analysis, 'confidence', 0.5)
        
        # Detect hybrid categories
        potential_categories = detect_hybrid_categories(analysis)
        
        # If content fits multiple categories (hybrid content)
        if len(potential_categories) > 1:
            if analysis.category in potential_categories:
                # Current category is valid, but reduce confidence due to ambiguity
                analysis.confidence = min(original_confidence, 0.8)
                analysis.reasoning += f" (Hybrid content - could also be: {', '.join([c for c in potential_categories if c != analysis.category])})"
            else:
                # Current category not in potential list - very low confidence
                analysis.confidence = max(original_confidence * 0.5, 0.2)
                analysis.reasoning += f" (Low confidence - better fit might be: {', '.join(potential_categories)})"
        
        # Boost confidence for very clear classifications
        elif len(potential_categories) == 1 and potential_categories[0] == analysis.category:
            analysis.confidence = min(original_confidence * 1.1, 1.0)
            analysis.reasoning += " (High confidence - clear single category match)"
        
        # Add hybrid category info for complex content
        if len(potential_categories) > 2:
            analysis.hybrid_categories = potential_categories
            analysis.is_hybrid = True
        else:
            analysis.hybrid_categories = []
            analysis.is_hybrid = False
    
    return analyses

def create_mixed_content_section(analysis: SectionAnalysis, potential_categories: List[str]) -> SectionAnalysis:
    """Create a mixed content section for uncertain classifications"""
    # Create a hybrid category name
    if len(potential_categories) >= 2:
        primary_cat = potential_categories[0]
        secondary_cat = potential_categories[1]
        analysis.category = f"{primary_cat}_mixed"
        analysis.confidence = 0.65  # Medium confidence for mixed content
        analysis.reasoning = f"Mixed content spanning {primary_cat} and {secondary_cat} categories"
        analysis.is_hybrid = True
        analysis.hybrid_categories = potential_categories
    return analysis

def apply_progressive_classification(analysis: SectionAnalysis) -> SectionAnalysis:
    """Apply progressive classification refinement for uncertain content"""
    text = (analysis.original_text or "").lower()
    
    # Level 1: Keyword-based classification
    keyword_scores = {
        'hero': 0,
        'about': 0, 
        'services': 0,
        'contact': 0,
        'gallery': 0
    }
    
    # Hero keywords
    hero_keywords = ['welcome', 'company', 'business', 'home', 'main', 'professional', 'expert']
    keyword_scores['hero'] += sum(1 for kw in hero_keywords if kw in text)
    
    # About keywords  
    about_keywords = ['about', 'experience', 'years', 'team', 'history', 'story', 'established']
    keyword_scores['about'] += sum(1 for kw in about_keywords if kw in text)
    
    # Services keywords
    service_keywords = ['service', 'offer', 'solution', 'specialist', 'repair', 'fix', 'clean']
    keyword_scores['services'] += sum(1 for kw in service_keywords if kw in text)
    
    # Contact keywords
    contact_keywords = ['contact', 'phone', 'email', 'address', 'location', 'call', 'quote']
    keyword_scores['contact'] += sum(1 for kw in contact_keywords if kw in text)
    
    # Gallery keywords
    gallery_keywords = ['portfolio', 'gallery', 'photos', 'images', 'work', 'projects']
    keyword_scores['gallery'] += sum(1 for kw in gallery_keywords if kw in text)
    
    # Level 2: Structural analysis
    if len(analysis.img_urls) >= 2:
        keyword_scores['gallery'] += 2
    
    if analysis.section_id == 0:
        keyword_scores['hero'] += 2
    
    # Level 3: Business data analysis
    business_data = getattr(analysis, 'business_data', {})
    if business_data:
        if business_data.get('phones') or business_data.get('emails'):
            keyword_scores['contact'] += 3
        if business_data.get('ctas'):
            keyword_scores['hero'] += 2
            keyword_scores['services'] += 1
    
    # Find best match
    best_category = max(keyword_scores, key=keyword_scores.get)
    best_score = keyword_scores[best_category]
    
    if best_score >= 2:
        analysis.category = best_category
        analysis.confidence = min(0.7, 0.4 + (best_score * 0.1))
        analysis.reasoning = f"Progressive classification based on {best_score} indicators"
    else:
        # Create mixed content if multiple categories have similar scores
        top_categories = [cat for cat, score in keyword_scores.items() if score >= max(1, best_score - 1)]
        if len(top_categories) >= 2:
            analysis = create_mixed_content_section(analysis, top_categories[:2])
    
    return analysis

def apply_content_splitting_strategy(analysis: SectionAnalysis) -> List[SectionAnalysis]:
    """Split large uncertain sections into smaller, more classifiable parts"""
    text = analysis.original_text
    
    # Only split very large sections (>300 words) with low confidence
    if len(text.split()) < 300 or getattr(analysis, 'confidence', 0.5) > 0.6:
        return [analysis]
    
    # Split by paragraphs or sentences
    paragraphs = text.split('\n\n')
    if len(paragraphs) < 2:
        sentences = text.split('. ')
        if len(sentences) < 4:
            return [analysis]
        
        # Group sentences into meaningful chunks
        chunk_size = max(2, len(sentences) // 3)
        paragraphs = []
        for i in range(0, len(sentences), chunk_size):
            paragraphs.append('. '.join(sentences[i:i+chunk_size]))
    
    # Create sub-sections
    sub_sections = []
    for i, paragraph in enumerate(paragraphs):
        if len(paragraph.strip()) < 50:  # Skip very short paragraphs
            continue
            
        sub_analysis = SectionAnalysis(
            section_id=analysis.section_id + (i * 0.1),  # Fractional IDs for sub-sections
            category="other",
            short_copy=paragraph[:150] + "..." if len(paragraph) > 150 else paragraph,
            original_text=paragraph,
            heading=analysis.heading if i == 0 else None,
            img_urls=analysis.img_urls if i == 0 else [],
            classes=analysis.classes,
            id=analysis.id
        )
        
        # Apply progressive classification to each sub-section
        sub_analysis = apply_progressive_classification(sub_analysis)
        sub_sections.append(sub_analysis)
    
    return sub_sections if sub_sections else [analysis]

def apply_contextual_improvements(analyses: List[SectionAnalysis]) -> List[SectionAnalysis]:
    """Apply contextual rules to improve classification accuracy"""
    
    # Sort by section_id to analyze in order
    analyses.sort(key=lambda x: x.section_id)
    
    # Apply confidence adjustments and hybrid detection first
    analyses = apply_confidence_adjustments(analyses)
    
    # CRITICAL FIX: Ensure only ONE hero section per site
    hero_sections = [(i, analysis) for i, analysis in enumerate(analyses) if analysis.category == "hero"]
    if len(hero_sections) > 1:
        print(f"⚠️  Found {len(hero_sections)} hero sections - limiting to one")
        
        # Find the best hero section (prefer first section with highest confidence)
        best_hero_idx = 0
        best_hero_score = -1
        
        for i, (idx, analysis) in enumerate(hero_sections):
            confidence = getattr(analysis, 'confidence', 0.5)
            # Score: position preference (first section gets bonus) + confidence
            score = (10 if analysis.section_id == 0 else 0) + confidence * 5
            
            if score > best_hero_score:
                best_hero_score = score
                best_hero_idx = i
        
        # Convert all other hero sections to appropriate categories
        for i, (idx, analysis) in enumerate(hero_sections):
            if i != best_hero_idx:
                # Reclassify based on content
                text = (analysis.original_text or "").lower()
                
                if ("about" in text or "company" in text or "experience" in text or 
                    "team" in text or "years" in text):
                    new_category = "about"
                elif ("service" in text or "offer" in text or "solution" in text):
                    new_category = "services"
                elif ("contact" in text or "phone" in text or 
                      getattr(analysis, 'business_data', {}).get('phones')):
                    new_category = "contact"
                else:
                    new_category = "about"  # Default fallback for hero-like content
                
                analyses[idx].category = new_category
                analyses[idx].confidence = getattr(analysis, 'confidence', 0.5) * 0.8  # Reduce confidence
                analyses[idx].reasoning = f"Reclassified from hero to {new_category} (only one hero allowed per site)"
                
                print(f"   ✅ Converted hero section {analysis.section_id} to {new_category}")
        
        print(f"   🎯 Kept section {hero_sections[best_hero_idx][1].section_id} as the primary hero")
    
    # Apply fallback strategies for uncertain content
    improved_analyses = []
    for i, analysis in enumerate(analyses):
        current_confidence = getattr(analysis, 'confidence', 0.5)
        
        # Strategy 1: Progressive classification for very low confidence
        if current_confidence < 0.4:
            analysis = apply_progressive_classification(analysis)
            
        # Strategy 2: Content splitting for large uncertain sections
        if (current_confidence < 0.5 and 
            len(analysis.original_text.split()) > 200 and
            analysis.category == "other"):
            sub_sections = apply_content_splitting_strategy(analysis)
            improved_analyses.extend(sub_sections)
            continue
        
        # Strategy 3: Contextual improvement rules (existing logic)
        
        # Rule 1: First section with company name is likely hero
        if (i == 0 and analysis.category == "other" and 
            analysis.heading and len(analysis.heading) > 5):
            analysis.category = "hero"
            analysis.confidence = 0.7
            analysis.reasoning = "First section with prominent heading - likely hero"
        
        # Rule 2: Sections with multiple CTAs are likely hero or services
        text_for_cta = (analysis.original_text or "").lower()
        cta_count = text_for_cta.count("contact") + text_for_cta.count("call")
        if cta_count >= 2 and analysis.category == "other":
            if i == 0:
                analysis.category = "hero"
                analysis.reasoning = "First section with multiple CTAs - hero"
            else:
                analysis.category = "services"
                analysis.reasoning = "Multiple CTAs detected - services"
            analysis.confidence = 0.8
        
        # Rule 3: Footer-like sections are often contact
        if (analysis.classes and any("footer" in cls.lower() for cls in analysis.classes) and
            analysis.category == "other"):
            analysis.category = "contact"
            analysis.confidence = 0.7
            analysis.reasoning = "Footer section with business info - contact"
        
        # Rule 4: Sections with only images might be gallery
        if (len(analysis.img_urls) >= 2 and len(analysis.original_text.split()) < 20 and
            analysis.category == "other"):
            analysis.category = "gallery"
            analysis.confidence = 0.6
            analysis.reasoning = "Multiple images with minimal text - gallery"
        
        # Rule 5: Handle remaining low confidence classifications with hybrid options
        current_confidence = getattr(analysis, 'confidence', 0.5)
        if current_confidence < 0.4:
            # Try to find a better category from hybrid options
            potential_categories = getattr(analysis, 'hybrid_categories', [])
            if potential_categories:
                # Choose the most likely alternative
                if 'hero' in potential_categories and i == 0:
                    analysis.category = 'hero'
                    analysis.confidence = 0.6
                elif 'contact' in potential_categories and (
                    getattr(analysis, 'business_data', {}).get('phones') or
                    getattr(analysis, 'business_data', {}).get('emails')):
                    analysis.category = 'contact'
                    analysis.confidence = 0.6
                elif 'services' in potential_categories:
                    analysis.category = 'services'
                    analysis.confidence = 0.6
                else:
                    # Create mixed content as final fallback
                    analysis = create_mixed_content_section(analysis, potential_categories[:2])
                
                analysis.reasoning += " (Improved from low-confidence classification)"
        
        improved_analyses.append(analysis)
    
    return improved_analyses

def parse_openai_response(content: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse OpenAI response and extract JSON results (legacy compatibility)"""
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