/**
 * SEAM Assessment – Consultant Dashboard Logic
 * Fetches analytics, sessions, clusters, and manages exports.
 */

(function () {
    'use strict';

    // ── DOM ──────────────────────────────────────────────
    const loginScreen    = document.getElementById('loginScreen');
    const dashboardScreen = document.getElementById('dashboardScreen');
    const loginForm      = document.getElementById('loginForm');
    const loginError     = document.getElementById('loginError');
    const logoutBtn      = document.getElementById('logoutBtn');
    const refreshBtn     = document.getElementById('refreshBtn');
    const filterStatus   = document.getElementById('filterStatus');
    const runClusterBtn  = document.getElementById('runClusterBtn');
    const modalOverlay   = document.getElementById('sessionModal');
    const modalContent   = document.getElementById('modalContent');
    const modalTitle     = document.getElementById('modalTitle');
    const modalClose     = document.getElementById('modalClose');
    const clusterTimestamp   = document.getElementById('clusterTimestamp');
    const clusterStaleWarning = document.getElementById('clusterStaleWarning');

    // Category color mapping
    const CATEGORY_CSS = {
        'Strategic Implementation': 'cat-strategic',
        'Working Conditions': 'cat-conditions',
        'Work Organization': 'cat-organization',
        'Time Management': 'cat-time',
        'Communication, Coordination & Cooperation (3Cs)': 'cat-communication',
        'Integrated Training': 'cat-training',
    };

    const BADGE_CSS = {
        'Strategic Implementation': 'badge-blue',
        'Working Conditions': 'badge-amber',
        'Work Organization': 'badge-purple',
        'Time Management': 'badge-rose',
        'Communication, Coordination & Cooperation (3Cs)': 'badge-teal',
        'Integrated Training': 'badge-emerald',
    };

    function showToast(msg, type = 'success') {
        const c = document.getElementById('toastContainer');
        const t = document.createElement('div');
        t.className = `toast toast-${type}`;
        t.textContent = msg;
        c.appendChild(t);
        setTimeout(() => t.remove(), 4000);
    }

    // ── Auth ─────────────────────────────────────────────

    function checkAuth() {
        if (api.isLoggedIn()) {
            showDashboard();
        } else {
            loginScreen.style.display = 'flex';
            dashboardScreen.style.display = 'none';
        }
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError.style.display = 'none';
        const pw = document.getElementById('loginPassword').value;

        try {
            await api.login(pw);
            showDashboard();
        } catch (err) {
            loginError.textContent = 'Invalid password. Please try again.';
            loginError.style.display = 'block';
        }
    });

    logoutBtn.addEventListener('click', () => {
        api.logout();
        location.reload();
    });

    // ── Dashboard ────────────────────────────────────────

    function showDashboard() {
        loginScreen.style.display = 'none';
        dashboardScreen.style.display = 'block';
        loadAll();
    }

    async function loadAll() {
        await Promise.all([
            loadAnalytics(),
            loadSessions(),
            loadSavedClusters(),
        ]);
    }

    // ── Analytics ────────────────────────────────────────

    async function loadAnalytics() {
        try {
            const data = await api.getAnalytics();

            document.getElementById('statTotal').textContent = data.total_sessions;
            document.getElementById('statCompleted').textContent = data.completed_sessions;
            document.getElementById('statNotes').textContent = data.total_field_notes;

            renderCategoryBars(data.category_distribution);
            renderTags(data.top_tags);
        } catch (err) {
            console.error('Analytics error:', err);
        }
    }

    function renderCategoryBars(distribution) {
        const container = document.getElementById('categoryBars');
        if (!distribution || distribution.length === 0) {
            container.innerHTML = '<div class="empty-state"><p class="empty-state-text">No data yet. Complete some interviews to see distribution.</p></div>';
            return;
        }

        const maxPct = Math.max(...distribution.map(d => d.percentage), 1);

        container.innerHTML = distribution.map(d => `
            <div class="category-bar-row">
                <div class="category-bar-label">${d.category}</div>
                <div class="category-bar-track">
                    <div class="category-bar-fill ${CATEGORY_CSS[d.category] || ''}"
                         style="width: ${(d.percentage / maxPct) * 100}%">
                        ${d.count}
                    </div>
                </div>
            </div>
        `).join('');
    }

    function renderTags(tags) {
        const container = document.getElementById('tagsContainer');
        if (!tags || tags.length === 0) {
            container.innerHTML = '<p style="color:var(--text-muted);">No tags yet</p>';
            return;
        }

        const colors = ['badge-blue', 'badge-purple', 'badge-teal', 'badge-amber', 'badge-rose', 'badge-emerald'];
        container.innerHTML = tags.map((t, i) =>
            `<span class="badge ${colors[i % colors.length]}">${t.tag.replace(/_/g, ' ')} (${t.count})</span>`
        ).join('');
    }

    // ── Sessions ─────────────────────────────────────────

    async function loadSessions() {
        try {
            const filters = {};
            if (filterStatus.value) filters.status = filterStatus.value;

            const sessions = await api.getSessions(filters);
            renderSessions(sessions);
        } catch (err) {
            console.error('Sessions error:', err);
        }
    }

    function renderSessions(sessions) {
        const tbody = document.getElementById('sessionsBody');
        if (!sessions || sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><p>No sessions found</p></td></tr>';
            return;
        }

        tbody.innerHTML = sessions.map(s => {
            const date = new Date(s.created_at).toLocaleDateString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
            const statusBadge = s.status === 'completed'
                ? '<span class="badge badge-emerald">Completed</span>'
                : '<span class="badge badge-amber">Active</span>';

            const summaryIndicator = s.has_summary
                ? '<span class="badge badge-blue" style="font-size:0.65rem;" title="Summary available">📋 Summary</span>'
                : '';

            return `
                <tr>
                    <td><strong>${s.participant_code}</strong></td>
                    <td>${s.department || '—'}</td>
                    <td>${s.role_level || '—'}</td>
                    <td>${statusBadge} ${summaryIndicator}</td>
                    <td>${s.message_count}</td>
                    <td>${s.field_notes_count}</td>
                    <td style="white-space:nowrap;">${date}</td>
                    <td>
                        <div style="display:flex; gap:0.25rem; flex-wrap:wrap;">
                            <button class="btn btn-ghost btn-sm" onclick="viewSession('${s.id}')">View</button>
                            <button class="btn btn-ghost btn-sm" onclick="exportSession('${s.id}', 'json')">JSON</button>
                            <button class="btn btn-ghost btn-sm" onclick="exportSession('${s.id}', 'csv')">CSV</button>
                            <button class="btn btn-ghost btn-sm" onclick="deleteSession('${s.id}', '${s.participant_code}')" style="color:var(--accent-rose);" title="Delete session">🗑️</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    filterStatus.addEventListener('change', loadSessions);
    refreshBtn.addEventListener('click', loadAll);

    // ── Delete Session ───────────────────────────────────

    window.deleteSession = async function (sessionId, code) {
        if (!confirm(`Are you sure you want to delete session "${code}"?\n\nThis will permanently remove all messages, field notes, and data for this session. This cannot be undone.`)) {
            return;
        }

        try {
            await api.deleteSession(sessionId);
            showToast(`Session "${code}" deleted`);
            // Close the modal if it's showing this session
            modalOverlay.classList.remove('active');
            loadAll();
        } catch (err) {
            showToast('Failed to delete session', 'error');
            console.error('Delete error:', err);
        }
    };

    // ── Session Detail Modal ─────────────────────────────

    window.viewSession = async function (sessionId) {
        modalOverlay.classList.add('active');
        modalContent.innerHTML = '<div class="loading-center"><div class="spinner"></div></div>';

        try {
            const detail = await api.getSessionDetail(sessionId);
            modalTitle.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                    <span>Session: ${detail.session.participant_code}</span>
                    <button class="btn btn-ghost btn-sm" onclick="deleteSession('${sessionId}', '${detail.session.participant_code}')" style="color:var(--accent-rose);" title="Delete session">
                        🗑️ Delete
                    </button>
                </div>
            `;

            // ── Summary Section ─────────────────────
            let summaryHtml = '';
            if (detail.summary) {
                summaryHtml = `
                    <div style="margin-bottom:1.5rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                            <h4 style="color:var(--accent-blue); margin:0;">📋 Diagnostic Summary</h4>
                            <button class="btn btn-ghost btn-sm" onclick="generateSessionSummary('${sessionId}')" 
                                    title="Regenerate summary">
                                🔄 Regenerate
                            </button>
                        </div>
                        <div id="summaryContent" class="markdown-body" style="padding:1rem; background:var(--bg-input); border-radius:var(--radius-sm); 
                                    border-left:3px solid var(--accent-blue); line-height:1.8;">
                            ${formatMarkdown(detail.summary)}
                        </div>
                    </div>
                `;
            } else if (detail.field_notes.length > 0) {
                summaryHtml = `
                    <div style="margin-bottom:1.5rem; text-align:center; padding:1.5rem; background:var(--bg-input); border-radius:var(--radius-sm);">
                        <p style="color:var(--text-muted); margin-bottom:0.75rem;">No diagnostic summary generated yet</p>
                        <button class="btn btn-primary" onclick="generateSessionSummary('${sessionId}')">
                            📋 Generate Diagnostic Summary
                        </button>
                    </div>
                `;
            }

            // ── Field Notes Section ──────────────────
            let notesHtml = '';
            if (detail.field_notes.length === 0) {
                notesHtml = '<p style="color:var(--text-muted);">No field notes yet.</p>';
            } else {
                notesHtml = detail.field_notes.map(n => {
                    const catBadge = n.primary_category
                        ? `<span class="badge ${BADGE_CSS[n.primary_category] || 'badge-blue'}">${n.primary_category}</span>`
                        : '';
                    const tagsBadges = (n.tags || []).map(t =>
                        `<span class="badge badge-purple" style="font-size:0.7rem;">${t.replace(/_/g, ' ')}</span>`
                    ).join(' ');

                    const isArabic = /[\u0600-\u06FF]/.test(n.anonymized_text);

                    return `
                        <div style="padding:0.75rem; background:var(--bg-input); border-radius:var(--radius-sm); margin-bottom:0.75rem;">
                            <p style="margin-bottom:0.5rem; line-height:1.6; ${isArabic ? 'direction:rtl; text-align:right;' : ''}">${n.anonymized_text}</p>
                            <div style="display:flex; flex-wrap:wrap; gap:0.35rem; align-items:center;">
                                ${catBadge}
                                ${tagsBadges}
                                <span style="margin-left:auto; font-size:0.7rem; color:var(--text-muted);">
                                    Confidence: ${n.confidence}%
                                </span>
                            </div>
                        </div>
                    `;
                }).join('');
            }

            modalContent.innerHTML = `
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:1rem;">
                    <div><strong style="color:var(--text-muted); font-size:0.75rem;">Department</strong><br>${detail.session.department || '—'}</div>
                    <div><strong style="color:var(--text-muted); font-size:0.75rem;">Level</strong><br>${detail.session.role_level || '—'}</div>
                    <div><strong style="color:var(--text-muted); font-size:0.75rem;">Messages</strong><br>${detail.session.message_count}</div>
                    <div><strong style="color:var(--text-muted); font-size:0.75rem;">Field Notes</strong><br>${detail.session.field_notes_count}</div>
                </div>
                ${summaryHtml}
                <h4 style="margin-bottom:0.75rem; color:var(--text-secondary);">Field Notes</h4>
                ${notesHtml}
            `;
        } catch (err) {
            modalContent.innerHTML = '<p style="color:var(--accent-rose);">Failed to load session detail.</p>';
        }
    };

    // ── Generate Summary ─────────────────────────────────

    window.generateSessionSummary = async function (sessionId) {
        const summaryContainer = document.getElementById('summaryContent');
        // Find a container to show loading state
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '⏳ Generating...';
        btn.disabled = true;

        try {
            const result = await api.generateSummary(sessionId);

            // Update the modal with the new summary
            if (summaryContainer) {
                summaryContainer.innerHTML = formatMarkdown(result.summary);
            } else {
                // Re-open modal to show the summary
                window.viewSession(sessionId);
            }

            showToast('Diagnostic summary generated!');
            // Refresh sessions to update the summary indicator
            loadSessions();
        } catch (err) {
            showToast('Failed to generate summary', 'error');
            console.error('Summary generation error:', err);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    };

    // ── Markdown Formatter ────────────────────────────────

    function formatMarkdown(text) {
        if (!text) return '';
        // Use marked.js for proper markdown rendering
        if (typeof marked !== 'undefined') {
            return marked.parse(text);
        }
        // Fallback if marked.js not loaded
        return text.replace(/\n/g, '<br>');
    }

    modalClose.addEventListener('click', () => modalOverlay.classList.remove('active'));
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) modalOverlay.classList.remove('active');
    });

    // ── Export ────────────────────────────────────────────

    window.exportSession = async function (sessionId, format) {
        try {
            const blob = await api.exportSession(sessionId, format);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${sessionId.substring(0, 8)}.${format}`;
            a.click();
            URL.revokeObjectURL(url);
            showToast(`Exported as ${format.toUpperCase()}`);
        } catch (err) {
            showToast('Export failed', 'error');
        }
    };

    // ── Clusters ─────────────────────────────────────────

    function renderClusterStatus(data) {
        // Update timestamp
        if (data.ran_at) {
            const date = new Date(data.ran_at).toLocaleString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
            clusterTimestamp.textContent = `Last run: ${date}`;
        } else {
            clusterTimestamp.textContent = '';
        }

        // Update staleness warning
        if (data.is_stale && data.stale_reason) {
            clusterStaleWarning.style.display = 'inline-flex';
            clusterStaleWarning.textContent = `⚠️ ${data.stale_reason} — re-run recommended`;
        } else {
            clusterStaleWarning.style.display = 'none';
            clusterStaleWarning.textContent = '';
        }
    }

    function renderClusterGrid(clusters) {
        const grid = document.getElementById('clustersGrid');

        if (!clusters || clusters.length === 0) {
            grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><div class="empty-state-icon">🔍</div><p class="empty-state-text">No clusters yet. Run clustering after completing some interviews.</p></div>';
            return;
        }

        grid.innerHTML = clusters.map(c => `
            <div class="glass-card cluster-card">
                <div class="cluster-header">
                    <div>
                        <span class="cluster-size">${c.size}</span>
                        <span style="color:var(--text-muted); font-size:0.8rem;"> notes</span>
                    </div>
                    ${c.category ? `<span class="badge ${BADGE_CSS[c.category] || 'badge-blue'}">${c.category}</span>` : ''}
                </div>
                <div class="cluster-representative">"${c.representative_text}"</div>
                ${c.sample_texts.length > 1 ? `
                    <div class="cluster-samples">
                        ${c.sample_texts.slice(1, 4).map(t => `
                            <div class="cluster-sample">"${t}"</div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    async function loadSavedClusters() {
        try {
            const data = await api.getClusters();
            renderClusterStatus(data);
            renderClusterGrid(data.clusters);
        } catch (err) {
            console.error('Clusters load error:', err);
        }
    }

    runClusterBtn.addEventListener('click', async () => {
        const grid = document.getElementById('clustersGrid');
        grid.innerHTML = '<div class="loading-center" style="grid-column:1/-1;"><div class="spinner"></div></div>';
        runClusterBtn.disabled = true;
        runClusterBtn.textContent = '⏳ Running...';

        try {
            const data = await api.runClusters();
            renderClusterStatus(data);
            renderClusterGrid(data.clusters);
            showToast('Clustering complete!');
        } catch (err) {
            grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><p style="color:var(--accent-rose);">Failed to run clustering.</p></div>';
            showToast('Clustering failed', 'error');
        } finally {
            runClusterBtn.disabled = false;
            runClusterBtn.textContent = 'Run Clustering';
        }
    });

    // ── Init ─────────────────────────────────────────────
    checkAuth();

})();
