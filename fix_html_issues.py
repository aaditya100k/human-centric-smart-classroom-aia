import os
import re
from pathlib import Path

html_dir = Path(r"c:\Users\HP\OneDrive\Desktop\human centric smart classroom monitoring system\frontend_refactored\html")

font_link = '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300..800;1,300..800&family=Inter:ital,wght@0,300..900;1,300..900&family=Geist:wght@300..800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">'

def clean_main_class(cls_str):
    classes = cls_str.split()
    filtered = []
    for c in classes:
        if c.startswith('pt-') or c.startswith('md:pt-') or c.startswith('lg:pt-') or c.startswith('md:ml-'):
            continue
        filtered.append(c)
    return ' '.join(filtered)

def fix_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Clean duplicate font links
    pattern = r'(?:<link\s+href="https://fonts\.googleapis\.com[^\n]+>\s*){2,}'
    if re.search(pattern, content):
        content = re.sub(pattern, font_link + "\n", content)
    else:
        content = re.sub(r'<link\s+href="https://fonts\.googleapis\.com/css2\?family=Material\+Symbols\+Outlined[^\n]+>\s*', '', content)

    # 2. Fix main tag padding to avoid double top gap below navbar
    content = re.sub(
        r'<main([^>]*)class="([^"]*)"',
        lambda m: '<main' + m.group(1) + 'class="' + clean_main_class(m.group(2)) + '"',
        content
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def add_student_management_script():
    file_path = html_dir / "student_management_smart_classroom_ai.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "renderStudentsTable" in content:
        return

    script_code = """
<script>
function renderStudentsTable() {
    const tbody = document.getElementById("students-table-body");
    if (!tbody) return;

    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = (urlParams.get("search") || "").toLowerCase().trim();
    const deptFilter = (document.getElementById("dept-filter")?.value || "").toLowerCase();

    let students = DataAPI.getStudents();

    if (searchQuery) {
        students = students.filter(s => 
            s.name.toLowerCase().includes(searchQuery) ||
            s.id.toLowerCase().includes(searchQuery) ||
            s.email.toLowerCase().includes(searchQuery) ||
            s.dept.toLowerCase().includes(searchQuery) ||
            s.class.toLowerCase().includes(searchQuery)
        );
    }

    if (deptFilter) {
        students = students.filter(s => s.dept.toLowerCase() === deptFilter);
    }

    if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-8 text-center text-on-surface-variant">No student records match your search criteria.</td></tr>`;
        return;
    }

    tbody.innerHTML = students.map(s => `
        <tr class="hover:bg-white/5 transition-colors">
            <td class="px-6 py-4 flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center font-bold text-primary text-xs">${s.name.split(" ").map(n => n[0]).join("")}</div>
                <div>
                    <p class="font-bold text-sm text-on-surface">${s.name}</p>
                    <p class="text-xs text-on-surface-variant opacity-70">${s.id}</p>
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-on-surface-variant">${s.id}</td>
            <td class="px-6 py-4 text-sm text-on-surface-variant">${s.dept} (${s.class})</td>
            <td class="px-6 py-4 text-sm text-on-surface-variant">${s.email}</td>
            <td class="px-6 py-4 text-sm">
                <div class="flex items-center gap-2">
                    <div class="w-16 bg-white/10 rounded-full h-2 overflow-hidden">
                        <div class="bg-tertiary h-full rounded-full" style="width: ${s.attendance}%"></div>
                    </div>
                    <span class="font-bold text-xs text-tertiary">${s.attendance}%</span>
                </div>
            </td>
            <td class="px-6 py-4 text-sm">
                <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-tertiary/10 text-tertiary border border-tertiary/20">${s.status}</span>
            </td>
            <td class="px-6 py-4 text-sm text-right">
                <button class="p-1.5 text-on-surface-variant hover:text-error transition-colors" onclick="deleteStudent('${s.id}')">
                    <span class="material-symbols-outlined text-lg">delete</span>
                </button>
            </td>
        </tr>
    `).join("");
}

function deleteStudent(id) {
    if (confirm(`Are you sure you want to delete student ${id}?`)) {
        DataAPI.deleteStudent(id);
        renderStudentsTable();
    }
}

function openModal() {
    const modal = document.getElementById("addStudentModal");
    const container = document.getElementById("modalContainer");
    const backdrop = document.getElementById("modalBackdrop");
    if (modal) {
        modal.classList.remove("invisible");
        if (backdrop) backdrop.classList.remove("opacity-0");
        if (container) container.classList.remove("translate-x-full");
    }
}

function closeModal() {
    const modal = document.getElementById("addStudentModal");
    const container = document.getElementById("modalContainer");
    const backdrop = document.getElementById("modalBackdrop");
    if (container) container.classList.add("translate-x-full");
    if (backdrop) backdrop.classList.add("opacity-0");
    setTimeout(() => {
        if (modal) modal.classList.add("invisible");
    }, 300);
}

document.addEventListener("DOMContentLoaded", () => {
    renderStudentsTable();
    const deptFilter = document.getElementById("dept-filter");
    if (deptFilter) deptFilter.addEventListener("change", renderStudentsTable);
});
</script>
</body>
"""

    content = content.replace("</body>", script_code)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

for html_file in html_dir.glob("*.html"):
    fix_html_file(html_file)

add_student_management_script()
print("All HTML files fixed successfully!")
