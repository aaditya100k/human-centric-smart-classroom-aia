#!/usr/bin/env python3
"""
Script to fix duplicated content in HTML and CSS files
"""

from pathlib import Path
import re

root = Path(r'c:/Users/HP/OneDrive/Desktop/human centric smart classroom monitoring system')
html_dir = root / 'frontend_refactored' / 'html'
css_dir = root / 'frontend_refactored' / 'css'

def fix_css_file(file_path):
    """Remove duplicate CSS content and inline-style definitions"""
    content = file_path.read_text(encoding='utf-8')
    
    # Split by @import to handle multiple imports
    parts = content.split('@import')
    
    if len(parts) <= 1:
        # No duplication issues
        return content
    
    # Keep first import and process the rest
    fixed_parts = []
    seen_parts = set()
    
    for i, part in enumerate(parts):
        if i == 0:
            # First part (before any @import)
            fixed_parts.append(part)
        else:
            # Normalize the part to detect duplicates
            normalized = part.strip()
            if normalized and normalized not in seen_parts:
                fixed_parts.append('@import' + part)
                seen_parts.add(normalized)
    
    result = ''.join(fixed_parts)
    
    # Remove duplicate inline-style definitions
    # Find all .inline-style-N { ... } definitions
    pattern = r'\.inline-style-(\d+)\s*\{\s*([^}]+)\s*\}'
    matches = list(re.finditer(pattern, result))
    
    seen_styles = {}
    lines_to_remove = set()
    
    for match in matches:
        style_num = match.group(1)
        style_content = match.group(2).strip()
        key = (style_num, style_content)
        
        if key in seen_styles:
            # Mark this match for removal
            lines_to_remove.add(match.span())
        else:
            seen_styles[key] = match.span()
    
    # Remove duplicate inline-style definitions by reconstructing
    if lines_to_remove:
        result_lines = result.split('\n')
        result_text = result
        
        # Remove duplicate definitions - simpler approach
        lines = result.split('\n')
        cleaned_lines = []
        seen_inline_styles = {}
        
        for line in lines:
            # Check if this is an inline-style definition
            inline_match = re.match(r'\.inline-style-(\d+)\s*\{\s*(.+)\s*\}', line.strip())
            if inline_match:
                style_key = (inline_match.group(1), inline_match.group(2).strip())
                if style_key not in seen_inline_styles:
                    cleaned_lines.append(line)
                    seen_inline_styles[style_key] = True
            else:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
    
    # Remove consecutive blank lines
    result = re.sub(r'\n\n\n+', '\n\n', result)
    
    return result.strip() + '\n'


def fix_html_file(file_path):
    """Remove duplicate head sections and fix malformed tags"""
    content = file_path.read_text(encoding='utf-8')
    
    # Fix incomplete SVG tag pattern: <svg class="inline-defs-container" a
    content = re.sub(r'<svg\s+class="inline-defs-container"\s+a', '<svg class="inline-defs-container"', content)
    
    # Remove multiple <head> sections - keep only the first complete one
    head_pattern = r'<head>(.*?)</head>'
    head_matches = list(re.finditer(head_pattern, content, re.IGNORECASE | re.DOTALL))
    
    if len(head_matches) > 1:
        # Multiple head sections found
        first_head = head_matches[0]
        # Keep the first head, remove others
        heads_to_remove = head_matches[1:]
        
        # Build the fixed content
        result = content[:first_head.end()]
        last_pos = first_head.end()
        
        for head_match in heads_to_remove:
            # Add content before this head
            result += content[last_pos:head_match.start()]
            # Skip this head section
            last_pos = head_match.end()
        
        # Add remaining content
        result += content[last_pos:]
        content = result
    
    # Remove duplicate <meta content="viewport"> tags
    meta_viewport_pattern = r'<meta\s+(?:content|name)=["\']width=device-width["\'].*?>'
    metas = list(re.finditer(meta_viewport_pattern, content, re.IGNORECASE | re.DOTALL))
    if len(metas) > 1:
        # Keep first, remove subsequent
        seen_positions = set()
        for meta in metas[1:]:
            seen_positions.add((meta.start(), meta.end()))
        
        # Reconstruct without duplicates
        result = []
        last_end = 0
        for meta in metas:
            if (meta.start(), meta.end()) not in seen_positions or meta == metas[0]:
                result.append(content[last_end:meta.start()])
                if meta == metas[0] or (meta.start(), meta.end()) not in seen_positions:
                    result.append(content[meta.start():meta.end()])
                last_end = meta.end()
            else:
                # Skip this duplicate
                pass
        result.append(content[last_end:])
        content = ''.join(result)
    
    # Remove duplicate title tags
    title_pattern = r'<title>([^<]+)</title>'
    titles = list(re.finditer(title_pattern, content, re.IGNORECASE))
    if len(titles) > 1:
        # Keep first title, remove others
        result = content[:titles[0].end()]
        last_pos = titles[0].end()
        
        for title in titles[1:]:
            result += content[last_pos:title.start()]
            last_pos = title.end()
        
        result += content[last_pos:]
        content = result
    
    # Remove duplicate tailwind config scripts
    script_pattern = r'<script\s+id=["\']tailwind-config["\'][^>]*>.*?</script>'
    scripts = list(re.finditer(script_pattern, content, re.IGNORECASE | re.DOTALL))
    if len(scripts) > 1:
        # Keep first, remove others
        result = content[:scripts[0].end()]
        last_pos = scripts[0].end()
        
        for script in scripts[1:]:
            result += content[last_pos:script.start()]
            last_pos = script.end()
        
        result += content[last_pos:]
        content = result
    
    return content.strip() + '\n'


def main():
    print("Fixing CSS files...")
    css_files = sorted(css_dir.glob('*.css'))
    css_fixed = 0
    
    for css_file in css_files:
        original = css_file.read_text(encoding='utf-8')
        fixed = fix_css_file(css_file)
        
        if fixed != original:
            css_file.write_text(fixed, encoding='utf-8')
            css_fixed += 1
            print(f"  ✓ Fixed: {css_file.name}")
        else:
            print(f"  - No changes: {css_file.name}")
    
    print(f"\nFixed {css_fixed} CSS files")
    
    print("\nFixing HTML files...")
    html_files = sorted(html_dir.glob('*.html'))
    html_fixed = 0
    
    for html_file in html_files:
        original = html_file.read_text(encoding='utf-8')
        fixed = fix_html_file(html_file)
        
        if fixed != original:
            html_file.write_text(fixed, encoding='utf-8')
            html_fixed += 1
            print(f"  ✓ Fixed: {html_file.name}")
        else:
            print(f"  - No changes: {html_file.name}")
    
    print(f"\nFixed {html_fixed} HTML files")
    print(f"\nTotal files fixed: {css_fixed + html_fixed}")


if __name__ == '__main__':
    main()
