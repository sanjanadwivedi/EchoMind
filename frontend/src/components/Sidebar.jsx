import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import NPCCard from "./NPCCard";
import CreateCharacterModal from "./CreateCharacterModal";
import { fetchNPCs } from "../api/client";

export default function Sidebar({ activeNpc, onSelectNpc }) {
  const [npcs, setNpcs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchNPCs()
      .then(setNpcs)
      .catch((err) => console.error("Failed to load NPCs:", err))
      .finally(() => setLoading(false));
  }, []);

  const handleNpcCreated = (newNpc) => {
    setNpcs((prev) => [...prev, newNpc]);
    onSelectNpc(newNpc);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar__header">
        <h1 className="sidebar__title">
          <span className="sidebar__logo">🧠</span>
          EchoMind
        </h1>
        <p className="sidebar__subtitle">NPC Memory System</p>
      </div>

      <div className="sidebar__divider" />

      <div className="sidebar__actions">
        <button
          className="create-character-btn"
          onClick={() => setIsModalOpen(true)}
        >
          <span>✨</span> Create Character
        </button>
      </div>

      <nav className="sidebar__list">
        {loading ? (
          <div className="sidebar__loading">
            <div className="spinner" />
            <p>Loading NPCs...</p>
          </div>
        ) : (
          <AnimatePresence>
            {npcs.map((npc) => (
              <NPCCard
                key={npc.id}
                npc={npc}
                isActive={activeNpc?.id === npc.id}
                onClick={() => onSelectNpc(npc)}
              />
            ))}
          </AnimatePresence>
        )}
      </nav>

      <div className="sidebar__footer">
        <p className="sidebar__version">v1.0.0</p>
      </div>

      <CreateCharacterModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreated={handleNpcCreated}
      />
    </aside>
  );
}

