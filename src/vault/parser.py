import os
import re
import yaml

WIKILINK_RE = re.compile(r'\[\[(.*?)\]\]')

def parse_markdown_file(filepath: str) -> tuple[dict, str]:
    """
    Parses an Obsidian markdown file.
    Returns a tuple of (frontmatter_dict, body_content_str).
    """
    if not os.path.exists(filepath):
        return {}, ""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm_data = yaml.safe_load(parts[1]) or {}
                body = parts[2].lstrip()
                return fm_data, body
            except Exception as e:
