"""
Component-Based Template Mixing System
Intelligent mixing and combination of template components based on content analysis
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from pathlib import Path


class ComponentType(Enum):
    """Types of template components"""
    HERO = "hero"
    SERVICES = "services"
    ABOUT = "about"
    TESTIMONIALS = "testimonials"
    CONTACT = "contact"
    FOOTER = "footer"
    GALLERY = "gallery"
    PRICING = "pricing"
    FAQ = "faq"
    TEAM = "team"
    FEATURES = "features"
    CTA = "cta"


class ContentVolume(Enum):
    """Content volume classifications"""
    MINIMAL = "minimal"      # <100 chars
    STANDARD = "standard"    # 100-300 chars
    RICH = "rich"           # 300-800 chars
    COMPREHENSIVE = "comprehensive"  # >800 chars


class IndustryType(Enum):
    """Industry classifications for component selection"""
    PLUMBING = "plumbing"
    RESTAURANT = "restaurant"
    TECH = "tech"
    MEDICAL = "medical"
    BUSINESS = "business"
    RETAIL = "retail"
    LEGAL = "legal"
    REAL_ESTATE = "real_estate"
    AUTOMOTIVE = "automotive"
    EDUCATION = "education"


@dataclass
class ComponentVariant:
    """Individual component variant with metadata"""
    name: str
    template_path: str
    content_volume: ContentVolume
    industry_fit: List[IndustryType]
    layout_style: str  # modern, classic, minimal, bold
    complexity: str    # simple, medium, complex
    required_data: List[str]
    optional_data: List[str] = field(default_factory=list)
    visual_weight: int = 1  # 1-5 scale for visual hierarchy
    mobile_optimized: bool = True
    touch_friendly: bool = True
    accessibility_score: int = 5  # 1-5 scale


@dataclass
class ComponentCombination:
    """A validated combination of components"""
    components: List[ComponentVariant]
    layout_score: float
    content_fit_score: float
    industry_fit_score: float
    visual_hierarchy_score: float
    total_score: float
    reasoning: str


class ComponentMixer:
    """Intelligent component mixing and template generation"""
    
    def __init__(self):
        self.component_registry = self._build_component_registry()
        self.layout_rules = self._define_layout_rules()
        self.industry_preferences = self._define_industry_preferences()
        
    def mix_components(
        self,
        content_analysis: Dict[str, Any],
        brand_identity: Dict[str, Any],
        requirements: Optional[Dict[str, Any]] = None
    ) -> ComponentCombination:
        """Generate optimal component combination"""
        
        # Analyze content characteristics
        content_profile = self._analyze_content_profile(content_analysis)
        
        # Determine industry and style preferences
        industry = self._extract_industry(brand_identity)
        style_preferences = self._extract_style_preferences(brand_identity)
        
        # Generate candidate combinations
        candidates = self._generate_component_candidates(
            content_profile, industry, style_preferences, requirements or {}
        )
        
        # Score and rank combinations
        scored_combinations = [
            self._score_combination(combo, content_profile, industry, style_preferences)
            for combo in candidates
        ]
        
        # Return best combination
        best_combination = max(scored_combinations, key=lambda x: x.total_score)
        
        return best_combination
    
    def get_component_variants(self, component_type: ComponentType) -> List[ComponentVariant]:
        """Get all variants for a specific component type"""
        return self.component_registry.get(component_type, [])
    
    def validate_combination(self, components: List[ComponentVariant]) -> Tuple[bool, List[str]]:
        """Validate component combination for conflicts and requirements"""
        issues = []
        
        # Check for required data conflicts
        all_required_data = set()
        for component in components:
            all_required_data.update(component.required_data)
        
        # Check visual hierarchy balance
        total_weight = sum(c.visual_weight for c in components)
        if total_weight > 20:
            issues.append("Visual hierarchy too heavy - reduce component complexity")
        elif total_weight < 8:
            issues.append("Visual hierarchy too light - consider more engaging components")
        
        # Check mobile optimization
        mobile_optimized = all(c.mobile_optimized for c in components)
        if not mobile_optimized:
            issues.append("Some components are not mobile optimized")
        
        # Check layout flow
        if not self._validate_layout_flow(components):
            issues.append("Component layout flow has issues")
        
        return len(issues) == 0, issues
    
    def _build_component_registry(self) -> Dict[ComponentType, List[ComponentVariant]]:
        """Build comprehensive component registry"""
        registry = {}
        
        # Hero Component Variants
        registry[ComponentType.HERO] = [
            ComponentVariant(
                name="hero_minimal",
                template_path="blocks/hero_minimal.html",
                content_volume=ContentVolume.MINIMAL,
                industry_fit=[IndustryType.TECH, IndustryType.BUSINESS, IndustryType.MEDICAL],
                layout_style="minimal",
                complexity="simple",
                required_data=["heading", "short_copy"],
                optional_data=["phone_number", "email", "background_image"],
                visual_weight=3,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=5
            ),
            ComponentVariant(
                name="hero_modern", 
                template_path="blocks/hero_modern.html",
                content_volume=ContentVolume.STANDARD,
                industry_fit=[IndustryType.PLUMBING, IndustryType.RESTAURANT, IndustryType.RETAIL],
                layout_style="modern",
                complexity="medium",
                required_data=["heading", "short_copy", "brand_identity"],
                optional_data=["phone_number", "hero_image", "services"],
                visual_weight=4,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            ),
            ComponentVariant(
                name="hero_responsive",
                template_path="blocks/hero_responsive.html", 
                content_volume=ContentVolume.RICH,
                industry_fit=[IndustryType.REAL_ESTATE, IndustryType.AUTOMOTIVE, IndustryType.LEGAL],
                layout_style="bold",
                complexity="complex",
                required_data=["heading", "original_text", "brand_identity"],
                optional_data=["multiple_images", "video", "testimonial"],
                visual_weight=5,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            )
        ]
        
        # Services Component Variants
        registry[ComponentType.SERVICES] = [
            ComponentVariant(
                name="services_grid_simple",
                template_path="blocks/services_grid_simple.html",
                content_volume=ContentVolume.MINIMAL,
                industry_fit=[IndustryType.BUSINESS, IndustryType.TECH],
                layout_style="minimal",
                complexity="simple",
                required_data=["services"],
                optional_data=["service_images", "pricing"],
                visual_weight=2,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=5
            ),
            ComponentVariant(
                name="services_cards_modern",
                template_path="blocks/services_cards_modern.html",
                content_volume=ContentVolume.STANDARD,
                industry_fit=[IndustryType.PLUMBING, IndustryType.MEDICAL, IndustryType.AUTOMOTIVE],
                layout_style="modern",
                complexity="medium", 
                required_data=["services", "brand_colors"],
                optional_data=["service_icons", "pricing", "cta_buttons"],
                visual_weight=3,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            ),
            ComponentVariant(
                name="services_showcase_rich",
                template_path="blocks/services_showcase_rich.html",
                content_volume=ContentVolume.RICH,
                industry_fit=[IndustryType.RESTAURANT, IndustryType.RETAIL, IndustryType.REAL_ESTATE],
                layout_style="bold",
                complexity="complex",
                required_data=["services", "detailed_descriptions", "images"],
                optional_data=["testimonials", "before_after", "portfolio"],
                visual_weight=4,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            )
        ]
        
        # Contact Component Variants
        registry[ComponentType.CONTACT] = [
            ComponentVariant(
                name="contact_minimal",
                template_path="blocks/contact_minimal.html",
                content_volume=ContentVolume.MINIMAL,
                industry_fit=[IndustryType.TECH, IndustryType.BUSINESS],
                layout_style="minimal",
                complexity="simple",
                required_data=["phone_number", "email"],
                optional_data=["address", "hours"],
                visual_weight=1,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=5
            ),
            ComponentVariant(
                name="contact_form_modern",
                template_path="blocks/contact_form_modern.html",
                content_volume=ContentVolume.STANDARD,
                industry_fit=[IndustryType.PLUMBING, IndustryType.MEDICAL, IndustryType.LEGAL],
                layout_style="modern",
                complexity="medium",
                required_data=["contact_form", "phone_number"],
                optional_data=["map", "social_media", "hours"],
                visual_weight=3,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            ),
            ComponentVariant(
                name="contact_comprehensive",
                template_path="blocks/contact_comprehensive.html",
                content_volume=ContentVolume.RICH,
                industry_fit=[IndustryType.RESTAURANT, IndustryType.RETAIL, IndustryType.REAL_ESTATE],
                layout_style="bold",
                complexity="complex",
                required_data=["contact_form", "map", "phone_number", "address"],
                optional_data=["multiple_locations", "team_photos", "social_proof"],
                visual_weight=4,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            )
        ]
        
        # About Component Variants
        registry[ComponentType.ABOUT] = [
            ComponentVariant(
                name="about_simple",
                template_path="blocks/about_simple.html",
                content_volume=ContentVolume.MINIMAL,
                industry_fit=[IndustryType.TECH, IndustryType.BUSINESS],
                layout_style="minimal",
                complexity="simple",
                required_data=["about_text"],
                optional_data=["team_photo", "years_experience"],
                visual_weight=2,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=5
            ),
            ComponentVariant(
                name="about_story_rich",
                template_path="blocks/about_story_rich.html",
                content_volume=ContentVolume.RICH,
                industry_fit=[IndustryType.RESTAURANT, IndustryType.MEDICAL, IndustryType.LEGAL],
                layout_style="modern",
                complexity="complex",
                required_data=["about_text", "story", "values"],
                optional_data=["founder_photo", "timeline", "achievements"],
                visual_weight=4,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            )
        ]
        
        # CTA Component Variants  
        registry[ComponentType.CTA] = [
            ComponentVariant(
                name="cta_simple",
                template_path="blocks/cta_simple.html",
                content_volume=ContentVolume.MINIMAL,
                industry_fit=list(IndustryType),  # Universal
                layout_style="minimal",
                complexity="simple",
                required_data=["cta_text", "phone_number"],
                optional_data=["urgency_text"],
                visual_weight=2,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=5
            ),
            ComponentVariant(
                name="cta_emergency",
                template_path="blocks/cta_emergency.html",
                content_volume=ContentVolume.STANDARD,
                industry_fit=[IndustryType.PLUMBING, IndustryType.MEDICAL, IndustryType.AUTOMOTIVE],
                layout_style="bold",
                complexity="medium",
                required_data=["emergency_phone", "emergency_text"],
                optional_data=["service_area", "response_time"],
                visual_weight=4,
                mobile_optimized=True,
                touch_friendly=True,
                accessibility_score=4
            )
        ]
        
        return registry
    
    def _define_layout_rules(self) -> Dict[str, Any]:
        """Define rules for component layout and flow"""
        return {
            "required_components": [ComponentType.HERO, ComponentType.CONTACT],
            "recommended_order": [
                ComponentType.HERO,
                ComponentType.SERVICES,
                ComponentType.ABOUT,
                ComponentType.TESTIMONIALS,
                ComponentType.GALLERY,
                ComponentType.PRICING,
                ComponentType.FAQ,
                ComponentType.CTA,
                ComponentType.CONTACT,
                ComponentType.FOOTER
            ],
            "visual_weight_balance": {
                "max_total": 20,
                "min_total": 8,
                "hero_min": 3,
                "heavy_components_max": 2  # Components with weight > 4
            },
            "complexity_rules": {
                "max_complex": 2,
                "balance_simple_complex": True
            }
        }
    
    def _define_industry_preferences(self) -> Dict[IndustryType, Dict[str, Any]]:
        """Define industry-specific component preferences"""
        return {
            IndustryType.PLUMBING: {
                "preferred_components": [ComponentType.HERO, ComponentType.SERVICES, ComponentType.CTA, ComponentType.CONTACT],
                "style_preference": "modern",
                "visual_weight_preference": "medium",
                "emergency_focused": True
            },
            IndustryType.RESTAURANT: {
                "preferred_components": [ComponentType.HERO, ComponentType.GALLERY, ComponentType.SERVICES, ComponentType.ABOUT, ComponentType.CONTACT],
                "style_preference": "bold",
                "visual_weight_preference": "high",
                "visual_heavy": True
            },
            IndustryType.TECH: {
                "preferred_components": [ComponentType.HERO, ComponentType.FEATURES, ComponentType.ABOUT, ComponentType.CONTACT],
                "style_preference": "minimal",
                "visual_weight_preference": "low",
                "clean_focused": True
            },
            IndustryType.MEDICAL: {
                "preferred_components": [ComponentType.HERO, ComponentType.SERVICES, ComponentType.TEAM, ComponentType.TESTIMONIALS, ComponentType.CONTACT],
                "style_preference": "modern",
                "visual_weight_preference": "medium",
                "trust_focused": True
            },
            IndustryType.BUSINESS: {
                "preferred_components": [ComponentType.HERO, ComponentType.SERVICES, ComponentType.ABOUT, ComponentType.CONTACT],
                "style_preference": "minimal",
                "visual_weight_preference": "medium",
                "professional_focused": True
            }
        }
    
    def _analyze_content_profile(self, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content to determine optimal component requirements"""
        
        # Determine content volume
        text_content = content_analysis.get('original_text', '') or content_analysis.get('short_copy', '')
        content_length = len(text_content)
        
        if content_length < 100:
            volume = ContentVolume.MINIMAL
        elif content_length < 300:
            volume = ContentVolume.STANDARD
        elif content_length < 800:
            volume = ContentVolume.RICH
        else:
            volume = ContentVolume.COMPREHENSIVE
        
        # Analyze available data types
        available_data = []
        if content_analysis.get('phone_number'):
            available_data.append('phone_number')
        if content_analysis.get('email'):
            available_data.append('email')
        if content_analysis.get('address'):
            available_data.append('address')
        if content_analysis.get('services'):
            available_data.append('services')
        if content_analysis.get('images'):
            available_data.append('images')
        if content_analysis.get('testimonials'):
            available_data.append('testimonials')
        
        # Determine content focus
        content_focus = []
        if 'emergency' in text_content.lower() or '24/7' in text_content:
            content_focus.append('emergency')
        if any(word in text_content.lower() for word in ['experience', 'professional', 'expert']):
            content_focus.append('expertise')
        if any(word in text_content.lower() for word in ['family', 'local', 'community']):
            content_focus.append('personal')
        
        return {
            'volume': volume,
            'available_data': available_data,
            'content_focus': content_focus,
            'text_length': content_length,
            'has_rich_media': bool(content_analysis.get('images')),
            'has_contact_info': bool(content_analysis.get('phone_number') or content_analysis.get('email'))
        }
    
    def _extract_industry(self, brand_identity: Dict[str, Any]) -> IndustryType:
        """Extract industry type from brand identity"""
        industry_str = brand_identity.get('brand', {}).get('industry', 'business').lower()
        
        industry_mapping = {
            'plumbing': IndustryType.PLUMBING,
            'restaurant': IndustryType.RESTAURANT,
            'food': IndustryType.RESTAURANT,
            'tech': IndustryType.TECH,
            'technology': IndustryType.TECH,
            'medical': IndustryType.MEDICAL,
            'healthcare': IndustryType.MEDICAL,
            'business': IndustryType.BUSINESS,
            'retail': IndustryType.RETAIL,
            'legal': IndustryType.LEGAL,
            'law': IndustryType.LEGAL,
            'real_estate': IndustryType.REAL_ESTATE,
            'realestate': IndustryType.REAL_ESTATE,
            'automotive': IndustryType.AUTOMOTIVE,
            'auto': IndustryType.AUTOMOTIVE,
            'education': IndustryType.EDUCATION
        }
        
        return industry_mapping.get(industry_str, IndustryType.BUSINESS)
    
    def _extract_style_preferences(self, brand_identity: Dict[str, Any]) -> Dict[str, Any]:
        """Extract style preferences from brand identity"""
        tone = brand_identity.get('brand', {}).get('tone', 'professional').lower()
        
        style_mapping = {
            'professional': 'modern',
            'friendly': 'modern',
            'urgent': 'bold',
            'emergency': 'bold',
            'elegant': 'minimal',
            'sophisticated': 'minimal',
            'approachable': 'modern',
            'trustworthy': 'modern'
        }
        
        return {
            'layout_style': style_mapping.get(tone, 'modern'),
            'visual_emphasis': 'high' if tone in ['urgent', 'emergency'] else 'medium',
            'complexity_preference': 'simple' if tone in ['elegant', 'sophisticated'] else 'medium'
        }
    
    def _generate_component_candidates(
        self,
        content_profile: Dict[str, Any],
        industry: IndustryType,
        style_preferences: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[List[ComponentVariant]]:
        """Generate candidate component combinations"""
        
        candidates = []
        
        # Get industry preferences
        industry_prefs = self.industry_preferences.get(industry, {})
        preferred_components = industry_prefs.get('preferred_components', [ComponentType.HERO, ComponentType.SERVICES, ComponentType.CONTACT])
        
        # Filter components by content volume and industry fit
        volume = content_profile['volume']
        available_components = {}
        
        for comp_type, variants in self.component_registry.items():
            available_components[comp_type] = [
                v for v in variants
                if (v.content_volume == volume or 
                    (volume == ContentVolume.COMPREHENSIVE and v.content_volume == ContentVolume.RICH)) and
                industry in v.industry_fit
            ]
        
        # Generate base combinations
        base_combinations = [
            # Minimal combination
            [ComponentType.HERO, ComponentType.CONTACT],
            # Standard combination
            [ComponentType.HERO, ComponentType.SERVICES, ComponentType.CONTACT],
            # Extended combination
            [ComponentType.HERO, ComponentType.SERVICES, ComponentType.ABOUT, ComponentType.CONTACT],
            # Full combination (based on industry preferences)
            preferred_components
        ]
        
        # Create variant combinations
        for base_combo in base_combinations:
            try:
                variant_combo = []
                for comp_type in base_combo:
                    variants = available_components.get(comp_type, [])
                    if variants:
                        # Select best fitting variant
                        best_variant = self._select_best_variant(variants, style_preferences, content_profile)
                        if best_variant:
                            variant_combo.append(best_variant)
                
                if len(variant_combo) >= 2:  # Minimum viable combination
                    candidates.append(variant_combo)
                    
            except Exception:
                # Skip problematic combinations
                continue
        
        # Remove duplicates
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            candidate_sig = tuple(c.name for c in candidate)
            if candidate_sig not in seen:
                seen.add(candidate_sig)
                unique_candidates.append(candidate)
        
        return unique_candidates[:10]  # Limit to top 10 candidates
    
    def _select_best_variant(
        self,
        variants: List[ComponentVariant],
        style_preferences: Dict[str, Any],
        content_profile: Dict[str, Any]
    ) -> Optional[ComponentVariant]:
        """Select the best variant from available options"""
        
        if not variants:
            return None
        
        preferred_style = style_preferences.get('layout_style', 'modern')
        
        # Score each variant
        scored_variants = []
        for variant in variants:
            score = 0
            
            # Style match
            if variant.layout_style == preferred_style:
                score += 3
            
            # Data availability match
            available_data = set(content_profile.get('available_data', []))
            required_data = set(variant.required_data)
            if required_data.issubset(available_data):
                score += 5
            else:
                score -= 2  # Penalty for missing required data
            
            # Accessibility and mobile optimization
            score += variant.accessibility_score
            if variant.mobile_optimized:
                score += 2
            if variant.touch_friendly:
                score += 1
            
            scored_variants.append((variant, score))
        
        # Return highest scoring variant
        if scored_variants:
            return max(scored_variants, key=lambda x: x[1])[0]
        
        return variants[0]  # Fallback to first variant
    
    def _score_combination(
        self,
        components: List[ComponentVariant],
        content_profile: Dict[str, Any],
        industry: IndustryType,
        style_preferences: Dict[str, Any]
    ) -> ComponentCombination:
        """Score a component combination comprehensively"""
        
        # Layout score (component flow and structure)
        layout_score = self._score_layout(components)
        
        # Content fit score (how well components match available content)
        content_fit_score = self._score_content_fit(components, content_profile)
        
        # Industry fit score (how well components suit the industry)
        industry_fit_score = self._score_industry_fit(components, industry)
        
        # Visual hierarchy score (balanced visual weight and flow)
        visual_hierarchy_score = self._score_visual_hierarchy(components)
        
        # Calculate weighted total score
        total_score = (
            layout_score * 0.25 +
            content_fit_score * 0.30 +
            industry_fit_score * 0.25 +
            visual_hierarchy_score * 0.20
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            components, layout_score, content_fit_score, 
            industry_fit_score, visual_hierarchy_score
        )
        
        return ComponentCombination(
            components=components,
            layout_score=layout_score,
            content_fit_score=content_fit_score,
            industry_fit_score=industry_fit_score,
            visual_hierarchy_score=visual_hierarchy_score,
            total_score=total_score,
            reasoning=reasoning
        )
    
    def _score_layout(self, components: List[ComponentVariant]) -> float:
        """Score component layout and flow"""
        score = 0.0
        
        # Check for required components
        component_types = {ComponentType(c.name.split('_')[0]) for c in components}
        required_types = set(self.layout_rules['required_components'])
        
        if required_types.issubset(component_types):
            score += 30
        else:
            missing = required_types - component_types
            score -= len(missing) * 10
        
        # Check component count (optimal range)
        comp_count = len(components)
        if 3 <= comp_count <= 6:
            score += 20
        elif comp_count == 2:
            score += 10
        elif comp_count > 6:
            score -= (comp_count - 6) * 5
        
        # Check complexity balance
        complexities = [c.complexity for c in components]
        complex_count = complexities.count('complex')
        simple_count = complexities.count('simple')
        
        if complex_count <= 2 and simple_count >= 1:
            score += 15
        
        return max(0, min(100, score))
    
    def _score_content_fit(self, components: List[ComponentVariant], content_profile: Dict[str, Any]) -> float:
        """Score how well components fit available content"""
        score = 0.0
        available_data = set(content_profile.get('available_data', []))
        
        for component in components:
            required_data = set(component.required_data)
            optional_data = set(component.optional_data)
            
            # Required data availability
            if required_data.issubset(available_data):
                score += 25
            else:
                missing_required = required_data - available_data
                score -= len(missing_required) * 10
            
            # Optional data availability (bonus)
            available_optional = optional_data.intersection(available_data)
            score += len(available_optional) * 2
        
        return max(0, min(100, score / len(components)))
    
    def _score_industry_fit(self, components: List[ComponentVariant], industry: IndustryType) -> float:
        """Score industry appropriateness"""
        score = 0.0
        
        for component in components:
            if industry in component.industry_fit:
                score += 25
            else:
                score -= 5
        
        return max(0, min(100, score / len(components)))
    
    def _score_visual_hierarchy(self, components: List[ComponentVariant]) -> float:
        """Score visual hierarchy and balance"""
        score = 50  # Base score
        
        total_weight = sum(c.visual_weight for c in components)
        weight_rules = self.layout_rules['visual_weight_balance']
        
        # Check total weight balance
        if weight_rules['min_total'] <= total_weight <= weight_rules['max_total']:
            score += 20
        else:
            if total_weight < weight_rules['min_total']:
                score -= (weight_rules['min_total'] - total_weight) * 5
            else:
                score -= (total_weight - weight_rules['max_total']) * 3
        
        # Check for hero prominence
        hero_components = [c for c in components if 'hero' in c.name]
        if hero_components and hero_components[0].visual_weight >= weight_rules['hero_min']:
            score += 15
        
        # Check heavy components limit
        heavy_components = [c for c in components if c.visual_weight > 4]
        if len(heavy_components) <= weight_rules['heavy_components_max']:
            score += 15
        else:
            score -= (len(heavy_components) - weight_rules['heavy_components_max']) * 10
        
        return max(0, min(100, score))
    
    def _generate_reasoning(
        self,
        components: List[ComponentVariant],
        layout_score: float,
        content_fit_score: float,
        industry_fit_score: float,
        visual_hierarchy_score: float
    ) -> str:
        """Generate human-readable reasoning for component selection"""
        
        component_names = [c.name.replace('_', ' ').title() for c in components]
        component_list = ', '.join(component_names)
        
        reasoning_parts = [
            f"Selected components: {component_list}"
        ]
        
        if layout_score >= 80:
            reasoning_parts.append("Excellent layout structure with optimal component flow.")
        elif layout_score >= 60:
            reasoning_parts.append("Good layout structure with minor optimization opportunities.")
        else:
            reasoning_parts.append("Layout structure needs improvement for better user experience.")
        
        if content_fit_score >= 80:
            reasoning_parts.append("Components perfectly match available content data.")
        elif content_fit_score >= 60:
            reasoning_parts.append("Components adequately utilize available content.")
        else:
            reasoning_parts.append("Some components may require additional content data.")
        
        if industry_fit_score >= 80:
            reasoning_parts.append("Components are highly appropriate for the target industry.")
        elif industry_fit_score >= 60:
            reasoning_parts.append("Components are suitable for the industry with good alignment.")
        else:
            reasoning_parts.append("Components may benefit from industry-specific customization.")
        
        if visual_hierarchy_score >= 80:
            reasoning_parts.append("Visual hierarchy is well-balanced and engaging.")
        elif visual_hierarchy_score >= 60:
            reasoning_parts.append("Visual hierarchy provides adequate emphasis and flow.")
        else:
            reasoning_parts.append("Visual hierarchy could be optimized for better user engagement.")
        
        return " ".join(reasoning_parts)
    
    def _validate_layout_flow(self, components: List[ComponentVariant]) -> bool:
        """Validate logical component flow"""
        component_types = [ComponentType(c.name.split('_')[0]) for c in components]
        recommended_order = self.layout_rules['recommended_order']
        
        # Check if components follow a logical order
        last_index = -1
        for comp_type in component_types:
            try:
                current_index = recommended_order.index(comp_type)
                if current_index < last_index:
                    return False
                last_index = current_index
            except ValueError:
                # Component type not in recommended order, allow it
                continue
        
        return True


def mix_template_components(
    content_analysis: Dict[str, Any],
    brand_identity: Dict[str, Any],
    requirements: Optional[Dict[str, Any]] = None
) -> ComponentCombination:
    """Convenience function for component mixing"""
    mixer = ComponentMixer()
    return mixer.mix_components(content_analysis, brand_identity, requirements)