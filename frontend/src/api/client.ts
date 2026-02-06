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
