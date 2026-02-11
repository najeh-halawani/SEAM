/**
 * SEAM Assessment – Interview Chat Logic
 * Handles the chatbot interview flow, message rendering,
 * language detection, and session management.
 */

(function () {
    'use strict';

    // ── DOM References ───────────────────────────────────
    const welcomeOverlay = document.getElementById('welcomeOverlay');
    const welcomeForm    = document.getElementById('welcomeForm');
    const chatContainer  = document.getElementById('chatContainer');
    const chatMessages   = document.getElementById('chatMessages');
    const chatInput      = document.getElementById('chatInput');
    const sendBtn        = document.getElementById('sendBtn');
    const endBtn         = document.getElementById('endInterviewBtn');
    const categoryLabel  = document.getElementById('categoryLabel');
    const progressLabel  = document.getElementById('progressLabel');
    const progressFill   = document.getElementById('progressFill');
    const completeOverlay = document.getElementById('completeOverlay');
    const completionStats = document.getElementById('completionStats');

    // ── State ────────────────────────────────────────────
    let sessionId = null;
    let isWaiting = false;
    let messageCount = 0;

    const CATEGORY_NAMES = {
        strategic_implementation: 'Strategic Implementation',
        working_conditions: 'Working Conditions',
        work_organization: 'Work Organization',
        time_management: 'Time Management',
        communication_coordination_cooperation: 'Communication & Coordination (3Cs)',
        integrated_training: 'Integrated Training',
    };

    // ── Arabic detection ─────────────────────────────────
    const ARABIC_RE = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
    function hasArabic(text) {
        const arabicChars = (text.match(/[\u0600-\u06FF]/g) || []).length;
        const latinChars  = (text.match(/[a-zA-Z]/g) || []).length;
        return arabicChars > latinChars;
    }

    // ── Message Rendering ────────────────────────────────
    function addMessage(content, role) {
        const div = document.createElement('div');
        div.className = `message message-${role === 'assistant' ? 'bot' : 'user'}`;

        // RTL detection
        if (hasArabic(content)) {
            div.classList.add('rtl');
            div.setAttribute('dir', 'rtl');
        }

        // Simple markdown-ish: bold and paragraphs
        const html = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .split('\n\n')
            .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
            .join('');

        div.innerHTML = html;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        messageCount++;
    }

    function showTyping() {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typingIndicator';
        div.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTyping() {
        const el = document.getElementById('typingIndicator');
        if (el) el.remove();
    }

    function showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // ── Progress Update ──────────────────────────────────
    function updateProgress(categoryHint) {
        const categoryKeys = Object.keys(CATEGORY_NAMES);
        const index = categoryKeys.indexOf(categoryHint);
        if (index >= 0) {
            const num = index + 1;
            progressLabel.textContent = `Category ${num}/6`;
            progressFill.style.width = `${(num / 6) * 100}%`;
            categoryLabel.textContent = CATEGORY_NAMES[categoryHint] || categoryHint;
        }
    }

    // ── Auto-resize textarea ─────────────────────────────
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        sendBtn.disabled = !chatInput.value.trim();

        // Dynamic RTL
        if (hasArabic(chatInput.value)) {
            chatInput.classList.add('rtl');
            chatInput.setAttribute('dir', 'rtl');
        } else {
            chatInput.classList.remove('rtl');
            chatInput.setAttribute('dir', 'ltr');
        }
    });

    // ── Send Message ─────────────────────────────────────
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || isWaiting || !sessionId) return;

        isWaiting = true;
        sendBtn.disabled = true;
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Show user message
        addMessage(text, 'user');
        showTyping();

        try {
            const response = await api.sendMessage(sessionId, text);

            hideTyping();
            addMessage(response.reply, 'assistant');

            if (response.category_hint) {
                updateProgress(response.category_hint);
            }

            if (response.is_complete) {
                completeInterview();
            }
        } catch (err) {
            hideTyping();
            showToast('Failed to send message. Please try again.', 'error');
            console.error('Send error:', err);
        } finally {
            isWaiting = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // ── Start Interview ──────────────────────────────────
    welcomeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = welcomeForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Starting...';

        try {
            const response = await api.startInterview({
                department: document.getElementById('department').value.trim(),
                role_level: document.getElementById('roleLevel').value,
                language_pref: document.getElementById('languagePref').value,
            });

            sessionId = response.session_id;

            // Transition to chat
            welcomeOverlay.classList.add('hidden');
            chatContainer.style.display = 'flex';

            // Show greeting
            addMessage(response.greeting, 'assistant');
            updateProgress('strategic_implementation');
            chatInput.focus();

        } catch (err) {
            showToast('Failed to start interview. Please try again.', 'error');
            console.error('Start error:', err);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Begin Interview';
        }
    });

    // ── End Interview ────────────────────────────────────
    endBtn.addEventListener('click', async () => {
        if (!sessionId) return;
        if (!confirm('Are you sure you want to end the interview early?')) return;

        try {
            const result = await api.endInterview(sessionId);
            completeInterview(result);
        } catch (err) {
            showToast('Failed to end interview.', 'error');
        }
    });

    function completeInterview(stats) {
        chatContainer.style.display = 'none';
        completeOverlay.classList.remove('hidden');

        if (stats) {
            completionStats.innerHTML = `
                <div style="display:flex; gap:1rem; justify-content:center;">
                    <div class="glass-card stat-card" style="padding:1rem 1.5rem; text-align:center;">
                        <div class="stat-value" style="font-size:1.5rem;">${stats.total_messages}</div>
                        <div class="stat-label" style="font-size:0.75rem;">Messages</div>
                    </div>
                    <div class="glass-card stat-card" style="padding:1rem 1.5rem; text-align:center;">
                        <div class="stat-value" style="font-size:1.5rem;">${stats.field_notes_count}</div>
                        <div class="stat-label" style="font-size:0.75rem;">Field Notes</div>
                    </div>
                </div>
            `;
        }
    }

})();
