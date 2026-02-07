const API_BASE =
  import.meta.env.VITE_API_BASE?.toString() || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  return (await response.json()) as T;
}

async function requestBlob(path: string, options: RequestInit = {}): Promise<Blob> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  return await response.blob();
}

export interface Profile {
  id: number;
  name: string;
  coins: number;
  level: number;
  xp: number;
  hunger: number;
  energy: number;
  hygiene: number;
  fun: number;
  mood: number;
  last_updated: string;
  owned_items: string[];
  equipped_items: Record<string, string>;
}

export interface ShopItem {
  id: string;
  name: string;
  type: string;
  price: number;
  asset_url: string;
  icon_url: string;
  description: string;
}

export type ChatRole = "system" | "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface ChatEquip {
  hat_id?: string | null;
  background_id?: string | null;
}

export interface ChatResult {
  reply: string;
  mood: "happy" | "neutral" | "sad" | "angry" | "tired";
  action: "feed" | "sleep" | "clean" | "play" | "none";
  equip?: ChatEquip | null;
  animation?: string | null;
  sfx_prompt?: string | null;
}

export interface ChatResponse {
  response: ChatResult;
  profile: Profile;
}

export async function getProfile(): Promise<Profile> {
  return request<Profile>("/api/profile");
}

export async function getShop(): Promise<{ items: ShopItem[] }> {
  return request<{ items: ShopItem[] }>("/api/shop");
}

export async function performAction(action: string): Promise<{ profile: Profile }> {
  return request(`/api/actions/${action}`, { method: "POST" });
}

export async function buyItem(item_id: string): Promise<{ profile: Profile }> {
  return request("/api/shop/buy", {
    method: "POST",
    body: JSON.stringify({ item_id }),
  });
}

export async function equipItem(item_id: string): Promise<{ profile: Profile }> {
  return request("/api/shop/equip", {
    method: "POST",
    body: JSON.stringify({ item_id }),
  });
}

export async function submitMinigame(
  score: number,
  duration_ms: number
): Promise<{ profile: Profile }> {
  return request("/api/minigame/result", {
    method: "POST",
    body: JSON.stringify({ score, duration_ms }),
  });
}

export async function sendChat(messages: ChatMessage[]): Promise<ChatResponse> {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ messages }),
  });
}

export async function requestActionFeedback(
  action: "feed" | "sleep" | "clean" | "play"
): Promise<ChatResponse> {
  return request("/api/action-feedback", {
    method: "POST",
    body: JSON.stringify({ action }),
  });
}

export async function requestReminder(): Promise<ChatResponse> {
  return request("/api/reminder", {
    method: "POST",
  });
}

export async function synthesizeSpeech(text: string): Promise<Blob> {
  return requestBlob("/api/tts", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function synthesizeSoundEffect(prompt: string): Promise<Blob> {
  return requestBlob("/api/sfx", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
}

export async function transcribeSpeech(audio: Blob): Promise<{ text: string }> {
  const formData = new FormData();
  const file = audio instanceof File ? audio : new File([audio], "speech.webm", {
    type: audio.type || "audio/webm",
  });
  formData.append("audio", file);

  const response = await fetch(`${API_BASE}/api/stt`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  return (await response.json()) as { text: string };
}
