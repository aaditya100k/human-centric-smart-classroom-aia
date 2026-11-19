// Comprehensive Page Handlers & Interactivity Controller

document.addEventListener("DOMContentLoaded", () => {
    initGlobalToasts();
    initDashboardPage();
    initClassroomPage();
    initAttendancePage();
    initEmotionPage();
    initReportsPage();
    initNotificationsPage();
    initSettingsPage();
    initLandingPage();
});

// ==========================================
// 1. GLOBAL TOAST & EXPORT UTILITIES
// ==========================================

function initGlobalToasts() {
    if (!document.getElementById("toast-container")) {
        const container = document.createElement("div");
        container.id = "toast-container";
        container.className = "fixed bottom-5 right-5 z-[200] flex flex-col gap-3 pointer-events-none";
        document.body.appendChild(container);
    }
}

function showToast(message, type = "success") {
    const container = document.getElementById("toast-container") || document.body;
    const toast = document.createElement("div");
    
    const icon = type === "success" ? "check_circle" : (type === "error" ? "error" : "info");
    const borderColor = type === "success" ? "border-tertiary/40" : (type === "error" ? "border-error/40" : "border-primary/40");
    const textColor = type === "success" ? "text-tertiary" : (type === "error" ? "text-error" : "text-primary");

    toast.className = `pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-2xl bg-surface/90 backdrop-blur-xl border ${borderColor} shadow-2xl transition-all duration-300 transform translate-y-4 opacity-0 max-w-sm`;
    toast.innerHTML = `
        <span class="material-symbols-outlined ${textColor}">${icon}</span>
        <p class="text-sm font-medium text-on-surface leading-tight">${message}</p>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove("translate-y-4", "opacity-0");
    }, 10);

    setTimeout(() => {
        toast.classList.add("opacity-0", "translate-y-2");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function exportToCSV(filename, rows) {
    const processRow = (row) => row.map(val => `"${String(val).replace(/"/g, '""')}"`).join(",");
    const csvContent = "data:text/csv;charset=utf-8," + rows.map(processRow).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(`Exported ${filename} successfully!`);
}


// ==========================================
// 2. DASHBOARD PAGE LOGIC
// ==========================================

function initDashboardPage() {
    if (window.isDashboardApiManaged) return;
    const statsContainer = document.querySelector("main section.grid");
    if (!statsContainer || !window.location.pathname.includes("dashboard")) return;

    const students = DataAPI.getStudents();
    const classrooms = DataAPI.getClassrooms();
    const notifications = DataAPI.getNotifications();

    const activeRooms = classrooms.filter(c => c.status === "Active").length;
    const avgAttendance = Math.round(students.reduce((acc, s) => acc + (s.attendance || 0), 0) / (students.length || 1));
    const activeAlerts = notifications.filter(n => !n.read && n.category === "Alert").length;

    // Update KPI card text dynamically if elements exist
    const kpiElements = document.querySelectorAll(".glass-card .text-3xl");
    if (kpiElements.length >= 4) {
        kpiElements[0].textContent = students.length;
        kpiElements[1].textContent = `${activeRooms}/${classrooms.length}`;
        kpiElements[2].textContent = `${avgAttendance}%`;
        kpiElements[3].textContent = activeAlerts;
    }

    // Render Recent Activity Feed
    const activityFeed = document.getElementById("recent-activity-feed");
    if (activityFeed) {
        const recent = notifications.slice(0, 5);
        if (recent.length === 0) {
            activityFeed.innerHTML = `<p class="text-xs text-on-surface-variant text-center py-4">No recent activity logged</p>`;
        } else {
            activityFeed.innerHTML = recent.map(n => `
                <div class="flex items-start gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors border border-white/5">
                    <span class="material-symbols-outlined text-lg ${n.category === 'Alert' ? 'text-error' : 'text-primary'}">${n.category === 'Alert' ? 'warning' : 'notifications'}</span>
                    <div class="flex-1">
                        <div class="flex justify-between items-center">
                            <p class="text-xs font-bold text-on-surface">${n.title}</p>
                            <span class="text-[10px] text-on-surface-variant opacity-70">${n.time}</span>
                        </div>
                        <p class="text-[11px] text-on-surface-variant mt-0.5 line-clamp-1">${n.message}</p>
                    </div>
                </div>
            `).join("");
        }
    }
}


// ==========================================
// 3. CLASSROOM MANAGEMENT LOGIC
// ==========================================

function initClassroomPage() {
    if (!document.getElementById("classroom-cards-container")) return;
    renderClassrooms();

    const searchInput = document.getElementById("classroom-search-input");
    const statusSelect = document.getElementById("classroom-status-filter");

    if (searchInput) searchInput.addEventListener("input", renderClassrooms);
    if (statusSelect) statusSelect.addEventListener("change", renderClassrooms);
}

function renderClassrooms() {
    const container = document.getElementById("classroom-cards-container");
    if (!container) return;

    const search = (document.getElementById("classroom-search-input")?.value || "").toLowerCase().trim();
    const filterStatus = document.getElementById("classroom-status-filter")?.value || "All";

    let classrooms = DataAPI.getClassrooms();

    if (search) {
        classrooms = classrooms.filter(c => c.name.toLowerCase().includes(search) || c.dept.toLowerCase().includes(search));
    }
    if (filterStatus !== "All") {
        classrooms = classrooms.filter(c => c.status === filterStatus);
    }

    if (classrooms.length === 0) {
        container.innerHTML = `<div class="col-span-full py-12 text-center text-on-surface-variant"><p>No classrooms found matching search filters.</p></div>`;
        return;
    }

    container.innerHTML = classrooms.map(c => `
        <div class="glass-card rounded-2xl p-6 flex flex-col justify-between gap-4 border border-white/10 hover:border-primary/40 transition-all">
            <div class="flex justify-between items-start">
                <div>
                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${c.status === 'Active' ? 'bg-tertiary/10 text-tertiary border border-tertiary/20' : 'bg-white/10 text-on-surface-variant'}">${c.status}</span>
                    <h3 class="text-xl font-bold text-on-surface mt-2">${c.name}</h3>
                    <p class="text-xs text-on-surface-variant">${c.dept} Department</p>
                </div>
                <button class="p-1.5 text-on-surface-variant hover:text-error transition-colors" onclick="deleteClassroom('${c.name}')">
                    <span class="material-symbols-outlined text-lg">delete</span>
                </button>
            </div>
            
            <div class="grid grid-cols-3 gap-2 py-3 border-y border-white/5 text-center">
                <div>
                    <p class="text-[10px] text-on-surface-variant uppercase font-bold">Students</p>
                    <p class="text-sm font-bold text-on-surface mt-0.5">${c.students}</p>
                </div>
                <div>
                    <p class="text-[10px] text-on-surface-variant uppercase font-bold">Attention</p>
                    <p class="text-sm font-bold text-primary mt-0.5">${c.attention}%</p>
                </div>
                <div>
                    <p class="text-[10px] text-on-surface-variant uppercase font-bold">Occupancy</p>
                    <p class="text-sm font-bold text-tertiary mt-0.5">${c.occupancy}%</p>
                </div>
            </div>

            <div class="flex gap-2">
                <button class="flex-1 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-bold text-on-surface transition-all" onclick="toggleRoomStatus('${c.name}')">
                    Toggle ${c.status === 'Active' ? 'Inactive' : 'Active'}
                </button>
                <a href="live_monitoring_smart_classroom_ai.html" class="py-2 px-3 rounded-xl gradient-btn text-xs font-bold text-white flex items-center justify-center gap-1">
                    <span class="material-symbols-outlined text-sm">videocam</span> Live
                </a>
            </div>
        </div>
    `).join("");
}

function toggleRoomStatus(roomName) {
    const classrooms = DataAPI.getClassrooms();
    const room = classrooms.find(c => c.name === roomName);
    if (room) {
        room.status = room.status === "Active" ? "Inactive" : "Active";
        DataAPI.saveClassroom(room);
        renderClassrooms();
        showToast(`${roomName} status changed to ${room.status}`);
    }
}

function deleteClassroom(roomName) {
    if (confirm(`Are you sure you want to remove ${roomName}?`)) {
        const classrooms = DataAPI.getClassrooms().filter(c => c.name !== roomName);
        localStorage.setItem("sc_classrooms", JSON.stringify(classrooms));
        renderClassrooms();
        showToast(`${roomName} removed.`);
    }
}

function openClassroomModal() {
    const modal = document.getElementById("addClassroomModal");
    if (modal) modal.classList.remove("hidden", "invisible");
}

function closeClassroomModal() {
    const modal = document.getElementById("addClassroomModal");
    if (modal) modal.classList.add("hidden", "invisible");
}


// ==========================================
// 4. ATTENDANCE LOGS LOGIC
// ==========================================

function initAttendancePage() {
    if (window.isAttendanceManagementApiManaged) return;
    const tbody = document.getElementById("attendance-table-body");
    if (!tbody) return;

    renderAttendanceTable();

    const searchInput = document.getElementById("attendance-search");
    const deptSelect = document.getElementById("attendance-dept-filter");
    const statusSelect = document.getElementById("attendance-status-filter");
    const exportBtn = document.getElementById("export-attendance-btn");

    if (searchInput) searchInput.addEventListener("input", renderAttendanceTable);
    if (deptSelect) deptSelect.addEventListener("change", renderAttendanceTable);
    if (statusSelect) statusSelect.addEventListener("change", renderAttendanceTable);

    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            const students = DataAPI.getStudents();
            const rows = [["Student ID", "Name", "Department", "Class", "Attendance %", "Status"]];
            students.forEach(s => rows.push([s.id, s.name, s.dept, s.class, `${s.attendance}%`, s.status]));
            exportToCSV(`Attendance_Report_${new Date().toISOString().slice(0,10)}.csv`, rows);
        });
    }
}

function renderAttendanceTable() {
    const tbody = document.getElementById("attendance-table-body");
    if (!tbody) return;

    const search = (document.getElementById("attendance-search")?.value || "").toLowerCase().trim();
    const dept = document.getElementById("attendance-dept-filter")?.value || "";
    const status = document.getElementById("attendance-status-filter")?.value || "";

    let students = DataAPI.getStudents();

    if (search) {
        students = students.filter(s => s.name.toLowerCase().includes(search) || s.id.toLowerCase().includes(search));
    }
    if (dept) {
        students = students.filter(s => s.dept === dept);
    }

    if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="px-6 py-8 text-center text-on-surface-variant">No attendance records found</td></tr>`;
        return;
    }

    tbody.innerHTML = students.map(s => {
        const attStatus = s.attendance >= 90 ? "Present" : (s.attendance >= 80 ? "Late" : "Absent");
        if (status && status !== "All" && attStatus !== status) return "";

        const badgeClass = attStatus === "Present" ? "bg-tertiary/10 text-tertiary border-tertiary/20" : (attStatus === "Late" ? "bg-secondary/10 text-secondary border-secondary/20" : "bg-error/10 text-error border-error/20");

        return `
            <tr class="hover:bg-white/5 transition-colors">
                <td class="px-6 py-4 flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center font-bold text-primary text-xs">${s.name.split(" ").map(n => n[0]).join("")}</div>
                    <div>
                        <p class="font-bold text-sm text-on-surface">${s.name}</p>
                        <p class="text-xs text-on-surface-variant opacity-70">${s.id}</p>
                    </div>
                </td>
                <td class="px-6 py-4 text-sm text-on-surface-variant">${s.dept} (${s.class})</td>
                <td class="px-6 py-4 text-sm text-on-surface-variant">${new Date().toLocaleDateString()}</td>
                <td class="px-6 py-4 text-sm">
                    <div class="flex items-center gap-2">
                        <div class="w-16 bg-white/10 rounded-full h-2 overflow-hidden">
                            <div class="bg-tertiary h-full rounded-full" style="width: ${s.attendance}%"></div>
                        </div>
                        <span class="font-bold text-xs text-tertiary">${s.attendance}%</span>
                    </div>
                </td>
                <td class="px-6 py-4 text-sm">
                    <span class="px-2.5 py-1 rounded-full text-xs font-bold border ${badgeClass}">${attStatus}</span>
                </td>
                <td class="px-6 py-4 text-sm text-right">
                    <button class="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-bold text-primary transition-all" onclick="cycleAttendanceStatus('${s.id}')">
                        Toggle Status
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function cycleAttendanceStatus(studentId) {
    const students = DataAPI.getStudents();
    const student = students.find(s => s.id === studentId);
    if (student) {
        if (student.attendance >= 90) student.attendance = 82;
        else if (student.attendance >= 80) student.attendance = 65;
        else student.attendance = 95;

        DataAPI.saveStudent(student);
        renderAttendanceTable();
        showToast(`Updated attendance status for ${student.name}`);
    }
}


// ==========================================
// 5. EMOTION ANALYTICS LOGIC
// ==========================================

function initEmotionPage() {
    const tabs = document.querySelectorAll(".emotion-timeframe-btn");
    if (tabs.length === 0) return;

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active", "bg-primary", "text-on-primary-container"));
            tabs.forEach(t => t.classList.add("bg-white/5", "text-on-surface-variant"));
            
            tab.classList.add("active", "bg-primary", "text-on-primary-container");
            tab.classList.remove("bg-white/5", "text-on-surface-variant");

            const tf = tab.textContent.trim();
            showToast(`Loaded Emotion Data for: ${tf}`);
        });
    });
}


// ==========================================
// 6. REPORTS & ANALYTICS LOGIC
// ==========================================

function initReportsPage() {
    const generateBtn = document.getElementById("generate-report-btn");
    const downloadPdfBtn = document.getElementById("download-pdf-btn");
    const exportCsvBtn = document.getElementById("export-csv-btn");

    if (generateBtn) {
        generateBtn.addEventListener("click", () => {
            showToast("Generating comprehensive analytics report...");
        });
    }

    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener("click", () => {
            showToast("Preparing PDF download...");
            setTimeout(() => window.print(), 800);
        });
    }

    if (exportCsvBtn) {
        exportCsvBtn.addEventListener("click", () => {
            const students = DataAPI.getStudents();
            const rows = [["Student ID", "Name", "Department", "Attendance %"]];
            students.forEach(s => rows.push([s.id, s.name, s.dept, `${s.attendance}%`]));
            exportToCSV("ClassMind_Full_Analytics_Report.csv", rows);
        });
    }
}


// ==========================================
// 7. NOTIFICATIONS & ALERTS LOGIC
// ==========================================

function initNotificationsPage() {
    const listContainer = document.getElementById("notifications-page-list");
    if (!listContainer) return;

    renderNotificationsPage();

    const markAllBtn = document.getElementById("notif-mark-all-btn");
    const clearAllBtn = document.getElementById("notif-clear-all-btn");
    const testAlertBtn = document.getElementById("notif-trigger-test-btn");

    if (markAllBtn) {
        markAllBtn.addEventListener("click", () => {
            DataAPI.markAllNotificationsAsRead();
            renderNotificationsPage();
            showToast("All notifications marked as read.");
        });
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener("click", () => {
            if (confirm("Are you sure you want to clear all notifications?")) {
                DataAPI.clearNotifications();
                renderNotificationsPage();
                showToast("Notifications cleared.");
            }
        });
    }

    if (testAlertBtn) {
        testAlertBtn.addEventListener("click", () => {
            DataAPI.addNotification({
                title: "Simulated AI Alert",
                message: "High temperature anomaly detected in Room 101 AI Camera Sensor.",
                category: "Alert"
            });
            renderNotificationsPage();
            showToast("Test alert notification generated!");
        });
    }
}

function renderNotificationsPage() {
    const listContainer = document.getElementById("notifications-page-list");
    if (!listContainer) return;

    const notifs = DataAPI.getNotifications();

    if (notifs.length === 0) {
        listContainer.innerHTML = `<div class="p-8 text-center text-on-surface-variant"><p>No notifications present.</p></div>`;
        return;
    }

    listContainer.innerHTML = notifs.map(n => `
        <div class="p-5 rounded-2xl bg-white/5 hover:bg-white/10 transition-all border border-white/10 flex items-start justify-between gap-4 ${!n.read ? 'border-l-4 border-l-primary' : ''}">
            <div class="flex items-start gap-4">
                <div class="p-2.5 rounded-xl ${n.category === 'Alert' ? 'bg-error/20 text-error' : 'bg-primary/20 text-primary'}">
                    <span class="material-symbols-outlined">${n.category === 'Alert' ? 'warning' : 'notifications'}</span>
                </div>
                <div>
                    <div class="flex items-center gap-3">
                        <h4 class="font-bold text-base text-on-surface">${n.title}</h4>
                        <span class="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${n.category === 'Alert' ? 'bg-error/10 text-error' : 'bg-primary/10 text-primary'}">${n.category}</span>
                    </div>
                    <p class="text-xs text-on-surface-variant mt-1 leading-relaxed">${n.message}</p>
                    <span class="text-[10px] text-on-surface-variant opacity-70 mt-2 block">${n.time}</span>
                </div>
            </div>
            ${!n.read ? `<button class="px-3 py-1.5 text-xs font-bold text-primary hover:bg-white/5 rounded-xl transition-all" onclick="markSingleNotifRead(${n.id})">Mark Read</button>` : ''}
        </div>
    `).join("");
}

function markSingleNotifRead(id) {
    const notifs = DataAPI.getNotifications();
    const target = notifs.find(n => n.id === id);
    if (target) {
        target.read = true;
        localStorage.setItem("sc_notifications", JSON.stringify(notifs));
        renderNotificationsPage();
        showToast("Notification marked read");
    }
}


// ==========================================
// 8. SYSTEM SETTINGS LOGIC
// ==========================================

function initSettingsPage() {
    const form = document.getElementById("settings-form");
    if (!form) return;

    const settings = DataAPI.getSettings();

    // Populate inputs if present
    const nameInput = form.querySelector("input[name='adminName']") || form.querySelector("input[placeholder='Alex Admin']");
    const roleInput = form.querySelector("input[name='adminRole']") || form.querySelector("input[placeholder='Senior Administrator']");
    const emailInput = form.querySelector("input[type='email']");

    if (nameInput) nameInput.value = settings.adminName || "";
    if (roleInput) roleInput.value = settings.adminRole || "";
    if (emailInput) emailInput.value = settings.adminEmail || "";
}


// ==========================================
// 9. LANDING PAGE LOGIC
// ==========================================

function initLandingPage() {
    const contactForm = document.getElementById("landing-contact-form");
    if (contactForm) {
        contactForm.addEventListener("submit", (e) => {
            e.preventDefault();
            showToast("Thank you! Your message has been sent to our support team.");
            contactForm.reset();
        });
    }

    const drawerToggle = document.getElementById("mobile-nav-toggle");
    const drawerClose = document.getElementById("mobile-nav-close");
    const drawer = document.getElementById("mobile-nav-drawer");

    if (drawerToggle && drawer) {
        drawerToggle.addEventListener("click", () => {
            drawer.classList.remove("translate-x-full");
        });
    }

    if (drawerClose && drawer) {
        drawerClose.addEventListener("click", () => {
            drawer.classList.add("translate-x-full");
        });
    }
}
