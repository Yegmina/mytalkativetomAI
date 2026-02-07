<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import type { Profile, ShopItem } from "../api/client";

const props = defineProps<{
  profile: Profile | null;
  shopItems: ShopItem[];
  lastAction?: { type: string; at: number } | null;
  moodOverride?: "happy" | "neutral" | "sad" | "angry" | "tired" | null;
  animationOverride?: string | null;
}>();

const itemMap = computed(() => {
  const map: Record<string, ShopItem> = {};
  for (const item of props.shopItems) {
    map[item.id] = item;
  }
  return map;
});

const equippedBackground = computed(() => {
  const id = props.profile?.equipped_items?.background;
  return id ? itemMap.value[id]?.asset_url : null;
});

const equippedHat = computed(() => {
  const id = props.profile?.equipped_items?.hat;
  return id ? itemMap.value[id]?.asset_url : null;
});

const moodOverrideValue = computed(() => {
  switch (props.moodOverride) {
    case "happy":
      return 90;
    case "neutral":
      return 60;
    case "sad":
      return 35;
    case "angry":
      return 15;
    case "tired":
      return 25;
    default:
      return null;
  }
});

const moodLevel = computed(() => moodOverrideValue.value ?? props.profile?.mood ?? 0);
const energyLevel = computed(() => props.profile?.energy ?? 0);

const asset = (file: string) => `/assets/kit/${file}`;
const apiBase =
  import.meta.env.VITE_API_BASE?.toString() || "http://localhost:8000";

const bodyImage = computed(() => {
  if (energyLevel.value < 25) {
    return asset("kit_body_tired.png");
  }
  if (moodLevel.value < 20) {
    return asset("kit_body_angry.png");
  }
  if (moodLevel.value < 40) {
    return asset("kit_body_sad.png");
  }
  if (moodLevel.value > 80) {
    return asset("kit_body_happy.png");
  }
  return asset("kit_body_neutral.png");
});

const bodyImageFallback = asset("kit_cat1.jpg");
const bodySrc = ref(asset("kit_body_neutral.png"));
watch(bodyImage, (src) => {
  bodySrc.value = src;
}, { immediate: true });
function onBodyImageError() {
  bodySrc.value = bodyImageFallback;
}

const petImage = computed(() => {
  if (energyLevel.value < 25) {
    return asset("kit_face_phew.png");
  }
  if (moodLevel.value < 20) {
    return asset("kit_face_angry.png");
  }
  if (moodLevel.value < 40) {
    return asset("kit_face_sad.png");
  }
  if (moodLevel.value > 80) {
    return asset("kit_face_happy.png");
  }
  return asset("kit_face_neutral.png");
});

const DEFAULT_IDLE_ANIMATION = "animation-Kit.webm";

const animationSrc = computed(() => {
  const filename = props.animationOverride ?? DEFAULT_IDLE_ANIMATION;
  return `${apiBase}/assets/animations_cat/${filename}`;
});

const actionOverlay = ref<{ type: string; src?: string; kind: "image" | "video" | "text" } | null>(null);
let actionTimer: number | undefined;

const actionSources: Record<
  string,
  { src?: string; kind: "image" | "video" | "text" }
> = {
  feed: { src: asset("actions/feed_hearts.gif"), kind: "image" },
  clean: { src: asset("actions/clean_bubble.png"), kind: "image" },
  play: { src: asset("kit_win.gif"), kind: "image" },
  sleep: { kind: "text" },
};

watch(
  () => props.lastAction?.at,
  () => {
    if (!props.lastAction) return;
    const type = props.lastAction.type;
    const config = actionSources[type] ?? { kind: "text" as const };
    actionOverlay.value = { type, ...config };
    if (actionTimer) {
      window.clearTimeout(actionTimer);
    }
    actionTimer = window.setTimeout(() => {
      actionOverlay.value = null;
    }, 2600);
  }
);

onUnmounted(() => {
  if (actionTimer) {
    window.clearTimeout(actionTimer);
  }
});

const alerts = computed(() => {
  if (!props.profile) return [];
  const alertsList = [];
  if (props.profile.hunger < 30) {
    alertsList.push({
      id: "hunger",
      icon: asset("kit_face_sad.png"),
    });
  }
  if (props.profile.energy < 30) {
    alertsList.push({
      id: "energy",
      icon: asset("kit_face_phew.png"),
    });
  }
  if (props.profile.hygiene < 30) {
    alertsList.push({
      id: "hygiene",
      icon: asset("kit_face_facepalm.png"),
    });
  }
  if (props.profile.fun < 30) {
    alertsList.push({
      id: "fun",
      icon: asset("kit_face_clap.png"),
    });
  }
  return alertsList;
});
</script>

<template>
  <div class="panel pet-scene">
    <div class="panel-title">Pet Scene</div>
    <div
      class="scene"
      :style="{
        backgroundImage: equippedBackground ? `url(${equippedBackground})` : undefined,
      }"
    >
      <div class="pet-wrap" :class="{ 'is-animating': !!animationSrc }">
        <transition name="pet-animation-fade" mode="out-in">
          <video
            :key="animationSrc"
            :src="animationSrc"
            class="pet-animation"
            autoplay
            loop
            muted
            playsinline
          ></video>
        </transition>
        <transition name="pet-body-fade" mode="out-in">
          <img
            :src="bodySrc"
            :key="bodyImage"
            alt="Kit body"
            class="pet-body"
            @error="onBodyImageError"
          />
        </transition>
        <transition name="pet-face-pop" mode="out-in">
          <img :src="petImage" :key="petImage" alt="Kit face" class="pet-face" />
        </transition>
        <img v-if="equippedHat" :src="equippedHat" alt="Hat" class="hat" />
        <div class="alerts">
          <img v-for="alert in alerts" :key="alert.id" :src="alert.icon" />
        </div>
        <transition name="action-fade">
          <div
            v-if="actionOverlay"
            class="action-overlay"
            :class="`action-${actionOverlay.type}`"
          >
            <img
              v-if="actionOverlay.kind === 'image'"
              :src="actionOverlay.src"
              alt="Action"
            />
            <video
              v-else-if="actionOverlay.kind === 'video'"
              :src="actionOverlay.src"
              autoplay
              loop
              muted
              playsinline
            ></video>
            <div v-else class="action-zzz">Zzz</div>
          </div>
        </transition>
      </div>
      <div class="speech">
        <span>{{ profile?.name ?? "Tom" }}</span>
        <small>mood {{ profile?.mood?.toFixed(0) ?? 0 }}%</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pet-scene {
  min-height: 340px;
}

.scene {
  position: relative;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(127, 199, 255, 0.2), rgba(20, 30, 60, 0.7));
  min-height: 260px;
  display: grid;
  place-items: center;
  overflow: hidden;
  background-size: cover;
  background-position: center;
}

.pet-wrap {
  position: relative;
  display: grid;
  place-items: center;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.25), rgba(0, 0, 0, 0));
  animation: float 3s ease-in-out infinite;
}

.pet-body {
  width: 210px;
  height: 210px;
  object-fit: contain;
  filter: drop-shadow(0 12px 20px rgba(0, 0, 0, 0.25));
}

.pet-animation {
  position: absolute;
  top: -6px;
  left: -6px;
  width: 252px;
  height: 252px;
  object-fit: contain;
  z-index: 3;
  filter: drop-shadow(0 12px 22px rgba(0, 0, 0, 0.35));
}

.pet-wrap.is-animating .pet-body {
  opacity: 0;
}

.pet-face {
  position: absolute;
  top: 8px;
  left: -105px;
  width: 120px;
  height: 120px;
  object-fit: contain;
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.25));
}

.hat {
  position: absolute;
  top: -6px;
  left: -88px;
  width: 78px;
  transform: rotate(-6deg);
}

.alerts {
  position: absolute;
  top: 0;
  right: -10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alerts img {
  width: 28px;
  height: 28px;
}

.speech {
  position: absolute;
  bottom: 18px;
  left: 18px;
  background: rgba(0, 0, 0, 0.4);
  padding: 8px 12px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.speech span {
  font-weight: 600;
}

.speech small {
  color: rgba(255, 255, 255, 0.7);
}

.pet-body-fade-enter-active,
.pet-body-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.pet-body-fade-enter-from,
.pet-body-fade-leave-to {
  opacity: 0;
  transform: scale(0.92) rotate(-2deg);
}

.pet-face-pop-enter-active,
.pet-face-pop-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.pet-face-pop-enter-from,
.pet-face-pop-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.pet-animation-fade-enter-active,
.pet-animation-fade-leave-active {
  transition: opacity 0.3s ease;
}

.pet-animation-fade-enter-from,
.pet-animation-fade-leave-to {
  opacity: 0;
}

.action-overlay {
  position: absolute;
  right: -6px;
  bottom: -8px;
  display: grid;
  place-items: center;
  width: 110px;
  height: 110px;
  pointer-events: none;
  animation: action-pop 0.3s ease;
}

.action-overlay img,
.action-overlay video {
  width: 96px;
  height: 96px;
  object-fit: contain;
}

.action-feed img {
  animation: float-up 2.6s ease;
}

.action-clean img {
  animation: bubble-pop 2.6s ease;
  opacity: 0.9;
}

.action-play img {
  width: 140px;
  height: 140px;
  animation: sparkle-spin 2.6s ease;
}

.action-sleep video {
  width: 150px;
  height: 150px;
  opacity: 0.9;
}

.action-zzz {
  font-size: 28px;
  font-weight: 700;
  color: #b8d8ff;
  text-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
  animation: zzz 1.8s ease-in-out infinite;
}

.action-fade-enter-active,
.action-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.action-fade-enter-from,
.action-fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
  100% {
    transform: translateY(0px);
  }
}

@keyframes action-pop {
  0% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes float-up {
  0% {
    transform: translateY(6px) scale(0.9);
    opacity: 0.7;
  }
  60% {
    transform: translateY(-16px) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(-28px) scale(1.05);
    opacity: 0;
  }
}

@keyframes bubble-pop {
  0% {
    transform: scale(0.85);
    opacity: 0.7;
  }
  60% {
    transform: scale(1);
    opacity: 0.95;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}

@keyframes sparkle-spin {
  0% {
    transform: scale(0.9) rotate(-6deg);
  }
  60% {
    transform: scale(1.05) rotate(4deg);
  }
  100% {
    transform: scale(1.1) rotate(0deg);
    opacity: 0;
  }
}

@keyframes zzz {
  0% {
    transform: translateY(0px);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-6px);
    opacity: 1;
  }
  100% {
    transform: translateY(0px);
    opacity: 0.6;
  }
}
</style>
