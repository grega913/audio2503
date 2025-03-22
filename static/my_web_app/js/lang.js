console.log("Sanity in lang.js");

// Reusable function to handle form submission
async function handleLangFormSubmit(event, item_id) {
  console.log("handleLangFormSubmit");
  console.log(item_id);

  // Prevent the default form submission behavior
  event.preventDefault();

  // Get the name input value
  const myTxt = document.getElementById("myName").value;

  // Determine the correct endpoint based on item_id
  const endpoint =
    item_id === "3" || item_id === "4" ? `/api/lang_protected/${item_id}` : `/api/lang_private/${item_id}`;

  // Make a POST request to the correct endpoint
  const response = await fetch(endpoint, {
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
    

    const reader = response.body.getReader();
    let chunk = null;
    while ((chunk = await reader.read())) {
      if (!chunk.done) {
        const chunkData = new TextDecoder("utf-8").decode(chunk.value);

        console.log(chunkData);
        const message = document.createElement("li");
        const timestamp = new Date().toLocaleTimeString();

        try {
          const json = JSON.parse(chunkData);
          const contentText = json.content;

          // Create message content with timestamp
          message.innerHTML = `
                <div class="message-content is-size-7">${contentText}</div>
                <div class="message-timestamp is-size-7 has-text-right" style="margin-top: 0.25rem;">${timestamp}</div>
            `;
          message.classList.add("message", "mb-4");

        } catch (error) {
          console.error("Error parsing JSON:", error);
          message.textContent = error;
          message.classList.add("error");
        }

        messagesArea.appendChild(message);
        // Scroll to bottom of messages
        messagesArea.scrollTop = messagesArea.scrollHeight;
      } else {
        break; // Stop reading when the response is exhausted
      }
    }
    // Clear and focus the input field after successful response
    const inputField = document.getElementById("myName");
    if (inputField) {
      inputField.value = "";
      inputField.focus();
      // Reset textarea height
      inputField.style.height = "auto";
      inputField.style.overflowY = "hidden";
    }
  } else {
    // Display an error message
    alert("Error receiving name");
  }
}

// Handle form submission and text input
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("myForm");
  const messageInput = document.getElementById("myName");

  if (form) {
    // Handle form submission
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const item_id = form.dataset.itemId || "1";
      handleLangFormSubmit(e, item_id);
    });
  }

  if (messageInput) {
    // Handle textarea resizing
    messageInput.addEventListener("input", function () {
      // Only resize if we actually need to wrap
      if (this.scrollHeight > 40) {
        this.style.height = "auto";
        this.style.height = Math.min(this.scrollHeight, 200) + "px";
        this.style.overflowY = this.scrollHeight > 200 ? "auto" : "hidden";
      }
    });

    // Handle Enter key press
    messageInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const form = document.getElementById("myForm");
        const item_id = form ? form.dataset.itemId : "1";
        handleLangFormSubmit(e, item_id);
      }
    });
  }
});


