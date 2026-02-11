/**
 * SEAM Assessment – API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = '/api';

class SeamAPI {
    constructor() {
        this._token = localStorage.getItem('seam_token') || '';
    }

    // ── Helpers ──────────────────────────────────────────

    _headers(auth = false) {
        const headers = { 'Content-Type': 'application/json' };
        if (auth && this._token) {
            headers['Authorization'] = `Bearer ${this._token}`;
        }
        return headers;
    }

    async _request(method, path, body = null, auth = false) {
        const opts = {
            method,
            headers: this._headers(auth),
        };
        if (body) opts.body = JSON.stringify(body);

        const res = await fetch(`${API_BASE}${path}`, opts);

        if (res.status === 401) {
            localStorage.removeItem('seam_token');
            if (auth) {
                window.location.href = '/dashboard.html';
                throw new Error('Session expired');
            }
        }

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || 'Request failed');
        }

        // Handle file downloads
        const contentDisposition = res.headers.get('Content-Disposition');
        if (contentDisposition && contentDisposition.includes('attachment')) {
            return res.blob();
        }

        return res.json();
    }

    // ── Auth ─────────────────────────────────────────────

    async login(password) {
        const data = await this._request('POST', '/auth/login', { password });
        this._token = data.access_token;
        localStorage.setItem('seam_token', this._token);
        return data;
    }

    isLoggedIn() {
        return !!this._token;
    }

    logout() {
        this._token = '';
        localStorage.removeItem('seam_token');
    }

    // ── Interview ────────────────────────────────────────

    async startInterview({ participant_code, department, role_level, language_pref }) {
        return this._request('POST', '/interview/start', {
            participant_code,
            department: department || '',
            role_level: role_level || '',
            language_pref: language_pref || 'auto',
        });
    }

    async sendMessage(session_id, message) {
        return this._request('POST', '/interview/message', {
            session_id,
            message,
        });
    }

    async endInterview(session_id) {
        return this._request('POST', '/interview/end', { session_id });
    }

    async getSessionStatus(session_id) {
        return this._request('GET', `/interview/${session_id}/status`);
    }

    // ── Dashboard (auth required) ────────────────────────

    async getSessions(filters = {}) {
        let path = '/dashboard/sessions';
        const params = new URLSearchParams();
        if (filters.status) params.set('status', filters.status);
        if (filters.department) params.set('department', filters.department);
        if (params.toString()) path += `?${params}`;
        return this._request('GET', path, null, true);
    }

    async getSessionDetail(sessionId) {
        return this._request('GET', `/dashboard/session/${sessionId}`, null, true);
    }

    async getAnalytics() {
        return this._request('GET', '/dashboard/analytics', null, true);
    }

    async getClusters() {
        return this._request('GET', '/dashboard/clusters', null, true);
    }

    async exportSession(sessionId, format = 'json') {
        return this._request('GET', `/dashboard/export/${sessionId}?format=${format}`, null, true);
    }

    async getConversation(sessionId) {
        return this._request('GET', `/dashboard/conversation/${sessionId}`, null, true);
    }

    async generateSummary(sessionId) {
        return this._request('POST', `/dashboard/summary/${sessionId}`, null, true);
    }

    async getSummary(sessionId) {
        return this._request('GET', `/dashboard/summary/${sessionId}`, null, true);
    }
}

// Singleton instance
const api = new SeamAPI();
