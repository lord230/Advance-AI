const gameBoard = document.querySelector("#gameBoard");
const ctx = gameBoard.getContext("2d");
const scoreText = document.querySelector("#scoreText");
const score_max = document.querySelector("#score_max");
const resetBtn = document.querySelector("#resetBtn");
const unitSize = 25;

const gameWidth = gameBoard.width;
const gameHeight = gameBoard.height;
const boardBackground = "white";

let snake = [
    { x: unitSize * 2, y: 0 },
    { x: unitSize, y: 0 },
    { x: 0, y: 0 }
];
const snakeColor = "white";
const snakeBorder = "red";
const foodColor = "green";

let running = false;
let xVelocity = unitSize;
let yVelocity = 0;

let foodX;
let foodY;

let score = 0;

// Track collision learning
let moveHistory = [];

window.addEventListener("keydown", changeDirection);
resetBtn.addEventListener("click", resetGame);

gameStart();

function drawFilledCircle(ctx, x, y, radius) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.closePath();
    ctx.fill();
}

function gameStart() {
    running = true;
    scoreText.textContent = score;
    createFood();
    drawFood();
    nextTick();
}

function nextTick() {
    if (running) {
        setTimeout(() => {
            clearBoard();
            drawFood();
            moveSnake();
            drawSnake();
            checkGameOver();
            if (running) {
                computerPlay(); // Make the computer play
            }
            nextTick();
        }, 75);
    } else {
        displayGameOver();
        learnFromCollision();
    }
}

function clearBoard() {
    ctx.fillStyle = boardBackground;
    ctx.fillRect(0, 0, gameWidth, gameHeight);
}

function createFood() {
    function randomFood(min, max) {
        const randNum = Math.round((Math.random() * (max - min) + min) / unitSize) * unitSize;
        return randNum;
    }
    foodX = randomFood(0, gameWidth - unitSize);
    foodY = randomFood(0, gameHeight - unitSize);
}

function drawFood() {
    ctx.fillStyle = foodColor;
    const radius = unitSize / 2;
    drawFilledCircle(ctx, foodX + radius, foodY + radius, radius);
}

function drawSnake() {
    ctx.fillStyle = snakeColor;
    ctx.strokeStyle = snakeBorder;
    snake.forEach(snakePart => {
        ctx.fillRect(snakePart.x, snakePart.y, unitSize, unitSize);
        ctx.strokeRect(snakePart.x, snakePart.y, unitSize, unitSize);
    });
}

function moveSnake() {
    const head = {
        x: snake[0].x + xVelocity,
        y: snake[0].y + yVelocity
    };
    snake.unshift(head);
    if (snake[0].x === foodX && snake[0].y === foodY) {
        score += 1;
        scoreText.textContent = score;
        if (score > getHighestScore()) {
            score_max.textContent = score;
        }
        createFood();
    } else {
        snake.pop();
    }

    // Store the successful move in history
    let direction;
    if (xVelocity > 0) direction = 'right';
    else if (xVelocity < 0) direction = 'left';
    else if (yVelocity > 0) direction = 'down';
    else if (yVelocity < 0) direction = 'up';

    moveHistory.push({ direction, success: true, score });
}

function changeDirection(event) {
    const keyPressed = event.keyCode;
    const LEFT = 37;
    const RIGHT = 39;
    const UP = 38;
    const DOWN = 40;

    const goingUp = (yVelocity === -unitSize);
    const goingDown = (yVelocity === unitSize);
    const goingRight = (xVelocity === unitSize);
    const goingLeft = (xVelocity === -unitSize);

    switch (true) {
        case (keyPressed === LEFT && !goingRight):
            xVelocity = -unitSize;
            yVelocity = 0;
            break;

        case (keyPressed === UP && !goingDown):
            xVelocity = 0;
            yVelocity = -unitSize;
            break;

        case (keyPressed === RIGHT && !goingLeft):
            xVelocity = unitSize;
            yVelocity = 0;
            break;

        case (keyPressed === DOWN && !goingUp):
            xVelocity = 0;
            yVelocity = unitSize;
            break;
    }
}

function computerPlay() {
    const head = snake[0];

    function willCollide(newX, newY) {
        if (newX < 0 || newX >= gameWidth || newY < 0 || newY >= gameHeight) {
            return true;
        }
        for (let i = 1; i < snake.length; i++) {
            if (snake[i].x === newX && snake[i].y === newY) {
                return true;
            }
        }
        return false;
    }

    function moveTowardsFood() {
        if (head.x < foodX && !willCollide(head.x + unitSize, head.y) && xVelocity === 0) {
            xVelocity = unitSize;
            yVelocity = 0;
        } else if (head.x > foodX && !willCollide(head.x - unitSize, head.y) && xVelocity === 0) {
            xVelocity = -unitSize;
            yVelocity = 0;
        } else if (head.y < foodY && !willCollide(head.x, head.y + unitSize) && yVelocity === 0) {
            xVelocity = 0;
            yVelocity = unitSize;
        } else if (head.y > foodY && !willCollide(head.x, head.y - unitSize) && yVelocity === 0) {
            xVelocity = 0;
            yVelocity = -unitSize;
        }
    }

    function avoidCollision() {
        if (xVelocity !== 0) {
            if (!willCollide(head.x, head.y - unitSize)) {
                xVelocity = 0;
                yVelocity = -unitSize;
            } else if (!willCollide(head.x, head.y + unitSize)) {
                xVelocity = 0;
                yVelocity = unitSize;
            }
        } else if (yVelocity !== 0) {
            if (!willCollide(head.x - unitSize, head.y)) {
                xVelocity = -unitSize;
                yVelocity = 0;
            } else if (!willCollide(head.x + unitSize, head.y)) {
                xVelocity = unitSize;
                yVelocity = 0;
            }
        }
    }

    function getBestMove() {
        const moveScores = { up: 0, down: 0, left: 0, right: 0 };
        moveHistory.forEach(move => {
            if (move.success) {
                moveScores[move.direction]++;
            } else {
                moveScores[move.direction]--;
            }
        });

        const sortedMoves = Object.entries(moveScores).sort((a, b) => b[1] - a[1]);

        for (let [direction, score] of sortedMoves) {
            switch (direction) {
                case 'up':
                    if (!willCollide(head.x, head.y - unitSize)) return { x: 0, y: -unitSize };
                    break;
                case 'down':
                    if (!willCollide(head.x, head.y + unitSize)) return { x: 0, y: unitSize };
                    break;
                case 'left':
                    if (!willCollide(head.x - unitSize, head.y)) return { x: -unitSize, y: 0 };
                    break;
                case 'right':
                    if (!willCollide(head.x + unitSize, head.y)) return { x: unitSize, y: 0 };
                    break;
            }
        }

        return { x: xVelocity, y: yVelocity };
    }

    moveTowardsFood();
    if (willCollide(head.x + xVelocity, head.y + yVelocity)) {
        avoidCollision();
    } else {
        const bestMove = getBestMove();
        xVelocity = bestMove.x;
        yVelocity = bestMove.y;
    }
}

function checkGameOver() {
    switch (true) {
        case (snake[0].x < 0):
            running = false;
            break;
        case (snake[0].x >= gameWidth):
            running = false;
            break;
        case (snake[0].y < 0):
            running = false;
            break;
        case (snake[0].y >= gameHeight):
            running = false;
            break;
    }

    for (let i = 1; i < snake.length; i++) {
        if (snake[i].x === snake[0].x && snake[i].y === snake[0].y) {
            running = false;
        }
    }
}

function displayGameOver() {
    ctx.font = "50px MV Boli";
    ctx.fillStyle = "black";
    ctx.textAlign = "center";
    ctx.fillText("GAME OVER", gameWidth / 2, gameHeight / 2);
    running = false;
}

function resetGame() {
    score = 0;
    xVelocity = unitSize;
    yVelocity = 0;
    snake = [
        { x: unitSize * 2, y: 0 },
        { x: unitSize, y: 0 },
        { x: 0, y: 0 }
    ];
    moveHistory = []; // Clear history on reset
    gameStart();
}

function learnFromCollision() {
    let direction;
    if (xVelocity > 0) direction = 'right';
    else if (xVelocity < 0) direction = 'left';
    else if (yVelocity > 0) direction = 'down';
    else if (yVelocity < 0) direction = 'up';

    moveHistory.push({ direction, success: false, score });

    // Log collision history
    console.log("Collision History:", moveHistory);

    // Restart the game
    resetGame();
}

function getHighestScore() {
    let highest = 0;
    moveHistory.forEach(move => {
        if (move.score > highest) {
            highest = move.score;
        }
    });
    return highest;
}