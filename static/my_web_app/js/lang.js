console.log("Sanity in lang.js")

// Reusable function to handle form submission
async function handleLangFormSubmit(event, item_id) {
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
    const messagesArea = document.getElementById("messages");
    messagesArea.innerHTML = ""; // Clear previous content
    
    const reader = response.body.getReader();
    let chunk = null;
    while ((chunk = await reader.read())) {
      if (!chunk.done) {
        const chunkData = new TextDecoder("utf-8").decode(chunk.value);

        console.log(chunkData)
        const li = document.createElement("li");

        try {
            const json = JSON.parse(chunkData);
            const contentText = json.content;
            li.textContent = contentText
        } catch (error) {
            console.error('Error parsing JSON:', error);
            li.textContent=error
        }
        messagesArea.appendChild(li);
      } else {
        break; // Stop reading when the response is exhausted
      }
    }
  } else {
    // Display an error message
    alert("Error receiving name");
  }
}

// Get the form element and set up event listener
const form = document.getElementById("myForm");
if (form) {
  form.addEventListener("submit", async (event) => {
    // Get item_id from form data attribute or default to "1"
    const item_id = form.dataset.itemId || "1";
    await handleLangFormSubmit(event, item_id);
  });
}
