#!/usr/bin/env python3
"""
Comprehensive fix for duplicated content in HTML and CSS files
"""

from pathlib import Path
import re

root = Path(r'c:/Users/HP/OneDrive/Desktop/human centric smart classroom monitoring system')
html_dir = root / 'frontend_refactored' / 'html'
css_dir = root / 'frontend_refactored' / 'css'


def fix_css_file(file_path):
    """Remove duplicate CSS content and inline-style definitions"""
    content = file_path.read_text(encoding='utf-8')
    
    # Find all major blocks (imports, rules, etc.)
    lines = content.split('\n')
    seen_content = {}
    result_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check for @import statements
        if stripped.startswith('@import'):
            if stripped not in seen_content:
                result_lines.append(line)
                seen_content[stripped] = True
            i += 1
        # Check for CSS rules - need to collect the full rule
        elif stripped and '{' in stripped and '}' in stripped:
            # Single line rule
            if stripped not in seen_content:
                result_lines.append(line)
                seen_content[stripped] = True
            i += 1
        elif stripped and '{' in stripped:
            # Multi-line rule - collect until }
            rule_lines = [line]
            i += 1
            brace_count = stripped.count('{') - stripped.count('}')
            
            while i < len(lines) and brace_count > 0:
                rule_lines.append(lines[i])
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            
            # Normalize the rule for comparison
            rule_text = '\n'.join(rule_lines).strip()
            rule_key = re.sub(r'\s+', ' ', rule_text)  # Normalize whitespace
            
            if rule_key not in seen_content:
                result_lines.extend(rule_lines)
                seen_content[rule_key] = True
        else:
            # Empty line or comment
            if stripped or not result_lines or result_lines[-1].strip():  # Keep one empty line
                result_lines.append(line)
            i += 1
    
    result = '\n'.join(result_lines)
    
    # Clean up excessive blank lines
    result = re.sub(r'\n\n\n+', '\n\n', result)
    
    return result.strip() + '\n'


def fix_html_file(file_path):
    """Remove duplicate head sections and fix malformed tags"""
    content = file_path.read_text(encoding='utf-8')
    
    # Extract the head section
    head_match = re.search(r'<head>(.*?)</head>', content, re.IGNORECASE | re.DOTALL)
    body_match = re.search(r'<body[^>]*>(.*)', content, re.IGNORECASE | re.DOTALL)
    
    if not head_match:
        return content
    
    head_content = head_match.group(1)
    
    # Clean up duplicate items in head
    head_lines = head_content.split('\n')
    seen_lines = {}
    clean_head_lines = []
    
    for line in head_lines:
        normalized = line.strip()
        if not normalized:
            # Keep empty lines but not consecutive ones
            if clean_head_lines and clean_head_lines[-1].strip():
                clean_head_lines.append(line)
        else:
            # Create a key for comparison (ignoring exact whitespace)
            key = re.sub(r'\s+', ' ', normalized)
            
            if key not in seen_lines:
                clean_head_lines.append(line)
                seen_lines[key] = True
    
    clean_head = '\n'.join(clean_head_lines)
    
    # Remove duplicate title tags within head
    clean_head = re.sub(r'(<title>[^<]+</title>)\s*\1+', r'\1', clean_head, flags=re.IGNORECASE)
    
    # Remove duplicate meta viewport tags
    viewport_match = re.search(r'(<meta[^>]*viewport[^>]*>)', clean_head, re.IGNORECASE)
    if viewport_match:
        clean_head = re.sub(
            r'<meta[^>]*viewport[^>]*>',
            viewport_match.group(1),
            clean_head,
            flags=re.IGNORECASE
        )
    
    # Reconstruct the document
    if body_match:
        body_start = body_match.start()
        body_content = body_match.group(0)
        
        # Clean up body content - remove duplicate meta tags and scripts that shouldn't be there
        body_content = re.sub(r'<meta[^>]*>', '', body_content, flags=re.IGNORECASE)
        body_content = re.sub(r'<title>[^<]+</title>', '', body_content, flags=re.IGNORECASE)
        body_content = re.sub(
            r'<script[^>]*(?:id=["\']tailwind-config["\'])?[^>]*>.*?</script>',
            '',
            body_content,
            flags=re.IGNORECASE | re.DOTALL,
            count=1
        )
        body_content = re.sub(r'<link[^>]*(?:fonts\.googleapis|tailwind)[^>]*>', '', body_content, flags=re.IGNORECASE)
        
        # Fix incomplete tags
        body_content = re.sub(
            r'<svg\s+class="inline-defs-container"\s+[^>]*$',
            '<svg class="inline-defs-container"></svg>',
            body_content,
            flags=re.IGNORECASE | re.MULTILINE
        )
        
        result = f'<!DOCTYPE html>\n<html{content[9:body_start].replace("<html", "").replace(">", "", 1).rstrip()}>\n<head>\n{clean_head}\n</head>\n{body_content}'
    else:
        result = f'<!DOCTYPE html>\n<html>\n<head>\n{clean_head}\n</head>\n</html>'
    
    return result.strip() + '\n'


def main():
    print("Performing comprehensive fix on CSS files...")
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
    
    print("\nPerforming comprehensive fix on HTML files...")
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
