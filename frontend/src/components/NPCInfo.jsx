import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchRelationshipInfo, triggerReflection } from "../api/client";
import { soundEffects } from "../utils/soundEffects";

const traitLabels = {
  trust: { label: "Trust", emoji: "🤝" },
  respect: { label: "Respect", emoji: "👑" },
  warmth: { label: "Warmth", emoji: "🔥" },
  curiosity: { label: "Curiosity", emoji: "🔍" },
  fear: { label: "Fear", emoji: "😨" },
  loyalty: { label: "Loyalty", emoji: "🛡️" },
  aggression: { label: "Aggression", emoji: "⚡" },
};

function TraitBar({ trait, value, delay }) {
  const info = traitLabels[trait] || { label: trait, emoji: "•" };

  return (
    <div className="trait-bar">
      <div className="trait-bar__header">
        <span className="trait-bar__label">
          {info.emoji} {info.label}
        </span>
        <span className="trait-bar__value">{value}</span>
      </div>
      <div className="trait-bar__track">
        <motion.div
          className="trait-bar__fill"
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, delay: delay * 0.1, ease: "easeOut" }}
          style={{
            background:
              value > 70
                ? "linear-gradient(90deg, #10b981, #34d399)"
                : value > 40
                  ? "linear-gradient(90deg, #f59e0b, #fbbf24)"
                  : "linear-gradient(90deg, #ef4444, #f87171)",
          }}
        />
      </div>
    </div>
  );
}

export default function NPCInfo({ npc, playerId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reflection, setReflection] = useState(null);
  const [reflectionLoading, setReflectionLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    if (!npc || !playerId) return;
    setLoading(true);
    setReflection(null);

    fetchRelationshipInfo(npc.id, playerId)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [npc?.id, playerId]);

  async function handleReflect() {
    if (!npc || !playerId) return;
    setReflectionLoading(true);
    soundEffects.playReflectSound();
    try {
      const result = await triggerReflection(npc.id, playerId);
      setReflection(result);
    } catch {
      setReflection({ reflection: "Failed to generate reflection." });
    } finally {
      setReflectionLoading(false);
    }
  }

  if (!npc) return null;

  return (
    <aside className={`npc-info ${isOpen ? "npc-info--open" : "npc-info--collapsed"}`}>
      <div className="npc-info__header">
        <div className="npc-info__header-title">
          <span>📜</span> NPC Dossier
        </div>
        <button
          className="npc-info__toggle-btn"
          onClick={() => setIsOpen(!isOpen)}
          title={isOpen ? "Collapse Panel" : "Expand Panel"}
        >
          {isOpen ? "➔" : "⬅"}
        </button>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="npc-info__content"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.2 }}
          >
            {loading ? (
              <div className="npc-info__loading">
                <div className="spinner" />
              </div>
            ) : data ? (
              <>
                {/* Personality */}
                {data.personality && (
                  <div className="npc-info__section">
                    <h4 className="npc-info__section-title">
                      🎭 Personality
                    </h4>
                    {Object.entries(data.personality).map(
                      ([trait, value], i) => (
                        <TraitBar
                          key={trait}
                          trait={trait}
                          value={value}
                          delay={i}
                        />
                      )
                    )}
                  </div>
                )}

                {/* Relationship */}
                {data.relationship && (
                  <div className="npc-info__section">
                    <h4 className="npc-info__section-title">
                      💫 Relationship
                    </h4>
                    <div className="npc-info__stats">
                      <div className="npc-info__stat">
                        <span className="npc-info__stat-label">Trust</span>
                        <span className="npc-info__stat-value">
                          {(data.relationship.trust * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="npc-info__stat">
                        <span className="npc-info__stat-label">Affinity</span>
                        <span className="npc-info__stat-value">
                          {(data.relationship.affinity * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Reflection */}
                <div className="npc-info__section">
                  <h4 className="npc-info__section-title">
                    🔮 Memory Reflection
                  </h4>
                  <button
                    className="npc-info__reflect-btn"
                    onClick={handleReflect}
                    disabled={reflectionLoading}
                  >
                    {reflectionLoading
                      ? "Reflecting..."
                      : "Generate Reflection"}
                  </button>

                  {reflection && (
                    <motion.div
                      className="npc-info__reflection"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <p>{reflection.reflection}</p>
                      {reflection.memory_count != null && (
                        <span className="npc-info__reflection-meta">
                          Based on {reflection.memory_count} memories
                        </span>
                      )}
                    </motion.div>
                  )}
                </div>
              </>
            ) : (
              <p className="npc-info__empty">
                No relationship data available.
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </aside>
  );
}
