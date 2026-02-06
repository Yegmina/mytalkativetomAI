<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useGameStore } from "../stores/game";

const store = useGameStore();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const running = ref(false);
const score = ref(0);
const timeLeft = ref(30);
const status = ref("Catch as many coins as you can!");
const result = ref<"win" | "lose" | null>(null);
const showResult = ref(false);

const width = 520;
const height = 300;
const basketWidth = 90;
const basketHeight = 18;
const coinRadius = 10;
const spawnInterval = 0.7;
const gameDuration = 30;
const winThreshold = 10;
const winSrc = "/assets/kit/kit_win.gif";
const loseSrc = "/assets/kit/kit_lose.mp4";

let basketX = width / 2 - basketWidth / 2;
let coins: { x: number; y: number; speed: number }[] = [];
let lastTime = 0;
let spawnTimer = 0;
let animationId = 0;
let startTime = 0;
let resultTimer: number | undefined;

function resetGame() {
  basketX = width / 2 - basketWidth / 2;
  coins = [];
  score.value = 0;
  timeLeft.value = gameDuration;
  status.value = "Catch as many coins as you can!";
  result.value = null;
  showResult.value = false;
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
  result.value = score.value >= winThreshold ? "win" : "lose";
  showResult.value = true;
  if (resultTimer) {
    window.clearTimeout(resultTimer);
  }
  resultTimer = window.setTimeout(() => {
    showResult.value = false;
  }, 4000);
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
  if (resultTimer) {
    window.clearTimeout(resultTimer);
  }
});
</script>

<template>
  <div class="panel mini-game">
    <div class="panel-title">Mini-Game: Coin Catch</div>
    <div class="mini-game-stage">
      <canvas ref="canvasRef"></canvas>
      <transition name="result-fade">
        <div v-if="showResult && result" class="result-overlay">
          <img v-if="result === 'win'" :src="winSrc" alt="Kit wins" />
          <video
            v-else
            :src="loseSrc"
            autoplay
            loop
            muted
            playsinline
          ></video>
          <div class="result-label">
            {{ result === "win" ? "Kit wins!" : "Try again!" }}
          </div>
        </div>
      </transition>
    </div>
    <div class="row" style="justify-content: space-between">
      <span class="badge">Score {{ score }}</span>
      <span class="badge">Time {{ timeLeft }}s</span>
    </div>
    <p class="muted">{{ status }}</p>
    <button class="cta" @click="startGame" :disabled="running">
      {{ running ? "Running..." : "Start" }}
    </button>
  </div>
</template>

<style scoped>
.mini-game-stage {
  position: relative;
}

.result-overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  gap: 8px;
  background: rgba(8, 12, 28, 0.65);
  border-radius: 16px;
  text-align: center;
}

.result-overlay img,
.result-overlay video {
  width: 180px;
  height: 180px;
  object-fit: contain;
  filter: drop-shadow(0 12px 20px rgba(0, 0, 0, 0.35));
}

.result-label {
  font-weight: 600;
  letter-spacing: 0.5px;
}

.result-fade-enter-active,
.result-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.result-fade-enter-from,
.result-fade-leave-to {
  opacity: 0;
  transform: scale(0.96);
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
