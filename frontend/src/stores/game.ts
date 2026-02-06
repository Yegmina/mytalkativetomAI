import { defineStore } from "pinia";
import {
  buyItem,
  equipItem,
  getProfile,
  getShop,
  performAction,
  submitMinigame,
  type Profile,
  type ShopItem,
} from "../api/client";

export const useGameStore = defineStore("game", {
  state: () => ({
    profile: null as Profile | null,
    shopItems: [] as ShopItem[],
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async loadProfile() {
      this.loading = true;
      this.error = null;
      try {
        this.profile = await getProfile();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Load failed";
      } finally {
        this.loading = false;
      }
    },
    async loadShop() {
      try {
        const response = await getShop();
        this.shopItems = response.items;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Shop failed";
      }
    },
    async action(action: string) {
      if (!this.profile) {
        await this.loadProfile();
      }
      try {
        const response = await performAction(action);
        this.profile = response.profile;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Action failed";
      }
    },
    async buy(itemId: string) {
      try {
        const response = await buyItem(itemId);
        this.profile = response.profile;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Purchase failed";
      }
    },
    async equip(itemId: string) {
      try {
        const response = await equipItem(itemId);
        this.profile = response.profile;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Equip failed";
      }
    },
    async submitMinigame(score: number, durationMs: number) {
      try {
        const response = await submitMinigame(score, durationMs);
        this.profile = response.profile;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Mini-game failed";
      }
    },
  },
});
