console.log("Sanity in lang.js")

// Reusable function to handle form submission
async function handleLangFormSubmit(event, item_id) {

    console.log("handleLangFormSubmit")
    console.log(item_id)

  // Prevent the default form submission behavior
  event.preventDefault();

  // Get the name input value
  const myTxt = document.getElementById("myName").value;

  // Make a POST request to the dynamic /api/lang/{item_id} route
  const response = await fetch(`/api/lang/${item_id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input: myTxt }),
  });

  // Check if the response was successful
  if (response.ok) {
    // Get messages area from form data attribute or default to "messages"
    const form = document.getElementById("myForm");
    const messagesAreaId = form ? form.dataset.messagesArea : "messages";
    const messagesArea = document.getElementById(messagesAreaId);
    // Don't clear previous content - keep all messages
    
    const reader = response.body.getReader();
    let chunk = null;
    while ((chunk = await reader.read())) {
      if (!chunk.done) {
        const chunkData = new TextDecoder("utf-8").decode(chunk.value);

        console.log(chunkData)
        const message = document.createElement("li");
        const timestamp = new Date().toLocaleTimeString();
        
        try {
            const json = JSON.parse(chunkData);
            const contentText = json.content;
            
            // Create message content with timestamp
            message.innerHTML = `
                <div class="message-content">${contentText}</div>
                <div class="message-timestamp">${timestamp}</div>
            `;
            message.classList.add('message');
            
        } catch (error) {
            console.error('Error parsing JSON:', error);
            message.textContent = error;
            message.classList.add('error');
        }
        
        messagesArea.appendChild(message);
        // Scroll to bottom of messages
        messagesArea.scrollTop = messagesArea.scrollHeight;
      } else {
        break; // Stop reading when the response is exhausted
      }
    }
  } else {
    // Display an error message
    alert("Error receiving name");
  }
}

// Handle textarea input and Enter key
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('myName');
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
                handleLangFormSubmit(e, 3);
            }
        });
    }
});
