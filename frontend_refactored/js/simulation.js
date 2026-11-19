// Live AI Camera Monitoring Feed Simulation & Webcam Controller

document.addEventListener("DOMContentLoaded", () => {
    initCameraSimulation();
});

function initCameraSimulation() {
    const canvas = document.getElementById("camera-feed-canvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    
    // Set internal resolution matching standard HD aspect ratio
    canvas.width = 1280;
    canvas.height = 720;

    // Simulated students data for tracking boxes
    const trackedStudents = [
        { name: "Leo Sterling", baseX: 250, baseY: 220, targetX: 250, targetY: 220, status: "Focused", attention: 98, temp: 36.5, color: "#adc6ff" },
        { name: "Elena Vance", baseX: 550, baseY: 300, targetX: 550, targetY: 300, status: "Distracted", attention: 12, temp: 37.1, color: "#ffb4ab" },
        { name: "Marcus Chen", baseX: 850, baseY: 250, targetX: 850, targetY: 250, status: "Neutral", attention: 85, temp: 36.6, color: "#c0c1ff" },
        { name: "Sarah Jenkins", baseX: 1050, baseY: 280, targetX: 1050, targetY: 280, status: "Happy", attention: 92, temp: 36.4, color: "#4ae176" }
    ];

    // HUD state
    let scanlineY = 0;
    let frameCount = 0;
    let isPlaying = true;
    let animId = null;
    
    // Camera state
    let useWebcam = false;
    let videoEl = null;
    let mediaStream = null;
    let mousePos = { x: 640, y: 360 };
    const alertTimers = {};

    // Phase 2 Real-Time Face Detection State
    let wsMonitoring = null;
    let realFacesDetected = [];
    let lastFrameSentTime = 0;

    // Mouse listener on canvas to simulate face tracking target lock
    canvas.addEventListener("mousemove", (e) => {
        const rect = canvas.getBoundingClientRect();
        mousePos.x = ((e.clientX - rect.left) / rect.width) * canvas.width;
        mousePos.y = ((e.clientY - rect.top) / rect.height) * canvas.height;
    });

    // Helper: Toast display fallback
    const triggerToast = (msg, type = "success") => {
        if (typeof showToast === "function") {
            showToast(msg, type);
        } else {
            console.log(`[Toast ${type.toUpperCase()}] ${msg}`);
        }
    };

    // Main Draw Function
    function drawSimulation() {
        frameCount++;
        
        // 1. Draw webcam feed or Cyber classroom grid background
        if (useWebcam && videoEl && videoEl.readyState >= 2) {
            ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
            
            // Draw camera border HUD
            ctx.strokeStyle = "rgba(173, 198, 255, 0.4)";
            ctx.lineWidth = 4;
            ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);
            
            ctx.fillStyle = "rgba(173, 198, 255, 0.9)";
            ctx.font = "bold 12px Courier New, monospace";
            ctx.fillText("🔴 LIVE CAMERA FEED STREAMING", 30, 40);

            // Draw Real OpenCV Face Detection & Recognition Bounding Boxes
            if (realFacesDetected && realFacesDetected.length > 0) {
                realFacesDetected.forEach((face, idx) => {
                    const x = face.x;
                    const y = face.y;
                    const w = face.width;
                    const h = face.height;
                    const isRecognized = !!face.recognized;
                    const name = face.name || (isRecognized ? "Recognized Student" : "Unknown");
                    const simPct = Math.round((face.similarity || 0) * 100);

                    const strokeColor = isRecognized ? "#4ae176" : "#ffb4ab";
                    const fillColor = isRecognized ? "rgba(74, 225, 118, 0.08)" : "rgba(255, 180, 171, 0.08)";

                    // Draw bounding box
                    ctx.strokeStyle = strokeColor;
                    ctx.lineWidth = 3;
                    ctx.strokeRect(x, y, w, h);

                    // Corner brackets
                    const len = Math.min(15, w / 4);
                    ctx.strokeStyle = "#adc6ff";
                    ctx.lineWidth = 2;

                    ctx.beginPath(); ctx.moveTo(x + len, y); ctx.lineTo(x, y); ctx.lineTo(x, y + len); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x + w - len, y); ctx.lineTo(x + w); ctx.lineTo(x + w, y + len); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x, y + h - len); ctx.lineTo(x, y + h); ctx.lineTo(x + len, y + h); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x + w, y + h - len); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - len, y + h); ctx.stroke();

                    // Translucent overlay
                    ctx.fillStyle = fillColor;
                    ctx.fillRect(x, y, w, h);

                    // Draw tag background with attendance status
                    let labelText = isRecognized ? `${name} (${simPct}%)` : `Unknown (${simPct}%)`;
                    let attStatusStr = "";
                    if (isRecognized && face.attendance) {
                        if (face.attendance.status === "marked") {
                            attStatusStr = "✓ Attendance Marked";
                        } else if (face.attendance.status === "already_marked") {
                            attStatusStr = "✓ Already Present";
                        } else {
                            attStatusStr = "Attendance Not Marked";
                        }
                    } else if (!isRecognized) {
                        attStatusStr = "Not Registered";
                    }

                    ctx.font = "bold 11px Inter, sans-serif";
                    const mainWidth = ctx.measureText(labelText).width;
                    ctx.font = "9px Inter, sans-serif";
                    const subWidth = attStatusStr ? ctx.measureText(attStatusStr).width : 0;
                    const textWidth = Math.max(mainWidth, subWidth);

                    const tagHeight = attStatusStr ? 32 : 18;
                    const tagY = Math.max(0, y - tagHeight - 4);

                    ctx.fillStyle = isRecognized ? "rgba(0, 57, 21, 0.85)" : "rgba(105, 0, 5, 0.85)";
                    ctx.fillRect(x, tagY, textWidth + 12, tagHeight + 4);

                    // Draw label text
                    ctx.font = "bold 11px Inter, sans-serif";
                    ctx.fillStyle = strokeColor;
                    ctx.fillText(labelText, x + 6, tagY + 14);

                    if (attStatusStr) {
                        ctx.font = "9px Inter, sans-serif";
                        ctx.fillStyle = isRecognized ? "#6bff8f" : "#ffdad6";
                        ctx.fillText(attStatusStr, x + 6, tagY + 27);
                    }
                });
            }

            // Frame Sampling: Send frame over WebSocket at 5–10 FPS (~150ms interval)
            const now = Date.now();
            if (wsMonitoring && wsMonitoring.readyState === WebSocket.OPEN && (now - lastFrameSentTime >= 150)) {
                lastFrameSentTime = now;
                try {
                    const frameJpeg = canvas.toDataURL("image/jpeg", 0.5);
                    wsMonitoring.send(JSON.stringify({ type: "frame", image: frameJpeg }));
                } catch (err) {
                    console.warn("WebSocket frame send error:", err);
                }
            }
        } else {
            // Clear background & Draw virtual classroom grid
            ctx.fillStyle = "#0c0f10";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw grid lines
            ctx.strokeStyle = "rgba(173, 198, 255, 0.04)";
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

            // Draw camera scanning circle in center
            ctx.strokeStyle = "rgba(173, 198, 255, 0.08)";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(canvas.width / 2, canvas.height / 2, 120, 0, Math.PI * 2);
            ctx.stroke();
        }

        // 2. Draw Simulated Video Noise/Static occasionally
        if (Math.random() > 0.98) {
            ctx.fillStyle = "rgba(255, 255, 255, 0.05)";
            for (let i = 0; i < 20; i++) {
                const rx = Math.random() * canvas.width;
                const ry = Math.random() * canvas.height;
                const rw = Math.random() * 100 + 50;
                const rh = Math.random() * 4 + 1;
                ctx.fillRect(rx, ry, rw, rh);
            }
        }

        // 3. Update and Draw Bounding Boxes
        trackedStudents.forEach((student, index) => {
            // Drift target coordinate slightly or lock to cursor if webcam is active on user
            if (useWebcam && index === 0) {
                // Smooth tracking to mouse position
                student.targetX = mousePos.x;
                student.targetY = mousePos.y;
                student.name = "Leo Sterling (You)";
                
                // Fluctuate attention/status actively
                if (frameCount % 60 === 0) {
                    student.attention = Math.floor(Math.random() * 10) + 90; // High focus
                    const statuses = ["Focused", "Neutral"];
                    student.status = statuses[Math.floor(Math.random() * statuses.length)];
                }
            } else {
                if (index === 0) student.name = "Leo Sterling";
                
                if (frameCount % 60 === 0) {
                    student.targetX = student.baseX + (Math.random() * 20 - 10);
                    student.targetY = student.baseY + (Math.random() * 20 - 10);
                    
                    // Randomly fluctuate attention & status
                    if (Math.random() > 0.7) {
                        if (student.name === "Elena Vance") {
                            student.attention = Math.floor(Math.random() * 25) + 5;
                            student.status = student.attention < 15 ? "Distracted" : "Neutral";
                        } else {
                            student.attention = Math.floor(Math.random() * 20) + 80;
                            const statuses = ["Focused", "Happy", "Neutral"];
                            student.status = statuses[Math.floor(Math.random() * statuses.length)];
                        }
                    }
                }
            }

            // Interpolate coordinate
            student.baseX += (student.targetX - student.baseX) * 0.05;
            student.baseY += (student.targetY - student.baseY) * 0.05;

            const w = 110;
            const h = 110;
            const x = student.baseX - w / 2;
            const y = student.baseY - h / 2;

            // Trigger low attention alerts
            if (student.attention < 15) {
                triggerLowAttentionAlert(student);
            }

            // Draw Box Corner Brackets
            ctx.strokeStyle = student.color;
            ctx.lineWidth = 2;
            const len = 15;
            
            // Top-left
            ctx.beginPath();
            ctx.moveTo(x + len, y); ctx.lineTo(x, y); ctx.lineTo(x, y + len);
            ctx.stroke();

            // Top-right
            ctx.beginPath();
            ctx.moveTo(x + w - len, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + len);
            ctx.stroke();

            // Bottom-left
            ctx.beginPath();
            ctx.moveTo(x, y + h - len); ctx.lineTo(x, y + h); ctx.lineTo(x + len, y + h);
            ctx.stroke();

            // Bottom-right
            ctx.beginPath();
            ctx.moveTo(x + w, y + h - len); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - len, y + h);
            ctx.stroke();

            // Fill face area translucent
            ctx.fillStyle = student.status === "Distracted" ? "rgba(255, 180, 171, 0.05)" : "rgba(173, 198, 255, 0.03)";
            ctx.fillRect(x, y, w, h);

            // Draw HUD Label details
            ctx.fillStyle = student.color;
            ctx.font = "bold 11px Inter, sans-serif";
            ctx.fillText(student.name, x, y - 22);

            ctx.font = "9px Courier New, monospace";
            ctx.fillStyle = "rgba(224, 227, 229, 0.9)";
            ctx.fillText(`ATT: ${student.attention}%`, x, y - 10);
            ctx.fillText(`EMO: ${student.status.toUpperCase()}`, x, y + h + 12);
            ctx.fillText(`TEMP: ${student.temp.toFixed(1)}C`, x, y + h + 22);

            // Update DOM element tags if they exist
            updateDOMStudentDetails(index, student);
        });

        // 4. Draw HUD Overlays (Running scanline, text overlays)
        scanlineY = (scanlineY + 1.5) % canvas.height;
        ctx.strokeStyle = "rgba(173, 198, 255, 0.03)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, scanlineY);
        ctx.lineTo(canvas.width, scanlineY);
        ctx.stroke();

        // 5. Update dashboard stats widgets dynamically
        updateWidgets();
    }

    // Dynamic Stats Widgets Updater
    function updateWidgets() {
        // Attendance Count
        const attCountEl = document.getElementById("widget-attendance-count");
        if (attCountEl) {
            attCountEl.textContent = "24"; // Base count
        }

        // Avg Emotion
        const emoValEl = document.getElementById("widget-emotion-val");
        const emoChgEl = document.getElementById("widget-emotion-change");
        if (emoValEl) {
            const statusCounts = {};
            trackedStudents.forEach(s => {
                statusCounts[s.status] = (statusCounts[s.status] || 0) + 1;
            });
            const topEmotion = Object.keys(statusCounts).reduce((a, b) => statusCounts[a] > statusCounts[b] ? a : b, "Focused");
            emoValEl.textContent = topEmotion;
            
            // Adjust colors of emotion progress bars based on students status percentages
            const posCount = trackedStudents.filter(s => ["Focused", "Happy"].includes(s.status)).length;
            const neuCount = trackedStudents.filter(s => s.status === "Neutral").length;
            const negCount = trackedStudents.filter(s => s.status === "Distracted").length;
            const total = trackedStudents.length;

            const posBar = document.getElementById("widget-emotion-bar-positive");
            const neuBar = document.getElementById("widget-emotion-bar-neutral");
            const negBar = document.getElementById("widget-emotion-bar-negative");

            if (posBar) posBar.style.width = `${(posCount / total) * 100}%`;
            if (neuBar) neuBar.style.width = `${(neuCount / total) * 100}%`;
            if (negBar) negBar.style.width = `${(negCount / total) * 100}%`;
            
            if (emoChgEl) {
                if (negCount > 0) {
                    emoChgEl.textContent = "Fluctuating";
                    emoChgEl.className = "text-error text-xs font-bold";
                } else {
                    emoChgEl.textContent = "↑ 14% Stable";
                    emoChgEl.className = "text-tertiary text-xs font-bold";
                }
            }
        }

        // Attention Level
        const attValEl = document.getElementById("widget-attention-val");
        const attLblEl = document.getElementById("widget-attention-lbl");
        const attBarsContainer = document.getElementById("widget-attention-bars");
        if (attValEl) {
            const avgAttention = Math.round(trackedStudents.reduce((sum, s) => sum + s.attention, 0) / trackedStudents.length);
            attValEl.textContent = `${avgAttention}%`;
            
            if (attLblEl) {
                if (avgAttention >= 85) {
                    attLblEl.textContent = "Optimal Focus";
                    attLblEl.className = "text-tertiary text-xs font-bold";
                } else if (avgAttention >= 70) {
                    attLblEl.textContent = "Moderate";
                    attLblEl.className = "text-secondary text-xs font-bold";
                } else {
                    attLblEl.textContent = "Attention Dropping";
                    attLblEl.className = "text-error text-xs font-bold";
                }
            }

            if (attBarsContainer && attBarsContainer.children.length >= 4) {
                // Adjust active visualization bars heights dynamically
                attBarsContainer.children[0].style.height = "40%";
                attBarsContainer.children[1].style.height = "60%";
                attBarsContainer.children[2].style.height = "80%";
                attBarsContainer.children[3].style.height = `${avgAttention}%`;
                
                // Color adjustment
                const lastBar = attBarsContainer.children[3];
                if (avgAttention < 70) {
                    lastBar.className = "flex-1 bg-error rounded-t-sm";
                } else {
                    lastBar.className = "flex-1 bg-secondary rounded-t-sm";
                }
            }
        }

        // Temp Sensor Simulation
        const tempValEl = document.getElementById("widget-temp-val");
        if (tempValEl) {
            // Live micro fluctuated temperatures
            const ambient = 22.4 + (Math.sin(frameCount / 240) * 0.15);
            tempValEl.textContent = `${ambient.toFixed(1)}°C`;
        }
    }

    // Dynamic DOM cards synchronizer
    function updateDOMStudentDetails(index, student) {
        const cardElement = document.getElementById(`card-student-${index}`);
        if (!cardElement) return;

        const nameEl = cardElement.querySelector("h4");
        const statusEl = cardElement.querySelector("span.rounded") || cardElement.querySelector("span");
        
        // Find attendance text element safely
        const spans = cardElement.querySelectorAll("span");
        let attEl = null;
        spans.forEach(s => {
            if (s.textContent.includes("Att:") || s.className.includes("text-error") || s.className.includes("text-on-surface-variant")) {
                if (s !== statusEl) attEl = s;
            }
        });

        if (nameEl) nameEl.textContent = student.name;
        if (statusEl) {
            statusEl.textContent = student.status;
            statusEl.className = `px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-tighter ${
                student.status === "Focused" ? "bg-tertiary/20 text-tertiary" :
                student.status === "Distracted" ? "bg-error/20 text-error animate-pulse" :
                student.status === "Happy" ? "bg-primary/20 text-primary" :
                student.status === "Neutral" ? "bg-secondary/20 text-secondary" :
                "bg-white/10 text-on-surface-variant"
            }`;
        }
        if (attEl) {
            attEl.textContent = `Att: ${student.attention}%`;
            attEl.className = `text-[10px] ${
                student.attention < 50 ? "text-error font-bold" : "text-on-surface-variant"
            }`;
        }
    }

    // Real-time attention drift logger
    function triggerLowAttentionAlert(student) {
        const now = Date.now();
        // Limit triggering of alerts to once per 20 seconds to prevent alert storms
        if (!alertTimers[student.name] || now - alertTimers[student.name] > 20000) {
            alertTimers[student.name] = now;
            
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            // Append alert to UI logs panel
            const alertsContainer = document.getElementById("live-alerts-container");
            if (alertsContainer) {
                // Clear default messages if present
                if (alertsContainer.querySelector("p.text-center")) {
                    alertsContainer.innerHTML = "";
                }

                const alertNode = document.createElement("div");
                alertNode.className = "flex gap-3 p-3 bg-error/10 border-l-2 border-error rounded-r-lg animate-pulse";
                alertNode.innerHTML = `
                    <span class="material-symbols-outlined text-error text-xl shrink-0">person_off</span>
                    <div>
                        <p class="text-xs font-bold">Low Attention Alert</p>
                        <p class="text-[10px] text-on-surface-variant">Student ${student.name} attention level: ${student.attention}%</p>
                        <p class="text-[9px] text-error mt-1">${timeStr} • Critical</p>
                    </div>
                `;
                alertsContainer.prepend(alertNode);
                
                // Limit list to top 6 alerts
                if (alertsContainer.children.length > 6) {
                    alertsContainer.lastElementChild.remove();
                }
            }

            // Sync with global notifications (DataAPI)
            if (typeof DataAPI !== "undefined" && typeof DataAPI.addNotification === "function") {
                DataAPI.addNotification({
                    title: `Attention Dropped: ${student.name}`,
                    message: `${student.name} attention level has dropped to ${student.attention}% in CAM_04.`,
                    category: "Alert"
                });
                
                // Trigger animation update on header alerts badge
                const dropdownNotifBtn = document.getElementById("dropdown-notif-btn");
                if (dropdownNotifBtn && !dropdownNotifBtn.querySelector(".bg-error")) {
                    const alertBadge = document.createElement("span");
                    alertBadge.className = "absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full animate-bounce";
                    dropdownNotifBtn.appendChild(alertBadge);
                }
            }

            triggerToast(`Attention anomaly flagged for ${student.name}`, "error");

            // Voice synthesis announcement
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const alertUtterance = new SpeechSynthesisUtterance(`Warning. Student ${student.name} attention levels are critically low.`);
                alertUtterance.rate = 1.0;
                window.speechSynthesis.speak(alertUtterance);
            }
        }
    }

    // Start Simulation Loop
    function loop() {
        if (isPlaying) {
            drawSimulation();
            animId = requestAnimationFrame(loop);
        }
    }
    loop();

    // Controls Action Binding
    const playPauseBtn = document.getElementById("feed-play-pause-btn");
    const snapshotBtn = document.getElementById("feed-snapshot-btn");
    const webcamBtn = document.getElementById("feed-webcam-btn");
    const clearAlertsBtn = document.getElementById("clear-alerts-btn");

    if (playPauseBtn) {
        playPauseBtn.addEventListener("click", () => {
            isPlaying = !isPlaying;
            playPauseBtn.querySelector("span").textContent = isPlaying ? "pause" : "play_arrow";
            triggerToast(isPlaying ? "Camera feed resumed" : "Camera feed paused", "info");
            
            if (videoEl) {
                if (isPlaying) videoEl.play();
                else videoEl.pause();
            }
            if (isPlaying) loop();
        });
    }

    if (snapshotBtn) {
        snapshotBtn.addEventListener("click", () => {
            const dataUrl = canvas.toDataURL("image/png");
            const link = document.createElement("a");
            link.download = `ClassMind_AI_Snapshot_${Date.now()}.png`;
            link.href = dataUrl;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            triggerToast("Captured high-res camera snapshot!", "success");
        });
    }

    // ==========================================
    // REAL LIVE MONITORING CONTROLLER & WEBCAM
    // ==========================================

    const btnStartMon = document.getElementById("btn-start-monitoring");
    const btnStopMon = document.getElementById("btn-stop-monitoring");
    const btnRetryConn = document.getElementById("btn-retry-connection");
    const statusDotEl = document.getElementById("monitoring-status-dot");
    const statusTextEl = document.getElementById("monitoring-status-text");
    const lastUpdateEl = document.getElementById("monitoring-last-update");
    const hudCamStatusEl = document.getElementById("hud-camera-status-text");
    const studentsDetectedEl = document.getElementById("monitoring-students-detected");

    function updateUIStatus(statusData) {
        if (!statusData) return;
        const isActive = !!(statusData.active || statusData.is_active);
        
        if (statusTextEl) {
            statusTextEl.textContent = isActive ? "MONITORING ACTIVE" : "MONITORING STOPPED";
        }
        if (statusDotEl) {
            statusDotEl.className = isActive
                ? "w-2.5 h-2.5 rounded-full bg-tertiary animate-pulse"
                : "w-2.5 h-2.5 rounded-full bg-error";
        }
        if (btnStartMon) {
            if (isActive) btnStartMon.classList.add("hidden");
            else btnStartMon.classList.remove("hidden");
        }
        if (btnStopMon) {
            if (isActive) btnStopMon.classList.remove("hidden");
            else btnStopMon.classList.add("hidden");
        }
        if (lastUpdateEl && statusData.last_update) {
            const timeStr = new Date(statusData.last_update).toLocaleTimeString();
            lastUpdateEl.textContent = `LAST_UPDATE: ${timeStr}`;
        }
        if (studentsDetectedEl) {
            const count = statusData.students_detected ?? 0;
            studentsDetectedEl.textContent = `${count} DETECTED (NO AI)`;
        }
    }

    async function syncMonitoringStatusWithBackend() {
        if (typeof ApiService === "undefined" || !ApiService.getMonitoringStatus) return;
        try {
            const statusData = await ApiService.getMonitoringStatus();
            updateUIStatus(statusData);
        } catch (err) {
            console.warn("Monitoring status sync failed:", err.message);
            if (statusTextEl) statusTextEl.textContent = "BACKEND OFFLINE";
            if (statusDotEl) statusDotEl.className = "w-2.5 h-2.5 rounded-full bg-yellow-500";
            triggerToast("Backend server offline or unreachable. Click Retry Connection.", "error");
        }
    }

    async function populateClassroomsDropdown() {
        const clsSelect = document.getElementById("monitoring-classroom-select");
        if (!clsSelect || typeof ApiService === "undefined" || !ApiService.getClassrooms) return;
        try {
            const classrooms = await ApiService.getClassrooms();
            clsSelect.innerHTML = '<option value="">Select Classroom...</option>';
            classrooms.forEach(c => {
                const opt = document.createElement("option");
                opt.value = c.id;
                opt.textContent = `${c.name} (${c.department})`;
                clsSelect.appendChild(opt);
            });
        } catch (err) {
            console.warn("Could not load classrooms dropdown:", err.message);
        }
    }
    populateClassroomsDropdown();

    async function startLiveMonitoring() {
        const clsSelect = document.getElementById("monitoring-classroom-select");
        const selectedClassroomId = clsSelect && clsSelect.value ? parseInt(clsSelect.value, 10) : null;

        if (!selectedClassroomId) {
            triggerToast("Select a classroom before starting automatic attendance.", "error");
            if (statusTextEl) statusTextEl.textContent = "SELECT CLASSROOM";
            return;
        }

        triggerToast("Requesting device camera permission...", "info");

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            triggerToast("Browser security restriction: Media device API requires HTTPS or localhost.", "error");
            if (statusTextEl) statusTextEl.textContent = "CAMERA RESTRICTED";
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            mediaStream = stream;
            videoEl = document.createElement("video");
            videoEl.srcObject = stream;
            videoEl.autoplay = true;
            videoEl.playsInline = true;
            videoEl.muted = true;
            await videoEl.play();

            useWebcam = true;
            if (hudCamStatusEl) hudCamStatusEl.textContent = "WEBCAM ACTIVE";

            if (webcamBtn) {
                webcamBtn.classList.add("bg-primary", "text-on-primary");
                webcamBtn.classList.remove("glass-card");
            }

            // Call Backend POST /api/monitoring/start
            if (typeof ApiService !== "undefined" && ApiService.startMonitoring) {
                const res = await ApiService.startMonitoring(selectedClassroomId);
                updateUIStatus(res.status || { active: true });
            } else {
                updateUIStatus({ active: true, last_update: new Date().toISOString() });
            }

            triggerToast("Live camera stream & automatic attendance session started!", "success");

        } catch (err) {
            console.error("Camera access error:", err);
            useWebcam = false;
            
            let userMsg = "Could not access camera: " + err.message;
            if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
                userMsg = "Camera permission denied by user. Please allow camera access in browser.";
            } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
                userMsg = "No webcam device detected. Please attach a camera.";
            } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
                userMsg = "Camera is currently in use by another application.";
            }

            if (statusTextEl) statusTextEl.textContent = "CAMERA UNAVAILABLE";
            if (statusDotEl) statusDotEl.className = "w-2.5 h-2.5 rounded-full bg-error";
            triggerToast(userMsg, "error");
        }
    }

    async function stopLiveMonitoring() {
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
        videoEl = null;
        useWebcam = false;

        if (hudCamStatusEl) hudCamStatusEl.textContent = "SIMULATION FEED";

        if (webcamBtn) {
            webcamBtn.classList.remove("bg-primary", "text-on-primary");
            webcamBtn.classList.add("glass-card");
        }

        // Call Backend POST /api/monitoring/stop
        if (typeof ApiService !== "undefined" && ApiService.stopMonitoring) {
            try {
                const res = await ApiService.stopMonitoring();
                updateUIStatus(res.status || { active: false });
            } catch (err) {
                console.error("Failed to call stop monitoring API:", err);
                updateUIStatus({ active: false, last_update: new Date().toISOString() });
            }
        } else {
            updateUIStatus({ active: false, last_update: new Date().toISOString() });
        }

        triggerToast("Live monitoring session stopped.", "info");
    }

    // Bind Button Click Handlers
    if (btnStartMon) {
        btnStartMon.addEventListener("click", startLiveMonitoring);
    }
    if (btnStopMon) {
        btnStopMon.addEventListener("click", stopLiveMonitoring);
    }
    if (btnRetryConn) {
        btnRetryConn.addEventListener("click", () => {
            triggerToast("Retrying backend connection...", "info");
            syncMonitoringStatusWithBackend();
        });
    }
    if (webcamBtn) {
        webcamBtn.addEventListener("click", () => {
            if (useWebcam) {
                stopLiveMonitoring();
            } else {
                startLiveMonitoring();
            }
        });
    }

    // Initialize backend status sync and WebSocket connection
    syncMonitoringStatusWithBackend();

    if (typeof ApiService !== "undefined" && ApiService.connectMonitoringWebSocket) {
        wsMonitoring = ApiService.connectMonitoringWebSocket((msg) => {
            if (!msg) return;
            if (msg.event === "monitoring_started" || msg.event === "monitoring_stopped" || msg.event === "connection_established") {
                updateUIStatus(msg.data);
            } else if (msg.type === "face_detection" || msg.type === "face_recognition") {
                realFacesDetected = msg.faces || [];
                const count = msg.faces_detected ?? 0;
                if (studentsDetectedEl) {
                    studentsDetectedEl.textContent = `${count} DETECTED (FACE DETECTION)`;
                }
                if (statusTextEl) {
                    statusTextEl.textContent = "FACE DETECTION: ACTIVE";
                }
                if (statusDotEl) {
                    statusDotEl.className = "w-2.5 h-2.5 rounded-full bg-tertiary animate-pulse";
                }
                if (lastUpdateEl && msg.timestamp) {
                    const timeStr = new Date(msg.timestamp).toLocaleTimeString();
                    lastUpdateEl.textContent = `LAST_UPDATE: ${timeStr}`;
                }
            }
        });
    }

    if (clearAlertsBtn) {
        clearAlertsBtn.addEventListener("click", () => {
            const alertsContainer = document.getElementById("live-alerts-container");
            if (alertsContainer) {
                alertsContainer.innerHTML = `<p class="text-xs text-on-surface-variant text-center py-8">No active security alerts</p>`;
            }
            triggerToast("All real-time alerts cleared", "info");
        });
    }

    // Telemetry Events Logger Panel simulation
    const logContainer = document.getElementById("live-telemetry-log");
    if (logContainer) {
        const events = [
            "Face detection locked on ST-2024-001 (Alex Johnson)",
            "Gaze tracking calibrated: 98% focus score",
            "Attention fluctuation flagged in Rear Desk Row 3",
            "Thermal sensor baseline verified: 36.5C",
            "Audio sentiment level: Normal classroom acoustics"
        ];
        
        setInterval(() => {
            if (!isPlaying) return;
            const randomEvt = events[Math.floor(Math.random() * events.length)];
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            const logEntry = document.createElement("div");
            logEntry.className = "flex items-center gap-2 text-[11px] text-on-surface-variant border-b border-white/5 py-1.5 animate-fadeIn";
            logEntry.innerHTML = `<span class="text-tertiary font-mono">${timeStr}</span> <span>${randomEvt}</span>`;
            logContainer.prepend(logEntry);
            if (logContainer.children.length > 8) {
                logContainer.lastElementChild.remove();
            }
        }, 5000);
    }

    // Initialize Voice Assistant Integration
    initVoiceAssistant();
}

// AI Voice Assistant Module
function initVoiceAssistant() {
    const micBtn = document.getElementById("voice-mic-btn");
    const statusLbl = document.getElementById("voice-status-lbl");
    const historyContainer = document.getElementById("voice-history-container");
    const textInput = document.getElementById("voice-text-input");
    const pulseGlow = document.getElementById("voice-pulse-glow");

    let recognition = null;
    let isListening = false;

    // Initialize Speech Recognition API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            statusLbl.textContent = "Listening to command...";
            micBtn.classList.remove("bg-gradient-to-tr", "from-primary", "to-secondary");
            micBtn.classList.add("bg-error", "scale-105");
            if (pulseGlow) {
                pulseGlow.className = "absolute inset-0 bg-error/10 pulse -z-0";
            }
        };

        recognition.onend = () => {
            isListening = false;
            statusLbl.textContent = "Click mic to speak";
            micBtn.classList.remove("bg-error", "scale-105");
            micBtn.classList.add("bg-gradient-to-tr", "from-primary", "to-secondary");
            if (pulseGlow) {
                pulseGlow.className = "absolute inset-0 bg-primary/5 pulse -z-0";
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            processVoiceCommand(transcript);
        };

        recognition.onerror = (event) => {
            console.error("Speech Recognition Error:", event.error);
            if (event.error !== "no-speech") {
                if (typeof showToast === "function") showToast("Speech API Error: " + event.error, "error");
            }
        };
    } else {
        statusLbl.textContent = "Speech API unsupported. Type commands.";
    }

    if (micBtn) {
        micBtn.addEventListener("click", () => {
            if (!recognition) {
                if (typeof showToast === "function") {
                    showToast("Speech recognition is not supported in this browser. Please type commands instead.", "info");
                }
                if (textInput) textInput.focus();
                return;
            }
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    }

    if (textInput) {
        textInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && textInput.value.trim() !== "") {
                const command = textInput.value.trim();
                processVoiceCommand(command);
                textInput.value = "";
            }
        });
    }

    function processVoiceCommand(commandText) {
        // Log to History panel
        if (historyContainer) {
            const logItem = document.createElement("div");
            logItem.className = "bg-black/20 rounded-lg p-2 flex items-start gap-2 animate-fadeIn";
            logItem.innerHTML = `
                <span class="material-symbols-outlined text-xs mt-0.5 opacity-40">subdirectory_arrow_right</span>
                <p class="text-[10px] italic">"${commandText}"</p>
            `;
            historyContainer.prepend(logItem);
            if (historyContainer.children.length > 5) {
                historyContainer.lastElementChild.remove();
            }
        }

        const normalizedCmd = commandText.toLowerCase().trim();
        let vocalResponse = "";

        if (normalizedCmd.includes("attention") || normalizedCmd.includes("focus") || normalizedCmd.includes("score")) {
            // Find average attention of active students
            const attentionVal = document.getElementById("widget-attention-val")?.textContent || "92%";
            vocalResponse = `The average classroom attention level is currently ${attentionVal}.`;
            
            // Check for distracted students
            const elenaCard = document.getElementById("card-student-1");
            const isElenaDistracted = elenaCard?.innerText.includes("Distracted");
            if (isElenaDistracted) {
                vocalResponse += " Warning: Student Elena Vance is flagged as distracted.";
            }
        } else if (normalizedCmd.includes("pause") || normalizedCmd.includes("stop feed")) {
            const playPauseBtn = document.getElementById("feed-play-pause-btn");
            if (playPauseBtn && playPauseBtn.querySelector("span").textContent === "pause") {
                playPauseBtn.click();
                vocalResponse = "Session camera stream has been paused.";
            } else {
                vocalResponse = "Camera stream is already paused.";
            }
        } else if (normalizedCmd.includes("resume") || normalizedCmd.includes("play feed") || normalizedCmd.includes("start feed")) {
            const playPauseBtn = document.getElementById("feed-play-pause-btn");
            if (playPauseBtn && playPauseBtn.querySelector("span").textContent === "play_arrow") {
                playPauseBtn.click();
                vocalResponse = "Session camera stream is now active.";
            } else {
                vocalResponse = "Camera stream is already active.";
            }
        } else if (normalizedCmd.includes("snapshot") || normalizedCmd.includes("photo") || normalizedCmd.includes("capture")) {
            const snapshotBtn = document.getElementById("feed-snapshot-btn");
            if (snapshotBtn) {
                snapshotBtn.click();
                vocalResponse = "Generating high resolution canvas image capture.";
            }
        } else if (normalizedCmd.includes("webcam") || normalizedCmd.includes("live camera") || normalizedCmd.includes("real camera")) {
            const webcamBtn = document.getElementById("feed-webcam-btn");
            const isActive = webcamBtn?.classList.contains("bg-primary");
            if (webcamBtn && !isActive) {
                webcamBtn.click();
                vocalResponse = "Requesting device camera access. Streaming live.";
            } else {
                vocalResponse = "Webcam is already active.";
            }
        } else if (normalizedCmd.includes("simulation") || normalizedCmd.includes("mock") || normalizedCmd.includes("virtual")) {
            const webcamBtn = document.getElementById("feed-webcam-btn");
            const isActive = webcamBtn?.classList.contains("bg-primary");
            if (webcamBtn && isActive) {
                webcamBtn.click();
                vocalResponse = "Restoring simulated classroom tracking models.";
            } else {
                vocalResponse = "Virtual simulation is already active.";
            }
        } else if (normalizedCmd.includes("help") || normalizedCmd.includes("command") || normalizedCmd.includes("say")) {
            vocalResponse = "Supported voice directives: Check attention, Pause camera, Resume camera, Switch to webcam, Switch to simulation, or Take snapshot.";
        } else {
            vocalResponse = "Command not recognized. Please request attention check, camera controls, or snapshot.";
        }

        // TTS Speech Synthesis Output
        speakVoiceResponse(vocalResponse);
    }

    function speakVoiceResponse(responseText) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const speechUtterance = new SpeechSynthesisUtterance(responseText);
            speechUtterance.rate = 1.05;
            speechUtterance.pitch = 1.0;
            window.speechSynthesis.speak(speechUtterance);
        }
        if (typeof showToast === "function") {
            showToast(responseText, "success");
        }
    }
}
