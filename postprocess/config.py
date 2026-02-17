"""
Configuration module for Fandom mirror post-processing
"""
from pathlib import Path

# Project configuration
PROJECT_ROOT = Path(r"/workspace/test_mirror")  # Will be overridden by command line argument
BACKUP_ROOT = PROJECT_ROOT.parent / f"{PROJECT_ROOT.name}_backup"

# Classes and IDs to remove (advertising, navigation, tracking scripts)
REMOVE_SELECTORS = [
    "#global-navigation",
    "#fandom-bar", 
    ".ads-container",
    ".advertisement",
    ".cookie-policy",
    ".tracking-script",
    ".analytics",
    ".fandom-sticky-header",
    "#WikiaBar",
    ".wikia-ad",
    ".mobile-top-ad",
    ".leaderboard-wrapper",
    ".incontent-ad",
    ".video-ad",
    ".ad-slot",
    ".sponsored-content",
    ".affiliate-link",
    ".donate-module",
    ".social-media-widget",
    ".taboola",
    ".outbrain",
    ".share-element",
    ".print-footer",  # Remove print-specific footer
]

# Additional elements to remove
REMOVE_TAGS = [
    {"tag": "script", "attrs": {"src": ["google-analytics.com", "googletagmanager.com", "facebook.com", "twitter.com"]}},
    {"tag": "script", "attrs": {"type": "application/ld+json"}},  # Structured data we don't need
    {"tag": "link", "attrs": {"rel": "canonical"}},
    {"tag": "meta", "attrs": {"property": ["og:url", "og:type", "og:title", "og:description", "og:image", "og:site_name", "fb:app_id", "twitter:card", "twitter:site"]}},
]

# Image CDN domains to handle
IMAGE_DOMAINS = [
    "static.wikia.nocookie.net",
    "vignette.wikia.nocookie.net", 
    "images.wikia.nocookie.net",
    "static.fandom.com",
    "assets.fandom.com"
]

# File extensions for images
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']

# URL patterns to clean
CLEAN_URL_PATTERNS = [
    r'\?cb=\d+',  # Cache breaker
    r'\?format=\w+',  # Format parameter
    r'\?width=\d+',  # Width parameter
    r'\?height=\d+',  # Height parameter
    r'\/revision\/\w+',  # Revision paths
    r'\/scale-to-width-down\/\d+',  # Scale down
    r'\/scale-to-width\/\d+',  # Scale to width
    r'\/scale-to-height\/\d+',  # Scale to height
]