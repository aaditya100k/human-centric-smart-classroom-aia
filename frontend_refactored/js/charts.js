// Chart.js Manager for Dashboard, Emotion, and Reports pages

document.addEventListener("DOMContentLoaded", () => {
    // 1. Dashboard Charts
    initDashboardCharts();
    
    // 2. Emotion Analytics Charts
    initEmotionCharts();
    
    // 3. Reports & Analytics Charts
    initReportsCharts();
});

// Helper for standard dark chart configurations
const darkChartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: "#c2c6d6",
                font: {
                    family: "Inter",
                    size: 11
                }
            }
        },
        tooltip: {
            backgroundColor: "#1d2022",
            titleColor: "#e0e3e5",
            bodyColor: "#c2c6d6",
            borderColor: "rgba(255, 255, 255, 0.1)",
            borderWidth: 1,
            padding: 10,
            cornerRadius: 10
        }
    },
    scales: {
        x: {
            grid: {
                color: "rgba(255, 255, 255, 0.05)"
            },
            ticks: {
                color: "#8c909f",
                font: { family: "Inter", size: 10 }
            }
        },
        y: {
            grid: {
                color: "rgba(255, 255, 255, 0.05)"
            },
            ticks: {
                color: "#8c909f",
                font: { family: "Inter", size: 10 }
            }
        }
    }
};

function initDashboardCharts() {
    // Attendance Trend Line Chart
    const attendanceCtx = document.getElementById("attendanceTrendChart");
    if (attendanceCtx) {
        new Chart(attendanceCtx, {
            type: "line",
            data: {
                labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
                datasets: [{
                    label: "Attendance Rate (%)",
                    data: [92, 95, 88, 94, 91],
                    borderColor: "#adc6ff",
                    backgroundColor: "rgba(173, 198, 255, 0.15)",
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: "#adc6ff",
                    pointBorderColor: "#101415",
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                ...darkChartDefaults,
                scales: {
                    x: darkChartDefaults.scales.x,
                    y: {
                        ...darkChartDefaults.scales.y,
                        min: 70,
                        max: 100,
                        ticks: {
                            color: "#8c909f",
                            callback: value => value + "%"
                        }
                    }
                }
            }
        });
    }

    // Emotion Distribution Doughnut Chart
    const emotionCtx = document.getElementById("emotionDistributionChart");
    if (emotionCtx) {
        new Chart(emotionCtx, {
            type: "doughnut",
            data: {
                labels: ["Focused", "Happy", "Neutral", "Confused"],
                datasets: [{
                    data: [65, 20, 10, 5],
                    backgroundColor: [
                        "#adc6ff", // Focused
                        "#c0c1ff", // Happy
                        "#4ae176", // Neutral
                        "#ffb4ab"  // Confused
                    ],
                    borderWidth: 2,
                    borderColor: "#101415",
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            color: "#c2c6d6",
                            font: { family: "Inter", size: 12 },
                            padding: 15
                        }
                    },
                    tooltip: darkChartDefaults.plugins.tooltip
                },
                cutout: "70%"
            }
        });
    }
}

function initEmotionCharts() {
    // Timeline Chart
    const timelineCtx = document.getElementById("emotionTimelineChart");
    if (timelineCtx) {
        new Chart(timelineCtx, {
            type: "line",
            data: {
                labels: ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM"],
                datasets: [
                    {
                        label: "Attention Index",
                        data: [85, 92, 78, 64, 88, 81],
                        borderColor: "#adc6ff",
                        borderWidth: 2.5,
                        fill: false,
                        tension: 0.3,
                        pointRadius: 4
                    },
                    {
                        label: "Engagement Index",
                        data: [72, 85, 80, 55, 82, 79],
                        borderColor: "#c0c1ff",
                        borderWidth: 2.5,
                        fill: false,
                        tension: 0.3,
                        pointRadius: 4
                    },
                    {
                        label: "Stress Level",
                        data: [15, 10, 22, 35, 12, 18],
                        borderColor: "#ffb4ab",
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3,
                        pointRadius: 3
                    }
                ]
            },
            options: {
                ...darkChartDefaults,
                scales: {
                    x: darkChartDefaults.scales.x,
                    y: {
                        ...darkChartDefaults.scales.y,
                        max: 100,
                        ticks: {
                            color: "#8c909f",
                            callback: value => value + "%"
                        }
                    }
                }
            }
        });
    }

    // Overall Mood Doughnut
    const overallMoodCtx = document.getElementById("overallMoodDoughnut");
    if (overallMoodCtx) {
        new Chart(overallMoodCtx, {
            type: "doughnut",
            data: {
                labels: ["Focused", "Interested", "Bored", "Frustrated"],
                datasets: [{
                    data: [58, 25, 12, 5],
                    backgroundColor: ["#adc6ff", "#4ae176", "#c0c1ff", "#ffb4ab"],
                    borderWidth: 2,
                    borderColor: "#101415"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#c2c6d6", font: { family: "Inter", size: 11 }, padding: 10 }
                    },
                    tooltip: darkChartDefaults.plugins.tooltip
                },
                cutout: "65%"
            }
        });
    }
}

function initReportsCharts() {
    // Monthly Attendance Bar Chart
    const monthlyAttendanceCtx = document.getElementById("monthlyAttendanceBar");
    if (monthlyAttendanceCtx) {
        new Chart(monthlyAttendanceCtx, {
            type: "bar",
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                datasets: [{
                    label: "Avg Attendance (%)",
                    data: [91, 93, 89, 94, 95, 92],
                    backgroundColor: "rgba(173, 198, 255, 0.75)",
                    borderColor: "#adc6ff",
                    borderWidth: 1.5,
                    borderRadius: 6,
                    barThickness: 24
                }]
            },
            options: {
                ...darkChartDefaults,
                scales: {
                    x: darkChartDefaults.scales.x,
                    y: {
                        ...darkChartDefaults.scales.y,
                        min: 80,
                        max: 100,
                        ticks: {
                            color: "#8c909f",
                            callback: value => value + "%"
                        }
                    }
                }
            }
        });
    }

    // Engagement Radar Chart
    const engagementRadarCtx = document.getElementById("engagementRadar");
    if (engagementRadarCtx) {
        new Chart(engagementRadarCtx, {
            type: "radar",
            data: {
                labels: ["Focus Level", "Attendance", "Participation", "Collaboration", "Punctuality"],
                datasets: [{
                    label: "Classroom Average",
                    data: [82, 94, 75, 80, 88],
                    backgroundColor: "rgba(192, 193, 255, 0.25)",
                    borderColor: "#c0c1ff",
                    borderWidth: 2.5,
                    pointBackgroundColor: "#c0c1ff",
                    pointBorderColor: "#101415",
                    pointBorderWidth: 1.5,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "#c2c6d6", font: { family: "Inter", size: 11 } }
                    },
                    tooltip: darkChartDefaults.plugins.tooltip
                },
                scales: {
                    r: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        angleLines: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: {
                            color: "#8c909f",
                            backdropColor: "transparent",
                            font: { size: 9 }
                        },
                        pointLabels: {
                            color: "#8c909f",
                            font: { family: "Inter", size: 10, weight: "bold" }
                        },
                        min: 50,
                        max: 100
                    }
                }
            }
        });
    }
}
