<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useGameStore } from "./stores/game";
import PetScene from "./components/PetScene.vue";
import HudBar from "./components/HudBar.vue";
import ActionPanel from "./components/ActionPanel.vue";
import ShopPanel from "./components/ShopPanel.vue";
import MiniGameCatch from "./components/MiniGameCatch.vue";
import StatsPanel from "./components/StatsPanel.vue";
import ChatFab from "./components/ChatFab.vue";
import ChatPanel from "./components/ChatPanel.vue";

const store = useGameStore();
const view = ref<"care" | "shop" | "play">("care");
const lastAction = ref<{ type: string; at: number } | null>(null);
const chatOpen = ref(false);
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

async function handleAction(action: string) {
  lastAction.value = { type: action, at: Date.now() };
  await store.action(action);
}

watch(
  () => store.chatResult,
  (result) => {
    if (result && result.action !== "none") {
      lastAction.value = { type: result.action, at: Date.now() };
    }
  }
);
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
        <PetScene
          :profile="store.profile"
          :shop-items="store.shopItems"
          :last-action="lastAction"
          :mood-override="store.moodOverride?.mood ?? null"
          :animation-override="store.animationOverride?.animation ?? null"
        />
        <HudBar :profile="store.profile" />
      </section>

      <section class="stack">
        <StatsPanel :profile="store.profile" />
        <ActionPanel @action="handleAction" />
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
    <ChatPanel
      v-if="chatOpen"
      :messages="store.chatMessages"
      :pending="store.chatPending"
      :error="store.chatError"
      :last-result="store.chatResult"
      @send="store.sendChatMessage"
      @close="chatOpen = false"
    />
    <ChatFab @toggle="chatOpen = !chatOpen" />
  </div>
</template>
