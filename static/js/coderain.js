const canvas = document.getElementById("background");
const context = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Create a matrix of code characters
const columns = Math.floor(canvas.width / 12); // Number of columns of code rain
const codeMatrix = [];
for (let i = 0; i < columns; i++) {
  codeMatrix[i] = Math.floor(Math.random() * canvas.height);
}

// Draw the code rain effect
function draw() {
  context.fillStyle = "rgba(0, 0, 0, 0.05)";
  context.fillRect(0, 0, canvas.width, canvas.height);

  context.fillStyle = "#0F0";
  context.font = "12pt Courier New";
  for (let i = 0; i < columns; i++) {
    const x = i * 12;
    const y = codeMatrix[i];
    context.fillText(String.fromCharCode(65 + Math.floor(Math.random() * 56)), x, y);
    if (y > canvas.height && Math.random() > 0.975) {
      codeMatrix[i] = 0;
    } else {
      codeMatrix[i] += 12;
    }
  }
}

setInterval(draw, 50); // Refresh the code rain effect every 50 milliseconds
