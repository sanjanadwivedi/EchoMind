import { useState, useEffect, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import NPCInfo from "./components/NPCInfo";
import { useChat } from "./hooks/useChat";
import { fetchPlayers, createPlayer } from "./api/client";
import "./App.css";

export default function App() {
  const [activeNpc, setActiveNpc] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const { getMessages, getEmotion, send, isLoading } = useChat();

  // Load or auto-create player on mount
  useEffect(() => {
    fetchPlayers()
      .then(async (players) => {
        if (players.length > 0) {
          setPlayerId(players[0].id);
        } else {
          try {
            const newPlayer = await createPlayer("Sanjana");
            setPlayerId(newPlayer.id);
          } catch (e) {
            console.error("Failed to auto-create player:", e);
          }
        }
      })
      .catch(async (err) => {
        console.error("Failed to load players, attempting creation:", err);
        try {
          const newPlayer = await createPlayer("Sanjana");
          setPlayerId(newPlayer.id);
        } catch (e) {
          console.error("Failed to create player fallback:", e);
        }
      });
  }, []);

  const handleSend = useCallback(
    async (message) => {
      if (!activeNpc) return;

      let currentId = playerId;
      if (!currentId) {
        try {
          const players = await fetchPlayers();
          if (players.length > 0) {
            currentId = players[0].id;
          } else {
            const newPlayer = await createPlayer("Sanjana");
            currentId = newPlayer.id;
          }
          setPlayerId(currentId);
        } catch (e) {
          console.error("Could not obtain player ID before send:", e);
          return;
        }
      }

      send(activeNpc.id, currentId, message, activeNpc.name);
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
