import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchMemories } from "../api/client";

const categoryColors = {
  personal_fact: { label: "Personal Fact", color: "#3b82f6", bg: "rgba(59, 130, 246, 0.15)" },
  preference: { label: "Preference", color: "#ec4899", bg: "rgba(236, 72, 153, 0.15)" },
  relationship: { label: "Relationship", color: "#a855f7", bg: "rgba(168, 85, 247, 0.15)" },
  goal: { label: "Goal", color: "#10b981", bg: "rgba(16, 185, 129, 0.15)" },
  event: { label: "Event", color: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)" },
  other: { label: "Other", color: "#94a3b8", bg: "rgba(148, 163, 184, 0.15)" },
};

export default function MemoryBankDrawer({ npc, playerId, isOpen, onClose }) {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    if (!npc || !playerId || !isOpen) return;
    setLoading(true);

    fetchMemories(npc.id, playerId)
      .then(setMemories)
      .catch((err) => console.error("Failed to fetch memories:", err))
      .finally(() => setLoading(false));
  }, [npc?.id, playerId, isOpen]);

  if (!isOpen || !npc) return null;

  const filteredMemories = memories.filter((m) => {
    const matchesCategory =
      selectedCategory === "all" || m.category === selectedCategory;
    const matchesSearch =
      m.summary?.toLowerCase().includes(search.toLowerCase()) ||
      m.category?.toLowerCase().includes(search.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <AnimatePresence>
      <div className="memory-modal-overlay" onClick={onClose}>
        <motion.div
          className="memory-modal"
          onClick={(e) => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
        >
          {/* Modal Header */}
          <div className="memory-modal__header">
            <div>
              <h3 className="memory-modal__title">
                🧠 {npc.name}'s Vector Memory Bank
              </h3>
              <p className="memory-modal__subtitle">
                Live ChromaDB & PostgreSQL long-term knowledge repository
              </p>
            </div>
            <button className="memory-modal__close" onClick={onClose}>
              ✕
            </button>
          </div>

          {/* Controls Bar */}
          <div className="memory-modal__controls">
            <input
              type="text"
              className="memory-modal__search"
              placeholder="🔍 Search memories..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

            <select
              className="memory-modal__select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="all">All Categories ({memories.length})</option>
              <option value="personal_fact">Personal Facts</option>
              <option value="preference">Preferences</option>
              <option value="relationship">Relationships</option>
              <option value="goal">Goals</option>
              <option value="event">Events</option>
            </select>
          </div>

          {/* Memories List */}
          <div className="memory-modal__body">
            {loading ? (
              <div className="memory-modal__loading">
                <div className="spinner" />
                <p>Retrieving vector embeddings from ChromaDB...</p>
              </div>
            ) : filteredMemories.length === 0 ? (
              <div className="memory-modal__empty">
                <p>No memories found for this filter.</p>
                <span className="memory-modal__empty-hint">
                  Tell {npc.name} new facts in chat to create long-term memories!
                </span>
              </div>
            ) : (
              <div className="memory-modal__list">
                {filteredMemories.map((m) => {
                  const catInfo =
                    categoryColors[m.category] || categoryColors.other;
                  return (
                    <motion.div
                      key={m.id}
                      className="memory-card"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <div className="memory-card__header">
                        <span
                          className="memory-card__badge"
                          style={{
                            color: catInfo.color,
                            backgroundColor: catInfo.bg,
                            borderColor: catInfo.color,
                          }}
                        >
                          {catInfo.label}
                        </span>

                        <span className="memory-card__date">
                          {new Date(m.created_at).toLocaleDateString([], {
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>

                      <p className="memory-card__summary">{m.summary}</p>

                      <div className="memory-card__footer">
                        <div className="memory-card__importance">
                          <span>Importance: {(m.importance * 100).toFixed(0)}%</span>
                          <div className="memory-card__bar-track">
                            <div
                              className="memory-card__bar-fill"
                              style={{ width: `${m.importance * 100}%` }}
                            />
                          </div>
                        </div>

                        {m.embedding_id && (
                          <span className="memory-card__vector-tag">
                            Vector ID: {m.embedding_id.slice(0, 8)}...
                          </span>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
