"""
Typography System - Creates intelligent font matching and typography hierarchy
Preserves original website's text styles while making them modern and readable
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TypographyScale:
    """Typography scale with semantic naming"""
    display: str = "4rem"      # 64px - For hero titles
    h1: str = "3rem"           # 48px - Main headings
    h2: str = "2.25rem"        # 36px - Section headings
    h3: str = "1.875rem"       # 30px - Subsection headings
    h4: str = "1.5rem"         # 24px - Card titles
    h5: str = "1.25rem"        # 20px - Small headings
    h6: str = "1.125rem"       # 18px - Micro headings
    xl: str = "1.25rem"        # 20px - Large text
    lg: str = "1.125rem"       # 18px - Large body
    base: str = "1rem"         # 16px - Body text
    sm: str = "0.875rem"       # 14px - Small text
    xs: str = "0.75rem"        # 12px - Captions
    
@dataclass
class FontWeights:
    """Font weight scale"""
    thin: str = "100"
    extralight: str = "200"
    light: str = "300"
    normal: str = "400"
    medium: str = "500"
    semibold: str = "600"
    bold: str = "700"
    extrabold: str = "800"
    black: str = "900"

@dataclass
class LineHeights:
    """Line height scale for readability"""
    none: str = "1"
    tight: str = "1.25"
    snug: str = "1.375"
    normal: str = "1.5"
    relaxed: str = "1.625"
    loose: str = "1.75"

@dataclass
class LetterSpacing:
    """Letter spacing for different contexts"""
    tighter: str = "-0.05em"
    tight: str = "-0.025em"
    normal: str = "0em"
    wide: str = "0.025em"
    wider: str = "0.05em"
    widest: str = "0.1em"

class TypographySystem:
    """Creates intelligent typography system from brand identity"""
    
    def __init__(self, brand_identity: Dict[str, Any]):
        self.brand_identity = brand_identity
        self.typography_config = brand_identity.get('typography', {})
        self.brand_config = brand_identity.get('brand', {})
        
        # Create typography scales
        self.scale = TypographyScale()
        self.weights = FontWeights()
        self.line_heights = LineHeights()
        self.letter_spacing = LetterSpacing()
        
        # Determine font strategy
        self.primary_font = self._get_optimized_font('primary')
        self.heading_font = self._get_optimized_font('heading')
        self.mono_font = self._get_mono_font()
        
    def _get_optimized_font(self, context: str) -> str:
        """Get optimized font stack for given context"""
        
        original_font = self.typography_config.get(f'{context}_font', '')
        
        # Extract main font family name
        font_family = self._extract_main_font(original_font)
        
        # Check if it's a web-safe font we can enhance
        enhanced_font = self._enhance_font_stack(font_family, context)
        
        logger.info(f"Typography: {context} font '{font_family}' -> '{enhanced_font}'")
        
        return enhanced_font
    
    def _extract_main_font(self, font_string: str) -> str:
        """Extract the main font family from a font string"""
        if not font_string:
            return 'Inter'
        
        # Remove quotes and split by comma
        fonts = font_string.replace('"', '').replace("'", '').split(',')
        
        # Get first font and clean it
        main_font = fonts[0].strip()
        
        # Remove fallback terms
        fallback_terms = ['system-ui', 'sans-serif', 'serif', 'monospace', 'ui-serif', 'ui-sans-serif']
        if main_font.lower() in [term.lower() for term in fallback_terms]:
            return 'Inter'  # Default to Inter if only fallbacks
        
        return main_font
    
    def _enhance_font_stack(self, font_family: str, context: str) -> str:
        """Create enhanced font stack with proper fallbacks"""
        
        # Map common fonts to enhanced versions
        font_enhancements = {
            'roboto': 'Roboto, ui-sans-serif, system-ui, sans-serif',
            'open sans': 'Open Sans, ui-sans-serif, system-ui, sans-serif',
            'lato': 'Lato, ui-sans-serif, system-ui, sans-serif',
            'montserrat': 'Montserrat, ui-sans-serif, system-ui, sans-serif',
            'poppins': 'Poppins, ui-sans-serif, system-ui, sans-serif',
            'inter': 'Inter, ui-sans-serif, system-ui, sans-serif',
            'nunito': 'Nunito, ui-sans-serif, system-ui, sans-serif',
            'source sans pro': 'Source Sans Pro, ui-sans-serif, system-ui, sans-serif',
            'raleway': 'Raleway, ui-sans-serif, system-ui, sans-serif',
            'oswald': 'Oswald, ui-sans-serif, system-ui, sans-serif',
            
            # Serif fonts
            'playfair display': 'Playfair Display, ui-serif, Georgia, serif',
            'merriweather': 'Merriweather, ui-serif, Georgia, serif',
            'lora': 'Lora, ui-serif, Georgia, serif',
            'crimson text': 'Crimson Text, ui-serif, Georgia, serif',
            
            # Mono fonts
            'fira code': 'Fira Code, ui-monospace, Consolas, monospace',
            'source code pro': 'Source Code Pro, ui-monospace, Consolas, monospace',
        }
        
        font_key = font_family.lower()
        
        # Check for exact matches
        if font_key in font_enhancements:
            return font_enhancements[font_key]
        
        # Check for partial matches
        for key, enhanced in font_enhancements.items():
            if key in font_key or font_key in key:
                return enhanced
        
        # Determine font type and create appropriate stack
        if self._is_serif_font(font_family):
            return f"{font_family}, ui-serif, Georgia, serif"
        elif self._is_mono_font(font_family):
            return f"{font_family}, ui-monospace, Consolas, monospace"
        else:
            # Sans-serif (default)
            return f"{font_family}, ui-sans-serif, system-ui, sans-serif"
    
    def _is_serif_font(self, font_family: str) -> bool:
        """Check if font is serif"""
        serif_indicators = ['serif', 'times', 'georgia', 'garamond', 'baskerville', 
                           'playfair', 'merriweather', 'lora', 'crimson']
        return any(indicator in font_family.lower() for indicator in serif_indicators)
    
    def _is_mono_font(self, font_family: str) -> bool:
        """Check if font is monospace"""
        mono_indicators = ['mono', 'code', 'courier', 'console', 'hack', 'fira']
        return any(indicator in font_family.lower() for indicator in mono_indicators)
    
    def _get_mono_font(self) -> str:
        """Get monospace font for code/technical content"""
        return "ui-monospace, 'Fira Code', 'Source Code Pro', Consolas, 'Courier New', monospace"
    
    def get_font_imports(self) -> List[str]:
        """Generate Google Fonts imports for enhanced fonts"""
        imports = []
        
        fonts_to_import = []
        
        # Extract font names that need imports
        for font_stack in [self.primary_font, self.heading_font]:
            font_name = font_stack.split(',')[0].strip()
            
            # Check if it's a Google Font
            if self._is_google_font(font_name):
                fonts_to_import.append(font_name)
        
        # Generate imports
        for font in set(fonts_to_import):
            font_url = self._get_google_font_url(font)
            if font_url:
                imports.append(font_url)
        
        return imports
    
    def _is_google_font(self, font_name: str) -> bool:
        """Check if font is available on Google Fonts"""
        google_fonts = [
            'inter', 'roboto', 'open sans', 'lato', 'montserrat', 'poppins',
            'nunito', 'source sans pro', 'raleway', 'oswald', 'playfair display',
            'merriweather', 'lora', 'crimson text', 'fira code', 'source code pro'
        ]
        return font_name.lower() in google_fonts
    
    def _get_google_font_url(self, font_name: str) -> str:
        """Generate Google Fonts URL with proper weights"""
        
        # Map fonts to their common weights
        font_weights = {
            'inter': '300,400,500,600,700',
            'roboto': '300,400,500,700',
            'open sans': '300,400,600,700',
            'lato': '300,400,700',
            'montserrat': '300,400,500,600,700',
            'poppins': '300,400,500,600,700',
            'nunito': '300,400,600,700',
            'source sans pro': '300,400,600,700',
            'raleway': '300,400,500,600,700',
            'oswald': '300,400,500,600,700',
            'playfair display': '400,500,600,700',
            'merriweather': '300,400,700',
            'lora': '400,500,600,700',
            'crimson text': '400,600',
            'fira code': '300,400,500,600,700',
            'source code pro': '300,400,500,600,700',
        }
        
        font_key = font_name.lower()
        weights = font_weights.get(font_key, '300,400,500,600,700')
        
        # URL encode font name
        url_font_name = font_name.replace(' ', '+')
        
        return f"https://fonts.googleapis.com/css2?family={url_font_name}:wght@{weights}&display=swap"
    
    def get_typography_css(self) -> str:
        """Generate CSS custom properties for typography system"""
        
        css = f"""
/* Typography System - Generated from Brand Identity */
:root {{
  /* Font Families */
  --font-primary: {self.primary_font};
  --font-heading: {self.heading_font};
  --font-mono: {self.mono_font};
  
  /* Font Sizes */
  --text-display: {self.scale.display};
  --text-h1: {self.scale.h1};
  --text-h2: {self.scale.h2};
  --text-h3: {self.scale.h3};
  --text-h4: {self.scale.h4};
  --text-h5: {self.scale.h5};
  --text-h6: {self.scale.h6};
  --text-xl: {self.scale.xl};
  --text-lg: {self.scale.lg};
  --text-base: {self.scale.base};
  --text-sm: {self.scale.sm};
  --text-xs: {self.scale.xs};
  
  /* Font Weights */
  --font-thin: {self.weights.thin};
  --font-extralight: {self.weights.extralight};
  --font-light: {self.weights.light};
  --font-normal: {self.weights.normal};
  --font-medium: {self.weights.medium};
  --font-semibold: {self.weights.semibold};
  --font-bold: {self.weights.bold};
  --font-extrabold: {self.weights.extrabold};
  --font-black: {self.weights.black};
  
  /* Line Heights */
  --leading-none: {self.line_heights.none};
  --leading-tight: {self.line_heights.tight};
  --leading-snug: {self.line_heights.snug};
  --leading-normal: {self.line_heights.normal};
  --leading-relaxed: {self.line_heights.relaxed};
  --leading-loose: {self.line_heights.loose};
  
  /* Letter Spacing */
  --tracking-tighter: {self.letter_spacing.tighter};
  --tracking-tight: {self.letter_spacing.tight};
  --tracking-normal: {self.letter_spacing.normal};
  --tracking-wide: {self.letter_spacing.wide};
  --tracking-wider: {self.letter_spacing.wider};
  --tracking-widest: {self.letter_spacing.widest};
}}

/* Base Typography Styles */
html {{
  font-family: var(--font-primary);
  font-size: 16px;
  line-height: var(--leading-normal);
}}

/* Heading Styles */
h1, h2, h3, h4, h5, h6 {{
  font-family: var(--font-heading);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  margin: 0;
}}

h1 {{ font-size: var(--text-h1); }}
h2 {{ font-size: var(--text-h2); }}
h3 {{ font-size: var(--text-h3); }}
h4 {{ font-size: var(--text-h4); }}
h5 {{ font-size: var(--text-h5); }}
h6 {{ font-size: var(--text-h6); }}

/* Display Text */
.text-display {{
  font-family: var(--font-heading);
  font-size: var(--text-display);
  font-weight: var(--font-bold);
  line-height: var(--leading-none);
  letter-spacing: var(--tracking-tight);
}}

/* Body Text */
p, .text-base {{
  font-family: var(--font-primary);
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: var(--leading-relaxed);
  margin: 0;
}}

/* Utility Classes */
.text-xl {{ font-size: var(--text-xl); }}
.text-lg {{ font-size: var(--text-lg); }}
.text-sm {{ font-size: var(--text-sm); }}
.text-xs {{ font-size: var(--text-xs); }}

.font-light {{ font-weight: var(--font-light); }}
.font-normal {{ font-weight: var(--font-normal); }}
.font-medium {{ font-weight: var(--font-medium); }}
.font-semibold {{ font-weight: var(--font-semibold); }}
.font-bold {{ font-weight: var(--font-bold); }}

.leading-tight {{ line-height: var(--leading-tight); }}
.leading-normal {{ line-height: var(--leading-normal); }}
.leading-relaxed {{ line-height: var(--leading-relaxed); }}

.tracking-tight {{ letter-spacing: var(--tracking-tight); }}
.tracking-normal {{ letter-spacing: var(--tracking-normal); }}
.tracking-wide {{ letter-spacing: var(--tracking-wide); }}
"""
        
        return css.strip()
    
    def get_semantic_text_styles(self) -> Dict[str, Dict[str, str]]:
        """Get semantic text styles for different content types"""
        
        industry = self.brand_config.get('industry', 'business')
        tone = self.brand_config.get('tone', 'professional')
        
        # Base styles
        styles = {
            'hero_title': {
                'font-family': f'var(--font-heading), {self.heading_font}',
                'font-size': 'var(--text-display)',
                'font-weight': 'var(--font-bold)',
                'line-height': 'var(--leading-none)',
                'letter-spacing': 'var(--tracking-tight)',
            },
            'hero_subtitle': {
                'font-family': f'var(--font-primary), {self.primary_font}',
                'font-size': 'var(--text-xl)',
                'font-weight': 'var(--font-normal)',
                'line-height': 'var(--leading-relaxed)',
                'letter-spacing': 'var(--tracking-normal)',
            },
            'section_title': {
                'font-family': f'var(--font-heading), {self.heading_font}',
                'font-size': 'var(--text-h2)',
                'font-weight': 'var(--font-semibold)',
                'line-height': 'var(--leading-tight)',
                'letter-spacing': 'var(--tracking-tight)',
            },
            'card_title': {
                'font-family': f'var(--font-heading), {self.heading_font}',
                'font-size': 'var(--text-h4)',
                'font-weight': 'var(--font-medium)',
                'line-height': 'var(--leading-snug)',
                'letter-spacing': 'var(--tracking-normal)',
            },
            'body_text': {
                'font-family': f'var(--font-primary), {self.primary_font}',
                'font-size': 'var(--text-base)',
                'font-weight': 'var(--font-normal)',
                'line-height': 'var(--leading-relaxed)',
                'letter-spacing': 'var(--tracking-normal)',
            },
            'small_text': {
                'font-family': f'var(--font-primary), {self.primary_font}',
                'font-size': 'var(--text-sm)',
                'font-weight': 'var(--font-normal)',
                'line-height': 'var(--leading-normal)',
                'letter-spacing': 'var(--tracking-normal)',
            },
            'button_text': {
                'font-family': f'var(--font-primary), {self.primary_font}',
                'font-size': 'var(--text-base)',
                'font-weight': 'var(--font-medium)',
                'line-height': 'var(--leading-none)',
                'letter-spacing': 'var(--tracking-wide)',
            },
        }
        
        # Adjust for industry
        if industry == 'luxury':
            styles['hero_title']['letter-spacing'] = 'var(--tracking-widest)'
            styles['section_title']['letter-spacing'] = 'var(--tracking-wide)'
        elif industry == 'tech':
            styles['hero_title']['letter-spacing'] = 'var(--tracking-tighter)'
            styles['body_text']['font-weight'] = 'var(--font-light)'
        
        # Adjust for tone
        if tone == 'playful':
            styles['hero_title']['font-weight'] = 'var(--font-black)'
            styles['button_text']['font-weight'] = 'var(--font-semibold)'
        elif tone == 'professional':
            styles['hero_title']['font-weight'] = 'var(--font-bold)'
            styles['section_title']['font-weight'] = 'var(--font-semibold)'
        
        return styles
    
    def apply_responsive_scaling(self) -> str:
        """Generate responsive typography scaling CSS"""
        
        responsive_css = """
/* Responsive Typography Scaling */
@media (max-width: 768px) {
  :root {
    --text-display: 2.5rem;    /* 40px */
    --text-h1: 2rem;          /* 32px */
    --text-h2: 1.75rem;       /* 28px */
    --text-h3: 1.5rem;        /* 24px */
    --text-h4: 1.25rem;       /* 20px */
    --text-xl: 1.125rem;      /* 18px */
    --text-lg: 1rem;          /* 16px */
  }
}

@media (max-width: 480px) {
  :root {
    --text-display: 2rem;     /* 32px */
    --text-h1: 1.75rem;       /* 28px */
    --text-h2: 1.5rem;        /* 24px */
    --text-h3: 1.25rem;       /* 20px */
    --text-h4: 1.125rem;      /* 18px */
  }
}

@media (min-width: 1200px) {
  :root {
    --text-display: 5rem;     /* 80px */
    --text-h1: 3.5rem;        /* 56px */
    --text-h2: 2.5rem;        /* 40px */
  }
}
"""
        return responsive_css.strip()

def create_typography_system(brand_identity: Dict[str, Any]) -> TypographySystem:
    """Create typography system from brand identity"""
    return TypographySystem(brand_identity)