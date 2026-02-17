"""
HTML cleaner module - removes ads, navigation, tracking scripts, etc.
"""
import re
from bs4 import BeautifulSoup
from loguru import logger
from postprocess.config import REMOVE_SELECTORS, REMOVE_TAGS


def clean_html(html_content):
    """
    Clean HTML by removing unwanted elements like ads, navigation, tracking scripts
    """
    soup = BeautifulSoup(html_content, 'lxml')
    modified = False
    
    # Remove elements by CSS selectors
    for selector in REMOVE_SELECTORS:
        elements = soup.select(selector)
        for element in elements:
            element.decompose()
            modified = True
            logger.debug(f"Removed element matching selector: {selector}")
    
    # Remove specific tags with certain attributes
    for tag_config in REMOVE_TAGS:
        tag_name = tag_config['tag']
        attrs = tag_config.get('attrs', {})
        
        # Find tags with matching attributes
        for tag in soup.find_all(tag_name, attrs):
            # Check if any of the attribute values match our criteria
            should_remove = False
            for attr_name, attr_values in attrs.items():
                attr_value = tag.get(attr_name)
                if attr_value:
                    if isinstance(attr_values, list):
                        if isinstance(attr_value, str):
                            if any(val in attr_value for val in attr_values):
                                should_remove = True
                                break
                        elif isinstance(attr_value, list):
                            if any(val in attr_list for val in attr_values for attr_list in attr_value):
                                should_remove = True
                                break
                    else:
                        if attr_values in attr_value:
                            should_remove = True
                            break
            
            if should_remove:
                tag.decompose()
                modified = True
                logger.debug(f"Removed {tag_name} tag with attributes: {attrs}")
    
    # Remove meta tags that are not essential
    for meta in soup.find_all('meta'):
        # Keep charset and viewport, remove others
        if not meta.get('charset') and not meta.get('name') == 'viewport':
            prop = meta.get('property', '')
            name_attr = meta.get('name', '')
            
            # Remove social media and analytics meta tags
            if (prop.startswith(('og:', 'twitter:')) or 
                name_attr in ['keywords', 'description', 'robots', 'generator', 'author', 'publisher', 'copyright']):
                meta.decompose()
                modified = True
    
    # Remove comments that are not essential
    from bs4 import Comment
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        # Remove tracking and ad-related comments
        if any(keyword in comment.lower() for keyword in ['tracking', 'analytics', 'ads', 'advertising', 'google']):
            comment.extract()
            modified = True
    
    # Remove inline styles that hide content
    for tag in soup.find_all(style=True):
        style = tag.get('style', '').lower()
        if 'display: none' in style or 'visibility: hidden' in style:
            # Only remove if it's clearly hiding content and not just layout
            tag_classes = tag.get('class', [])
            if any(cls in ['hidden', 'invisible', 'visually-hidden', 'sr-only'] for cls in tag_classes):
                tag.decompose()
                modified = True
    
    return str(soup) if modified else html_content