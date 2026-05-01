import streamlit as st
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(page_title="Apex Glider", layout="centered", page_icon="🦗")

# --- GAME HTML & JAVASCRIPT ---
game_html = """
<div id="game-container" style="text-align: center; user-select: none; touch-action: none; position: relative; width: 450px; margin: 0 auto;">
    <canvas id="gameCanvas" width="450" height="600" style="border:3px solid #1b5e20; border-radius: 8px; display: block; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);"></canvas>
    
    <!-- Scoreboard moved INSIDE the canvas container at the bottom -->
    <div id="scoreBoard" style="position: absolute; bottom: 10px; left: 0; width: 100%; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 20px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); pointer-events: none;">
        Energy: 100 | Score: 0
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreBoard = document.getElementById("scoreBoard");

// 1. Game State Variables
let gameState = "START"; 
let mantis = { x: 60, y: 250, width: 35, height: 35, velocity: 0, energy: 100, score: 0 };
let gravity = 0.4;
let jumpForce = -7;
let obstacles = [];
let food = [];
let frame = 0;

// 2. Input Handling
function jump() {
    if (gameState === "GAMEOVER") {
        location.reload(); 
    } else if (gameState === "START") {
        gameState = "PLAYING"; 
        mantis.velocity = jumpForce;
    } else {
        mantis.velocity = jumpForce;
    }
}

document.addEventListener('keydown', (e) => { if(e.code === 'Space') jump(); });
canvas.addEventListener('mousedown', jump);
canvas.addEventListener('touchstart', (e) => { e.preventDefault(); jump(); }, {passive: false});

// 3. Game Logic
function createObstacle() {
    let gap = 160; 
    let minHeight = 50;
    let topHeight = Math.floor(Math.random() * (canvas.height - gap - (2 * minHeight))) + minHeight;
    obstacles.push({ x: canvas.width, y: 0, w: 45, h: topHeight });
    obstacles.push({ x: canvas.width, y: topHeight + gap, w: 45, h: canvas.height - topHeight - gap });
}

function createFood() {
    food.push({ x: canvas.width, y: Math.random() * (canvas.height - 80) + 40, width: 25, height: 25 });
}

function update() {
    if (gameState === "GAMEOVER") return;

    if (gameState === "START") {
        drawStartScreen();
        requestAnimationFrame(update);
        return;
    }

    // Physics
    mantis.velocity += gravity;
    mantis.y += mantis.velocity;
    mantis.energy -= 0.08; 

    // Hit boundaries or out of energy
    if (mantis.y + mantis.height >= canvas.height || mantis.y < 0 || mantis.energy <= 0) {
        return endGame();
    }

    if (frame % 110 === 0) createObstacle();
    if (frame % 150 === 0) createFood();

    obstacles.forEach((obs, index) => {
        obs.x -= 2.5; 
        if (mantis.x < obs.x + obs.w && mantis.x + mantis.width > obs.x &&
            mantis.y < obs.y + obs.h && mantis.y + mantis.height > obs.y) {
            endGame();
        }
        if (obs.x + obs.w < 0) {
            obstacles.splice(index, 1);
            mantis.score += 0.5; 
        }
    });

    food.forEach((f, index) => {
        f.x -= 3; 
        if (mantis.x < f.x + f.width && mantis.x + mantis.width > f.x &&
            mantis.y < f.y + f.height && mantis.y + mantis.height > f.y) {
            mantis.energy = Math.min(100, mantis.energy + 20); 
            food.splice(index, 1);
        }
    });

    frame++;
    draw();
    scoreBoard.innerHTML = `Energy: ${Math.max(0, Math.floor(mantis.energy))} | Score: ${Math.floor(mantis.score)}`;
    requestAnimationFrame(update);
}

// 4. Render 
function draw() {
    // Background
    ctx.fillStyle = "#87CEEB";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Obstacles
    ctx.fillStyle = "#2e7d32";
    obstacles.forEach(obs => {
        ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
        ctx.fillStyle = "#4caf50";
        ctx.fillRect(obs.x, obs.y, 10, obs.h);
        ctx.fillStyle = "#2e7d32"; 
    });

    // Food
    ctx.font = "24px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    food.forEach(f => {
        ctx.fillText("🪰", f.x + f.width/2, f.y + f.height/2);
    });

    // --- CUSTOM GREEN MANTIS ---
    ctx.save();
    ctx.translate(mantis.x + mantis.width / 2, mantis.y + mantis.height / 2);
    
    let rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (mantis.velocity * 0.1)));
    
    // Scale to face right, and adjust rotation
    ctx.scale(-1, 1); 
    ctx.rotate(-rotation); 
    
    // Body (Green oval)
    ctx.fillStyle = "#4caf50"; 
    ctx.beginPath();
    ctx.ellipse(0, 0, 16, 8, 0, 0, Math.PI * 2);
    ctx.fill();

    // Head (Darker green circle)
    ctx.fillStyle = "#2e7d32"; 
    ctx.beginPath();
    ctx.arc(-14, -4, 7, 0, Math.PI * 2);
    ctx.fill();

    // Eye (White and black dot)
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(-16, -5, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "black";
    ctx.beginPath();
    ctx.arc(-16.5, -5, 1.5, 0, Math.PI * 2);
    ctx.fill();

    // Front Scythe Arm (Classic mantis pose)
    ctx.strokeStyle = "#1b5e20";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(-10, 0);
    ctx.lineTo(-18, 12);
    ctx.lineTo(-24, 6);
    ctx.stroke();

    ctx.restore();
}

function drawStartScreen() {
    draw(); 
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.font = "bold 40px 'Segoe UI', sans-serif";
    ctx.fillText("APEX GLIDER", canvas.width / 2, canvas.height / 2 - 50);
    ctx.font = "18px 'Segoe UI', sans-serif";
    ctx.fillText("Tap the screen, click the mouse,", canvas.width / 2, canvas.height / 2 + 10);
    ctx.fillText("or press Spacebar to fly!", canvas.width / 2, canvas.height / 2 + 40);
}

function endGame() {
    gameState = "GAMEOVER";
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 40px 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);
    ctx.font = "20px 'Segoe UI', sans-serif";
    ctx.fillText("Tap or Click to Restart", canvas.width / 2, canvas.height / 2 + 30);
}

update();
</script>
"""

components.html(game_html, height=650)