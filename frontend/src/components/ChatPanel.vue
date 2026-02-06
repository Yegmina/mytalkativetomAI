<script setup lang="ts">
import { ref } from "vue";
import type { ChatResult, ChatMessage } from "../api/client";

const props = defineProps<{
  messages: (ChatMessage & { at: number })[];
  pending: boolean;
  error: string | null;
  lastResult: ChatResult | null;
}>();

const emit = defineEmits<{
  (event: "send", message: string): void;
  (event: "close"): void;
}>();

const input = ref("");

function submit() {
  emit("send", input.value);
  input.value = "";
}
</script>

<template>
  <div class="chat-panel">
    <div class="chat-header">
      <div class="chat-title">Chat with Kit</div>
      <button class="chat-close" @click="emit('close')">×</button>
    </div>
    <div class="chat-mood" v-if="lastResult">
      Mood: {{ lastResult.mood }} · Action: {{ lastResult.action }}
    </div>
    <div class="chat-body">
      <div
        v-for="msg in messages"
        :key="msg.at"
        class="chat-msg"
        :class="`role-${msg.role}`"
      >
        <span>{{ msg.content }}</span>
      </div>
      <div v-if="pending" class="chat-msg role-assistant">
        <span>…</span>
      </div>
    </div>
    <div class="chat-error" v-if="error">{{ error }}</div>
    <div class="chat-input">
      <input
        v-model="input"
        type="text"
        placeholder="Say something…"
        @keydown.enter="submit"
      />
      <button class="cta" :disabled="pending" @click="submit">Send</button>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  position: fixed;
  bottom: 90px;
  right: 24px;
  width: 320px;
  background: rgba(17, 21, 44, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  z-index: 60;
  display: grid;
  gap: 10px;
  padding: 12px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title {
  font-weight: 700;
}

.chat-close {
  background: transparent;
  color: inherit;
  font-size: 20px;
}

.chat-mood {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.chat-body {
  max-height: 220px;
  overflow-y: auto;
  display: grid;
  gap: 8px;
  padding-right: 4px;
}

.chat-msg {
  padding: 8px 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  font-size: 13px;
}

.role-user {
  background: rgba(121, 194, 255, 0.18);
  justify-self: end;
}

.role-assistant {
  background: rgba(255, 179, 71, 0.18);
}

.chat-error {
  color: #ff8b8b;
  font-size: 12px;
}

.chat-input {
  display: flex;
  gap: 8px;
}

.chat-input input {
  flex: 1;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(9, 12, 26, 0.8);
  color: inherit;
}
</style>
