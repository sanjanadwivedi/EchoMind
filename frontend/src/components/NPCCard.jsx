import { motion } from "framer-motion";
import AnimatedAvatar from "./AnimatedAvatar";
import { soundEffects } from "../utils/soundEffects";

const npcBanners = {
  Eldon: "/banners/eldon.png",
  Ragnar: "/banners/ragnar.png",
  Luna: "/banners/luna.png",
};

const roleColor = {
  Merchant: "#f59e0b",
  Guard: "#ef4444",
  Scholar: "#8b5cf6",
  Alchemist: "#10b981",
};

const roleBadge = {
  Merchant: "💰 Merchant",
  Guard: "🛡 Guard",
  Scholar: "📜 Scholar",
  Alchemist: "⚗️ Alchemist",
};

export default function NPCCard({ npc, isActive, onClick }) {
  const color = roleColor[npc.role] || "#6b7280";
  const banner = npcBanners[npc.name];
  const badgeText = roleBadge[npc.role] || npc.role;

  function handleClick() {
    soundEffects.playClickSound();
    onClick();
  }

  return (
    <motion.button
      className={`npc-card ${isActive ? "npc-card--active" : ""}`}
      onClick={handleClick}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.97 }}
      layout
      style={{ "--card-accent": color }}
    >
      {/* Background Banner Art */}
      {banner && (
        <div className="npc-card__banner">
          <img src={banner} alt="" className="npc-card__banner-img" />
          <div className="npc-card__banner-overlay" />
        </div>
      )}

      {/* Card Content */}
      <div className="npc-card__content">
        <AnimatedAvatar
          name={npc.name}
          role={npc.role}
          size="sm"
          isActive={isActive}
        />

        <div className="npc-card__info">
          {/* Name row */}
          <h3 className="npc-card__name">{npc.name}</h3>

          {/* Badge on its own row — never clips */}
          <span className="npc-card__badge">{badgeText}</span>

          {/* Location */}
          <p className="npc-card__location">📍 {npc.location}</p>
        </div>
      </div>
    </motion.button>
  );
}
