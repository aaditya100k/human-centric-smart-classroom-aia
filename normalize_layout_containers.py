from pathlib import Path
import re

html_dir = Path(r"c:\Users\HP\OneDrive\Desktop\human centric smart classroom monitoring system\frontend_refactored\html")

app_pages = [
    "attendance_smart_classroom_ai.html",
    "classroom_management_smart_classroom_ai.html",
    "emotion_analytics_smart_classroom_ai.html",
    "live_monitoring_smart_classroom_ai.html",
    "notifications_alerts_smart_classroom_ai.html",
    "reports_analytics_smart_classroom_ai.html",
    "settings_smart_classroom_ai.html",
    "smart_classroom_ai_dashboard.html",
    "student_management_smart_classroom_ai.html"
]

for page_name in app_pages:
    file_path = html_dir / page_name
    if not file_path.exists():
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace hardcoded <aside ...> ... </aside> with <aside id="layout-sidebar"></aside>
    content = re.sub(
        r'<aside[^>]*>.*?</aside>',
        '<aside id="layout-sidebar"></aside>',
        content,
        flags=re.DOTALL
    )

    # Replace hardcoded <header ...> ... </header> (if not layout-navbar) with <header id="layout-navbar"></header>
    content = re.sub(
        r'<header(?![^>]*id="layout-navbar")[^>]*>.*?</header>',
        '<header id="layout-navbar"></header>',
        content,
        flags=re.DOTALL
    )

    # Ensure main tag has no pt- / ml- hardcoded inline classes
    content = re.sub(
        r'<main\s+class="[^"]*"',
        '<main class="px-4 md:px-6 lg:px-8 pb-6"',
        content
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Normalized layout containers across app pages!")
