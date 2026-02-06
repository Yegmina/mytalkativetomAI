<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useGameStore } from "./stores/game";
import PetScene from "./components/PetScene.vue";
import HudBar from "./components/HudBar.vue";
import ActionPanel from "./components/ActionPanel.vue";
import ShopPanel from "./components/ShopPanel.vue";
import MiniGameCatch from "./components/MiniGameCatch.vue";
import StatsPanel from "./components/StatsPanel.vue";

const store = useGameStore();
const view = ref<"care" | "shop" | "play">("care");
let refreshTimer: number | undefined;

onMounted(async () => {
  await store.loadProfile();
  await store.loadShop();
  refreshTimer = window.setInterval(() => {
    store.loadProfile();
  }, 15000);
});

onUnmounted(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer);
  }
});
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="brand">
        Talking <span>Tom</span> Hackathon
      </div>
      <nav class="nav">
        <button
          :class="{ active: view === 'care' }"
          @click="view = 'care'"
        >
          Care
        </button>
        <button
          :class="{ active: view === 'shop' }"
          @click="view = 'shop'"
        >
          Shop
        </button>
        <button
          :class="{ active: view === 'play' }"
          @click="view = 'play'"
        >
          Play
        </button>
      </nav>
    </header>

    <main class="main">
      <section class="stack">
        <PetScene :profile="store.profile" :shop-items="store.shopItems" />
        <HudBar :profile="store.profile" />
      </section>

      <section class="stack">
        <StatsPanel :profile="store.profile" />
        <ActionPanel @action="store.action" />
        <ShopPanel
          v-if="view === 'shop'"
          :items="store.shopItems"
          :profile="store.profile"
          @buy="store.buy"
          @equip="store.equip"
        />
        <MiniGameCatch v-if="view === 'play'" />
        <div v-if="store.error" class="panel">
          <div class="panel-title">Status</div>
          <p class="muted">{{ store.error }}</p>
        </div>
      </section>
    </main>
  </div>
</template>
