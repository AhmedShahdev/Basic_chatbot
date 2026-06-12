async function sendMessage() {
    const inputField = document.getElementById('userInput');
    const message = inputField.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chatBox');

    appendMessage(chatBox, 'user', message);
    inputField.value = '';
    scrollToBottom(chatBox);

    const typingEl = showTyping(chatBox);

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        typingEl.remove();

        if (data.response) {
            appendMessage(chatBox, 'bot', data.response);
        } else {
            appendMessage(chatBox, 'bot', '⚠️ Error: ' + (data.error || 'Something went wrong!'));
        }

    } catch (error) {
        typingEl.remove();
        appendMessage(chatBox, 'bot', '⚠️ Server se connection nahi ho raha!');
    }

    scrollToBottom(chatBox);
    loadHistory();
}

function appendMessage(chatBox, type, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', type);
    msgDiv.innerHTML = `<span class="bubble">${text}</span>`;
    chatBox.appendChild(msgDiv);
}

function showTyping(chatBox) {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot', 'typing');
    typingDiv.innerHTML = `<span class="bubble"><span></span><span></span><span></span></span>`;
    chatBox.appendChild(typingDiv);
    scrollToBottom(chatBox);
    return typingDiv;
}

function scrollToBottom(el) {
    el.scrollTop = el.scrollHeight;
}

function loadHistory() {
    fetch('/history')
        .then(res => res.json())
        .then(data => {
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';

            if (!data.history || data.history.length === 0) {
                historyList.innerHTML = '<p class="empty-msg">No history yet...</p>';
                return;
            }

            data.history.forEach(msg => {
                const item = document.createElement('div');
                item.classList.add('history-item', msg.role);

                const roleLabel = msg.role === 'user' ? '🧑 You' : '🤖 Bot';
                const shortText = msg.content.length > 60 ? msg.text.substring(0, 60) + '...' : msg.text;

                item.innerHTML = `<span class="role">${roleLabel}</span><p>${shortText}</p>`;
                historyList.appendChild(item);
            });

            historyList.scrollTop = historyList.scrollHeight;
        })
        .catch(() => {
            console.error('History not loaded');
        });
}

function clearHistory() {
    fetch('/clear', { method: 'POST' })
        .then(() => {
            document.getElementById('historyList').innerHTML = '<p class="empty-msg">No history yet...</p>';
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML = `<div class="message bot"><span class="bubble">Salam! Main tumhara AI assistant hun. Kuch bhi poochho! 😊</span></div>`;
        });
}

window.onload = loadHistory;