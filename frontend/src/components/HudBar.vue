<script setup lang="ts">
import type { Profile } from "../api/client";

defineProps<{
  profile: Profile | null;
}>();
</script>

<template>
  <div class="panel">
    <div class="row" style="justify-content: space-between">
      <div class="row">
        <span class="badge">Coins</span>
        <strong>{{ profile?.coins ?? 0 }}</strong>
      </div>
      <div class="row">
        <span class="badge">Level</span>
        <strong>{{ profile?.level ?? 1 }}</strong>
      </div>
      <div class="row">
        <span class="badge">XP</span>
        <strong>{{ profile?.xp ?? 0 }}</strong>
      </div>
    </div>
  </div>
</template>
