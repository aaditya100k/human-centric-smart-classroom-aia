#!/usr/bin/env python3
"""
Comprehensive responsive design update script
"""

from pathlib import Path
import re

root = Path(r'c:/Users/HP/OneDrive/Desktop/human centric smart classroom monitoring system')
html_dir = root / 'frontend_refactored' / 'html'
css_dir = root / 'frontend_refactored' / 'css'

# Updated Tailwind config for better sizing
TAILWIND_CONFIG = '''    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          "colors": {
            "tertiary-fixed": "#6bff8f",
            "on-secondary-fixed": "#07006c",
            "surface-variant": "#323537",
            "on-secondary-fixed-variant": "#2f2ebe",
            "on-error-container": "#ffdad6",
            "primary-container": "#4d8eff",
            "on-tertiary-fixed": "#002109",
            "primary-fixed": "#d8e2ff",
            "primary": "#adc6ff",
            "on-primary-fixed": "#001a42",
            "on-error": "#690005",
            "tertiary-container": "#00a74b",
            "surface-dim": "#101415",
            "inverse-on-surface": "#2d3133",
            "error": "#ffb4ab",
            "tertiary": "#4ae176",
            "on-surface": "#e0e3e5",
            "secondary-fixed": "#e1e0ff",
            "outline": "#8c909f",
            "secondary": "#c0c1ff",
            "secondary-container": "#3131c0",
            "surface-container-low": "#191c1e",
            "background": "#101415",
            "tertiary-fixed-dim": "#4ae176",
            "primary-fixed-dim": "#adc6ff",
            "on-tertiary": "#003915",
            "on-primary-container": "#00285d",
            "surface-container-lowest": "#0b0f10",
            "on-secondary": "#1000a9",
            "secondary-fixed-dim": "#c0c1ff",
            "on-tertiary-fixed-variant": "#005321",
            "outline-variant": "#424754",
            "inverse-primary": "#005ac2",
            "surface-container": "#1d2022",
            "on-primary-fixed-variant": "#004395",
            "surface": "#101415",
            "surface-container-high": "#272a2c",
            "on-surface-variant": "#c2c6d6",
            "on-primary": "#002e6a",
            "on-background": "#e0e3e5",
            "surface-tint": "#adc6ff",
            "on-tertiary-container": "#003111",
            "error-container": "#93000a",
            "surface-container-highest": "#323537",
            "inverse-surface": "#e0e3e5",
            "surface-bright": "#363a3b",
            "on-secondary-container": "#b0b2ff"
          },
          "borderRadius": {
            "DEFAULT": "0.25rem",
            "lg": "0.5rem",
            "xl": "0.75rem",
            "glass": "16px",
            "full": "9999px"
          },
          "spacing": {
            "stack-md": "1.2rem",
            "section-padding": "2rem",
            "gutter": "1.5rem",
            "stack-lg": "2rem",
            "stack-sm": "0.75rem",
            "margin-mobile": "1.25rem",
            "container-max": "100%"
          },
          "fontFamily": {
            "body-lg": ["Inter"],
            "headline-md": ["Plus Jakarta Sans"],
            "headline-lg-mobile": ["Plus Jakarta Sans"],
            "headline-xl": ["Plus Jakarta Sans"],
            "headline-lg": ["Plus Jakarta Sans"],
            "label-sm": ["Geist"],
            "body-md": ["Inter"]
          },
          "fontSize": {
            "body-lg": ["1.1rem", {"lineHeight": "1.6", "fontWeight": "400"}],
            "headline-md": ["1.75rem", {"lineHeight": "1.3", "fontWeight": "600"}],
            "headline-lg-mobile": ["2rem", {"lineHeight": "1.2", "fontWeight": "700"}],
            "headline-xl": ["3.5rem", {"lineHeight": "1.1", "letterSpacing": "-0.02em", "fontWeight": "800"}],
            "headline-lg": ["2.5rem", {"lineHeight": "1.2", "letterSpacing": "-0.01em", "fontWeight": "700"}],
            "label-sm": ["0.95rem", {"lineHeight": "1.0", "letterSpacing": "0.05em", "fontWeight": "500"}],
            "body-md": ["1rem", {"lineHeight": "1.6", "fontWeight": "400"}]
          }
        },
        "screens": {
          "sm": "640px",
          "md": "768px",
          "lg": "1024px",
          "xl": "1280px",
          "2xl": "1536px"
        }
      }
    }'''


def update_html_file(file_path):
    """Update HTML file with responsive improvements"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Update Tailwind config
    content = re.sub(
        r'tailwind\.config = \{[^}]*?"spacing"[^}]*?"container-max":[^}]*?\}[^}]*?"fontSize"[^}]*?\}\s*,\s*\},?\s*\}',
        TAILWIND_CONFIG,
        content,
        flags=re.DOTALL
    )
    
    # More flexible approach - replace the entire tailwind.config block
    tailwind_pattern = r'<script id="tailwind-config">(.*?)</script>'
    if re.search(tailwind_pattern, content, re.DOTALL):
        content = re.sub(
            tailwind_pattern,
            f'<script id="tailwind-config">\n{TAILWIND_CONFIG}\n  </script>',
            content,
            flags=re.DOTALL
        )
    
    # Update sidebar width in classes (if using md:ml-64, change to better responsive)
    content = re.sub(
        r'md:ml-64',
        'md:ml-60',
        content
    )
    
    # Update padding classes
    content = re.sub(
        r'\bpx-gutter\b',
        'px-4 md:px-6 lg:px-8',
        content
    )
    
    content = re.sub(
        r'\bpt-24\b',
        'pt-16 md:pt-20 lg:pt-24',
        content
    )
    
    # Improve grid layouts
    content = re.sub(
        r'grid-cols-1 md:grid-cols-3 lg:grid-cols-6',
        'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6',
        content
    )
    
    content = re.sub(
        r'grid-cols-1 lg:grid-cols-2',
        'grid-cols-1 md:grid-cols-2',
        content
    )
    
    content = re.sub(
        r'grid-cols-1 lg:grid-cols-3',
        'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
        content
    )
    
    # Add responsive link tag for responsive-system.css
    if '<link rel="stylesheet" href="../css/' in content and 'responsive-system.css' not in content:
        # Find the last CSS link and add responsive-system.css before it or after head opening
        head_close_pattern = r'</head>'
        if re.search(head_close_pattern, content):
            content = re.sub(
                r'</head>',
                '<link rel="stylesheet" href="../css/responsive-system.css">\n</head>',
                content
            )
    
    if content != original:
        return content
    return None


def update_css_file(file_path):
    """Update CSS file with responsive improvements"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Add responsive-system import at the beginning if not already there
    if '@import url' not in content or 'responsive-system' not in content:
        if not content.startswith('@import'):
            content = '@import url(\'./responsive-system.css\');\n\n' + content
    
    if content != original:
        return content
    return None


def main():
    print("=" * 60)
    print("UPDATING HTML AND CSS FILES FOR RESPONSIVE DESIGN")
    print("=" * 60)
    
    # Update HTML files
    print("\nUpdating HTML files...")
    html_files = sorted(html_dir.glob('*.html'))
    html_updated = 0
    
    for html_file in html_files:
        try:
            updated_content = update_html_file(html_file)
            if updated_content:
                html_file.write_text(updated_content, encoding='utf-8')
                html_updated += 1
                print(f"  ✓ Updated: {html_file.name}")
            else:
                print(f"  - No changes: {html_file.name}")
        except Exception as e:
            print(f"  ✗ Error: {html_file.name} - {str(e)}")
    
    print(f"\nUpdated {html_updated}/{len(html_files)} HTML files")
    
    # Update CSS files
    print("\nUpdating CSS files...")
    css_files = sorted(css_dir.glob('*.css'))
    css_updated = 0
    
    for css_file in css_files:
        # Skip responsive-system.css itself
        if 'responsive-system' in css_file.name:
            print(f"  - Skipped: {css_file.name} (system file)")
            continue
        
        try:
            updated_content = update_css_file(css_file)
            if updated_content:
                css_file.write_text(updated_content, encoding='utf-8')
                css_updated += 1
                print(f"  ✓ Updated: {css_file.name}")
            else:
                print(f"  - No changes: {css_file.name}")
        except Exception as e:
            print(f"  ✗ Error: {css_file.name} - {str(e)}")
    
    print(f"\nUpdated {css_updated}/{len(css_files) - 1} CSS files")
    print("\n" + "=" * 60)
    print("RESPONSIVE DESIGN UPDATE COMPLETE!")
    print("=" * 60)


if __name__ == '__main__':
    main()
