const API_BASE =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;

  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function fetchNPCs() {
  return request("/npcs/");
}

export async function createNPC(npcData) {
  return request("/npcs/", {
    method: "POST",
    body: JSON.stringify(npcData),
  });
}

export async function fetchPlayers() {
  return request("/players/");
}

export async function sendMessage(npcId, playerId, message) {
  return request("/chat/", {
    method: "POST",
    body: JSON.stringify({
      npc_id: npcId,
      player_id: playerId,
      message,
    }),
  });
}

export async function fetchRelationshipInfo(npcId, playerId) {
  return request(`/relationships/${npcId}/${playerId}`);
}

export async function triggerReflection(npcId, playerId) {
  return request(`/memory/reflect?npc_id=${npcId}&player_id=${playerId}`, {
    method: "POST",
  });
}

export async function fetchMemories(npcId, playerId) {
  return request(`/memory/debug?npc_id=${npcId}&player_id=${playerId}`);
}
