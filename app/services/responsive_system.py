"""
Mobile-First Responsive Design System
Advanced responsive utilities and breakpoint management for modern web templates
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class Breakpoint:
    """Responsive breakpoint configuration"""
    name: str
    min_width: int
    max_width: Optional[int]
    container_width: int
    columns: int
    gutter: int
    font_scale: float
    spacing_scale: float


@dataclass
class ResponsiveConfig:
    """Responsive configuration for different device types"""
    breakpoints: List[Breakpoint]
    touch_targets: Dict[str, int]
    font_sizes: Dict[str, Dict[str, str]]
    spacing: Dict[str, Dict[str, str]]
    component_sizes: Dict[str, Dict[str, str]]


class ResponsiveSystem:
    """Advanced responsive design system with mobile-first approach"""
    
    def __init__(self):
        self.config = self._create_responsive_config()
        self.device_capabilities = self._get_device_capabilities()
        
    def generate_responsive_css(self, brand_identity: Dict[str, Any]) -> str:
        """Generate complete responsive CSS system"""
        
        industry = brand_identity.get('brand', {}).get('industry', 'business')
        tone = brand_identity.get('brand', {}).get('tone', 'professional')
        
        css_parts = [
            self._build_breakpoint_system(),
            self._build_container_system(),
            self._build_responsive_typography(industry, tone),
            self._build_responsive_spacing(),
            self._build_responsive_components(),
            self._build_touch_optimizations(),
            self._build_device_specific_styles(),
            self._build_print_styles(),
            self._build_accessibility_enhancements(),
            self._build_performance_optimizations()
        ]
        
        return '\n\n'.join(filter(None, css_parts))
    
    def _create_responsive_config(self) -> ResponsiveConfig:
        """Create comprehensive responsive configuration"""
        
        breakpoints = [
            # Mobile-first approach
            Breakpoint('xs', 0, 639, 100, 4, 16, 0.9, 0.8),        # Small phones
            Breakpoint('sm', 640, 767, 640, 6, 20, 0.95, 0.9),     # Large phones
            Breakpoint('md', 768, 1023, 768, 8, 24, 1.0, 1.0),     # Tablets
            Breakpoint('lg', 1024, 1279, 1024, 12, 32, 1.05, 1.1), # Small desktops
            Breakpoint('xl', 1280, 1535, 1280, 12, 40, 1.1, 1.2),  # Large desktops
            Breakpoint('2xl', 1536, None, 1536, 12, 48, 1.15, 1.3) # Extra large screens
        ]
        
        # Touch-friendly target sizes (44px minimum)
        touch_targets = {
            'minimum': 44,
            'comfortable': 48,
            'large': 56
        }
        
        # Responsive font scales
        font_sizes = {
            'xs': {
                'text-xs': '0.75rem',
                'text-sm': '0.875rem', 
                'text-base': '1rem',
                'text-lg': '1.125rem',
                'text-xl': '1.25rem',
                'text-2xl': '1.5rem',
                'text-3xl': '1.875rem',
                'text-4xl': '2.25rem',
                'text-5xl': '2.5rem',
                'text-6xl': '3rem'
            },
            'sm': {
                'text-xs': '0.75rem',
                'text-sm': '0.875rem',
                'text-base': '1rem', 
                'text-lg': '1.125rem',
                'text-xl': '1.25rem',
                'text-2xl': '1.5rem',
                'text-3xl': '1.875rem',
                'text-4xl': '2.5rem',
                'text-5xl': '3rem',
                'text-6xl': '3.5rem'
            },
            'md': {
                'text-xs': '0.75rem',
                'text-sm': '0.875rem',
                'text-base': '1rem',
                'text-lg': '1.125rem', 
                'text-xl': '1.25rem',
                'text-2xl': '1.5rem',
                'text-3xl': '1.875rem',
                'text-4xl': '2.75rem',
                'text-5xl': '3.5rem',
                'text-6xl': '4rem'
            },
            'lg': {
                'text-xs': '0.75rem',
                'text-sm': '0.875rem',
                'text-base': '1rem',
                'text-lg': '1.125rem',
                'text-xl': '1.25rem',
                'text-2xl': '1.5rem', 
                'text-3xl': '1.875rem',
                'text-4xl': '3rem',
                'text-5xl': '4rem',
                'text-6xl': '4.5rem'
            }
        }
        
        # Responsive spacing scales
        spacing = {
            'xs': {
                'space-xs': '0.25rem',
                'space-sm': '0.5rem',
                'space-md': '0.75rem',
                'space-lg': '1rem',
                'space-xl': '1.5rem',
                'space-2xl': '2rem',
                'space-3xl': '2.5rem',
                'space-4xl': '3rem'
            },
            'md': {
                'space-xs': '0.25rem',
                'space-sm': '0.5rem', 
                'space-md': '1rem',
                'space-lg': '1.5rem',
                'space-xl': '2rem',
                'space-2xl': '3rem',
                'space-3xl': '4rem',
                'space-4xl': '6rem'
            },
            'lg': {
                'space-xs': '0.25rem',
                'space-sm': '0.5rem',
                'space-md': '1rem',
                'space-lg': '1.5rem',
                'space-xl': '2rem',
                'space-2xl': '3rem',
                'space-3xl': '4rem',
                'space-4xl': '8rem'
            }
        }
        
        # Component size variations
        component_sizes = {
            'buttons': {
                'xs': 'px-3 py-1.5 text-sm',
                'sm': 'px-4 py-2 text-sm',
                'md': 'px-6 py-3 text-base',
                'lg': 'px-8 py-4 text-lg',
                'xl': 'px-10 py-5 text-xl'
            },
            'cards': {
                'xs': 'p-4',
                'sm': 'p-6',
                'md': 'p-8',
                'lg': 'p-10',
                'xl': 'p-12'
            }
        }
        
        return ResponsiveConfig(
            breakpoints=breakpoints,
            touch_targets=touch_targets,
            font_sizes=font_sizes,
            spacing=spacing,
            component_sizes=component_sizes
        )
    
    def _get_device_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Define device-specific capabilities and optimizations"""
        return {
            'mobile': {
                'touch': True,
                'hover': False,
                'bandwidth': 'limited',
                'memory': 'limited',
                'cpu': 'limited',
                'optimizations': ['reduce_animations', 'compress_images', 'minimize_js']
            },
            'tablet': {
                'touch': True,
                'hover': False,
                'bandwidth': 'good',
                'memory': 'good', 
                'cpu': 'good',
                'optimizations': ['optimize_images', 'lazy_load']
            },
            'desktop': {
                'touch': False,
                'hover': True,
                'bandwidth': 'excellent',
                'memory': 'excellent',
                'cpu': 'excellent',
                'optimizations': ['full_experience', 'advanced_animations']
            }
        }
    
    def _build_breakpoint_system(self) -> str:
        """Build comprehensive breakpoint system"""
        css = "/* Responsive Breakpoint System */\n"
        
        # CSS custom properties for breakpoints
        css += ":root {\n"
        for bp in self.config.breakpoints:
            css += f"  --breakpoint-{bp.name}: {bp.min_width}px;\n"
        css += "}\n\n"
        
        # Breakpoint utilities
        css += "/* Responsive Display Utilities */\n"
        for bp in self.config.breakpoints:
            if bp.max_width:
                css += f"@media (min-width: {bp.min_width}px) and (max-width: {bp.max_width}px) {{\n"
            else:
                css += f"@media (min-width: {bp.min_width}px) {{\n"
            
            css += f"  .{bp.name}\\:block {{ display: block; }}\n"
            css += f"  .{bp.name}\\:hidden {{ display: none; }}\n" 
            css += f"  .{bp.name}\\:flex {{ display: flex; }}\n"
            css += f"  .{bp.name}\\:grid {{ display: grid; }}\n"
            css += f"  .{bp.name}\\:inline-flex {{ display: inline-flex; }}\n"
            css += "}\n\n"
            
        return css
    
    def _build_container_system(self) -> str:
        """Build responsive container system"""
        css = "/* Responsive Container System */\n"
        
        css += ".container {\n"
        css += "  width: 100%;\n"
        css += "  margin: 0 auto;\n"
        css += "  padding-left: 1rem;\n"
        css += "  padding-right: 1rem;\n"
        css += "}\n\n"
        
        for bp in self.config.breakpoints:
            if bp.min_width > 0:
                css += f"@media (min-width: {bp.min_width}px) {{\n"
                css += "  .container {\n"
                css += f"    max-width: {bp.container_width}px;\n"
                css += f"    padding-left: {bp.gutter}px;\n"
                css += f"    padding-right: {bp.gutter}px;\n"
                css += "  }\n"
                css += "}\n\n"
        
        # Fluid containers
        css += "/* Fluid Containers */\n"
        css += ".container-fluid {\n"
        css += "  width: 100%;\n" 
        css += "  padding-left: 1rem;\n"
        css += "  padding-right: 1rem;\n"
        css += "}\n\n"
        
        return css
    
    def _build_responsive_typography(self, industry: str, tone: str) -> str:
        """Build responsive typography system"""
        css = "/* Responsive Typography */\n"
        
        # Base responsive font sizing
        css += "html {\n"
        css += "  font-size: 16px; /* Base size for mobile */\n"
        css += "}\n\n"
        
        for bp in self.config.breakpoints:
            if bp.min_width > 0:
                base_size = 16 * bp.font_scale
                css += f"@media (min-width: {bp.min_width}px) {{\n"
                css += "  html {\n"
                css += f"    font-size: {base_size}px;\n"
                css += "  }\n"
                css += "}\n\n"
        
        # Responsive heading scales
        for bp_name, sizes in self.config.font_sizes.items():
            bp = next((b for b in self.config.breakpoints if b.name == bp_name), None)
            if bp and bp.min_width > 0:
                css += f"@media (min-width: {bp.min_width}px) {{\n"
                for size_class, size_value in sizes.items():
                    css += f"  .{size_class} {{ font-size: {size_value}; }}\n"
                css += "}\n\n"
        
        # Industry-specific responsive adjustments
        if industry == 'restaurant':
            css += "/* Restaurant Industry Typography */\n"
            css += "@media (max-width: 767px) {\n"
            css += "  .menu-title { font-size: clamp(1.5rem, 4vw, 2rem); }\n"
            css += "  .price-display { font-size: clamp(1rem, 3vw, 1.25rem); }\n"
            css += "}\n\n"
        elif industry == 'tech':
            css += "/* Tech Industry Typography */\n"
            css += "@media (max-width: 767px) {\n"
            css += "  .code-snippet { font-size: 0.75rem; line-height: 1.4; }\n"
            css += "  .api-endpoint { font-size: 0.8rem; }\n"
            css += "}\n\n"
        
        # Readable line lengths
        css += "/* Optimal Reading Lengths */\n"
        css += ".prose {\n"
        css += "  max-width: none;\n"
        css += "}\n"
        css += "@media (min-width: 640px) {\n"
        css += "  .prose { max-width: 65ch; }\n"
        css += "}\n"
        css += "@media (min-width: 1024px) {\n"
        css += "  .prose { max-width: 75ch; }\n"
        css += "}\n\n"
        
        return css
    
    def _build_responsive_spacing(self) -> str:
        """Build responsive spacing system"""
        css = "/* Responsive Spacing System */\n"
        
        # Section padding responsive scales - PROPORTIONAL FOR BUSINESS SITES
        spacing_classes = {
            'py-section-sm': ('py-6', 'py-8', 'py-10'),    # Small sections (96-160px total)
            'py-section-md': ('py-8', 'py-10', 'py-12'),   # Medium sections (128-192px total) 
            'py-section-lg': ('py-10', 'py-12', 'py-16'),   # Large sections (160-256px total)
            'py-section-xl': ('py-12', 'py-16', 'py-20')    # Extra large sections (192-320px total)
        }
        
        for class_name, (mobile, tablet, desktop) in spacing_classes.items():
            css += f".{class_name} {{\n"
            css += f"  padding-top: {mobile.split('-')[1]};\n"
            css += f"  padding-bottom: {mobile.split('-')[1]};\n"
            css += "}\n"
            
            css += f"@media (min-width: 768px) {{\n"
            css += f"  .{class_name} {{\n"
            css += f"    padding-top: {tablet.split('-')[1]};\n"
            css += f"    padding-bottom: {tablet.split('-')[1]};\n"
            css += "  }\n"
            css += "}\n"
            
            css += f"@media (min-width: 1024px) {{\n"
            css += f"  .{class_name} {{\n"
            css += f"    padding-top: {desktop.split('-')[1]};\n"
            css += f"    padding-bottom: {desktop.split('-')[1]};\n"
            css += "  }\n"
            css += "}\n\n"
        
        # Responsive margins
        margin_scales = ['mt', 'mb', 'ml', 'mr', 'mx', 'my', 'm']
        for scale in margin_scales:
            for size in ['sm', 'md', 'lg', 'xl', '2xl']:
                css += f".{scale}-{size}-responsive {{\n"
                if size == 'sm':
                    css += f"  margin: 0.5rem;\n"
                elif size == 'md':
                    css += f"  margin: 1rem;\n"
                elif size == 'lg':
                    css += f"  margin: 1.5rem;\n"
                elif size == 'xl':
                    css += f"  margin: 2rem;\n"
                elif size == '2xl':
                    css += f"  margin: 3rem;\n"
                css += "}\n"
                
                css += "@media (min-width: 768px) {\n"
                css += f"  .{scale}-{size}-responsive {{\n"
                if size == 'sm':
                    css += f"    margin: 0.75rem;\n"
                elif size == 'md':
                    css += f"    margin: 1.5rem;\n"
                elif size == 'lg':
                    css += f"    margin: 2rem;\n"
                elif size == 'xl':
                    css += f"    margin: 3rem;\n"
                elif size == '2xl':
                    css += f"    margin: 4rem;\n"
                css += "  }\n"
                css += "}\n\n"
        
        return css
    
    def _build_responsive_components(self) -> str:
        """Build responsive component variations"""
        css = "/* Responsive Component Variations */\n"
        
        # Responsive buttons
        css += "/* Responsive Buttons */\n"
        css += ".btn-responsive {\n"
        css += f"  min-height: {self.config.touch_targets['minimum']}px;\n"
        css += "  padding: 0.75rem 1rem;\n"
        css += "  font-size: 0.875rem;\n"
        css += "}\n"
        
        css += "@media (min-width: 768px) {\n"
        css += "  .btn-responsive {\n"
        css += "    padding: 0.875rem 1.5rem;\n"
        css += "    font-size: 1rem;\n"
        css += "  }\n"
        css += "}\n"
        
        css += "@media (min-width: 1024px) {\n"
        css += "  .btn-responsive {\n"
        css += "    padding: 1rem 2rem;\n"
        css += "    font-size: 1.125rem;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # Responsive cards
        css += "/* Responsive Cards */\n"
        css += ".card-responsive {\n"
        css += "  padding: 1rem;\n"
        css += "  margin-bottom: 1rem;\n"
        css += "}\n"
        
        css += "@media (min-width: 768px) {\n"
        css += "  .card-responsive {\n"
        css += "    padding: 1.5rem;\n"
        css += "    margin-bottom: 1.5rem;\n"
        css += "  }\n"
        css += "}\n"
        
        css += "@media (min-width: 1024px) {\n"
        css += "  .card-responsive {\n"
        css += "    padding: 2rem;\n"
        css += "    margin-bottom: 2rem;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # Responsive grids
        css += "/* Responsive Grid Systems */\n"
        css += ".grid-responsive-1 { display: grid; grid-template-columns: 1fr; gap: 1rem; }\n"
        css += ".grid-responsive-2 { display: grid; grid-template-columns: 1fr; gap: 1rem; }\n"
        css += ".grid-responsive-3 { display: grid; grid-template-columns: 1fr; gap: 1rem; }\n"
        css += ".grid-responsive-4 { display: grid; grid-template-columns: 1fr; gap: 1rem; }\n\n"
        
        css += "@media (min-width: 640px) {\n"
        css += "  .grid-responsive-2 { grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }\n"
        css += "  .grid-responsive-3 { grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }\n"
        css += "  .grid-responsive-4 { grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }\n"
        css += "}\n\n"
        
        css += "@media (min-width: 1024px) {\n"
        css += "  .grid-responsive-3 { grid-template-columns: repeat(3, 1fr); gap: 2rem; }\n"
        css += "  .grid-responsive-4 { grid-template-columns: repeat(4, 1fr); gap: 2rem; }\n"
        css += "}\n\n"
        
        return css
    
    def _build_touch_optimizations(self) -> str:
        """Build touch-specific optimizations"""
        css = "/* Touch Device Optimizations */\n"
        
        # Touch target sizes
        css += "@media (hover: none) and (pointer: coarse) {\n"
        css += "  /* Touch-friendly sizing */\n"
        css += f"  .btn, button, a, .form-input, .card {{ min-height: {self.config.touch_targets['minimum']}px; }}\n"
        css += f"  .btn-large, .touch-target {{ min-height: {self.config.touch_targets['comfortable']}px; }}\n"
        css += f"  .btn-xl, .prominent-touch {{ min-height: {self.config.touch_targets['large']}px; }}\n"
        css += "\n"
        
        # Enhanced tap targets
        css += "  /* Enhanced tap areas */\n"
        css += "  .btn, .card, .form-input {\n"
        css += "    padding: 0.75rem;\n"
        css += "  }\n"
        css += "\n"
        
        # Remove hover effects on touch devices
        css += "  /* Disable hover effects */\n"
        css += "  .hover\\:scale-105:hover,\n"
        css += "  .hover\\:shadow-lg:hover,\n"
        css += "  .hover\\:-translate-y-2:hover {\n"
        css += "    transform: none;\n"
        css += "    box-shadow: inherit;\n"
        css += "  }\n"
        css += "\n"
        
        # Touch-specific styles
        css += "  /* Touch-specific interactions */\n"
        css += "  .btn:active,\n"
        css += "  .card:active {\n"
        css += "    transform: scale(0.98);\n"
        css += "    transition: transform 0.1s;\n"
        css += "  }\n"
        css += "\n"
        
        # Improve scroll behavior
        css += "  /* Improved scrolling */\n"
        css += "  body {\n"
        css += "    -webkit-overflow-scrolling: touch;\n"
        css += "    scroll-behavior: smooth;\n"
        css += "  }\n"
        css += "}\n\n"
        
        return css
    
    def _build_device_specific_styles(self) -> str:
        """Build device-specific styling"""
        css = "/* Device-Specific Styles */\n"
        
        # High DPI/Retina displays
        css += "@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {\n"
        css += "  /* High DPI optimizations */\n"
        css += "  .icon, .logo {\n"
        css += "    image-rendering: -webkit-optimize-contrast;\n"
        css += "    image-rendering: crisp-edges;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # iOS specific fixes
        css += "@supports (-webkit-touch-callout: none) {\n"
        css += "  /* iOS Safari fixes */\n"
        css += "  .form-input {\n"
        css += "    -webkit-appearance: none;\n"
        css += "    border-radius: 0;\n"
        css += "  }\n"
        css += "  \n"
        css += "  /* Fix iOS zoom on form focus */\n"
        css += "  input, textarea, select {\n"
        css += "    font-size: 16px;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # Android specific fixes  
        css += "@media screen and (-webkit-min-device-pixel-ratio:0) and (min-resolution:.001dpcm) {\n"
        css += "  /* Android Chrome fixes */\n"
        css += "  .btn {\n"
        css += "    -webkit-tap-highlight-color: transparent;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # Desktop hover capabilities
        css += "@media (hover: hover) and (pointer: fine) {\n"
        css += "  /* Desktop hover enhancements */\n"
        css += "  .hover-lift:hover {\n"
        css += "    transform: translateY(-4px);\n"
        css += "    transition: transform 0.2s ease;\n"
        css += "  }\n"
        css += "  \n"
        css += "  .hover-scale:hover {\n"
        css += "    transform: scale(1.05);\n"
        css += "    transition: transform 0.2s ease;\n"
        css += "  }\n"
        css += "  \n"
        css += "  .hover-glow:hover {\n"
        css += "    box-shadow: 0 0 20px rgba(0,0,0,0.1);\n"
        css += "    transition: box-shadow 0.2s ease;\n"
        css += "  }\n"
        css += "}\n\n"
        
        return css
    
    def _build_print_styles(self) -> str:
        """Build print-optimized styles"""
        css = "/* Print Styles */\n"
        css += "@media print {\n"
        css += "  * {\n"
        css += "    background: white !important;\n"
        css += "    color: black !important;\n"
        css += "    box-shadow: none !important;\n"
        css += "  }\n"
        css += "  \n"
        css += "  .no-print,\n"
        css += "  nav,\n"
        css += "  .btn,\n"
        css += "  .form {\n"
        css += "    display: none !important;\n"
        css += "  }\n"
        css += "  \n"
        css += "  body {\n"
        css += "    font-size: 12pt;\n"
        css += "    line-height: 1.4;\n"
        css += "  }\n"
        css += "  \n"
        css += "  h1, h2, h3 {\n"
        css += "    page-break-after: avoid;\n"
        css += "  }\n"
        css += "  \n"
        css += "  img {\n"
        css += "    max-width: 100%;\n"
        css += "    height: auto;\n"
        css += "  }\n"
        css += "  \n"
        css += "  a[href]:after {\n"
        css += '    content: " (" attr(href) ")";\n'
        css += "  }\n"
        css += "}\n\n"
        
        return css
    
    def _build_accessibility_enhancements(self) -> str:
        """Build accessibility-focused responsive features"""
        css = "/* Accessibility Enhancements */\n"
        
        # Reduced motion preferences
        css += "@media (prefers-reduced-motion: reduce) {\n"
        css += "  *,\n"
        css += "  *::before,\n"
        css += "  *::after {\n"
        css += "    animation-duration: 0.01ms !important;\n"
        css += "    animation-iteration-count: 1 !important;\n"
        css += "    transition-duration: 0.01ms !important;\n"
        css += "    scroll-behavior: auto !important;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # High contrast preferences
        css += "@media (prefers-contrast: high) {\n"
        css += "  .btn {\n"
        css += "    border: 2px solid currentColor;\n"
        css += "  }\n"
        css += "  \n"
        css += "  .card {\n"
        css += "    border: 1px solid currentColor;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # Font size preferences
        css += "@media (prefers-font-size: large) {\n"
        css += "  html {\n"
        css += "    font-size: 18px;\n"
        css += "  }\n"
        css += "}\n\n"
        
        # Focus enhancements for keyboard navigation
        css += "/* Enhanced Focus States */\n"
        css += "@media (prefers-reduced-motion: no-preference) {\n"
        css += "  :focus-visible {\n"
        css += "    outline: 2px solid var(--brand-accent, #F59E0B);\n"
        css += "    outline-offset: 2px;\n"
        css += "    border-radius: 4px;\n"
        css += "    transition: outline-offset 0.2s ease;\n"
        css += "  }\n"
        css += "}\n\n"
        
        return css
    
    def _build_performance_optimizations(self) -> str:
        """Build performance-focused responsive optimizations"""
        css = "/* Performance Optimizations */\n"
        
        # GPU acceleration for animations
        css += ".animate-gpu {\n"
        css += "  transform: translate3d(0, 0, 0);\n"
        css += "  backface-visibility: hidden;\n"
        css += "  perspective: 1000px;\n"
        css += "}\n\n"
        
        # Optimize repaints
        css += ".optimize-paint {\n"
        css += "  will-change: transform;\n"
        css += "}\n\n"
        
        # Connection-aware optimizations  
        css += "@media (prefers-reduced-data: reduce) {\n"
        css += "  /* Reduce data usage */\n"
        css += "  .background-image {\n"
        css += "    background-image: none;\n"
        css += "  }\n"
        css += "  \n"
        css += "  .optional-image {\n"
        css += "    display: none;\n"
        css += "  }\n"
        css += "  \n"
        css += "  .animation,\n"
        css += "  .transition {\n"
        css += "    animation: none;\n"
        css += "    transition: none;\n"
        css += "  }\n"
        css += "}\n\n"
        
        return css

def generate_responsive_css(brand_identity: Dict[str, Any]) -> str:
    """Convenience function to generate responsive CSS"""
    system = ResponsiveSystem()
    return system.generate_responsive_css(brand_identity)