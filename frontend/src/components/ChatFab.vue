<script setup lang="ts">
const emit = defineEmits<{
  (event: "toggle"): void;
}>();
</script>

<template>
  <button class="chat-fab" @click="emit('toggle')">Chat</button>
</template>

<style scoped>
.chat-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 50;
  padding: 14px 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ffb347, #79c2ff);
  color: #0b0e1e;
  font-weight: 700;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
}
</style>
