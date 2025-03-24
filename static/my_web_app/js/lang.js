console.log("Sanity in lang.js");

function createMessageElementAndCheckForHumanAssistance(json) {
  console.log("createMessageElementAndCheckForHumanAssistance");
  const lastMessage = json.last?.[0];
  if (!lastMessage) return null;

  const {
    content,
    type,
    timestamp,
    additional_kwargs,
    response_metadata,
    tool_calls,
  } = lastMessage;

  // Handle AI messages with tool calls
  let toolCallsContent = "";
  let showHumanAssist = false;

  if (type === "ai" && !content && tool_calls) {
    toolCallsContent = `
      <div class="tool-calls">
        <p>Tool calls requested:</p>
        <pre>${JSON.stringify(tool_calls, null, 2)}</pre>
      </div>
    `;

    // Check for human assistance tool call
    if (tool_calls.some((tc) => tc.function?.name === "human_assistance")) {
      showHumanAssist = true;
    }
  }

  const article = document.createElement("article");
  article.innerHTML = `
        <div class="message-header">
            <p>${type}</p> 
            <p>${new Date(timestamp).toLocaleTimeString()}</p>
        </div>
        <div class="message-body">
          ${content || ""}
          ${toolCallsContent}
        </div>
    `;
  article.classList.add("message", `message-${type}`);

  // Show/hide human assist section
  const humanAssistSection = document.getElementById("human-assist-section");
  if (humanAssistSection) {
    if (showHumanAssist) {
      humanAssistSection.classList.remove("is-hidden");
    } else {
      humanAssistSection.classList.add("is-hidden");
    }
  }

  return article;
}

// Reusable function to handle form submission //
/*  This is the main form and is called in all 6 parts for the first interaction
    Basically it makes a post request to the /api/lang/public (if item_id ==1 or2) or /api/lang/protected (if item_id == 3,4,5,6)
    calls to protected route are for cases, wherwe we need a config, since we need history/memory, based on the logged in user

*/
async function handleLangFormSubmit(event, item_id) {
  console.log("handleLangFormSubmit");
  console.log(item_id);

  // Prevent the default form submission behavior
  event.preventDefault();

  // Get the name input value
  const myTxt = document.getElementById("myName").value;

  // Determine the correct endpoint based on item_id
  const endpoint =
    item_id === "3" || item_id === "4" || item_id === "5"
      ? `/api/lang_protected/${item_id}`
      : `/api/lang_public/${item_id}`;

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
    const humanAssistSection = document.getElementById("human-assist-section");

    const reader = response.body.getReader();
    let chunk = null;
    while ((chunk = await reader.read())) {
      if (!chunk.done) {
        const chunkData = new TextDecoder("utf-8").decode(chunk.value);
        console.log(`in handleLangFormSubmit: ${chunkData}`);

        try {
          const json = JSON.parse(chunkData);
          const message = createMessageElementAndCheckForHumanAssistance(json);
          console.log(`message in try ${JSON.stringify(message)}`);

          if (message) {
            messagesArea.appendChild(message);
          }
        } catch (error) {
          console.error("Error parsing JSON:", error);
          message.textContent = error;
          message.classList.add("error");
        }

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
    alert("error in handleLangFormSubmit");
  }
}

// Function to handle human verification form submission
async function handleHumanAssistFormSubmit(event, item_id) {
  console.log(`handleHumanAssistFormSubmit ${item_id}`);
  event.preventDefault();

  const isCorrect = document.getElementById("isCorrect").checked;
  const correctName = document.getElementById("correctName").value;
  const correctBirthday = document.getElementById("correctBirthday").value;

  const humanResponse = {
    correct: isCorrect ? "yes" : "no",
    name: correctName,
    birthday: correctBirthday,
  };
  const messagesArea = document.getElementById("messages");

  if (!humanResponse) {
    alert("Please enter an expert response");
    return;
  }

  try {
    const response = await fetch(`/api/lang_human_assist/${item_id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ human_response: humanResponse }),
    });

    if (response.ok) {
      const reader = response.body.getReader();
      let chunk = null;
      while ((chunk = await reader.read())) {
        if (!chunk.done) {
          const chunkData = new TextDecoder("utf-8").decode(chunk.value);
          console.log(
            `in handleHumanAssistFormSubmits, chunkData: ${chunkData}`
          );

          const json = JSON.parse(chunkData);
          const message = createMessageElementAndCheckForHumanAssistance(json);


          if (message) {
            console.log("we have a message here")
            messagesArea.appendChild(message);
            messagesArea.scrollTop = messagesArea.scrollHeight;
          }
        } else {
          break; // Add this line to properly end the stream reading
        }
      }

      // Hide the human assist section and clear the textarea
      const humanAssistSection = document.getElementById(
        "human-assist-section"
      );
      if (humanAssistSection) {
        humanAssistSection.classList.add("is-hidden");
      }
      //document.getElementById("humanResponse").value = "";
    }
  } catch (error) {
    console.error("Error in handleHumanAssistFormSubmit:", error);
    alert(`Error in handleHumanAssistFormSubmit: ${error}`);
  }
}

// Handle form submission and text input
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("myForm");
  const messageInput = document.getElementById("myName");
  const humanAssistForm = document.getElementById("humanAssistForm");

  if (form) {
    // Handle form submission
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const item_id = form.dataset.itemId || "1";
      if (item_id === "4") {
        handleLangFormSubmit(e, "4");
      } else {
        handleLangFormSubmit(e, item_id);
      }
    });
  }

  if (humanAssistForm) {
    // Handle human assistance form submission
    humanAssistForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const item_id = document.getElementById("myForm").dataset.itemId || "4";
      handleHumanAssistFormSubmit(e, item_id);
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
