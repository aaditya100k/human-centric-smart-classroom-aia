// Client-side Form Validation and LocalStorage CRUD linkage

document.addEventListener("DOMContentLoaded", () => {
    // 1. Login Form Handler
    initLoginForm();

    // 2. Add Student Form Handler
    initAddStudentForm();

    // 3. Add Classroom Form Handler
    initAddClassroomForm();

    // 4. Settings Form Handler
    initSettingsForm();
});

// Utility to display status message or browser alert
function showStatus(message, type = "success") {
    if (typeof showToast === "function") {
        showToast(message, type);
    } else {
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

function initLoginForm() {
    const loginForm = document.getElementById("login-form");
    if (!loginForm) return;

    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const emailInput = loginForm.querySelector("input[type='email']");
        const passwordInput = loginForm.querySelector("input[type='password']");

        if (!emailInput.value || !passwordInput.value) {
            showStatus("Please enter both email and password.", "error");
            return;
        }

        // Simple validation check (any email/password works for demo)
        sessionStorage.setItem("activeSession", JSON.stringify({
            email: emailInput.value,
            loggedInAt: Date.now()
        }));

        // Redirect to dashboard
        window.location.href = "smart_classroom_ai_dashboard.html";
    });
}

function initAddStudentForm() {
    const studentForm = document.getElementById("add-student-form");
    if (!studentForm) return;

    studentForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const nameInput = studentForm.querySelector("input[placeholder='e.g. Alex Johnson']");
        const rollInput = studentForm.querySelector("input[placeholder='ST-2024-XXX']");
        const emailInput = studentForm.querySelector("input[type='email']");
        const deptSelect = studentForm.querySelector("select");
        const roomInput = studentForm.querySelector("input[placeholder='e.g. 101']");

        if (!nameInput.value || !rollInput.value || !emailInput.value || !deptSelect.value || !roomInput.value) {
            showStatus("All fields are required to enroll a student.", "error");
            return;
        }

        const newStudent = {
            id: rollInput.value.toUpperCase(),
            name: nameInput.value,
            email: emailInput.value,
            class: `Room ${roomInput.value}`,
            dept: deptSelect.options[deptSelect.selectedIndex].text,
            attendance: 100, // Starts at 100%
            status: "Active"
        };

        // Save to LocalStorage
        DataAPI.saveStudent(newStudent);

        // Add Notification
        DataAPI.addNotification({
            title: "New Student Enrolled",
            message: `${newStudent.name} (${newStudent.id}) has been added to ${newStudent.class}.`,
            category: "System"
        });

        showStatus("Student profile saved successfully.");
        
        // Reset form
        studentForm.reset();

        // Close modal if modal closing function is available
        if (typeof closeModal === "function") {
            closeModal();
        }

        // Trigger page re-render if we are on student_management page
        if (typeof renderStudentsTable === "function") {
            renderStudentsTable();
        }
    });
}

function initAddClassroomForm() {
    const classroomForm = document.getElementById("add-classroom-form");
    if (!classroomForm) return;

    classroomForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const nameInput = classroomForm.querySelector("input[name='room_name']") || classroomForm.querySelector("input[placeholder*='e.g. Room 101']");
        const deptSelect = classroomForm.querySelector("select[name='department']") || classroomForm.querySelector("select");
        const capacityInput = classroomForm.querySelector("input[name='capacity']") || classroomForm.querySelector("input[type='number']");

        if (!nameInput || !nameInput.value || !deptSelect || !deptSelect.value) {
            showStatus("Classroom name and department are required.", "error");
            return;
        }

        const newClassroom = {
            name: nameInput.value,
            dept: deptSelect.options[deptSelect.selectedIndex].text,
            students: parseInt(capacityInput ? capacityInput.value : "30") || 30,
            attention: 85, // Initial attention estimate
            occupancy: 90, // Initial occupancy estimate
            status: "Active"
        };

        // Save to LocalStorage
        DataAPI.saveClassroom(newClassroom);

        // Add Notification
        DataAPI.addNotification({
            title: "New Classroom Created",
            message: `${newClassroom.name} (${newClassroom.dept}) added to active monitoring.`,
            category: "System"
        });

        showStatus("Classroom added successfully.");
        
        // Reset form
        classroomForm.reset();

        // Close modal if close modal function is available
        if (typeof closeModal === "function") {
            closeModal();
        }

        // Trigger page re-render if we are on classroom_management page
        if (typeof renderClassroomsList === "function") {
            renderClassroomsList();
        }
    });
}

function initSettingsForm() {
    const settingsForm = document.getElementById("settings-form");
    if (!settingsForm) return;

    // Load initial settings values
    const currentSettings = DataAPI.getSettings();
    
    // Fill in the form values
    const adminNameInput = settingsForm.querySelector("input[name='admin_name']") || document.getElementById("admin-name-field");
    const adminEmailInput = settingsForm.querySelector("input[name='admin_email']") || document.getElementById("admin-email-field");
    const adminRoleInput = settingsForm.querySelector("input[name='admin_role']") || document.getElementById("admin-role-field");
    const fpsInput = settingsForm.querySelector("select[name='camera_fps']") || document.getElementById("fps-field");
    const thresholdInput = settingsForm.querySelector("input[type='range']") || document.getElementById("attention-field");
    const detectionToggle = document.getElementById("face-detection-toggle");

    if (adminNameInput) adminNameInput.value = currentSettings.adminName || "";
    if (adminEmailInput) adminEmailInput.value = currentSettings.adminEmail || "";
    if (adminRoleInput) adminRoleInput.value = currentSettings.adminRole || "";
    if (fpsInput) fpsInput.value = currentSettings.cameraFps || "30";
    if (thresholdInput) thresholdInput.value = currentSettings.attentionThreshold || "75";
    if (detectionToggle) detectionToggle.checked = currentSettings.faceDetectionEnabled !== false;

    // Save changes
    settingsForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const updatedSettings = {};
        if (adminNameInput) updatedSettings.adminName = adminNameInput.value;
        if (adminEmailInput) updatedSettings.adminEmail = adminEmailInput.value;
        if (adminRoleInput) updatedSettings.adminRole = adminRoleInput.value;
        if (fpsInput) updatedSettings.cameraFps = parseInt(fpsInput.value);
        if (thresholdInput) updatedSettings.attentionThreshold = parseInt(thresholdInput.value);
        if (detectionToggle) updatedSettings.faceDetectionEnabled = detectionToggle.checked;

        DataAPI.saveSettings(updatedSettings);

        // Add Notification
        DataAPI.addNotification({
            title: "Settings Updated",
            message: "System thresholds and profile information saved successfully.",
            category: "System"
        });

        showStatus("Settings saved successfully. Refreshing layout...");
        
        // Reload page to apply navbar changes immediately
        setTimeout(() => {
            window.location.reload();
        }, 800);
    });
}
