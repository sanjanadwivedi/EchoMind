import { motion } from "framer-motion";
import AnimatedAvatar from "./AnimatedAvatar";

export default function MessageBubble({ message, npcName }) {
  const isPlayer = message.role === "player";
  const isError = message.role === "error";
  const telemetry = message.telemetry;

  return (
    <motion.div
      className={`message ${isPlayer ? "message--player" : ""} ${isError ? "message--error" : ""}`}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
    >
      {!isPlayer && !isError && (
        <AnimatedAvatar name={npcName} size="sm" />
      )}

      <div className="message__body">
        {!isPlayer && !isError && (
          <div className="message__header-line" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="message__sender">{npcName}</span>
            {telemetry && (
              <span
                className="telemetry-pill"
                style={{
                  fontSize: "0.7rem",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  background: telemetry.cache_hit ? "rgba(16, 185, 129, 0.2)" : "rgba(99, 102, 241, 0.2)",
                  color: telemetry.cache_hit ? "#10b981" : "#a5b4fc",
                  border: `1px solid ${telemetry.cache_hit ? "rgba(16, 185, 129, 0.4)" : "rgba(99, 102, 241, 0.4)"}`,
                  fontWeight: 600
                }}
                title={telemetry.cache_hit ? "Served instantly from Semantic Query Cache" : `Retrieval: ${telemetry.retrieval_ms || 0}ms | Gen: ${telemetry.generation_ms || 0}ms`}
              >
                {telemetry.cache_hit ? "⚡ Cache Hit (0ms)" : `⏱️ ${telemetry.total_ms}ms`}
              </span>
            )}
          </div>
        )}
        <div className="message__bubble">
          <p className="message__text">{message.content}</p>
        </div>
        <span className="message__time">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </motion.div>
  );
}
