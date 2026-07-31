import { motion } from "framer-motion";

const npcAvatars = {
  Eldon: "/avatars/eldon.png",
  Ragnar: "/avatars/ragnar.png",
  Luna: "/avatars/luna.png",
};

const roleEmoji = {
  Merchant: "🏪",
  Guard: "⚔️",
  Scholar: "📚",
};

export default function AnimatedAvatar({
  name,
  role,
  size = "md", // "sm", "md", "lg"
  isActive = false,
  isSpeaking = false,
}) {
  const avatar = npcAvatars[name];
  const emoji = roleEmoji[role] || "👤";

  return (
    <motion.div
      className={`animated-avatar animated-avatar--${size} ${isActive ? "animated-avatar--active" : ""} ${isSpeaking ? "animated-avatar--speaking" : ""}`}
      whileHover={{ scale: 1.08, rotate: [0, -2, 2, 0] }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {/* Rotating magical rune aura ring */}
      <div className="animated-avatar__aura" />

      {/* Shimmer light sweep on hover */}
      <div className="animated-avatar__shimmer" />

      {/* Main Image or Emoji fallback */}
      <div className="animated-avatar__frame">
        {avatar ? (
          <img src={avatar} alt={name} className="animated-avatar__img" />
        ) : (
          <div className="animated-avatar__initial">
            <span>{name ? name.charAt(0).toUpperCase() : "?"}</span>
          </div>
        )}
      </div>

      {/* Online pulsing indicator */}
      {isActive && <span className="animated-avatar__pulse-dot" />}
    </motion.div>
  );
}
