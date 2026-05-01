import streamlit as st
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(page_title="Apex Glider", layout="centered", page_icon="🦗")

# --- REMOVE STREAMLIT DEFAULT PADDING ---
st.markdown("""
    <style>
        /* This targets the main Streamlit container and removes the top whitespace */
        .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 0rem !important;
            margin-top: 0rem !important;
        }
        /* Hides the default Streamlit header bar (with the 'Deploy' button) to save more space */
        header {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# --- GAME HTML & JAVASCRIPT ---
game_html = """
<div id="game-container" style="text-align: center; user-select: none; touch-action: none; position: relative; width: 300px; margin: 0 auto;">
    <canvas id="gameCanvas" width="300" height="650" style="border:3px solid #1b5e20; border-radius: 8px; display: block; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);"></canvas>
    
    <!-- Scoreboard -->
    <div id="scoreBoard" style="position: absolute; bottom: 10px; left: 0; width: 100%; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 18px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); pointer-events: none;">
        Energy: 100 | Score: 0
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreBoard = document.getElementById("scoreBoard");

// 1. Game State Variables
let gameState = "START"; 
let mantis = { x: 50, y: 300, width: 30, height: 30, velocity: 0, energy: 100, score: 0 }; 
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
    obstacles.push({ x: canvas.width, y: 0, w: 40, h: topHeight });
    obstacles.push({ x: canvas.width, y: topHeight + gap, w: 40, h: canvas.height - topHeight - gap });
}

function createFood() {
    food.push({ x: canvas.width, y: Math.random() * (canvas.height - 80) + 40, width: 20, height: 20 });
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

    if (frame % 100 === 0) createObstacle(); 
    if (frame % 140 === 0) createFood();

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
        ctx.fillRect(obs.x, obs.y, 8, obs.h);
        ctx.fillStyle = "#2e7d32"; 
    });

    // Food
    ctx.font = "20px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    food.forEach(f => {
        ctx.fillText("🪰", f.x + f.width/2, f.y + f.height/2);
    });

    // --- CUSTOM GREEN MANTIS ---
    ctx.save();
    ctx.translate(mantis.x + mantis.width / 2, mantis.y + mantis.height / 2);
    
    let rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (mantis.velocity * 0.1)));
    
    ctx.scale(-1, 1); 
    ctx.rotate(-rotation); 
    
    // Body 
    ctx.fillStyle = "#4caf50"; 
    ctx.beginPath();
    ctx.ellipse(0, 0, 14, 7, 0, 0, Math.PI * 2);
    ctx.fill();

    // Head
    ctx.fillStyle = "#2e7d32"; 
    ctx.beginPath();
    ctx.arc(-12, -3, 6, 0, Math.PI * 2);
    ctx.fill();

    // Eye 
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(-14, -4, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "black";
    ctx.beginPath();
    ctx.arc(-14.5, -4, 1.2, 0, Math.PI * 2);
    ctx.fill();

    // Front Scythe Arm 
    ctx.strokeStyle = "#1b5e20";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(-8, 0);
    ctx.lineTo(-15, 10);
    ctx.lineTo(-20, 5);
    ctx.stroke();

    ctx.restore();
}

function drawStartScreen() {
    draw(); 
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.font = "bold 32px 'Segoe UI', sans-serif";
    ctx.fillText("APEX GLIDER", canvas.width / 2, canvas.height / 2 - 40);
    ctx.font = "16px 'Segoe UI', sans-serif";
    ctx.fillText("Tap to fly!", canvas.width / 2, canvas.height / 2 + 10);
}

function endGame() {
    gameState = "GAMEOVER";
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 32px 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);
    ctx.font = "16px 'Segoe UI', sans-serif";
    ctx.fillText("Tap to Restart", canvas.width / 2, canvas.height / 2 + 20);
}

update();
</script>
"""

# Streamlit component height
components.html(game_html, height=660)