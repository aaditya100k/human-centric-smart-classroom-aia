from pathlib import Path
import re

html_dir = Path(r"c:\Users\HP\OneDrive\Desktop\human centric smart classroom monitoring system\frontend_refactored\html")

script_tag = '<script src="../js/page-handlers.js"></script>'

for html_file in html_dir.glob("*.html"):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    if "page-handlers.js" in content:
        continue

    # Insert page-handlers.js script tag before layout.js or before </head>
    if '<script src="../js/layout.js"></script>' in content:
        content = content.replace(
            '<script src="../js/layout.js"></script>',
            '<script src="../js/page-handlers.js"></script>\n<script src="../js/layout.js"></script>'
        )
    elif '</head>' in content:
        content = content.replace('</head>', f'{script_tag}\n</head>')

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)

print("Added page-handlers.js script tag to all HTML files!")
