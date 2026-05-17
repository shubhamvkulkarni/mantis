import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Apex Glider", layout="centered", page_icon="🦗")

# --- REMOVE STREAMLIT DEFAULT PADDING ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 0rem !important;
            margin-top: 0rem !important;
        }
        header {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# --- IMAGE LOADER ---
def get_base64_image(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = file_path.split('.')[-1].lower()
            mime_type = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime_type};base64,{encoded}" 
    return "" 

bg_img_data = get_base64_image("assets/background.jpg")
mantis_img_data = get_base64_image("assets/mantis.png")

# --- GAME HTML & JAVASCRIPT ---
game_html = """
<div id="game-container" style="text-align: center; user-select: none; touch-action: none; position: relative; width: 320px; margin: 0 auto;">
    <canvas id="gameCanvas" width="320" height="560" style="border:3px solid #1b5e20; border-radius: 8px; display: block; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);"></canvas>
    
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
let mantis = { x: 50, y: 280, width: 35, height: 35, velocity: 0, energy: 100, score: 0 }; 
let gravity = 0.4;
let jumpForce = -7;
let bgX = 0; 
let obstacles = [];
let food = [];
let frame = 0;

// Load Images
const bgImg = new Image();
bgImg.src = "BACKGROUND_IMAGE_DATA"; 

const mantisImg = new Image();
mantisImg.src = "MANTIS_IMAGE_DATA";

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
    let gap = 150; 
    let minHeight = 50;
    let topHeight = Math.floor(Math.random() * (canvas.height - gap - (2 * minHeight))) + minHeight;
    obstacles.push({ x: canvas.width, y: 0, w: 40, h: topHeight });
    obstacles.push({ x: canvas.width, y: topHeight + gap, w: 40, h: canvas.height - topHeight - gap });
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

    // Hit boundaries
    if (mantis.y + mantis.height >= canvas.height || mantis.y < 0 || mantis.energy <= 0) {
        return endGame();
    }

    // Scroll Background
    bgX -= 1;
    if (bgX <= -canvas.width) bgX = 0;

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
    // Background Image
    if (bgImg.src && bgImg.src.startsWith("data:image")) {
        ctx.drawImage(bgImg, bgX, 0, canvas.width, canvas.height);
        ctx.drawImage(bgImg, bgX + canvas.width, 0, canvas.width, canvas.height);
    } else {
        ctx.fillStyle = "#87CEEB";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // --- PROCEDURAL OBSTACLES ---
    obstacles.forEach(obs => {
        if (obs.y === 0) {
            // TOP OBSTACLE: Hanging Branch
            
            // 1. Draw Wood Trunk
            ctx.fillStyle = "#5d4037"; // Brown
            ctx.fillRect(obs.x + 10, obs.y, obs.w - 20, obs.h - 20);
            
            // 2. Draw Leaf Clusters
            ctx.fillStyle = "#2e7d32"; // Dark Green
            ctx.beginPath();
            // Center cluster
            ctx.arc(obs.x + obs.w/2, obs.y + obs.h - 20, 22, 0, Math.PI * 2); 
            // Left cluster
            ctx.arc(obs.x + 5, obs.y + obs.h - 35, 16, 0, Math.PI * 2);       
            // Right cluster
            ctx.arc(obs.x + obs.w - 5, obs.y + obs.h - 35, 16, 0, Math.PI * 2); 
            ctx.fill();

            // Light Green Highlights on leaves
            ctx.fillStyle = "#4caf50"; 
            ctx.beginPath();
            ctx.arc(obs.x + obs.w/2 - 6, obs.y + obs.h - 24, 10, 0, Math.PI * 2); 
            ctx.fill();

        } else {
            // BOTTOM OBSTACLE: Tall Grass
            
            // 1. Solid base
            ctx.fillStyle = "#1b5e20"; // Very dark green base
            ctx.fillRect(obs.x, obs.y + 18, obs.w, obs.h - 18);
            
            // 2. Spiky Grass Blades reaching up
            ctx.fillStyle = "#4caf50"; // Brighter green blades
            ctx.beginPath();
            ctx.moveTo(obs.x, obs.y + 20); // Start slightly lower than the bounding box
            
            let blades = 3; 
            let bladeWidth = obs.w / blades;
            
            for (let i = 0; i < blades; i++) {
                // Tip of the blade (alternating height slightly for organic look)
                let peakOffset = i % 2 === 0 ? 0 : 6;
                ctx.lineTo(obs.x + (i * bladeWidth) + (bladeWidth * 0.4), obs.y + peakOffset); 
                // Base of the blade
                ctx.lineTo(obs.x + ((i + 1) * bladeWidth), obs.y + 20);
            }
            ctx.fill();
        }
    });

    // Food (Fly Emoji)
    ctx.font = "20px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    food.forEach(f => {
        ctx.fillText("🪰", f.x + f.width/2, f.y + f.height/2);
    });

    // Mantis Rendering
    ctx.save();
    ctx.translate(mantis.x + mantis.width / 2, mantis.y + mantis.height / 2);
    
    let rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (mantis.velocity * 0.1)));
    
    // Uncomment next line if your mantis.png naturally faces LEFT
    // ctx.scale(-1, 1); 
    
    ctx.rotate(rotation); 
    
    if (mantisImg.src && mantisImg.src.startsWith("data:image")) {
        ctx.drawImage(mantisImg, -mantis.width / 2, -mantis.height / 2, mantis.width, mantis.height);
    } else {
        ctx.font = "35px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("🦗", 0, 0); 
    }
    
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

setTimeout(update, 100);
</script>
"""

game_html = game_html.replace("BACKGROUND_IMAGE_DATA", bg_img_data)
game_html = game_html.replace("MANTIS_IMAGE_DATA", mantis_img_data)

components.html(game_html, height=580)