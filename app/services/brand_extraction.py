"""
Brand Extraction Service - Analyzes original websites to extract visual identity
Extracts colors, fonts, spacing, layout patterns, and visual style for modern recreation
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ColorPalette:
    """Extracted color scheme from original website"""
    primary: str = "#3B82F6"  # Default blue
    secondary: str = "#64748B"  # Default gray
    accent: str = "#F59E0B"  # Default amber
    background: str = "#FFFFFF"  # Default white
    text_primary: str = "#111827"  # Default dark
    text_secondary: str = "#6B7280"  # Default gray
    success: str = "#10B981"  # Default green
    error: str = "#EF4444"  # Default red
    
@dataclass
class Typography:
    """Extracted typography system from original website"""
    primary_font: str = "Inter, system-ui, sans-serif"
    secondary_font: str = "Inter, system-ui, sans-serif"
    heading_font: str = "Inter, system-ui, sans-serif"
    font_sizes: Dict[str, str] = None
    font_weights: Dict[str, str] = None
    line_heights: Dict[str, str] = None
    
    def __post_init__(self):
        if self.font_sizes is None:
            self.font_sizes = {
                'xs': '0.75rem',    # 12px
                'sm': '0.875rem',   # 14px
                'base': '1rem',     # 16px
                'lg': '1.125rem',   # 18px
                'xl': '1.25rem',    # 20px
                '2xl': '1.5rem',    # 24px
                '3xl': '1.875rem',  # 30px
                '4xl': '2.25rem',   # 36px
                '5xl': '3rem',      # 48px
                '6xl': '3.75rem',   # 60px
            }
        if self.font_weights is None:
            self.font_weights = {
                'light': '300',
                'normal': '400',
                'medium': '500',
                'semibold': '600',
                'bold': '700',
                'extrabold': '800',
            }
        if self.line_heights is None:
            self.line_heights = {
                'tight': '1.25',
                'snug': '1.375',
                'normal': '1.5',
                'relaxed': '1.625',
                'loose': '1.75',
            }

@dataclass 
class VisualStyle:
    """Extracted visual style patterns from original website"""
    border_radius: str = "0.5rem"  # Default rounded
    shadow_style: str = "0 4px 6px -1px rgb(0 0 0 / 0.1)"  # Default shadow
    spacing_scale: Dict[str, str] = None
    button_styles: Dict[str, Any] = None
    card_styles: Dict[str, Any] = None
    layout_patterns: List[str] = None
    
    def __post_init__(self):
        if self.spacing_scale is None:
            self.spacing_scale = {
                '1': '0.25rem',   # 4px
                '2': '0.5rem',    # 8px
                '3': '0.75rem',   # 12px
                '4': '1rem',      # 16px
                '6': '1.5rem',    # 24px
                '8': '2rem',      # 32px
                '12': '3rem',     # 48px
                '16': '4rem',     # 64px
                '20': '5rem',     # 80px
                '24': '6rem',     # 96px
            }
        if self.button_styles is None:
            self.button_styles = {
                'primary': {'padding': '0.75rem 1.5rem', 'rounded': '0.5rem'},
                'secondary': {'padding': '0.75rem 1.5rem', 'rounded': '0.5rem'},
            }
        if self.card_styles is None:
            self.card_styles = {
                'padding': '1.5rem',
                'rounded': '0.75rem',
                'shadow': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            }
        if self.layout_patterns is None:
            self.layout_patterns = ['grid', 'flex', 'stack']

@dataclass
class BrandIdentity:
    """Complete brand identity extracted from original website"""
    colors: ColorPalette
    typography: Typography
    style: VisualStyle
    industry: str = "business"
    tone: str = "professional"
    layout_preference: str = "modern"
    image_style: str = "photography"

class BrandExtractor:
    """Extracts comprehensive brand identity from original websites"""
    
    def __init__(self):
        self.css_rules = {}
        self.computed_styles = {}
        self.color_frequency = Counter()
        self.font_frequency = Counter()
        
    def extract_brand_identity(self, url: str, html: str) -> BrandIdentity:
        """Main method to extract complete brand identity"""
        try:
            logger.info(f"Starting brand extraction for: {url}")
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract CSS and styles
            css_content = self._extract_css_content(soup, url)
            inline_styles = self._extract_inline_styles(soup)
            
            # Analyze visual elements
            colors = self._extract_color_palette(css_content, inline_styles, soup)
            typography = self._extract_typography(css_content, inline_styles, soup)
            style = self._extract_visual_style(css_content, inline_styles, soup)
            
            # Determine industry and tone
            industry = self._detect_industry(soup)
            tone = self._detect_tone(soup)
            layout_preference = self._detect_layout_style(soup)
            image_style = self._detect_image_style(soup)
            
            brand_identity = BrandIdentity(
                colors=colors,
                typography=typography,
                style=style,
                industry=industry,
                tone=tone,
                layout_preference=layout_preference,
                image_style=image_style
            )
            
            logger.info(f"Brand extraction completed successfully")
            return brand_identity
            
        except Exception as e:
            logger.error(f"Brand extraction failed: {e}", exc_info=True)
            # Return default modern brand identity
            return self._get_default_brand_identity()
    
    def _extract_css_content(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract CSS content from external stylesheets and style tags"""
        css_content = ""
        
        # Extract from <style> tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_content += style_tag.string + "\n"
        
        # Extract from external stylesheets (limited to avoid heavy requests)
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and len(css_content) < 50000:  # Limit CSS size
                try:
                    css_url = urljoin(base_url, href)
                    # Skip CDN fonts and large frameworks for now
                    if any(cdn in css_url.lower() for cdn in ['fonts.googleapis.com', 'cdnjs.cloudflare.com']):
                        continue
                    
                    response = requests.get(css_url, timeout=5)
                    if response.status_code == 200:
                        css_content += response.text + "\n"
                except Exception as e:
                    logger.debug(f"Failed to fetch CSS from {href}: {e}")
                    continue
        
        return css_content
    
    def _extract_inline_styles(self, soup: BeautifulSoup) -> List[str]:
        """Extract inline styles from HTML elements"""
        inline_styles = []
        
        for element in soup.find_all(attrs={'style': True}):
            style = element.get('style', '')
            if style:
                inline_styles.append(style)
        
        return inline_styles
    
    def _extract_color_palette(self, css_content: str, inline_styles: List[str], soup: BeautifulSoup) -> ColorPalette:
        """Extract and analyze color palette from CSS and HTML"""
        colors = []
        
        # Extract colors from CSS
        color_patterns = [
            r'color:\s*([#\w\(\),\s\%\.]+)',
            r'background-color:\s*([#\w\(\),\s\%\.]+)',
            r'background:\s*([#\w\(\),\s\%\.]+)',
            r'border-color:\s*([#\w\(\),\s\%\.]+)',
            r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})',
            r'rgb\([^\)]+\)',
            r'rgba\([^\)]+\)',
            r'hsl\([^\)]+\)',
        ]
        
        all_styles = css_content + " ".join(inline_styles)
        
        for pattern in color_patterns:
            matches = re.findall(pattern, all_styles, re.IGNORECASE)
            colors.extend(matches)
        
        # Clean and categorize colors
        cleaned_colors = []
        for color in colors:
            color = color.strip().lower()
            if self._is_valid_color(color):
                cleaned_colors.append(color)
        
        # Analyze color usage frequency
        color_counter = Counter(cleaned_colors)
        most_common_colors = [color for color, count in color_counter.most_common(10)]
        
        # Intelligently assign colors to roles
        return self._assign_color_roles(most_common_colors, soup)
    
    def _extract_typography(self, css_content: str, inline_styles: List[str], soup: BeautifulSoup) -> Typography:
        """Extract typography system from CSS and HTML"""
        
        # Extract font families
        font_patterns = [
            r'font-family:\s*([^;}\n]+)',
            r'font:\s*[^;}\n]*?([\'"][^\'"]+"[\'"][^;}\n]*)',
        ]
        
        all_styles = css_content + " ".join(inline_styles)
        fonts = []
        
        for pattern in font_patterns:
            matches = re.findall(pattern, all_styles, re.IGNORECASE)
            fonts.extend(matches)
        
        # Clean font names
        cleaned_fonts = []
        for font in fonts:
            font = font.strip().replace('"', '').replace("'", '')
            if font and font.lower() not in ['inherit', 'initial', 'unset']:
                cleaned_fonts.append(font)
        
        font_counter = Counter(cleaned_fonts)
        common_fonts = [font for font, count in font_counter.most_common(5)]
        
        # Assign font roles
        primary_font = self._get_best_font(common_fonts, 'primary')
        heading_font = self._get_best_font(common_fonts, 'heading')
        
        # Extract font sizes, weights, etc.
        font_sizes = self._extract_font_sizes(all_styles)
        font_weights = self._extract_font_weights(all_styles)
        
        return Typography(
            primary_font=primary_font,
            secondary_font=primary_font,
            heading_font=heading_font,
            font_sizes=font_sizes,
            font_weights=font_weights
        )
    
    def _extract_visual_style(self, css_content: str, inline_styles: List[str], soup: BeautifulSoup) -> VisualStyle:
        """Extract visual style patterns like spacing, shadows, borders"""
        
        all_styles = css_content + " ".join(inline_styles)
        
        # Extract border radius patterns
        border_radius = self._extract_border_radius(all_styles)
        
        # Extract shadow patterns
        shadow_style = self._extract_shadows(all_styles)
        
        # Extract spacing patterns
        spacing_scale = self._extract_spacing_patterns(all_styles)
        
        # Analyze button styles
        button_styles = self._analyze_button_styles(soup, all_styles)
        
        # Analyze card/container styles
        card_styles = self._analyze_card_styles(soup, all_styles)
        
        # Detect layout patterns
        layout_patterns = self._detect_layout_patterns(soup)
        
        return VisualStyle(
            border_radius=border_radius,
            shadow_style=shadow_style,
            spacing_scale=spacing_scale,
            button_styles=button_styles,
            card_styles=card_styles,
            layout_patterns=layout_patterns
        )
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color string is valid and not a common non-color value"""
        invalid_colors = ['transparent', 'inherit', 'initial', 'unset', 'none', 'auto', '0', '']
        if color in invalid_colors or len(color) == 0:
            return False
        
        # Additional validation for hex colors
        if color.startswith('#'):
            hex_part = color[1:].strip()
            if len(hex_part) in [3, 6]:
                return all(c.isdigit() or c.lower() in 'abcdef' for c in hex_part)
        
        # Allow rgb, rgba, hsl functions and named colors
        if any(color.startswith(prefix) for prefix in ['rgb', 'rgba', 'hsl', 'hsla']) or color.isalpha():
            return True
            
        return False
    
    def _assign_color_roles(self, colors: List[str], soup: BeautifulSoup) -> ColorPalette:
        """Intelligently assign colors to semantic roles (primary, secondary, etc.)"""
        
        if not colors:
            return ColorPalette()
        
        # Analyze color context from HTML elements
        primary_color = self._find_primary_color(colors, soup)
        secondary_color = self._find_secondary_color(colors, primary_color)
        accent_color = self._find_accent_color(colors, primary_color, secondary_color)
        
        # Find text colors
        text_primary = self._find_text_color(colors, 'primary')
        text_secondary = self._find_text_color(colors, 'secondary')
        
        # Find background colors
        background = self._find_background_color(colors)
        
        return ColorPalette(
            primary=primary_color,
            secondary=secondary_color,
            accent=accent_color,
            background=background,
            text_primary=text_primary,
            text_secondary=text_secondary
        )
    
    def _find_primary_color(self, colors: List[str], soup: BeautifulSoup) -> str:
        """Find the primary brand color by analyzing button, header, and CTA elements"""
        
        # Look for colors in important elements
        primary_selectors = ['button', '.btn', '.cta', 'header', '.header', '.primary', '.brand']
        primary_candidates = []
        
        for selector in primary_selectors:
            elements = soup.select(selector)
            for element in elements[:3]:  # Limit to avoid performance issues
                style = element.get('style', '')
                if style:
                    # Extract colors from inline styles
                    color_matches = re.findall(r'(?:color|background-color|background):\s*([#\w\(\),\s\%\.]+)', style)
                    primary_candidates.extend(color_matches)
        
        # Find most common color in primary contexts
        if primary_candidates:
            primary_counter = Counter(primary_candidates)
            return primary_counter.most_common(1)[0][0]
        
        # Fallback to first available color
        return colors[0] if colors else "#3B82F6"
    
    def _find_secondary_color(self, colors: List[str], primary_color: str) -> str:
        """Find secondary color (usually gray or a complementary color)"""
        for color in colors:
            if color != primary_color and self._is_neutral_color(color):
                return color
        return colors[1] if len(colors) > 1 else "#64748B"
    
    def _find_accent_color(self, colors: List[str], primary_color: str, secondary_color: str) -> str:
        """Find accent color for highlights and CTAs"""
        for color in colors:
            if color not in [primary_color, secondary_color] and self._is_bright_color(color):
                return color
        return colors[2] if len(colors) > 2 else "#F59E0B"
    
    def _find_text_color(self, colors: List[str], priority: str) -> str:
        """Find text colors (usually dark or light)"""
        dark_colors = [c for c in colors if self._is_dark_color(c)]
        light_colors = [c for c in colors if self._is_light_color(c)]
        
        if priority == 'primary':
            return dark_colors[0] if dark_colors else "#111827"
        else:
            return dark_colors[1] if len(dark_colors) > 1 else "#6B7280"
    
    def _find_background_color(self, colors: List[str]) -> str:
        """Find background color (usually light)"""
        light_colors = [c for c in colors if self._is_light_color(c)]
        return light_colors[0] if light_colors else "#FFFFFF"
    
    def _is_neutral_color(self, color: str) -> bool:
        """Check if color is neutral (gray, etc.)"""
        # Simplified check - could be enhanced with actual color analysis
        neutral_keywords = ['gray', 'grey', 'slate', 'stone', 'neutral', 'zinc']
        return any(keyword in color.lower() for keyword in neutral_keywords)
    
    def _is_bright_color(self, color: str) -> bool:
        """Check if color is bright/vibrant"""
        bright_keywords = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink']
        return any(keyword in color.lower() for keyword in bright_keywords)
    
    def _is_dark_color(self, color: str) -> bool:
        """Check if color is dark"""
        try:
            # Simplified - could use actual luminance calculation
            if color.startswith('#'):
                # Remove # and clean the color
                hex_color = color[1:].strip()
                if len(hex_color) == 3:  # #RGB
                    return all(int(c, 16) < 8 for c in hex_color if c.isdigit() or c.lower() in 'abcdef')
                elif len(hex_color) == 6:  # #RRGGBB
                    return all(int(hex_color[i:i+2], 16) < 128 for i in range(0, 6, 2) 
                             if all(c.isdigit() or c.lower() in 'abcdef' for c in hex_color[i:i+2]))
        except (ValueError, IndexError):
            # If parsing fails, fall back to keyword detection
            pass
        return 'dark' in color.lower() or 'black' in color.lower()
    
    def _is_light_color(self, color: str) -> bool:
        """Check if color is light"""
        return not self._is_dark_color(color) or 'white' in color.lower() or 'light' in color.lower()
    
    def _get_best_font(self, fonts: List[str], context: str) -> str:
        """Select best font for given context"""
        if not fonts:
            return "Inter, system-ui, sans-serif"
        
        # Prefer web-safe and modern fonts
        preferred_fonts = ['Inter', 'Roboto', 'Open Sans', 'Lato', 'Montserrat', 'Poppins']
        
        for font in fonts:
            for preferred in preferred_fonts:
                if preferred.lower() in font.lower():
                    return f"{preferred}, system-ui, sans-serif"
        
        # Use first available font with fallbacks
        return f"{fonts[0]}, system-ui, sans-serif"
    
    def _extract_font_sizes(self, styles: str) -> Dict[str, str]:
        """Extract font size patterns from CSS"""
        size_pattern = r'font-size:\s*([^;}\n]+)'
        sizes = re.findall(size_pattern, styles, re.IGNORECASE)
        
        # Convert to standard size scale
        size_map = {}
        for size in set(sizes):
            size = size.strip()
            if 'px' in size:
                px_value = int(re.findall(r'(\d+)', size)[0]) if re.findall(r'(\d+)', size) else 16
                size_map[self._px_to_size_name(px_value)] = size
        
        return size_map if size_map else None
    
    def _extract_font_weights(self, styles: str) -> Dict[str, str]:
        """Extract font weight patterns from CSS"""
        weight_pattern = r'font-weight:\s*([^;}\n]+)'
        weights = re.findall(weight_pattern, styles, re.IGNORECASE)
        
        weight_map = {}
        for weight in set(weights):
            weight = weight.strip()
            weight_map[self._weight_to_name(weight)] = weight
        
        return weight_map if weight_map else None
    
    def _px_to_size_name(self, px: int) -> str:
        """Convert pixel size to semantic size name"""
        size_mapping = {
            12: 'xs', 14: 'sm', 16: 'base', 18: 'lg', 20: 'xl',
            24: '2xl', 30: '3xl', 36: '4xl', 48: '5xl', 60: '6xl'
        }
        return size_mapping.get(px, 'base')
    
    def _weight_to_name(self, weight: str) -> str:
        """Convert font weight to semantic name"""
        weight_mapping = {
            '300': 'light', '400': 'normal', '500': 'medium',
            '600': 'semibold', '700': 'bold', '800': 'extrabold',
            'light': 'light', 'normal': 'normal', 'bold': 'bold'
        }
        return weight_mapping.get(weight.lower(), 'normal')
    
    def _extract_border_radius(self, styles: str) -> str:
        """Extract border radius patterns"""
        radius_pattern = r'border-radius:\s*([^;}\n]+)'
        radii = re.findall(radius_pattern, styles, re.IGNORECASE)
        
        if radii:
            # Return most common radius
            radius_counter = Counter(radii)
            return radius_counter.most_common(1)[0][0].strip()
        
        return "0.5rem"
    
    def _extract_shadows(self, styles: str) -> str:
        """Extract box shadow patterns"""
        shadow_pattern = r'box-shadow:\s*([^;}\n]+)'
        shadows = re.findall(shadow_pattern, styles, re.IGNORECASE)
        
        if shadows:
            shadow_counter = Counter(shadows)
            return shadow_counter.most_common(1)[0][0].strip()
        
        return "0 4px 6px -1px rgb(0 0 0 / 0.1)"
    
    def _extract_spacing_patterns(self, styles: str) -> Dict[str, str]:
        """Extract spacing patterns (margin, padding)"""
        # This would analyze margin/padding patterns
        # For now, return default Tailwind-like scale
        return None
    
    def _analyze_button_styles(self, soup: BeautifulSoup, styles: str) -> Dict[str, Any]:
        """Analyze button styling patterns"""
        buttons = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta'))
        
        # Analyze common button patterns
        button_styles = {
            'primary': {'padding': '0.75rem 1.5rem', 'rounded': '0.5rem'},
            'secondary': {'padding': '0.75rem 1.5rem', 'rounded': '0.5rem'},
        }
        
        return button_styles
    
    def _analyze_card_styles(self, soup: BeautifulSoup, styles: str) -> Dict[str, Any]:
        """Analyze card/container styling patterns"""
        cards = soup.find_all(class_=re.compile(r'card|container|box|panel'))
        
        card_styles = {
            'padding': '1.5rem',
            'rounded': '0.75rem',
            'shadow': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        }
        
        return card_styles
    
    def _detect_layout_patterns(self, soup: BeautifulSoup) -> List[str]:
        """Detect common layout patterns used"""
        patterns = []
        
        # Check for grid usage
        if soup.find_all(class_=re.compile(r'grid|row|col')):
            patterns.append('grid')
        
        # Check for flexbox usage  
        if soup.find_all(class_=re.compile(r'flex|d-flex')):
            patterns.append('flex')
        
        # Default patterns
        if not patterns:
            patterns = ['flex', 'grid']
        
        return patterns
    
    def _detect_industry(self, soup: BeautifulSoup) -> str:
        """Detect industry/business type from content"""
        text = soup.get_text().lower()
        
        industry_keywords = {
            'plumbing': ['plumb', 'pipe', 'drain', 'water', 'leak', 'faucet', 'toilet'],
            'restaurant': ['food', 'restaurant', 'menu', 'dining', 'cuisine', 'chef'],
            'healthcare': ['health', 'medical', 'doctor', 'patient', 'treatment'],
            'tech': ['software', 'technology', 'app', 'digital', 'code', 'development'],
            'legal': ['law', 'legal', 'attorney', 'lawyer', 'court', 'justice'],
            'finance': ['finance', 'money', 'investment', 'banking', 'loan'],
            'education': ['education', 'school', 'learning', 'student', 'course'],
            'construction': ['construction', 'building', 'contractor', 'renovation'],
            'cleaning': ['clean', 'cleaning', 'service', 'maintenance', 'janitor'],
        }
        
        for industry, keywords in industry_keywords.items():
            if sum(text.count(keyword) for keyword in keywords) >= 3:
                return industry
        
        return 'business'
    
    def _detect_tone(self, soup: BeautifulSoup) -> str:
        """Detect brand tone from content and language"""
        text = soup.get_text().lower()
        
        # Analyze language patterns
        if any(word in text for word in ['premium', 'luxury', 'exclusive', 'elite']):
            return 'luxury'
        elif any(word in text for word in ['fun', 'exciting', 'awesome', 'cool']):
            return 'playful'
        elif any(word in text for word in ['trust', 'reliable', 'professional', 'expert']):
            return 'professional'
        elif any(word in text for word in ['friendly', 'welcome', 'family', 'community']):
            return 'friendly'
        
        return 'professional'
    
    def _detect_layout_style(self, soup: BeautifulSoup) -> str:
        """Detect preferred layout style"""
        # Analyze layout complexity and patterns
        sections = len(soup.find_all(['section', 'div'], class_=re.compile(r'section|container|wrapper')))
        
        if sections > 10:
            return 'complex'
        elif sections > 5:
            return 'modern'
        else:
            return 'minimal'
    
    def _detect_image_style(self, soup: BeautifulSoup) -> str:
        """Detect image style preference"""
        images = soup.find_all('img')
        
        if not images:
            return 'icons'
        
        # Analyze image patterns (simplified)
        if len(images) > 10:
            return 'photography'
        elif any('icon' in img.get('class', []) for img in images):
            return 'icons'
        
        return 'photography'
    
    def _get_default_brand_identity(self) -> BrandIdentity:
        """Return default modern brand identity when extraction fails"""
        return BrandIdentity(
            colors=ColorPalette(),
            typography=Typography(),
            style=VisualStyle(),
            industry="business",
            tone="professional",
            layout_preference="modern",
            image_style="photography"
        )

def extract_brand_identity(url: str, html: str) -> BrandIdentity:
    """Convenience function for brand extraction"""
    extractor = BrandExtractor()
    return extractor.extract_brand_identity(url, html)