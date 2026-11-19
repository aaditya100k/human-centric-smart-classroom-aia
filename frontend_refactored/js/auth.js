/**
 * Authentication Service Client for ClassMind AI
 * Manages JWT session tokens, user profile persistence, and route protection.
 */

const AuthService = {
    /**
     * Get stored JWT access token from localStorage or sessionStorage
     * @returns {string|null} JWT token
     */
    getToken() {
        return localStorage.getItem("sc_token") || sessionStorage.getItem("sc_token");
    },

    /**
     * Get currently logged-in user details object
     * @returns {Object|null} User details
     */
    getCurrentUser() {
        const rawUser = localStorage.getItem("sc_user") || sessionStorage.getItem("sc_user");
        if (!rawUser) return null;
        try {
            return JSON.parse(rawUser);
        } catch (e) {
            return null;
        }
    },

    /**
     * Check if user currently holds an authentication token
     * @returns {boolean} True if token exists
     */
    isAuthenticated() {
        const token = this.getToken();
        return !!token;
    },

    /**
     * Authenticate user against FastAPI backend
     * @param {string} emailOrUsername 
     * @param {string} password 
     * @param {boolean} remember 
     * @returns {Promise<Object>} Token and user data
     */
    async login(emailOrUsername, password, remember = true) {
        const baseUrl = window.API_BASE_URL || "http://127.0.0.1:8000/api";
        const response = await fetch(`${baseUrl}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: emailOrUsername.trim(),
                password: password,
            }),
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || "Invalid email/username or password.");
        }

        const data = await response.json();
        const storage = remember ? localStorage : sessionStorage;

        // Clear any old credentials from both storages
        localStorage.removeItem("sc_token");
        localStorage.removeItem("sc_user");
        sessionStorage.removeItem("sc_token");
        sessionStorage.removeItem("sc_user");

        storage.setItem("sc_token", data.access_token);
        storage.setItem("sc_user", JSON.stringify(data.user));

        return data;
    },

    /**
     * Register a new user account
     * @param {Object} userData - { username, email, password, full_name, role }
     * @returns {Promise<Object>} Token and user data
     */
    async register(userData) {
        const baseUrl = window.API_BASE_URL || "http://127.0.0.1:8000/api";
        const response = await fetch(`${baseUrl}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || "Registration failed.");
        }

        const data = await response.json();
        localStorage.setItem("sc_token", data.access_token);
        localStorage.setItem("sc_user", JSON.stringify(data.user));
        return data;
    },

    /**
     * Log out the current user session and redirect to Login
     */
    logout() {
        localStorage.removeItem("sc_token");
        localStorage.removeItem("sc_user");
        sessionStorage.removeItem("sc_token");
        sessionStorage.removeItem("sc_user");
        sessionStorage.removeItem("activeSession");

        // Redirect to Login Page
        if (!window.location.pathname.includes("edumonitor_ai_login_page.html")) {
            window.location.href = "edumonitor_ai_login_page.html";
        }
    },

    /**
     * Guard route access: redirect unauthenticated users to Login,
     * and authenticated users away from Login.
     */
    checkAuthProtection() {
        const path = window.location.pathname;
        const isLoginPage = path.includes("edumonitor_ai_login_page.html");
        const isLandingPage = path.includes("lumina_ai_classroom_landing_page.html");
        const authenticated = this.isAuthenticated();

        if (!isLoginPage && !isLandingPage && !authenticated) {
            console.warn("Unauthenticated access attempt detected. Redirecting to Login...");
            window.location.href = "edumonitor_ai_login_page.html";
        } else if (isLoginPage && authenticated) {
            window.location.href = "smart_classroom_ai_dashboard.html";
        }
    }
};

// Auto-run auth check on page load
document.addEventListener("DOMContentLoaded", () => {
    AuthService.checkAuthProtection();
});

// Make globally available
window.AuthService = AuthService;
