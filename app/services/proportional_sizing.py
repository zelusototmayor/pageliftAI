"""
Content-aware proportional sizing system for website templates.
Calculates appropriate section heights and spacing based on actual content.
"""

from typing import Dict, Any, Tuple
import re


class ProportionalSizing:
    """Calculate content-aware sizing for website sections"""
    
    # Base sizing constants - OPTIMIZED for business sites to prevent excessive padding
    MINIMAL_PADDING = "py-4"     # ~100-150px total - Very compact (REDUCED from py-6)
    COMPACT_PADDING = "py-6"     # ~150-200px total - Standard compact (REDUCED from py-8)
    STANDARD_PADDING = "py-8"    # ~200-250px total - Moderate (REDUCED from py-10)
    EXPANDED_PADDING = "py-10"   # ~250-300px total - Rich content (REDUCED from py-12)
    
    # Content thresholds
    MINIMAL_WORDS = 50
    COMPACT_WORDS = 150  
    STANDARD_WORDS = 400
    EXPANDED_WORDS = 800
    
    @classmethod
    def calculate_section_size(cls, section_data: Dict[str, Any]) -> Dict[str, str]:
        """Calculate appropriate sizing classes for a section based on content"""
        
        # Extract content metrics
        text = str(section_data.get('original_text', '') or section_data.get('short_copy', ''))
        heading = str(section_data.get('heading', ''))
        images = section_data.get('img_urls', [])
        category = section_data.get('category', 'other')
        
        word_count = len(text.split()) if text else 0
        has_images = len(images) > 0
        has_substantial_heading = len(heading) > 5
        
        # Content complexity scoring
        complexity_score = cls._calculate_complexity(word_count, has_images, has_substantial_heading, category)
        
        # Determine size tier
        size_tier = cls._determine_size_tier(complexity_score, category, word_count)
        
        return {
            'section_padding': cls._get_section_padding(size_tier),
            'container_spacing': cls._get_container_spacing(size_tier),
            'content_spacing': cls._get_content_spacing(size_tier),
            'size_tier': size_tier,
            'height_class': cls._get_height_class(size_tier, category),
            'responsive_adjustments': cls._get_responsive_adjustments(size_tier)
        }
    
    @classmethod 
    def _calculate_complexity(cls, word_count: int, has_images: bool, has_heading: bool, category: str) -> int:
        """Calculate content complexity score"""
        score = 0
        
        # Word count contribution
        if word_count <= cls.MINIMAL_WORDS:
            score += 1
        elif word_count <= cls.COMPACT_WORDS:
            score += 2
        elif word_count <= cls.STANDARD_WORDS:
            score += 3
        else:
            score += 4
            
        # Visual content contribution
        if has_images:
            score += 2
        if has_heading:
            score += 1
            
        # Category-specific adjustments
        category_modifiers = {
            'hero': 2,      # Heroes should be more prominent
            'contact': -1,  # Contact sections should be compact
            'other': -1,    # Generic content should be minimal
            'about': 0,     # Standard sizing
            'services': 1,  # Slightly expanded for service details
            'gallery': 2    # Galleries need more space
        }
        
        score += category_modifiers.get(category, 0)
        return max(1, score)  # Minimum score of 1
    
    @classmethod
    def _determine_size_tier(cls, complexity_score: int, category: str, word_count: int) -> str:
        """Determine size tier based on complexity"""
        
        # Special handling for categories
        if category == 'contact' and word_count < cls.COMPACT_WORDS:
            return 'compact'
        elif category == 'hero' and complexity_score <= 3:
            return 'standard'  # Even heroes should not be oversized for business sites
        elif category == 'other' and word_count < cls.MINIMAL_WORDS:
            return 'minimal'
        
        # General complexity-based sizing
        if complexity_score <= 2:
            return 'minimal'
        elif complexity_score <= 4:
            return 'compact'  
        elif complexity_score <= 6:
            return 'standard'
        else:
            return 'expanded'
    
    @classmethod
    def _get_section_padding(cls, size_tier: str) -> str:
        """Get section padding classes - OPTIMIZED for business sites"""
        padding_map = {
            'minimal': cls.MINIMAL_PADDING,    # py-6  - Very compact
            'compact': cls.COMPACT_PADDING,    # py-8  - Standard compact
            'standard': cls.STANDARD_PADDING,  # py-10 - Moderate
            'expanded': cls.EXPANDED_PADDING,  # py-12 - Maximum for business sites
        }
        return padding_map.get(size_tier, cls.COMPACT_PADDING)
    
    @classmethod
    def _get_container_spacing(cls, size_tier: str) -> str:
        """Get container spacing classes"""
        spacing_map = {
            'minimal': 'space-y-4',
            'compact': 'space-y-6', 
            'standard': 'space-y-8',
            'expanded': 'space-y-12'
        }
        return spacing_map.get(size_tier, 'space-y-6')
    
    @classmethod
    def _get_content_spacing(cls, size_tier: str) -> str:
        """Get content element spacing"""
        spacing_map = {
            'minimal': 'mb-4',
            'compact': 'mb-6',
            'standard': 'mb-8', 
            'expanded': 'mb-10'
        }
        return spacing_map.get(size_tier, 'mb-6')
    
    @classmethod
    def _get_height_class(cls, size_tier: str, category: str) -> str:
        """Get height constraint class - OPTIMIZED for business sites to prevent oversized sections"""
        
        # HERO sections: Reasonable heights that don't dominate the page
        if category == 'hero':
            hero_heights = {
                'minimal': 'min-h-[300px]',   # Small hero
                'compact': 'min-h-[350px]',   # Standard hero  
                'standard': 'min-h-[400px]',  # Rich content hero
                'expanded': 'min-h-[450px]'   # Maximum hero - still reasonable
            }
            return hero_heights.get(size_tier, 'min-h-[350px]')
        
        # All other sections: Focus on content, not artificial height
        height_map = {
            'minimal': 'min-h-[150px]',    # Very compact
            'compact': 'min-h-[200px]',    # Standard compact  
            'standard': 'min-h-[250px]',   # Moderate height
            'expanded': 'min-h-[300px]'    # Still reasonable for content sections
        }
        return height_map.get(size_tier, 'min-h-[200px]')
    
    @classmethod
    def _get_responsive_adjustments(cls, size_tier: str) -> Dict[str, str]:
        """Get responsive sizing adjustments"""
        base_adjustments = {
            'mobile': 'px-4 py-4',
            'tablet': 'px-6 py-6', 
            'desktop': 'px-8'
        }
        
        # Adjust mobile padding based on size tier
        mobile_padding_map = {
            'minimal': 'px-4 py-3',
            'compact': 'px-4 py-4',
            'standard': 'px-4 py-6',
            'expanded': 'px-4 py-8'
        }
        
        base_adjustments['mobile'] = mobile_padding_map.get(size_tier, 'px-4 py-4')
        return base_adjustments
    
    @classmethod
    def get_template_sizing_context(cls, sections: list) -> Dict[str, Any]:
        """Generate sizing context for templates"""
        
        total_sections = len(sections)
        sizing_data = {}
        
        for section in sections:
            section_id = section.get('section_id', 0)
            sizing = cls.calculate_section_size(section)
            sizing_data[f'section_{section_id}'] = sizing
        
        # Global sizing preferences
        is_compact_site = total_sections > 5  # Sites with many sections should be more compact
        
        global_adjustments = {
            'is_compact_site': is_compact_site,
            'max_hero_count': 1,  # Only allow one hero section per site
            'prefer_compact_spacing': is_compact_site,
            'section_separator': 'border-t border-gray-100' if is_compact_site else ''
        }
        
        return {
            'section_sizing': sizing_data,
            'global_sizing': global_adjustments
        }


def apply_proportional_sizing_to_sections(sections: list) -> list:
    """Apply proportional sizing to section data"""
    
    sizing_context = ProportionalSizing.get_template_sizing_context(sections)
    
    # Update each section with sizing information
    for section in sections:
        section_id = section.get('section_id', 0)
        sizing_key = f'section_{section_id}'
        
        if sizing_key in sizing_context['section_sizing']:
            sizing_info = sizing_context['section_sizing'][sizing_key]
            
            # Add sizing properties to section
            section['sizing'] = sizing_info
            section['is_compact_site'] = sizing_context['global_sizing']['is_compact_site']
    
    # Limit hero sections to prevent multiple full-height sections
    hero_count = 0
    max_heroes = sizing_context['global_sizing']['max_hero_count']
    
    for section in sections:
        if section.get('category') == 'hero':
            hero_count += 1
            if hero_count > max_heroes:
                # Convert excess heroes to 'about' or 'other'
                if len(section.get('original_text', '').split()) > 100:
                    section['category'] = 'about'
                else:
                    section['category'] = 'other'
                section['reasoning'] = f"Converted from hero to prevent multiple oversized sections"
    
    return sections