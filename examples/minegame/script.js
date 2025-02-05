
document.addEventListener("DOMContentLoaded", () => {
  const gameContainer = document.getElementById("game-container");
  const gridSize = 10;
  const mineCount = 20;
  const grid = [];
  const mineArray = [];

  function generateMineArray() {
    while (mineArray.length < mineCount) {
      const randomIndex = Math.floor(Math.random() * gridSize * gridSize);
      if (!mineArray.includes(randomIndex)) {
        mineArray.push(randomIndex);
      }
    }
  }

  function createGrid() {
    gameContainer.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;
    gameContainer.style.gridTemplateRows = `repeat(${gridSize}, 1fr)`;
    for (let i = 0; i < gridSize * gridSize; i++) {
      const cell = document.createElement("div");
      cell.classList.add("cell");
      cell.setAttribute("data-id", i);
      gameContainer.appendChild(cell);
      grid.push(cell);
    }
  }

  function placeMines() {
    mineArray.forEach(index => {
      grid[index].classList.add("mine");
    });
  }

  function addClickHandlers() {
    grid.forEach(cell => {
      cell.addEventListener("click", (e) => {
        const cell = e.target;
        const cellId = parseInt(cell.getAttribute("data-id"));

        if (cell.classList.contains("mine")) {
          revealMines();
          showEndMessage("Game Over");
        } else {
          revealCell(cellId);
          checkGameWin();
        }
      });

      cell.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        toggleFlag(cell);
      });
    });
  }

  function toggleFlag(cell) {
    if (!cell.classList.contains("revealed")) {
      cell.classList.toggle("flag");
    }
  }

  function revealCell(cellId) {
    if (cellId < 0 || cellId >= grid.length || grid[cellId].classList.contains("revealed")) {
      return;
    }

    grid[cellId].classList.add("revealed");
    const isMine = grid[cellId].classList.contains("mine");
    if (!isMine) {
      const adjacentMines = countAdjacentMines(cellId);
      if (adjacentMines > 0) {
        grid[cellId].textContent = adjacentMines;
      } else {
        revealAdjacentCells(cellId);
      }
    }
  }

  function countAdjacentMines(cellId) {
    const adjacentCells = getAdjacentCells(cellId);
    return adjacentCells.filter(id => grid[id].classList.contains("mine")).length;
  }

  function revealAdjacentCells(cellId) {
    const adjacentCells = getAdjacentCells(cellId);
    adjacentCells.forEach(id => revealCell(id));
  }

  function getAdjacentCells(cellId) {
    const adjacentCells = [];
    const row = Math.floor(cellId / gridSize);
    const col = cellId % gridSize;

    for (let r = row - 1; r <= row + 1; r++) {
      for (let c = col - 1; c <= col + 1; c++) {
        if (r >= 0 && r < gridSize && c >= 0 && c < gridSize && !(r === row && c === col)) {
          adjacentCells.push(r * gridSize + c);
        }
      }
    }

    return adjacentCells;
  }

  function revealMines() {
    mineArray.forEach(index => {
      grid[index].classList.add("revealed");
    });
  }

  function showEndMessage(message) {
    const endMessage = document.createElement("div");
    endMessage.id = "end-message";
    endMessage.textContent = message;
    document.body.appendChild(endMessage);
    document.getElementById("restart-btn").style.display = "block";
  }

  function removeEndMessage() {
    const endMessage = document.getElementById("end-message");
    if (endMessage) {
      document.body.removeChild(endMessage);
    }
  }

  function checkGameWin() {
    const unrevealedCells = grid.filter(cell =>
      !cell.classList.contains("revealed") && !cell.classList.contains("mine")
    );
    if (unrevealedCells.length === 0) {
      revealMines();
      showEndMessage("You Win!");
    }
  }

function init() {
    document.getElementById("restart-btn").style.display = "none";
    removeEndMessage();
    generateMineArray();
    createGrid();
    placeMines();
    addClickHandlers();
  }

  init();
  document.getElementById("restart-btn").addEventListener("click", () => {
    resetGame();
  });

function resetGame() {
  gameContainer.innerHTML = "";
  grid.length = 0;
  mineArray.length = 0;
  init();
}
});
