import streamlit as st
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(page_title="Apex Glider", layout="centered", page_icon="🦗")

st.title("🦗 Apex Glider")
# Removed the st.write() controls text as requested!

# --- GAME HTML & JAVASCRIPT ---
# Notice the canvas width is now 450 and height is 600 (3:4 ratio)
game_html = """
<div id="game-container" style="text-align: center; user-select: none; touch-action: none;">
    <canvas id="gameCanvas" width="450" height="600" style="border:3px solid #1b5e20; border-radius: 8px; display: block; margin: 0 auto; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);"></canvas>
    <h2 id="scoreBoard" style="color: #1b5e20; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-top: 15px;">Energy: 100 | Score: 0</h2>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreBoard = document.getElementById("scoreBoard");

// 1. Game State Variables
let gameState = "START"; // Can be "START", "PLAYING", or "GAMEOVER"
let mantis = { x: 60, y: 250, width: 35, height: 35, velocity: 0, energy: 100, score: 0 };
let gravity = 0.4;
let jumpForce = -7;
let obstacles = [];
let food = [];
let frame = 0;

// 2. Input Handling
function jump() {
    if (gameState === "GAMEOVER") {
        location.reload(); // Restart game
    } else if (gameState === "START") {
        gameState = "PLAYING"; // Transition from start screen to playing
        mantis.velocity = jumpForce;
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
    let gap = 160; // Slightly larger gap for the taller screen
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

    // --- PLAYING LOGIC ---
    // Physics
    mantis.velocity += gravity;
    mantis.y += mantis.velocity;
    mantis.energy -= 0.08; 

    // Hit the ground, ceiling, or run out of energy
    if (mantis.y + mantis.height >= canvas.height || mantis.y < 0 || mantis.energy <= 0) {
        return endGame();
    }

    // Spawning logic
    if (frame % 110 === 0) createObstacle();
    if (frame % 150 === 0) createFood();

    // Obstacles movement & collision
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

    // Food movement & eating logic
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
    // Background (Sky Blue)
    ctx.fillStyle = "#87CEEB";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Obstacles (Green Stems)
    ctx.fillStyle = "#2e7d32";
    obstacles.forEach(obs => {
        ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
        ctx.fillStyle = "#4caf50";
        ctx.fillRect(obs.x, obs.y, 10, obs.h);
        ctx.fillStyle = "#2e7d32"; 
    });

    // Food (Fly Emoji)
    ctx.font = "24px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    food.forEach(f => {
        ctx.fillText("🪰", f.x + f.width/2, f.y + f.height/2);
    });

    // Mantis Emoji
    ctx.save();
    ctx.translate(mantis.x + mantis.width / 2, mantis.y + mantis.height / 2);
    let rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (mantis.velocity * 0.1)));
    ctx.rotate(rotation);
    
    ctx.font = "40px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("🦗", 0, 0); 
    ctx.restore();
}

function drawStartScreen() {
    draw(); // Draw the background elements first
    
    // Add dark overlay
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add text
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

// Start the loop
update();

</script>
"""

# Render the custom component in Streamlit. Height adjusted for the new aspect ratio.
components.html(game_html, height=750)