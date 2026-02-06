<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useGameStore } from "../stores/game";

const store = useGameStore();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const running = ref(false);
const score = ref(0);
const timeLeft = ref(30);
const status = ref("Catch as many coins as you can!");

const width = 520;
const height = 300;
const basketWidth = 90;
const basketHeight = 18;
const coinRadius = 10;
const spawnInterval = 0.7;
const gameDuration = 30;

let basketX = width / 2 - basketWidth / 2;
let coins: { x: number; y: number; speed: number }[] = [];
let lastTime = 0;
let spawnTimer = 0;
let animationId = 0;
let startTime = 0;

function resetGame() {
  basketX = width / 2 - basketWidth / 2;
  coins = [];
  score.value = 0;
  timeLeft.value = gameDuration;
  status.value = "Catch as many coins as you can!";
}

function startGame() {
  if (running.value) return;
  resetGame();
  running.value = true;
  startTime = performance.now();
  lastTime = startTime;
  spawnTimer = 0;
  animationId = requestAnimationFrame(loop);
}

function endGame() {
  running.value = false;
  cancelAnimationFrame(animationId);
  const durationMs = Math.round(performance.now() - startTime);
  status.value = `Nice! You caught ${score.value} coins.`;
  store.submitMinigame(score.value, durationMs);
}

function spawnCoin() {
  coins.push({
    x: Math.random() * (width - coinRadius * 2) + coinRadius,
    y: -coinRadius,
    speed: 80 + Math.random() * 80,
  });
}

function update(delta: number) {
  spawnTimer += delta;
  if (spawnTimer >= spawnInterval) {
    spawnTimer = 0;
    spawnCoin();
  }

  coins = coins
    .map((coin) => ({ ...coin, y: coin.y + coin.speed * delta }))
    .filter((coin) => coin.y < height + coinRadius);

  const basketTop = height - basketHeight - 16;
  const basketLeft = basketX;
  const basketRight = basketX + basketWidth;

  coins = coins.filter((coin) => {
    const hitY = coin.y + coinRadius >= basketTop;
    const hitX = coin.x >= basketLeft && coin.x <= basketRight;
    if (hitX && hitY) {
      score.value += 1;
      return false;
    }
    return true;
  });

  const elapsed = (performance.now() - startTime) / 1000;
  timeLeft.value = Math.max(0, Math.ceil(gameDuration - elapsed));
  if (timeLeft.value <= 0) {
    endGame();
  }
}

function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "rgba(255,255,255,0.08)";
  ctx.fillRect(0, 0, width, height);

  ctx.fillStyle = "#ffda79";
  for (const coin of coins) {
    ctx.beginPath();
    ctx.arc(coin.x, coin.y, coinRadius, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.fillStyle = "#79c2ff";
  ctx.fillRect(basketX, height - basketHeight - 16, basketWidth, basketHeight);
  ctx.fillStyle = "#0b0e1e";
  ctx.fillRect(basketX + 8, height - basketHeight - 10, basketWidth - 16, 6);
}

function loop(time: number) {
  const delta = (time - lastTime) / 1000;
  lastTime = time;
  update(delta);
  draw();
  if (running.value) {
    animationId = requestAnimationFrame(loop);
  }
}

function setBasketFromClientX(clientX: number) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const relativeX = clientX - rect.left;
  basketX = Math.min(width - basketWidth, Math.max(0, relativeX - basketWidth / 2));
}

function onMouseMove(event: MouseEvent) {
  if (!running.value) return;
  setBasketFromClientX(event.clientX);
}

function onKeyDown(event: KeyboardEvent) {
  if (!running.value) return;
  if (event.key === "ArrowLeft") {
    basketX = Math.max(0, basketX - 24);
  }
  if (event.key === "ArrowRight") {
    basketX = Math.min(width - basketWidth, basketX + 24);
  }
}

onMounted(() => {
  const canvas = canvasRef.value;
  if (canvas) {
    canvas.width = width;
    canvas.height = height;
  }
  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("keydown", onKeyDown);
});

onUnmounted(() => {
  window.removeEventListener("mousemove", onMouseMove);
  window.removeEventListener("keydown", onKeyDown);
  cancelAnimationFrame(animationId);
});
</script>

<template>
  <div class="panel mini-game">
    <div class="panel-title">Mini-Game: Coin Catch</div>
    <canvas ref="canvasRef"></canvas>
    <div class="row" style="justify-content: space-between">
      <span class="badge">Score {{ score }}</span>
      <span class="badge">Time {{ timeLeft }}s</span>
    </div>
    <p class="muted">{{ status }}</p>
    <button class="cta" @click="startGame">Start</button>
  </div>
</template>
