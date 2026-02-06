<script setup lang="ts">
const emit = defineEmits<{
  (event: "action", action: string): void;
}>();

const actions = [
  {
    id: "feed",
    label: "Feed",
    icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f372.png",
  },
  {
    id: "sleep",
    label: "Sleep",
    icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f634.png",
  },
  {
    id: "clean",
    label: "Clean",
    icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f9fc.png",
  },
  {
    id: "play",
    label: "Play",
    icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/26bd.png",
  },
];
</script>

<template>
  <div class="panel">
    <div class="panel-title">Care Actions</div>
    <div class="grid" style="grid-template-columns: repeat(2, 1fr)">
      <button
        v-for="action in actions"
        :key="action.id"
        class="ghost row"
        @click="emit('action', action.id)"
      >
        <img :src="action.icon" alt="" width="28" height="28" />
        <span>{{ action.label }}</span>
      </button>
    </div>
  </div>
</template>
