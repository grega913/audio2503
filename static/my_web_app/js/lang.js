console.log("Sanity in lang.js")


// Get the form element
const form = document.getElementById("myForm");


form.addEventListener("submit", async (event) => {
  // Prevent the default form submission behavior
  event.preventDefault();

  // Get the name input value
  const myTxt = document.getElementById("myName").value;

  // Get the current URL path and extract item_id
  const pathSegments = window.location.pathname.split('/');
  const item_id = pathSegments[pathSegments.length - 1];
  
  if (!item_id) {
    alert("Invalid URL - missing item_id");
    return;
  }

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

});
