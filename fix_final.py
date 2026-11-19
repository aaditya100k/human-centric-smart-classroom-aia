#!/usr/bin/env python3
"""
Final targeted fix for remaining issues
"""

import sys
from pathlib import Path
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

root = Path(r'c:/Users/HP/OneDrive/Desktop/human centric smart classroom monitoring system')
html_dir = root / 'frontend_refactored' / 'html'
css_dir = root / 'frontend_refactored' / 'css'


def fix_remaining_issues():
    """Fix specific remaining issues in files"""
    
    # Fix HTML files
    print("Fixing remaining HTML issues...")
    for html_file in sorted(html_dir.glob('*.html')):
        content = html_file.read_text(encoding='utf-8')
        original = content
        
        # Fix <html html pattern
        content = re.sub(r'<html\s+html\s+', '<html ', content, flags=re.IGNORECASE)
        content = re.sub(r'<html\s+html\s*>', '<html>', content, flags=re.IGNORECASE)
        
        # Fix duplicate attributes in html tag
        html_match = re.match(r'<!DOCTYPE html>\s*<html([^>]*)>', content, re.IGNORECASE)
        if html_match:
            attrs = html_match.group(1)
            # Remove duplicate attributes
            attr_dict = {}
            for attr in re.findall(r'(\w+)=(["\'])([^"\']*)\2', attrs):
                key = attr[0].lower()
                if key not in attr_dict:
                    attr_dict[key] = (attr[0], attr[1], attr[2])
            
            if len(attr_dict) != len(re.findall(r'\w+=["\'][^"\']*["\']', attrs)):
                new_attrs = ' '.join(
                    f'{key}={quote}{val}{quote}'
                    for key, (orig_key, quote, val) in attr_dict.items()
                )
                if new_attrs:
                    content = re.sub(
                        r'<!DOCTYPE html>\s*<html[^>]*>',
                        f'<!DOCTYPE html>\n<html {new_attrs}>',
                        content,
                        flags=re.IGNORECASE
                    )
                else:
                    content = re.sub(
                        r'<!DOCTYPE html>\s*<html[^>]*>',
                        '<!DOCTYPE html>\n<html>',
                        content,
                        flags=re.IGNORECASE
                    )
        
        if content != original:
            html_file.write_text(content, encoding='utf-8')
            print(f"  ✓ Fixed: {html_file.name}")
        else:
            print(f"  - No changes: {html_file.name}")
    
    # Fix CSS files - remove duplicate comments and normalize
    print("\nFixing remaining CSS issues...")
    for css_file in sorted(css_dir.glob('*.css')):
        content = css_file.read_text(encoding='utf-8')
        original = content
        
        # Remove duplicate comments
        lines = content.split('\n')
        result_lines = []
        seen_comments = set()
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('/*') and stripped.endswith('*/'):
                # Single line comment
                if stripped not in seen_comments:
                    result_lines.append(line)
                    seen_comments.add(stripped)
            else:
                result_lines.append(line)
        
        content = '\n'.join(result_lines)
        
        if content != original:
            css_file.write_text(content, encoding='utf-8')
            print(f"  ✓ Fixed: {css_file.name}")
        else:
            print(f"  - No changes: {css_file.name}")


if __name__ == '__main__':
    fix_remaining_issues()
    print("\n✓ All fixes complete!")
