
const canvas = document.getElementById("gameBoard");
const ctx = canvas.getContext("2d");

// Game settings
const gridSize = 20; // Size of one grid block
const totalGrid = canvas.width / gridSize;

// Snake, food, and score
let snake = [{ x: 10, y: 10 }];
let food = { x: 5, y: 5 };
let direction = { x: 0, y: 0 };
let score = 0;

// Draw a rectangle
function drawRect(x, y, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x * gridSize, y * gridSize, gridSize - 2, gridSize - 2);
}

// Spawn food randomly
function spawnFood() {
    food.x = Math.floor(Math.random() * totalGrid);
    food.y = Math.floor(Math.random() * totalGrid);
}

// Main game loop
function gameLoop() {
    // Move snake
    const head = {
        x: snake[0].x + direction.x,
        y: snake[0].y + direction.y
    };
    snake.unshift(head);

    // Check food collision
    if (head.x === food.x && head.y === food.y) {
        score++;
        document.getElementById("score").innerText = score;
        spawnFood();
    } else {
        snake.pop(); // Remove tail if no food eaten
    }

    // Check wall or self collision
    if (
        head.x < 0 || head.x >= totalGrid ||
        head.y < 0 || head.y >= totalGrid ||
        snake.slice(1).some(segment => segment.x === head.x && segment.y === head.y)
    ) {
        alert("Game Over! Your score: " + score);
        resetGame();
        return;
    }

    // Redraw elements
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawRect(food.x, food.y, "red"); // Draw food
    snake.forEach(segment => drawRect(segment.x, segment.y, "lime")); // Draw snake
}

// Reset game
function resetGame() {
    snake = [{ x: 10, y: 10 }];
    direction = { x: 0, y: 0 };
    score = 0;
    document.getElementById("score").innerText = score;
    spawnFood();
}

// Handle keyboard inputs
document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowUp" && direction.y === 0) {
        direction = { x: 0, y: -1 };
    } else if (event.key === "ArrowDown" && direction.y === 0) {
        direction = { x: 0, y: 1 };
    } else if (event.key === "ArrowLeft" && direction.x === 0) {
        direction = { x: -1, y: 0 };
    } else if (event.key === "ArrowRight" && direction.x === 0) {
        direction = { x: 1, y: 0 };
    }
});

// Start game
resetGame();
setInterval(gameLoop, 100); // Run game loop every 100ms
