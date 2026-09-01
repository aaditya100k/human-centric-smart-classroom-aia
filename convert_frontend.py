from pathlib import Path
import re
import html

root = Path(r'c:/Users/HP/OneDrive/Desktop/human centric smart classroom monitoring system')
src_root = root / 'stitch_smart_classroom'
out_root = root / 'frontend_refactored'
out_html_dir = out_root / 'html'
out_css_dir = out_root / 'css'
out_html_dir.mkdir(parents=True, exist_ok=True)
out_css_dir.mkdir(parents=True, exist_ok=True)

src_files = sorted(src_root.rglob('*.html'))

for src in src_files:
    text = src.read_text(encoding='utf-8')
    css_rules = []
    style_blocks = re.findall(r'<style\b[^>]*>(.*?)</style>', text, flags=re.I | re.S)
    for block in style_blocks:
        content = block.strip()
        if content:
            css_rules.append(content)

    style_attr_pattern = re.compile(r'(<[^>]+)\sstyle=("|\')(.*?)\2([^>]*>)', re.S)
    style_map = {}

    def replace_style_attrs(match):
        prefix, quote, value, suffix = match.groups()
        decls = value.strip()
        if not decls:
            return match.group(0)
        if decls not in style_map:
            style_map[decls] = f'inline-style-{len(style_map) + 1}'
        class_name = style_map[decls]
        css_rules.append(f'.{class_name} {{ {decls} }}')
        class_match = re.search(r'\bclass=("|\')(.*?)\1', prefix)
        if class_match:
            updated_prefix = prefix.replace(
                class_match.group(0),
                f'class={class_match.group(1)}{class_match.group(2)} {class_name}{class_match.group(1)}',
                1,
            )
        else:
            updated_prefix = prefix + f' class="{class_name}"'
        return updated_prefix + suffix

    html_without_styles = re.sub(r'<style\b[^>]*>.*?</style>', '', text, flags=re.I | re.S)
    html_without_styles = style_attr_pattern.sub(replace_style_attrs, html_without_styles)

    css_content = '\n\n'.join(css_rules).strip() + '\n' if css_rules else ''

    name = src.parent.name
    html_name = f'{name}.html'
    css_name = f'{name}.css'
    html_out = out_html_dir / html_name
    css_out = out_css_dir / css_name

    if '</head>' in html_without_styles.lower():
        html_without_styles = re.sub(r'</head>', f'  <link rel="stylesheet" href="../css/{css_name}">\n</head>', html_without_styles, count=1, flags=re.I)
    else:
        html_without_styles = f'<link rel="stylesheet" href="../css/{css_name}">\n' + html_without_styles

    html_out.write_text(html_without_styles, encoding='utf-8')
    css_out.write_text(css_content, encoding='utf-8')

print(f'Created {len(src_files)} HTML/CSS pairs')
for p in sorted(out_html_dir.glob('*.html')):
    print(p.name)
