<script setup lang="ts">
import type { Profile, ShopItem } from "../api/client";

const props = defineProps<{
  items: ShopItem[];
  profile: Profile | null;
}>();

const emit = defineEmits<{
  (event: "buy", itemId: string): void;
  (event: "equip", itemId: string): void;
}>();

function isOwned(itemId: string) {
  return props.profile?.owned_items?.includes(itemId) ?? false;
}

function isEquipped(item: ShopItem) {
  const equipped = props.profile?.equipped_items?.[item.type];
  return equipped === item.id;
}
</script>

<template>
  <div class="panel">
    <div class="panel-title">Shop & Customization</div>
    <div class="grid shop-grid">
      <div v-for="item in items" :key="item.id" class="card">
        <img :src="item.icon_url" :alt="item.name" />
        <strong>{{ item.name }}</strong>
        <span class="muted">{{ item.description }}</span>
        <div class="row" style="justify-content: space-between">
          <span class="pill">{{ item.type }}</span>
          <span class="pill">{{ item.price }} coins</span>
        </div>
        <button
          v-if="!isOwned(item.id)"
          class="cta"
          @click="emit('buy', item.id)"
        >
          Buy
        </button>
        <button
          v-else-if="!isEquipped(item)"
          class="ghost"
          @click="emit('equip', item.id)"
        >
          Equip
        </button>
        <span v-else class="badge">Equipped</span>
      </div>
    </div>
  </div>
</template>
