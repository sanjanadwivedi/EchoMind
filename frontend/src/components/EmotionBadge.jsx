import { motion } from "framer-motion";

const emotionConfig = {
  Friendly: { label: "Friendly", emoji: "😊", color: "#10b981", bg: "rgba(16, 185, 129, 0.15)" },
  Suspicious: { label: "Suspicious", emoji: "🤔", color: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)" },
  Impressed: { label: "Impressed", emoji: "🔥", color: "#a855f7", bg: "rgba(168, 85, 247, 0.15)" },
  Amused: { label: "Amused", emoji: "✨", color: "#06b6d4", bg: "rgba(6, 182, 212, 0.15)" },
  Thoughtful: { label: "Thoughtful", emoji: "💭", color: "#6366f1", bg: "rgba(99, 102, 241, 0.15)" },
  Guarded: { label: "Guarded", emoji: "🛡️", color: "#94a3b8", bg: "rgba(148, 163, 184, 0.15)" },
  Grateful: { label: "Grateful", emoji: "💖", color: "#ec4899", bg: "rgba(236, 72, 153, 0.15)" },
  Neutral: { label: "Neutral", emoji: "😐", color: "#9ca3af", bg: "rgba(156, 163, 175, 0.15)" },
};

export default function EmotionBadge({ emotion = "Neutral" }) {
  const config = emotionConfig[emotion] || emotionConfig.Neutral;

  return (
    <motion.span
      className="emotion-badge"
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      key={emotion}
      style={{
        "--emotion-color": config.color,
        "--emotion-bg": config.bg,
      }}
    >
      <span className="emotion-badge__emoji">{config.emoji}</span>
      <span className="emotion-badge__label">{config.label}</span>
    </motion.span>
  );
}
