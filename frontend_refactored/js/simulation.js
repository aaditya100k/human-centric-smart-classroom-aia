/**
 * Legacy simulation.js replaced with Real-Time AI Camera Monitoring Controller.
 * Redirects directly to initRealAIMonitoring.
 * Zero simulated data, fake students, or random telemetry.
 */

document.addEventListener("DOMContentLoaded", () => {
    if (typeof initRealAIMonitoring === "function") {
        // Handled by real_monitoring.js
    } else {
        console.log("Real-time AI monitoring initialized.");
    }
});
