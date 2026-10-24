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
                # Log error or return empty
                print(f"Error parsing frontmatter in {filepath}: {e}")
                return {}, content
    
    return {}, content

def write_markdown_file(filepath: str, frontmatter: dict, body: str) -> None:
    """
    Writes frontmatter and body to an Obsidian markdown file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    fm_str = yaml.dump(frontmatter, sort_keys=False, default_flow_style=False, allow_unicode=True)
    content = f"---\n{fm_str}---\n\n{body}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_wikilinks(text: str) -> list[str]:
    """
    Extracts all wikilinks from a text string.
    e.g. [[SQL]] -> ['SQL']
    """
    return WIKILINK_RE.findall(text)

def create_wikilink(target: str, text: str = None) -> str:
    """
    Creates an Obsidian wiki-link.
    """
    if text:
        return f"[[{target}|{text}]]"
    return f"[[{target}]]"
