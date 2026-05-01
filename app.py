import streamlit as st
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(page_title="Apex Glider", layout="centered", page_icon="🦗")

st.title("🦗 Apex Glider")
st.write("**Controls:** Tap the screen, click the mouse, or press **Spacebar** to fly!")

# --- GAME HTML & JAVASCRIPT ---
game_html = """
<div id="game-container" style="text-align: center; user-select: none; touch-action: none;">
    <canvas id="gameCanvas" width="400" height="500" style="border:3px solid #1b5e20; border-radius: 8px; display: block; margin: 0 auto; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);"></canvas>
    <h2 id="scoreBoard" style="color: #1b5e20; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-top: 15px;">Energy: 100 | Score: 0</h2>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreBoard = document.getElementById("scoreBoard");

// 1. Game State Variables
let mantis = { x: 50, y: 200, width: 35, height: 35, velocity: 0, energy: 100, score: 0 };
let gravity = 0.4;
let jumpForce = -7;
let obstacles = [];
let food = [];
let frame = 0;
let isGameOver = false;

// 2. Input Handling
function jump() {
    if (isGameOver) {
        location.reload(); // Restart game
    } else {
        mantis.velocity = jumpForce;
    }
}

// Event Listeners (Spacebar, Click, Touch)
document.addEventListener('keydown', (e) => { if(e.code === 'Space') jump(); });
canvas.addEventListener('mousedown', jump);
canvas.addEventListener('touchstart', (e) => { e.preventDefault(); jump(); }, {passive: false});

// 3. Game Logic
function createObstacle() {
    let gap = 150; // Distance between top and bottom stems
    let minHeight = 50;
    let topHeight = Math.floor(Math.random() * (canvas.height - gap - (2 * minHeight))) + minHeight;
    obstacles.push({ x: canvas.width, y: 0, w: 40, h: topHeight });
    obstacles.push({ x: canvas.width, y: topHeight + gap, w: 40, h: canvas.height - topHeight - gap });
}

function createFood() {
    // Spawn a fly somewhere in the playable vertical space
    food.push({ x: canvas.width, y: Math.random() * (canvas.height - 60) + 30, width: 25, height: 25 });
}

function update() {
    if (isGameOver) return;

    // Physics
    mantis.velocity += gravity;
    mantis.y += mantis.velocity;
    mantis.energy -= 0.08; // Energy drains slowly over time

    // Hit the ground, ceiling, or run out of energy
    if (mantis.y + mantis.height >= canvas.height || mantis.y < 0 || mantis.energy <= 0) {
        return endGame();
    }

    // Spawning logic
    if (frame % 100 === 0) createObstacle();
    if (frame % 140 === 0) createFood();

    // Obstacles movement & collision
    obstacles.forEach((obs, index) => {
        obs.x -= 2.5; // Stem speed
        
        // Bounding box collision detection
        if (mantis.x < obs.x + obs.w && mantis.x + mantis.width > obs.x &&
            mantis.y < obs.y + obs.h && mantis.y + mantis.height > obs.y) {
            endGame();
        }
        
        // Remove off-screen obstacles and add to score
        if (obs.x + obs.w < 0) {
            obstacles.splice(index, 1);
            mantis.score += 0.5; // 0.5 because there is a top and bottom stem
        }
    });

    // Food movement & eating logic
    food.forEach((f, index) => {
        f.x -= 3; // Flies move slightly faster than stems
        if (mantis.x < f.x + f.width && mantis.x + mantis.width > f.x &&
            mantis.y < f.y + f.height && mantis.y + mantis.height > f.y) {
            mantis.energy = Math.min(100, mantis.energy + 20); // Cap energy at 100
            food.splice(index, 1);
        }
    });

    frame++;
    draw();
    
    // Update Scoreboard UI
    scoreBoard.innerHTML = `Energy: ${Math.max(0, Math.floor(mantis.energy))} | Score: ${Math.floor(mantis.score)}`;
    requestAnimationFrame(update);
}

// 4. Render (Using Emojis and Colors instead of Images)
function draw() {
    // Background (Sky Blue)
    ctx.fillStyle = "#87CEEB";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Obstacles (Green Stems)
    ctx.fillStyle = "#2e7d32";
    obstacles.forEach(obs => {
        ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
        
        // Add a little highlight to make it look like a stem
        ctx.fillStyle = "#4caf50";
        ctx.fillRect(obs.x, obs.y, 10, obs.h);
        ctx.fillStyle = "#2e7d32"; // reset for next stem
    });

    // Food (Fly Emoji)
    ctx.font = "20px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    food.forEach(f => {
        ctx.fillText("🪰", f.x + f.width/2, f.y + f.height/2);
    });

    // Mantis Emoji (Tilt character slightly based on falling velocity)
    ctx.save();
    ctx.translate(mantis.x + mantis.width / 2, mantis.y + mantis.height / 2);
    let rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (mantis.velocity * 0.1)));
    ctx.rotate(rotation);
    
    ctx.font = "35px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("🦗", 0, 0); // Drawn at 0,0 because we translated the context
    ctx.restore();
}

function endGame() {
    isGameOver = true;
    ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 35px 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("GAME OVER", canvas.width / 2, 230);
    ctx.font = "18px 'Segoe UI', sans-serif";
    ctx.fillText("Tap or Click to Restart", canvas.width / 2, 270);
}

// Start the game immediately
update();

</script>
"""

# Render the custom component in Streamlit
components.html(game_html, height=650)