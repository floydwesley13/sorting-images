"""
Content stabilizer module - handles lazy loading, hidden content, etc.
"""
import re
from bs4 import BeautifulSoup
from loguru import logger


def stabilize_content(html_content, current_file_path):
    """
    Stabilize content by handling lazy loading and revealing hidden content
    """
    soup = BeautifulSoup(html_content, 'lxml')
    modified = False
    
    # Handle lazy loading images - move data-src to src
    for img in soup.find_all(['img', 'source']):
        if img.get('data-src'):
            img['src'] = img['data-src']
            del img['data-src']
            modified = True
            
        # Also handle other lazy-loading attributes
        if img.get('data-lazy-src'):
            img['src'] = img['data-lazy-src']
            del img['data-lazy-src']
            modified = True
            
        # Clean up additional lazy-loading related attributes
        for attr in ['srcset', 'data-srcset', 'data-original', 'data-lazy', 'onload', 'loading']:
            if img.get(attr):
                del img[attr]
                modified = True
                
        # Remove lazyload class if present
        if img.get('class'):
            classes = img.get('class')
            if 'lazyload' in classes or 'lazy' in classes:
                classes = [cls for cls in classes if cls not in ['lazyload', 'lazy']]
                if classes:
                    img['class'] = classes
                else:
                    del img['class']
                modified = True
    
    # Handle picture elements with source tags
    for picture in soup.find_all('picture'):
        for source in picture.find_all('source'):
            if source.get('data-srcset'):
                source['srcset'] = source['data-srcset']
                del source['data-srcset']
                modified = True
            elif source.get('data-src'):
                source['src'] = source['data-src']
                del source['data-src']
                modified = True
    
    # Reveal hidden collapsible content (for infoboxes, galleries, etc.)
    for element in soup.find_all(class_=re.compile(r'mw-collapsible|mwe-collapsible|collapsible')):
        content_div = element.find(class_=re.compile(r'mw-collapsible-content|mwe-collapsible-content|collapseButton'))
        if content_div:
            # Force display of collapsed content
            if content_div.get('style'):
                content_div['style'] = content_div['style'] + '; display: block !important;'
            else:
                content_div['style'] = 'display: block !important;'
            modified = True
        
        # Find and handle toggle buttons
        toggles = element.find_all(class_=re.compile(r'collapsiblerelement|toggle|mw-collapsible-toggle'))
        for toggle in toggles:
            # Remove toggle buttons since content is now visible
            toggle.decompose()
            modified = True
    
    # Handle other common hiding techniques
    for element in soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden')):
        style = element.get('style', '')
        # Check if it's a real hiding technique vs just a layout thing
        if 'display: none' in style or 'visibility: hidden' in style:
            # For certain classes known to hide content, make it visible
            element_classes = element.get('class', [])
            if any(cls in ['hidden', 'invisible', 'visually-hidden', 'sr-only'] for cls in element_classes):
                element['style'] = style.replace('display: none', 'display: block').replace('visibility: hidden', 'visibility: visible')
                modified = True
    
    # Handle gallery elements that might be hidden initially
    for gallery in soup.find_all(class_=re.compile(r'gallery|slideshow|image-gallery')):
        if gallery.get('style') and ('display: none' in gallery['style'] or 'visibility: hidden' in gallery['style']):
            gallery['style'] = gallery['style'].replace('display: none', 'display: grid').replace('visibility: hidden', 'visibility: visible')
            modified = True
    
    return str(soup) if modified else html_content