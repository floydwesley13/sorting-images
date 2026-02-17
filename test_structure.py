#!/usr/bin/env python3
"""
Test script to analyze the structure of a Fandom mirror
"""
import os
from pathlib import Path


def analyze_mirror_structure(mirror_path):
    """
    Analyze the structure of a Fandom mirror downloaded with Offline Explorer
    """
    mirror_path = Path(mirror_path)
    
    print(f"Analyzing mirror structure at: {mirror_path}")
    print("="*50)
    
    # List top-level directories
    print("Top-level directories:")
    for item in mirror_path.iterdir():
        if item.is_dir():
            print(f"  - {item.name}/")
    print()
    
    # Look for common Fandom structures
    fandom_dirs = []
    static_dirs = []
    
    for item in mirror_path.iterdir():
        if item.is_dir():
            if any(subdomain in item.name for subdomain in ['fandom.com', 'wikia.nocookie.net', 'wikia.com']):
                fandom_dirs.append(item.name)
            elif any(cdndomain in item.name for cdndomain in ['static.', 'vignette.', 'images.', 'assets.']):
                static_dirs.append(item.name)
    
    if fandom_dirs:
        print("Potential Fandom content directories:")
        for dir_name in fandom_dirs:
            print(f"  - {dir_name}")
            # Show some sample files
            content_files = list(Path(mirror_path / dir_name).rglob("*.html"))[:5]  # First 5 HTML files
            for file_path in content_files:
                print(f"    * {file_path.relative_to(mirror_path / dir_name)}")
        print()
    
    if static_dirs:
        print("Potential static asset directories (images, CSS, JS):")
        for dir_name in static_dirs:
            print(f"  - {dir_name}")
            # Count file types
            ext_count = {}
            for file_path in Path(mirror_path / dir_name).rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    ext_count[ext] = ext_count.get(ext, 0) + 1
            # Show top file extensions
            sorted_exts = sorted(ext_count.items(), key=lambda x: x[1], reverse=True)[:5]
            for ext, count in sorted_exts:
                print(f"    * {ext}: {count} files")
        print()
    
    # Analyze HTML file structure
    html_files = list(mirror_path.rglob("*.html"))
    print(f"Total HTML files found: {len(html_files)}")
    
    # Sample a few HTML files to check their content
    print("\nSample HTML file analysis:")
    for i, html_file in enumerate(html_files[:3]):  # Analyze first 3 files
        print(f"\nFile {i+1}: {html_file.relative_to(mirror_path)}")
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 chars
                
            # Check for common Fandom elements
            checks = {
                'Fandom/Wikia references': any(x in content for x in ['fandom.com', 'wikia.nocookie.net', 'Wikia']),
                'CDN image links': any(domain in content for domain in ['static.wikia.nocookie.net', 'vignette.wikia.nocookie.net']),
                'Lazy loading': any(attr in content for attr in ['data-src', 'data-lazy-src', 'loading=']),
                'Infoboxes/collapsible': any(cls in content for cls in ['infobox', 'mw-collapsible', 'collapsible'])
            }
            
            for check, found in checks.items():
                status = "✓" if found else "✗"
                print(f"  {status} {check}")
                
        except Exception as e:
            print(f"  Error reading file: {e}")
    
    # Analyze image file extensions
    print(f"\nImage file extensions found in entire mirror:")
    image_extensions = {}
    for file_path in mirror_path.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                image_extensions[ext] = image_extensions.get(ext, 0) + 1
    
    for ext, count in sorted(image_extensions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ext}: {count} files")


if __name__ == "__main__":
    # Default path - this would need to be updated to point to an actual mirror
    MIRROR_PATH = "/workspace/mirror_root"  # Placeholder
    
    if Path(MIRROR_PATH).exists():
        analyze_mirror_structure(MIRROR_PATH)
    else:
        print(f"Mirror path {MIRROR_PATH} does not exist.")
        print("Creating a sample structure for testing...")
        
        # Create sample structure for testing
        sample_mirror = Path("/workspace/sample_fandom_mirror")
        sample_mirror.mkdir(exist_ok=True)
        
        # Create content directory
        content_dir = sample_mirror / "fallout.fandom.com"
        content_dir.mkdir(exist_ok=True)
        
        # Create static assets directory
        static_dir = sample_mirror / "static.wikia.nocookie.net"
        static_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for images
        (static_dir / "fallout_gamepedia").mkdir(exist_ok=True)
        (static_dir / "images").mkdir(exist_ok=True)
        
        # Create a sample HTML file
        sample_html = content_dir / "Vault_Boy.html"
        sample_html.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>Vault Boy - Fallout Wiki</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Vault Boy</h1>
    <img data-src="https://static.wikia.nocookie.net/fallout_gamepedia/images/vault_boy.png?cb=12345" 
         src="placeholder.jpg" 
         alt="Vault Boy" 
         class="lazyload">
    <div class="mw-collapsible">
        <div class="mw-collapsible-content" style="display: none;">
            <p>This is collapsible content.</p>
        </div>
    </div>
    <p>Check out the <a href="/wiki/Nuka_Cola">Nuka Cola</a> article.</p>
</body>
</html>
        """)
        
        # Create a sample image file
        sample_img = static_dir / "fallout_gamepedia" / "vault_boy.png"
        sample_img.write_bytes(b"fake png content")
        
        print(f"Sample structure created at {sample_mirror}")
        analyze_mirror_structure(sample_mirror)