import { useState, useEffect, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import NPCInfo from "./components/NPCInfo";
import { useChat } from "./hooks/useChat";
import { fetchPlayers } from "./api/client";
import "./App.css";

export default function App() {
  const [activeNpc, setActiveNpc] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const { getMessages, getEmotion, send, isLoading } = useChat();

  // Load the first player on mount
  useEffect(() => {
    fetchPlayers()
      .then((players) => {
        if (players.length > 0) {
          setPlayerId(players[0].id);
        }
      })
      .catch((err) => console.error("Failed to load players:", err));
  }, []);

  const handleSend = useCallback(
    (message) => {
      if (!activeNpc || !playerId) return;
      send(activeNpc.id, playerId, message, activeNpc.name);
    },
    [activeNpc, playerId, send]
  );

  const messages = activeNpc ? getMessages(activeNpc.id) : [];
  const currentEmotion = activeNpc ? getEmotion(activeNpc.id) : "Neutral";

  return (
    <div className="app">
      <Sidebar activeNpc={activeNpc} onSelectNpc={setActiveNpc} />

      <main className="main">
        <ChatPanel
          npc={activeNpc}
          messages={messages}
          currentEmotion={currentEmotion}
          isLoading={isLoading}
          onSend={handleSend}
          playerId={playerId}
        />

        {activeNpc && playerId && (
          <NPCInfo npc={activeNpc} playerId={playerId} />
        )}
      </main>
    </div>
  );
}
