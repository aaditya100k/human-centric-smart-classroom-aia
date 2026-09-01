#!/usr/bin/env python3
"""
Advanced CSS enhancement for better component sizing and responsiveness
"""

from pathlib import Path

root = Path(r'c:/Users/HP/OneDrive/Desktop/human centric smart classroom monitoring system')
css_dir = root / 'frontend_refactored' / 'css'

# Enhanced CSS additions for better sizing
ENHANCED_CSS = '''
/* ========================================
   SIDEBAR ENHANCEMENTS
   ======================================== */

aside {
  width: 260px;
  min-width: 260px;
}

aside h1,
aside .text-2xl,
aside [class*="headline"] {
  font-size: 1.4rem;
  margin-bottom: 1rem;
}

aside p,
aside .text-sm {
  font-size: 0.95rem;
}

nav a {
  font-size: 1rem;
  padding: 0.9rem 1rem;
  gap: 1rem;
}

nav a span.material-symbols-outlined {
  font-size: 1.4rem;
  min-width: 1.4rem;
}

/* ========================================
   HEADER ENHANCEMENTS
   ======================================== */

header {
  padding: 0 1.5rem;
  height: 70px;
}

header input,
header .font-label-sm {
  font-size: 1rem;
}

header button {
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  height: 44px;
}

/* ========================================
   CARD SIZING
   ======================================== */

.glass-card {
  padding: 1.5rem;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.glass-card h3,
.glass-card .font-headline-md {
  font-size: 1.8rem;
  margin: 0.5rem 0 0 0;
}

.glass-card .font-label-sm,
.glass-card .text-sm {
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.glass-card .material-symbols-outlined {
  font-size: 1.8rem;
  min-width: 1.8rem;
}

.glass-card .inline-style-5,
.glass-card .inline-style-6,
.glass-card .inline-style-7,
.glass-card .inline-style-8 {
  min-height: 8px;
}

/* ========================================
   BUTTON SIZING
   ======================================== */

button,
.primary-gradient,
[class*="btn"],
input[type="button"],
input[type="submit"] {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  height: 44px;
  border-radius: 8px;
}

button .material-symbols-outlined,
.primary-gradient .material-symbols-outlined {
  font-size: 1.3rem;
}

/* ========================================
   TABLE ENHANCEMENTS
   ======================================== */

table {
  font-size: 1rem;
}

th {
  padding: 1.2rem;
  font-size: 1.05rem;
  font-weight: 600;
}

td {
  padding: 1.2rem;
  font-size: 1rem;
}

tr:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}

/* ========================================
   FORM ELEMENTS
   ======================================== */

input,
textarea,
select {
  padding: 0.9rem 1rem;
  font-size: 1rem;
  height: 44px;
  border-radius: 8px;
}

textarea {
  height: auto;
  min-height: 100px;
}

label {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  display: block;
}

/* ========================================
   TYPOGRAPHY OVERRIDES
   ======================================== */

h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  margin-bottom: 1.5rem;
}

h2 {
  font-size: clamp(1.75rem, 3.5vw, 2.5rem);
  margin-bottom: 1.2rem;
}

h3 {
  font-size: clamp(1.5rem, 3vw, 2rem);
  margin-bottom: 1rem;
}

h4 {
  font-size: clamp(1.25rem, 2.5vw, 1.75rem);
  margin-bottom: 0.8rem;
}

p {
  font-size: 1rem;
  line-height: 1.7;
}

/* ========================================
   CHART & GRAPH SIZING
   ======================================== */

canvas {
  max-height: 450px;
  min-height: 250px;
}

.h-64 {
  height: 400px;
}

.h-96 {
  height: 500px;
}

.relative.h-96 {
  height: 400px;
}

/* ========================================
   MODAL & DIALOG SIZING
   ======================================== */

.modal,
.dialog,
[role="dialog"] {
  max-width: 600px;
  padding: 2rem;
}

.modal h2,
.dialog h2 {
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
}

/* ========================================
   RESPONSIVE OVERRIDES
   ======================================== */

@media (max-width: 768px) {
  aside {
    width: 100%;
    height: auto;
    position: relative;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  header {
    width: 100%;
    position: relative;
    top: auto;
    height: auto;
    padding: 1rem;
    margin-top: 1rem;
  }

  main {
    margin-left: 0;
    margin-top: 0;
    padding: 1rem;
  }

  .glass-card {
    padding: 1.2rem;
  }

  table {
    font-size: 0.95rem;
  }

  th, td {
    padding: 0.8rem;
  }

  button {
    width: 100%;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  aside {
    width: 220px;
  }

  header {
    width: calc(100% - 220px);
  }

  main {
    margin-left: 220px;
  }
}

@media (min-width: 1025px) {
  aside {
    width: 260px;
  }

  header {
    width: calc(100% - 260px);
  }

  main {
    margin-left: 260px;
  }

  .glass-card {
    min-height: 140px;
  }
}

@media (min-width: 1366px) {
  .glass-card {
    min-height: 160px;
  }

  h1 {
    font-size: 2.8rem;
  }

  h2 {
    font-size: 2.2rem;
  }

  h3 {
    font-size: 1.8rem;
  }

  p {
    font-size: 1.05rem;
  }
}

@media (min-width: 1920px) {
  aside {
    width: 280px;
  }

  header {
    width: calc(100% - 280px);
    height: 80px;
  }

  main {
    margin-left: 280px;
    padding: 2rem;
  }

  .glass-card {
    padding: 2rem;
    min-height: 180px;
  }

  h1 {
    font-size: 3rem;
  }

  h2 {
    font-size: 2.4rem;
  }

  h3 {
    font-size: 2rem;
  }

  p {
    font-size: 1.1rem;
  }

  canvas {
    max-height: 500px;
    min-height: 300px;
  }

  table {
    font-size: 1.05rem;
  }

  th, td {
    padding: 1.4rem;
  }

  button {
    font-size: 1.05rem;
    height: 48px;
    padding: 0.8rem 2rem;
  }
}

/* ========================================
   GRID & LAYOUT IMPROVEMENTS
   ======================================== */

.grid {
  gap: 1.5rem;
}

.gap-stack-md {
  gap: 1.2rem;
}

.gap-stack-lg {
  gap: 1.8rem;
}

.gap-gutter {
  gap: 1.5rem;
}

/* ========================================
   SPACING UTILITIES
   ======================================== */

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-8 {
  margin-bottom: 2rem;
}

.mt-6 {
  margin-top: 1.5rem;
}

.mt-8 {
  margin-top: 2rem;
}

.p-6 {
  padding: 1.5rem;
}

.p-8 {
  padding: 2rem;
}

.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.py-6 {
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

/* ========================================
   STATUS CHIP SIZING
   ======================================== */

.status-chip {
  padding: 0.6rem 1rem;
  border-radius: 20px;
  font-size: 0.95rem;
  font-weight: 600;
}

.px-3,
.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}

.py-1,
.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

/* ========================================
   ICON SIZING
   ======================================== */

.text-\[20px\] {
  font-size: 1.5rem;
}

.text-\[24px\] {
  font-size: 1.75rem;
}

.text-\[32px\] {
  font-size: 2rem;
}

/* ========================================
   SPACING FIX FOR MAIN CONTENT
   ======================================== */

main > section {
  margin-bottom: 2rem;
}

main > section > div {
  margin-bottom: 1.5rem;
}
'''

def enhance_css_files():
    """Add enhanced CSS to all CSS files"""
    print("Enhancing CSS files with better component sizing...")
    
    css_files = sorted(css_dir.glob('*.css'))
    enhanced_count = 0
    
    for css_file in css_files:
        # Skip responsive-system as it's already comprehensive
        if 'responsive-system' in css_file.name:
            continue
        
        content = css_file.read_text(encoding='utf-8')
        
        # Check if already enhanced
        if 'SIDEBAR ENHANCEMENTS' in content:
            print(f"  - Already enhanced: {css_file.name}")
            continue
        
        # Add enhanced CSS at the end
        new_content = content + '\n\n' + ENHANCED_CSS
        css_file.write_text(new_content, encoding='utf-8')
        enhanced_count += 1
        print(f"  ✓ Enhanced: {css_file.name}")
    
    return enhanced_count


if __name__ == '__main__':
    print("=" * 60)
    print("ENHANCING CSS FOR BETTER COMPONENT SIZING")
    print("=" * 60)
    print()
    
    enhanced = enhance_css_files()
    
    print()
    print("=" * 60)
    print(f"Enhanced {enhanced} CSS files")
    print("=" * 60)
