/**
 * Reusable API Service Client for Smart Classroom AI
 * Connects frontend to the FastAPI + MySQL backend.
 * Automatically handles JWT Bearer authentication headers and 401 redirects.
 */

const API_BASE_URL = "http://127.0.0.1:8000/api";

/**
 * Authenticated fetch wrapper that attaches Bearer JWT token and handles 401 responses
 */
async function fetchWithAuth(url, options = {}) {
    options = options || {};
    options.headers = options.headers || {};

    const token = typeof AuthService !== "undefined"
        ? AuthService.getToken()
        : (localStorage.getItem("sc_token") || sessionStorage.getItem("sc_token"));

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, options);

    if (response.status === 401) {
        console.warn("Received 401 Unauthorized from backend. Clearing token and redirecting to Login...");
        if (typeof AuthService !== "undefined") {
            AuthService.logout();
        } else {
            localStorage.removeItem("sc_token");
            localStorage.removeItem("sc_user");
            sessionStorage.removeItem("sc_token");
            sessionStorage.removeItem("sc_user");
            window.location.href = "edumonitor_ai_login_page.html";
        }
        throw new Error("Unauthorized session. Please log in again.");
    }

    return response;
}

const ApiService = {
    // ==========================================
    // STUDENTS API
    // ==========================================

    /**
     * Fetch list of students with optional query filters
     * @param {Object} params - { search, department, classroom_id, status }
     * @returns {Promise<Array>} List of students
     */
    async getStudents(params = {}) {
        const query = new URLSearchParams();
        if (params.search) query.append("search", params.search.trim());
        if (params.department) query.append("department", params.department.trim());
        if (params.classroom_id) query.append("classroom_id", params.classroom_id);
        if (params.status) query.append("status", params.status);

        const url = `${API_BASE_URL}/students${query.toString() ? '?' + query.toString() : ''}`;
        const response = await fetchWithAuth(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch students (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Get a single student by ID
     * @param {string} id - e.g. "ST-2024-001"
     * @returns {Promise<Object>} Student details
     */
    async getStudent(id) {
        const response = await fetchWithAuth(`${API_BASE_URL}/students/${encodeURIComponent(id)}`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch student ${id}`);
        }
        return await response.json();
    },

    /**
     * Create a new student in MySQL database
     * @param {Object} studentData - { id, name, email, department, classroom_id, status }
     * @returns {Promise<Object>} Created student
     */
    async createStudent(studentData) {
        const response = await fetchWithAuth(`${API_BASE_URL}/students`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(studentData),
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to create student (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Update an existing student
     * @param {string} id - Student ID
     * @param {Object} studentData - Fields to update
     * @returns {Promise<Object>} Updated student
     */
    async updateStudent(id, studentData) {
        const response = await fetchWithAuth(`${API_BASE_URL}/students/${encodeURIComponent(id)}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(studentData),
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to update student ${id} (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Delete a student by ID
     * @param {string} id - Student ID
     * @returns {Promise<Object>} Result
     */
    async deleteStudent(id) {
        const response = await fetchWithAuth(`${API_BASE_URL}/students/${encodeURIComponent(id)}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            }
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to delete student ${id} (${response.status})`);
        }
        return await response.json();
    },

    // ==========================================
    // CLASSROOMS API
    // ==========================================

    /**
     * Fetch list of classrooms with optional query filters
     * @param {Object} params - { department, status }
     * @returns {Promise<Array>} List of classrooms
     */
    async getClassrooms(params = {}) {
        const query = new URLSearchParams();
        if (params.department) query.append("department", params.department.trim());
        if (params.status) query.append("status", params.status);

        const url = `${API_BASE_URL}/classrooms${query.toString() ? '?' + query.toString() : ''}`;
        const response = await fetchWithAuth(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch classrooms (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Get a single classroom by ID
     * @param {number|string} id - Classroom ID (int)
     * @returns {Promise<Object>} Classroom details
     */
    async getClassroom(id) {
        const response = await fetchWithAuth(`${API_BASE_URL}/classrooms/${encodeURIComponent(id)}`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch classroom ${id}`);
        }
        return await response.json();
    },

    /**
     * Create a new classroom in MySQL database
     * @param {Object} classroomData - { name, department, capacity, status }
     * @returns {Promise<Object>} Created classroom
     */
    async createClassroom(classroomData) {
        const response = await fetchWithAuth(`${API_BASE_URL}/classrooms`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(classroomData),
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to create classroom (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Update an existing classroom
     * @param {number|string} id - Classroom ID
     * @param {Object} classroomData - Fields to update
     * @returns {Promise<Object>} Updated classroom
     */
    async updateClassroom(id, classroomData) {
        const response = await fetchWithAuth(`${API_BASE_URL}/classrooms/${encodeURIComponent(id)}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(classroomData),
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to update classroom ${id} (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Delete a classroom by ID
     * @param {number|string} id - Classroom ID
     * @returns {Promise<Object>} Result
     */
    async deleteClassroom(id) {
        const response = await fetchWithAuth(`${API_BASE_URL}/classrooms/${encodeURIComponent(id)}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            }
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to delete classroom ${id} (${response.status})`);
        }
        return await response.json();
    },

    // ==========================================
    // ATTENDANCE API
    // ==========================================

    /**
     * Fetch attendance records with optional filters
     * @param {Object} params - { date, student_id, classroom_id, status, department, search, limit, offset }
     * @returns {Promise<Array>} List of attendance records
     */
    async getAttendance(params = {}) {
        const query = new URLSearchParams();
        if (params.date) query.append("date", params.date);
        if (params.student_id) query.append("student_id", params.student_id);
        if (params.classroom_id) query.append("classroom_id", params.classroom_id);
        if (params.status && params.status !== "All") query.append("status", params.status);
        if (params.department && params.department !== "All") query.append("department", params.department);
        if (params.search) query.append("search", params.search.trim());
        if (params.limit) query.append("limit", params.limit);
        if (params.offset) query.append("offset", params.offset);

        const url = `${API_BASE_URL}/attendance${query.toString() ? '?' + query.toString() : ''}`;
        const response = await fetchWithAuth(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch attendance (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Get summary and records of attendance for today
     * @returns {Promise<Object>} AttendanceSummary object
     */
    async getTodayAttendance() {
        const response = await fetchWithAuth(`${API_BASE_URL}/attendance/today`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch today's attendance (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Get attendance history for a specific student
     * @param {string} studentId
     * @returns {Promise<Array>} List of attendance records
     */
    async getStudentAttendance(studentId) {
        const response = await fetchWithAuth(`${API_BASE_URL}/attendance/student/${encodeURIComponent(studentId)}`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch attendance for student ${studentId}`);
        }
        return await response.json();
    },

    /**
     * Create attendance record (Manual or Face AI)
     * @param {Object} data - { student_id, classroom_id, date, status, verification_method, confidence }
     * @returns {Promise<Object>} Created attendance record
     */
    async createAttendance(data) {
        const response = await fetchWithAuth(`${API_BASE_URL}/attendance`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to record attendance (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Update an attendance record
     * @param {number|string} id - Attendance record ID
     * @param {Object} data - { status, verification_method, confidence, classroom_id }
     * @returns {Promise<Object>} Updated record
     */
    async updateAttendance(id, data) {
        const response = await fetchWithAuth(`${API_BASE_URL}/attendance/${encodeURIComponent(id)}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to update attendance record ${id}`);
        }
        return await response.json();
    },

    /**
     * Delete an attendance record
     * @param {number|string} id - Attendance record ID
     * @returns {Promise<Object>} Result
     */
    async deleteAttendance(id) {
        const response = await fetchWithAuth(`${API_BASE_URL}/attendance/${encodeURIComponent(id)}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            }
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to delete attendance record ${id}`);
        }
        return await response.json();
    },

    // ==========================================
    // DASHBOARD AGGREGATION API
    // ==========================================

    /**
     * Fetch all dashboard data concurrently from FastAPI + MySQL
     * @returns {Promise<Object>} Aggregated dashboard metrics
     */
    async getDashboardData() {
        const [students, classrooms, todaySummary, recentAttendance] = await Promise.all([
            this.getStudents(),
            this.getClassrooms(),
            this.getTodayAttendance(),
            this.getAttendance({ limit: 15 })
        ]);

        const totalStudents = students.length;
        const totalClassrooms = classrooms.length;
        const activeClassrooms = classrooms.filter(c => (c.status || '').toLowerCase() === 'active').length;
        const presentToday = todaySummary.present_count ?? 0;

        let attendanceRate = 0;
        if (totalStudents > 0) {
            attendanceRate = Math.round((presentToday / totalStudents) * 100);
        } else if (todaySummary.total_records > 0) {
            attendanceRate = Math.round((presentToday / todaySummary.total_records) * 100);
        }

        return {
            students,
            classrooms,
            totalStudents,
            totalClassrooms,
            activeClassrooms,
            presentToday,
            attendanceRate,
            todaySummary,
            recentAttendance
        };
    },

    // ==========================================
    // LIVE MONITORING API
    // ==========================================

    /**
     * Get live monitoring status from backend
     * @returns {Promise<Object>} Monitoring status
     */
    async getMonitoringStatus() {
        const response = await fetchWithAuth(`${API_BASE_URL}/monitoring/status`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch monitoring status (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Start live monitoring session
     * @param {number|null} classroomId
     * @returns {Promise<Object>} Status response
     */
    async startMonitoring(classroomId = null) {
        const payload = classroomId ? { classroom_id: parseInt(classroomId, 10) } : {};
        const response = await fetchWithAuth(`${API_BASE_URL}/monitoring/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to start monitoring (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Stop live monitoring session
     * @returns {Promise<Object>} Status response
     */
    async stopMonitoring() {
        const response = await fetchWithAuth(`${API_BASE_URL}/monitoring/stop`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to stop monitoring (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Process single frame for face detection via REST
     * @param {string} base64Image
     * @returns {Promise<Object>} Detection result
     */
    async detectFacesFrame(base64Image) {
        const response = await fetchWithAuth(`${API_BASE_URL}/monitoring/detect-faces`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: base64Image })
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed face detection REST request (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Enroll a student's face embedding from base64 image string
     * @param {string} studentId
     * @param {string} base64Image
     * @returns {Promise<Object>} Enrollment result
     */
    async enrollStudentFace(studentId, base64Image) {
        const response = await fetchWithAuth(`${API_BASE_URL}/face-recognition/enroll/${encodeURIComponent(studentId)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: base64Image })
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Face enrollment failed (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Get face enrollment status for a student
     * @param {string} studentId
     * @returns {Promise<Object>} Status payload { enrolled: bool, count: int }
     */
    async getFaceEnrollmentStatus(studentId) {
        const response = await fetchWithAuth(`${API_BASE_URL}/face-recognition/status/${encodeURIComponent(studentId)}`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch face enrollment status (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Delete face enrollment for a student
     * @param {string} studentId
     * @returns {Promise<Object>} Result payload
     */
    async deleteStudentFaceEnrollment(studentId) {
        const response = await fetchWithAuth(`${API_BASE_URL}/face-recognition/enrollment/${encodeURIComponent(studentId)}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to delete face enrollment (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Record automatic Face AI attendance for a recognized student
     * @param {string} studentId
     * @param {number} classroomId
     * @param {number} confidence
     * @returns {Promise<Object>} Response payload { status: 'marked'|'already_marked'|'rejected' }
     */
    async recordFaceAttendance(studentId, classroomId, confidence = 0.87) {
        const response = await fetchWithAuth(`${API_BASE_URL}/attendance/face`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id: studentId,
                classroom_id: parseInt(classroomId, 10),
                confidence: parseFloat(confidence)
            })
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Automatic face attendance failed (${response.status})`);
        }
        return await response.json();
    },

    /**
     * Connect to WebSocket live monitoring channel
     * @param {Function} onMessageCallback
     * @returns {WebSocket}
     */
    connectMonitoringWebSocket(onMessageCallback) {
        const token = typeof AuthService !== "undefined"
            ? AuthService.getToken()
            : (localStorage.getItem("sc_token") || sessionStorage.getItem("sc_token"));
        const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsHost = API_BASE_URL.replace(/^https?:\/\//, "");
        const wsUrl = `${wsProtocol}//${wsHost}/monitoring/ws${token ? '?token=' + encodeURIComponent(token) : ''}`;
        
        try {
            const ws = new WebSocket(wsUrl);
            ws.onmessage = (event) => {
                try {
                    const parsed = JSON.parse(event.data);
                    if (typeof onMessageCallback === "function") {
                        onMessageCallback(parsed);
                    }
                } catch (e) {
                    console.error("Error parsing WS message:", e);
                }
            };
            return ws;
        } catch (e) {
            console.warn("Could not initiate WebSocket connection:", e);
            return null;
        }
    },

    // ==========================================
    // PRIVACY & FAIRNESS APIS
    // ==========================================

    async getStudentConsents(params = {}) {
        const query = new URLSearchParams();
        if (params.status) query.append("status", params.status);
        if (params.department) query.append("department", params.department);
        if (params.search) query.append("search", params.search.trim());
        if (params.limit) query.append("limit", params.limit);
        if (params.offset) query.append("offset", params.offset);

        const url = `${API_BASE_URL}/privacy/consent${query.toString() ? '?' + query.toString() : ''}`;
        const response = await fetchWithAuth(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch consent records (${response.status})`);
        }
        return await response.json();
    },

    async getStudentConsent(studentId) {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/consent/${encodeURIComponent(studentId)}`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch student consent (${response.status})`);
        }
        return await response.json();
    },

    async updateStudentConsent(studentId, consentData) {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/consent/${encodeURIComponent(studentId)}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(consentData)
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to update student consent (${response.status})`);
        }
        return await response.json();
    },

    async withdrawStudentConsent(studentId, reason = "Consent withdrawn via portal") {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/consent/${encodeURIComponent(studentId)}/withdraw`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reason })
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to withdraw consent (${response.status})`);
        }
        return await response.json();
    },

    async getRetentionPolicies() {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/retention`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch retention policies (${response.status})`);
        }
        return await response.json();
    },

    async updateRetentionPolicy(policyId, updateData) {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/retention/${encodeURIComponent(policyId)}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updateData)
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to update retention policy (${response.status})`);
        }
        return await response.json();
    },

    async purgeRetentionData(policyName) {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/retention/purge/${encodeURIComponent(policyName)}`, {
            method: "POST"
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to purge retention data (${response.status})`);
        }
        return await response.json();
    },

    async purgeStudentData(studentId, options = {}) {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/student/${encodeURIComponent(studentId)}/purge`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(options)
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to execute student data purge (${response.status})`);
        }
        return await response.json();
    },

    async getAuditLogs(params = {}) {
        const query = new URLSearchParams();
        if (params.action) query.append("action", params.action);
        if (params.target_type) query.append("target_type", params.target_type);
        if (params.limit) query.append("limit", params.limit);
        if (params.offset) query.append("offset", params.offset);

        const url = `${API_BASE_URL}/privacy/audit-logs${query.toString() ? '?' + query.toString() : ''}`;
        const response = await fetchWithAuth(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch audit logs (${response.status})`);
        }
        return await response.json();
    },

    async getFairnessEvaluation() {
        const response = await fetchWithAuth(`${API_BASE_URL}/privacy/fairness`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch fairness evaluation (${response.status})`);
        }
        return await response.json();
    },

    // ==========================================
    // RESEARCH METHODOLOGY APIS
    // ==========================================

    async getResearchMethodology() {
        const response = await fetchWithAuth(`${API_BASE_URL}/research/methodology`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch research methodology (${response.status})`);
        }
        return await response.json();
    },

    async getResearchBenchmarks() {
        const response = await fetchWithAuth(`${API_BASE_URL}/research/benchmarks`);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `Failed to fetch research benchmarks (${response.status})`);
        }
        return await response.json();
    }
};

// Make available globally
window.API_BASE_URL = API_BASE_URL;
window.ApiService = ApiService;
window.fetchWithAuth = fetchWithAuth;
