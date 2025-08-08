"""
CSS-in-JS System - Dynamic CSS generation based on brand identity
Generates CSS variables, utility classes, and component styles dynamically
"""

from typing import Dict, List, Any, Optional
import colorsys
import re
import json
from dataclasses import dataclass
from .responsive_system import generate_responsive_css


@dataclass
class ColorPalette:
    """Generated color palette with variations and utilities"""
    primary: str
    primary_light: str
    primary_dark: str
    secondary: str
    secondary_light: str
    secondary_dark: str
    accent: str
    accent_light: str
    accent_dark: str
    text_primary: str
    text_secondary: str
    background: str
    surface: str
    border: str
    hover: str
    focus: str
    success: str
    warning: str
    error: str
    info: str


@dataclass
class TypographyScale:
    """Typography scale with responsive sizing"""
    font_imports: str
    primary_font: str
    heading_font: str
    mono_font: str
    base_size: str
    scale_ratio: float
    line_heights: Dict[str, str]
    font_weights: Dict[str, str]
    letter_spacing: Dict[str, str]


class CSSGenerator:
    """Dynamic CSS generation system"""
    
    def __init__(self):
        self.industry_defaults = self._get_industry_defaults()
        self.css_cache = {}
        
    def generate_brand_css(self, brand_identity: Dict[str, Any], typography: Any) -> str:
        """Generate complete CSS system from brand identity"""
        
        # Create cache key
        cache_key = self._create_cache_key(brand_identity, typography)
        if cache_key in self.css_cache:
            return self.css_cache[cache_key]
        
        # Generate color palette
        color_palette = self._generate_color_palette(brand_identity)
        
        # Generate typography scale
        typography_scale = self._generate_typography_scale(brand_identity, typography)
        
        # Generate complete CSS
        css_output = self._build_complete_css(brand_identity, color_palette, typography_scale)
        
        # Cache result
        self.css_cache[cache_key] = css_output
        
        return css_output
    
    def _create_cache_key(self, brand_identity: Dict[str, Any], typography: Any) -> str:
        """Create cache key from brand identity"""
        key_data = {
            'colors': brand_identity.get('colors', {}),
            'industry': brand_identity.get('brand', {}).get('industry', 'business'),
            'tone': brand_identity.get('brand', {}).get('tone', 'professional'),
            'primary_font': getattr(typography, 'primary_font', ''),
            'heading_font': getattr(typography, 'heading_font', '')
        }
        return str(hash(json.dumps(key_data, sort_keys=True)))
    
    def _generate_color_palette(self, brand_identity: Dict[str, Any]) -> ColorPalette:
        """Generate complete color palette from brand colors"""
        
        colors = brand_identity.get('colors', {})
        industry = brand_identity.get('brand', {}).get('industry', 'business')
        
        # Base colors with fallbacks
        primary = colors.get('primary') or self.industry_defaults[industry]['primary']
        secondary = colors.get('secondary') or self.industry_defaults[industry]['secondary']
        accent = colors.get('accent') or self.industry_defaults[industry]['accent']
        text_primary = colors.get('text_primary') or '#111827'
        background = colors.get('background') or '#FFFFFF'
        
        return ColorPalette(
            # Base colors
            primary=primary,
            secondary=secondary,
            accent=accent,
            text_primary=text_primary,
            background=background,
            
            # Generated variations
            primary_light=self._lighten_color(primary, 0.2),
            primary_dark=self._darken_color(primary, 0.2),
            secondary_light=self._lighten_color(secondary, 0.2),
            secondary_dark=self._darken_color(secondary, 0.2),
            accent_light=self._lighten_color(accent, 0.2),
            accent_dark=self._darken_color(accent, 0.2),
            
            # Semantic colors
            text_secondary=self._mix_colors(text_primary, background, 0.6),
            surface=self._mix_colors(background, primary, 0.02),
            border=self._mix_colors(primary, background, 0.15),
            hover=self._mix_colors(primary, background, 0.1),
            focus=self._adjust_opacity(accent, 0.2),
            
            # Status colors
            success='#10B981',
            warning='#F59E0B',
            error='#EF4444',
            info='#3B82F6'
        )
    
    def _generate_typography_scale(self, brand_identity: Dict[str, Any], typography: Any) -> TypographyScale:
        """Generate typography scale and font system"""
        
        industry = brand_identity.get('brand', {}).get('industry', 'business')
        tone = brand_identity.get('brand', {}).get('tone', 'professional')
        
        # Get fonts with fallbacks
        primary_font = getattr(typography, 'primary_font', None) or self.industry_defaults[industry]['primary_font']
        heading_font = getattr(typography, 'heading_font', None) or self.industry_defaults[industry]['heading_font']
        
        # Generate font imports
        font_imports = self._generate_font_imports(primary_font, heading_font)
        
        # Scale ratio based on industry and tone
        scale_ratios = {
            ('tech', 'modern'): 1.25,
            ('restaurant', 'elegant'): 1.333,
            ('medical', 'professional'): 1.2,
            ('plumbing', 'professional'): 1.2,
            ('business', 'professional'): 1.25
        }
        scale_ratio = scale_ratios.get((industry, tone), 1.25)
        
        return TypographyScale(
            font_imports=font_imports,
            primary_font=f"{primary_font}, system-ui, sans-serif",
            heading_font=f"{heading_font}, system-ui, sans-serif",
            mono_font="'SF Mono', 'Monaco', 'Inconsolata', monospace",
            base_size='1rem',
            scale_ratio=scale_ratio,
            line_heights={
                'tight': '1.1',
                'snug': '1.25',
                'normal': '1.5',
                'relaxed': '1.625',
                'loose': '2.0'
            },
            font_weights={
                'light': '300',
                'normal': '400',
                'medium': '500',
                'semibold': '600',
                'bold': '700',
                'extrabold': '800'
            },
            letter_spacing={
                'tighter': '-0.05em',
                'tight': '-0.025em',
                'normal': '0em',
                'wide': '0.025em',
                'wider': '0.05em',
                'widest': '0.1em'
            }
        )
    
    def _build_complete_css(self, brand_identity: Dict[str, Any], colors: ColorPalette, typography: TypographyScale) -> str:
        """Build complete CSS with all systems"""
        
        industry = brand_identity.get('brand', {}).get('industry', 'business')
        tone = brand_identity.get('brand', {}).get('tone', 'professional')
        
        css_parts = [
            self._build_font_imports(typography),
            self._build_css_variables(colors, typography),
            self._build_base_styles(colors, typography),
            self._build_typography_utilities(typography),
            self._build_color_utilities(colors),
            self._build_component_styles(colors, typography, industry),
            self._build_animation_utilities(),
            self._build_responsive_utilities(),
            generate_responsive_css(brand_identity),  # Advanced responsive system
            self._build_industry_specific_css(industry, tone, colors),
        ]
        
        return '\n\n'.join(filter(None, css_parts))
    
    def _build_font_imports(self, typography: TypographyScale) -> str:
        """Build Google Fonts imports"""
        return f"/* Font Imports */\n{typography.font_imports}"
    
    def _build_css_variables(self, colors: ColorPalette, typography: TypographyScale) -> str:
        """Build CSS custom properties"""
        return f"""/* Brand CSS Variables */
:root {{
  /* Colors */
  --brand-primary: {colors.primary};
  --brand-primary-light: {colors.primary_light};
  --brand-primary-dark: {colors.primary_dark};
  --brand-secondary: {colors.secondary};
  --brand-secondary-light: {colors.secondary_light};
  --brand-secondary-dark: {colors.secondary_dark};
  --brand-accent: {colors.accent};
  --brand-accent-light: {colors.accent_light};
  --brand-accent-dark: {colors.accent_dark};
  --brand-text-primary: {colors.text_primary};
  --brand-text-secondary: {colors.text_secondary};
  --brand-background: {colors.background};
  --brand-surface: {colors.surface};
  --brand-border: {colors.border};
  --brand-hover: {colors.hover};
  --brand-focus: {colors.focus};
  --brand-success: {colors.success};
  --brand-warning: {colors.warning};
  --brand-error: {colors.error};
  --brand-info: {colors.info};
  
  /* Typography */
  --font-primary: {typography.primary_font};
  --font-heading: {typography.heading_font};
  --font-mono: {typography.mono_font};
  --font-size-base: {typography.base_size};
  --font-scale-ratio: {typography.scale_ratio};
  
  /* Line Heights */
  --line-height-tight: {typography.line_heights['tight']};
  --line-height-snug: {typography.line_heights['snug']};
  --line-height-normal: {typography.line_heights['normal']};
  --line-height-relaxed: {typography.line_heights['relaxed']};
  --line-height-loose: {typography.line_heights['loose']};
  
  /* Font Weights */
  --font-weight-light: {typography.font_weights['light']};
  --font-weight-normal: {typography.font_weights['normal']};
  --font-weight-medium: {typography.font_weights['medium']};
  --font-weight-semibold: {typography.font_weights['semibold']};
  --font-weight-bold: {typography.font_weights['bold']};
  --font-weight-extrabold: {typography.font_weights['extrabold']};
  
  /* Spacing Scale */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;
  --space-3xl: 4rem;
  --space-4xl: 6rem;
  
  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-3xl: 2rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}}"""
    
    def _build_base_styles(self, colors: ColorPalette, typography: TypographyScale) -> str:
        """Build base HTML styles"""
        return f"""/* Base Styles */
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

html {{
  font-size: 16px;
  scroll-behavior: smooth;
}}

body {{
  font-family: var(--font-primary);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--brand-text-primary);
  background-color: var(--brand-background);
  font-weight: var(--font-weight-normal);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
  font-family: var(--font-heading);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  letter-spacing: -0.025em;
  color: var(--brand-text-primary);
}}

h1 {{ font-size: calc(var(--font-size-base) * pow(var(--font-scale-ratio), 4)); }}
h2 {{ font-size: calc(var(--font-size-base) * pow(var(--font-scale-ratio), 3)); }}
h3 {{ font-size: calc(var(--font-size-base) * pow(var(--font-scale-ratio), 2)); }}
h4 {{ font-size: calc(var(--font-size-base) * var(--font-scale-ratio)); }}
h5 {{ font-size: var(--font-size-base); }}
h6 {{ font-size: calc(var(--font-size-base) / var(--font-scale-ratio)); }}

/* Links */
a {{
  color: var(--brand-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}}

a:hover {{
  color: var(--brand-primary-dark);
}}

/* Selection */
::selection {{
  background-color: var(--brand-accent);
  color: white;
}}

/* Focus styles */
:focus-visible {{
  outline: 2px solid var(--brand-accent);
  outline-offset: 2px;
}}"""
    
    def _build_typography_utilities(self, typography: TypographyScale) -> str:
        """Build typography utility classes"""
        return """/* Typography Utilities */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
.text-4xl { font-size: 2.25rem; line-height: 2.5rem; }
.text-5xl { font-size: 3rem; line-height: 1; }
.text-6xl { font-size: 3.75rem; line-height: 1; }

.font-primary { font-family: var(--font-primary); }
.font-heading { font-family: var(--font-heading); }
.font-mono { font-family: var(--font-mono); }

.font-light { font-weight: var(--font-weight-light); }
.font-normal { font-weight: var(--font-weight-normal); }
.font-medium { font-weight: var(--font-weight-medium); }
.font-semibold { font-weight: var(--font-weight-semibold); }
.font-bold { font-weight: var(--font-weight-bold); }
.font-extrabold { font-weight: var(--font-weight-extrabold); }

.leading-tight { line-height: var(--line-height-tight); }
.leading-snug { line-height: var(--line-height-snug); }
.leading-normal { line-height: var(--line-height-normal); }
.leading-relaxed { line-height: var(--line-height-relaxed); }
.leading-loose { line-height: var(--line-height-loose); }

.tracking-tighter { letter-spacing: -0.05em; }
.tracking-tight { letter-spacing: -0.025em; }
.tracking-normal { letter-spacing: 0; }
.tracking-wide { letter-spacing: 0.025em; }
.tracking-wider { letter-spacing: 0.05em; }
.tracking-widest { letter-spacing: 0.1em; }"""
    
    def _build_color_utilities(self, colors: ColorPalette) -> str:
        """Build color utility classes"""
        return f"""/* Color Utilities */
.text-primary {{ color: var(--brand-text-primary); }}
.text-secondary {{ color: var(--brand-text-secondary); }}
.text-brand-primary {{ color: var(--brand-primary); }}
.text-brand-secondary {{ color: var(--brand-secondary); }}
.text-brand-accent {{ color: var(--brand-accent); }}
.text-white {{ color: #ffffff; }}
.text-black {{ color: #000000; }}

.bg-primary {{ background-color: var(--brand-primary); }}
.bg-secondary {{ background-color: var(--brand-secondary); }}
.bg-accent {{ background-color: var(--brand-accent); }}
.bg-surface {{ background-color: var(--brand-surface); }}
.bg-background {{ background-color: var(--brand-background); }}
.bg-white {{ background-color: #ffffff; }}
.bg-black {{ background-color: #000000; }}

.border-primary {{ border-color: var(--brand-primary); }}
.border-secondary {{ border-color: var(--brand-secondary); }}
.border-accent {{ border-color: var(--brand-accent); }}
.border-default {{ border-color: var(--brand-border); }}

/* Gradient Utilities */
.bg-gradient-primary {{
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark));
}}

.bg-gradient-accent {{
  background: linear-gradient(135deg, var(--brand-accent), var(--brand-accent-dark));
}}

.bg-gradient-hero {{
  background: linear-gradient(135deg, 
    color-mix(in srgb, var(--brand-primary) 90%, #000000 10%), 
    color-mix(in srgb, var(--brand-primary) 70%, var(--brand-secondary) 30%)
  );
}}"""
    
    def _build_component_styles(self, colors: ColorPalette, typography: TypographyScale, industry: str) -> str:
        """Build reusable component styles"""
        return f"""/* Component Styles */

/* Buttons */
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-family: var(--font-primary);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  outline: none;
}}

.btn:focus-visible {{
  box-shadow: 0 0 0 3px var(--brand-focus);
}}

.btn-primary {{
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark));
  color: white;
  box-shadow: var(--shadow-md);
}}

.btn-primary:hover {{
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}}

.btn-secondary {{
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}}

.btn-secondary:hover {{
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}}

.btn-accent {{
  background: linear-gradient(135deg, var(--brand-accent), var(--brand-accent-dark));
  color: white;
  box-shadow: 0 10px 25px color-mix(in srgb, var(--brand-accent) 30%, transparent 70%);
}}

.btn-accent:hover {{
  transform: translateY(-2px);
  box-shadow: 0 15px 35px color-mix(in srgb, var(--brand-accent) 40%, transparent 60%);
}}

/* Cards */
.card {{
  background: var(--brand-surface);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}}

.card:hover {{
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: color-mix(in srgb, var(--brand-primary) 30%, transparent 70%);
}}

.card-glass {{
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-2xl);
  padding: var(--space-xl);
}}

.card-glass:hover {{
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 25px 50px color-mix(in srgb, var(--brand-primary) 20%, transparent 80%);
}}

/* Forms */
.form-input {{
  width: 100%;
  padding: 0.75rem 1rem;
  font-family: var(--font-primary);
  font-size: 1rem;
  background: var(--brand-surface);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-md);
  color: var(--brand-text-primary);
  transition: all var(--transition-fast);
}}

.form-input:focus {{
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px var(--brand-focus);
  outline: none;
}}

.form-input::placeholder {{
  color: var(--brand-text-secondary);
}}

/* Icons */
.icon {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}}

.icon-primary {{
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark));
  color: white;
}}

.icon-accent {{
  background: linear-gradient(135deg, var(--brand-accent), var(--brand-accent-dark));
  color: white;
}}

/* Badges */
.badge {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-full);
  border: 1px solid transparent;
}}

.badge-primary {{
  background: color-mix(in srgb, var(--brand-primary) 15%, transparent 85%);
  color: var(--brand-primary-dark);
  border-color: color-mix(in srgb, var(--brand-primary) 30%, transparent 70%);
}}

.badge-accent {{
  background: color-mix(in srgb, var(--brand-accent) 15%, transparent 85%);
  color: var(--brand-accent-dark);
  border-color: color-mix(in srgb, var(--brand-accent) 30%, transparent 70%);
}}"""
    
    def _build_animation_utilities(self) -> str:
        """Build animation and transition utilities"""
        return """/* Animation Utilities */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes bounce {
  0%, 20%, 53%, 80%, 100% { transform: translateY(0); }
  40%, 43% { transform: translateY(-30px); }
  70% { transform: translateY(-15px); }
  90% { transform: translateY(-4px); }
}

.animate-fade-in { animation: fadeIn 0.5s ease-out; }
.animate-scale-in { animation: scaleIn 0.3s ease-out; }
.animate-slide-in-right { animation: slideInRight 0.4s ease-out; }
.animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
.animate-bounce { animation: bounce 1s infinite; }

.transition-fast { transition: all var(--transition-fast); }
.transition-normal { transition: all var(--transition-normal); }
.transition-slow { transition: all var(--transition-slow); }

.hover-lift:hover { transform: translateY(-4px); }
.hover-scale:hover { transform: scale(1.05); }
.hover-glow:hover { box-shadow: 0 0 20px color-mix(in srgb, var(--brand-accent) 50%, transparent 50%); }"""
    
    def _build_responsive_utilities(self) -> str:
        """Build responsive design utilities"""
        return """/* Responsive Utilities */
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 640px) {
  .container { max-width: 640px; padding: 0 1.5rem; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; }
}

@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}

@media (min-width: 1536px) {
  .container { max-width: 1536px; }
}

/* Mobile-first responsive text */
@media (max-width: 767px) {
  .text-responsive-sm { font-size: clamp(1.5rem, 4vw, 2rem); }
  .text-responsive-md { font-size: clamp(2rem, 6vw, 3rem); }
  .text-responsive-lg { font-size: clamp(2.5rem, 8vw, 4rem); }
}

/* Touch targets */
@media (hover: none) and (pointer: coarse) {
  .btn, .form-input, .card {
    min-height: 44px;
  }
}"""
    
    def _build_industry_specific_css(self, industry: str, tone: str, colors: ColorPalette) -> str:
        """Build industry-specific CSS customizations"""
        
        if industry == 'plumbing':
            return f"""/* Plumbing Industry Styles */
.emergency-banner {{
  background: linear-gradient(135deg, #DC2626, #B91C1C);
  color: white;
  padding: 1rem;
  border-radius: var(--radius-lg);
  border-left: 4px solid #FCA5A5;
}}

.service-badge-emergency {{
  background: linear-gradient(135deg, #DC2626, #B91C1C);
  color: white;
  animation: pulse 2s infinite;
}}

.water-wave {{
  position: relative;
  overflow: hidden;
}}

.water-wave::after {{
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 20%;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-light));
  opacity: 0.1;
  animation: wave 3s ease-in-out infinite;
}}

@keyframes wave {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-10px); }}
}}"""
        
        elif industry == 'restaurant':
            return f"""/* Restaurant Industry Styles */
.menu-item {{
  position: relative;
  padding: 1.5rem;
  border-radius: var(--radius-xl);
  background: var(--brand-surface);
  transition: all var(--transition-normal);
}}

.menu-item:hover {{
  background: color-mix(in srgb, var(--brand-accent) 5%, var(--brand-surface));
}}

.price-tag {{
  font-family: var(--font-heading);
  font-weight: var(--font-weight-bold);
  color: var(--brand-accent);
  font-size: 1.25rem;
}}

.reservation-highlight {{
  background: linear-gradient(135deg, var(--brand-accent), var(--brand-accent-light));
  color: white;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-full);
  font-weight: var(--font-weight-semibold);
  animation: gentle-glow 2s ease-in-out infinite alternate;
}}

@keyframes gentle-glow {{
  from {{ box-shadow: 0 0 10px color-mix(in srgb, var(--brand-accent) 30%, transparent 70%); }}
  to {{ box-shadow: 0 0 20px color-mix(in srgb, var(--brand-accent) 50%, transparent 50%); }}
}}"""
        
        elif industry == 'tech':
            return f"""/* Tech Industry Styles */
.code-block {{
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  font-family: var(--font-mono);
  font-size: 0.875rem;
  line-height: 1.6;
  overflow-x: auto;
}}

.terminal {{
  background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
  border: 1px solid #404040;
  border-radius: var(--radius-lg);
  padding: 1rem;
  position: relative;
}}

.terminal::before {{
  content: '●●●';
  position: absolute;
  top: 0.5rem;
  left: 1rem;
  color: #ff5f56;
  font-size: 1.2rem;
  letter-spacing: 0.2rem;
}}

.api-endpoint {{
  background: color-mix(in srgb, var(--brand-primary) 10%, transparent 90%);
  border: 1px solid color-mix(in srgb, var(--brand-primary) 30%, transparent 70%);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-family: var(--font-mono);
  font-size: 0.9rem;
}}

.loading-dots {{
  display: inline-flex;
  gap: 0.25rem;
}}

.loading-dots::after {{
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--brand-primary);
  animation: loading-dot 1.4s infinite ease-in-out both;
}}

@keyframes loading-dot {{
  0%, 80%, 100% {{ transform: scale(0); }}
  40% {{ transform: scale(1); }}
}}"""
        
        else:
            return f"""/* General Business Styles */
.professional-badge {{
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark));
  color: white;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  font-weight: var(--font-weight-medium);
}}

.trust-indicator {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: color-mix(in srgb, var(--brand-success) 10%, transparent 90%);
  border: 1px solid color-mix(in srgb, var(--brand-success) 30%, transparent 70%);
  border-radius: var(--radius-md);
  color: var(--brand-success);
  font-size: 0.875rem;
  font-weight: var(--font-weight-medium);
}}

.business-hours {{
  background: var(--brand-surface);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 1rem;
}}"""
    
    def _get_industry_defaults(self) -> Dict[str, Dict[str, str]]:
        """Get default colors and fonts for different industries"""
        return {
            'plumbing': {
                'primary': '#0EA5E9',
                'secondary': '#64748B',
                'accent': '#F59E0B',
                'primary_font': 'Inter',
                'heading_font': 'Inter'
            },
            'restaurant': {
                'primary': '#DC2626',
                'secondary': '#92400E',
                'accent': '#F59E0B',
                'primary_font': 'Playfair Display',
                'heading_font': 'Playfair Display'
            },
            'tech': {
                'primary': '#6366F1',
                'secondary': '#8B5CF6',
                'accent': '#06B6D4',
                'primary_font': 'Inter',
                'heading_font': 'Inter'
            },
            'medical': {
                'primary': '#10B981',
                'secondary': '#059669',
                'accent': '#3B82F6',
                'primary_font': 'Inter',
                'heading_font': 'Inter'
            },
            'business': {
                'primary': '#3B82F6',
                'secondary': '#64748B',
                'accent': '#F59E0B',
                'primary_font': 'Inter',
                'heading_font': 'Inter'
            }
        }
    
    def _generate_font_imports(self, primary_font: str, heading_font: str) -> str:
        """Generate Google Fonts import statements"""
        fonts = set([primary_font, heading_font])
        
        # Map font names to Google Fonts imports
        font_imports = {
            'Inter': '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap");',
            'Playfair Display': '@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&display=swap");',
            'Roboto': '@import url("https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap");',
            'Open Sans': '@import url("https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700;800&display=swap");',
            'Lato': '@import url("https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap");',
            'Montserrat': '@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap");',
            'Poppins': '@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap");'
        }
        
        imports = []
        for font in fonts:
            if font in font_imports:
                imports.append(font_imports[font])
        
        return '\n'.join(imports)
    
    # Color utility methods
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by a factor (0.0 to 1.0)"""
        rgb = self._hex_to_rgb(hex_color)
        lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return self._rgb_to_hex(lightened)
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darken a hex color by a factor (0.0 to 1.0)"""
        rgb = self._hex_to_rgb(hex_color)
        darkened = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return self._rgb_to_hex(darkened)
    
    def _mix_colors(self, color1: str, color2: str, ratio: float) -> str:
        """Mix two hex colors with a ratio (0.0 = all color2, 1.0 = all color1)"""
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)
        mixed = tuple(int(c1 * ratio + c2 * (1 - ratio)) for c1, c2 in zip(rgb1, rgb2))
        return self._rgb_to_hex(mixed)
    
    def _adjust_opacity(self, hex_color: str, opacity: float) -> str:
        """Convert hex color to rgba with opacity"""
        rgb = self._hex_to_rgb(hex_color)
        return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"


def generate_brand_css(brand_identity: Dict[str, Any], typography: Any) -> str:
    """Convenience function to generate brand CSS"""
    generator = CSSGenerator()
    return generator.generate_brand_css(brand_identity, typography)