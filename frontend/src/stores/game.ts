import { defineStore } from "pinia";
import {
  buyItem,
  equipItem,
  getProfile,
  getShop,
  performAction,
  requestActionFeedback,
  requestReminder,
  sendChat,
  synthesizeSoundEffect,
  synthesizeSpeech,
  submitMinigame,
  type ChatMessage,
  type ChatResult,
  type Profile,
  type ShopItem,
} from "../api/client";

type ChatHistoryItem = ChatMessage & { at: number };

let moodTimer: number | undefined;
let animationTimer: number | undefined;
let ttsAudio: HTMLAudioElement | null = null;
let ttsUrl: string | null = null;
let sfxAudio: HTMLAudioElement | null = null;
let sfxUrl: string | null = null;
let playbackToken = 0;
let reminderTimer: number | undefined;
let reminderInFlight = false;
let lastReminderAt = 0;

const REMINDER_MIN_MS = 20000;
const REMINDER_MAX_MS = 50000;
const HUNGER_LOW = 30;
const LOW_STAT = 30;
const ANIMATION_DURATION_MS = 6000;

const ACTION_ANIMATIONS: Record<
  "feed" | "sleep" | "clean" | "play",
  string
> = {
  feed: "eat.webm",
  sleep: "chilling_cat.webm",
  clean: "clean.webm",
  play: "dancing.webm",
};

function randomBetween(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function needsAttention(profile: Profile | null) {
  if (!profile) return false;
  return (
    profile.hunger <= HUNGER_LOW ||
    profile.energy <= LOW_STAT ||
    profile.hygiene <= LOW_STAT ||
    profile.fun <= LOW_STAT ||
    profile.mood <= LOW_STAT
  );
}

function stopAudioPlayback() {
  if (ttsAudio) {
    ttsAudio.pause();
    ttsAudio = null;
  }
  if (sfxAudio) {
    sfxAudio.pause();
    sfxAudio = null;
  }
  if (ttsUrl) {
    URL.revokeObjectURL(ttsUrl);
    ttsUrl = null;
  }
  if (sfxUrl) {
    URL.revokeObjectURL(sfxUrl);
    sfxUrl = null;
  }
}

function playAndWait(audio: HTMLAudioElement): Promise<void> {
  return new Promise((resolve) => {
    const finish = () => {
      audio.onended = null;
      audio.onerror = null;
      resolve();
    };
    audio.onended = finish;
    audio.onerror = finish;
    audio.play().catch(finish);
  });
}

async function playTtsWithSfx(text: string, sfxPrompt?: string | null) {
  if (!text.trim()) return;
  const requestToken = ++playbackToken;
  const trimmedPrompt = sfxPrompt?.trim();
  try {
    const [ttsBlob, sfxBlob] = await Promise.all([
      synthesizeSpeech(text),
      trimmedPrompt ? synthesizeSoundEffect(trimmedPrompt) : Promise.resolve(null),
    ]);
    if (requestToken !== playbackToken) return;
    stopAudioPlayback();
    ttsUrl = URL.createObjectURL(ttsBlob);
    ttsAudio = new Audio(ttsUrl);
    await playAndWait(ttsAudio);
    if (!sfxBlob || requestToken !== playbackToken) return;
    sfxUrl = URL.createObjectURL(sfxBlob);
    sfxAudio = new Audio(sfxUrl);
    await playAndWait(sfxAudio);
  } catch (error) {
    console.warn("TTS/SFX playback failed", error);
  }
}

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
    animationOverride: null as { animation: string; until: number } | null,
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
    async action(action: "feed" | "sleep" | "clean" | "play") {
      if (!this.profile) {
        await this.loadProfile();
      }
      try {
        const response = await performAction(action);
        this.profile = response.profile;
        const animation = ACTION_ANIMATIONS[action];
        if (animation) {
          this.animationOverride = {
            animation,
            until: Date.now() + ANIMATION_DURATION_MS,
          };
          if (animationTimer) {
            window.clearTimeout(animationTimer);
          }
          animationTimer = window.setTimeout(() => {
            this.animationOverride = null;
          }, ANIMATION_DURATION_MS);
        }
        void this.playActionFeedback(action);
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Action failed";
      }
    },
    async playActionFeedback(action: "feed" | "sleep" | "clean" | "play") {
      try {
        const response = await requestActionFeedback(action);
        void playTtsWithSfx(
          response.response.reply,
          response.response.sfx_prompt
        );
      } catch (error) {
        console.warn("Action feedback failed", error);
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
        if (response.response.animation) {
          this.animationOverride = {
            animation: response.response.animation,
            until: Date.now() + 6000,
          };
          if (animationTimer) {
            window.clearTimeout(animationTimer);
          }
          animationTimer = window.setTimeout(() => {
            this.animationOverride = null;
          }, 6000);
        } else {
          this.animationOverride = null;
        }
        const assistantMessage: ChatHistoryItem = {
          role: "assistant",
          content: response.response.reply,
          at: Date.now(),
        };
        this.chatMessages.push(assistantMessage);
        void playTtsWithSfx(
          response.response.reply,
          response.response.sfx_prompt
        );
      } catch (error) {
        this.chatError =
          error instanceof Error ? error.message : "Chat failed";
      } finally {
        this.chatPending = false;
      }
    },
    async maybeSendReminder() {
      if (reminderInFlight || this.chatPending) return;
      if (!needsAttention(this.profile)) return;
      const now = Date.now();
      if (now - lastReminderAt < REMINDER_MIN_MS) return;
      reminderInFlight = true;
      try {
        const response = await requestReminder();
        lastReminderAt = Date.now();
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
        if (response.response.animation) {
          this.animationOverride = {
            animation: response.response.animation,
            until: Date.now() + 6000,
          };
          if (animationTimer) {
            window.clearTimeout(animationTimer);
          }
          animationTimer = window.setTimeout(() => {
            this.animationOverride = null;
          }, 6000);
        } else {
          this.animationOverride = null;
        }
        if (response.response.reply?.trim()) {
          const assistantMessage: ChatHistoryItem = {
            role: "assistant",
            content: response.response.reply,
            at: Date.now(),
          };
          this.chatMessages.push(assistantMessage);
          void playTtsWithSfx(
            response.response.reply,
            response.response.sfx_prompt
          );
        }
      } catch (error) {
        console.warn("Reminder failed", error);
      } finally {
        reminderInFlight = false;
      }
    },
    startReminderLoop() {
      if (reminderTimer) return;
      const schedule = () => {
        const delay = randomBetween(REMINDER_MIN_MS, REMINDER_MAX_MS);
        reminderTimer = window.setTimeout(async () => {
          await this.maybeSendReminder();
          schedule();
        }, delay);
      };
      schedule();
    },
    stopReminderLoop() {
      if (reminderTimer) {
        window.clearTimeout(reminderTimer);
        reminderTimer = undefined;
      }
      reminderInFlight = false;
    },
  },
});
