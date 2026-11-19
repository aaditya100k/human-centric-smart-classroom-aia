// Shared Layout Injector (Sidebar, Navbar, Mobile Menu, Notifications Dropdown)

document.addEventListener("DOMContentLoaded", () => {
    // 1. Get elements and page info
    const sidebarContainer = document.getElementById("layout-sidebar");
    const navbarContainer = document.getElementById("layout-navbar");
    const currentPath = window.location.pathname;
    const pageName = currentPath.substring(currentPath.lastIndexOf("/") + 1);

    // Fetch dynamic admin settings / user state
    const currentUser = typeof AuthService !== "undefined" ? AuthService.getCurrentUser() : null;
    const settings = DataAPI.getSettings();
    const displayName = currentUser ? (currentUser.full_name || currentUser.username) : (settings.adminName || "Admin");
    const displayRole = currentUser ? (currentUser.role || "Administrator") : (settings.adminRole || "Senior Administrator");
    const adminInitials = displayName ? displayName.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() : "AD";
    
    // Fetch notifications count
    const notifications = DataAPI.getNotifications();
    const unreadCount = notifications.filter(n => !n.read).length;

    // Helper to check if a navigation link is active
    const isActive = (href) => {
        return pageName === href || (pageName === "" && href === "smart_classroom_ai_dashboard.html");
    };

    // 2. Inject Sidebar
    if (sidebarContainer) {
        document.body.classList.add("has-sidebar");
        sidebarContainer.className = "fixed left-0 top-0 h-full w-[270px] z-50 flex flex-col backdrop-blur-xl bg-surface/80 border-r border-white/10 shadow-2xl transition-transform duration-300 transform -translate-x-full md:translate-x-0";
        sidebarContainer.id = "app-sidebar";
        
        sidebarContainer.innerHTML = `
            <div class="p-6 flex flex-col gap-1 relative">
                <button id="close-sidebar-btn" class="absolute top-4 right-4 md:hidden text-on-surface-variant hover:text-primary">
                    <span class="material-symbols-outlined">close</span>
                </button>
                <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-primary text-3xl font-variation-fill">psychology</span>
                    <h1 class="font-headline-md text-xl font-bold text-primary">ClassMind AI</h1>
                </div>
                <p class="font-label-sm text-xs text-on-surface-variant opacity-70">Smart Classroom Suite</p>
            </div>
            
            <nav class="flex-1 px-4 mt-6 flex flex-col gap-2 overflow-y-auto custom-scrollbar">
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("smart_classroom_ai_dashboard.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="smart_classroom_ai_dashboard.html">
                    <span class="material-symbols-outlined">dashboard</span>
                    <span class="text-sm">Dashboard</span>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("student_management_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="student_management_smart_classroom_ai.html">
                    <span class="material-symbols-outlined">group</span>
                    <span class="text-sm">Student Management</span>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("classroom_management_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="classroom_management_smart_classroom_ai.html">
                    <span class="material-symbols-outlined">meeting_room</span>
                    <span class="text-sm">Classroom Management</span>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("live_monitoring_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="live_monitoring_smart_classroom_ai.html">
                    <span class="material-symbols-outlined font-variation-fill">videocam</span>
                    <span class="text-sm">Live Monitoring</span>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("attendance_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="attendance_smart_classroom_ai.html">
                    <span class="material-symbols-outlined">how_to_reg</span>
                    <span class="text-sm">Attendance</span>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("emotion_analytics_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="emotion_analytics_smart_classroom_ai.html">
                    <span class="material-symbols-outlined">sentiment_satisfied</span>
                    <span class="text-sm">Emotion Analytics</span>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("reports_analytics_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="reports_analytics_smart_classroom_ai.html">
                    <span class="material-symbols-outlined">analytics</span>
                    <span class="text-sm">Reports & Analytics</span>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("notifications_alerts_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'}" href="notifications_alerts_smart_classroom_ai.html">
                    <div class="relative flex items-center gap-3 w-full">
                        <span class="material-symbols-outlined">notifications</span>
                        <span class="text-sm">Notifications</span>
                        ${unreadCount > 0 ? `<span class="absolute right-0 w-2 h-2 bg-error rounded-full animate-pulse"></span>` : ''}
                    </div>
                </a>
                <a class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive("settings_smart_classroom_ai.html") ? 'active' : 'text-on-surface-variant font-medium hover:bg-white/5 hover:text-primary hover:translate-x-1'} mt-4" href="settings_smart_classroom_ai.html">
                    <span class="material-symbols-outlined">settings</span>
                    <span class="text-sm">Settings</span>
                </a>
            </nav>
            
            <div class="px-4 pb-6 flex flex-col gap-2 mt-auto">
                <div class="px-4 py-2.5 rounded-xl bg-tertiary/10 border border-tertiary/20 flex items-center gap-2 mb-2 justify-center">
                    <div class="w-2 h-2 rounded-full bg-tertiary animate-pulse"></div>
                    <span class="font-label-sm text-xs text-tertiary font-bold">System Online</span>
                </div>
                <button id="logout-btn" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-error font-medium hover:bg-error/10 transition-all">
                    <span class="material-symbols-outlined">logout</span>
                    <span class="text-sm">Logout</span>
                </button>
            </div>
        `;
    }

    // 3. Inject Navbar
    if (navbarContainer) {
        navbarContainer.className = "fixed top-0 right-0 left-0 md:left-[270px] h-[80px] z-40 flex justify-between items-center px-6 md:px-8 backdrop-blur-xl bg-surface/60 border-b border-white/10 shadow-lg transition-all";
        
        let headerTitle = "Dashboard";
        if (isActive("student_management_smart_classroom_ai.html")) headerTitle = "Student Management";
        else if (isActive("classroom_management_smart_classroom_ai.html")) headerTitle = "Classroom Management";
        else if (isActive("live_monitoring_smart_classroom_ai.html")) headerTitle = "Live AI Monitoring";
        else if (isActive("attendance_smart_classroom_ai.html")) headerTitle = "Attendance Logs";
        else if (isActive("emotion_analytics_smart_classroom_ai.html")) headerTitle = "Emotion Analytics";
        else if (isActive("reports_analytics_smart_classroom_ai.html")) headerTitle = "Reports & Analytics";
        else if (isActive("notifications_alerts_smart_classroom_ai.html")) headerTitle = "Notifications & Alerts";
        else if (isActive("settings_smart_classroom_ai.html")) headerTitle = "System Settings";

        navbarContainer.innerHTML = `
            <div class="flex items-center gap-4 flex-1">
                <button id="menu-toggle-btn" class="md:hidden p-2 text-on-surface-variant hover:text-primary transition-colors">
                    <span class="material-symbols-outlined text-2xl">menu</span>
                </button>
                <h2 class="text-xl font-extrabold text-primary hidden sm:block whitespace-nowrap">${headerTitle}</h2>
                <div class="relative w-full max-w-xs md:max-w-md ml-2 sm:ml-4">
                    <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none text-xl">search</span>
                    <input id="nav-search-input" class="w-full bg-white/5 border border-white/10 rounded-full py-1.5 pl-10 pr-4 text-sm text-on-surface placeholder-on-surface-variant/50 focus:outline-none focus:ring-1 focus:ring-primary/50 focus:border-primary/50 transition-all" placeholder="Search students, rooms..." type="text">
                </div>
            </div>
            
            <div class="flex items-center gap-4">
                <div class="flex items-center gap-2">
                    <!-- Notifications Dropdown Trigger -->
                    <div class="relative">
                        <button id="dropdown-notif-btn" class="relative p-2 text-on-surface-variant hover:text-primary transition-colors rounded-full hover:bg-white/5">
                            <span class="material-symbols-outlined text-2xl">notifications</span>
                            ${unreadCount > 0 ? `<span class="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full animate-bounce"></span>` : ''}
                        </button>
                        
                        <!-- Notifications Quick Dropdown -->
                        <div id="quick-notif-dropdown" class="absolute right-0 mt-2 w-80 bg-surface-container rounded-2xl border border-white/10 shadow-2xl p-4 hidden flex-col gap-3 z-50">
                            <div class="flex justify-between items-center pb-2 border-b border-white/10">
                                <h4 class="font-bold text-sm">Notifications</h4>
                                <span class="text-xs text-primary font-semibold hover:underline cursor-pointer" id="mark-all-read-btn">Mark all read</span>
                            </div>
                            <div class="flex flex-col gap-2.5 max-h-60 overflow-y-auto custom-scrollbar" id="dropdown-notif-list">
                                <!-- Populated dynamically -->
                            </div>
                            <a href="notifications_alerts_smart_classroom_ai.html" class="text-center text-xs text-primary font-bold py-1.5 hover:bg-white/5 rounded-xl transition-all">View All Notifications</a>
                        </div>
                    </div>
                    
                    <a href="settings_smart_classroom_ai.html" class="p-2 text-on-surface-variant hover:text-primary transition-colors rounded-full hover:bg-white/5">
                        <span class="material-symbols-outlined text-2xl">settings</span>
                    </a>
                </div>
                
                <!-- Admin Profile Info -->
                <div class="flex items-center gap-3 pl-4 border-l border-white/10">
                    <div class="text-right hidden sm:block">
                        <p class="text-xs font-bold text-on-surface">${displayName}</p>
                        <p class="text-[9px] text-on-surface-variant tracking-wider uppercase opacity-80">${displayRole}</p>
                    </div>
                    <div class="w-9 h-9 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center font-bold text-primary text-xs shadow-inner cursor-pointer" onclick="window.location.href='settings_smart_classroom_ai.html'">
                        ${adminInitials}
                    </div>
                </div>
            </div>
        `;

        // 4. Setup Event Listeners inside layout
        setupLayoutListeners();
    }
});

// Setup sidebar toggles, dropdown behaviors
function setupLayoutListeners() {
    const sidebar = document.getElementById("app-sidebar");
    const menuToggle = document.getElementById("menu-toggle-btn");
    const closeSidebar = document.getElementById("close-sidebar-btn");
    const logoutBtn = document.getElementById("logout-btn");
    const dropdownNotifBtn = document.getElementById("dropdown-notif-btn");
    const quickNotifDropdown = document.getElementById("quick-notif-dropdown");
    const dropdownNotifList = document.getElementById("dropdown-notif-list");
    const markAllReadBtn = document.getElementById("mark-all-read-btn");
    const searchInput = document.getElementById("nav-search-input");

    // Sidebar Mobile Toggle & Backdrop Overlay
    let backdrop = document.getElementById("sidebar-backdrop");
    if (!backdrop) {
        backdrop = document.createElement("div");
        backdrop.id = "sidebar-backdrop";
        backdrop.className = "fixed inset-0 bg-black/60 backdrop-blur-sm z-40 hidden transition-opacity duration-300 opacity-0 md:hidden";
        document.body.appendChild(backdrop);
    }

    const openSidebar = () => {
        if (sidebar) sidebar.classList.remove("-translate-x-full");
        if (backdrop) {
            backdrop.classList.remove("hidden");
            setTimeout(() => backdrop.classList.remove("opacity-0"), 10);
        }
    };

    const closeSidebarFn = () => {
        if (sidebar) sidebar.classList.add("-translate-x-full");
        if (backdrop) {
            backdrop.classList.add("opacity-0");
            setTimeout(() => backdrop.classList.add("hidden"), 300);
        }
    };

    if (menuToggle) {
        menuToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            openSidebar();
        });
    }

    if (closeSidebar) {
        closeSidebar.addEventListener("click", closeSidebarFn);
    }

    if (backdrop) {
        backdrop.addEventListener("click", closeSidebarFn);
    }

    // Close mobile sidebar on click outside
    document.addEventListener("click", (e) => {
        if (sidebar && !sidebar.contains(e.target) && menuToggle && !menuToggle.contains(e.target)) {
            closeSidebarFn();
        }
    });

    // Logout
    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            if (typeof AuthService !== "undefined") {
                AuthService.logout();
            } else {
                localStorage.removeItem("sc_token");
                sessionStorage.removeItem("sc_token");
                window.location.href = "edumonitor_ai_login_page.html";
            }
        });
    }

    // Notifications Dropdown Populate
    if (dropdownNotifBtn && quickNotifDropdown) {
        dropdownNotifBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            quickNotifDropdown.classList.toggle("hidden");
            quickNotifDropdown.classList.toggle("flex");
            
            if (!quickNotifDropdown.classList.contains("hidden")) {
                renderDropdownNotifications();
            }
        });

        document.addEventListener("click", (e) => {
            if (quickNotifDropdown && !quickNotifDropdown.contains(e.target) && e.target !== dropdownNotifBtn) {
                quickNotifDropdown.classList.add("hidden");
                quickNotifDropdown.classList.remove("flex");
            }
        });
    }

    function renderDropdownNotifications() {
        if (!dropdownNotifList) return;
        const notifs = DataAPI.getNotifications().slice(0, 3); // Get latest 3
        if (notifs.length === 0) {
            dropdownNotifList.innerHTML = `<p class="text-xs text-on-surface-variant text-center py-4">No recent notifications</p>`;
            return;
        }

        dropdownNotifList.innerHTML = notifs.map(n => `
            <div class="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 transition-all cursor-pointer flex flex-col gap-0.5 border border-white/5 ${!n.read ? 'border-l-2 border-l-primary' : ''}">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-bold text-on-surface ${!n.read ? 'text-primary' : ''}">${n.title}</span>
                    <span class="text-[9px] text-on-surface-variant opacity-70">${n.time}</span>
                </div>
                <p class="text-[11px] text-on-surface-variant leading-relaxed line-clamp-2">${n.message}</p>
            </div>
        `).join("");
    }

    if (markAllReadBtn) {
        markAllReadBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            DataAPI.markAllNotificationsAsRead();
            renderDropdownNotifications();
            
            // Reload page or update badges dynamically
            const badge = document.querySelector("#dropdown-notif-btn span.bg-error");
            if (badge) badge.remove();
            
            const sidebarBadge = document.querySelector("a[href='notifications_alerts_smart_classroom_ai.html'] span.bg-error");
            if (sidebarBadge) sidebarBadge.remove();
        });
    }

    // Search bar functionality (Simple redirect to student page with search parameter if executed)
    if (searchInput) {
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && searchInput.value.trim() !== "") {
                const query = encodeURIComponent(searchInput.value.trim());
                window.location.href = `student_management_smart_classroom_ai.html?search=${query}`;
            }
        });
    }
}
