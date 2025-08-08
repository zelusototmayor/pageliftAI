"""
Image Processing Pipeline - Advanced image handling for modern web templates
Handles sizing, aspect ratios, lazy loading, optimization, and fallbacks
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

@dataclass
class ProcessedImage:
    """Processed image with metadata and optimization"""
    url: str
    alt_text: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: str = "16/9"
    file_size: Optional[int] = None
    format: str = "webp"
    lazy_load: bool = True
    placeholder: Optional[str] = None  # Base64 placeholder
    srcset: Optional[str] = None  # Responsive image set
    sizes: str = "100vw"  # Default sizes attribute
    category: str = "content"  # hero, content, icon, avatar, gallery
    
@dataclass
class ImageSet:
    """Collection of images for a section"""
    images: List[ProcessedImage]
    primary_image: Optional[ProcessedImage] = None
    gallery_images: List[ProcessedImage] = None
    icon_images: List[ProcessedImage] = None
    hero_images: List[ProcessedImage] = None
    
    def __post_init__(self):
        if self.gallery_images is None:
            self.gallery_images = []
        if self.icon_images is None:
            self.icon_images = []
        if self.hero_images is None:
            self.hero_images = []

class ImageProcessor:
    """Advanced image processing for modern web templates"""
    
    def __init__(self):
        self.processed_cache = {}
        self.fallback_images = self._get_fallback_images()
        
    def process_section_images(self, section_data: Dict[str, Any], brand_identity: Dict[str, Any]) -> ImageSet:
        """Process all images in a section with context-aware optimization"""
        
        img_urls = section_data.get('img_urls', [])
        section_category = section_data.get('category', 'other')
        
        if not img_urls:
            # Return appropriate fallback images based on section type
            return self._get_fallback_image_set(section_category, brand_identity)
        
        logger.info(f"Processing {len(img_urls)} images for {section_category} section")
        
        processed_images = []
        
        for i, img_url in enumerate(img_urls):
            if not img_url or img_url.startswith('data:'):
                continue
                
            try:
                processed_img = self._process_single_image(
                    img_url, 
                    section_category, 
                    i, 
                    brand_identity
                )
                if processed_img:
                    processed_images.append(processed_img)
                    
            except Exception as e:
                logger.warning(f"Failed to process image {img_url}: {e}")
                # Add fallback image
                fallback = self._get_fallback_image(section_category, brand_identity)
                if fallback:
                    processed_images.append(fallback)
        
        # Organize images by type
        image_set = self._organize_images(processed_images, section_category)
        
        logger.info(f"Image processing complete: {len(processed_images)} images processed")
        return image_set
    
    def _process_single_image(self, img_url: str, section_category: str, index: int, brand_identity: Dict[str, Any]) -> Optional[ProcessedImage]:
        """Process a single image with optimization and metadata"""
        
        # Check cache first
        cache_key = f"{img_url}_{section_category}"
        if cache_key in self.processed_cache:
            return self.processed_cache[cache_key]
        
        try:
            # Determine image category and requirements
            image_category = self._determine_image_category(section_category, index)
            requirements = self._get_image_requirements(image_category)
            
            # Get image metadata (without downloading full image)
            metadata = self._get_image_metadata(img_url)
            
            # Create processed image
            processed_img = ProcessedImage(
                url=img_url,
                alt_text=self._generate_alt_text(section_category, index, brand_identity),
                width=metadata.get('width'),
                height=metadata.get('height'),
                aspect_ratio=self._calculate_aspect_ratio(metadata, requirements),
                file_size=metadata.get('file_size'),
                format=self._determine_optimal_format(metadata),
                lazy_load=requirements['lazy_load'],
                placeholder=self._generate_placeholder(img_url, metadata),
                srcset=self._generate_srcset(img_url, requirements),
                sizes=self._generate_sizes(image_category),
                category=image_category
            )
            
            # Cache the result
            self.processed_cache[cache_key] = processed_img
            
            return processed_img
            
        except Exception as e:
            logger.error(f"Failed to process image {img_url}: {e}")
            return None
    
    def _get_image_metadata(self, img_url: str) -> Dict[str, Any]:
        """Get image metadata without downloading full image"""
        try:
            # Use HEAD request to get content info
            response = requests.head(img_url, timeout=5)
            
            metadata = {
                'content_type': response.headers.get('content-type', ''),
                'file_size': int(response.headers.get('content-length', 0)),
            }
            
            # For important images, download a small portion to get dimensions
            if 'image' in metadata['content_type']:
                try:
                    # Download first 2KB to get image header
                    headers = {'Range': 'bytes=0-2048'}
                    partial_response = requests.get(img_url, headers=headers, timeout=5)
                    
                    if partial_response.status_code == 206:  # Partial content
                        # Try to get dimensions from image header
                        dimensions = self._get_dimensions_from_header(partial_response.content)
                        if dimensions:
                            metadata.update(dimensions)
                            
                except Exception:
                    # If partial download fails, skip dimensions
                    pass
            
            return metadata
            
        except Exception as e:
            logger.debug(f"Failed to get metadata for {img_url}: {e}")
            return {}
    
    def _get_dimensions_from_header(self, image_data: bytes) -> Optional[Dict[str, int]]:
        """Extract dimensions from image header data"""
        try:
            # Try PIL for common formats
            image = Image.open(io.BytesIO(image_data))
            return {'width': image.width, 'height': image.height}
        except Exception:
            # Try manual parsing for common formats
            return self._parse_image_dimensions(image_data)
    
    def _parse_image_dimensions(self, data: bytes) -> Optional[Dict[str, int]]:
        """Parse image dimensions from binary data"""
        if not data:
            return None
            
        try:
            # PNG signature and IHDR chunk
            if data.startswith(b'\x89PNG\r\n\x1a\n'):
                if len(data) >= 24:  # PNG header + IHDR start
                    width = int.from_bytes(data[16:20], 'big')
                    height = int.from_bytes(data[20:24], 'big')
                    return {'width': width, 'height': height}
            
            # JPEG markers
            elif data.startswith(b'\xff\xd8'):
                # Look for SOF marker (Start of Frame)
                i = 2
                while i < len(data) - 8:
                    if data[i] == 0xFF and data[i+1] in [0xC0, 0xC1, 0xC2]:
                        height = int.from_bytes(data[i+5:i+7], 'big')
                        width = int.from_bytes(data[i+7:i+9], 'big')
                        return {'width': width, 'height': height}
                    i += 1
            
            # WebP format
            elif data.startswith(b'RIFF') and b'WEBP' in data[:12]:
                if b'VP8 ' in data[:16] and len(data) >= 30:
                    width = int.from_bytes(data[26:28], 'little') & 0x3fff
                    height = int.from_bytes(data[28:30], 'little') & 0x3fff
                    return {'width': width, 'height': height}
                    
        except Exception:
            pass
            
        return None
    
    def _determine_image_category(self, section_category: str, index: int) -> str:
        """Determine specific image category for optimization"""
        
        category_mapping = {
            'hero': 'hero' if index == 0 else 'content',
            'about': 'content',
            'services': 'content' if index == 0 else 'gallery',
            'gallery': 'gallery',
            'contact': 'content',
            'other': 'content'
        }
        
        return category_mapping.get(section_category, 'content')
    
    def _get_image_requirements(self, image_category: str) -> Dict[str, Any]:
        """Get optimization requirements for image category"""
        
        requirements = {
            'hero': {
                'max_width': 1920,
                'max_height': 1080,
                'aspect_ratios': ['16/9', '21/9', '4/3'],
                'lazy_load': False,  # Hero images should load immediately
                'priority': 'high',
                'quality': 85,
                'responsive_sizes': [1920, 1280, 768, 480],
            },
            'content': {
                'max_width': 1200,
                'max_height': 800,
                'aspect_ratios': ['16/9', '4/3', '3/2'],
                'lazy_load': True,
                'priority': 'medium',
                'quality': 80,
                'responsive_sizes': [1200, 800, 600, 400],
            },
            'gallery': {
                'max_width': 800,
                'max_height': 800,
                'aspect_ratios': ['1/1', '4/3', '3/2'],
                'lazy_load': True,
                'priority': 'low',
                'quality': 75,
                'responsive_sizes': [800, 600, 400, 300],
            },
            'icon': {
                'max_width': 64,
                'max_height': 64,
                'aspect_ratios': ['1/1'],
                'lazy_load': False,
                'priority': 'high',
                'quality': 90,
                'responsive_sizes': [64, 48, 32],
            },
            'avatar': {
                'max_width': 200,
                'max_height': 200,
                'aspect_ratios': ['1/1'],
                'lazy_load': True,
                'priority': 'medium',
                'quality': 85,
                'responsive_sizes': [200, 150, 100, 64],
            }
        }
        
        return requirements.get(image_category, requirements['content'])
    
    def _calculate_aspect_ratio(self, metadata: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Calculate optimal aspect ratio for image"""
        
        width = metadata.get('width')
        height = metadata.get('height')
        
        if not width or not height:
            # Return first preferred aspect ratio
            return requirements['aspect_ratios'][0]
        
        # Calculate actual ratio
        actual_ratio = width / height
        
        # Find closest preferred ratio
        preferred_ratios = requirements['aspect_ratios']
        ratio_values = []
        
        for ratio_str in preferred_ratios:
            w, h = map(int, ratio_str.split('/'))
            ratio_values.append((w/h, ratio_str))
        
        # Find closest ratio
        closest_ratio = min(ratio_values, key=lambda x: abs(x[0] - actual_ratio))
        
        return closest_ratio[1]
    
    def _determine_optimal_format(self, metadata: Dict[str, Any]) -> str:
        """Determine optimal image format"""
        
        content_type = metadata.get('content_type', '').lower()
        
        # Modern browsers support WebP for better compression
        if 'webp' in content_type:
            return 'webp'
        elif 'png' in content_type:
            return 'webp'  # Convert PNG to WebP for better compression
        elif 'jpeg' in content_type or 'jpg' in content_type:
            return 'webp'  # Convert JPEG to WebP
        else:
            return 'webp'  # Default to WebP
    
    def _generate_alt_text(self, section_category: str, index: int, brand_identity: Dict[str, Any]) -> str:
        """Generate appropriate alt text for image"""
        
        industry = brand_identity.get('brand', {}).get('industry', 'business')
        
        alt_templates = {
            'hero': {
                'plumbing': f"Professional plumbing services - {industry} experts ready to help",
                'restaurant': f"Delicious food and dining experience at our {industry}",
                'tech': f"Innovative {industry} solutions and technology services",
                'default': f"Professional {industry} services and solutions"
            },
            'about': {
                'plumbing': "Experienced plumbing team with years of expertise",
                'restaurant': "Our kitchen team preparing fresh, quality meals",
                'tech': "Our expert development team working on innovative solutions",
                'default': f"Professional {industry} team and expertise"
            },
            'services': {
                'plumbing': f"Quality plumbing service #{index + 1} - professional installation and repair",
                'restaurant': f"Featured dish #{index + 1} - fresh and delicious cuisine",
                'tech': f"Technology service #{index + 1} - innovative solutions",
                'default': f"Professional service #{index + 1} - quality {industry} solutions"
            },
            'contact': {
                'default': f"Contact our professional {industry} team for expert service"
            },
            'other': {
                'default': f"Professional {industry} image #{index + 1}"
            }
        }
        
        category_templates = alt_templates.get(section_category, alt_templates['other'])
        template = category_templates.get(industry, category_templates['default'])
        
        return template
    
    def _generate_placeholder(self, img_url: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Generate low-quality placeholder for lazy loading"""
        try:
            # Create a simple colored placeholder based on URL hash
            url_hash = hash(img_url) % 1000000
            
            # Generate a subtle color based on hash
            hue = (url_hash % 360)
            
            # Create SVG placeholder
            svg_placeholder = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
                <rect width="400" height="300" fill="hsl({hue}, 10%, 95%)"/>
                <circle cx="200" cy="150" r="30" fill="hsl({hue}, 20%, 85%)" opacity="0.5"/>
                <text x="200" y="160" text-anchor="middle" fill="hsl({hue}, 30%, 70%)" font-family="system-ui" font-size="14">Loading...</text>
            </svg>'''
            
            # Convert to base64
            placeholder_b64 = base64.b64encode(svg_placeholder.encode()).decode()
            return f"data:image/svg+xml;base64,{placeholder_b64}"
            
        except Exception:
            # Return default placeholder
            return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2Y5ZmFmYiIvPjx0ZXh0IHg9IjIwMCIgeT0iMTUwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOWNhM2FmIiBmb250LWZhbWlseT0ic3lzdGVtLXVpIiBmb250LXNpemU9IjE0Ij5JbWFnZTwvdGV4dD48L3N2Zz4="
    
    def _generate_srcset(self, img_url: str, requirements: Dict[str, Any]) -> str:
        """Generate responsive srcset for different screen sizes"""
        
        sizes = requirements['responsive_sizes']
        
        # For now, return the original URL for all sizes
        # In production, you'd use an image service like Cloudinary
        srcset_parts = []
        
        for size in sizes:
            # Format: URL width_descriptor
            srcset_parts.append(f"{img_url} {size}w")
        
        return ", ".join(srcset_parts)
    
    def _generate_sizes(self, image_category: str) -> str:
        """Generate sizes attribute for responsive images"""
        
        sizes_mapping = {
            'hero': '100vw',
            'content': '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
            'gallery': '(max-width: 768px) 50vw, (max-width: 1200px) 33vw, 25vw',
            'icon': '64px',
            'avatar': '(max-width: 768px) 64px, 128px'
        }
        
        return sizes_mapping.get(image_category, '100vw')
    
    def _organize_images(self, processed_images: List[ProcessedImage], section_category: str) -> ImageSet:
        """Organize images by type and set primary image"""
        
        if not processed_images:
            return ImageSet(images=[])
        
        # Categorize images
        hero_images = [img for img in processed_images if img.category == 'hero']
        gallery_images = [img for img in processed_images if img.category == 'gallery']
        icon_images = [img for img in processed_images if img.category == 'icon']
        content_images = [img for img in processed_images if img.category == 'content']
        
        # Determine primary image
        primary_image = None
        if hero_images:
            primary_image = hero_images[0]
        elif content_images:
            primary_image = content_images[0]
        elif processed_images:
            primary_image = processed_images[0]
        
        return ImageSet(
            images=processed_images,
            primary_image=primary_image,
            hero_images=hero_images,
            gallery_images=gallery_images,
            icon_images=icon_images
        )
    
    def _get_fallback_images(self) -> Dict[str, List[str]]:
        """Get fallback images for different industries and contexts"""
        
        return {
            'plumbing': {
                'hero': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1920&h=1080&fit=crop',
                'services': 'https://images.unsplash.com/photo-1562146077-0e35ba36b0e7?w=800&h=600&fit=crop',
                'contact': 'https://images.unsplash.com/photo-1516156008625-3a9d6067fab5?w=600&h=400&fit=crop'
            },
            'restaurant': {
                'hero': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1920&h=1080&fit=crop',
                'services': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop',
                'contact': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=600&h=400&fit=crop'
            },
            'business': {
                'hero': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&h=1080&fit=crop',
                'services': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop',
                'contact': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=600&h=400&fit=crop'
            }
        }
    
    def _get_fallback_image_set(self, section_category: str, brand_identity: Dict[str, Any]) -> ImageSet:
        """Get appropriate fallback images when no images are found"""
        
        industry = brand_identity.get('brand', {}).get('industry', 'business')
        fallback_urls = self.fallback_images.get(industry, self.fallback_images['business'])
        
        # Get appropriate fallback image
        if section_category == 'hero':
            img_url = fallback_urls.get('hero', fallback_urls['services'])
        elif section_category in ['services', 'about']:
            img_url = fallback_urls.get('services', fallback_urls['hero'])
        else:
            img_url = fallback_urls.get('contact', fallback_urls['services'])
        
        # Create processed fallback image
        fallback_image = ProcessedImage(
            url=img_url,
            alt_text=self._generate_alt_text(section_category, 0, brand_identity),
            aspect_ratio="16/9",
            format="webp",
            lazy_load=(section_category != 'hero'),
            category=self._determine_image_category(section_category, 0),
            sizes=self._generate_sizes(self._determine_image_category(section_category, 0))
        )
        
        return ImageSet(
            images=[fallback_image],
            primary_image=fallback_image
        )
    
    def _get_fallback_image(self, section_category: str, brand_identity: Dict[str, Any]) -> ProcessedImage:
        """Get a single fallback image"""
        fallback_set = self._get_fallback_image_set(section_category, brand_identity)
        return fallback_set.primary_image
    
    def generate_image_html(self, image: ProcessedImage, css_classes: str = "") -> str:
        """Generate modern HTML for an image with all optimizations"""
        
        # Build img attributes
        attributes = [
            f'src="{image.url}"',
            f'alt="{image.alt_text}"',
            f'class="{css_classes}"'
        ]
        
        # Add responsive attributes
        if image.srcset:
            attributes.append(f'srcset="{image.srcset}"')
        
        if image.sizes:
            attributes.append(f'sizes="{image.sizes}"')
        
        # Add lazy loading
        if image.lazy_load:
            attributes.append('loading="lazy"')
            attributes.append('decoding="async"')
        else:
            # Priority images should load immediately
            attributes.append('fetchpriority="high"')
        
        # Add dimensions if available
        if image.width and image.height:
            attributes.append(f'width="{image.width}"')
            attributes.append(f'height="{image.height}"')
        
        # Create modern picture element for better format support
        if image.format == 'webp':
            return f'''<picture>
                <source srcset="{image.url}" type="image/webp">
                <img {' '.join(attributes)}>
            </picture>'''
        else:
            return f'<img {' '.join(attributes)}>'

def process_section_images(section_data: Dict[str, Any], brand_identity: Dict[str, Any]) -> ImageSet:
    """Convenience function to process section images"""
    processor = ImageProcessor()
    return processor.process_section_images(section_data, brand_identity)