// Initialize WebSocket connection
const ws = new WebSocket("ws://localhost:8000/ws");

// Handle incoming messages
ws.onmessage = function(event) {

    console.log("onmessage")
    console.log(event)

    const messages = document.getElementById('messages');
    const message = document.createElement('li');
    const timestamp = new Date().toLocaleTimeString();
    
    // Set message content and timestamp
    message.textContent = event.data;
    message.dataset.timestamp = timestamp;
    
    messages.appendChild(message);
    // Scroll to bottom of messages
    messages.scrollTop = messages.scrollHeight;
};

// Send message function
function sendMessage(event) {
    if (event) event.preventDefault();
    
    const input = document.getElementById('messageText');
    const message = input.value.trim();
    if (message) {
        ws.send(message);
        input.value = '';
        // Reset textarea height
        input.style.height = '40px';
        input.style.overflowY = 'hidden';
    }
}

// Handle textarea input and Enter key
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageText');
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            // Only resize if we actually need to wrap
            if (this.scrollHeight > 40) {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 200) + 'px';
                this.style.overflowY = this.scrollHeight > 200 ? 'auto' : 'hidden';
            }
        });

        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});
