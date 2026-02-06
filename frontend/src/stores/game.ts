import { defineStore } from "pinia";
import {
  buyItem,
  equipItem,
  getProfile,
  getShop,
  performAction,
  sendChat,
  submitMinigame,
  type ChatMessage,
  type ChatResult,
  type Profile,
  type ShopItem,
} from "../api/client";

type ChatHistoryItem = ChatMessage & { at: number };

let moodTimer: number | undefined;

export const useGameStore = defineStore("game", {
  state: () => ({
    profile: null as Profile | null,
    shopItems: [] as ShopItem[],
    loading: false,
    error: null as string | null,
    chatMessages: [] as ChatHistoryItem[],
    chatPending: false,
    chatError: null as string | null,
    chatResult: null as ChatResult | null,
    moodOverride: null as { mood: ChatResult["mood"]; until: number } | null,
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
    async sendChatMessage(content: string) {
      const trimmed = content.trim();
      if (!trimmed) return;
      const userMessage: ChatHistoryItem = {
        role: "user",
        content: trimmed,
        at: Date.now(),
      };
      this.chatMessages.push(userMessage);
      this.chatPending = true;
      this.chatError = null;
      try {
        const apiMessages = this.chatMessages.slice(-12).map((msg) => ({
          role: msg.role,
          content: msg.content,
        }));
        const response = await sendChat(apiMessages);
        this.profile = response.profile;
        this.chatResult = response.response;
        this.moodOverride = {
          mood: response.response.mood,
          until: Date.now() + 6000,
        };
        if (moodTimer) {
          window.clearTimeout(moodTimer);
        }
        moodTimer = window.setTimeout(() => {
          this.moodOverride = null;
        }, 6000);
        const assistantMessage: ChatHistoryItem = {
          role: "assistant",
          content: response.response.reply,
          at: Date.now(),
        };
        this.chatMessages.push(assistantMessage);
      } catch (error) {
        this.chatError =
          error instanceof Error ? error.message : "Chat failed";
      } finally {
        this.chatPending = false;
      }
    },
  },
});
