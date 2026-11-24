/**
 * Real-Time AI Camera Monitoring & Face Analysis Controller
 * Human-Centric Smart Classroom Monitoring System
 * 
 * Genuine Computer Vision Integration:
 * - Real Browser Webcam Capture (getUserMedia)
 * - Authenticated WebSocket Frame Pipeline (~6-8 FPS)
 * - OpenCV Haar Cascade Face Detection
 * - OpenCV SFace 128-D Cosine Face Recognition
 * - MySQL Student Database Matching
 * - Phase 4 Automated Face AI Attendance
 * - Zero simulated/fake student names or random telemetry
 */

document.addEventListener("DOMContentLoaded", () => {
    initRealAIMonitoring();
});

function initRealAIMonitoring() {
    const canvas = document.getElementById("camera-feed-canvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    canvas.width = 1280;
    canvas.height = 720;

    // Camera and Stream State
    let isMonitoringActive = false;
    let isPaused = false;
    let mediaStream = null;
    let videoEl = null;
    let animId = null;
    let lastFrameSentTime = 0;
    const FRAME_SEND_INTERVAL = 140; // ~7 FPS frame processing

    // Backend WebSocket & Detection State
    let wsMonitoring = null;
    let detectedFaces = [];
    let lastDetectionTime = null;
    let selectedClassroom = null;
    let totalClassroomStudents = 0;

    // Telemetry and HUD counters
    let detectedCount = 0;
    let recognizedCount = 0;
    let unknownCount = 0;

    // DOM Elements - Top Widgets
    const widgetAttCount = document.getElementById("widget-attendance-count");
    const widgetAttTotal = document.getElementById("widget-attendance-total");
    const widgetAttBar = document.getElementById("widget-attendance-bar");
    const widgetEmotionVal = document.getElementById("widget-emotion-val");
    const widgetAttentionVal = document.getElementById("widget-attention-val");
    const widgetTempVal = document.getElementById("widget-temp-val");

    // DOM Elements - HUD Overlays
    const statusDotEl = document.getElementById("monitoring-status-dot");
    const statusTextEl = document.getElementById("monitoring-status-text");
    const camLabelEl = document.getElementById("monitoring-cam-label");
    const lastUpdateEl = document.getElementById("monitoring-last-update");
    const noFaceOverlay = document.getElementById("hud-no-face-overlay");

    // HUD Telemetry Grid Elements
    const hudMonitoringStatus = document.getElementById("hud-monitoring-status");
    const hudCameraStatus = document.getElementById("hud-camera-status");
    const hudFaceDetectionStatus = document.getElementById("hud-face-detection-status");
    const hudFaceRecognitionStatus = document.getElementById("hud-face-recognition-status");
    const hudAutoAttendanceStatus = document.getElementById("hud-auto-attendance-status");
    const hudDetectedFacesCount = document.getElementById("hud-detected-faces-count");
    const hudRecognizedCount = document.getElementById("hud-recognized-count");
    const hudUnknownCount = document.getElementById("hud-unknown-count");
    const hudLastUpdateTime = document.getElementById("hud-last-update-time");

    // Interactive Controls
    const clsSelect = document.getElementById("monitoring-classroom-select");
    const btnStart = document.getElementById("btn-start-monitoring");
    const btnStop = document.getElementById("btn-stop-monitoring");
    const btnRetry = document.getElementById("btn-retry-connection");
    const btnPlayPause = document.getElementById("feed-play-pause-btn");
    const btnSnapshot = document.getElementById("feed-snapshot-btn");
    const btnWebcam = document.getElementById("feed-webcam-btn");

    // Panels
    const studentProfilesContainer = document.getElementById("active-student-profiles-container");
    const profilesCountBadge = document.getElementById("active-profiles-count-badge");
    const alertsContainer = document.getElementById("live-alerts-container");
    const clearAlertsBtn = document.getElementById("clear-alerts-btn");

    // Helper: Toast Notifications
    const notify = (msg, type = "info") => {
        if (typeof showToast === "function") {
            showToast(msg, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${msg}`);
        }
    };

    // Helper: Push Live Alert
    const pushAlert = (title, message, level = "info") => {
        if (!alertsContainer) return;
        const emptyMsg = alertsContainer.querySelector("p.text-center");
        if (emptyMsg) emptyMsg.remove();

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const isError = level === "error" || level === "critical";
        const isSuccess = level === "success";

        const alertItem = document.createElement("div");
        alertItem.className = `flex gap-3 p-3 rounded-xl border ${
            isError ? "bg-error/10 border-error/40 text-error" :
            isSuccess ? "bg-tertiary/10 border-tertiary/40 text-tertiary" :
            "bg-primary/10 border-primary/40 text-primary"
        } transition-all duration-300`;

        alertItem.innerHTML = `
            <span class="material-symbols-outlined text-lg shrink-0 mt-0.5">
                ${isError ? "warning" : isSuccess ? "check_circle" : "info"}
            </span>
            <div class="overflow-hidden">
                <p class="text-xs font-bold leading-tight">${title}</p>
                <p class="text-[10px] text-on-surface-variant/80 mt-0.5">${message}</p>
                <p class="text-[9px] opacity-60 font-mono mt-1">${timeStr} • ${level.toUpperCase()}</p>
            </div>
        `;

        alertsContainer.prepend(alertItem);
        if (alertsContainer.children.length > 10) {
            alertsContainer.lastElementChild.remove();
        }
    };

    // =========================================================================
    // CANVAS RENDERING & HUD LOOP
    // =========================================================================

    function renderStandbyCanvas() {
        ctx.fillStyle = "#0c0f10";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Grid lines
        ctx.strokeStyle = "rgba(173, 198, 255, 0.05)";
        ctx.lineWidth = 1;
        const gridSize = 40;
        for (let x = 0; x < canvas.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }

        // Center Standby Icon / Text
        ctx.strokeStyle = "rgba(173, 198, 255, 0.15)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, 70, 0, Math.PI * 2);
        ctx.stroke();

        ctx.font = "bold 14px Inter, sans-serif";
        ctx.fillStyle = "rgba(224, 227, 229, 0.5)";
        ctx.textAlign = "center";
        ctx.fillText("CAMERA STANDBY", canvas.width / 2, canvas.height / 2 + 5);
        ctx.font = "11px Inter, sans-serif";
        ctx.fillStyle = "rgba(224, 227, 229, 0.3)";
        ctx.fillText("Select a classroom and click Start Monitoring", canvas.width / 2, canvas.height / 2 + 25);
        ctx.textAlign = "left";
    }

    function renderActiveCameraStream() {
        if (!isMonitoringActive || isPaused) return;

        // 1. Draw Real Video Stream to Canvas
        if (videoEl && videoEl.readyState >= 2) {
            ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);

            // Subtle Cyber Border
            ctx.strokeStyle = "rgba(173, 198, 255, 0.3)";
            ctx.lineWidth = 2;
            ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);

            // Live Indicator in upper-left corner
            ctx.fillStyle = "rgba(239, 68, 68, 0.9)";
            ctx.beginPath();
            ctx.arc(28, 28, 5, 0, Math.PI * 2);
            ctx.fill();

            ctx.font = "bold 11px Inter, sans-serif";
            ctx.fillStyle = "#ffffff";
            ctx.fillText("LIVE CAMERA STREAM", 40, 32);

            // 2. Draw Real OpenCV Face Detections and SFace Recognitions
            if (detectedFaces && detectedFaces.length > 0) {
                if (noFaceOverlay) noFaceOverlay.classList.add("hidden");

                detectedFaces.forEach(face => {
                    const x = face.x;
                    const y = face.y;
                    const w = face.width;
                    const h = face.height;
                    const isRecognized = !!face.recognized;
                    const studentName = face.name || (isRecognized ? "Recognized Student" : "Unknown Person");
                    const studentId = face.student_id;
                    const similarityPct = Math.round((face.similarity || 0) * 100);

                    const strokeColor = isRecognized ? "#4ae176" : "#ffb4ab";
                    const fillColor = isRecognized ? "rgba(74, 225, 118, 0.12)" : "rgba(255, 180, 171, 0.12)";

                    // Bounding Box
                    ctx.strokeStyle = strokeColor;
                    ctx.lineWidth = 3;
                    ctx.strokeRect(x, y, w, h);

                    // Translucent Face Fill
                    ctx.fillStyle = fillColor;
                    ctx.fillRect(x, y, w, h);

                    // Corner Accent Brackets
                    const bracketLen = Math.min(18, w / 4);
                    ctx.strokeStyle = isRecognized ? "#6bff8f" : "#ff897d";
                    ctx.lineWidth = 3;

                    // Top-Left
                    ctx.beginPath(); ctx.moveTo(x + bracketLen, y); ctx.lineTo(x, y); ctx.lineTo(x, y + bracketLen); ctx.stroke();
                    // Top-Right
                    ctx.beginPath(); ctx.moveTo(x + w - bracketLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + bracketLen); ctx.stroke();
                    // Bottom-Left
                    ctx.beginPath(); ctx.moveTo(x, y + h - bracketLen); ctx.lineTo(x, y + h); ctx.lineTo(x + bracketLen, y + h); ctx.stroke();
                    // Bottom-Right
                    ctx.beginPath(); ctx.moveTo(x + w, y + h - bracketLen); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - bracketLen, y + h); ctx.stroke();

                    // Information Tag Label
                    let primaryLabel = isRecognized ? `${studentName} (${similarityPct}%)` : `Unknown Person`;
                    let secondaryLabel = "";

                    if (isRecognized) {
                        const attStatus = face.attendance ? face.attendance.status : "not_marked";
                        if (attStatus === "marked") {
                            secondaryLabel = "✓ Attendance Marked";
                        } else if (attStatus === "already_marked") {
                            secondaryLabel = "✓ Already Present";
                        } else {
                            secondaryLabel = "Attendance Not Marked";
                        }
                    } else {
                        secondaryLabel = "Not Registered in Database";
                    }

                    ctx.font = "bold 12px Inter, sans-serif";
                    const primaryWidth = ctx.measureText(primaryLabel).width;
                    ctx.font = "10px Inter, sans-serif";
                    const secondaryWidth = ctx.measureText(secondaryLabel).width;
                    const tagWidth = Math.max(primaryWidth, secondaryWidth) + 16;
                    const tagHeight = 36;
                    const tagY = Math.max(8, y - tagHeight - 6);

                    // Label Box Background
                    ctx.fillStyle = isRecognized ? "rgba(0, 49, 17, 0.9)" : "rgba(105, 0, 5, 0.9)";
                    ctx.strokeStyle = strokeColor;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.roundRect(x, tagY, tagWidth, tagHeight, 6);
                    ctx.fill();
                    ctx.stroke();

                    // Label Texts
                    ctx.fillStyle = isRecognized ? "#6bff8f" : "#ffdad6";
                    ctx.font = "bold 12px Inter, sans-serif";
                    ctx.fillText(primaryLabel, x + 8, tagY + 16);

                    ctx.fillStyle = isRecognized ? "#adc6ff" : "#ffb4ab";
                    ctx.font = "10px Inter, sans-serif";
                    ctx.fillText(secondaryLabel, x + 8, tagY + 30);
                });
            } else {
                // Explicit Requirement 3: If no face is detected, show "NO FACE DETECTED"
                if (noFaceOverlay) noFaceOverlay.classList.remove("hidden");

                ctx.save();
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
                ctx.fillRect(canvas.width / 2 - 120, canvas.height / 2 - 24, 240, 48);
                ctx.strokeStyle = "rgba(255, 180, 171, 0.5)";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(canvas.width / 2 - 120, canvas.height / 2 - 24, 240, 48);

                ctx.font = "bold 13px Inter, monospace";
                ctx.fillStyle = "#ffb4ab";
                ctx.textAlign = "center";
                ctx.fillText("NO FACE DETECTED", canvas.width / 2, canvas.height / 2 + 5);
                ctx.restore();
            }

            // 3. Real Frame Capture & WebSocket Transmission (~7 FPS)
            const now = Date.now();
            if (wsMonitoring && wsMonitoring.readyState === WebSocket.OPEN && (now - lastFrameSentTime >= FRAME_SEND_INTERVAL)) {
                lastFrameSentTime = now;
                try {
                    // Send frame image at 0.6 quality for optimal real-time throughput
                    const frameDataUrl = canvas.toDataURL("image/jpeg", 0.6);
                    wsMonitoring.send(JSON.stringify({
                        type: "frame",
                        image: frameDataUrl
                    }));
                } catch (err) {
                    console.warn("WebSocket frame transmission error:", err);
                }
            }
        }
    }

    function monitoringLoop() {
        if (isMonitoringActive && !isPaused) {
            renderActiveCameraStream();
        }
        animId = requestAnimationFrame(monitoringLoop);
    }
    renderStandbyCanvas();
    animId = requestAnimationFrame(monitoringLoop);

    // =========================================================================
    // DYNAMIC UI UPDATERS
    // =========================================================================

    function updateHUDTelemetry(msg) {
        const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        detectedCount = msg.faces_detected ?? (msg.faces ? msg.faces.length : 0);
        recognizedCount = msg.recognized_count ?? (msg.faces ? msg.faces.filter(f => f.recognized).length : 0);
        unknownCount = msg.unknown_count ?? (detectedCount - recognizedCount);

        if (hudDetectedFacesCount) hudDetectedFacesCount.textContent = detectedCount;
        if (hudRecognizedCount) hudRecognizedCount.textContent = recognizedCount;
        if (hudUnknownCount) hudUnknownCount.textContent = unknownCount;
        if (hudLastUpdateTime) hudLastUpdateTime.textContent = timeNow;
        if (lastUpdateEl) lastUpdateEl.textContent = `LAST_UPDATE: ${timeNow}`;

        // Top HUD Active States
        if (hudFaceDetectionStatus) {
            hudFaceDetectionStatus.textContent = isMonitoringActive ? "ACTIVE" : "INACTIVE";
            hudFaceDetectionStatus.className = isMonitoringActive ? "text-xs font-bold font-mono text-tertiary" : "text-xs font-bold font-mono text-on-surface-variant";
        }
        if (hudFaceRecognitionStatus) {
            hudFaceRecognitionStatus.textContent = isMonitoringActive ? "ACTIVE" : "INACTIVE";
            hudFaceRecognitionStatus.className = isMonitoringActive ? "text-xs font-bold font-mono text-primary" : "text-xs font-bold font-mono text-on-surface-variant";
        }
        if (hudAutoAttendanceStatus) {
            const hasClassroom = !!selectedClassroom;
            hudAutoAttendanceStatus.textContent = (isMonitoringActive && hasClassroom) ? "ACTIVE" : "INACTIVE";
            hudAutoAttendanceStatus.className = (isMonitoringActive && hasClassroom) ? "text-xs font-bold font-mono text-secondary" : "text-xs font-bold font-mono text-on-surface-variant";
        }

        // Active Student Profiles Cards
        renderStudentProfiles(msg.faces || []);
    }

    function renderStudentProfiles(faces) {
        if (!studentProfilesContainer) return;

        if (profilesCountBadge) {
            profilesCountBadge.textContent = `${faces.length} Active ${faces.length === 1 ? 'Face' : 'Faces'}`;
        }

        if (!faces || faces.length === 0) {
            studentProfilesContainer.innerHTML = `
                <div class="col-span-full py-10 text-center glass-card rounded-2xl border border-white/10">
                    <span class="material-symbols-outlined text-4xl text-on-surface-variant/40 mb-2">person_search</span>
                    <p class="text-sm font-semibold text-on-surface">No faces currently detected in camera view</p>
                    <p class="text-xs text-on-surface-variant/60 mt-1">Camera is streaming. Real-time detected faces will appear here automatically.</p>
                </div>
            `;
            return;
        }

        studentProfilesContainer.innerHTML = "";

        faces.forEach((face, idx) => {
            const isRecognized = !!face.recognized;
            const name = face.name || (isRecognized ? "Recognized Student" : "Unknown Person");
            const studentId = face.student_id || "Not Registered";
            const simScore = Math.round((face.similarity || 0) * 100);

            let attStatusText = "Attendance Not Marked";
            let attStatusClass = "bg-white/5 border border-white/10 text-on-surface-variant";
            if (isRecognized && face.attendance) {
                if (face.attendance.status === "marked") {
                    attStatusText = "Attendance Marked";
                    attStatusClass = "bg-tertiary/20 border border-tertiary/40 text-tertiary font-bold";
                } else if (face.attendance.status === "already_marked") {
                    attStatusText = "Already Present";
                    attStatusClass = "bg-primary/20 border border-primary/40 text-primary font-bold";
                }
            }

            const card = document.createElement("div");
            card.className = `glass-card p-4 rounded-2xl border ${
                isRecognized ? "border-tertiary/30 bg-tertiary/5" : "border-error/30 bg-error/5"
            } transition-all duration-300`;

            card.innerHTML = `
                <div class="flex items-start justify-between gap-3">
                    <div class="w-12 h-12 rounded-xl flex items-center justify-center ${
                        isRecognized ? "bg-tertiary/20 text-tertiary" : "bg-error/20 text-error"
                    } shrink-0">
                        <span class="material-symbols-outlined text-2xl">
                            ${isRecognized ? "person" : "person_off"}
                        </span>
                    </div>
                    <div class="flex-1 min-w-0">
                        <h4 class="font-bold text-sm text-on-surface truncate">${name}</h4>
                        <p class="text-[11px] text-on-surface-variant font-mono mt-0.5">ID: ${studentId}</p>
                    </div>
                </div>

                <div class="mt-3 pt-3 border-t border-white/10 space-y-2">
                    <div class="flex justify-between items-center text-[11px]">
                        <span class="text-on-surface-variant">Recognition:</span>
                        <span class="font-bold ${isRecognized ? "text-tertiary" : "text-error"}">
                            ${isRecognized ? `Recognized (${simScore}%)` : "Unknown / Not Registered"}
                        </span>
                    </div>
                    <div class="flex justify-between items-center text-[11px]">
                        <span class="text-on-surface-variant">Attendance:</span>
                        <span class="px-2 py-0.5 rounded text-[10px] ${attStatusClass}">
                            ${attStatusText}
                        </span>
                    </div>
                </div>
            `;
            studentProfilesContainer.appendChild(card);
        });
    }

    async function syncTodayAttendanceWidget() {
        if (typeof ApiService === "undefined" || !ApiService.getTodayAttendance) return;
        try {
            const todayData = await ApiService.getTodayAttendance();
            const presentCount = todayData.present_count ?? 0;
            const totalCount = totalClassroomStudents > 0 ? totalClassroomStudents : (todayData.total_records || presentCount || 1);

            if (widgetAttCount) widgetAttCount.textContent = presentCount;
            if (widgetAttTotal) widgetAttTotal.textContent = `/ ${totalCount}`;
            if (widgetAttBar) {
                const pct = Math.min(100, Math.round((presentCount / Math.max(1, totalCount)) * 100));
                widgetAttBar.style.width = `${pct}%`;
            }
        } catch (err) {
            console.warn("Could not sync today attendance widget:", err);
        }
    }

    // =========================================================================
    // CLASSROOMS DROPDOWN POPULATION
    // =========================================================================

    async function loadClassrooms() {
        if (!clsSelect || typeof ApiService === "undefined" || !ApiService.getClassrooms) return;
        try {
            const classrooms = await ApiService.getClassrooms();
            clsSelect.innerHTML = '<option value="">Select Classroom...</option>';
            classrooms.forEach(c => {
                const opt = document.createElement("option");
                opt.value = c.id;
                opt.textContent = `${c.name} (${c.department || 'General'})`;
                clsSelect.appendChild(opt);
            });
        } catch (err) {
            console.warn("Error loading classrooms for monitoring:", err);
        }
    }
    loadClassrooms();

    if (clsSelect) {
        clsSelect.addEventListener("change", async (e) => {
            const val = e.target.value;
            selectedClassroom = val ? parseInt(val, 10) : null;
            if (selectedClassroom && typeof ApiService !== "undefined" && ApiService.getStudents) {
                try {
                    const students = await ApiService.getStudents({ classroom_id: selectedClassroom });
                    totalClassroomStudents = students.length;
                    syncTodayAttendanceWidget();
                } catch (err) {
                    console.warn("Error fetching classroom student count:", err);
                }
            } else {
                totalClassroomStudents = 0;
            }
        });
    }

    // =========================================================================
    // WEBCAM & MONITORING SESSION LIFECYCLE
    // =========================================================================

    async function startCameraMonitoring() {
        if (!selectedClassroom) {
            notify("Please select a classroom before starting automatic monitoring.", "error");
            if (clsSelect) clsSelect.focus();
            return;
        }

        notify("Requesting browser camera permission...", "info");

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            notify("Camera API unavailable. Use HTTPS or localhost.", "error");
            if (statusTextEl) statusTextEl.textContent = "CAMERA RESTRICTED";
            return;
        }

        try {
            // Real Webcam Stream Request
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "user"
                },
                audio: false
            });

            mediaStream = stream;
            videoEl = document.createElement("video");
            videoEl.srcObject = stream;
            videoEl.autoplay = true;
            videoEl.playsInline = true;
            videoEl.muted = true;
            await videoEl.play();

            isMonitoringActive = true;
            isPaused = false;

            // Update UI & Buttons
            if (statusDotEl) statusDotEl.className = "w-2.5 h-2.5 rounded-full bg-tertiary animate-pulse";
            if (statusTextEl) statusTextEl.textContent = "MONITORING ACTIVE";
            if (camLabelEl) camLabelEl.textContent = "CAMERA: CONNECTED (LIVE)";
            if (hudMonitoringStatus) {
                hudMonitoringStatus.textContent = "ACTIVE";
                hudMonitoringStatus.className = "text-xs font-bold font-mono text-tertiary";
            }
            if (hudCameraStatus) {
                hudCameraStatus.textContent = "CONNECTED";
                hudCameraStatus.className = "text-xs font-bold font-mono text-tertiary";
            }
            if (btnStart) btnStart.classList.add("hidden");
            if (btnStop) btnStop.classList.remove("hidden");
            if (btnWebcam) {
                btnWebcam.classList.add("bg-primary", "text-on-primary");
                btnWebcam.classList.remove("glass-card");
            }

            // Call Backend POST /api/monitoring/start
            if (typeof ApiService !== "undefined" && ApiService.startMonitoring) {
                await ApiService.startMonitoring(selectedClassroom);
            }

            pushAlert("Monitoring Started", `Live face detection session active for Classroom ${selectedClassroom}`, "success");
            notify("Live camera stream & automatic face analysis active!", "success");

            // Initialize or connect WebSocket
            ensureWebSocketConnection();

        } catch (err) {
            console.error("Camera access error:", err);
            isMonitoringActive = false;

            let userMsg = "Could not access camera: " + err.message;
            if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
                userMsg = "Camera permission was denied. Please allow camera access in your browser settings.";
            } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
                userMsg = "No camera hardware detected. Please connect a webcam.";
            } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
                userMsg = "Webcam is already in use by another program.";
            }

            if (statusTextEl) statusTextEl.textContent = "CAMERA ERROR";
            if (statusDotEl) statusDotEl.className = "w-2.5 h-2.5 rounded-full bg-error";
            if (hudCameraStatus) hudCameraStatus.textContent = "ERROR";

            pushAlert("Camera Access Failed", userMsg, "error");
            notify(userMsg, "error");
        }
    }

    async function stopCameraMonitoring() {
        isMonitoringActive = false;
        isPaused = false;
        detectedFaces = [];

        // Explicit Requirement 2: Release camera tracks when monitoring stops
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => {
                track.stop();
            });
            mediaStream = null;
        }
        if (videoEl) {
            videoEl.srcObject = null;
            videoEl = null;
        }

        // Hide overlay and re-render standby
        if (noFaceOverlay) noFaceOverlay.classList.add("hidden");
        renderStandbyCanvas();

        // Update UI & Buttons
        if (statusDotEl) statusDotEl.className = "w-2.5 h-2.5 rounded-full bg-error";
        if (statusTextEl) statusTextEl.textContent = "MONITORING STOPPED";
        if (camLabelEl) camLabelEl.textContent = "CAMERA: DISCONNECTED";
        if (hudMonitoringStatus) {
            hudMonitoringStatus.textContent = "STOPPED";
            hudMonitoringStatus.className = "text-xs font-bold font-mono text-error";
        }
        if (hudCameraStatus) {
            hudCameraStatus.textContent = "DISCONNECTED";
            hudCameraStatus.className = "text-xs font-bold font-mono text-on-surface-variant";
        }
        if (hudFaceDetectionStatus) {
            hudFaceDetectionStatus.textContent = "INACTIVE";
            hudFaceDetectionStatus.className = "text-xs font-bold font-mono text-on-surface-variant";
        }
        if (hudFaceRecognitionStatus) {
            hudFaceRecognitionStatus.textContent = "INACTIVE";
            hudFaceRecognitionStatus.className = "text-xs font-bold font-mono text-on-surface-variant";
        }
        if (hudAutoAttendanceStatus) {
            hudAutoAttendanceStatus.textContent = "INACTIVE";
            hudAutoAttendanceStatus.className = "text-xs font-bold font-mono text-on-surface-variant";
        }

        if (btnStart) btnStart.classList.remove("hidden");
        if (btnStop) btnStop.classList.add("hidden");
        if (btnWebcam) {
            btnWebcam.classList.remove("bg-primary", "text-on-primary");
            btnWebcam.classList.add("glass-card");
        }

        // Reset Dynamic Profiles
        renderStudentProfiles([]);

        // Call Backend POST /api/monitoring/stop
        if (typeof ApiService !== "undefined" && ApiService.stopMonitoring) {
            try {
                await ApiService.stopMonitoring();
            } catch (err) {
                console.warn("Backend stop monitoring call error:", err);
            }
        }

        pushAlert("Monitoring Stopped", "Camera and AI pipelines released.", "info");
        notify("Monitoring session terminated. Camera tracks released.", "info");
    }

    // =========================================================================
    // AUTHENTICATED WEBSOCKET INTEGRATION
    // =========================================================================

    function ensureWebSocketConnection() {
        if (wsMonitoring && wsMonitoring.readyState === WebSocket.OPEN) {
            return;
        }

        if (typeof ApiService === "undefined" || !ApiService.connectMonitoringWebSocket) {
            console.warn("ApiService.connectMonitoringWebSocket not defined.");
            return;
        }

        wsMonitoring = ApiService.connectMonitoringWebSocket((msg) => {
            if (!msg) return;

            if (msg.event === "monitoring_started") {
                notify("AI server confirmed monitoring session.", "info");
            } else if (msg.event === "monitoring_stopped") {
                notify("AI server acknowledged session stop.", "info");
            } else if (msg.type === "face_recognition" || msg.type === "face_detection") {
                detectedFaces = msg.faces || [];
                updateHUDTelemetry(msg);

                // Check for freshly recorded attendance
                if (detectedFaces.length > 0) {
                    detectedFaces.forEach(f => {
                        if (f.recognized && f.attendance && f.attendance.status === "marked") {
                            pushAlert(
                                "Attendance Recorded",
                                `${f.name} (${f.student_id}) verified with ${Math.round((f.similarity || 0) * 100)}% similarity.`,
                                "success"
                            );
                            syncTodayAttendanceWidget();
                        } else if (!f.recognized) {
                            // Unregistered Face Alert (rate limited via timestamp check)
                            const nowTs = Date.now();
                            if (!window._lastUnknownAlert || (nowTs - window._lastUnknownAlert > 15000)) {
                                window._lastUnknownAlert = nowTs;
                                pushAlert("Unknown Face", "Unregistered individual detected in active camera feed.", "error");
                            }
                        }
                    });
                }
            } else if (msg.type === "error") {
                console.error("Monitoring WebSocket Error:", msg.detail);
                notify(msg.detail || "AI processing error", "error");
            }
        });
    }

    // Initial WebSocket connection attempt
    ensureWebSocketConnection();
    syncTodayAttendanceWidget();

    // =========================================================================
    // BUTTON & CONTROLS BINDING
    // =========================================================================

    if (btnStart) btnStart.addEventListener("click", startCameraMonitoring);
    if (btnStop) btnStop.addEventListener("click", stopCameraMonitoring);
    if (btnWebcam) {
        btnWebcam.addEventListener("click", () => {
            if (isMonitoringActive) stopCameraMonitoring();
            else startCameraMonitoring();
        });
    }

    if (btnRetry) {
        btnRetry.addEventListener("click", () => {
            notify("Re-synchronizing AI backend and status...", "info");
            ensureWebSocketConnection();
            syncTodayAttendanceWidget();
            loadClassrooms();
        });
    }

    if (btnPlayPause) {
        btnPlayPause.addEventListener("click", () => {
            if (!isMonitoringActive) {
                notify("Start monitoring first to play or pause stream.", "info");
                return;
            }
            isPaused = !isPaused;
            btnPlayPause.querySelector("span").textContent = isPaused ? "play_arrow" : "pause";
            notify(isPaused ? "Live camera feed paused." : "Live camera feed resumed.", "info");

            if (videoEl) {
                if (isPaused) videoEl.pause();
                else videoEl.play();
            }
        });
    }

    if (btnSnapshot) {
        btnSnapshot.addEventListener("click", () => {
            const link = document.createElement("a");
            link.download = `Classroom_AI_Snapshot_${Date.now()}.png`;
            link.href = canvas.toDataURL("image/png");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            notify("Captured live camera snapshot!", "success");
        });
    }

    if (clearAlertsBtn) {
        clearAlertsBtn.addEventListener("click", () => {
            if (alertsContainer) {
                alertsContainer.innerHTML = `<p class="text-xs text-on-surface-variant text-center py-10">No active security alerts</p>`;
            }
            notify("All live security alerts cleared.", "info");
        });
    }

    // =========================================================================
    // AI VOICE ASSISTANT MODULE (REAL TELEMETRY AWARE)
    // =========================================================================

    initVoiceAssistantModule({
        onStartMonitoring: startCameraMonitoring,
        onStopMonitoring: stopCameraMonitoring,
        onSnapshot: () => btnSnapshot && btnSnapshot.click(),
        getTelemetryState: () => ({
            isActive: isMonitoringActive,
            facesCount: detectedCount,
            recognizedCount: recognizedCount,
            unknownCount: unknownCount,
            selectedClassroom: selectedClassroom
        })
    });
}

/**
 * AI Voice Assistant Controller bound to genuine telemetry
 */
function initVoiceAssistantModule(actions) {
    const micBtn = document.getElementById("voice-mic-btn");
    const statusLbl = document.getElementById("voice-status-lbl");
    const historyContainer = document.getElementById("voice-history-container");
    const textInput = document.getElementById("voice-text-input");
    const pulseGlow = document.getElementById("voice-pulse-glow");

    let recognition = null;
    let isListening = false;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            isListening = true;
            if (statusLbl) statusLbl.textContent = "Listening to voice directive...";
            if (micBtn) {
                micBtn.classList.remove("bg-gradient-to-tr", "from-primary", "to-secondary");
                micBtn.classList.add("bg-error", "scale-105");
            }
            if (pulseGlow) pulseGlow.className = "absolute inset-0 bg-error/10 pulse -z-0";
        };

        recognition.onend = () => {
            isListening = false;
            if (statusLbl) statusLbl.textContent = "Click mic to speak";
            if (micBtn) {
                micBtn.classList.remove("bg-error", "scale-105");
                micBtn.classList.add("bg-gradient-to-tr", "from-primary", "to-secondary");
            }
            if (pulseGlow) pulseGlow.className = "absolute inset-0 bg-primary/5 pulse -z-0";
        };

        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            processVoiceCommand(transcript, actions);
        };

        recognition.onerror = (e) => {
            console.warn("Speech recognition error:", e.error);
        };
    } else {
        if (statusLbl) statusLbl.textContent = "Speech recognition unsupported. Type commands.";
    }

    if (micBtn) {
        micBtn.addEventListener("click", () => {
            if (!recognition) {
                if (typeof showToast === "function") showToast("Speech API unsupported in this browser. Please type commands below.", "info");
                if (textInput) textInput.focus();
                return;
            }
            if (isListening) recognition.stop();
            else recognition.start();
        });
    }

    if (textInput) {
        textInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && textInput.value.trim() !== "") {
                const cmd = textInput.value.trim();
                processVoiceCommand(cmd, actions);
                textInput.value = "";
            }
        });
    }

    function processVoiceCommand(commandText, actions) {
        if (historyContainer) {
            const logItem = document.createElement("div");
            logItem.className = "bg-black/20 rounded-lg p-2 flex items-start gap-2";
            logItem.innerHTML = `
                <span class="material-symbols-outlined text-xs mt-0.5 opacity-40">subdirectory_arrow_right</span>
                <p class="text-[10px] italic">"${commandText}"</p>
            `;
            historyContainer.prepend(logItem);
            if (historyContainer.children.length > 5) historyContainer.lastElementChild.remove();
        }

        const normalized = commandText.toLowerCase().trim();
        const state = actions.getTelemetryState();
        let vocalResponse = "";

        if (normalized.includes("start") || normalized.includes("begin") || normalized.includes("connect")) {
            actions.onStartMonitoring();
            vocalResponse = "Starting real-time camera monitoring session.";
        } else if (normalized.includes("stop") || normalized.includes("end") || normalized.includes("terminate")) {
            actions.onStopMonitoring();
            vocalResponse = "Terminating live camera session and releasing devices.";
        } else if (normalized.includes("status") || normalized.includes("check") || normalized.includes("face")) {
            if (state.isActive) {
                vocalResponse = `Monitoring active. Detected ${state.facesCount} faces. ${state.recognizedCount} registered students recognized, and ${state.unknownCount} unknown.`;
            } else {
                vocalResponse = "Camera monitoring is currently stopped.";
            }
        } else if (normalized.includes("snapshot") || normalized.includes("photo") || normalized.includes("capture")) {
            actions.onSnapshot();
            vocalResponse = "Capturing canvas frame snapshot.";
        } else {
            vocalResponse = "Directives supported: 'Start monitoring', 'Stop monitoring', 'Check status', or 'Capture snapshot'.";
        }

        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(vocalResponse);
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }

        if (typeof showToast === "function") {
            showToast(vocalResponse, "success");
        }
    }
}
