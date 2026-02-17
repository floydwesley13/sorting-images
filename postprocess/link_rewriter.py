"""
Link rewriter module - fixes image paths and article links
"""
import re
import os
from urllib.parse import unquote
from bs4 import BeautifulSoup
from pathlib import Path
from loguru import logger
from postprocess.config import IMAGE_DOMAINS, CLEAN_URL_PATTERNS, IMAGE_EXTENSIONS


def clean_url(url):
    """
    Remove query parameters and size segments from URLs
    """
    cleaned = url.split('#')[0]  # Remove fragment
    
    # Apply each cleaning pattern
    for pattern in CLEAN_URL_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Remove trailing slashes and extra characters
    cleaned = cleaned.rstrip('?&/')
    
    return cleaned


def fix_image_paths(soup, current_file_path, project_root):
    """
    Fix image paths by converting CDN URLs to local relative paths
    """
    modified = False
    
    for img in soup.find_all(['img', 'source']):
        src = img.get('src')
        if not src:
            continue
            
        # Clean the URL first
        clean_src = clean_url(src)
        
        # Check if it's a CDN image that needs to be converted
        is_cdn_image = any(domain in clean_src for domain in IMAGE_DOMAINS)
        
        if is_cdn_image:
            # Extract the path part after the CDN domain
            for domain in IMAGE_DOMAINS:
                if domain in clean_src:
                    # Get the part after the domain
                    path_part = clean_src.split(domain)[1]
                    # Remove leading slash if present
                    path_part = path_part.lstrip('/')
                    
                    # Formulate the local path
                    local_img_path = project_root / domain / path_part
                    
                    # Calculate relative path from current file's directory to the image
                    try:
                        rel_path = os.path.relpath(local_img_path, current_file_path.parent)
                        rel_path = rel_path.replace('\\', '/')  # Normalize path separators
                        
                        # Update the src attribute
                        img['src'] = rel_path
                        modified = True
                        logger.debug(f"Fixed image path: {src} -> {rel_path}")
                    except ValueError:
                        # Handle case where paths are on different drives (Windows)
                        logger.warning(f"Could not compute relative path for: {clean_src}")
                    
                    break  # Found the domain, exit loop
    
    # Handle picture/source elements separately
    for picture in soup.find_all('picture'):
        for source in picture.find_all('source'):
            srcset = source.get('srcset')
            if srcset:
                # Clean and potentially fix srcset URLs
                fixed_srcset = srcset
                for domain in IMAGE_DOMAINS:
                    if domain in fixed_srcset:
                        # This is a simplified approach - for a production version, 
                        # you might want to parse each URL in the srcset individually
                        path_part = fixed_srcset.split(domain)[1] if domain in fixed_srcset else ''
                        if path_part:
                            path_part = path_part.lstrip('/')
                            local_img_path = project_root / domain / path_part
                            try:
                                rel_path = os.path.relpath(local_img_path, current_file_path.parent)
                                rel_path = rel_path.replace('\\', '/')
                                
                                # Update the srcset attribute
                                fixed_srcset = fixed_srcset.replace(f"{domain}/{path_part}", rel_path)
                                source['srcset'] = fixed_srcset
                                modified = True
                            except ValueError:
                                logger.warning(f"Could not compute relative path for srcset: {srcset}")
                
                if source.get('srcset') != srcset:
                    modified = True
    
    return modified


def fix_article_links(soup, current_file_path, project_root):
    """
    Convert wiki-style links to local relative paths
    """
    modified = False
    
    # Find all anchor tags with href attributes
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Handle wiki-style links (e.g., /ru/wiki/ArticleName)
        if href.startswith('/wiki/') or '/wiki/' in href:
            # Extract article name from URL
            if '/wiki/' in href:
                article_part = href.split('/wiki/', 1)[1].split('?')[0].split('#')[0]
                # Decode URL-encoded characters
                article_part = unquote(article_part)
                
                # Sanitize filename for filesystem
                # Replace invalid characters for filenames
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', article_part)
                
                # Add .html extension
                local_file = f"{safe_filename}.html"
                
                # Calculate relative path
                try:
                    # Look for the target file in the project
                    target_file = None
                    for root, dirs, files in os.walk(project_root):
                        for file in files:
                            if file == local_file or file.startswith(f"{safe_filename}_") or safe_filename in file:
                                target_file = Path(root) / file
                                break
                        if target_file:
                            break
                    
                    if target_file:
                        rel_path = os.path.relpath(target_file, current_file_path.parent)
                        rel_path = rel_path.replace('\\', '/')
                        
                        # Update the href attribute
                        link['href'] = rel_path
                        modified = True
                        logger.debug(f"Fixed article link: {href} -> {rel_path}")
                    else:
                        # If target file not found, could be an external link or missing page
                        logger.debug(f"Target file not found for link: {href}")
                        
                except ValueError:
                    logger.warning(f"Could not compute relative path for link: {href}")
        
        # Handle other relative links that might need adjustment
        elif href.startswith('/') and not any(domain in href for domain in IMAGE_DOMAINS):
            # These might be site-relative links that need to be converted
            # For now, we'll skip these unless they're clearly article links
            pass
    
    return modified


def rewrite_links(html_content, current_file_path):
    """
    Main function to rewrite both image paths and article links
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Import PROJECT_ROOT from config
    from postprocess.config import PROJECT_ROOT as project_root
    
    # Fix image paths
    img_modified = fix_image_paths(soup, current_file_path, project_root)
    
    # Fix article links
    link_modified = fix_article_links(soup, current_file_path, project_root)
    
    # Return modified content if any changes were made
    if img_modified or link_modified:
        return str(soup)
    else:
        return html_content