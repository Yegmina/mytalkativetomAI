<script setup lang="ts">
const emit = defineEmits<{
  (event: "action", action: string): void;
}>();

const actions = [
  {
    id: "feed",
    label: "Feed",
    icon: "/assets/kit/kit_face_thanks.png",
  },
  {
    id: "sleep",
    label: "Sleep",
    icon: "/assets/kit/kit_face_phew.png",
  },
  {
    id: "clean",
    label: "Clean",
    icon: "/assets/kit/kit_face_facepalm.png",
  },
  {
    id: "play",
    label: "Play",
    icon: "/assets/kit/kit_face_gg.png",
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
