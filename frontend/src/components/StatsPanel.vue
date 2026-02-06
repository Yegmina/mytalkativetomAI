<script setup lang="ts">
import type { Profile } from "../api/client";

const props = defineProps<{
  profile: Profile | null;
}>();

const stats = [
  { key: "hunger", label: "Hunger", color: "#ffb347" },
  { key: "energy", label: "Energy", color: "#79c2ff" },
  { key: "hygiene", label: "Hygiene", color: "#76e8a7" },
  { key: "fun", label: "Fun", color: "#c9a7ff" },
  { key: "mood", label: "Mood", color: "#ffd36b" },
] as const;

function valueFor(key: string): number {
  const profile = props.profile as Profile | null;
  if (!profile) return 0;
  return Math.round((profile as any)[key] ?? 0);
}
</script>

<template>
  <div class="panel">
    <div class="panel-title">Stats</div>
    <div class="stack">
      <div v-for="stat in stats" :key="stat.key" class="row">
        <div style="width: 80px">{{ stat.label }}</div>
        <div class="stat-bar" style="flex: 1">
          <div :style="{ width: `${valueFor(stat.key)}%`, background: stat.color }" />
        </div>
        <div style="width: 40px; text-align: right">
          {{ valueFor(stat.key) }}
        </div>
      </div>
    </div>
  </div>
</template>
