// State and Data Manager using LocalStorage for Smart Classroom AI

const INITIAL_STUDENTS = [
    { id: "ST-2024-001", name: "Alex Johnson", email: "alex.j@aura.edu", class: "Room 101", dept: "Science", attendance: 95, status: "Active" },
    { id: "ST-2024-042", name: "Elena Rodriguez", email: "elena.r@aura.edu", class: "Room 302", dept: "Arts", attendance: 82, status: "Active" },
    { id: "ST-2024-015", name: "Marcus Chen", email: "marcus.c@aura.edu", class: "Room 205", dept: "Engineering", attendance: 89, status: "Active" },
    { id: "ST-2024-088", name: "Sarah Miller", email: "sarah.m@aura.edu", class: "Room 101", dept: "Science", attendance: 92, status: "Active" },
    { id: "ST-2024-112", name: "David Kim", email: "david.k@aura.edu", class: "Room 205", dept: "Engineering", attendance: 76, status: "Active" }
];

const INITIAL_CLASSROOMS = [
    { name: "Room 101", dept: "Science", students: 32, attention: 94, occupancy: 85, status: "Active" },
    { name: "Room 205", dept: "Engineering", students: 28, attention: 82, occupancy: 90, status: "Active" },
    { name: "Room 302", dept: "Arts", students: 24, attention: 88, occupancy: 75, status: "Active" },
    { name: "Room 102", dept: "History", students: 30, attention: 79, occupancy: 80, status: "Inactive" }
];

const INITIAL_NOTIFICATIONS = [
    { id: 1, title: "Low Attention Detected", message: "Average attention in Room 205 dropped below 70%", time: "10 mins ago", category: "Alert", read: false },
    { id: 2, title: "Biometric Enrolment Successful", message: "Student Marcus Chen biometric enrollment complete", time: "2 hours ago", category: "System", read: true },
    { id: 3, title: "High Emotion Variance", message: "High stress detected in Room 101 during Exam", time: "1 day ago", category: "Warning", read: false }
];

const INITIAL_SETTINGS = {
    cameraFps: 30,
    attentionThreshold: 75,
    tempBoundMin: 18,
    tempBoundMax: 26,
    darkMode: true,
    adminName: "Alex Admin",
    adminRole: "Senior Administrator",
    adminEmail: "admin@aura.edu",
    faceDetectionEnabled: true,
    audioAlertsEnabled: false,
    alertThreshold: "High"
};

// Initialize data in LocalStorage if not present
function initializeData() {
    if (!localStorage.getItem("sc_students")) {
        localStorage.setItem("sc_students", JSON.stringify(INITIAL_STUDENTS));
    }
    if (!localStorage.getItem("sc_classrooms")) {
        localStorage.setItem("sc_classrooms", JSON.stringify(INITIAL_CLASSROOMS));
    }
    if (!localStorage.getItem("sc_notifications")) {
        localStorage.setItem("sc_notifications", JSON.stringify(INITIAL_NOTIFICATIONS));
    }
    if (!localStorage.getItem("sc_settings")) {
        localStorage.setItem("sc_settings", JSON.stringify(INITIAL_SETTINGS));
    }
}

// Data API helper functions
const DataAPI = {
    getStudents() {
        initializeData();
        return JSON.parse(localStorage.getItem("sc_students"));
    },
    saveStudent(student) {
        const students = this.getStudents();
        const index = students.findIndex(s => s.id === student.id);
        if (index > -1) {
            students[index] = student;
        } else {
            students.push(student);
        }
        localStorage.setItem("sc_students", JSON.stringify(students));
    },
    deleteStudent(studentId) {
        const students = this.getStudents();
        const filtered = students.filter(s => s.id !== studentId);
        localStorage.setItem("sc_students", JSON.stringify(filtered));
    },
    getClassrooms() {
        initializeData();
        return JSON.parse(localStorage.getItem("sc_classrooms"));
    },
    saveClassroom(classroom) {
        const classrooms = this.getClassrooms();
        const index = classrooms.findIndex(c => c.name === classroom.name);
        if (index > -1) {
            classrooms[index] = classroom;
        } else {
            classrooms.push(classroom);
        }
        localStorage.setItem("sc_classrooms", JSON.stringify(classrooms));
    },
    getNotifications() {
        initializeData();
        return JSON.parse(localStorage.getItem("sc_notifications"));
    },
    addNotification(notif) {
        const notifications = this.getNotifications();
        const newNotif = {
            id: Date.now(),
            title: notif.title,
            message: notif.message,
            time: "Just now",
            category: notif.category || "System",
            read: false
        };
        notifications.unshift(newNotif);
        localStorage.setItem("sc_notifications", JSON.stringify(notifications));
    },
    markAllNotificationsAsRead() {
        const notifications = this.getNotifications();
        notifications.forEach(n => n.read = true);
        localStorage.setItem("sc_notifications", JSON.stringify(notifications));
    },
    clearNotifications() {
        localStorage.setItem("sc_notifications", JSON.stringify([]));
    },
    getSettings() {
        initializeData();
        return JSON.parse(localStorage.getItem("sc_settings"));
    },
    saveSettings(settings) {
        const current = this.getSettings();
        const updated = { ...current, ...settings };
        localStorage.setItem("sc_settings", JSON.stringify(updated));
    }
};

// Auto initialize data
initializeData();
