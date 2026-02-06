<script setup lang="ts">
import { computed } from "vue";
import type { Profile, ShopItem } from "../api/client";

const props = defineProps<{
  profile: Profile | null;
  shopItems: ShopItem[];
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

const moodLevel = computed(() => props.profile?.mood ?? 0);
const energyLevel = computed(() => props.profile?.energy ?? 0);

const petImage = computed(() => {
  if (energyLevel.value < 25) {
    return "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f634.png";
  }
  if (moodLevel.value < 35) {
    return "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f63f.png";
  }
  if (moodLevel.value > 80) {
    return "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f63a.png";
  }
  return "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f431.png";
});

const alerts = computed(() => {
  if (!props.profile) return [];
  const alertsList = [];
  if (props.profile.hunger < 30) {
    alertsList.push({
      id: "hunger",
      icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f41f.png",
    });
  }
  if (props.profile.energy < 30) {
    alertsList.push({
      id: "energy",
      icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4a4.png",
    });
  }
  if (props.profile.hygiene < 30) {
    alertsList.push({
      id: "hygiene",
      icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9fc.png",
    });
  }
  if (props.profile.fun < 30) {
    alertsList.push({
      id: "fun",
      icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/26bd.png",
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
      <div class="pet-wrap">
        <img :src="petImage" alt="Pet" class="pet" />
        <img v-if="equippedHat" :src="equippedHat" alt="Hat" class="hat" />
        <div class="alerts">
          <img v-for="alert in alerts" :key="alert.id" :src="alert.icon" />
        </div>
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
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.25), rgba(0, 0, 0, 0));
  animation: float 3s ease-in-out infinite;
}

.pet {
  width: 120px;
  height: 120px;
}

.hat {
  position: absolute;
  top: 10px;
  width: 70px;
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
</style>
