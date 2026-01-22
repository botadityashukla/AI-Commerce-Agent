const API_URL = ""; // Relative path for same-origin requests

const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const ticketList = document.getElementById('ticket-list');
const lastAgentBadge = document.getElementById('last-agent');
const apiStatusDot = document.getElementById('api-status-dot');
const apiStatusText = document.getElementById('api-status-text');

// Helper to append messages
function appendMessage(text, isUser) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'ai'}`;
    msgDiv.innerHTML = `<div class="bubble">${text}</div>`;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Helper to create ticket card
function addTicket(ticketData) {
    // Determine priority color
    let priorityColor = '#94a3b8';
    if (ticketData.priority === 'High') priorityColor = '#ef4444';
    if (ticketData.priority === 'Medium') priorityColor = '#f59e0b';

    // Clear empty state if it exists
    const emptyState = ticketList.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const card = document.createElement('div');
    card.className = 'ticket-card';
    card.innerHTML = `
        <div class="title">${ticketData.issue_summary || 'Support Ticket'}</div>
        <div class="meta">
            <span>${ticketData.sentiment || 'Neutral'}</span>
            <span style="color: ${priorityColor}">${ticketData.priority || 'Normal'}</span>
        </div>
    `;
    ticketList.prepend(card);
}

// Send Message Logic
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // UI Updates
    appendMessage(text, true);
    userInput.value = '';
    userInput.disabled = true;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();

        // Append AI Data
        appendMessage(data.response, false);

        // Update Agent Badge
        lastAgentBadge.textContent = data.agent_used;

        // Handle Ticket
        if (data.ticket) {
            addTicket(data.ticket);
        }

    } catch (error) {
        console.error('Error:', error);
        appendMessage("Sorry, I'm having trouble connecting to the server.", false);
    } finally {
        userInput.disabled = false;
        userInput.focus();
    }
}

// Health Check
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        if (data.status === 'active') {
            apiStatusDot.classList.remove('error');
            apiStatusDot.classList.add('active');
            apiStatusText.textContent = "Online";
        }
    } catch (e) {
        apiStatusDot.classList.remove('active');
        apiStatusDot.classList.add('error');
        apiStatusText.textContent = "Offline";
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Initial Health Check
setInterval(checkHealth, 30000); // Every 30s
checkHealth();
