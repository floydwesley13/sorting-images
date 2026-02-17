"""
Main orchestrator for Fandom mirror post-processing
"""
import os
import shutil
from pathlib import Path
from loguru import logger
import argparse

from postprocess.config import PROJECT_ROOT, BACKUP_ROOT
from postprocess.content_stabilizer import stabilize_content
from postprocess.html_cleaner import clean_html
from postprocess.link_rewriter import rewrite_links
from postprocess.utils import setup_logging


def create_backup():
    """Create backup of the original mirror"""
    if not BACKUP_ROOT.exists():
        shutil.copytree(PROJECT_ROOT, BACKUP_ROOT)
        logger.info(f"Backup created at {BACKUP_ROOT}")


def process_mirror():
    """Process the entire mirror"""
    logger.info(f"Starting post-processing of mirror at {PROJECT_ROOT}")
    
    # Process all HTML files
    html_files = list(PROJECT_ROOT.rglob("*.html"))
    logger.info(f"Found {len(html_files)} HTML files to process")
    
    for i, html_file in enumerate(html_files, 1):
        try:
            logger.info(f"Processing ({i}/{len(html_files)}): {html_file.relative_to(PROJECT_ROOT)}")
            
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Apply processing steps in order
            content = stabilize_content(content, html_file)
            content = clean_html(content)
            content = rewrite_links(content, html_file)
            
            # Write the processed content back
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.success(f"Processed: {html_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {html_file.name}: {e}")

    logger.info("Mirror post-processing completed!")


def main():
    parser = argparse.ArgumentParser(description="Post-process Fandom mirror downloaded with Offline Explorer")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--project-root", type=str, help="Path to the OE project Download folder")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Override project root if provided
    if args.project_root:
        global PROJECT_ROOT, BACKUP_ROOT
        PROJECT_ROOT = Path(args.project_root)
        BACKUP_ROOT = PROJECT_ROOT.parent / f"{PROJECT_ROOT.name}_backup"
    
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # Create backup unless skipped
    if not args.no_backup:
        create_backup()
    
    # Process the mirror
    process_mirror()


if __name__ == "__main__":
    main()