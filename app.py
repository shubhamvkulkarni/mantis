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
banglore_img_data = get_base64_image("assets/banglore.jpg")

# --- GAME HTML & JAVASCRIPT ---
game_html = """
<div id="game-container" style="text-align: center; user-select: none; touch-action: none; position: relative; width: 320px; margin: 0 auto;">
    <canvas id="gameCanvas" width="320" height="560" style="border:3px solid #1b5e20; border-radius: 8px; display: block; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);"></canvas>
    
    <div id="scoreBoard" style="position: absolute; bottom: 10px; left: 0; width: 100%; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 18px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); pointer-events: none;">
        Score: 0 | ❤️: 2
    </div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreBoard = document.getElementById("scoreBoard");

// --- AUDIO SYNTHESIZER ---
const AudioContext = window.AudioContext || window.webkitAudioContext;
const audioCtx = new AudioContext();

function playSound(type) {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    if (type === 'jump') {
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(300, audioCtx.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(600, audioCtx.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.1);
        
    } else if (type === 'eat') {
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime);
        oscillator.frequency.setValueAtTime(1200, audioCtx.currentTime + 0.05);
        gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.1);
        
    } else if (type === 'crash') {
        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(150, audioCtx.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.3);
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.3);
        
    } else if (type === 'milestone') {
        // Uplifting 3-note chime
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(440, audioCtx.currentTime); // A4
        oscillator.frequency.setValueAtTime(554.37, audioCtx.currentTime + 0.1); // C#5
        oscillator.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.2); // E5
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.5);
        
    } else if (type === 'victory') {
        // Triumphant 4-note fanfare
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
        oscillator.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.15); // E5
        oscillator.frequency.setValueAtTime(783.99, audioCtx.currentTime + 0.3); // G5
        oscillator.frequency.setValueAtTime(1046.50, audioCtx.currentTime + 0.45); // C6
        gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.8);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.8);
    }
}

// 1. Game State Variables
let gameState = "START"; 
let mantis = { x: 50, y: 280, width: 35, height: 35, velocity: 0, score: 0 }; 
let gravity = 0.4;
let jumpForce = -7;
let bgX = 0; 
let obstacles = [];
let food = [];
let hearts = [];
let frame = 0;
let deathCount = 0; 
let lives = 2;
let fliesEaten = 0;
let collisionCount = 0;

let hasMilestone15 = false;
let hasWon = false;
let specialTapCount = 0; // Tracks taps for milestone and victory screens

const bgImg = new Image();
bgImg.src = "BACKGROUND_IMAGE_DATA"; 

const mantisImg = new Image();
mantisImg.src = "MANTIS_IMAGE_DATA";

const bangloreImg = new Image();
bangloreImg.src = "BANGLORE_IMAGE_DATA";

let currentBgImg = bgImg;

const gameOverMessages = [
    { main: "Bangalore is still far away...", sub: "Tap to try the journey again!" },
    { main: "Bok got grounded!", sub: "Tap to dust off his wings and restart." },
    { main: "Ouch! Missed the gap.", sub: "Tap to take off and try again!" },
    { main: "Flight Interrupted!", sub: "Tap to resume the trip to Bangalore." },
    { main: "Oh no, Bok crashed!", sub: "Bangalore awaits! Tap to restart." }
];

const collisionMessages = [
    "Mayday! Exoskeleton compromised!",
    "Praying for better flight controls...",
    "Mid-air traffic collision!",
    "Who put that obstacle there?!"
];

// --- INSTANT RESTART LOGIC ---
function resetGame() {
    mantis = { x: 50, y: 280, width: 35, height: 35, velocity: jumpForce, score: 0 }; 
    lives = 2;
    fliesEaten = 0;
    collisionCount = 0;
    specialTapCount = 0;
    hasMilestone15 = false;
    hasWon = false;
    currentBgImg = bgImg; 
    obstacles = [];
    food = [];
    hearts = [];
    frame = 0;
    bgX = 0;
    scoreBoard.innerHTML = `Score: 0 | ❤️: 2`;
    gameState = "PLAYING"; 
    playSound('jump'); 
    update(); 
}

// 2. Input Handling
function jump() {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    
    if (gameState === "GAMEOVER") {
        resetGame(); 
    } else if (gameState === "VICTORY") {
        specialTapCount++;
        if (specialTapCount >= 3) {
            specialTapCount = 0;
            resetGame();
        } else {
            drawVictoryScreen(); // Re-render to show updated tap count
        }
    } else if (gameState === "START") {
        gameState = "PLAYING"; 
        mantis.velocity = jumpForce;
        playSound('jump');
    } else if (gameState === "PAUSED") {
        gameState = "PLAYING";
        mantis.y = 280;
        mantis.velocity = jumpForce;
        obstacles = [];
        food = [];
        hearts = [];
        playSound('jump');
        update(); 
    } else if (gameState === "MILESTONE_15") {
        specialTapCount++;
        if (specialTapCount >= 3) {
            specialTapCount = 0;
            gameState = "PLAYING";
            playSound('jump');
            update();
        } else {
            drawMilestoneScreen(); // Re-render to show updated tap count
        }
    } else {
        mantis.velocity = jumpForce;
        playSound('jump');
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

function createHeart() {
    hearts.push({ x: canvas.width, y: Math.random() * (canvas.height - 80) + 40, width: 25, height: 25 });
}

function handleDamage() {
    playSound('crash');
    lives--;
    
    scoreBoard.innerHTML = `Score: ${Math.floor(mantis.score)} | ❤️: ${lives}`;

    if (lives <= 0) {
        endGame();
    } else {
        gameState = "PAUSED";
        collisionCount++;
        drawPauseScreen(); 
    }
}

function update() {
    if (gameState === "GAMEOVER" || gameState === "PAUSED" || gameState === "MILESTONE_15" || gameState === "VICTORY") return; 

    if (gameState === "START") {
        drawStartScreen();
        requestAnimationFrame(update);
        return;
    }

    // 15 Point Milestone Pause
    if (mantis.score >= 15 && !hasMilestone15) {
        hasMilestone15 = true;
        gameState = "MILESTONE_15";
        specialTapCount = 0;
        playSound('milestone'); // Play special sound!
        drawMilestoneScreen();
        return; 
    }

    // 45 Point Background Swap
    if (mantis.score >= 45) {
        currentBgImg = bangloreImg;
    }

    // 50 Point Victory
    if (mantis.score >= 50 && !hasWon) {
        hasWon = true;
        gameState = "VICTORY";
        specialTapCount = 0;
        playSound('victory'); // Play fanfare sound!
        drawVictoryScreen();
        return;
    }

    // Physics
    mantis.velocity += gravity;
    mantis.y += mantis.velocity;

    // Hit floor or ceiling
    if (mantis.y + mantis.height >= canvas.height || mantis.y < 0) {
        handleDamage();
        return; 
    }

    // Scroll Background
    bgX -= 1;
    if (bgX <= -canvas.width) bgX = 0;

    if (frame % 100 === 0) createObstacle(); 
    if (frame % 140 === 0) createFood();
    if (frame % 1400 === 0) createHeart(); 

    let hitObstacle = false; 

    obstacles.forEach((obs, index) => {
        obs.x -= 2.5; 
        
        let pad = 4;
        if (mantis.x + pad < obs.x + obs.w && mantis.x + mantis.width - pad > obs.x &&
            mantis.y + pad < obs.y + obs.h && mantis.y + mantis.height - pad > obs.y) {
            hitObstacle = true;
        }
        
        if (obs.x + obs.w < 0) {
            obstacles.splice(index, 1);
            mantis.score += 0.5; 
        }
    });

    if (hitObstacle) {
        handleDamage();
        return; 
    }

    // Food (Flies) Collision
    food.forEach((f, index) => {
        f.x -= 3; 
        if (mantis.x < f.x + f.width && mantis.x + mantis.width > f.x &&
            mantis.y < f.y + f.height && mantis.y + mantis.height > f.y) {
            
            fliesEaten++;
            if (fliesEaten >= 5) {
                lives++;
                fliesEaten = 0;
            }
            food.splice(index, 1);
            playSound('eat'); 
        }
    });

    // Heart Collision
    hearts.forEach((h, index) => {
        h.x -= 3;
        if (mantis.x < h.x + h.width && mantis.x + mantis.width > h.x &&
            mantis.y < h.y + h.height && mantis.y + mantis.height > h.y) {
            
            lives++;
            hearts.splice(index, 1);
            playSound('eat'); 
        }
    });

    frame++;
    draw();
    scoreBoard.innerHTML = `Score: ${Math.floor(mantis.score)} | ❤️: ${lives}`;
    requestAnimationFrame(update);
}

// 4. Render 
function draw() {
    if (currentBgImg.src && currentBgImg.src.startsWith("data:image")) {
        ctx.drawImage(currentBgImg, bgX, 0, canvas.width, canvas.height);
        ctx.drawImage(currentBgImg, bgX + canvas.width, 0, canvas.width, canvas.height);
    } else {
        ctx.fillStyle = "#87CEEB";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    obstacles.forEach(obs => {
        if (obs.y === 0) {
            ctx.fillStyle = "#5d4037"; 
            ctx.fillRect(obs.x + 10, obs.y, obs.w - 20, obs.h - 20);
            
            ctx.fillStyle = "#2e7d32"; 
            ctx.beginPath();
            ctx.arc(obs.x + obs.w/2, obs.y + obs.h - 20, 22, 0, Math.PI * 2); 
            ctx.arc(obs.x + 5, obs.y + obs.h - 35, 16, 0, Math.PI * 2);       
            ctx.arc(obs.x + obs.w - 5, obs.y + obs.h - 35, 16, 0, Math.PI * 2); 
            ctx.fill();

            ctx.fillStyle = "#4caf50"; 
            ctx.beginPath();
            ctx.arc(obs.x + obs.w/2 - 6, obs.y + obs.h - 24, 10, 0, Math.PI * 2); 
            ctx.fill();
        } else {
            ctx.fillStyle = "#1b5e20"; 
            ctx.fillRect(obs.x, obs.y + 18, obs.w, obs.h - 18);
            
            ctx.fillStyle = "#4caf50"; 
            ctx.beginPath();
            ctx.moveTo(obs.x, obs.y + 20); 
            
            let blades = 3; 
            let bladeWidth = obs.w / blades;
            for (let i = 0; i < blades; i++) {
                let peakOffset = i % 2 === 0 ? 0 : 6;
                ctx.lineTo(obs.x + (i * bladeWidth) + (bladeWidth * 0.4), obs.y + peakOffset); 
                ctx.lineTo(obs.x + ((i + 1) * bladeWidth), obs.y + 20);
            }
            ctx.fill();
        }
    });

    ctx.font = "20px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    
    // Draw Flies
    food.forEach(f => {
        ctx.fillText("🪰", f.x + f.width/2, f.y + f.height/2);
    });

    // Draw Hearts
    hearts.forEach(h => {
        ctx.fillText("❤️", h.x + h.width/2, h.y + h.height/2);
    });

    ctx.save();
    ctx.translate(mantis.x + mantis.width / 2, mantis.y + mantis.height / 2);
    
    let rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (mantis.velocity * 0.1)));
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
    ctx.fillText("APEX GLIDER", canvas.width / 2, canvas.height / 2 - 50);
    
    ctx.font = "18px 'Segoe UI', sans-serif";
    ctx.fillText("Tap to fly!", canvas.width / 2, canvas.height / 2 - 10);
    
    ctx.font = "13px 'Segoe UI', sans-serif";
    ctx.fillStyle = "#e0e0e0"; 
    ctx.fillText("Help Bok fly from Oxford to Bangalore!", canvas.width / 2, canvas.height / 2 + 25);
    ctx.fillText("Glide through the gaps in the obstacles.", canvas.width / 2, canvas.height / 2 + 45);
}

function drawMilestoneScreen() {
    draw();
    ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#4caf50"; 
    ctx.textAlign = "center";
    
    ctx.font = "bold 24px 'Segoe UI', sans-serif";
    ctx.fillText("30% of the journey", canvas.width / 2, canvas.height / 2 - 25);
    ctx.fillText("is complete!", canvas.width / 2, canvas.height / 2 + 5);
    
    ctx.font = "16px 'Segoe UI', sans-serif";
    ctx.fillStyle = "#ffffff";
    ctx.fillText(`Triple tap to continue! (${specialTapCount}/3)`, canvas.width / 2, canvas.height / 2 + 50);
}

function drawPauseScreen() {
    draw();
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    
    let msg = collisionMessages[(collisionCount - 1) % collisionMessages.length];
    
    ctx.font = "bold 18px 'Segoe UI', sans-serif";
    ctx.fillText(msg, canvas.width / 2, canvas.height / 2 - 20);
    
    ctx.font = "22px 'Segoe UI', sans-serif";
    ctx.fillText(`Lives Remaining: ${lives}`, canvas.width / 2, canvas.height / 2 + 15);
    
    ctx.font = "14px 'Segoe UI', sans-serif";
    ctx.fillStyle = "#e0e0e0";
    ctx.fillText("Tap to continue flight...", canvas.width / 2, canvas.height / 2 + 55);
}

function drawVictoryScreen() {
    draw();
    ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.textAlign = "center";
    
    ctx.fillStyle = "#FFD700"; // Gold
    ctx.font = "bold 32px 'Segoe UI', sans-serif";
    ctx.fillText("Touchdown!", canvas.width / 2, canvas.height / 2 - 50);
    
    ctx.fillStyle = "#ffffff";
    ctx.font = "16px 'Segoe UI', sans-serif";
    ctx.fillText("Bok has successfully completed", canvas.width / 2, canvas.height / 2 - 5);
    ctx.fillText("his epic quest to VJ!", canvas.width / 2, canvas.height / 2 + 20);
    
    ctx.fillStyle = "#FFD700"; // Gold
    ctx.font = "bold 28px 'Segoe UI', sans-serif";
    ctx.fillText("Victory!", canvas.width / 2, canvas.height / 2 + 70);
    
    ctx.fillStyle = "#a0a0a0";
    ctx.font = "14px 'Segoe UI', sans-serif";
    ctx.fillText(`Triple tap to play again! (${specialTapCount}/3)`, canvas.width / 2, canvas.height / 2 + 120);
}

function endGame() {
    gameState = "GAMEOVER";
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    
    let msg = gameOverMessages[deathCount % gameOverMessages.length];
    
    ctx.font = "bold 20px 'Segoe UI', sans-serif"; 
    ctx.textAlign = "center";
    ctx.fillText(msg.main, canvas.width / 2, canvas.height / 2 - 15);
    
    ctx.font = "14px 'Segoe UI', sans-serif";
    ctx.fillText(msg.sub, canvas.width / 2, canvas.height / 2 + 20);
    
    deathCount++;
}

setTimeout(update, 100);
</script>
"""

game_html = game_html.replace("BACKGROUND_IMAGE_DATA", bg_img_data)
game_html = game_html.replace("MANTIS_IMAGE_DATA", mantis_img_data)
game_html = game_html.replace("BANGLORE_IMAGE_DATA", banglore_img_data)

components.html(game_html, height=580)
