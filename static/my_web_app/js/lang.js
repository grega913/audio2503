// Get the form element
const form = document.getElementById("myForm");
const textAreaEl = document.getElementById("text-area");

form.addEventListener("submit", async (event) => {
  // Prevent the default form submission behavior
  event.preventDefault();

  // Get the name input value
  const myTxt = document.getElementById("myName").value;

  // Make a POST request to the /api/lang/1 route
  const response = await fetch("/api/lang/1", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input: myTxt }),
  });

  // Check if the response was successful
  if (response.ok) {
    const reader = response.body.getReader();
    let chunk = null;
        while ((chunk = await reader.read())) {
        if (!chunk.done) {
            const chunkData = new TextDecoder("utf-8").decode(chunk.value);
            console.log(chunkData); // Log each chunk of data
        } else {
            break; // Stop reading when the response is exhausted
        }
        }
     
  } else {
    // Display an error message
    alert("Error receiving name");
  }

});
