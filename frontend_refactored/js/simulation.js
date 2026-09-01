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

    if (webcamBtn) {
        webcamBtn.addEventListener("click", () => {
            useWebcam = !useWebcam;
            
            if (useWebcam) {
                // Style button active
                webcamBtn.classList.add("bg-primary", "text-on-primary");
                webcamBtn.classList.remove("glass-card");
                
                triggerToast("Initializing device camera stream...", "info");
                
                navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } })
                    .then(stream => {
                        mediaStream = stream;
                        videoEl = document.createElement("video");
                        videoEl.srcObject = stream;
                        videoEl.autoplay = true;
                        videoEl.playsInline = true;
                        videoEl.addEventListener("loadedmetadata", () => {
                            videoEl.play();
                            triggerToast("Device camera feed active!", "success");
                        });
                    })
                    .catch(err => {
                        console.error("Camera stream error:", err);
                        useWebcam = false;
                        webcamBtn.classList.remove("bg-primary", "text-on-primary");
                        webcamBtn.classList.add("glass-card");
                        triggerToast("Could not access camera: " + err.message, "error");
                    });
            } else {
                // Style button inactive
                webcamBtn.classList.remove("bg-primary", "text-on-primary");
                webcamBtn.classList.add("glass-card");
                
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                    mediaStream = null;
                }
                videoEl = null;
                triggerToast("Switched back to virtual simulated feed", "info");
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
